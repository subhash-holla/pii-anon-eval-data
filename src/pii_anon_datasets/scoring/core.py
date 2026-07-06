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

from collections import Counter, defaultdict
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
    """Deterministic greedy partial-overlap count (same type, each gold used once).

    Byte-identical to the brute-force greedy definition — each predicted span, in ``(start, end,
    entity_type)`` order, claims the FIRST still-unused same-type gold span it overlaps — but linear-ish
    rather than O(FP×FN) on the record-namespaced pools the orchestrator builds for a full multilingual run
    (115k records → ~1M+ pooled spans). Gold is bucketed by type and sorted by start; a per-bucket
    low-water pointer skips gold that is permanently dead (already used, OR ending at/before the prediction's
    start — and so, since predictions are processed in non-decreasing start order, unmatchable by this and
    every later prediction). The inner scan stops at the first gold whose start reaches the prediction's end
    (sorted ⇒ no later gold can overlap). The match chosen is identical to scanning the full sorted gold
    list, because every gold skipped by the pointer could not have matched anyway.
    """
    gold_by_type: dict[str, list[Span]] = defaultdict(list)
    for g in gold_left:
        gold_by_type[g.entity_type].append(g)
    for spans in gold_by_type.values():
        spans.sort(key=lambda s: (s.start, s.end))
    used_by_type = {t: [False] * len(spans) for t, spans in gold_by_type.items()}
    lo_by_type = dict.fromkeys(gold_by_type, 0)

    partial = 0
    for ps in sorted(pred_left, key=lambda s: (s.start, s.end, s.entity_type)):
        spans = gold_by_type.get(ps.entity_type)
        if not spans:
            continue
        used = used_by_type[ps.entity_type]
        lo = lo_by_type[ps.entity_type]
        # Retire gold that can never match this prediction or any later (higher-start) one.
        while lo < len(spans) and (used[lo] or spans[lo].end <= ps.start):
            lo += 1
        lo_by_type[ps.entity_type] = lo
        j = lo
        while j < len(spans):
            gs = spans[j]
            if gs.start >= ps.end:  # sorted by start ⇒ no remaining gold overlaps this prediction
                break
            if not used[j] and gs.end > ps.start:  # same type already; a genuine partial overlap
                used[j] = True
                partial += 1
                break
            j += 1
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
