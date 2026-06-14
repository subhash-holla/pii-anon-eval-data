"""Hexagonal scoring core (DC-04): I/O contract + deterministic span matching.

The scoring DOMAIN. A system-under-test plugs in via the ``SpanAdapter`` inbound
port (e.g. a Presidio adapter); the core never knows the system's native shape.

Reproducibility fixes from the D6 SME panel:
  * reidx-02 — strict matching yields INTEGER (k, n) counts; partial-overlap credit
    is reported SEPARATELY and excluded from any binomial CI.
  * reidx-03 — strict matching is a multiset (set) operation, so counts are
    INDEPENDENT of input order. A ``MATCHING_POLICY_VERSION`` is stamped on results.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable

MATCHING_POLICY_VERSION = "strict-v1"


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    entity_type: str

    def __post_init__(self) -> None:
        if self.start < 0 or self.end < self.start:
            raise ValueError(f"invalid span [{self.start},{self.end})")

    def overlaps(self, other: "Span") -> bool:
        return self.start < other.end and other.start < self.end


@runtime_checkable
class SpanAdapter(Protocol):
    """Inbound port: adapts a system's native PII output to canonical Spans.

    Implementations (e.g. ``presidio_adapter``) MUST map via a declared, validated
    entity-type crosswalk and FAIL LOUD on unmapped types (DX-02) — never silently
    pass an unknown label through.
    """

    def to_spans(self, raw: object) -> list["Span"]: ...


@dataclass(frozen=True)
class Counts:
    tp: int
    fp: int
    fn: int
    partial: int  # reported separately; NEVER used in a binomial CI (reidx-02)
    policy: str = MATCHING_POLICY_VERSION

    @property
    def n_pred(self) -> int:
        return self.tp + self.fp

    @property
    def n_gold(self) -> int:
        return self.tp + self.fn


def _count_partial(gold_left: Sequence[Span], pred_left: Sequence[Span]) -> int:
    """Deterministic greedy partial-overlap count (same type, each gold used once)."""
    gold_sorted = sorted(gold_left, key=lambda s: (s.start, s.end, s.entity_type))
    used = [False] * len(gold_sorted)
    partial = 0
    for ps in sorted(pred_left, key=lambda s: (s.start, s.end, s.entity_type)):
        for i, gs in enumerate(gold_sorted):
            if not used[i] and gs.entity_type == ps.entity_type and gs.overlaps(ps):
                used[i] = True
                partial += 1
                break
    return partial


def match_strict(gold: Sequence[Span], pred: Sequence[Span]) -> Counts:
    """Deterministic, order-independent strict matching → integer counts.

    A gold span is a TP iff an identical ``(start, end, entity_type)`` predicted span
    exists. Multiplicity is handled by multiset intersection, so the counts do not
    depend on input order.
    """
    g: Counter = Counter(gold)
    p: Counter = Counter(pred)
    inter = g & p
    tp = sum(inter.values())
    fn = sum(g.values()) - tp
    fp = sum(p.values()) - tp
    partial = _count_partial(list((g - inter).elements()), list((p - inter).elements()))
    return Counts(tp=tp, fp=fp, fn=fn, partial=partial)
