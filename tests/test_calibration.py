"""Tests for stats.calibration (FR-005 calibration: reliability + ECE + Brier; NFR-008).

S4-03 — the calibration reporting surface of DC-09: Expected Calibration Error (ECE),
Brier score, and per-bin reliability data, computable per entity class. Pure-stdlib +
deterministic (NFR-004): only ``math``/``statistics``; an AST guard pins out
{random, time, uuid, datetime, secrets}.

LOAD-BEARING (NFR-008): the ``ECE ≤ 0.05`` target is a **REFERENCE reported, never a
submitter pass/fail gate** — ``calibrate`` MUST return normally on a high-ECE input and only
surface the comparison as a ``meets_reference`` boolean. ``test_nfr_008_meets_reference_is_
reported_not_gated`` proves a high-ECE input does not raise.

Equal-width binning is PINNED (idx = min(n_bins-1, int(conf*n_bins))) so every ECE value here
is reproducible, not binning-drift-dependent. All worked ECE/Brier values are hand-computed in
the test (the implementation is NOT trusted to produce the reference). Every test fn carries an
``fr_005``/``nfr_008`` token.
"""
import ast
import pathlib

import pytest
from pii_anon_datasets.stats import calibration as calibration_mod
from pii_anon_datasets.stats.calibration import (
    Bin,
    CalibrationResult,
    brier_score,
    calibrate,
    calibration_by_entity_class,
    expected_calibration_error,
)


def test_fr_005_ece_known_value() -> None:
    """ECE on a fixed (confidences, correct) matches a HAND-computed value — [UNIT-TEST].

    Equal-width bins on [0,1], n_bins=10, idx = min(9, int(conf*10)); conf==1.0 → last bin.
    Input (n=8):
        conf 0.05/c0 → bin0   conf 0.15/c0 → bin1   conf 0.25/c1 → bin2
        conf 0.35/c0 → bin3   conf 0.85/c1 → bin8
        conf 0.95/c1, 0.95/c1, 1.00/c0 → bin9  (count 3, acc 2/3, conf_mean 2.9/3)
    ECE = Σ_m (|B_m|/N)·|acc(B_m) − conf_mean(B_m)|
        = 0.125·0.05 + 0.125·0.15 + 0.125·0.75 + 0.125·0.35 + 0.125·0.15 + 0.375·0.3
        = 0.00625 + 0.01875 + 0.09375 + 0.04375 + 0.01875 + 0.1125
        = 0.29375
    """
    confidences = [0.05, 0.15, 0.25, 0.35, 0.85, 0.95, 0.95, 1.00]
    correct = [0, 0, 1, 0, 1, 1, 1, 0]
    ece = expected_calibration_error(confidences, correct, n_bins=10)
    assert ece == pytest.approx(0.29375, abs=1e-12)


def test_fr_005_brier_known_value() -> None:
    """brier_score == mean((conf − correct)²) on a fixed input → known value — [UNIT-TEST].

    Same input as the ECE case. Per-prediction squared errors:
        0.05² 0.15² 0.75² 0.35² 0.15² 0.05² 0.05² 1.00²
      = 0.0025 0.0225 0.5625 0.1225 0.0225 0.0025 0.0025 1.0
      Σ = 1.7375 ; mean over n=8 = 1.7375 / 8 = 0.2171875
    """
    confidences = [0.05, 0.15, 0.25, 0.35, 0.85, 0.95, 0.95, 1.00]
    correct = [0, 0, 1, 0, 1, 1, 1, 0]
    assert brier_score(confidences, correct) == pytest.approx(0.2171875, abs=1e-12)


def test_fr_005_perfect_calibration_zero_ece() -> None:
    """A perfectly-calibrated input → ECE ≈ 0.0 — [UNIT-TEST].

    Within each populated bin the empirical accuracy equals the bin's mean confidence:
      bin 0.25: 4 preds, 1 correct → acc 0.25 == conf_mean 0.25 → contrib 0
      bin 0.75: 4 preds, 3 correct → acc 0.75 == conf_mean 0.75 → contrib 0
    """
    confidences = [0.25, 0.25, 0.25, 0.25, 0.75, 0.75, 0.75, 0.75]
    correct = [1, 0, 0, 0, 1, 1, 1, 0]
    assert expected_calibration_error(confidences, correct, n_bins=10) == pytest.approx(0.0, abs=1e-12)
    # and via the full result object
    res = calibrate(confidences, correct, n_bins=10)
    assert res.ece == pytest.approx(0.0, abs=1e-12)
    assert res.meets_reference is True  # 0.0 <= 0.05


def test_nfr_008_meets_reference_is_reported_not_gated() -> None:
    """meets_reference == (ece <= reference_ece); a HIGH-ECE result RETURNS (no raise) — [UNIT-TEST].

    LOAD-BEARING (NFR-008): ECE ≤ 0.05 is a REFERENCE reported, NOT a submitter gate. Computing a
    badly mis-calibrated input must succeed and merely report ``meets_reference == False`` — it must
    NEVER raise, block, or otherwise gate. (Same fixed input as the ECE case → ECE 0.29375 > 0.05.)
    """
    confidences = [0.05, 0.15, 0.25, 0.35, 0.85, 0.95, 0.95, 1.00]
    correct = [0, 0, 1, 0, 1, 1, 1, 0]

    # high ECE must not raise — calibration is reported, not gated
    res = calibrate(confidences, correct, n_bins=10)
    assert isinstance(res, CalibrationResult)
    assert res.ece == pytest.approx(0.29375, abs=1e-12)
    assert res.reference_ece == 0.05
    assert res.meets_reference is False  # 0.29375 <= 0.05 is False — REPORTED, not raised
    assert res.meets_reference == (res.ece <= res.reference_ece)

    # a calibrated result reports True on the same property (proves it's a live comparison)
    good = calibrate([0.25, 0.25, 0.25, 0.25, 0.75, 0.75, 0.75, 0.75], [1, 0, 0, 0, 1, 1, 1, 0])
    assert good.meets_reference is True
    assert good.meets_reference == (good.ece <= good.reference_ece)

    # round-trippable for reporting; the flag is carried in the dict view too
    d = res.as_dict()
    assert d["ece"] == pytest.approx(0.29375, abs=1e-12)
    assert d["meets_reference"] is False


def test_fr_005_reliability_bins_partition() -> None:
    """reliability bins partition [0,1] (n_bins, equal-width); sum(bin.count) == n — [UNIT-TEST].

    Every prediction lands in EXACTLY one bin: edges are lo=m/n_bins, hi=(m+1)/n_bins, contiguous
    and non-overlapping across the full [0,1] range, and the bin counts sum to n.
    """
    confidences = [0.0, 0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.85, 0.95, 1.00]
    correct = [0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0]
    n_bins = 10
    res = calibrate(confidences, correct, n_bins=n_bins)

    assert len(res.reliability) == n_bins
    # equal-width contiguous partition of [0,1]
    assert res.reliability[0].lo == pytest.approx(0.0)
    assert res.reliability[-1].hi == pytest.approx(1.0)
    for m, b in enumerate(res.reliability):
        assert isinstance(b, Bin)
        assert b.lo == pytest.approx(m / n_bins)
        assert b.hi == pytest.approx((m + 1) / n_bins)
        if m > 0:  # contiguous: this bin starts exactly where the previous ended
            assert b.lo == pytest.approx(res.reliability[m - 1].hi)

    # every prediction in exactly one bin
    assert sum(b.count for b in res.reliability) == len(confidences) == res.n

    # frozen dataclasses (NFR rigor): Bin is immutable
    with pytest.raises((AttributeError, TypeError)):
        res.reliability[0].count = 99  # type: ignore[misc]


def test_nfr_008_calibration_by_entity_class() -> None:
    """calibration_by_entity_class → dict[entity_type, CalibrationResult]; per-class — [UNIT-TEST].

    NFR-008: ECE is reported PER ENTITY CLASS. Each class is calibrated independently.
      PERSON: conf 0.75 × 3 correct + 0.75 × 1 wrong → acc 0.75 == conf_mean → ECE 0.0;
              Brier = mean(0.25², 0.25², 0.25², 0.75²) = (3·0.0625 + 0.5625)/4 = 0.1875
      EMAIL : conf 0.90 × 2 wrong → acc 0.0, conf_mean 0.90 → ECE 0.9; Brier = 0.90² = 0.81
    """
    records = [
        {"entity_type": "PERSON", "confidence": 0.75, "correct": 1},
        {"entity_type": "PERSON", "confidence": 0.75, "correct": 1},
        {"entity_type": "PERSON", "confidence": 0.75, "correct": 1},
        {"entity_type": "PERSON", "confidence": 0.75, "correct": 0},
        {"entity_type": "EMAIL", "confidence": 0.90, "correct": 0},
        {"entity_type": "EMAIL", "confidence": 0.90, "correct": 0},
    ]
    by = calibration_by_entity_class(records, n_bins=10)
    assert set(by) == {"PERSON", "EMAIL"}
    assert all(isinstance(v, CalibrationResult) for v in by.values())

    person = by["PERSON"]
    assert person.entity_class == "PERSON"
    assert person.n == 4
    assert person.ece == pytest.approx(0.0, abs=1e-12)
    assert person.brier == pytest.approx(0.1875, abs=1e-12)
    assert person.meets_reference is True  # 0.0 <= 0.05

    email = by["EMAIL"]
    assert email.entity_class == "EMAIL"
    assert email.n == 2
    assert email.ece == pytest.approx(0.9, abs=1e-12)
    assert email.brier == pytest.approx(0.81, abs=1e-12)
    # reported, not gated: the badly-calibrated class still produced a result
    assert email.meets_reference is False


def test_fr_005_input_length_mismatch_raises() -> None:
    """len(confidences) != len(correct) → ValueError — [UNIT-TEST].

    Mismatched lengths are a CALLER bug (not a calibration outcome) → ValueError. Note this is the
    ONLY raising path: a high ECE is reported, length mismatch is rejected (the §7 negative split).
    """
    with pytest.raises(ValueError):
        calibrate([0.1, 0.2, 0.3], [1, 0], n_bins=10)
    with pytest.raises(ValueError):
        expected_calibration_error([0.1, 0.2], [1, 0, 1], n_bins=10)
    with pytest.raises(ValueError):
        brier_score([0.1, 0.2, 0.3], [1, 1])


def test_fr_005_nfr004_calibration_imports_no_nondeterminism() -> None:
    """AST guard (NFR-004 / AX-002): calibration.py imports none of
    {random, time, uuid, datetime, secrets} — pure ``math``/``statistics`` only — [PROPERTY-TEST].
    """
    src = pathlib.Path(calibration_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)

    banned = {"random", "time", "uuid", "datetime", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), (
        f"calibration.py imports nondeterministic modules: {sorted(banned & imported)}"
    )
