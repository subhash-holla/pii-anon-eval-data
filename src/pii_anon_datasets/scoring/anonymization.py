"""Anonymization scorer — privacy-utility Pareto point (DC-06; FR-006).

The anon-family scorer. Given a system's anonymized text + the assembled adversary inputs,
:func:`score_anonymization` emits a :class:`ParetoPoint` with TWO axes:

  * **privacy** — residual re-identification risk, a :class:`MeasuredRRS` produced by REUSING
    the S3-04 measured-attack machinery (:func:`score_reidentification`). It carries the
    non-strippable anti-anonymity caveat (FR-009) inside its nested ``RRSResult``.
  * **utility** — downstream utility, a :class:`UtilityScore` from a pinned deterministic
    ``token-preservation-v1`` probe.

LOAD-BEARING (NFR-005 / AX-004 — the headline guarantee): the two axes are reported as a
**Pareto point that CANNOT be merged** into a single de-identification score. This is enforced
*structurally*, not by convention:

  * the two axes are nested objects of **different types** (``MeasuredRRS`` vs ``UtilityScore``);
  * there is **no arithmetic field/property** combining them, **no** ``__float__``, and **no**
    ``combined`` / ``overall`` / ``overall_score`` / ``deid`` / ``de_identification_score`` /
    ``score`` attribute anywhere on :class:`ParetoPoint`;
  * :meth:`ParetoPoint.as_dict` yields two SEPARATE sub-objects, never a fused scalar.

``test_nfr005_pareto_point_cannot_merge`` ([AUDIT]) pins this by ``hasattr`` introspection,
``float(point)`` rejection, ``as_dict`` inspection, AND a source grep of this module.

NOTE (allowed): the frozen weights INSIDE :class:`UtilityScore` combine the utility
*components* into one utility number — that is fine. What is forbidden is combining the
privacy and utility **axes**.

Determinism (AX-002 / NFR-004): frozen dataclasses; pure-stdlib; no RNG, no clock. The
``token-preservation-v1`` probe is a deterministic set/Jaccard computation. The bottom of this
file documents the import-purity contract that the NFR-004 AST guard enforces.
"""
from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from .adversary.base import Adversary, Persona, Target
from .reidentification import MeasuredRRS, score_reidentification

# ── pinned probe + the separation disclaimer ─────────────────────────────────────────

UTILITY_PROBE_VERSION = "token-preservation-v1"

PARETO_SEPARATION_NOTE = (
    "Privacy and utility are reported as a Pareto point and are NEVER "
    "combined into a single de-identification score (NFR-005 / AX-004)."
)

# Redaction placeholders an anonymizer leaves behind, e.g. ``[NAME]``, ``[REDACTED]``,
# ``<PERSON>``, ``***``. They mark REMOVED content — they are not preserved utility.
_PLACEHOLDER = re.compile(r"\[[^\]]*\]|<[^>]*>|\*{2,}|█+|x{3,}", re.IGNORECASE)
# Word tokens (unicode-aware): the unit the preservation Jaccard is measured over.
_WORD = re.compile(r"\w+", re.UNICODE)

# Frozen weights combining the utility COMPONENTS into one utility number (NOT the axes).
# When only the probe is available, the primary component carries the full weight (the
# secondaries are absent, so their weight is redistributed by renormalising over present ones).
_W_PRESERVATION = 0.60   # token-preservation Jaccard (always present — the v1 probe)
_W_INFO_RETAINED = 0.25  # 1 - information_loss_ratio (only if utility_metrics supplies it)
_W_COHERENCE = 0.15      # coherence boolean as 0/1 (only if utility_metrics supplies it)


def _content_tokens(text: str) -> set[str]:
    """Lower-cased word tokens with redaction placeholders stripped first.

    Placeholders (``[NAME]``, ``<PERSON>``, ``***``, block chars) are removed BEFORE
    tokenising so the masked content does not count as preserved utility — and so a token
    like ``NAME`` inside ``[NAME]`` never re-enters the set as a "preserved" word.
    """
    return {m.group(0).lower() for m in _WORD.finditer(_PLACEHOLDER.sub(" ", text))}


def _token_preservation_jaccard(original_text: str, anonymized_text: str) -> float:
    """Jaccard overlap of the two content-token sets (deterministic, stdlib).

    ``1.0`` when the anonymized text preserves exactly the original's (non-placeholder)
    tokens; ``0.0`` when nothing survives. Two empty texts are defined as fully preserved
    (``1.0``) — vacuously, no utility was lost.
    """
    o = _content_tokens(original_text)
    a = _content_tokens(anonymized_text)
    if not o and not a:
        return 1.0
    union = o | a
    if not union:
        return 1.0
    return len(o & a) / len(union)


def _as_ratio(value: object) -> float:
    """Coerce a supplied ``utility_metrics`` value to a ratio in ``[0, 1]`` (deterministic).

    Accepts only real numerics (``int``/``float``, but not ``bool`` — a ratio is not a flag);
    anything else is treated as a missing ratio (``0.0``). Clamped to ``[0, 1]`` so a
    caller-supplied out-of-range ratio cannot push ``utility`` outside its invariant.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    return min(1.0, max(0.0, float(value)))


@dataclass(frozen=True)
class UtilityScore:
    """Downstream-utility axis — the pinned ``token-preservation-v1`` probe (FR-006).

    ``utility`` in ``[0, 1]`` (higher = more downstream utility retained) is a fixed weighted
    combination of the transparent named ``components``. The frozen weights combine the utility
    *components* only — this object is NEVER combined with the privacy axis (NFR-005).
    """

    utility: float                              # [0,1]; higher = more downstream utility retained
    components: tuple[tuple[str, float], ...]   # named sub-scores (transparent)
    probe: str = UTILITY_PROBE_VERSION

    def __post_init__(self) -> None:
        if not 0.0 <= self.utility <= 1.0:
            raise ValueError(f"utility must be in [0,1]; got {self.utility!r}")

    def as_dict(self) -> dict[str, object]:
        return {
            "utility": self.utility,
            "components": [list(c) for c in self.components],
            "probe": self.probe,
        }


def score_utility(
    original_text: str,
    anonymized_text: str,
    utility_metrics: dict[str, object] | None = None,
) -> UtilityScore:
    """Deterministic ``token-preservation-v1`` utility probe (FR-006).

    Primary component = the non-placeholder token-preservation Jaccard of
    ``(original_text, anonymized_text)``. If ``utility_metrics`` is supplied, two optional
    secondary components are folded in:

      * ``information_loss_ratio`` (in ``[0,1]``) → ``information_retained = 1 - ratio``;
      * ``coherence`` (truthy/falsy) → ``1.0`` / ``0.0``.

    ``utility`` is the fixed weighted mean of whichever components are present, with the
    weights renormalised over the present components (so the probe alone returns the bare
    preservation Jaccard). Pure-stdlib; deterministic; no RNG/clock.
    """
    preservation = _token_preservation_jaccard(original_text, anonymized_text)
    components: list[tuple[str, float]] = [("token_preservation_jaccard", preservation)]
    weights: list[float] = [_W_PRESERVATION]

    if utility_metrics is not None:
        if "information_loss_ratio" in utility_metrics:
            ratio = _as_ratio(utility_metrics["information_loss_ratio"])
            retained = 1.0 - ratio
            components.append(("information_retained", retained))
            weights.append(_W_INFO_RETAINED)
        if "coherence" in utility_metrics:
            coherent = 1.0 if utility_metrics["coherence"] else 0.0
            components.append(("coherence", coherent))
            weights.append(_W_COHERENCE)

    total_w = sum(weights)
    # components and weights are appended in lockstep above, so they are always equal-length.
    weighted = sum(v * w for (_, v), w in zip(components, weights, strict=True))
    utility = weighted / total_w if total_w else 0.0
    # clamp against float drift so the [0,1] invariant in __post_init__ always holds
    utility = min(1.0, max(0.0, utility))
    return UtilityScore(utility=utility, components=tuple(components))


@dataclass(frozen=True)
class ParetoPoint:
    """The anonymization Pareto point (FR-006) — two SEPARATE, unmergeable axes.

    DELIBERATELY exposes NO ``combined`` / ``overall`` / ``overall_score`` / ``deid`` /
    ``de_identification_score`` / ``score`` property and NO ``__float__``: privacy and utility
    are nested objects of *different types* and can never be fused into a single
    de-identification scalar (NFR-005 / AX-004). The privacy axis (:class:`MeasuredRRS`)
    carries the non-strippable anti-anonymity caveat (FR-009).
    """

    residual_risk: MeasuredRRS    # privacy axis (carries the anti-anonymity caveat — FR-009)
    utility: UtilityScore         # utility axis
    variant: str                  # which anonymized_* variant was scored
    note: str = PARETO_SEPARATION_NOTE

    def __post_init__(self) -> None:
        if not self.note.strip():
            raise ValueError("Pareto separation note required")

    def as_dict(self) -> dict[str, object]:
        """Serialize as two SEPARATE sub-objects — never a fused scalar (NFR-005).

        ``privacy`` nests the full ``MeasuredRRS`` dict (so the FR-009 caveat travels with it);
        ``utility`` nests the ``UtilityScore`` dict. There is deliberately no combined key.
        """
        return {
            "privacy": self.residual_risk.as_dict(),   # carries the FR-009 caveat (non-strippable)
            "utility": self.utility.as_dict(),
            "variant": self.variant,
            "note": self.note,
        }


def score_anonymization(
    adversary: Adversary,
    targets: Sequence[Target],
    candidates: Sequence[Persona],
    candidate_set_size: int,
    *,
    original_text: str,
    anonymized_text: str,
    variant: str,
    utility_metrics: dict[str, object] | None = None,
    confidence: float = 0.95,
) -> ParetoPoint:
    """Score anonymization as a privacy-utility Pareto point (FR-006).

    Privacy axis = :func:`score_reidentification` over the assembled
    ``(targets, candidates, candidate_set_size)`` (REUSED from S3-04 — RRS is NOT
    reimplemented here). Utility axis = :func:`score_utility` on the original/anonymized text
    pair. The two are wrapped in a :class:`ParetoPoint` that no code path can merge into one
    de-identification number (NFR-005 / AX-004).
    """
    residual = score_reidentification(
        adversary, targets, candidates, candidate_set_size, confidence
    )
    util = score_utility(original_text, anonymized_text, utility_metrics)
    return ParetoPoint(residual_risk=residual, utility=util, variant=variant)
