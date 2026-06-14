"""Paired McNemar variant selection — exact for small samples, χ² for large (NFR-002).

The exact two-sided binomial McNemar tail (``Σ C(n,i) · 0.5**n``) is correct for small discordant counts but
numerically INFEASIBLE for large ones: ``math.comb(n, i)`` is an astronomically large int and ``0.5**n``
underflows, so their product raises ``OverflowError: int too large to convert to float`` for ``n`` beyond
~1074. A real-systems assessment over ~15k gold positives hits exactly this. The selector uses the standard
large-sample Edwards continuity-corrected χ² test above a threshold, recording the method used.
"""
from __future__ import annotations

import pytest
from pii_anon_datasets.stats import paired as P


def test_selector_uses_exact_for_small_discordant() -> None:
    r = P.mcnemar(5, 3)
    assert r.method == "mcnemar-exact"
    assert 0.0 <= r.p_value <= 1.0


def test_selector_uses_chi2_for_large_discordant_no_overflow() -> None:
    # would OverflowError under the raw exact test; selector falls back to chi2-continuity
    r = P.mcnemar(3000, 2000)
    assert r.method == "mcnemar-chi2-continuity"
    assert 0.0 <= r.p_value <= 1.0  # finite, no overflow
    assert r.b == 3000 and r.c == 2000


def test_raw_exact_overflows_at_scale_documents_why_selector_exists() -> None:
    with pytest.raises(OverflowError):
        P.mcnemar_exact(3000, 2000)


def test_selector_boundary_threshold() -> None:
    # at/under the threshold -> exact; just over -> chi2
    assert P.mcnemar(600, 400).method == "mcnemar-exact"          # n=1000 <= default exact_max_n
    assert P.mcnemar(600, 401).method == "mcnemar-chi2-continuity"  # n=1001 > threshold


def test_selector_matches_exact_below_threshold() -> None:
    # the selector must equal the exact test for a small case (no behavior change at small n)
    assert P.mcnemar(8, 2).p_value == pytest.approx(P.mcnemar_exact(8, 2).p_value)
