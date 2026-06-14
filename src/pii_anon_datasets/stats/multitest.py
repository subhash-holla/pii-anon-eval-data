"""Holm–Bonferroni step-down multiplicity correction (CAP-02 DC-22 / NFR-027).

The assessment leaderboard makes many *system-vs-system* pairwise claims at once; correcting for
multiplicity is required before any rank is called significant (AX-005 element 2). Holm–Bonferroni
is the chosen primitive: it controls the family-wise error rate exactly like Bonferroni but is
**uniformly more powerful** (step-down), so it never rejects fewer hypotheses.

This module is the *net-new* audited multiplicity primitive — verified absent from ``stats/`` at
design time, so it lands here in the Clean ``stats`` ring (never in the fabricated
``pii_rate_elo_pipeline.analysis.significance`` — P1/SP-S4). It is **partition-agnostic**: the
report layer calls it WITHIN each ``(metric, scoring-family)`` partition (Holm is never pooled
across metrics or across anonymization/pseudonymization — AX-004); the ``family_size`` is exactly
the number of p-values handed in.

Pure-stdlib (``math`` only — NFR-004) and deterministic: no RNG, so two calls with the same input
are byte-identical (AX-002). Inputs are guarded — p-values must lie in ``[0, 1]`` and ``alpha`` in
the open interval ``(0, 1)``.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class HolmResult:
    """Outcome of a Holm–Bonferroni correction over one family of p-values.

    All tuples are in **input order** (not sorted), so a caller can ``zip`` them back against the
    hypotheses it submitted. ``p_adjusted`` are the Holm-adjusted p-values (monotone-clamped along
    ascending raw-p order); ``rejected[i]`` is ``p_adjusted[i] <= alpha``.
    """

    labels: tuple[str, ...]
    p_raw: tuple[float, ...]
    p_adjusted: tuple[float, ...]
    rejected: tuple[bool, ...]
    family_size: int
    alpha: float
    method: str  # "holm-bonferroni"

    def as_dict(self) -> dict[str, object]:
        return {
            "labels": list(self.labels),
            "p_raw": list(self.p_raw),
            "p_adjusted": list(self.p_adjusted),
            "rejected": list(self.rejected),
            "family_size": self.family_size,
            "alpha": self.alpha,
            "method": self.method,
        }


def _normalize_items(
    pvalues: Mapping[str, float] | Sequence[tuple[str, float]],
) -> list[tuple[str, float]]:
    """Accept either a ``{label: p}`` mapping or an ordered sequence of ``(label, p)`` pairs."""
    if isinstance(pvalues, Mapping):
        return [(str(k), v) for k, v in pvalues.items()]
    return [(str(k), v) for k, v in pvalues]


def holm_bonferroni(
    pvalues: Mapping[str, float] | Sequence[tuple[str, float]],
    *,
    alpha: float = 0.05,
) -> HolmResult:
    """Holm–Bonferroni step-down correction of one family of p-values.

    Procedure (``m`` = family size): sort the raw p-values ascending; the rank-``r`` (0-based)
    smallest is compared against ``alpha / (m - r)``. The Holm-adjusted p-value is the running
    maximum, along that ascending order, of ``min(1, (m - r) * p)`` — the monotone clamp that gives
    the step-down property (once one hypothesis fails its threshold, no later one is rejected).
    ``rejected[i] == (p_adjusted[i] <= alpha)``.

    ``pvalues`` may be a ``{label: p}`` mapping or an ordered ``(label, p)`` sequence; the outputs
    preserve input order. An empty family is the identity (``family_size 0``, no rejections).

    Raises ``ValueError`` if ``alpha`` is not in ``(0, 1)`` or any p-value is NaN or outside
    ``[0, 1]``.
    """
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in the open interval (0, 1); got {alpha!r}")

    items = _normalize_items(pvalues)
    if not items:
        return HolmResult((), (), (), (), 0, alpha, "holm-bonferroni")

    labels = tuple(label for label, _ in items)
    p_raw: list[float] = []
    for label, raw in items:
        p = float(raw)
        if math.isnan(p) or not (0.0 <= p <= 1.0):
            raise ValueError(f"p-value for {label!r} must be in [0, 1]; got {raw!r}")
        p_raw.append(p)

    m = len(p_raw)
    order = sorted(range(m), key=lambda i: p_raw[i])  # stable ascending by raw p
    adjusted = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        factor = m - rank
        running = max(running, min(1.0, factor * p_raw[idx]))
        adjusted[idx] = running

    rejected = tuple(bool(adjusted[i] <= alpha) for i in range(m))
    return HolmResult(labels, tuple(p_raw), tuple(adjusted), rejected, m, alpha, "holm-bonferroni")
