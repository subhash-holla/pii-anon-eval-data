"""The L1 SEAM — the reproducible sample manifest (CAP-02 DC-19 / FR-034 / NFR-030).

The sole cross-process data coupling: the eval-data sampler WRITES it; the pii-rate-elo assessment adapter
READS it and scores ONLY its ``record_ids``. Canonical-form JSON (sorted keys + compact separators + trailing
newline) so a re-draw under the same ``{corpus content_hash, lattice_version, seed}`` is byte-identical
(AX-002 / NFR-030). Carries a NON-STRIPPABLE synthetic-only caveat (AX-001/003) — :func:`build_manifest`
raises on an empty caveat (mirrors ``scoring.detection.DesignProvenance`` / ``subsets.slices.Slice``).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # avoid an import cycle; SampleResult is only needed for typing
    from .sample import SampleResult

SCHEMA = "pii-anon-assessment-manifest/v1"

# Non-strippable synthetic-only / anti-anonymity caveat (AX-001/003), mirroring scoring.detection.DESIGN_CAVEAT.
ASSESSMENT_CAVEAT = (
    "Synthetic-only (AX-001): every scored record contains ONLY synthetic PII. Per-cell power is statistical "
    "precision on the SYNTHETIC distribution, conditional on THIS sample — NOT external validity and NOT a "
    "standalone recall claim absent the real-data correlation slice (cycle-1 UC-13). AX-003."
)


def build_manifest(
    result: SampleResult,
    *,
    corpus_content_hash: str,
    code_commit: str,
    caveat: str = ASSESSMENT_CAVEAT,
) -> dict:
    """Assemble the manifest DTO from a :class:`SampleResult`. Raises ``ValueError`` on an empty caveat."""
    if not caveat or not caveat.strip():
        raise ValueError("sample manifest requires a non-empty synthetic-only caveat (AX-001/003)")
    per_cell_draw = [
        {
            "cell_id": c.cell_id,
            "tier": c.tier,
            "target_n": c.target_n,
            "realized_positive_count": c.realized_positive_count,
            "full_positive_count": c.full_positive_count,
            "power_class": c.power_class.value,
            "power_operating_point": c.power_operating_point,
            "realized_positive_shortfall": c.realized_positive_shortfall,
            "dimensions": dict(c.dimensions),
        }
        for c in result.per_cell
    ]
    return {
        "schema": SCHEMA,
        "preset": result.preset,
        "run_type": result.run_type,
        "inferential_target": result.inferential_target,
        "power_verdict": result.verdict,
        "record_count": len(result.record_ids),
        "record_ids": list(result.record_ids),
        "per_cell_draw": per_cell_draw,
        "repro": {**result.repro, "corpus_content_hash": corpus_content_hash},
        "provenance": {"code_commit": code_commit, "producer_schema": SCHEMA},
        "caveat": caveat,
    }


def to_canonical_json(manifest: dict) -> str:
    """Deterministic canonical form: sorted keys + compact separators + trailing newline (NFR-030)."""
    return json.dumps(manifest, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def write_manifest(manifest: dict, path: str | Path) -> Path:
    out = Path(path)
    out.write_text(to_canonical_json(manifest), encoding="utf-8")
    return out


def read_manifest(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
