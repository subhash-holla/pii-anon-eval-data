"""Multi-family assessment tracks — detection / anonymization / pseudonymization (CAP-02 NFR-045/055; AX-004).

A privacy assessment scores DIFFERENT metric families that are NEVER collapsed into one "de-identification"
score (AX-004 / NFR-005): detection (a recall leaderboard), anonymization (residual re-identification risk +
utility, reported as a Pareto point), and pseudonymization (unauthorized/authorized reversal + collision
separation + referential integrity). This module lifts the cycle-1 STRUCTURAL separation (``scoring`` +
``compliance.end_state_bundle``) to the ASSESSMENT level: :class:`AssessmentTracks` holds the families as
SEPARATE sections and structurally forbids a merged cross-family headline — there is no ``combined`` /
``overall`` / ``deid`` / ``score`` field, no ``__float__``, and :meth:`as_dict` yields separate sub-objects.
:func:`assert_no_merged_family` is the mutation-tested guard. The existing scorers
(``scoring.anonymization.score_anonymization`` / ``scoring.pseudonymization.score_pseudonymization``) feed the
anon/pseudo tracks unchanged; this container guarantees they are never fused. Pure-stdlib, deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass

TRACKS = ("detection", "anonymization", "pseudonymization")

# Names that would (incorrectly) fuse the legally-distinct families into one score — banned (AX-004 / NFR-005).
# Mirrors compliance.end_state_bundle._FORBIDDEN_MERGE_NAMES at the assessment layer.
_FORBIDDEN_MERGE_NAMES = frozenset({
    "combined", "overall", "overall_score", "deid", "de_identification_score", "score", "merged", "fused",
})

TRACKS_SEPARATION_NOTE = (
    "Detection, anonymization, and pseudonymization are DIFFERENT metric families (AX-004 / NFR-005) and are "
    "never merged into a single de-identification score: anonymization -> residual re-id risk + utility "
    "(a two-axis Pareto point); pseudonymization -> unauthorized/authorized reversal + collision separation + "
    "referential integrity. A merged ranking is structurally impossible in this container."
)


@dataclass(frozen=True)
class AssessmentTracks:
    """The three privacy families as SEPARATE assessment sections; no merged cross-family score (AX-004)."""

    detection: object | None = None             # a report.LeaderboardReport (the recall family)
    anonymization: tuple = ()                    # per-system anonymization results (ParetoPoint-shaped)
    pseudonymization: tuple = ()                 # per-system pseudonymization results (PseudonymizationReport)
    separation_note: str = TRACKS_SEPARATION_NOTE

    def __post_init__(self) -> None:
        if not self.separation_note.strip():
            raise ValueError("AssessmentTracks requires a non-empty AX-004 separation note")

    def as_dict(self) -> dict[str, object]:
        return {
            "tracks": list(TRACKS),
            "detection": self.detection.as_dict() if hasattr(self.detection, "as_dict") else self.detection,
            "anonymization": [p.as_dict() if hasattr(p, "as_dict") else p for p in self.anonymization],
            "pseudonymization": [r.as_dict() if hasattr(r, "as_dict") else r for r in self.pseudonymization],
            "separation_note": self.separation_note,
        }


def assert_no_merged_family(obj: object) -> None:
    """Structural guard (AX-004 / NFR-005): raise ``ValueError`` if any forbidden merged-family field is present,
    or if the object is float-coercible (a single fused score). Mirrors the cycle-1 EndStateBundle / ParetoPoint
    no-merge guards at the assessment layer; the multi-family assessment MUST never expose a fused scalar."""
    present = sorted(n for n in _FORBIDDEN_MERGE_NAMES if hasattr(obj, n))
    if present:
        raise ValueError(f"AX-004 violation: merged-family field(s) {present} forbidden (anon/pseudo never fused)")
    # a single fused score would expose a numeric-coercion dunder — reject ALL of them, not just __float__
    # (an __int__/__index__/__round__-only object is not float()-coercible but is still a fused scalar).
    for dunder in ("__float__", "__int__", "__index__", "__round__"):
        if hasattr(type(obj), dunder):
            raise ValueError(
                f"AX-004 violation: a multi-family assessment object must not be {dunder}-coercible (a fused score)"
            )
