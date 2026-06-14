"""Hexagonal scoring harness (DC-04..DC-08): closes finding M6.

Turns precomputed Tier-2/3 annotations into RUNNING scorers that ingest a
system's output via adapter ports. Public surface:
"""
from . import signals
from .adversary import (
    DEFAULT_CANDIDATE_SET_SIZE,
    DEFAULT_OFFLINE_CONFIG,
    LLM_ADVERSARY_VERSION,
    OFFLINE_ADVERSARY_VERSION,
    Adversary,
    Guess,
    LLMAdversary,
    OfflineAdversaryConfig,
    OfflineDeterministicAdversary,
    Persona,
    Target,
    assemble_paired_set,
    make_adversary_id,
)
from .anonymization import (
    PARETO_SEPARATION_NOTE,
    UTILITY_PROBE_VERSION,
    ParetoPoint,
    UtilityScore,
    score_anonymization,
    score_utility,
)
from .core import MATCHING_POLICY_VERSION, Counts, Span, SpanAdapter, match_strict
from .detection import DESIGN_CAVEAT, DesignProvenance, DetectionScore, score_detection
from .pseudonymization import (
    PSEUDONYMIZATION_SCORER_VERSION,
    AttackerCapability,
    KeyRotationResult,
    KeyStateSeparationResult,
    PseudonymizationReport,
    Pseudonymizer,
    ReferentialIntegrityResult,
    ThreatModel,
    score_pseudonymization,
)
from .reidentification import (
    ANTI_ANONYMITY_CAVEAT,
    EXPOSURE_INDEX_NOTE,
    ExposureIndex,
    IndexRRSCorrelation,
    MeasuredRRS,
    RRSResult,
    correlate_index_vs_rrs,
    exposure_index,
    score_reidentification,
)

__all__ = [
    "Span",
    "SpanAdapter",
    "Counts",
    "match_strict",
    "MATCHING_POLICY_VERSION",
    "DetectionScore",
    "score_detection",
    "DesignProvenance",
    "DESIGN_CAVEAT",
    "RRSResult",
    "ANTI_ANONYMITY_CAVEAT",
    # measured-attack RRS scorer (S3-04; FR-007 headline / FR-009 caveat / reidx-02)
    "MeasuredRRS",
    "score_reidentification",
    # deterministic exposure-index PRIOR (NOT RRS) + index<->RRS correlation (S3-05; FR-008)
    "ExposureIndex",
    "EXPOSURE_INDEX_NOTE",
    "exposure_index",
    "IndexRRSCorrelation",
    "correlate_index_vs_rrs",
    # adversary port (S3-01; FR-010 / DC-07 / reidx-01)
    "signals",
    "Persona",
    "Target",
    "Guess",
    "Adversary",
    "assemble_paired_set",
    "DEFAULT_CANDIDATE_SET_SIZE",
    # offline deterministic adversary (S3-02; FR-007 headline / FR-010 distractor variant)
    "OfflineDeterministicAdversary",
    "OfflineAdversaryConfig",
    "DEFAULT_OFFLINE_CONFIG",
    "OFFLINE_ADVERSARY_VERSION",
    # LLM adversary — non-deterministic version-stamped SECONDARY (S3-03; FR-010 / reidx-01)
    "LLMAdversary",
    "make_adversary_id",
    "LLM_ADVERSARY_VERSION",
    # pseudonymization-integrity scorer — the moat (S3-07; DC-08; FR-011/012/013; NFR-005/AX-004)
    "score_pseudonymization",
    "PseudonymizationReport",
    "Pseudonymizer",
    "ThreatModel",
    "AttackerCapability",
    "ReferentialIntegrityResult",
    "KeyRotationResult",
    "KeyStateSeparationResult",
    "PSEUDONYMIZATION_SCORER_VERSION",
    # anonymization privacy-utility Pareto scorer (S3-06; DC-06; FR-006; NFR-005/AX-004; FR-009)
    "score_anonymization",
    "ParetoPoint",
    "UtilityScore",
    "score_utility",
    "UTILITY_PROBE_VERSION",
    "PARETO_SEPARATION_NOTE",
]
