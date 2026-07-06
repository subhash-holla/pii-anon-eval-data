import json
import sys
from pathlib import Path

from pii_anon_datasets.scoring.detection import aggregate_detection_score


def test_aggregate_from_counts():
    ds = aggregate_detection_score(pooled_tp=80, pooled_fp=20, pooled_fn=20)
    assert ds.counts.tp == 80 and ds.counts.fp == 20 and ds.counts.fn == 20
    assert abs(ds.precision - 0.8) < 1e-9 and abs(ds.recall - 0.8) < 1e-9
    assert 0.0 <= ds.recall_ci.low <= ds.recall <= ds.recall_ci.high <= 1.0
    d = ds.as_dict()
    assert d["counts"]["tp"] == 80 and "recall_ci" in d


def test_aws_en_aggregate_writes_json(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    import aws_en_aggregate

    dump = tmp_path / "dump"
    dump.mkdir()
    # 100 gold spans (60 PERSON_NAME + 40 EMAIL_ADDRESS); 80 hits (50/60 + 30/40)
    etype = ["PERSON_NAME"] * 60 + ["EMAIL_ADDRESS"] * 40
    hit = [1] * 50 + [0] * 10 + [1] * 30 + [0] * 10
    cols = {"record_id": ["r"] * 100, "gold_idx": list(range(100))}
    pq.write_table(pa.table({**cols, "entity_type": etype}), str(dump / "gold.parquet"))
    pq.write_table(pa.table({**cols, "hit": hit}), str(dump / "hits_aws.parquet"))
    (dump / "meta_aws.json").write_text(json.dumps({"n_tp": 80, "n_gold": 100, "n_pred": 100, "model_id": "aws"}))
    ref = tmp_path / "ref.json"
    ref.write_text(json.dumps({"dataset": {"dataset_version": "2.0.0", "language": "en",
                                           "n_gold": 100, "n_records": 50, "split": "test"}}))
    outdir = tmp_path / "aws-en"
    rc = aws_en_aggregate.main(["--dump", str(dump), "--out", str(outdir), "--ref", str(ref)])
    assert rc == 0
    res = json.loads((outdir / "baseline_results.json").read_text())
    assert "confidence" in res                                  # canonical shape -> mergeable (from_dict)
    assert res["dataset"]["dataset_version"] == "2.0.0"          # copied from --ref for the merge guard
    aws = res["detectors"]["aws"]
    assert aws["n_gold"] == 100 and abs(aws["micro"]["recall"] - 0.8) < 1e-9
    bt = aws["by_entity_type"]                                   # per-type recall derived from the per-record hits
    assert set(bt) == {"PERSON_NAME", "EMAIL_ADDRESS"}
    assert abs(bt["PERSON_NAME"]["recall"] - 50 / 60) < 1e-9
    assert abs(bt["EMAIL_ADDRESS"]["recall"] - 30 / 40) < 1e-9
