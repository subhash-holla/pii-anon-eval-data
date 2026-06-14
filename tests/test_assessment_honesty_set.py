"""CAP-02 — honesty-set completion (NFR-047): worst-language recall + rank-volatility.

The honesty set already ships the synthetic-only caveat, RD-NOT-CONVERGED, SMALL-N, and per-cell power. This
closes the two remaining members: (1) RANK-VOLATILITY via Kendall-τ across >= min_seeds (config: 3) seeded
reruns — a single/under-replicated run reports UNMEASURED rather than a false stability claim; (2) the
WORST-LANGUAGE recall floor surfaced explicitly so a high mean cannot hide a collapsed language.
"""
from __future__ import annotations

import pytest
from pii_anon_datasets.assessment import report as R
from pii_anon_datasets.stats import rank_stability as RS


# ---- Kendall-τ between rankings ----
def test_kendall_tau_identical_and_reversed() -> None:
    assert RS.kendall_tau_b(["A", "B", "C"], ["A", "B", "C"]) == pytest.approx(1.0)
    assert RS.kendall_tau_b(["A", "B", "C"], ["C", "B", "A"]) == pytest.approx(-1.0)


def test_kendall_tau_single_swap() -> None:
    # one adjacent swap out of 3 pairs -> tau = (2-1)/3
    assert RS.kendall_tau_b(["A", "B", "C"], ["B", "A", "C"]) == pytest.approx(1.0 / 3.0)


def test_kendall_tau_requires_same_items() -> None:
    with pytest.raises(ValueError):
        RS.kendall_tau_b(["A", "B"], ["A", "C"])


# ---- rank-volatility over seeds (UNMEASURED below min_seeds) ----
def test_rank_volatility_unmeasured_below_min_seeds() -> None:
    rv = RS.rank_volatility([["A", "B", "C"], ["A", "B", "C"]], min_seeds=3)
    assert rv.measured is False and rv.mean_tau is None
    assert "UNMEASURED" in rv.note and rv.n_seeds == 2


def test_rank_volatility_measured_stable() -> None:
    rv = RS.rank_volatility([["A", "B", "C"]] * 3, min_seeds=3)
    assert rv.measured is True and rv.mean_tau == pytest.approx(1.0) and rv.min_tau == pytest.approx(1.0)
    assert rv.n_seeds == 3


def test_rank_volatility_measured_volatile() -> None:
    rv = RS.rank_volatility([["A", "B", "C"], ["C", "B", "A"], ["A", "B", "C"]], min_seeds=3)
    assert rv.measured is True and rv.mean_tau < 1.0 and rv.min_tau == pytest.approx(-1.0)


# ---- worst-language recall floor (report surface) ----
def test_worst_language_recall() -> None:
    lang, rec = R.worst_language_recall({"en": 0.92, "sw": 0.41, "de": 0.88})
    assert lang == "sw" and rec == pytest.approx(0.41)


def test_worst_language_empty_is_none() -> None:
    assert R.worst_language_recall({}) is None


# ---- honesty-set flags bundle the two members non-strippably ----
def test_honesty_set_flags_include_both_members() -> None:
    rv = RS.rank_volatility([["A", "B"]] * 3, min_seeds=3)
    flags = R.honesty_set_flags(per_language_recall={"en": 0.9, "sw": 0.4}, rank_vol=rv)
    assert any("WORST-LANGUAGE" in f and "sw" in f for f in flags)
    assert any("Kendall" in f or "rank-volatility" in f.lower() for f in flags)


def test_honesty_set_flags_surface_unmeasured() -> None:
    rv = RS.rank_volatility([["A", "B"]], min_seeds=3)   # single seed -> UNMEASURED
    flags = R.honesty_set_flags(per_language_recall=None, rank_vol=rv)
    assert any("UNMEASURED" in f for f in flags)
