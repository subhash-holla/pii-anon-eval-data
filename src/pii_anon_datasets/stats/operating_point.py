"""Operating-point descriptive metrics for detection reporting (CAP-02 DC-27 / FR-048; NFR-046).

The de-identification recall/precision asymmetry (a missed SSN is a breach; a false positive is over-redaction)
makes a lone F1 misleading. This module supplies the audited, pure-stdlib MATH for a recall-priority
operating-point view: a recall-weighted ``fbeta`` (β ≥ 2), a threshold-free ``auprc`` over a precision-recall
curve, and ``precision_at_recall`` (read off the curve at a fixed recall target). These are DESCRIPTIVE point
estimates (no CI / no p-value), so they live beside — not inside — the inferential ``intervals``/``paired`` ring.

A precision-recall *curve* is a sequence of ``(recall, precision)`` points. A hit-only system (no per-prediction
score) yields a SINGLE point — its ``auprc`` is the degenerate rectangle ``recall * precision`` (documented, not
hidden); a scored detector yields a real swept curve. Deterministic.
"""
from __future__ import annotations

from collections.abc import Sequence


def fbeta(*, precision: float, recall: float, beta: float) -> float:
    """Recall-weighted Fβ = (1+β²)·P·R / (β²·P + R); 0 when the denominator is 0 (β≥2 ⇒ recall-priority)."""
    b2 = beta * beta
    denom = b2 * precision + recall
    return (1.0 + b2) * precision * recall / denom if denom > 0 else 0.0


def _sorted_curve(curve: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
    if not curve:
        raise ValueError("operating-point curve requires >= 1 (recall, precision) point")
    return sorted(((float(r), float(p)) for r, p in curve), key=lambda rp: rp[0])


def auprc(curve: Sequence[tuple[float, float]]) -> float:
    """Threshold-free area under the precision-recall curve (trapezoidal over recall).

    A single point ``(r, p)`` (a hit-only system) returns the degenerate rectangle ``r * p`` — an honest
    placeholder, NOT a swept curve; a real (scored) detector supplies many points for a true AUPRC."""
    pts = _sorted_curve(curve)
    if len(pts) == 1:
        r, p = pts[0]
        return r * p
    area = 0.0
    for (r1, p1), (r2, p2) in zip(pts, pts[1:]):
        area += (r2 - r1) * (p1 + p2) / 2.0
    return area


def precision_at_recall(curve: Sequence[tuple[float, float]], target: float) -> tuple[float, bool]:
    """Precision read off the curve at the lowest recall ≥ ``target``.

    Returns ``(precision, reached)``: ``reached`` is False when the system cannot achieve ``target`` recall, in
    which case the precision at its MAX recall is returned (still non-null, never fabricated)."""
    pts = _sorted_curve(curve)
    at_or_above = [(r, p) for r, p in pts if r >= target]
    if at_or_above:
        return at_or_above[0][1], True
    return pts[-1][1], False
