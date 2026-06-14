"""Baseline artifact emission — write the three canonical outputs of a ``pii-anon baselines`` run:

  * ``baseline_results.json``      — the F2-ranked leaderboard (canonical sorted-key JSON);
  * ``baseline_run_record.jsonl``  — the run-record (seed / dataset version / commit / content hash);
  * ``baseline_provenance.json``   — a sha256 index over the two files above.

A THIN wrapper: all provenance math is the AUDITED ``assessment.runrecord`` / ``assessment.provenance``
house style (no new hashing here). Every determinism input (``timestamp`` / ``generated_at`` /
``content_hash`` / ``code_commit`` / ``seed``) is INJECTED by the caller (never a clock/RNG), so a re-emit
with the same inputs is byte-identical. The run-record's ``canonical_verdict`` defaults to ``INDICATIVE``
(detectors on SYNTHETIC data — AX-001 — are never auto-promoted to a citable verdict).
"""

from __future__ import annotations

from pathlib import Path

from ..assessment.provenance import build_provenance_index, write_provenance_index
from ..assessment.runrecord import build_run_record, write_run_records
from .results import BaselineResults

RESULTS_NAME = "baseline_results.json"
RUN_RECORD_NAME = "baseline_run_record.jsonl"
PROVENANCE_NAME = "baseline_provenance.json"


def emit_baseline_artifacts(
    results: BaselineResults,
    out_dir: str | Path,
    *,
    run_id: str,
    seed: int,
    code_commit: str,
    content_hash: str,
    timestamp: str,
    generated_at: str,
    environment: str = "agent-execution-sandbox",
    canonical_verdict: str = "INDICATIVE",
) -> dict[str, Path]:
    """Write the results JSON + run-record + sha256 provenance index into ``out_dir``; return their paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    results_path = out / RESULTS_NAME
    results_path.write_text(results.to_json(), encoding="utf-8")

    run_record = build_run_record(
        stage="baselines",
        run_id=run_id,
        seed=seed,
        dataset_version=str(results.dataset.get("dataset_version", "")),
        record_count=int(results.dataset.get("n_records", 0)),
        code_commit=code_commit,
        content_hash=content_hash,
        timestamp=timestamp,
        canonical_verdict=canonical_verdict,
        environment=environment,
        extra={
            "detectors": sorted(results.detectors),
            "ranking": results.ranking,
            "confidence": results.confidence,
            "matching_policy": results.matching_policy,
        },
    )
    run_record_path = out / RUN_RECORD_NAME
    write_run_records([run_record], run_record_path)

    index = build_provenance_index(
        [results_path, run_record_path],
        harness_version=results.harness_version,
        generated_at=generated_at,
    )
    provenance_path = out / PROVENANCE_NAME
    write_provenance_index(index, provenance_path)

    return {"results": results_path, "run_record": run_record_path, "provenance": provenance_path}
