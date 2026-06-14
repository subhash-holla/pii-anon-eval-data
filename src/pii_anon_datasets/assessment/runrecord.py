"""Per-stage observability run-records (CAP-02 DC-25 / FR-045/046; NFR-042/043).

Reuses the verified ``scripts/benchmark_throughput.py`` run-record pattern: a schema id, ``harness_version``,
an INJECTABLE ``timestamp`` (byte-reproducible fixtures), and a ``provenance`` block
``{is_reference_host, environment, canonical_verdict}``. One write-once record per spine stage
(``load / sample / run / score / rate / report``) under a shared ``run_id`` (NFR-042). Pure-stdlib.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

RUNRECORD_SCHEMA = "pii-anon-assessment-runrecord/v1"
HARNESS_VERSION = "1.0.0"


def build_run_record(
    *,
    stage: str,
    run_id: str,
    seed: int,
    dataset_version: str,
    record_count: int,
    code_commit: str,
    content_hash: str,
    timestamp: str,
    canonical_verdict: str = "INDICATIVE",
    environment: str = "agent-execution-sandbox",
    extra: Mapping[str, object] | None = None,
) -> dict:
    """One spine-stage run-record. ``canonical_verdict`` defaults to INDICATIVE (agent-env / lightweight
    systems — the academic-soundness machinery is exercised, but a real-detector, reference-host run is the
    Pass-2 item; never over-claimed)."""
    record: dict[str, object] = {
        "schema": RUNRECORD_SCHEMA,
        "harness_version": HARNESS_VERSION,
        "timestamp": timestamp,
        "run_id": run_id,
        "stage": stage,
        "seed": seed,
        "dataset_version": dataset_version,
        "record_count": record_count,
        "code_commit": code_commit,
        "content_hash": content_hash,
        "provenance": {
            "is_reference_host": False,
            "environment": environment,
            "canonical_verdict": canonical_verdict,
        },
    }
    if extra:
        record["extra"] = dict(extra)
    return record


def write_run_records(records: list[dict], path: str | Path) -> Path:
    """Write the per-stage records as deterministic JSONL (sorted keys), one per line."""
    out = Path(path)
    out.write_text(
        "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )
    return out
