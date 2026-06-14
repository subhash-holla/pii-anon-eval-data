"""Real-data validation correlation harness (FR-027; DC-14, v1.1 SEAM).

Given paired *synthetic* and *real* detector scores, produce a pre-registered
**Kendall-tau (tau-b)** / **Spearman rho** point estimate, a **seeded bootstrap CI** for each,
and a **Bland-Altman** agreement view (mean per-pair difference +/- 1.96.sd limits). The crux is
**epistemic honesty**: the real i2b2-2014 / TAB corpus is NOT present in this repository
(licensing), so when the real scores are absent :func:`correlate` returns a
:class:`RealDataAbsent` sentinel and **NEVER fabricates** a correlation (FR-027). Every
:class:`CorrelationResult` carries a non-strippable "synthetic agreement != external validity"
caveat; the synthetic->real transfer delta is explicitly a real-data Pass-2 item.

Pure-stdlib (``math`` + ``random.Random`` only — NFR-004). Determinism is load-bearing
(AX-002): the bootstrap owns a **local** ``random.Random(seed)`` instance and never touches the
module-global RNG, so two runs with the same seed are byte-identical (mirrors
``stats/paired.py``).
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass

# A pair-statistic: maps two equal-length float sequences to a scalar (tau / rho). The bootstrap
# is generic over it so tau_ci and rho_ci share one seeded-resample driver.
_PairStat = Callable[[Sequence[float], Sequence[float]], float]

REAL_DATA_ABSENT_NOTE: str = (
    "Real i2b2-2014 / TAB data is NOT present in this repository (licensing). The synthetic-vs-real "
    "correlation requires a real-data Pass-2; this harness REFUSES to fabricate a correlation (FR-027)."
)
CORRELATION_CAVEAT: str = (
    "Pre-registered Kendall-tau / Spearman with seeded bootstrap CI + Bland-Altman. Synthetic-distribution "
    "agreement is NOT external validity (FR-027); the synthetic->real transfer delta is a real-data Pass-2 item."
)


@dataclass(frozen=True)
class RealDataAbsent:
    """Sentinel — real-data scores absent; NEVER a fabricated correlation (FR-027)."""

    available: bool = False
    note: str = REAL_DATA_ABSENT_NOTE

    def __post_init__(self) -> None:
        if not self.note.strip():
            raise ValueError("real-data-absent note required (FR-027 non-strippable)")


@dataclass(frozen=True)
class CorrelationResult:
    """Synthetic-vs-real correlation: Kendall-tau / Spearman rho + seeded CIs + Bland-Altman.

    ``tau_ci`` / ``rho_ci`` are seeded-bootstrap percentile CIs (local ``random.Random(seed)``);
    ``bland_altman_mean_diff`` and ``bland_altman_limits`` summarise the per-pair agreement.
    The ``caveat`` is non-strippable (FR-027): synthetic agreement is NOT external validity.
    """

    n: int
    kendall_tau: float
    spearman_rho: float
    tau_ci: tuple[float, float]
    rho_ci: tuple[float, float]
    bland_altman_mean_diff: float
    bland_altman_limits: tuple[float, float]
    method: str = "kendall-spearman-bootstrap-blandaltman"
    caveat: str = CORRELATION_CAVEAT

    def __post_init__(self) -> None:
        if not self.caveat.strip():
            raise ValueError("correlation caveat required (FR-027 non-strippable)")


def _average_ranks(values: Sequence[float]) -> list[float]:
    """Fractional (mid-) ranks of ``values``: tied values share the mean of their rank block."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        # ranks i..j (0-based) are tied -> assign the average 1-based rank of the block
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def kendall_tau(x: Sequence[float], y: Sequence[float]) -> float:
    """Kendall tau-b (concordant - discordant, tie-corrected); pure-stdlib.

    ``tau_b = (n_c - n_d) / sqrt((n_0 - n_x) * (n_0 - n_y))`` where ``n_0 = n(n-1)/2``, ``n_x``
    / ``n_y`` are the tie-correction sums over x / y, and ``n_c`` / ``n_d`` count concordant /
    discordant pairs. A perfectly-concordant pair -> +1.0; perfectly-discordant -> -1.0. The
    denominator is 0 only when one variable is constant -> tau is undefined, reported as 0.0.
    """
    n = len(x)
    n_c = 0
    n_d = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            s = (dx > 0) - (dx < 0)
            t = (dy > 0) - (dy < 0)
            prod = s * t
            if prod > 0:
                n_c += 1
            elif prod < 0:
                n_d += 1
            # prod == 0 -> a tie in x and/or y: contributes to neither n_c nor n_d (tau-b)
    n0 = n * (n - 1) // 2
    n_x = sum(c * (c - 1) // 2 for c in _tie_counts(x))
    n_y = sum(c * (c - 1) // 2 for c in _tie_counts(y))
    denom = math.sqrt((n0 - n_x) * (n0 - n_y))
    if denom == 0.0:
        return 0.0
    return (n_c - n_d) / denom


def _tie_counts(values: Sequence[float]) -> list[int]:
    """Group sizes of equal values in ``values`` (for the Kendall tau-b tie correction)."""
    counts: dict[float, int] = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return list(counts.values())


def spearman_rho(x: Sequence[float], y: Sequence[float]) -> float:
    """Spearman rho = Pearson correlation on ranks (average ranks for ties).

    Ranks both vectors with fractional mid-ranks (so ties are handled), then returns the
    Pearson product-moment correlation of the rank vectors. Monotone-increasing pair -> +1.0;
    monotone-decreasing -> -1.0. A constant rank vector makes the denominator 0 -> rho is
    undefined, reported as 0.0.
    """
    rx = _average_ranks(x)
    ry = _average_ranks(y)
    return _pearson(rx, ry)


def _pearson(a: Sequence[float], b: Sequence[float]) -> float:
    """Pearson product-moment correlation of ``a`` and ``b`` (0.0 if either is constant)."""
    n = len(a)
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    cov = sum((a[i] - mean_a) * (b[i] - mean_b) for i in range(n))
    var_a = sum((a[i] - mean_a) ** 2 for i in range(n))
    var_b = sum((b[i] - mean_b) ** 2 for i in range(n))
    denom = math.sqrt(var_a * var_b)
    if denom == 0.0:
        return 0.0
    return cov / denom


def bland_altman(x: Sequence[float], y: Sequence[float]) -> tuple[float, tuple[float, float]]:
    """(mean difference, (mean - 1.96*sd, mean + 1.96*sd)) of the per-pair differences.

    The per-pair difference is ``x[i] - y[i]``; ``mean_diff`` is their mean and the limits of
    agreement are ``mean_diff +/- 1.96 * sd`` (sample sd, ddof=1). A single pair has no spread
    -> sd 0.0 -> the limits collapse onto ``mean_diff``.
    """
    n = len(x)
    diffs = [x[i] - y[i] for i in range(n)]
    mean_diff = sum(diffs) / n
    if n < 2:
        return (mean_diff, (mean_diff, mean_diff))
    var = sum((d - mean_diff) ** 2 for d in diffs) / (n - 1)
    sd = math.sqrt(var)
    return (mean_diff, (mean_diff - 1.96 * sd, mean_diff + 1.96 * sd))


def _bootstrap_ci(
    x: Sequence[float],
    y: Sequence[float],
    stat: _PairStat,
    *,
    seed: int,
    n_boot: int = 1000,
    alpha: float = 0.05,
) -> tuple[float, float]:
    rng = random.Random(seed)  # LOCAL instance — never the module-global RNG (NFR-004 / AX-002)
    n = len(x)
    stats_: list[float] = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        stats_.append(stat([x[i] for i in idx], [y[i] for i in idx]))
    stats_.sort()
    lo = stats_[int((alpha / 2) * n_boot)]
    hi = stats_[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    return (lo, hi)


def correlate(
    synthetic_scores: Sequence[float],
    real_scores: Sequence[float] | None = None,
    *,
    seed: int = 0,
    n_boot: int = 1000,
) -> CorrelationResult | RealDataAbsent:
    """Correlate synthetic vs real scores. Absent real scores -> RealDataAbsent (NEVER fabricate)."""
    if not real_scores:  # None or empty: do NOT fabricate
        return RealDataAbsent()
    x, y = list(synthetic_scores), list(real_scores)
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("correlate needs >=2 paired scores of equal length")
    mean_diff, limits = bland_altman(x, y)
    return CorrelationResult(
        n=len(x),
        kendall_tau=kendall_tau(x, y),
        spearman_rho=spearman_rho(x, y),
        tau_ci=_bootstrap_ci(x, y, kendall_tau, seed=seed, n_boot=n_boot),
        rho_ci=_bootstrap_ci(x, y, spearman_rho, seed=seed, n_boot=n_boot),
        bland_altman_mean_diff=mean_diff,
        bland_altman_limits=limits,
    )
