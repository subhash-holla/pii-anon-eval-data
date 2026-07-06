#!/usr/bin/env python3
"""Build an aws-en single-detector baseline_results.json from the per-record dump (no second aws scoring;
McNemar reads the same hits). Recall-only per-record fallback for the McNemar/coverage-decomposition path.

micro: full (tp/fp/fn from meta — n_pred carries the precision side). by_entity_type: RECALL-ONLY (per-type
tp/fn derived from gold.parquet+hits_aws.parquet; per-type fp is NOT recoverable from a per-record dump, so
fp=0 — these cells are consumed ONLY by coverage_decomposition's within_reach_recall, which uses tp/fn).
by_domain is left empty (would otherwise render a misleading per-domain precision); by_language['en']==micro.

macro: emitted as null. A real macro-F2 needs per-type PRECISION, which the recall-only dump lacks (a
micro-copy placeholder would corrupt r(reachable, macro-F2)). The COMMITTED leaderboard's aws block comes
from a full ``pii-anon baselines --cloud --detectors aws`` run (byte-identical micro to this dump, plus a
real macro), so this aggregate is retained only as the recall-only per-record fallback.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pyarrow.parquet as pq  # noqa: E402
from pii_anon_datasets import taxonomy  # noqa: E402
from pii_anon_datasets.baselines.results import BaselineResults  # noqa: E402
from pii_anon_datasets.scoring.detection import aggregate_detection_score  # noqa: E402

_REGISTRY = os.path.join(os.path.dirname(__file__), "..", "src", "pii_anon_datasets", "data", "label_maps_63.json")


def _per_type_tp_fn(dump: str) -> dict:
    """{entity_type: (tp, fn)} from the per-record gold + hits (joined on record_id/gold_idx)."""
    gold = pq.read_table(os.path.join(dump, "gold.parquet"), columns=["record_id", "gold_idx", "entity_type"]).to_pylist()
    hits = pq.read_table(os.path.join(dump, "hits_aws.parquet"), columns=["record_id", "gold_idx", "hit"]).to_pylist()
    hit_by_key = {(h["record_id"], h["gold_idx"]): int(h["hit"]) for h in hits}
    tp = defaultdict(int)
    n = defaultdict(int)
    for g in gold:
        t = g["entity_type"]
        n[t] += 1
        tp[t] += hit_by_key.get((g["record_id"], g["gold_idx"]), 0)
    return {t: (tp[t], n[t] - tp[t]) for t in n}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True, help="results/per-record/en-test-v22")
    ap.add_argument("--out", required=True, help="output dir for aws baseline_results.json")
    ap.add_argument("--registry", default=_REGISTRY)
    ap.add_argument("--ref", default=os.path.join(os.path.dirname(__file__), "..", "results", "baselines",
                    "fulltest-cloud", "gcp", "en", "baseline_results.json"),
                    help="sibling en shard whose dataset block aws must match (merge consistency guard)")
    args = ap.parse_args(argv)

    meta = json.loads(open(os.path.join(args.dump, "meta_aws.json")).read())
    tp, n_gold, n_pred = int(meta["n_tp"]), int(meta["n_gold"]), int(meta["n_pred"])
    ds = aggregate_detection_score(tp, n_pred - tp, n_gold - tp)

    by_type = {t: aggregate_detection_score(t_tp, 0, t_fn).as_dict()  # RECALL-ONLY (fp=0; see module docstring)
               for t, (t_tp, t_fn) in _per_type_tp_fn(args.dump).items()}

    reg = json.loads(open(args.registry).read())
    aws_reg = (reg.get("detectors") or reg).get("aws", {})
    reachable = aws_reg.get("reachable_types", [])
    # of_total + unreachable are computed against the LIVE canonical (taxonomy.ENTITY_TYPE_COUNT, now 66)
    # so the aws coverage cell matches the 10 live-scored detectors in the same leaderboard (contract.py).
    # aws's reachable set (from the frozen-63 registry) is unchanged — it reaches none of the 3 new Art-9
    # types, so 63-projection == 66-projection here.
    unreachable = sorted(taxonomy.CANONICAL_ENTITY_TYPES - set(reachable))

    det = {
        "status": "scored",
        "model_id": meta.get("model_id", "aws-comprehend"),
        "deterministic": False,
        "record_errors": int(meta.get("record_errors", 0)),
        "n_records": int(meta.get("n_records", 0)),
        "n_gold": n_gold,
        "n_pred": n_pred,
        "coverage": {
            "reachable": len(reachable),
            "of_total": taxonomy.ENTITY_TYPE_COUNT,
            "reachable_types": reachable,
            "dropped_native": aws_reg.get("dropped_native", []),
            "unreachable_types": unreachable,
        },
        "micro": ds.as_dict(),
        # macro-F2 is null: not computable from a recall-only dump (no per-type precision). A micro-copy
        # placeholder would corrupt r(reachable, macro-F2); the committed leaderboard's aws macro comes from
        # a full `baselines --cloud` run. See module docstring.
        "macro": None,
        "by_entity_type": by_type,
        "by_domain": {},  # per-domain precision not recoverable from a per-record dump
        "by_language": {"en": ds.as_dict()},
        "_aggregate_note": "Derived from the en-test-v22 per-record dump (aws scored once). by_entity_type is "
                           "recall-only (per-type fp unavailable); micro is full. by_domain omitted.",
    }
    ref_dataset = json.loads(open(args.ref).read())["dataset"]  # match the sibling shards' (split, version, lang, n_records)
    results = BaselineResults(
        dataset=ref_dataset,
        confidence=0.95,
        ranking=[{"rank": 1, "detector": "aws", "f2_micro": ds.f2, "f2_macro": None}],  # macro N/A (recall-only dump)
        detectors={"aws": det},
    )
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "baseline_results.json"), "w", encoding="utf-8") as f:
        f.write(results.to_json())
    print(f"wrote aws-en aggregate -> {args.out}/baseline_results.json (F2 {ds.f2:.3f}, "
          f"{len(by_type)} entity types, recall {ds.recall:.3f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
