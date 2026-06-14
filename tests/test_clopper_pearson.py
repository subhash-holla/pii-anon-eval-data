"""Clopper-Pearson exact binomial CI — S4-01 (FR-004, NFR-002).

Pure-stdlib exact interval via the inverse regularized incomplete beta. Every test
function carries an ``fr_004`` / ``nfr_002`` token (traceability gate). Cross-checks the
hand-rolled inverse-beta against textbook 95% values and asserts the CP interval is at
least as conservative as Wilson (reidx-02 integer guard reused from S1).
"""
from __future__ import annotations

import math

import pytest
from pii_anon_datasets.stats.intervals import (
    Interval,
    clopper_pearson_interval,
    wilson_interval,
)


def test_fr_004_clopper_pearson_textbook_values() -> None:
    """At 95%, the inverse-beta must reproduce the standard Clopper-Pearson table (4 d.p.)."""
    cp_0_10 = clopper_pearson_interval(0, 10)
    cp_1_10 = clopper_pearson_interval(1, 10)
    cp_10_10 = clopper_pearson_interval(10, 10)

    # (0, 10): low exactly 0, high ≈ 0.3085
    assert cp_0_10.low == pytest.approx(0.0, abs=1e-4)
    assert cp_0_10.high == pytest.approx(0.3085, abs=1e-4)

    # (1, 10): low ≈ 0.0025, high ≈ 0.4450
    assert cp_1_10.low == pytest.approx(0.0025, abs=1e-4)
    assert cp_1_10.high == pytest.approx(0.4450, abs=1e-4)

    # (10, 10): low ≈ 0.6915, high exactly 1.0
    assert cp_10_10.low == pytest.approx(0.6915, abs=1e-4)
    assert cp_10_10.high == pytest.approx(1.0, abs=1e-4)


def test_fr_004_clopper_pearson_brackets_point() -> None:
    """low <= k/n <= high for assorted (k, n); point is exactly k/n."""
    for k, n in [(1, 4), (3, 7), (5, 10), (17, 20), (2, 50), (49, 50)]:
        ci = clopper_pearson_interval(k, n)
        assert ci.point == k / n
        assert ci.low <= k / n <= ci.high
        assert 0.0 <= ci.low <= ci.high <= 1.0


def test_nfr_002_clopper_pearson_method_named() -> None:
    """NFR-002: the CI carries a NAMED method, surfaced via the dataclass and as_dict()."""
    ci = clopper_pearson_interval(3, 10)
    assert isinstance(ci, Interval)
    assert ci.method == "clopper-pearson"
    assert ci.as_dict()["method"] == "clopper-pearson"
    assert ci.confidence == 0.95


def test_fr_004_reidx02_clopper_pearson_integer_guard() -> None:
    """reidx-02: fractional / bool k or n raise TypeError (same guard as Wilson)."""
    with pytest.raises(TypeError):
        clopper_pearson_interval(1.0, 10)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        clopper_pearson_interval(1, 10.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        clopper_pearson_interval(True, 10)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        clopper_pearson_interval(1, True)  # type: ignore[arg-type]
    # the value guard (0 <= k <= n) also still fires
    with pytest.raises(ValueError):
        clopper_pearson_interval(11, 10)
    with pytest.raises(ValueError):
        clopper_pearson_interval(-1, 10)


def test_fr_004_clopper_pearson_edges() -> None:
    """n=0 sentinel; k=0 -> low exactly 0.0; k=n -> high exactly 1.0."""
    # n == 0 sentinel: point=nan, low=0, high=1, n=0
    z = clopper_pearson_interval(0, 0)
    assert math.isnan(z.point)
    assert z.low == 0.0
    assert z.high == 1.0
    assert z.n == 0
    assert z.method == "clopper-pearson"

    # k == 0 -> low is exactly 0.0 (no inverse-beta call on the low bound)
    assert clopper_pearson_interval(0, 17).low == 0.0
    # k == n -> high is exactly 1.0 (no inverse-beta call on the high bound)
    assert clopper_pearson_interval(17, 17).high == 1.0


def test_fr_004_clopper_pearson_is_conservative_vs_wilson() -> None:
    """PROPERTY: for 0 < k < n, the exact CP interval CONTAINS the Wilson interval.

    Clopper-Pearson is the conservative exact interval; correctly inverted, its lower
    bound must be <= Wilson's and its upper bound >= Wilson's (CP no narrower than Wilson).
    Doubles as a correctness check on the inverse-beta.
    """
    for k, n in [(1, 10), (3, 10), (5, 10), (7, 20), (13, 20), (2, 8), (49, 100)]:
        cp = clopper_pearson_interval(k, n)
        w = wilson_interval(k, n)
        assert cp.low <= w.low + 1e-12, f"CP.low not <= Wilson.low at ({k},{n})"
        assert cp.high >= w.high - 1e-12, f"CP.high not >= Wilson.high at ({k},{n})"


def test_fr_004_clopper_pearson_deterministic() -> None:
    """NFR-004: fixed iteration counts -> byte-identical bounds across repeated calls."""
    runs = [clopper_pearson_interval(7, 23, 0.95).as_dict() for _ in range(5)]
    first = runs[0]
    for r in runs[1:]:
        assert r == first
    # also stable at a non-tabulated confidence level
    runs_99 = [clopper_pearson_interval(7, 23, 0.99).as_dict() for _ in range(3)]
    assert runs_99[0] == runs_99[1] == runs_99[2]
