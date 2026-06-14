"""Statistical core (DC-09): confidence intervals + (future) paired tests, calibration.

Clean-architecture subsystem inside the Hexagonal harness (design D5 switch-point).
"""
from .calibration import (
    Bin,
    CalibrationResult,
    brier_score,
    calibrate,
    calibration_by_entity_class,
    expected_calibration_error,
)
from .intervals import Interval, clopper_pearson_interval, wilson_interval
from .paired import (
    McNemarResult,
    mcnemar_chi2,
    mcnemar_exact,
    paired_bootstrap_recall_delta,
)
from .power import (
    REID_TIER_SPECS,
    TIER_SPECS,
    CellAudit,
    PowerClass,
    PowerMatrix,
    ReidProvenance,
    ReidTier,
    ReidTierSpec,
    Tier,
    TierSpec,
    audit_crossing,
    classify,
    default_tier_of,
    paired_vs_independent_ratio,
    projected_interval,
    projected_wilson_halfwidth,
    reid_required_n,
    required_discordant_pairs,
    required_n,
    target_for_tier,
)

__all__ = [
    "Interval", "wilson_interval", "clopper_pearson_interval",
    "Tier", "TierSpec", "TIER_SPECS", "PowerClass", "CellAudit", "PowerMatrix",
    "required_n", "projected_wilson_halfwidth", "projected_interval",
    "target_for_tier", "classify", "default_tier_of",
    "required_discordant_pairs", "paired_vs_independent_ratio", "audit_crossing",
    # S3-08: re-id-operating-point power ladder seam (NFR-018; sampling-design.md §5)
    "reid_required_n", "ReidTier", "ReidTierSpec", "REID_TIER_SPECS", "ReidProvenance",
    # S4-02: paired detector-A/B regression — McNemar + seeded paired bootstrap (FR-002/NFR-002)
    "McNemarResult", "mcnemar_exact", "mcnemar_chi2", "paired_bootstrap_recall_delta",
    # S4-03: calibration — ECE + Brier + per-bin reliability, per entity class (FR-005/NFR-008)
    "Bin", "CalibrationResult", "expected_calibration_error", "brier_score",
    "calibrate", "calibration_by_entity_class",
]
