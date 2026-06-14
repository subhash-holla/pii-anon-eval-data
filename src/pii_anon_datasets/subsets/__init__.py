"""Corpus slices (DC-01): coreference + quasi-identifier loaders (FR-015/016, v1.1).

This package hosts :mod:`pii_anon_datasets.subsets.slices` — two filters over the existing frozen
corpus fields:

* :func:`~pii_anon_datasets.subsets.slices.coreference_slice` — records with a non-empty
  ``entity_tracking.coreference_chains`` (a chain scored as a UNIT — FR-015), and
* :func:`~pii_anon_datasets.subsets.slices.quasi_identifier_slice` — records with >= ``min_qids``
  ``privacy_risk.quasi_identifiers`` (multi-span indirect identification — FR-016).

Each returns a :class:`~pii_anon_datasets.subsets.slices.Slice` value object carrying the
non-strippable v1.1 low-power caveat (:data:`~pii_anon_datasets.subsets.slices.SLICE_CAVEAT`): ~72%
of the corpus is formulaic synthetic enrichment, so these slices have limited power and external
validity (epistemic honesty about the synthetic monoculture).

(The ``by_domain`` / ``by_dimension`` / ``by_difficulty`` data subdirectories live alongside this
package init; they are corpus data, not importable modules.)

Pure-stdlib (NFR-004); deterministic — order-preserving, no RNG/clock (AX-002).
"""

from __future__ import annotations

from pii_anon_datasets.subsets.slices import (
    SLICE_CAVEAT,
    Slice,
    coreference_slice,
    quasi_identifier_slice,
)

__all__ = [
    "SLICE_CAVEAT",
    "Slice",
    "coreference_slice",
    "quasi_identifier_slice",
]
