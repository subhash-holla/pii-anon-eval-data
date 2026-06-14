"""Baseline artifact emission — writes baseline_results.json + a run-record + a sha256 provenance index,
reusing the AUDITED assessment.runrecord / assessment.provenance house style. Determinism inputs
(timestamp / generated_at / content_hash / code_commit / seed) are INJECTED, so a re-emit is byte-identical.
"""

from __future__ import annotations

import hashlib
import json

from pii_anon_datasets.baselines import provenance
from pii_anon_datasets.baselines.results import BaselineResults


def _results() -> BaselineResults:
    return BaselineResults(
        dataset={"split": "test", "language": "en", "dataset_version": "2.0.0", "n_records": 2, "n_gold": 3},
        confidence=0.95,
        ranking=[{"rank": 1, "detector": "x", "f2_micro": 0.9, "f2_macro": 0.8}],
        detectors={"x": {"status": "scored", "micro": {"f2": 0.9}}},
    )


def _emit(tmp_path):
    return provenance.emit_baseline_artifacts(
        _results(),
        tmp_path,
        run_id="run-1",
        seed=20260603,
        code_commit="abc123",
        content_hash="deadbeef",
        timestamp="2026-06-03T00:00:00Z",
        generated_at="2026-06-03T00:00:00Z",
    )


def test_emit_writes_three_artifacts(tmp_path) -> None:
    paths = _emit(tmp_path)
    assert paths["results"].exists()
    assert paths["run_record"].exists()
    assert paths["provenance"].exists()


def test_results_json_is_canonical_and_round_trips(tmp_path) -> None:
    paths = _emit(tmp_path)
    parsed = json.loads(paths["results"].read_text(encoding="utf-8"))
    assert parsed["dataset"]["n_records"] == 2
    assert parsed["matching_policy"] == "strict-v1"


def test_run_record_is_a_baselines_stage_record(tmp_path) -> None:
    paths = _emit(tmp_path)
    rr = json.loads(paths["run_record"].read_text(encoding="utf-8").strip())
    assert rr["stage"] == "baselines"
    assert rr["seed"] == 20260603
    assert rr["dataset_version"] == "2.0.0"
    assert rr["record_count"] == 2


def test_provenance_index_hashes_the_results_file(tmp_path) -> None:
    paths = _emit(tmp_path)
    idx = json.loads(paths["provenance"].read_text(encoding="utf-8"))
    by_name = {a["path"]: a["sha256"] for a in idx["artifacts"]}
    assert "baseline_results.json" in by_name
    assert by_name["baseline_results.json"] == hashlib.sha256(paths["results"].read_bytes()).hexdigest()


def test_emit_is_byte_reproducible(tmp_path) -> None:
    a = _emit(tmp_path / "a")
    b = _emit(tmp_path / "b")
    for key in ("results", "run_record", "provenance"):
        assert a[key].read_bytes() == b[key].read_bytes(), f"{key} not byte-reproducible"
