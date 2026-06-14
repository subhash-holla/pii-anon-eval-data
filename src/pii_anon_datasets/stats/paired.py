"""Paired statistics for detector A/B regression (FR-002, measurement side).

The benchmark's primary use compares two detectors **A** and **B** on the *same* gold
spans, so A/B regression must use a **paired** test — not a CI-overlap heuristic
(sampling-design.md §3.2; the two-gate distinction). This module supplies:

* **McNemar's test** over the discordant pairs ``(b, c)`` — both the *exact* two-sided
  binomial tail and the Edwards *continuity-corrected* χ² approximation, each tagged with
  a named method (NFR-002).
* a **seeded paired bootstrap** for the recall-difference confidence interval, reported as
  an :class:`~pii_anon_datasets.stats.intervals.Interval` with ``method == "paired-bootstrap"``.

Pure-stdlib (``math`` + ``random.Random`` only — NFR-004). Determinism is load-bearing: the
bootstrap owns a **local** ``random.Random(seed)`` instance and never touches the module-global
RNG, so two runs with the same seed are byte-identical (and the global RNG state is irrelevant).

This is the *measurement* realisation of the S-PWR design-time sizer
``power.py::required_discordant_pairs`` (Lachin): that sizes the discordant count needed; this
evaluates the discordant pairs once observed.
"""
from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass

from .intervals import Interval


@dataclass(frozen=True)
class McNemarResult:
    """Outcome of a McNemar paired test over discordant pairs ``(b, c)``.

    ``b`` = (A-hit & B-miss), ``c`` = (A-miss & B-hit). Concordant pairs (both hit / both
    miss) carry no information about a difference and are excluded by construction.
    """

    b: int
    c: int
    statistic: float
    p_value: float
    method: str  # "mcnemar-exact" | "mcnemar-chi2-continuity" | "mcnemar-chi2"
    odds_ratio: float | None  # b / c; None when c == 0 (undefined)

    def as_dict(self) -> dict[str, object]:
        return {
            "b": self.b,
            "c": self.c,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "method": self.method,
            "odds_ratio": self.odds_ratio,
        }


def _odds_ratio(b: int, c: int) -> float | None:
    """b / c, or None when c == 0 (the odds ratio is undefined)."""
    return None if c == 0 else b / c


def mcnemar_exact(b: int, c: int) -> McNemarResult:
    """Exact (two-sided binomial) McNemar test over the discordant pairs ``(b, c)``.

    Under H0 the discordant pairs split 50/50, so ``min(b, c)`` is Binomial(n, 0.5) with
    ``n = b + c``. The two-sided exact p-value doubles the smaller tail (clipped to 1.0)::

        p = min(1.0, 2 · Σ_{i=0}^{min(b,c)} C(n, i) · 0.5^n)

    ``b + c == 0`` → no discordance ⇒ no detectable difference (``statistic 0.0, p 1.0``).
    ``method == "mcnemar-exact"``; ``statistic == min(b, c)`` (the binomial test statistic).
    """
    n = b + c
    if n == 0:
        return McNemarResult(b, c, 0.0, 1.0, "mcnemar-exact", _odds_ratio(b, c))
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) * 0.5**n
    p_value = min(1.0, 2.0 * tail)
    return McNemarResult(b, c, float(k), p_value, "mcnemar-exact", _odds_ratio(b, c))


def mcnemar_chi2(b: int, c: int, *, continuity: bool = True) -> McNemarResult:
    """χ² (df=1) McNemar test over ``(b, c)``, Edwards continuity-corrected by default.

    ``χ² = (|b − c| − k)² / (b + c)`` with ``k = 1`` for the Edwards continuity correction
    (``k = 0`` otherwise); a negative ``|b − c| − k`` is clipped to 0. The right-tail p-value
    of a χ²(df=1) has the closed form ``erfc(sqrt(χ²/2))`` (pure stdlib — NFR-004).

    ``b + c == 0`` → ``statistic 0.0, p 1.0``. ``method`` is ``"mcnemar-chi2-continuity"`` when
    corrected, else ``"mcnemar-chi2"``.
    """
    n = b + c
    if n == 0:
        method = "mcnemar-chi2-continuity" if continuity else "mcnemar-chi2"
        return McNemarResult(b, c, 0.0, 1.0, method, _odds_ratio(b, c))
    correction = 1 if continuity else 0
    delta = max(0, abs(b - c) - correction)
    chi2 = (delta * delta) / n
    p_value = math.erfc(math.sqrt(chi2 / 2.0))
    method = "mcnemar-chi2-continuity" if continuity else "mcnemar-chi2"
    return McNemarResult(b, c, chi2, p_value, method, _odds_ratio(b, c))


def mcnemar(b: int, c: int, *, exact_max_n: int = 1000) -> McNemarResult:
    """Select the McNemar variant by discordant count (NFR-002 named-method).

    The EXACT two-sided binomial tail is correct for small samples but numerically INFEASIBLE for large ones:
    ``Σ C(n, i)`` is an astronomically large int while ``0.5**n`` underflows, so their product raises
    ``OverflowError: int too large to convert to float`` for ``n = b + c`` beyond ~1074 (a real-systems
    assessment over ~15k gold positives hits this). So: exact when ``b + c <= exact_max_n`` (default 1000,
    well below the overflow point and far above where exact is needed), else the standard large-sample Edwards
    continuity-corrected χ² test. ``McNemarResult.method`` records which was used."""
    if b + c <= exact_max_n:
        return mcnemar_exact(b, c)
    return mcnemar_chi2(b, c, continuity=True)


def _recall_delta(pairs: Sequence[tuple[bool, bool]]) -> float:
    """Observed recall difference mean(A_hit) − mean(B_hit) over the paired spans."""
    n = len(pairs)
    a_hits = sum(1 for a, _ in pairs if a)
    b_hits = sum(1 for _, b in pairs if b)
    return a_hits / n - b_hits / n


def paired_bootstrap_recall_delta(
    pairs: Sequence[tuple[bool, bool]],
    *,
    n_boot: int = 10000,
    seed: int,
    confidence: float = 0.95,
) -> Interval:
    """Seeded paired bootstrap CI for the recall difference Δ = recall(A) − recall(B).

    ``pairs`` is a sequence of ``(A_hit, B_hit)`` booleans over the *same* gold spans. Each of
    ``n_boot`` replicates resamples the **pair indices** with replacement (preserving the A/B
    pairing — that is what makes it a *paired* bootstrap) and recomputes Δ; the reported CI is
    the ``[α/2, 1−α/2]`` percentile interval of those replicate Δ's, with ``point`` = the
    observed Δ and ``n`` = the number of pairs. ``method == "paired-bootstrap"`` (NFR-002).

    Determinism (NFR-004): a **local** ``random.Random(seed)`` drives every draw — the
    module-global RNG is never consulted, so two runs with the same seed are byte-identical and
    independent of any ambient ``random.seed(...)``. An empty ``pairs`` yields a degenerate
    ``[0.0, 0.0]`` interval at Δ = 0.0.
    """
    n = len(pairs)
    if n == 0:
        return Interval(0.0, 0.0, 0.0, 0, "paired-bootstrap", confidence)

    observed = _recall_delta(pairs)
    a_flags = [1 if a else 0 for a, _ in pairs]
    b_flags = [1 if b else 0 for _, b in pairs]

    rng = random.Random(seed)  # LOCAL instance — never the module-global RNG (NFR-004)
    deltas: list[float] = []
    for _ in range(n_boot):
        a_sum = 0
        b_sum = 0
        for _ in range(n):
            j = rng.randrange(n)
            a_sum += a_flags[j]
            b_sum += b_flags[j]
        deltas.append(a_sum / n - b_sum / n)
    deltas.sort()

    alpha = 1.0 - confidence
    low = _percentile(deltas, alpha / 2.0)
    high = _percentile(deltas, 1.0 - alpha / 2.0)
    return Interval(observed, low, high, n, "paired-bootstrap", confidence)


def _percentile(sorted_values: list[float], q: float) -> float:
    """Linear-interpolated ``q``-quantile (q in [0, 1]) of an ascending list.

    Deterministic, dependency-free. ``q`` is clamped to [0, 1]; a singleton list returns its
    sole element. Matches the common ``numpy.percentile`` linear-interpolation convention so the
    percentile bootstrap interval is reproducible without a numerical dependency (NFR-004).
    """
    m = len(sorted_values)
    if m == 1:
        return sorted_values[0]
    q = min(1.0, max(0.0, q))
    pos = q * (m - 1)
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return sorted_values[int(pos)]
    frac = pos - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac
