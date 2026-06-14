"""Governance-artifact pins (FR-026 / NFR-014) — GOVERNANCE.md must exist with the charter,
an aspirational (AGENT_SIMULATED) advisory roster, a CoI statement naming pii-anon-core, and an
honest bus-factor note. These pins make the governance checklist (NFR-014) continuously enforced.
"""
from __future__ import annotations

import pathlib

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_GOVERNANCE = _REPO_ROOT / "GOVERNANCE.md"


def _governance_text() -> str:
    assert _GOVERNANCE.exists(), "GOVERNANCE.md must exist at the repo root (FR-026)"
    return _GOVERNANCE.read_text(encoding="utf-8")


def test_fr_026_governance_md_has_charter_and_roster() -> None:
    """GOVERNANCE.md has a charter + an advisory roster flagged aspirational/AGENT_SIMULATED — [PROPERTY-TEST]."""
    low = _governance_text().lower()
    # charter / mission + decision process
    assert "charter" in low or "mission" in low
    assert "decision" in low
    # advisory body roster, explicitly flagged aspirational / AGENT_SIMULATED (honesty — no fabricated members)
    assert "advisory" in low
    assert ("aspirational" in low) or ("agent_simulated" in low) or ("agent-simulated" in low)


def test_fr_026_governance_md_has_coi_and_bus_factor() -> None:
    """GOVERNANCE.md names pii-anon-core in a CoI statement + states an honest bus-factor — [PROPERTY-TEST]."""
    text = _governance_text()
    low = text.lower()
    assert "conflict of interest" in low or "conflict-of-interest" in low
    assert "pii-anon-core" in low  # the maintaining affiliation is named
    assert "recus" in low  # the recusal control is referenced
    # honest bus-factor note: the term + the single-maintainer reality
    assert ("bus factor" in low) or ("bus-factor" in low)
    assert ("1" in text) or ("single maintainer" in low) or ("single-maintainer" in low)


def test_nfr_014_governance_md_present() -> None:
    """NFR-014 governance checklist: GOVERNANCE.md + advisory roster + CoI statement all present — [PROPERTY-TEST]."""
    low = _governance_text().lower()
    assert "# governance" in low
    assert "advisory" in low
    assert "conflict of interest" in low or "conflict-of-interest" in low
    # the neutrality controls (held-out store / anti-gaming / recusal) are referenced
    assert ("held-out" in low) or ("held out" in low) or ("leaderboard" in low)
