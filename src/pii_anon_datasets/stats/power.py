"""Design-of-experiments power core (DC-09 sibling of intervals.py).

Operationalizes NFR-001 / NFR-018 / AX-pii-anon-003 statistical-power targets from
NIST proportion sample-sizing + McNemar paired-comparison efficiency. See
``dev-assist-artifacts/03-design/sampling-design.md``.

Pure-stdlib + deterministic (NFR-004). TWO PARALLEL PATHS, ONE z-TABLE:
  * the MEASURED path stays ``intervals.wilson_interval(k:int, n:int)`` — integer-guarded
    (reidx-02); a fractional/partial count is a TypeError.
  * the DESIGN-TIME path here (``required_n``, ``projected_wilson_halfwidth``,
    ``projected_interval``) takes a CONTINUOUS reference proportion and deliberately does
    NOT route through the integer guard — it re-derives the identical Wilson closed form.
A projection is stamped ``method="wilson-projected"`` so it can never be mistaken for a
measured CI downstream.
"""
from __future__ import annotations

import io
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Mapping, Sequence

from .. import taxonomy
from .intervals import Interval, _z


def _anti_anonymity_caveat() -> str:
    """The canonical FR-009 anti-anonymity caveat, sourced from ``scoring.reidentification``
    (NOT redefined here). Imported LAZILY — ``stats`` is a leaf subsystem and must not import
    the ``scoring`` package at module-load time, which would close a cycle
    (scoring → reidentification → ..stats.intervals → stats.__init__ → power → scoring). The
    constant is read once a :class:`ReidProvenance` is actually constructed, by which point all
    modules have finished importing. The default-empty guard in ``__post_init__`` keeps the
    field non-strippable regardless."""
    from ..scoring.reidentification import ANTI_ANONYMITY_CAVEAT
    return ANTI_ANONYMITY_CAVEAT

Cell = tuple  # a cell key: tuple of (dimension, value) pairs, e.g. (("language","fr"),("entity_type","IBAN"))

__all__ = [
    "Tier", "TierSpec", "TIER_SPECS", "PowerClass",
    "required_n", "projected_wilson_halfwidth", "projected_interval",
    "target_for_tier", "classify", "default_tier_of",
    "required_discordant_pairs", "paired_vs_independent_ratio",
    "CellAudit", "PowerMatrix", "audit_crossing",
    # S3-08: the RE-ID-operating-point power ladder seam (NFR-018; sampling-design.md §5) —
    # a PARALLEL ladder over paired personas / |C|, distinct from the detection-recall tiers.
    "reid_required_n", "ReidTier", "ReidTierSpec", "REID_TIER_SPECS", "ReidProvenance",
]


# ── tiers ──────────────────────────────────────────────────────────────────────────────
class Tier(str, Enum):
    CRITICAL = "critical"      # p_ref=0.99, d=0.005  → 1,522
    STANDARD = "standard"      # p_ref=0.98, d=0.010  → 753
    LONG_TAIL = "long_tail"    # p_ref=0.95, d≈0.030  → 200


class PowerClass(str, Enum):
    WELL_POWERED = "well_powered"     # n >= target_n
    UNDER_POWERED = "under_powered"   # 0 < n < target_n
    EMPTY = "empty"                   # n == 0 (structural)


# ── 1. NIST proportion sample size (design-time; floats expected — this is a TARGET) ─────
def required_n(p_ref: float, half_width: float, confidence: float = 0.95) -> int:
    """n = ceil(z^2 * p(1-p) / d^2) — NIST/SEMATECH §7.2.4.2 proportion sizing.

    Continuous by design: ``p_ref``/``half_width`` are hypotheses, NOT Bernoulli counts,
    so this never touches the integer-guarded ``wilson_interval``.
    """
    if not (0.0 < p_ref < 1.0):
        raise ValueError(f"p_ref must be in (0,1); got {p_ref}")
    if not (0.0 < half_width < 1.0):
        raise ValueError(f"half_width must be in (0,1); got {half_width}")
    z = _z(confidence)
    return math.ceil(z * z * p_ref * (1.0 - p_ref) / (half_width * half_width))


@dataclass(frozen=True)
class TierSpec:
    tier: Tier
    p_ref: float
    half_width: float
    target_n: int

    def as_dict(self) -> dict:
        return {"tier": self.tier.value, "p_ref": self.p_ref,
                "half_width": self.half_width, "target_n": self.target_n}


# Targets are DERIVED from (p_ref, half_width) — not hand-typed (NFR-018 anti-drift):
#   critical (0.99, 0.005) -> 1522 ; standard (0.98, 0.010) -> 753 ; long_tail (0.95, 0.03025) -> 200.
TIER_SPECS: Mapping[Tier, TierSpec] = {
    Tier.CRITICAL: TierSpec(Tier.CRITICAL, 0.99, 0.005, required_n(0.99, 0.005)),
    Tier.STANDARD: TierSpec(Tier.STANDARD, 0.98, 0.010, required_n(0.98, 0.010)),
    Tier.LONG_TAIL: TierSpec(Tier.LONG_TAIL, 0.95, 0.03025, required_n(0.95, 0.03025)),
}


def target_for_tier(tier: Tier | str) -> int:
    return TIER_SPECS[Tier(tier)].target_n


# ── 1b. RE-ID-operating-point power ladder (S3-08; NFR-018 — sampling-design.md §5) ──────
#
# A PARALLEL ladder to the detection-recall tiers above, for the anonymization /
# pseudonymization / RRS tracks. Their denominator is PAIRED personas / candidate-set |C|
# and their operating point is p≈0.1–0.5 (a re-identification *rate*, not a detection
# *recall* of 0.95–0.99), so the detection tiers (1522/753/200) do not describe them.
#
# LOAD-BEARING (the seam is CODE-ONLY): this ladder lives entirely here in stats/power.py.
# It does NOT touch — and does NOT rebuild — the FROZEN detection ``eval_lattice.json``
# (built from the pinned ``lattice_freq_snapshot.json``); the regression guard
# ``test_nfr_018_seam_does_not_mutate_frozen_lattice`` pins that the committed cell count is
# unchanged. It reuses the SAME ``required_n``/``_z`` closed form so the design-time detection
# ladder and this re-id ladder share ONE z-table (no second statistic to drift).

def reid_required_n(p_ref: float, half_width: float, confidence: float = 0.95) -> int:
    """NIST proportion sizing at the RE-ID operating point (p≈0.1–0.5) over PAIRED personas /
    candidate set |C| — a distinct *semantic* entry point from the detection-recall
    :func:`required_n`.

    Identical closed form (so design + measured share one z-table), documented for the re-id
    track: the re-id tracks estimate a re-identification *rate* p (≈0.1–0.5) with half-width
    ``half_width`` over paired personas / |C|, NOT a 0.95–0.99 detection recall. Pinned by §5:
    ``reid_required_n(0.30, 0.030) == 897`` and ``reid_required_n(0.10, 0.030) == 385``.
    """
    return required_n(p_ref, half_width, confidence)  # same closed form, re-id track semantics


class ReidTier(str, Enum):
    REID_HIGH = "reid_high"     # p_ref=0.30, d=0.030 → 897 pairs (sampling-design.md §5)
    REID_LOW = "reid_low"       # p_ref=0.10, d=0.030 → 385 pairs


@dataclass(frozen=True)
class ReidTierSpec:
    tier: ReidTier
    p_ref: float
    half_width: float
    target_n_pairs: int

    def as_dict(self) -> dict[str, object]:
        return {"tier": self.tier.value, "p_ref": self.p_ref,
                "half_width": self.half_width, "target_n_pairs": self.target_n_pairs}


# Targets DERIVED via ``reid_required_n`` — NOT hand-typed (NFR-018 anti-drift; mirrors the
# detection TIER_SPECS discipline). The trailing comments are the EXPECTED §5 figures only.
REID_TIER_SPECS: Mapping[ReidTier, ReidTierSpec] = {
    ReidTier.REID_HIGH: ReidTierSpec(ReidTier.REID_HIGH, 0.30, 0.030,
                                     reid_required_n(0.30, 0.030)),  # 897
    ReidTier.REID_LOW: ReidTierSpec(ReidTier.REID_LOW, 0.10, 0.030,
                                    reid_required_n(0.10, 0.030)),   # 385
}


@dataclass(frozen=True)
class ReidProvenance:
    """Per-record re-id-operating-point power statement (NFR-018; analogous to the detection
    ``DesignProvenance`` but at the re-id operating point) that attaches to ``MeasuredRRS``.

    Records the powered/under-powered status of a measured re-identification figure against
    its target pair count, plus the stated candidate-set size |C| and the version-pinned
    ``adversary_id`` (reidx-01). ``track == "reidentification"`` distinguishes it from the
    detection track. The anti-anonymity ``caveat`` (FR-009) is the non-strippable default — it
    cannot be constructed empty — so the disclaimer travels with the number through any
    serializer (mirrors the RRSResult caveat discipline).
    """

    target_n_pairs: int
    observed_pairs: int
    candidate_set_size: int            # |C| — stated parameter (closed-world re-id != open-world)
    adversary_id: str                  # version-pinned, frozen in the record (reidx-01)
    reid_tier: str = ReidTier.REID_HIGH.value
    track: str = "reidentification"    # distinguishes from the detection track
    # FR-009 anti-anonymity caveat — sourced lazily from scoring.reidentification (canonical,
    # not redefined) to keep stats a leaf subsystem; non-strippable via the __post_init__ guard.
    caveat: str = field(default_factory=_anti_anonymity_caveat)

    @property
    def powered(self) -> bool:
        return self.observed_pairs >= self.target_n_pairs

    def __post_init__(self) -> None:
        if not self.caveat.strip():
            raise ValueError("reid provenance caveat required")

    def as_dict(self) -> dict[str, object]:
        # the anti-anonymity caveat is ALWAYS serialized — non-strippable (FR-009).
        return {
            "track": self.track,
            "reid_tier": self.reid_tier,
            "target_n_pairs": self.target_n_pairs,
            "observed_pairs": self.observed_pairs,
            "candidate_set_size": self.candidate_set_size,
            "adversary_id": self.adversary_id,
            "powered": self.powered,
            "caveat": self.caveat,
        }


# ── 2. DESIGN-TIME continuous Wilson half-width at a reference proportion ────────────────
def projected_wilson_halfwidth(p_ref: float, n: int, confidence: float = 0.95) -> float:
    """Wilson half-width you'd OBTAIN at hypothesized recall ``p_ref`` with ``n`` trials.

    Design-time projection: ``p_ref`` is continuous (NOT k/n), so this re-derives the Wilson
    closed form directly rather than routing through the integer-guarded ``wilson_interval``.
    """
    if n <= 0:
        return 1.0
    z = _z(confidence)
    denom = 1.0 + z * z / n
    return (z / denom) * math.sqrt(p_ref * (1.0 - p_ref) / n + z * z / (4.0 * n * n))


def projected_interval(p_ref: float, n: int, confidence: float = 0.95) -> Interval:
    """Design-time projected Wilson Interval at ``p_ref``. ``method='wilson-projected'`` so a
    projection can never be confused with a MEASURED ``wilson_interval`` result downstream."""
    if not (0.0 <= p_ref <= 1.0):
        raise ValueError(f"p_ref must be in [0,1]; got {p_ref}")
    if n <= 0:
        return Interval(float("nan"), 0.0, 1.0, 0, "wilson-projected", confidence)
    z = _z(confidence)
    denom = 1.0 + z * z / n
    center = (p_ref + z * z / (2.0 * n)) / denom
    half = projected_wilson_halfwidth(p_ref, n, confidence)
    return Interval(p_ref, max(0.0, center - half), min(1.0, center + half), n,
                    "wilson-projected", confidence)


# ── 3. cell classification ───────────────────────────────────────────────────────────────
def classify(n: int, target_n: int) -> PowerClass:
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("cell positive count n must be a non-bool int (reidx-02)")
    if n <= 0:
        return PowerClass.EMPTY
    return PowerClass.WELL_POWERED if n >= target_n else PowerClass.UNDER_POWERED


def default_tier_of(cell: Cell) -> Tier:
    """Max-of-members rule (sampling-design.md §3.4): a cell's tier is the most demanding
    tier among its entity_type member(s); a cell with no entity_type defaults to STANDARD."""
    tiers = [Tier(taxonomy.risk_tier(v)) for (dim, v) in cell if dim == "entity_type"]
    if not tiers:
        return Tier.STANDARD
    return max(tiers, key=lambda t: TIER_SPECS[t].target_n)


# ── 3b. McNemar paired-efficiency (the "head-to-head is over-powered" claim, computable) ──
def required_discordant_pairs(odds_ratio: float, power: float = 0.8,
                              confidence: float = 0.95) -> int:
    """Discordant pairs needed for McNemar's paired test to detect a given odds ratio
    ψ = b/c (Lachin 1992; normal approximation). Conditional prob a discordant pair favors
    system A is p = ψ/(1+ψ); n_disc = (z_{1-α/2} + z_{1-β})^2 / (4 (p-0.5)^2)."""
    if odds_ratio <= 0:
        raise ValueError(f"odds_ratio must be > 0; got {odds_ratio}")
    if odds_ratio == 1.0:
        raise ValueError("odds_ratio == 1 has no detectable effect (infinite sample)")
    if not (0.0 < power < 1.0):
        raise ValueError(f"power must be in (0,1); got {power}")
    p = odds_ratio / (1.0 + odds_ratio)
    z_alpha = _z(confidence)               # two-sided critical value, e.g. 1.96 @95%
    z_beta = _z(2.0 * power - 1.0)         # one-sided quantile at (1-β), e.g. 0.8416 @power .8
    return math.ceil((z_alpha + z_beta) ** 2 / (4.0 * (p - 0.5) ** 2))


def paired_vs_independent_ratio(p_ref: float, p_disc: float) -> float:
    """Variance ratio of a PAIRED (McNemar) recall-difference estimator to two INDEPENDENT
    marginals: ``p_disc / (2 · p_ref · (1-p_ref))``.

    The paired difference has variance ≈ p_disc/n (only discordant pairs are informative);
    two independent arms have ≈ 2·p_ref(1-p_ref)/n. The ratio is **< 1 (paired more
    efficient) exactly when p_disc < 2·p_ref·(1-p_ref)** — i.e. when the two systems' errors
    are positively correlated (they miss the same hard cases), which is the realistic regime
    for two detectors scored on the SAME gold. So sizing cells for the harder marginal recall
    CI leaves head-to-head A/B comparisons at those cells over-powered."""
    if not (0.0 < p_ref < 1.0):
        raise ValueError(f"p_ref must be in (0,1); got {p_ref}")
    if not (0.0 <= p_disc <= 1.0):
        raise ValueError(f"p_disc must be in [0,1]; got {p_disc}")
    return p_disc / (2.0 * p_ref * (1.0 - p_ref))


# ── 4. corpus audit over an arbitrary crossing ──────────────────────────────────────────
@dataclass(frozen=True)
class CellAudit:
    dimensions: tuple                 # the cell key: ((dim, value), ...)
    n: int                            # measured positive count (int → reidx-02 safe)
    tier: Tier
    target_n: int
    power_class: PowerClass
    projected_ci: Interval            # design-time projection at the tier p_ref (always present)
    shortfall: int
    measured_ci: Interval | None = None   # wilson_interval(k, n) IF a measured recall was given

    @property
    def cell_id(self) -> str:
        return "|".join(f"{d}={v}" for d, v in self.dimensions)

    def as_dict(self) -> dict:
        d = {
            "cell_id": self.cell_id,
            "dimensions": {k: v for k, v in self.dimensions},
            "n": self.n,
            "tier": self.tier.value,
            "target_n": self.target_n,
            "power_class": self.power_class.value,
            "shortfall": self.shortfall,
            "projected_ci": self.projected_ci.as_dict(),
        }
        if self.measured_ci is not None:
            d["measured_ci"] = self.measured_ci.as_dict()
        return d


@dataclass(frozen=True)
class PowerMatrix:
    cells: tuple                      # tuple[CellAudit, ...], sorted by cell_id (deterministic)
    axes: tuple                       # the factor names crossed, e.g. ("language", "entity_type")
    confidence: float

    def summary(self) -> dict:
        counts = {pc: 0 for pc in PowerClass}
        for c in self.cells:
            counts[c.power_class] += 1
        return {
            "cells": len(self.cells),
            "well_powered": counts[PowerClass.WELL_POWERED],
            "under_powered": counts[PowerClass.UNDER_POWERED],
            "empty": counts[PowerClass.EMPTY],
            "total_shortfall": self.total_shortfall(),
            "axes": list(self.axes),
            "confidence": self.confidence,
        }

    def well_powered(self) -> tuple:
        return tuple(c for c in self.cells if c.power_class is PowerClass.WELL_POWERED)

    def under_powered(self) -> tuple:
        return tuple(c for c in self.cells if c.power_class is PowerClass.UNDER_POWERED)

    def empty(self) -> tuple:
        return tuple(c for c in self.cells if c.power_class is PowerClass.EMPTY)

    def total_shortfall(self) -> int:
        return sum(c.shortfall for c in self.cells)

    def verdict(self) -> str:
        """SMALL / ADEQUATE / LARGE summary over committed cells (sampling-design.md §7)."""
        s = self.summary()
        if s["cells"] == 0:
            return "EMPTY"
        frac = s["well_powered"] / s["cells"]
        if frac >= 0.999:
            return "LARGE"
        if frac >= 0.80:
            return "ADEQUATE"
        return "SMALL"

    def to_markdown(self) -> str:
        s = self.summary()
        out = [
            f"# Power matrix — {' × '.join(self.axes)}",
            "",
            f"- cells: **{s['cells']}** · well-powered: **{s['well_powered']}** · "
            f"under-powered: **{s['under_powered']}** · empty: **{s['empty']}**",
            f"- total shortfall: **{s['total_shortfall']}** positives · verdict: **{self.verdict()}** "
            f"(confidence {self.confidence})",
            "",
            "| cell | n | tier | target | class | shortfall | projected recall CI |",
            "|---|---:|---|---:|---|---:|---|",
        ]
        for c in self.cells:
            ci = c.projected_ci
            ci_s = "n/a" if math.isnan(ci.point) else f"[{ci.low:.3f}, {ci.high:.3f}]"
            out.append(
                f"| {c.cell_id} | {c.n} | {c.tier.value} | {c.target_n} | "
                f"{c.power_class.value} | {c.shortfall} | {ci_s} |"
            )
        return "\n".join(out) + "\n"

    def to_csv(self) -> str:
        import csv
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(["cell_id", "n", "tier", "target_n", "power_class", "shortfall",
                    "projected_low", "projected_high"])
        for c in self.cells:
            ci = c.projected_ci
            w.writerow([c.cell_id, c.n, c.tier.value, c.target_n, c.power_class.value,
                        c.shortfall, f"{ci.low:.6f}", f"{ci.high:.6f}"])
        return buf.getvalue()

    def heatmap(self, path: str) -> None:  # pragma: no cover - optional viz extra
        """Render a slice heatmap PNG. Requires the optional ``viz`` extra (matplotlib)."""
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError as e:
            raise RuntimeError(
                "heatmap() needs the 'viz' extra: pip install pii-anon-datasets[viz]"
            ) from e
        if len(self.axes) != 2:
            raise ValueError("heatmap() requires a 2-axis crossing")
        xs = sorted({dict(c.dimensions)[self.axes[0]] for c in self.cells})
        ys = sorted({dict(c.dimensions)[self.axes[1]] for c in self.cells})
        xi = {v: i for i, v in enumerate(xs)}
        yi = {v: i for i, v in enumerate(ys)}
        grid = [[float("nan")] * len(xs) for _ in ys]
        for c in self.cells:
            d = dict(c.dimensions)
            grid[yi[d[self.axes[1]]]][xi[d[self.axes[0]]]] = min(1.0, c.n / c.target_n)
        fig, ax = plt.subplots(figsize=(max(6, len(xs) * 0.3), max(4, len(ys) * 0.3)))
        ax.imshow(grid, aspect="auto", vmin=0.0, vmax=1.0, cmap="RdYlGn")
        ax.set_xticks(range(len(xs))); ax.set_xticklabels(xs, rotation=90, fontsize=6)
        ax.set_yticks(range(len(ys))); ax.set_yticklabels(ys, fontsize=6)
        ax.set_xlabel(self.axes[0]); ax.set_ylabel(self.axes[1])
        ax.set_title(f"power coverage (n/target, capped at 1.0) — verdict {self.verdict()}")
        fig.tight_layout()
        fig.savefig(path, dpi=120)
        plt.close(fig)


def audit_crossing(
    counts: Mapping[Cell, int],
    tier_of: Callable[[Cell], Tier] = default_tier_of,
    axes: Sequence[str] | None = None,
    measured_recall: Mapping[Cell, tuple] | None = None,
    confidence: float = 0.95,
) -> PowerMatrix:
    """Audit positives-per-cell against risk-tiered targets → a deterministic PowerMatrix.

    ``counts``          : cell key → positive count (gold annotations; the recall-CI denominator).
    ``tier_of``         : cell key → Tier (default: max-of-members rule).
    ``measured_recall`` : optional cell key → (k:int, n:int) to attach a MEASURED wilson_interval.
    """
    from .intervals import wilson_interval
    audits = []
    for cell, n in counts.items():
        tier = Tier(tier_of(cell))
        spec = TIER_SPECS[tier]
        pc = classify(n, spec.target_n)
        shortfall = max(0, spec.target_n - n)
        proj = projected_interval(spec.p_ref, n, confidence)
        measured = None
        if measured_recall is not None and cell in measured_recall:
            k, mn = measured_recall[cell]
            measured = wilson_interval(k, mn, confidence)
        audits.append(CellAudit(
            dimensions=tuple(cell), n=n, tier=tier, target_n=spec.target_n,
            power_class=pc, projected_ci=proj, shortfall=shortfall, measured_ci=measured,
        ))
    audits.sort(key=lambda c: c.cell_id)   # deterministic ordering (NFR-004)
    if axes is None:
        seen: list[str] = []
        for c in audits:
            for d, _ in c.dimensions:
                if d not in seen:
                    seen.append(d)
        axes = tuple(seen)
    return PowerMatrix(cells=tuple(audits), axes=tuple(axes), confidence=confidence)
