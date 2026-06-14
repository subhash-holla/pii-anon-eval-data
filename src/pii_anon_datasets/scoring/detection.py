"""Detection scorer (DC-05; FR-001/004).

Scores a system's spans against gold: integer-count strict P/R/F1/F2 each with a
**Wilson CI** (reidx-02 — integer Bernoulli counts only). Partial-overlap F1 is
reported SEPARATELY and is explicitly excluded from the CIs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

from ..stats.intervals import Interval, wilson_interval
from .core import MATCHING_POLICY_VERSION, Counts, Span, match_strict

# Non-strippable external-validity caveat for any committed-cell metric (AX-003 at crossed-cell
# level; R10 refinement #3). Travels with the number through any serializer, like the RRS caveat.
DESIGN_CAVEAT = (
    "Power on a committed cell is statistical precision on the SYNTHETIC distribution, NOT external "
    "validity; not citable as a standalone recall claim absent the real-data correlation slice "
    "(FR-027). Synthetic-only (AX-001)."
)


def _fbeta(beta2: float, p: float, r: float) -> float:
    denom = beta2 * p + r
    return (1.0 + beta2) * p * r / denom if denom else 0.0


@dataclass(frozen=True)
class DesignProvenance:
    """Per-cell power statement attached to a published committed-cell metric (FR-029, NFR-018).

    Puts the CI's denominator (recall_ci.n) and the cell's tiered target side by side so a reader
    can verify the metric was computed on a powered cell, and carries the non-strippable
    synthetic-provenance/external-validity caveat (cannot be constructed empty)."""
    lattice_cell_id: str
    tier: str
    target_n: int
    observed_positives: int
    powered: bool
    matching_policy: str = MATCHING_POLICY_VERSION
    caveat: str = DESIGN_CAVEAT

    def __post_init__(self) -> None:
        if not self.caveat or not self.caveat.strip():
            raise ValueError("DesignProvenance requires a non-empty external-validity caveat (AX-003).")

    @classmethod
    def from_cell(cls, cell: dict, observed_positives: int) -> "DesignProvenance":
        return cls(
            lattice_cell_id=cell["id"], tier=cell["tier"], target_n=cell["target_n"],
            observed_positives=observed_positives, powered=observed_positives >= cell["target_n"],
        )

    def as_dict(self) -> dict:
        return {
            "lattice_cell_id": self.lattice_cell_id, "tier": self.tier,
            "target_n": self.target_n, "observed_positives": self.observed_positives,
            "powered": self.powered, "matching_policy": self.matching_policy,
            "caveat": self.caveat,
        }


@dataclass(frozen=True)
class DetectionScore:
    precision: float
    recall: float
    f1: float
    f2: float
    recall_ci: Interval
    precision_ci: Interval
    counts: Counts
    partial_f1: float  # separate; NOT CI'd
    design_provenance: "DesignProvenance | None" = None  # set for committed-cell metrics (AX-003)

    def as_dict(self) -> dict:
        d = {
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "f2": self.f2,
            "recall_ci": self.recall_ci.as_dict(),
            "precision_ci": self.precision_ci.as_dict(),
            "counts": asdict(self.counts),
            "partial_f1": self.partial_f1,
            "_note": "partial_f1 carries 0.5 partial credit and is EXCLUDED from CIs (reidx-02).",
        }
        if self.design_provenance is not None:
            d["design_provenance"] = self.design_provenance.as_dict()
        return d


def score_detection(
    gold: Sequence[Span], pred: Sequence[Span], confidence: float = 0.95,
    design_provenance: "DesignProvenance | None" = None,
) -> DetectionScore:
    c = match_strict(gold, pred)
    precision = c.tp / c.n_pred if c.n_pred else 0.0
    recall = c.tp / c.n_gold if c.n_gold else 0.0
    # partial-credit F1 (0.5 credit), reported separately — never feeds a CI
    tp_partial = c.tp + 0.5 * c.partial
    p_part = tp_partial / c.n_pred if c.n_pred else 0.0
    r_part = tp_partial / c.n_gold if c.n_gold else 0.0
    return DetectionScore(
        precision=precision,
        recall=recall,
        f1=_fbeta(1.0, precision, recall),
        f2=_fbeta(4.0, precision, recall),
        recall_ci=wilson_interval(c.tp, c.n_gold, confidence),
        precision_ci=wilson_interval(c.tp, c.n_pred, confidence),
        counts=c,
        partial_f1=_fbeta(1.0, p_part, r_part),
        design_provenance=design_provenance,
    )
