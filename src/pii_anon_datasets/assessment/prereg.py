"""Pre-registration of the assessment run (CAP-02 DC-24 / FR-044/050; AX-005 element 4).

The ``prereg_hash`` is a sha256 over the canonical design-and-analysis PLAN ONLY (never the wall-clock), so a
report can prove plan-equality regardless of WHEN the run was registered. :func:`verify_prereg` recomputes the
hash over the stored plan and compares to ``prereg_hash`` — a tampered plan fails (FR-050 recomputed-equality,
not a self-asserted boolean). Pure-stdlib; pre-registration is opt-in rigor (manifest-reproducibility is the
universal floor), so the plan is small + explicit.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence

PREREG_SCHEMA = "pii-anon-assessment-prereg/v1"


def _plan_hash(plan: dict) -> str:
    return hashlib.sha256(json.dumps(plan, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def build_prereg(
    *,
    manifest_hash: str,
    seed: int,
    systems: Sequence[str],
    metrics: Sequence[str],
    run_type: str,
    code_commit: str,
    timestamp: str,
    interval_rule: dict | None = None,
    multiplicity: str = "holm-bonferroni",
    design_point: dict | None = None,
) -> dict:
    """Build the immutable pre-registration record. ``prereg_hash`` covers the plan only (FR-050)."""
    plan = {
        "manifest_hash": manifest_hash,
        "seed": seed,
        "systems": list(systems),
        "metrics": list(metrics),
        "run_type": run_type,
        "interval_rule": interval_rule or {},
        "multiplicity": multiplicity,
        "design_point": design_point or {},
    }
    return {
        "schema": PREREG_SCHEMA,
        "prereg_hash": _plan_hash(plan),
        "created_utc": timestamp,
        "code_commit": code_commit,
        "run_type": run_type,
        "design_and_analysis_plan": plan,
    }


def verify_prereg(prereg: dict) -> bool:
    """Recompute the plan-hash and compare to the stored ``prereg_hash`` (FR-050 recomputed-equality)."""
    return _plan_hash(prereg["design_and_analysis_plan"]) == prereg["prereg_hash"]
