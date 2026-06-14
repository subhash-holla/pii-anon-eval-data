"""Tests for stats.intervals (NFR-002 Wilson CI; reidx-02 integer-count guard)."""
import math

import pytest

from pii_anon_datasets.stats.intervals import Interval, wilson_interval


def test_wilson_point_and_brackets():
    iv = wilson_interval(98, 100, 0.95)
    assert iv.point == pytest.approx(0.98)
    assert iv.method == "wilson"
    assert iv.n == 100
    # interval brackets the point and stays within [0, 1]
    assert 0.0 <= iv.low < iv.point < iv.high <= 1.0
    # known Wilson 98/100 @95% ≈ [0.930, 0.995]
    assert iv.low == pytest.approx(0.930, abs=0.01)
    assert iv.high == pytest.approx(0.995, abs=0.01)


def test_wilson_half_symmetry_at_half():
    iv = wilson_interval(50, 100, 0.95)
    assert iv.point == pytest.approx(0.5)
    # Wilson is symmetric about 0.5 when p̂ = 0.5
    assert (iv.point - iv.low) == pytest.approx(iv.high - iv.point, abs=1e-9)


def test_integer_counts_required_reidx02():
    # fractional/partial counts must NEVER feed a binomial CI
    with pytest.raises(TypeError):
        wilson_interval(98.5, 100)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        wilson_interval(98, 100.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        wilson_interval(True, 100)  # bool is not an honest count


def test_bounds_validation():
    with pytest.raises(ValueError):
        wilson_interval(101, 100)
    with pytest.raises(ValueError):
        wilson_interval(-1, 100)


def test_zero_n_is_nan_point_full_interval():
    iv = wilson_interval(0, 0)
    assert math.isnan(iv.point)
    assert (iv.low, iv.high) == (0.0, 1.0)


def test_determinism():
    a = wilson_interval(753, 1000)
    b = wilson_interval(753, 1000)
    assert a == b  # frozen dataclass, pure-stdlib → byte-identical (NFR-004)
