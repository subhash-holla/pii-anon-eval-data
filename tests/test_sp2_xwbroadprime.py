"""Task 6 — XW-BROAD-PRIME third crosswalk (NIST SP 800-122, EX-01b)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import coverage_decomposition as cd  # noqa: E402


def test_xw_broad_prime_nist_strict_date_only():
    # XW-BROAD' is NIST-strict: DATE (identifier) granted; NORP/NRP (linkable, not identifier) NOT granted.
    # That makes its reach strictly BETWEEN XW-EXACT and XW-BROAD — a genuinely distinct third crosswalk.
    assert "XW-BROAD-PRIME" in cd.CROSSWALKS
    reg_det = {"reachable_types": ["PERSON_NAME"], "dropped_native": ["DATE", "NORP", "MISC"]}
    base = cd.reachable_set(reg_det, "XW-EXACT")
    prime = cd.reachable_set(reg_det, "XW-BROAD-PRIME")
    broad = cd.reachable_set(reg_det, "XW-BROAD")
    assert base <= prime <= broad and prime != broad  # strictly between EXACT and BROAD
    assert "DATE_OF_BIRTH" in prime          # DATE granted (NIST identifier)
    assert "ETHNICITY" not in prime          # NORP NOT granted (linkable, not identifier) — the distinction
    assert "ETHNICITY" in broad              # ...whereas XW-BROAD does grant it
    assert "MISC" not in prime               # unmapped native dropped, not granted
