"""Baseline leaderboard result container (the DETECTION metric family only — AX-004).

Holds the F2-ranked detector leaderboard plus per-entity-type / per-domain / per-language breakdowns,
each cell carrying the AUDITED :func:`pii_anon_datasets.scoring.detection.score_detection` output
(P/R/F1/F2 + Wilson 95% CIs + the separately-reported relaxed ``partial_f1``). Serializes to canonical
sorted-key JSON (byte-reproducible).

It is structurally NOT a merged de-identification score (AX-004 / NFR-005): it exposes no
``overall``/``score``/``combined``/``deid``/``merged``/``fused`` field and is not numeric-coercible, so
``assessment.tracks.assert_no_merged_family`` passes and a :class:`BaselineResults` can be dropped into
``AssessmentTracks(detection=...)`` unchanged. Pure-stdlib, deterministic.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

from ..scoring.core import MATCHING_POLICY_VERSION
from ..scoring.detection import DESIGN_CAVEAT

SCHEMA = "pii-anon-baseline-results/v1"
HARNESS_VERSION = "1.0.0"
SPAN_MATCHING_DISCLOSURE = (
    "Headline metrics use strict-v1 exact (start, end, entity_type) span matching; the relaxed "
    "partial-overlap variant is reported separately as partial_f1 (0.5 overlap credit) and is EXCLUDED "
    "from all confidence intervals (reidx-02). Predicted spans are whitespace-trimmed to their entity "
    "boundary before matching (gold is authoritative and untrimmed)."
)


class BaselineResults:
    """The detection-family leaderboard. ``detectors`` and ``ranking`` already hold serialized dicts, so
    the live object mirrors its JSON shape exactly; no merged cross-family score (AX-004)."""

    def __init__(
        self,
        *,
        dataset: dict,
        confidence: float,
        ranking: list,
        detectors: dict,
    ) -> None:
        self.schema = SCHEMA
        self.harness_version = HARNESS_VERSION
        self.matching_policy = MATCHING_POLICY_VERSION
        self.span_matching_disclosure = SPAN_MATCHING_DISCLOSURE
        self.caveat = DESIGN_CAVEAT
        self.confidence = confidence
        self.dataset = dataset
        self.ranking = ranking
        self.detectors = detectors

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> BaselineResults:
        """Reconstruct from an ``as_dict()`` / loaded ``baseline_results.json`` payload (for merging runs)."""
        return cls(
            dataset=dict(data["dataset"]),  # type: ignore[arg-type]
            confidence=float(data["confidence"]),  # type: ignore[arg-type]
            ranking=list(data["ranking"]),  # type: ignore[arg-type]
            detectors=dict(data["detectors"]),  # type: ignore[arg-type]
        )

    def as_dict(self) -> dict:
        return {
            "schema": self.schema,
            "harness_version": self.harness_version,
            "matching_policy": self.matching_policy,
            "span_matching_disclosure": self.span_matching_disclosure,
            "caveat": self.caveat,
            "confidence": self.confidence,
            "dataset": self.dataset,
            "ranking": self.ranking,
            "detectors": self.detectors,
        }

    def to_json(self) -> str:
        """Canonical sorted-key JSON with a trailing newline — byte-reproducible for provenance hashing."""
        return json.dumps(self.as_dict(), sort_keys=True, ensure_ascii=False) + "\n"
