"""Coreference + quasi-identifier corpus slices (FR-015/016; DC-01, v1.1).

Two loaders/filters over the existing frozen corpus fields:

* :func:`coreference_slice` returns the records whose ``entity_tracking.coreference_chains`` is
  non-empty — a coreference chain to be scored as a UNIT, not atomic spans (FR-015), and
* :func:`quasi_identifier_slice` returns the records whose ``privacy_risk.quasi_identifiers`` has
  >= ``min_qids`` entries — multi-span indirect/contextual identification distinct from direct-span
  detection (FR-016).

Each slice is a :class:`Slice` value object carrying a **non-strippable v1.1 low-power caveat**
(:data:`SLICE_CAVEAT`): 79.2% of the corpus is formulaic ``synthetic_lattice_enrichment``, so these
slices (FR-015/016 are SHOULD / v1.1) have **limited statistical power and external validity** —
synthetic-distribution coverage is not external validity.

Pure-stdlib (NFR-004); deterministic — order-preserving filter, no RNG/clock (AX-002).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

# Non-strippable v1.1 low-power caveat (epistemic honesty).
SLICE_CAVEAT: str = (
    "v1.1 slice (FR-015/016 are SHOULD): 79.2% of the corpus is formulaic "
    "synthetic_lattice_enrichment, so this slice's statistical power and external validity are LIMITED. "
    "Synthetic-distribution coverage is not external validity."
)


@dataclass(frozen=True)
class Slice:
    """A named subset of records + the non-strippable v1.1 low-power caveat."""

    name: str
    records: tuple[Mapping[str, object], ...]
    caveat: str = SLICE_CAVEAT

    def __post_init__(self) -> None:
        if not self.caveat.strip():
            raise ValueError("slice low-power caveat required (FR-015/016 v1.1 non-strippable)")

    def __len__(self) -> int:
        return len(self.records)

    def as_dict(self) -> dict[str, object]:
        return {"name": self.name, "n": len(self.records), "caveat": self.caveat}


def _coreference_chains(record: Mapping[str, object]) -> object:
    et = record.get("entity_tracking")
    return (et or {}).get("coreference_chains") if isinstance(et, Mapping) else None


def _quasi_identifiers(record: Mapping[str, object]) -> Sequence[object]:
    pr = record.get("privacy_risk")
    qids = (pr or {}).get("quasi_identifiers") if isinstance(pr, Mapping) else None
    return qids if isinstance(qids, Sequence) and not isinstance(qids, (str, bytes)) else ()


def coreference_slice(records: Iterable[Mapping[str, object]]) -> Slice:
    """Records with a NON-EMPTY entity_tracking.coreference_chains (a chain scored as a unit — FR-015)."""
    chosen = tuple(r for r in records if _coreference_chains(r))
    return Slice(name="coreference", records=chosen)


def quasi_identifier_slice(records: Iterable[Mapping[str, object]], *, min_qids: int = 2) -> Slice:
    """Records with >= min_qids privacy_risk.quasi_identifiers (multi-span indirect ID — FR-016)."""
    chosen = tuple(r for r in records if len(_quasi_identifiers(r)) >= min_qids)
    return Slice(name="quasi_identifier", records=chosen)
