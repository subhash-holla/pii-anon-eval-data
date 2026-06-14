"""Calibration reporting: ECE + Brier + per-bin reliability (FR-005, DC-09).

A detector that emits confidences is *calibrated* when its stated confidence matches its
empirical accuracy. This module computes, per entity class when grouped:

* the **Expected Calibration Error (ECE)** — the bin-weighted gap between accuracy and mean
  confidence, ``ECE = Σ_m (|B_m|/N)·|acc(B_m) − conf_mean(B_m)|``;
* the **Brier score** — ``mean((conf − correct)²)``, a strictly-proper scoring rule; and
* the **per-bin reliability** data (a :class:`Bin` per equal-width bucket) that a reliability
  diagram is drawn from (S4-05 consumes :class:`CalibrationResult`).

**NFR-008 is a REFERENCE, NOT a gate (load-bearing).** The ``ECE ≤ 0.05`` target is reported per
entity class for *reference/baseline* detectors; it is **not** a submitter pass/fail. This module
therefore NEVER raises or blocks on a high ECE — it surfaces the comparison only through the
:attr:`CalibrationResult.meets_reference` boolean property. The single raising path is a caller
bug: ``len(confidences) != len(correct)`` → :class:`ValueError`.

**Binning convention is PINNED** (so the ECE value is reproducible, not binning-drift-dependent):
equal-width bins on ``[0, 1]``; a confidence lands in bin ``idx = min(n_bins-1, int(conf*n_bins))``
(so ``conf == 1.0`` falls in the last bin). Bin ``m`` spans ``[m/n_bins, (m+1)/n_bins]``.

Pure-stdlib (``math``/``statistics`` only — NFR-004); deterministic (no RNG/clock — AX-002).
"""
from __future__ import annotations

import statistics
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import SupportsFloat, SupportsInt, cast

# Default reference target for NFR-008 (reported, never a gate).
_REFERENCE_ECE = 0.05


@dataclass(frozen=True)
class Bin:
    """One equal-width reliability bucket spanning ``[lo, hi]`` of the confidence axis.

    ``conf_mean`` / ``acc`` are the mean confidence and empirical accuracy of the ``count``
    predictions that landed in this bin (both ``0.0`` for an empty bin). Frozen → immutable so a
    :class:`CalibrationResult` is a safe, hashable reporting value.
    """

    lo: float
    hi: float
    conf_mean: float
    acc: float
    count: int

    def as_dict(self) -> dict[str, object]:
        return {
            "lo": self.lo,
            "hi": self.hi,
            "conf_mean": self.conf_mean,
            "acc": self.acc,
            "count": self.count,
        }


@dataclass(frozen=True)
class CalibrationResult:
    """Calibration summary for one population (optionally one entity class).

    Carries the headline ``ece`` + ``brier``, the sample size ``n`` and bin count ``n_bins``, the
    full per-bin ``reliability`` tuple, and — for NFR-008 — the ``reference_ece`` target plus the
    derived :attr:`meets_reference` flag. ``entity_class`` is set when produced by
    :func:`calibration_by_entity_class`, else ``None``.
    """

    ece: float
    brier: float
    n: int
    n_bins: int
    reliability: tuple[Bin, ...]
    entity_class: str | None = None
    reference_ece: float = _REFERENCE_ECE

    @property
    def meets_reference(self) -> bool:
        """``True`` iff ``ece <= reference_ece`` (NFR-008). REPORTED, never a pass/fail gate.

        This is the *only* place the ``ECE ≤ 0.05`` reference surfaces. Calibration itself never
        raises or blocks on a high ECE — a mis-calibrated detector simply reports ``False`` here.
        """
        return self.ece <= self.reference_ece

    def as_dict(self) -> dict[str, object]:
        return {
            "ece": self.ece,
            "brier": self.brier,
            "n": self.n,
            "n_bins": self.n_bins,
            "reliability": [b.as_dict() for b in self.reliability],
            "entity_class": self.entity_class,
            "reference_ece": self.reference_ece,
            "meets_reference": self.meets_reference,
        }


def _check_lengths(confidences: Sequence[float], correct: Sequence[int], fname: str) -> None:
    """Length-mismatch guard — the single raising path (a caller bug, not a calibration outcome)."""
    if len(confidences) != len(correct):
        raise ValueError(
            f"{fname}: len(confidences) ({len(confidences)}) != len(correct) ({len(correct)})"
        )


def _bin_index(conf: float, n_bins: int) -> int:
    """PINNED equal-width assignment: ``idx = min(n_bins-1, int(conf*n_bins))``.

    Pinning this convention (vs. e.g. equal-frequency bins) is what makes the reported ECE value
    reproducible rather than binning-drift-dependent. ``conf == 1.0`` clamps into the last bin.
    """
    return min(n_bins - 1, int(conf * n_bins))


def expected_calibration_error(
    confidences: Sequence[float], correct: Sequence[int], *, n_bins: int = 10
) -> float:
    """ECE over equal-width bins on ``[0, 1]``: ``Σ_m (|B_m|/N)·|acc(B_m) − conf_mean(B_m)|``.

    Empty bins contribute nothing. ``len(confidences) != len(correct)`` → :class:`ValueError`; an
    empty input → ``0.0``. Bin assignment follows the pinned convention (:func:`_bin_index`).
    """
    _check_lengths(confidences, correct, "expected_calibration_error")
    n = len(confidences)
    if n == 0:
        return 0.0
    conf_sums = [0.0] * n_bins
    acc_sums = [0.0] * n_bins
    counts = [0] * n_bins
    for conf, y in zip(confidences, correct, strict=True):  # lengths checked above
        idx = _bin_index(conf, n_bins)
        conf_sums[idx] += conf
        acc_sums[idx] += y
        counts[idx] += 1
    ece = 0.0
    for m in range(n_bins):
        if counts[m] == 0:
            continue
        conf_mean = conf_sums[m] / counts[m]
        acc = acc_sums[m] / counts[m]
        ece += (counts[m] / n) * abs(acc - conf_mean)
    return ece


def brier_score(confidences: Sequence[float], correct: Sequence[int]) -> float:
    """Brier score ``mean((conf − correct)²)`` — a strictly-proper scoring rule.

    ``len(confidences) != len(correct)`` → :class:`ValueError`; an empty input → ``0.0``.
    """
    _check_lengths(confidences, correct, "brier_score")
    if not confidences:
        return 0.0
    return statistics.fmean(
        (conf - y) ** 2 for conf, y in zip(confidences, correct, strict=True)  # lengths checked above
    )


def _reliability_bins(
    confidences: Sequence[float], correct: Sequence[int], n_bins: int
) -> tuple[Bin, ...]:
    """Build the equal-width :class:`Bin` tuple partitioning ``[0, 1]`` (every pred in exactly one).

    Bin ``m`` spans ``[m/n_bins, (m+1)/n_bins]``; the tuple has length ``n_bins`` and its counts sum
    to ``len(confidences)``. Empty bins carry ``conf_mean == acc == 0.0``.
    """
    conf_sums = [0.0] * n_bins
    acc_sums = [0.0] * n_bins
    counts = [0] * n_bins
    for conf, y in zip(confidences, correct, strict=True):  # lengths checked by caller (calibrate)
        idx = _bin_index(conf, n_bins)
        conf_sums[idx] += conf
        acc_sums[idx] += y
        counts[idx] += 1
    bins: list[Bin] = []
    for m in range(n_bins):
        lo = m / n_bins
        hi = (m + 1) / n_bins
        if counts[m] == 0:
            bins.append(Bin(lo, hi, 0.0, 0.0, 0))
        else:
            bins.append(
                Bin(lo, hi, conf_sums[m] / counts[m], acc_sums[m] / counts[m], counts[m])
            )
    return tuple(bins)


def calibrate(
    confidences: Sequence[float],
    correct: Sequence[int],
    *,
    n_bins: int = 10,
    entity_class: str | None = None,
) -> CalibrationResult:
    """Compute ECE + Brier + per-bin reliability for one population → :class:`CalibrationResult`.

    ``len(confidences) != len(correct)`` → :class:`ValueError` (the only raising path). A high ECE
    is **reported, never gated** (NFR-008): this returns normally and the comparison is surfaced via
    :attr:`CalibrationResult.meets_reference`.
    """
    _check_lengths(confidences, correct, "calibrate")
    ece = expected_calibration_error(confidences, correct, n_bins=n_bins)
    brier = brier_score(confidences, correct)
    reliability = _reliability_bins(confidences, correct, n_bins)
    return CalibrationResult(
        ece=ece,
        brier=brier,
        n=len(confidences),
        n_bins=n_bins,
        reliability=reliability,
        entity_class=entity_class,
    )


def calibration_by_entity_class(
    records: Sequence[Mapping[str, object]], *, n_bins: int = 10
) -> dict[str, CalibrationResult]:
    """Group ``records`` by ``entity_type`` and :func:`calibrate` each class independently (NFR-008).

    Each record is a mapping carrying ``entity_type`` + ``confidence`` + ``correct``. Returns
    ``dict[entity_type, CalibrationResult]`` with each result's ``entity_class`` set. Class iteration
    order follows first-appearance (insertion-ordered dict) → deterministic.
    """
    grouped_conf: dict[str, list[float]] = {}
    grouped_correct: dict[str, list[int]] = {}
    for rec in records:
        entity_type = str(rec["entity_type"])
        conf = float(cast(SupportsFloat, rec["confidence"]))
        y = int(cast(SupportsInt, rec["correct"]))
        grouped_conf.setdefault(entity_type, []).append(conf)
        grouped_correct.setdefault(entity_type, []).append(y)
    return {
        entity_type: calibrate(
            grouped_conf[entity_type],
            grouped_correct[entity_type],
            n_bins=n_bins,
            entity_class=entity_type,
        )
        for entity_type in grouped_conf
    }
