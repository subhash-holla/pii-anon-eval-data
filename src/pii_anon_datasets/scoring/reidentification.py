"""Re-identification-resistance result (DC-07; FR-007/008/009).

gov-01 fix (FR-009 made STRUCTURAL): the anti-anonymity caveat is a **mandatory,
non-defaulted field** on the value object — so it is impossible to construct an
RRS result without it, and it travels with the number through ANY serializer
(report, Parquet, JSON, leaderboard). A serializer that drops it fails the
``test_rrs_caveat`` schema test.

reidx-01: the headline RRS is produced by a DETERMINISTIC offline adversary
(``deterministic=True``); an LLM adversary is a version-stamped SECONDARY figure.

S3-04 (FR-007): :class:`MeasuredRRS` + :func:`score_reidentification` turn an
:class:`~pii_anon_datasets.scoring.adversary.base.Adversary`'s ``Guess`` es over an
assembled ``(targets, candidates, |C|)`` into the **headline measured number** —
empirical re-identification recall and precision with Wilson CIs **on integer counts**
(reidx-02), wrapped as ``RRS = 1 − recall × precision`` inside the frozen
:class:`RRSResult` so the non-strippable caveat still travels with the number.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from ..stats.intervals import Interval, wilson_interval
from . import signals
from .adversary.base import Adversary, Persona, Target

ANTI_ANONYMITY_CAVEAT = (
    "RRS is a relative re-identification-resistance metric under a specific, "
    "version-pinned synthetic adversary. It is NOT an anonymity threshold and MUST "
    "NOT be cited as evidence that output is 'anonymized' under GDPR/HIPAA."
)


@dataclass(frozen=True)
class RRSResult:
    rrs: float                  # 1 - reid_recall * reid_precision
    reid_recall: float
    reid_precision: float
    candidate_set_size: int     # |C| — first-class parameter (closed-world recall != open-world)
    adversary_id: str           # version-pinned, e.g. "offline-deterministic-v1"
    deterministic: bool         # headline RRS uses the deterministic offline adversary (reidx-01)
    caveat: str                 # MANDATORY — no default; cannot construct without it (FR-009)

    def __post_init__(self) -> None:
        if not self.caveat or not self.caveat.strip():
            raise ValueError("RRSResult requires a non-empty anti-anonymity caveat (FR-009).")
        if self.candidate_set_size < 0:
            raise ValueError("candidate_set_size (|C|) must be >= 0")

    @classmethod
    def from_attack(
        cls,
        reid_recall: float,
        reid_precision: float,
        candidate_set_size: int,
        adversary_id: str,
        deterministic: bool,
    ) -> "RRSResult":
        return cls(
            rrs=1.0 - reid_recall * reid_precision,
            reid_recall=reid_recall,
            reid_precision=reid_precision,
            candidate_set_size=candidate_set_size,
            adversary_id=adversary_id,
            deterministic=deterministic,
            caveat=ANTI_ANONYMITY_CAVEAT,
        )

    def as_dict(self) -> dict:
        # the caveat is ALWAYS serialized — non-strippable (FR-009 / gov-01)
        return {
            "rrs": self.rrs,
            "reid_recall": self.reid_recall,
            "reid_precision": self.reid_precision,
            "candidate_set_size": self.candidate_set_size,
            "adversary_id": self.adversary_id,
            "deterministic": self.deterministic,
            "caveat": self.caveat,
        }


@dataclass(frozen=True)
class MeasuredRRS:
    """The headline MEASURED re-identification result (FR-007).

    Produced by :func:`score_reidentification`: an :class:`RRSResult` (carrying the
    non-strippable anti-anonymity caveat — FR-009) plus the empirical re-identification
    **recall and precision Wilson CIs on integer counts** (reidx-02) and the integer
    tallies they were measured from. ``|C|`` (``candidate_set_size``), the version-pinned
    ``adversary_id`` and the ``deterministic`` flag are recorded so a figure is always
    citable as "RRS vs adversary@version over |C| candidates".
    """

    rrs: RRSResult                # S1 value object — carries the non-strippable caveat (FR-009)
    reid_recall_ci: Interval      # wilson_interval(correct, n_targets, confidence)
    reid_precision_ci: Interval   # wilson_interval(correct, n_guesses, confidence)
    correct: int
    n_targets: int
    n_guesses: int                # non-abstain (committed) guesses — the precision denominator
    candidate_set_size: int
    adversary_id: str
    deterministic: bool
    reid_provenance: object | None = None   # ReidProvenance attaches in S3-08 (forward seam)

    def as_dict(self) -> dict[str, object]:
        # MUST nest self.rrs.as_dict() so the anti-anonymity caveat is ALWAYS serialized
        # (gov-01 / FR-009 — the [AUDIT] test pins this). The CIs serialize their named
        # method + integer n (NFR-002). reid_provenance is included once it is attached (S3-08).
        out: dict[str, object] = {
            "rrs": self.rrs.as_dict(),
            "reid_recall_ci": self.reid_recall_ci.as_dict(),
            "reid_precision_ci": self.reid_precision_ci.as_dict(),
            "correct": self.correct,
            "n_targets": self.n_targets,
            "n_guesses": self.n_guesses,
            "candidate_set_size": self.candidate_set_size,
            "adversary_id": self.adversary_id,
            "deterministic": self.deterministic,
        }
        if self.reid_provenance is not None:
            as_dict = getattr(self.reid_provenance, "as_dict", None)
            out["reid_provenance"] = as_dict() if callable(as_dict) else self.reid_provenance
        return out


def score_reidentification(
    adversary: Adversary,
    targets: Sequence[Target],
    candidates: Sequence[Persona],
    candidate_set_size: int,
    confidence: float = 0.95,
    reid_provenance: object | None = None,
) -> MeasuredRRS:
    """Measure the headline attack RRS (FR-007).

    Run ``adversary`` over the assembled ``(targets, candidates, candidate_set_size)``,
    count correct re-links (a guess whose ``guessed_persona_id`` equals its ``target_id`` —
    the ground-truth link :func:`assemble_paired_set` established), and compute empirical
    re-identification recall and precision with **Wilson CIs on integer (correct, n_targets)
    and (correct, n_guesses)** (reidx-02). Abstentions (``guessed_persona_id is None``) are
    excluded from ``n_guesses`` (the precision denominator) — abstaining is not guessing
    wrong. The result wraps ``RRS = 1 − recall × precision`` in :class:`RRSResult` so the
    non-strippable caveat (FR-009) travels with the number.

    Edge cases (handled GRACEFULLY, never by fabricating a CI):
      * ``n_targets == 0`` → recall defined as ``0.0`` and ``wilson_interval(0, 0)`` returns
        the n=0 sentinel ``Interval(nan, 0.0, 1.0, 0, "wilson", confidence)``.
      * ``n_guesses == 0`` (all-abstain) → precision defined as ``0.0`` and the precision CI
        is likewise the n=0 sentinel. Both come straight from ``stats.intervals`` (its own
        reidx-02 guard), so the CI's named method + integer ``n=0`` are preserved.
    """
    guesses = adversary.attack(targets, candidates, candidate_set_size)
    committed = [g for g in guesses if g.guessed_persona_id is not None]
    n_targets = len(targets)
    n_guesses = len(committed)
    # Ground-truth link: assemble_paired_set set target_id == true persona_id.
    correct = sum(1 for g in committed if g.guessed_persona_id == g.target_id)
    recall = correct / n_targets if n_targets else 0.0
    precision = correct / n_guesses if n_guesses else 0.0
    rrs = RRSResult.from_attack(
        recall, precision, candidate_set_size, adversary.adversary_id, adversary.deterministic
    )
    return MeasuredRRS(
        rrs=rrs,
        # Integer counts ONLY into the Wilson CIs (reidx-02). n=0 cases return the
        # intervals.py n=0 sentinel — we rely on that guard, we do not fabricate a CI.
        reid_recall_ci=wilson_interval(correct, n_targets, confidence),
        reid_precision_ci=wilson_interval(correct, n_guesses, confidence),
        correct=correct,
        n_targets=n_targets,
        n_guesses=n_guesses,
        candidate_set_size=candidate_set_size,
        adversary_id=adversary.adversary_id,
        deterministic=adversary.deterministic,
        reid_provenance=reid_provenance,
    )


# ─── FR-008: deterministic exposure index (pre-screen PRIOR — NOT RRS) + correlation ──
#
# S3-05 (FR-008). The exposure index is the CHEAP pre-screen: a deterministic prior
# computed transparently from the behavioral-signal annotations (recomputing the density
# via the S3-01 ``signals`` module — NOT reading any precomputed scalar). It is a DISTINCT
# type from :class:`MeasuredRRS` with NO ``rrs``/``reid_recall``/``reid_precision`` field and
# a non-empty, validated ``note`` disclaiming RRS — so it is structurally impossible to cite
# the heuristic as a re-identification result (the de-circularization concern). The
# correlation function is the EVIDENCE that the prior tracks the measured attack: Pearson +
# Spearman, computed by hand in pure stdlib (Spearman added because the relationship is
# monotone-but-nonlinear by construction). All pure-stdlib (NFR-004); no RNG/clock (AX-002).

EXPOSURE_INDEX_NOTE = ("Exposure index is a DETERMINISTIC pre-screen PRIOR computed from "
                       "behavioral-signal annotations. It is NOT measured RRS and MUST NOT be "
                       "reported as a re-identification result.")


@dataclass(frozen=True)
class ExposureIndex:
    """A DETERMINISTIC exposure-index pre-screen PRIOR — explicitly NOT measured RRS (FR-008).

    Produced by :func:`exposure_index` by recomputing the behavioral-signal density
    (``signals.compute_signal_density``) transparently from the annotations. It carries NO
    ``rrs``/``reid_recall``/``reid_precision`` field (it is a separate type from
    :class:`MeasuredRRS`) and a non-empty, validated ``note`` that disclaims RRS — so the
    cheap heuristic can never be mistaken for, or cited as, a re-identification result.
    """

    value: float                                # in [0, 1]
    per_signal: tuple[tuple[str, float], ...]   # transparent per-category contribution (sorted)
    method: str = "behavioral-signal-density-v1"
    note: str = EXPOSURE_INDEX_NOTE

    def __post_init__(self) -> None:
        if not self.note.strip():
            raise ValueError("exposure-index note required")

    def as_dict(self) -> dict[str, object]:
        # The prior-not-RRS ``note`` is ALWAYS serialized so the disclaimer travels with the
        # number through any serializer (mirrors the FR-009 caveat discipline on RRSResult).
        return {
            "value": self.value,
            "per_signal": [list(p) for p in self.per_signal],
            "method": self.method,
            "note": self.note,
        }


def exposure_index(behavioral_signals: dict[str, object]) -> ExposureIndex:
    """Compute the FR-008 deterministic exposure-index PRIOR (NOT RRS).

    The ``value`` is RECOMPUTED transparently from the annotations via
    :func:`signals.compute_signal_density` (``0.6*peak + 0.4*mean`` over the per-category
    uniqueness weights) — it deliberately does NOT trust any precomputed
    ``behavioral_signal_density`` scalar that may be present in the block. ``per_signal`` is
    the sorted ``(category, w_c)`` tuples, where ``w_c = signals.UNIQUENESS_WEIGHT[uniqueness]``
    for each detector category present (else ``0.0``) — making every contribution auditable.
    """
    per_signal = tuple(
        sorted(
            (category, signals.UNIQUENESS_WEIGHT.get(sig.get("uniqueness", "none"), 0.0))
            for category, sig in behavioral_signals.items()
            if isinstance(sig, dict) and "uniqueness" in sig
        )
    )
    # Transparent recompute — NOT a read of behavioral_signals["behavioral_signal_density"].
    value = signals.compute_signal_density(behavioral_signals)
    return ExposureIndex(value=value, per_signal=per_signal)


@dataclass(frozen=True)
class IndexRRSCorrelation:
    """Correlation between the cheap exposure-index PRIOR and the measured RRS (FR-008).

    The evidence that the prior tracks the measured attack: ``pearson_r`` (linear) and
    ``spearman_rho`` (rank, robust to the monotone-but-nonlinear relationship). ``n`` is the
    number of paired observations. For ``n == 0`` (or a degenerate zero-variance input) the
    coefficients are ``nan`` (reported, never raised).
    """

    pearson_r: float
    spearman_rho: float
    n: int
    method: str = "pearson+spearman-stdlib"


def _pearson_r(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Pearson product-moment correlation by hand (stdlib). nan on n<2 or zero variance."""
    n = len(xs)
    if n < 2:
        return math.nan
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    denom = math.sqrt(var_x * var_y)
    if denom == 0.0:
        return math.nan  # at least one variable is constant — correlation undefined
    return cov / denom


def _rank(values: Sequence[float]) -> list[float]:
    """Fractional (average-of-ties) ranks — the standard Spearman ranking (stdlib)."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        # tied positions i..j share the average rank (1-based).
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def correlate_index_vs_rrs(pairs: Sequence[tuple[float, float]]) -> IndexRRSCorrelation:
    """Correlate the cheap exposure index against the measured RRS (FR-008).

    ``pairs`` is a sequence of ``(exposure_index_value, measured_rrs_value)`` observations.
    Computes the Pearson ``r`` (covariance / stddevs) and the Spearman ``rho`` (Pearson on
    fractional ranks) by hand in pure stdlib. ``n == 0`` (and any degenerate zero-variance
    input) yields ``nan`` coefficients — reported, never raised — so an empty correlation
    request does not crash a reporting pipeline.
    """
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    n = len(pairs)
    if n == 0:
        return IndexRRSCorrelation(pearson_r=math.nan, spearman_rho=math.nan, n=0)
    pearson = _pearson_r(xs, ys)
    spearman = _pearson_r(_rank(xs), _rank(ys))  # Spearman == Pearson on ranks
    return IndexRRSCorrelation(pearson_r=pearson, spearman_rho=spearman, n=n)
