"""Coreference-chain UNIT scorer (FR-015; DC-01, v1.1 — AX-001/002/003).

A coreference chain is scored as a **UNIT**, not as atomic spans: it is "leaked" iff ANY of its
mentions is recovered by the detector (any-mention semantics — FR-015). One recovered alias
re-identifies the whole referent, so chain-level recall is the privacy-relevant signal that
span-level P/R (scoring/detection.py) misses.

* :func:`score_coreference_chain` scores a single chain -> :class:`ChainLeak`.
* :func:`score_coreference` aggregates the FRACTION of chains leaked + integer counts over a slice
  (reuse the ``entity_tracking.coreference_chains`` record shape — see subsets/slices.py) ->
  :class:`CoreferenceScore`.

Both value objects carry a **non-strippable v1.1 LOW-POWER caveat** (:data:`COREFERENCE_CAVEAT`,
reusing the meaning of subsets/slices.py ``SLICE_CAVEAT``): 79.2% of the corpus is formulaic
``synthetic_lattice_enrichment``, so FR-015 (SHOULD / v1.1) has LIMITED statistical power and
external validity (AX-003 epistemic honesty; cannot be constructed empty).

Pure-stdlib (NFR-004); deterministic — no RNG/clock, order-preserving (AX-002). Synthetic-only
(AX-001).
"""

from __future__ import annotations

from collections.abc import Container, Iterable
from dataclasses import dataclass

# Non-strippable v1.1 low-power caveat (epistemic honesty; mirrors subsets/slices.py SLICE_CAVEAT).
COREFERENCE_CAVEAT: str = (
    "v1.1 coreference-chain scoring (FR-015 is SHOULD): 79.2% of the corpus is formulaic "
    "synthetic_lattice_enrichment, so chain-leak power and external validity are LIMITED. "
    "Synthetic-distribution coverage is not external validity."
)


@dataclass(frozen=True)
class ChainLeak:
    """Per-chain leak verdict (any-mention semantics — FR-015) + non-strippable low-power caveat."""

    leaked: bool
    n_mentions: int
    n_recovered: int
    caveat: str = COREFERENCE_CAVEAT

    def __post_init__(self) -> None:
        if not self.caveat or not self.caveat.strip():
            raise ValueError("ChainLeak requires a non-empty v1.1 low-power caveat (FR-015; AX-003).")

    def as_dict(self) -> dict[str, object]:
        return {
            "leaked": self.leaked,
            "n_mentions": self.n_mentions,
            "n_recovered": self.n_recovered,
            "caveat": self.caveat,
        }


@dataclass(frozen=True)
class CoreferenceScore:
    """Corpus aggregate: fraction of coreference chains leaked + counts + non-strippable caveat."""

    n_chains: int
    n_leaked: int
    fraction_leaked: float
    caveat: str = COREFERENCE_CAVEAT

    def __post_init__(self) -> None:
        if not self.caveat or not self.caveat.strip():
            raise ValueError(
                "CoreferenceScore requires a non-empty v1.1 low-power caveat (FR-015; AX-003)."
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "n_chains": self.n_chains,
            "n_leaked": self.n_leaked,
            "fraction_leaked": self.fraction_leaked,
            "caveat": self.caveat,
        }


def score_coreference_chain(
    chain_mentions: Iterable[object], recovered_mention_ids: Container[object]
) -> ChainLeak:
    """Score one chain as a UNIT: leaked iff ANY mention is in ``recovered_mention_ids`` (FR-015)."""
    mentions = tuple(chain_mentions)
    n_recovered = sum(1 for m in mentions if m in recovered_mention_ids)
    return ChainLeak(leaked=n_recovered > 0, n_mentions=len(mentions), n_recovered=n_recovered)


def score_coreference(
    chains: Iterable[Iterable[object]], recovered: Container[object]
) -> CoreferenceScore:
    """Aggregate any-mention chain leaks over a slice -> fraction leaked + integer counts (FR-015)."""
    leaks = [score_coreference_chain(chain, recovered) for chain in chains]
    n_chains = len(leaks)
    n_leaked = sum(1 for leak in leaks if leak.leaked)
    fraction = n_leaked / n_chains if n_chains else 0.0
    return CoreferenceScore(n_chains=n_chains, n_leaked=n_leaked, fraction_leaked=fraction)
