"""CAP-02 S10/S11 — observability run-records (DC-25) + pre-registration (DC-24).

Run-records reuse the benchmark_throughput pattern (schema id, harness_version, injectable timestamp,
provenance block with is_reference_host / environment / canonical_verdict). Pre-registration hashes ONLY the
design-and-analysis plan (not the wall-clock), so the report can prove plan-equality (FR-050; AX-005 element 4).
"""
from __future__ import annotations

from pii_anon_datasets.assessment import prereg as P
from pii_anon_datasets.assessment import runrecord as RR


# ---- run-records (DC-25) ----
def test_run_record_has_provenance_and_schema() -> None:
    rec = RR.build_run_record(
        stage="sample", run_id="run-1", seed=7, dataset_version="2.0.0", record_count=575604,
        code_commit="abc", content_hash="h", timestamp="2026-06-01T00:00:00Z",
    )
    assert rec["schema"] == RR.RUNRECORD_SCHEMA
    assert rec["stage"] == "sample" and rec["run_id"] == "run-1"
    assert rec["provenance"]["is_reference_host"] is False
    assert rec["provenance"]["environment"]
    assert rec["provenance"]["canonical_verdict"]  # INDICATIVE in agent-env


def test_run_record_timestamp_injectable_for_byte_repro() -> None:
    kw = dict(stage="load", run_id="r", seed=1, dataset_version="2.0.0", record_count=1,
              code_commit="c", content_hash="h", timestamp="2026-06-01T00:00:00Z")
    assert RR.build_run_record(**kw) == RR.build_run_record(**kw)


def test_write_run_records_jsonl_shared_run_id(tmp_path) -> None:
    recs = [
        RR.build_run_record(stage=s, run_id="R", seed=1, dataset_version="2.0.0", record_count=1,
                            code_commit="c", content_hash="h", timestamp="2026-06-01T00:00:00Z")
        for s in ("load", "sample", "run", "score", "rate", "report")
    ]
    out = RR.write_run_records(recs, tmp_path / "run-R.jsonl")
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 6
    import json
    assert all(json.loads(line)["run_id"] == "R" for line in lines)


# ---- pre-registration (DC-24) ----
def _prereg(seed=7, ts="2026-06-01T00:00:00Z"):
    return P.build_prereg(
        manifest_hash="mh", seed=seed, systems=["A", "B"], metrics=["recall"], run_type="dev",
        interval_rule={"default": "wilson", "small_n_cutoff": 15}, multiplicity="holm-bonferroni",
        code_commit="c", timestamp=ts,
    )


def test_prereg_hash_is_hex_over_plan_only() -> None:
    pr = _prereg()
    assert pr["schema"] == P.PREREG_SCHEMA
    assert isinstance(pr["prereg_hash"], str) and len(pr["prereg_hash"]) == 64


def test_prereg_hash_stable_across_timestamps() -> None:
    """The plan-hash must not depend on WHEN it was registered (only on the plan) — FR-050 plan-equality."""
    a = _prereg(ts="2026-06-01T00:00:00Z")
    b = _prereg(ts="2030-12-31T23:59:59Z")
    assert a["prereg_hash"] == b["prereg_hash"]


def test_prereg_hash_changes_with_plan() -> None:
    assert _prereg(seed=7)["prereg_hash"] != _prereg(seed=8)["prereg_hash"]


def test_verify_prereg_roundtrip_and_tamper() -> None:
    pr = _prereg()
    assert P.verify_prereg(pr) is True
    tampered = dict(pr)
    tampered["design_and_analysis_plan"] = {**pr["design_and_analysis_plan"], "seed": 999}
    assert P.verify_prereg(tampered) is False
