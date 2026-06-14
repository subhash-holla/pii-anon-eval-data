"""Tests for stats/multitest.py — Holm–Bonferroni step-down multiplicity correction.

CAP-02 DC-22 / NFR-027 (S8). Holm is the net-new audited multiplicity primitive (verified absent from
``stats/`` at design time). It is applied by the report layer WITHIN each (metric, scoring-family) partition;
this module is partition-agnostic — it corrects ONE family of p-values at a time. Pure-stdlib + deterministic,
matching the ``stats/`` house style (cf. paired.py / intervals.py).
"""
from __future__ import annotations

import pytest
from pii_anon_datasets.stats.multitest import HolmResult, holm_bonferroni


def test_empty_family() -> None:
    """An empty family is the identity: family_size 0, no rejections, no error."""
    res = holm_bonferroni({})
    assert isinstance(res, HolmResult)
    assert res.family_size == 0
    assert res.labels == ()
    assert res.p_adjusted == ()
    assert res.rejected == ()
    assert res.method == "holm-bonferroni"


def test_single_hypothesis_is_uncorrected() -> None:
    """With m=1 the Holm factor is 1, so the adjusted p equals the raw p (clipped to 1)."""
    res = holm_bonferroni({"a__vs__b__recall": 0.03}, alpha=0.05)
    assert res.family_size == 1
    assert res.p_adjusted == (pytest.approx(0.03),)
    assert res.rejected == (True,)
    res2 = holm_bonferroni({"x": 0.20}, alpha=0.05)
    assert res2.rejected == (False,)


def test_known_three_hypothesis_stepdown() -> None:
    """Worked Holm example p=[0.01,0.04,0.03], alpha=0.05, m=3.

    Sorted ascending: 0.01 (factor 3) -> 0.03; 0.03 (factor 2) -> 0.06; 0.04 (factor 1) -> 0.04,
    monotone-clamped up to 0.06. Adjusted in INPUT order = [0.03, 0.06, 0.06]; only the smallest
    (0.01) is rejected at 0.05 (Holm stops at the first threshold failure).
    """
    res = holm_bonferroni({"h1": 0.01, "h2": 0.04, "h3": 0.03}, alpha=0.05)
    assert res.labels == ("h1", "h2", "h3")
    assert res.p_adjusted[0] == pytest.approx(0.03)
    assert res.p_adjusted[1] == pytest.approx(0.06)
    assert res.p_adjusted[2] == pytest.approx(0.06)
    assert res.rejected == (True, False, False)


def test_all_reject_when_all_tiny() -> None:
    res = holm_bonferroni({"a": 0.0001, "b": 0.0002, "c": 0.0003}, alpha=0.05)
    assert res.rejected == (True, True, True)


def test_adjusted_p_is_monotone_in_rank_order() -> None:
    """Holm adjusted p-values are non-decreasing along ascending raw-p order (the step-down clamp)."""
    res = holm_bonferroni({"a": 0.001, "b": 0.2, "c": 0.04, "d": 0.5})
    by_raw = sorted(zip(res.p_raw, res.p_adjusted))
    adj_in_order = [adj for _, adj in by_raw]
    assert adj_in_order == sorted(adj_in_order)


def test_adjusted_never_exceeds_one() -> None:
    res = holm_bonferroni({"a": 0.9, "b": 0.8, "c": 0.95})
    assert all(0.0 <= p <= 1.0 for p in res.p_adjusted)


def test_input_order_preserved() -> None:
    """Output tuples are in INPUT order (not sorted), so callers can zip with their labels."""
    res = holm_bonferroni({"z": 0.5, "a": 0.001})
    assert res.labels == ("z", "a")
    assert res.p_raw == (pytest.approx(0.5), pytest.approx(0.001))


def test_deterministic() -> None:
    """No RNG — repeated calls are byte-identical (AX-002)."""
    pv = {"a": 0.01, "b": 0.049, "c": 0.5}
    assert holm_bonferroni(pv).as_dict() == holm_bonferroni(pv).as_dict()


def test_rejects_p_value_out_of_range() -> None:
    with pytest.raises(ValueError):
        holm_bonferroni({"a": 1.5})
    with pytest.raises(ValueError):
        holm_bonferroni({"a": -0.01})


def test_rejects_bad_alpha() -> None:
    with pytest.raises(ValueError):
        holm_bonferroni({"a": 0.01}, alpha=0.0)
    with pytest.raises(ValueError):
        holm_bonferroni({"a": 0.01}, alpha=1.0)


def test_as_dict_shape() -> None:
    res = holm_bonferroni({"a": 0.01, "b": 0.2}, alpha=0.05)
    d = res.as_dict()
    assert set(d) == {"labels", "p_raw", "p_adjusted", "rejected", "family_size", "alpha", "method"}
    assert d["family_size"] == 2
    assert d["method"] == "holm-bonferroni"
    assert d["alpha"] == pytest.approx(0.05)


def test_sequence_of_pairs_accepted() -> None:
    """A sequence of (label, p) pairs is accepted as well as a mapping (caller convenience)."""
    res = holm_bonferroni([("a", 0.01), ("b", 0.2)], alpha=0.05)
    assert res.labels == ("a", "b")
    assert res.rejected[0] is True


def test_holm_uniformly_more_powerful_than_bonferroni() -> None:
    """Sanity: Holm rejects at least as many as plain Bonferroni (adjusted_holm <= m*p)."""
    pv = {"a": 0.01, "b": 0.02, "c": 0.03}
    res = holm_bonferroni(pv)
    m = res.family_size
    for praw, padj in zip(res.p_raw, res.p_adjusted):
        assert padj <= min(1.0, m * praw) + 1e-12
