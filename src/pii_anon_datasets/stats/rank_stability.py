"""Rank-volatility via Kendall-τ across seeded reruns (CAP-02 NFR-047 honesty-set).

A leaderboard rank that flips under a different RNG seed is not a finding. This module measures rank stability:
:func:`kendall_tau_b` scores agreement between two rankings (τ-b reduces to τ-a for the strict orders a
leaderboard produces), and :func:`rank_volatility` aggregates pairwise τ across ``>= min_seeds`` (config: 3)
seeded reruns. Below ``min_seeds`` it returns an explicit **UNMEASURED** verdict — never a false stability
claim from a single run. Pure-stdlib, deterministic.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


def kendall_tau_b(a: Sequence[str], b: Sequence[str]) -> float:
    """Kendall-τ between two rankings of the SAME items (most-preferred first); +1 identical, -1 reversed.

    The leaderboard yields strict total orders (no ties), so τ-b == τ-a == ``(n_c - n_d) / (n(n-1)/2)``.
    Raises ``ValueError`` if the two rankings do not rank the same item set."""
    items = list(a)
    if sorted(items) != sorted(b):
        raise ValueError("kendall_tau_b requires the same item set in both rankings")
    n = len(items)
    if n < 2:
        return 1.0
    rank_a = {x: i for i, x in enumerate(a)}
    rank_b = {x: i for i, x in enumerate(b)}
    n_c = n_d = 0
    for i in range(n):
        for j in range(i + 1, n):
            x, y = items[i], items[j]
            s = (rank_a[x] - rank_a[y]) * (rank_b[x] - rank_b[y])
            if s > 0:
                n_c += 1
            elif s < 0:
                n_d += 1
    denom = n * (n - 1) / 2
    return (n_c - n_d) / denom if denom else 1.0


@dataclass(frozen=True)
class RankVolatility:
    n_seeds: int
    measured: bool
    mean_tau: float | None
    min_tau: float | None
    note: str

    def as_dict(self) -> dict[str, object]:
        return {
            "n_seeds": self.n_seeds, "measured": self.measured,
            "mean_tau": self.mean_tau, "min_tau": self.min_tau, "note": self.note,
        }


def rank_volatility(rankings: Sequence[Sequence[str]], *, min_seeds: int = 3) -> RankVolatility:
    """Aggregate pairwise Kendall-τ across seeded rankings. Below ``min_seeds`` returns UNMEASURED (NFR-047)."""
    rankings = [list(r) for r in rankings]
    n = len(rankings)
    if n < min_seeds:
        return RankVolatility(
            n_seeds=n, measured=False, mean_tau=None, min_tau=None,
            note=f"rank-volatility UNMEASURED: {n} seed(s) < {min_seeds} required — single/under-replicated run "
                 "makes NO rank-stability claim (NFR-047)",
        )
    taus = [
        kendall_tau_b(rankings[i], rankings[j])
        for i in range(n) for j in range(i + 1, n)
    ]
    mean_tau = sum(taus) / len(taus)
    min_tau = min(taus)
    return RankVolatility(
        n_seeds=n, measured=True, mean_tau=mean_tau, min_tau=min_tau,
        note=f"rank-volatility MEASURED over {n} seeds: mean Kendall-τ={mean_tau:.3f}, min={min_tau:.3f} "
             "(τ near 1 ⇒ stable ranking; low/negative ⇒ seed-sensitive — NFR-047)",
    )
