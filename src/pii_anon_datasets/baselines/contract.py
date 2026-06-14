"""Uniform detector-adapter contract for the ``pii-anon baselines`` leaderboard (detection family).

This is the seam that lets the pure-stdlib orchestrator drive any detector — local
(presidio/spacy/gliner/piiranha/scrubadub/stanza/flair) or cloud — without importing a single detector
library at module-load time (NFR-050). An adapter:

  * declares a ``label_map`` (native label -> canonical-63 type, or ``None`` == intentional drop),
  * probes ``available()`` WITHOUT importing its heavy library (use ``importlib.util.find_spec``),
  * lazily ``build()``s its model/engine (the heavy import happens HERE only),
  * ``detect()``s on one record's text and returns :class:`AdapterSpan`\\ s,
  * reports its ``coverage()`` (the label-map lossiness denominator).

:func:`to_scoring_spans` is the ONE place an :class:`AdapterSpan` becomes the scorer's frozen
:class:`pii_anon_datasets.scoring.core.Span` (dropping the debug ``text``, validating canonical
membership, failing loud per DX-02). Pure-stdlib and deterministic.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from pii_anon_datasets import taxonomy
from pii_anon_datasets.scoring.core import Span


@dataclass(frozen=True)
class AdapterSpan:
    """A detected span as an adapter emits it.

    Field-compatible with ``baselines.evaluate.Span`` (``start, end, entity_type, text``) so an adapter
    doubles as a dev-harness detector; the ``text`` is for debugging only and is dropped at the
    :func:`to_scoring_spans` boundary.
    """

    start: int
    end: int
    entity_type: str
    text: str = ""


@runtime_checkable
class DetectorAdapter(Protocol):
    """The structural contract every repo-root ``*_baseline.py`` adapter satisfies (duck-typed — the
    adapter need not import this module).

    ``available()`` MUST NOT import the heavy library (probe with ``importlib.util.find_spec``); the heavy
    import happens only inside ``build()`` (NFR-050). ``map_label`` returns a canonical-63 type or ``None``
    (drop); ``detect`` returns only mapped, canonical spans.
    """

    name: str
    model_id: str
    label_map: Mapping[str, str | None]

    def available(self) -> bool: ...

    def map_label(self, native: str) -> str | None: ...

    def build(self) -> object: ...

    def detect(self, text: str, model: object) -> list[AdapterSpan]: ...

    def coverage(self) -> int: ...


def to_scoring_spans(spans: Iterable[AdapterSpan]) -> list[Span]:
    """Convert adapter spans to the scorer's canonical :class:`Span`\\ s — the SINGLE convert seam.

    Drops the debug ``text``; validates every type against the canonical 63 and FAILS LOUD on a
    non-canonical type (DX-02 — an adapter must map or drop, never leak an unknown label).
    """
    out: list[Span] = []
    for s in spans:
        if s.entity_type not in taxonomy.CANONICAL_ENTITY_TYPES:
            raise ValueError(
                f"non-canonical entity_type {s.entity_type!r} reached the scorer "
                "(adapters must map to one of the 63 canonical types or drop the span; DX-02)"
            )
        out.append(Span(start=s.start, end=s.end, entity_type=s.entity_type))
    return out


def coverage_of(label_map: Mapping[str, str | None]) -> int:
    """The number of DISTINCT canonical-63 types a label map can reach (``None`` values are drops)."""
    return len(_reachable(label_map))


def lossiness(label_map: Mapping[str, str | None]) -> dict:
    """The label-map lossiness disclosure for one detector: which canonical types are reachable, which
    native labels are intentionally dropped, and which canonical types are UNREACHABLE (the projection
    ceiling — types this detector can never score a true positive on, regardless of model quality)."""
    reachable = sorted(_reachable(label_map))
    return {
        "reachable": len(reachable),
        "of_total": taxonomy.ENTITY_TYPE_COUNT,
        "reachable_types": reachable,
        "dropped_native": sorted(k for k, v in label_map.items() if v is None),
        "unreachable_types": sorted(taxonomy.CANONICAL_ENTITY_TYPES - set(reachable)),
    }


def _reachable(label_map: Mapping[str, str | None]) -> set[str]:
    """The set of canonical-63 types a label map maps onto (ignores ``None`` drops + stray non-canonical)."""
    return {v for v in label_map.values() if v is not None and v in taxonomy.CANONICAL_ENTITY_TYPES}
