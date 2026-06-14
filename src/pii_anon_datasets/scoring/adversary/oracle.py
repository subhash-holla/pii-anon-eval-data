"""PII-recognition oracle (FR-017; DC-10, bounded).

A callable PII-**recognition** oracle over a synthetic record's gold annotations:
:func:`recognize` returns an :class:`OracleVerdict` of labeled entities (which spans are PII +
their type); :func:`recognize_span` answers a point query. This lets a live agent harness call
PII-Anon as a recognition oracle.

**Non-strippable scope guard (FR-017).** The oracle carries a mandatory :data:`ORACLE_DISCLAIMER`
(a module constant + a non-defaulted-validated dataclass field whose ``__post_init__`` rejects an
empty value): it is a *recognition* oracle and is **NEVER marketed as agent-leakage scoring** —
cross-turn / transcript-residual / live-harness agent-leakage measurement is explicitly out of
scope (roadmap FR-018/019/020). The oracle makes NO agent-leakage claim; it only labels spans.

Pure-stdlib (NFR-004); deterministic — no clock / RNG (AX-002). Synthetic gold only (AX-001).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

# Non-strippable (FR-017): this is a RECOGNITION oracle, not agent-leakage scoring.
ORACLE_DISCLAIMER: str = (
    "PII-recognition oracle over synthetic gold annotations: it returns labeled-entity verdicts. It is "
    "NEVER marketed as agent-leakage scoring (FR-017) — cross-turn / transcript-residual / live-harness "
    "agent-leakage measurement is out of scope (roadmap FR-018/019/020)."
)


@dataclass(frozen=True)
class RecognizedEntity:
    start: int
    end: int
    entity_type: str
    text: str


@dataclass(frozen=True)
class OracleVerdict:
    """Labeled-entity verdicts for a record + the non-strippable FR-017 disclaimer."""

    recognized: tuple[RecognizedEntity, ...]
    disclaimer: str = ORACLE_DISCLAIMER

    def __post_init__(self) -> None:
        if not self.disclaimer.strip():
            raise ValueError("oracle disclaimer required (FR-017 non-strippable)")

    def labels(self) -> tuple[str, ...]:
        return tuple(e.entity_type for e in self.recognized)

    def as_dict(self) -> dict[str, object]:
        return {
            "recognized": [
                {"start": e.start, "end": e.end, "entity_type": e.entity_type, "text": e.text} for e in self.recognized
            ],
            "disclaimer": self.disclaimer,
        }


def _entities(record: Mapping[str, object]) -> tuple[RecognizedEntity, ...]:
    anns = record.get("annotations") or []
    out: list[RecognizedEntity] = []
    if isinstance(anns, Sequence):
        for a in anns:
            if isinstance(a, Mapping) and "start" in a and "end" in a and "entity_type" in a:
                out.append(
                    RecognizedEntity(int(a["start"]), int(a["end"]), str(a["entity_type"]), str(a.get("text", "")))
                )
    return tuple(out)


def recognize(record: Mapping[str, object]) -> OracleVerdict:
    """Return the labeled-entity verdicts for a synthetic record (from its gold annotations)."""
    return OracleVerdict(recognized=_entities(record))


def recognize_span(record: Mapping[str, object], start: int, end: int) -> RecognizedEntity | None:
    """Point query: the recognized PII entity exactly covering [start, end), or None."""
    for e in _entities(record):
        if e.start == start and e.end == end:
            return e
    return None
