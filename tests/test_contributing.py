"""Contribution-pipeline pins (FR-025) — CONTRIBUTING.md must exist with a PR template, a CC0
license-compatibility checklist, a provenance / synthetic-only gate (AX-001), a deprecation/erratum
policy, and a semantic-versioned dated-release policy.
"""
from __future__ import annotations

import pathlib

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_CONTRIBUTING = _REPO_ROOT / "CONTRIBUTING.md"


def _contributing_text() -> str:
    assert _CONTRIBUTING.exists(), "CONTRIBUTING.md must exist at the repo root (FR-025)"
    return _CONTRIBUTING.read_text(encoding="utf-8")


def test_fr_025_contributing_has_pr_template_and_cc0() -> None:
    """CONTRIBUTING.md has a PR template + a CC0 license-compatibility checklist — [PROPERTY-TEST]."""
    low = _contributing_text().lower()
    assert ("pull-request" in low) or ("pull request" in low) or ("pr template" in low)
    assert "template" in low
    assert "cc0" in low
    assert "license" in low
    assert "apache" in low  # the code-Apache-2.0 / data-CC0 split is stated


def test_fr_025_contributing_has_provenance_and_synthetic_only() -> None:
    """CONTRIBUTING.md requires provenance + synthetic-only (no real PII, AX-001) — [PROPERTY-TEST]."""
    low = _contributing_text().lower()
    assert "provenance" in low
    assert "synthetic" in low
    assert ("no real pii" in low) or ("real pii" in low) or ("real personal" in low)


def test_fr_025_contributing_has_deprecation_and_semver() -> None:
    """CONTRIBUTING.md has a deprecation/erratum policy + semver dated releases — [PROPERTY-TEST]."""
    low = _contributing_text().lower()
    assert ("deprecat" in low) and ("erratum" in low or "errata" in low)
    assert ("semantic version" in low) or ("semver" in low)
    assert ("dated" in low) or ("release" in low)
