"""Quasi-identifier COMBINATION scorer (FR-016; DC-01, v1.1 — AX-001/002/003).

A quasi-identifier COMBINATION is "re-identifying" iff >= ``k`` of its quasi-identifiers are
recovered/present (k configurable, default 2 — FR-016): indirect/contextual identification (a
{date_of_birth, city, job_title} tuple) distinct from the direct-span detection of
scoring/detection.py. The combination — not any single span — is the privacy-relevant unit.

* :func:`score_qid_combination` scores a single combination -> :class:`QidCombo`.
* :func:`score_quasi_identifier` aggregates the FRACTION of combinations that are re-identifying +
  integer counts over a slice (reuse the ``privacy_risk.quasi_identifiers`` record shape — see
  subsets/slices.py) -> :class:`QuasiIdScore`.

Both value objects carry a **non-strippable v1.1 LOW-POWER caveat**
(:data:`QUASI_IDENTIFIER_CAVEAT`, reusing the meaning of subsets/slices.py ``SLICE_CAVEAT``): ~72%
of the corpus is formulaic ``synthetic_lattice_enrichment``, so FR-016 (SHOULD / v1.1) has LIMITED
statistical power and external validity (AX-003 epistemic honesty; cannot be constructed empty).

Pure-stdlib (NFR-004); deterministic — no RNG/clock, order-preserving (AX-002). Synthetic-only
(AX-001).
"""

from __future__ import annotations

from collections.abc import Container, Iterable
from dataclasses import dataclass

# Non-strippable v1.1 low-power caveat (epistemic honesty; mirrors subsets/slices.py SLICE_CAVEAT).
QUASI_IDENTIFIER_CAVEAT: str = (
    "v1.1 quasi-identifier-combination scoring (FR-016 is SHOULD): ~72% of the corpus is formulaic "
    "synthetic_lattice_enrichment, so re-identification power and external validity are LIMITED. "
    "Synthetic-distribution coverage is not external validity."
)


@dataclass(frozen=True)
class QidCombo:
    """Per-combination re-id verdict (>= k recovered — FR-016) + non-strippable low-power caveat."""

    reidentifying: bool
    n_qids: int
    n_recovered: int
    k: int
    caveat: str = QUASI_IDENTIFIER_CAVEAT

    def __post_init__(self) -> None:
        if not self.caveat or not self.caveat.strip():
            raise ValueError("QidCombo requires a non-empty v1.1 low-power caveat (FR-016; AX-003).")

    def as_dict(self) -> dict[str, object]:
        return {
            "reidentifying": self.reidentifying,
            "n_qids": self.n_qids,
            "n_recovered": self.n_recovered,
            "k": self.k,
            "caveat": self.caveat,
        }


@dataclass(frozen=True)
class QuasiIdScore:
    """Corpus aggregate: fraction of re-identifying combinations + counts + non-strippable caveat."""

    n_combinations: int
    n_reidentifying: int
    k: int
    fraction_reidentifying: float
    caveat: str = QUASI_IDENTIFIER_CAVEAT

    def __post_init__(self) -> None:
        if not self.caveat or not self.caveat.strip():
            raise ValueError(
                "QuasiIdScore requires a non-empty v1.1 low-power caveat (FR-016; AX-003)."
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "n_combinations": self.n_combinations,
            "n_reidentifying": self.n_reidentifying,
            "k": self.k,
            "fraction_reidentifying": self.fraction_reidentifying,
            "caveat": self.caveat,
        }


def score_qid_combination(
    qids: Iterable[object], recovered: Container[object], k: int = 2
) -> QidCombo:
    """Score one combination: re-identifying iff >= k of ``qids`` are in ``recovered`` (FR-016).

    De-duplicates qids first so a repeated quasi-identifier cannot inflate the count past k.
    """
    unique = tuple(dict.fromkeys(qids))
    n_recovered = sum(1 for q in unique if q in recovered)
    return QidCombo(
        reidentifying=n_recovered >= k, n_qids=len(unique), n_recovered=n_recovered, k=k
    )


def score_quasi_identifier(
    records_qids: Iterable[Iterable[object]], recovered: Container[object], k: int = 2
) -> QuasiIdScore:
    """Aggregate >= k re-identifying combinations over a slice -> fraction + counts (FR-016)."""
    combos = [score_qid_combination(qids, recovered, k=k) for qids in records_qids]
    n_combinations = len(combos)
    n_reidentifying = sum(1 for combo in combos if combo.reidentifying)
    fraction = n_reidentifying / n_combinations if n_combinations else 0.0
    return QuasiIdScore(
        n_combinations=n_combinations,
        n_reidentifying=n_reidentifying,
        k=k,
        fraction_reidentifying=fraction,
    )
