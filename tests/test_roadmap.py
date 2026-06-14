"""Roadmap pins (FR-018/019/020) — ROADMAP.md must document the deferred agentic-leakage items
as future v1.x roadmap (NOT shipped in v1), anchored to the v1 seams (oracle + payloads). Honest
scoping: the roadmap must not claim these are implemented.
"""
from __future__ import annotations

import pathlib

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_ROADMAP = _REPO_ROOT / "ROADMAP.md"


def _roadmap_text() -> str:
    assert _ROADMAP.exists(), "ROADMAP.md must exist at the repo root"
    return _ROADMAP.read_text(encoding="utf-8")


def test_fr_018_fr_019_fr_020_roadmap_documents_deferred_items() -> None:
    """ROADMAP.md names FR-018/019/020 and describes each deferred item — [PROPERTY-TEST]."""
    text = _roadmap_text()
    low = text.lower()
    for fr in ("FR-018", "FR-019", "FR-020"):
        assert fr in text, f"ROADMAP.md must name {fr}"
    # each item is described (cross-turn fragmented leakage / transcript-residual / live-harness)
    assert ("cross-turn" in low) or ("fragmented" in low)
    assert "transcript" in low
    assert ("live-harness" in low) or ("live harness" in low) or ("agentdojo" in low) or ("injecagent" in low)


def test_fr_020_roadmap_frames_items_as_future_not_shipped() -> None:
    """ROADMAP.md frames FR-018/019/020 as future v1.x — NOT implemented in v1 (honest) — [PROPERTY-TEST]."""
    low = _roadmap_text().lower()
    assert "roadmap" in low
    assert ("v1.x" in low) or ("future" in low) or ("not implemented" in low) or ("not shipped" in low)
    # anchored to the v1 seams (oracle / payloads) the agentic direction builds on
    assert ("oracle" in low) and ("payload" in low)
