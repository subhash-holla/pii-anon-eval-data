"""Audited report projection (CAP-02 DC-22/26/28) — the academic heart, eval-data side.

Every published number is computed by the AUDITED ``stats`` ring ONLY — ``intervals`` (Wilson / Clopper-Pearson),
``paired`` (McNemar + seeded paired bootstrap), ``multitest`` (Holm). This module NEVER imports
``pii_rate_elo_pipeline`` (the FORBIDDEN EDGE, P1): the Elo ratings + Glicko RD are PASSED IN by the consumer's
orchestrator and only assembled here. Produces a tie-gated leaderboard (ranked by recall; adjacent pairs gated
by the paired McNemar/Holm verdict — the rank oracle, stat-02), with per-system Wilson/Clopper-Pearson recall
CIs under a deterministic interval-selection rule, and a non-strippable synthetic-only caveat + honest-verdict
bundle (RD-NOT-CONVERGED, small-n). Deterministic given the seed.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from ..stats import intervals as _intervals
from ..stats import multitest as _multitest
from ..stats import operating_point as _op
from ..stats import paired as _paired
from .manifest import ASSESSMENT_CAVEAT

DEFAULT_N_BOOT = 2000

# Canonical run-type -> rigor-bar mapping (mirrors pii-rate-elo configs/assessment.yaml `run_types`), kept
# here so the eval-data report ENFORCES the bar without importing the consumer's config (NFR-033/034).
RUN_TYPE_RIGOR = {
    "smoke": "suppressed",
    "dev": "suppressed",
    "leaderboard-submission": "full-AX005",
    "filing-grade": "full-AX005",
}


def rigor_bar_for_run_type(run_type: str) -> str:
    """Map a committed run-type to its rigor bar; an unknown run-type defaults to the FULL bar (fail-closed)."""
    return RUN_TYPE_RIGOR.get(run_type, "full-AX005")


def _is_suppressed(rigor_bar: str, inferential_target: str) -> bool:
    """CI + p-value fields are suppressed under a ``suppressed`` rigor bar OR a descriptive census (NFR-025/033/034)."""
    return rigor_bar == "suppressed" or inferential_target == "descriptive-census"


@dataclass(frozen=True)
class SystemOutcome:
    name: str
    hits: tuple[bool, ...]          # aligned per gold positive; True = recalled (the OutcomeDTO recall view)
    elo: float | None = None
    rd: float | None = None


@dataclass(frozen=True)
class LeaderboardRow:
    rank: int
    system: str
    recall: float
    recall_ci_low: float | None       # None iff inference suppressed (smoke/dev/descriptive-census) — never fabricated
    recall_ci_high: float | None
    recall_ci_method: str             # "wilson" | "clopper-pearson" | "suppressed"
    n_positives: int
    elo: float | None
    rd: float | None
    tie_group: int


@dataclass(frozen=True)
class PairVerdict:
    system_a: str
    system_b: str
    mcnemar_b: int
    mcnemar_c: int
    mcnemar_p: float
    mcnemar_p_holm: float
    delta_recall: float
    delta_ci_low: float
    delta_ci_high: float
    significant: bool
    mcnemar_method: str = "mcnemar-exact"   # which variant the selector used (exact small-n / chi2 large-n)


@dataclass(frozen=True)
class LeaderboardReport:
    rows: tuple[LeaderboardRow, ...]
    pair_verdicts: tuple[PairVerdict, ...]
    holm_family_size: int
    caveat: str
    honest_flags: tuple[str, ...]
    converged: bool
    rigor_bar: str = "full-AX005"
    inferential_target: str = "super-population"
    inferential_suppressed: bool = False

    def as_dict(self) -> dict[str, object]:
        rows: list[dict[str, object]] = []
        for r in self.rows:
            if self.inferential_suppressed:
                # OMIT the CI fields entirely under suppression (no inferential claim) — NFR-025/033/034.
                rows.append({
                    "rank": r.rank, "system": r.system, "recall": r.recall,
                    "n_positives": r.n_positives, "elo": r.elo, "rd": r.rd, "tie_group": r.tie_group,
                })
            else:
                rows.append({
                    "rank": r.rank, "system": r.system, "recall": r.recall,
                    "recall_ci": [r.recall_ci_low, r.recall_ci_high], "recall_ci_method": r.recall_ci_method,
                    "n_positives": r.n_positives, "elo": r.elo, "rd": r.rd, "tie_group": r.tie_group,
                })
        return {
            "rows": rows,
            # pair_verdicts is empty under suppression (no pairwise p-values emitted)
            "pair_verdicts": [
                {
                    "system_a": p.system_a, "system_b": p.system_b, "mcnemar_b": p.mcnemar_b,
                    "mcnemar_c": p.mcnemar_c, "mcnemar_p": p.mcnemar_p, "mcnemar_p_holm": p.mcnemar_p_holm,
                    "mcnemar_method": p.mcnemar_method,
                    "delta_recall": p.delta_recall, "delta_ci": [p.delta_ci_low, p.delta_ci_high],
                    "significant": p.significant,
                }
                for p in self.pair_verdicts
            ],
            "holm_family_size": self.holm_family_size,
            "caveat": self.caveat,
            "honest_flags": list(self.honest_flags),
            "converged": self.converged,
            "rigor_bar": self.rigor_bar,
            "inferential_target": self.inferential_target,
            "inferential_suppressed": self.inferential_suppressed,
        }


def _recall(o: SystemOutcome, n: int) -> float:
    return (sum(1 for h in o.hits if h) / n) if n else 0.0


def build_leaderboard(
    outcomes: Sequence[SystemOutcome],
    *,
    seed: int,
    alpha: float = 0.05,
    small_n_cutoff: int = 15,
    n_boot: int = DEFAULT_N_BOOT,
    rd_threshold: float = 100.0,
    rigor_bar: str = "full-AX005",
    inferential_target: str = "super-population",
) -> LeaderboardReport:
    """Assemble the audited, tie-gated leaderboard from aligned per-system recall-hit vectors.

    Under a SUPPRESSED rigor bar (smoke/dev) or a descriptive census (full-corpus), confidence intervals +
    pairwise p-values are NOT emitted (NFR-025/033/034): the report carries point-estimate recall + the power
    verdict + an explicit non-strippable suppression note, and makes NO inferential claim. The default
    (``full-AX005`` / ``super-population``) preserves the full audited leaderboard behavior.
    """
    outcomes = list(outcomes)
    if not outcomes:
        raise ValueError("build_leaderboard requires >= 1 system outcome")
    n = len(outcomes[0].hits)
    if any(len(o.hits) != n for o in outcomes):
        raise ValueError("all systems must have ALIGNED hit vectors (same #gold positives)")

    suppressed = _is_suppressed(rigor_bar, inferential_target)
    ranked = sorted(outcomes, key=lambda o: _recall(o, n), reverse=True)  # stable; ties keep input order

    pair_verdicts: list[PairVerdict] = []
    family: dict[str, float] = {}
    tie_groups = [0] * len(ranked)

    if not suppressed:
        # ---- adjacent-pair McNemar + paired-bootstrap Δ (the rank oracle), then Holm across the family ----
        raw: list[tuple[str, str, int, int, float, float, float, float, str]] = []
        for i in range(len(ranked) - 1):
            a, b = ranked[i], ranked[i + 1]
            bb = sum(1 for ha, hb in zip(a.hits, b.hits) if ha and not hb)
            cc = sum(1 for ha, hb in zip(a.hits, b.hits) if (not ha) and hb)
            mc = _paired.mcnemar(bb, cc)   # exact for small discordant n, chi2-continuity for large (no overflow)
            dci = _paired.paired_bootstrap_recall_delta(list(zip(a.hits, b.hits)), n_boot=n_boot, seed=seed, confidence=1.0 - alpha)
            delta = _recall(a, n) - _recall(b, n)
            key = f"{a.name}__vs__{b.name}"
            family[key] = mc.p_value
            raw.append((a.name, b.name, bb, cc, mc.p_value, delta, dci.low, dci.high, mc.method))

        holm = _multitest.holm_bonferroni(family, alpha=alpha) if family else None
        holm_p = dict(zip(holm.labels, holm.p_adjusted)) if holm else {}
        holm_rej = dict(zip(holm.labels, holm.rejected)) if holm else {}

        for (pa, pb, bb, cc, p, delta, dlo, dhi, method) in raw:
            key = f"{pa}__vs__{pb}"
            pair_verdicts.append(
                PairVerdict(pa, pb, bb, cc, p, holm_p.get(key, p), delta, dlo, dhi,
                            bool(holm_rej.get(key, False)), method)
            )

        # ---- tie-gating: a non-significant adjacent pair groups the two systems (overlapping ranks) ----
        for i in range(1, len(ranked)):
            prev_sig = pair_verdicts[i - 1].significant
            tie_groups[i] = tie_groups[i - 1] + (1 if prev_sig else 0)

    # ---- rows; CI under the deterministic interval-selection rule (SUPPRESSED -> None, never fabricated) ----
    rows: list[LeaderboardRow] = []
    for idx, o in enumerate(ranked):
        if suppressed:
            lo, hi, method = None, None, "suppressed"
        else:
            k = sum(1 for h in o.hits if h)
            if n == 0:
                lo, hi, method = 0.0, 1.0, "clopper-pearson"
            elif n >= small_n_cutoff:
                iv = _intervals.wilson_interval(k, n)
                lo, hi, method = iv.low, iv.high, "wilson"
            else:
                iv = _intervals.clopper_pearson_interval(k, n)
                lo, hi, method = iv.low, iv.high, "clopper-pearson"
        rows.append(
            LeaderboardRow(
                rank=idx + 1, system=o.name, recall=_recall(o, n), recall_ci_low=lo, recall_ci_high=hi,
                recall_ci_method=method, n_positives=n, elo=o.elo, rd=o.rd, tie_group=tie_groups[idx],
            )
        )

    # ---- honest-verdict bundle (non-strippable) ----
    flags: list[str] = [ASSESSMENT_CAVEAT]
    rds = [o.rd for o in outcomes if o.rd is not None]
    converged = bool(rds) and all(rd <= rd_threshold for rd in rds)
    if rds and not converged:
        flags.append(
            f"RD-NOT-CONVERGED: achieved max-RD {max(rds):.1f} > threshold {rd_threshold:.1f} "
            "(tournament-rating convergence only; blocks ranking, NOT recall-CI validity)"
        )
    if suppressed:
        flags.append(
            f"CI/p-values SUPPRESSED under rigor_bar={rigor_bar!r} / inferential_target={inferential_target!r} "
            "(NFR-025/033/034): point-estimate recall + power verdict only — NO confidence intervals, NO pairwise "
            "significance, NO tie-gating; this run makes NO inferential claim (descriptive-census / smoke-inert)."
        )
    elif 0 < n < small_n_cutoff:
        flags.append(f"SMALL-N: {n} positives < small_n_cutoff {small_n_cutoff}; Clopper-Pearson recall CIs used")

    return LeaderboardReport(
        rows=tuple(rows),
        pair_verdicts=tuple(pair_verdicts),
        holm_family_size=len(family),
        caveat=ASSESSMENT_CAVEAT,
        honest_flags=tuple(flags),
        converged=converged,
        rigor_bar=rigor_bar,
        inferential_target=inferential_target,
        inferential_suppressed=suppressed,
    )


@dataclass(frozen=True)
class OperatingPointView:
    """A recall-priority detection operating-point (DC-27 / FR-048): the false-positive tax — never a lone F1."""

    precision: float
    recall: float
    beta: float
    fbeta: float
    auprc: float
    precision_at_recall: float
    recall_target: float
    recall_target_reached: bool
    threshold_rule: str
    fn_fp_cost: int | None = None
    matches_prereg: bool = True
    n_curve_points: int = 1
    auprc_degenerate: bool = True   # True when the PR "curve" is a single point (hit-only systems): AUPRC == r*p

    def as_dict(self) -> dict[str, object]:
        return {
            "precision": self.precision, "recall": self.recall, "beta": self.beta, "fbeta": self.fbeta,
            "auprc": self.auprc, "auprc_degenerate": self.auprc_degenerate, "n_curve_points": self.n_curve_points,
            "precision_at_recall": self.precision_at_recall,
            "recall_target": self.recall_target, "recall_target_reached": self.recall_target_reached,
            "threshold_rule": self.threshold_rule, "fn_fp_cost": self.fn_fp_cost,
            "matches_prereg": self.matches_prereg,
        }


def build_operating_point_view(
    *,
    precision: float,
    recall: float,
    beta: float,
    auprc: float | None,
    precision_at_recall: float | None,
    recall_target_reached: bool,
    recall_target: float,
    threshold_rule: str,
    prereg_design_point: dict,
    fn_fp_cost: int | None = None,
    n_curve_points: int = 1,
) -> OperatingPointView:
    """Validate + assemble the operating-point view (FR-048). Raises ``ValueError`` on a lone F1 / free-or-low β
    without a stated FN:FP cost, an absent AUPRC, an absent precision-at-recall, or an operating point that
    disagrees with the pre-registered threshold rule (post-hoc tuning, FR-044)."""
    using_cost = isinstance(fn_fp_cost, int) and not isinstance(fn_fp_cost, bool) and fn_fp_cost > 0
    if not (beta >= 2 or using_cost):
        raise ValueError(
            "operating-point requires a recall-priority Fβ (β ≥ 2) OR a stated positive integer FN:FP cost — "
            "a lone F1 / free β is rejected (FR-048)"
        )
    if auprc is None:
        raise ValueError("operating-point requires a threshold-free AUPRC (FR-048)")
    if precision_at_recall is None:
        raise ValueError("operating-point requires a non-null precision-at-fixed-recall (FR-048)")
    dp = prereg_design_point or {}
    if float(recall_target) != float(dp.get("recall_target", -1)) or str(threshold_rule) != str(dp.get("threshold_rule", "")):
        raise ValueError(
            "operating point disagrees with the pre-registered design point "
            f"(report: recall_target={recall_target}, rule={threshold_rule!r}; prereg: {dp}) — "
            "post-hoc tuning rejected (FR-048/FR-044)"
        )
    if not using_cost and float(beta) != float(dp.get("beta", -1)):
        raise ValueError(
            f"Fβ operating point uses β={beta} != the pre-registered β={dp.get('beta')} (FR-048 recorded-β)"
        )
    fb = _op.fbeta(precision=precision, recall=recall, beta=beta)
    return OperatingPointView(
        precision=precision, recall=recall, beta=beta, fbeta=fb, auprc=auprc,
        precision_at_recall=precision_at_recall, recall_target=recall_target,
        recall_target_reached=recall_target_reached, threshold_rule=threshold_rule,
        fn_fp_cost=fn_fp_cost, matches_prereg=True,
        n_curve_points=n_curve_points, auprc_degenerate=(n_curve_points <= 1),
    )


# --------------------------------------------------------------------------- honesty-set (NFR-047)
def worst_language_recall(per_language_recall: Mapping[str, float]) -> tuple[str, float] | None:
    """Surface the WORST-language recall floor ``(language, recall)`` so a high mean cannot hide a collapsed
    language (NFR-047). Returns ``None`` for an empty mapping."""
    if not per_language_recall:
        return None
    lang, rec = min(per_language_recall.items(), key=lambda kv: kv[1])
    return lang, rec


def honesty_set_flags(*, per_language_recall: Mapping[str, float] | None = None, rank_vol: object = None) -> list[str]:
    """Bundle the two remaining honesty-set members into non-strippable report flags (NFR-047): the worst-language
    recall floor and the rank-volatility verdict (``rank_vol`` is any object exposing a ``.note`` — e.g.
    :class:`~pii_anon_datasets.stats.rank_stability.RankVolatility`; MEASURED or UNMEASURED, both surfaced)."""
    flags: list[str] = []
    if per_language_recall:
        worst = worst_language_recall(per_language_recall)
        if worst is not None:
            lang, rec = worst
            flags.append(f"WORST-LANGUAGE recall floor: {lang} at {rec:.3f} (the per-language minimum; NFR-047 honesty-set)")
    if rank_vol is not None:
        note = getattr(rank_vol, "note", None)
        if note:
            flags.append(str(note))
    return flags
