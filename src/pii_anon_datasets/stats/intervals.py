"""Confidence intervals for proportions.

NFR-002: every published metric carries n + a CI with the **method named**.
Implements the **Wilson score interval** (the method named in the R9 audit) in pure
stdlib (deterministic, no heavy deps — NFR-004).

reidx-02 fix: the interval REQUIRES integer (k, n) Bernoulli counts. Fractional /
partial-credit counts are a TypeError — they must never feed a binomial CI.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# z critical values for common two-sided confidence levels
_Z = {0.90: 1.6448536269514722, 0.95: 1.959963984540054, 0.99: 2.5758293035489004}


@dataclass(frozen=True)
class Interval:
    point: float
    low: float
    high: float
    n: int
    method: str
    confidence: float

    def as_dict(self) -> dict:
        return {
            "point": self.point,
            "low": self.low,
            "high": self.high,
            "n": self.n,
            "method": self.method,
            "confidence": self.confidence,
        }


def _require_int_counts(k: int, n: int, fname: str) -> None:
    """reidx-02 guard: (k, n) must be honest integer Bernoulli counts with 0 <= k <= n.

    Shared by ``wilson_interval`` and ``clopper_pearson_interval``. ``bool`` is rejected
    (it is an ``int`` subclass but not an honest count). Raises ``TypeError`` for
    non-integer / bool inputs and ``ValueError`` for out-of-range counts.
    """
    if not (isinstance(k, int) and isinstance(n, int)) or isinstance(k, bool) or isinstance(n, bool):
        raise TypeError(
            f"{fname} requires integer k and n (no fractional/partial counts) — reidx-02."
        )
    if n < 0 or k < 0 or k > n:
        raise ValueError(f"require 0 <= k <= n; got k={k}, n={n}")


def _z(confidence: float) -> float:
    if confidence in _Z:
        return _Z[confidence]
    # Winitzki inverse-erf approximation for uncommon confidence levels
    x = 2.0 * ((1.0 + confidence) / 2.0) - 1.0
    a = 0.147
    ln = math.log(1.0 - x * x)
    t = 2.0 / (math.pi * a) + ln / 2.0
    return math.sqrt(2.0) * math.copysign(math.sqrt(math.sqrt(t * t - ln / a) - t), x)


def wilson_interval(k: int, n: int, confidence: float = 0.95) -> Interval:
    """Wilson score interval for *k* successes in *n* integer Bernoulli trials."""
    _require_int_counts(k, n, "wilson_interval")
    if n == 0:
        return Interval(float("nan"), 0.0, 1.0, 0, "wilson", confidence)
    z = _z(confidence)
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return Interval(p, max(0.0, center - half), min(1.0, center + half), n, "wilson", confidence)


# ── Inverse regularized incomplete beta (pure stdlib; NFR-004) ──────────────────
# Used by clopper_pearson_interval. No scipy/numpy: the regularized incomplete beta
# I_x(a, b) is evaluated via the Lentz continued fraction (Numerical Recipes §6.4),
# and inverted by bisection. All loops have FIXED iteration counts → deterministic.

_BETACF_MAXIT = 200  # continued-fraction iterations (converges to tol well before this)
_BETACF_TOL = 1e-12
_INV_BETAINC_ITERS = 60  # bisection steps; 2**-60 ≈ 8.7e-19 << any reported precision


def _betacf(a: float, b: float, x: float) -> float:
    """Continued-fraction expansion for the incomplete beta function (Lentz's method)."""
    tiny = 1e-30
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, _BETACF_MAXIT + 1):
        m2 = 2 * m
        # even step
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        # odd step
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _BETACF_TOL:
            break
    return h


def _betainc(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a, b) on x in [0, 1] (pure stdlib via lgamma)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    # log of the front factor x**a * (1-x)**b / B(a, b)
    ln_front = (
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log(1.0 - x)
    )
    front = math.exp(ln_front)
    # use the continued fraction in its region of fast convergence; else the symmetry swap
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def _inv_betainc(p: float, a: float, b: float) -> float:
    """Inverse of I_x(a, b): the x in [0, 1] with I_x(a, b) == p, via bisection.

    Bisection (not Newton) is dependency-free, monotone-safe, and robust at the
    a→small / b→small edges. The FIXED iteration count makes the result deterministic
    (NFR-004) — no RNG, no convergence-dependent early exit that could vary by platform.
    """
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(_INV_BETAINC_ITERS):
        mid = 0.5 * (lo + hi)
        if _betainc(a, b, mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def clopper_pearson_interval(k: int, n: int, confidence: float = 0.95) -> Interval:
    """Exact Clopper-Pearson binomial CI for *k* successes in *n* integer trials.

    The conservative exact interval (guaranteed >= nominal coverage), bounded by Beta
    quantiles: low = B^{-1}(α/2; k, n-k+1), high = B^{-1}(1-α/2; k+1, n-k), computed via
    the hand-rolled inverse regularized incomplete beta (NFR-004, pure stdlib). Integer-
    guarded identically to ``wilson_interval`` (reidx-02); ``method == "clopper-pearson"``
    (NFR-002). ``k == 0`` pins low to exactly 0.0 and ``k == n`` pins high to exactly 1.0.
    """
    _require_int_counts(k, n, "clopper_pearson_interval")
    if n == 0:
        return Interval(float("nan"), 0.0, 1.0, 0, "clopper-pearson", confidence)
    alpha = 1.0 - confidence
    low = 0.0 if k == 0 else _inv_betainc(alpha / 2.0, k, n - k + 1)
    high = 1.0 if k == n else _inv_betainc(1.0 - alpha / 2.0, k + 1, n - k)
    point = k / n
    return Interval(point, low, high, n, "clopper-pearson", confidence)
