"""Deterministic OFFLINE re-identification adversary (FR-007 headline; FR-010 variant).

The *headline* RRS attacker (design revision #1, reidx-01): NO RNG, NO clock, NO network,
NO LLM — fully reproducible. It links pseudonymous :class:`~..base.Target` s to real
:class:`~..base.Persona` candidates using ONLY what survived anonymization, and emits one
ranked :class:`~..base.Guess` per target. The measured RRS *scoring* (recall / precision /
RRS + CIs) is S3-04; this module is the adversary that scorer runs.

reidx-01 (LOAD-BEARING): the TARGET side is described EXCLUSIVELY by post-anonymization
signal — its re-extracted :attr:`~..base.Target.observed_signals` plus the quasi-identifier
token strings still present in :attr:`~..base.Target.anonymized_text`. The gold
:attr:`~..base.Persona.behavioral_signals` of a target's own source is NEVER consulted for
the target; it is only read for the *candidate* pool (the real-side substrate the adversary
searches). Copying gold for the target would collapse the downstream RRS back into the
precomputed heuristic — the exact defect the SME panel flagged.

Determinism (AX-002 / NFR-004): :meth:`OfflineDeterministicAdversary.attack` is a pure
function of ``(targets, candidates, candidate_set_size)``. Ranking uses a total order —
``(similarity desc, persona_id asc)`` — so output is byte-identical across runs and across
candidate input orderings. There is no import of ``random`` / ``time`` / ``datetime`` /
``uuid`` / ``secrets`` and no network/LLM dependency (an AST guard test enforces this).

FR-010: a distractor-augmented (web-like auxiliary) variant is available, version-pinned in
:attr:`~OfflineDeterministicAdversary.adversary_id`. For this story the distractor pool is
caller-supplied via the candidate sequence and the variant version-stamps its id; assembling
distractors from non-candidate tier3 records is S3-01's ``assemble_paired_set`` distractor
mode / later wiring. Effect: |C| grows, precision drops as decoys compete.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..signals import UNIQUENESS_WEIGHT, SignalsBlock
from .base import Guess, Persona, Target

OFFLINE_ADVERSARY_VERSION = "offline-deterministic-v1"
DISTRACTOR_CORPUS_ID = "web-like-distractors-v1"

# The six behavioral-signal categories the extractor emits (the scalar density /
# contribution keys are intentionally excluded — they are derived, not features).
_SIGNAL_CATEGORIES: tuple[str, ...] = (
    "interest_topics",
    "location_signals",
    "personal_anecdote",
    "professional_domain",
    "temporal_patterns",
    "writing_style",
)

# Synthetic category name for the surviving-QI-token feature class (weighted via
# ``feature_weights`` like the behavioral categories; QI tokens survive into the
# anonymized text and are strongly identifying, hence weighted double by default).
_QI_FEATURE = "quasi_identifier_token"


@dataclass(frozen=True)
class OfflineAdversaryConfig:
    """Frozen, hashable configuration for the deterministic offline adversary.

    ``feature_weights`` is a SORTED tuple of ``(category, weight)`` pairs (sorted by
    category name) so the config is a deterministic, stampable reproducibility key. The
    seven categories are the six behavioral-signal categories plus the synthetic
    ``quasi_identifier_token`` class (surviving QI tokens, weighted double by default).
    """

    feature_weights: tuple[tuple[str, float], ...]
    """Sorted ``((category, weight), ...)`` — per signal-category multiplier."""
    score_threshold: float
    """Minimum top-similarity to commit a guess; below it the adversary abstains."""
    tie_break: str = "lexicographic_persona_id"
    """Total-order tie-break label (the ranking always uses ``persona_id`` ascending)."""
    distractor_corpus_id: str | None = None
    """When set, version-stamps the FR-010 distractor-augmented variant (else ``None``)."""

    def weight_of(self, category: str) -> float:
        """Configured multiplier for ``category`` (0.0 if absent — deterministic)."""
        for cat, weight in self.feature_weights:
            if cat == category:
                return weight
        return 0.0


DEFAULT_OFFLINE_CONFIG = OfflineAdversaryConfig(
    feature_weights=(
        ("interest_topics", 1.0),
        ("location_signals", 1.0),
        ("personal_anecdote", 1.0),
        ("professional_domain", 1.0),
        ("temporal_patterns", 1.0),
        ("writing_style", 1.0),
        ("quasi_identifier_token", 2.0),  # surviving QI tokens weigh double
    ),
    score_threshold=0.0,  # 0.0 == always commit the top candidate; raise to force abstention
)


def _signal_feature_weights(block: SignalsBlock, config: OfflineAdversaryConfig) -> dict[str, float]:
    """Weighted feature map from a behavioral/observed-signals block.

    For each of the six categories that is ``present``, emit ``signal:{category} ->
    UNIQUENESS_WEIGHT[uniqueness] * config.weight_of(category)``. A zero product (absent,
    ``none`` uniqueness, or zero config weight) contributes nothing. Pure + deterministic.
    """
    features: dict[str, float] = {}
    for category in _SIGNAL_CATEGORIES:
        sig = block.get(category)
        if not isinstance(sig, dict) or not sig.get("present"):
            continue
        uniqueness = sig.get("uniqueness", "none")
        weight = UNIQUENESS_WEIGHT.get(str(uniqueness), 0.0) * config.weight_of(category)
        if weight > 0.0:
            features[f"signal:{category}"] = weight
    return features


def _candidate_qi_values(candidate: Persona) -> tuple[str, ...]:
    """Distinct, sorted QI value strings for a candidate (deterministic)."""
    return tuple(sorted({value for _entity_type, value in candidate.quasi_identifiers if value}))


def _candidate_feature_weights(
    candidate: Persona, config: OfflineAdversaryConfig
) -> dict[str, float]:
    """The candidate's (real-side) feature map: gold signal features + QI-token features."""
    features = _signal_feature_weights(candidate.behavioral_signals, config)
    qi_weight = config.weight_of(_QI_FEATURE)
    if qi_weight > 0.0:
        for value in _candidate_qi_values(candidate):
            features[f"qi:{value}"] = qi_weight
    return features


def _weighted_jaccard(a: dict[str, float], b: dict[str, float]) -> float:
    """Deterministic weighted Jaccard over two feature->weight maps, in ``[0.0, 1.0]``.

    ``sum_f min(a_f, b_f) / sum_f max(a_f, b_f)`` over the union of feature keys (absent
    features contribute weight 0). Empty union → ``0.0`` (no shared signal == no link).
    """
    keys = a.keys() | b.keys()
    if not keys:
        return 0.0
    intersection = 0.0
    union = 0.0
    for key in keys:
        wa = a.get(key, 0.0)
        wb = b.get(key, 0.0)
        intersection += min(wa, wb)
        union += max(wa, wb)
    if union <= 0.0:
        return 0.0
    return intersection / union


class OfflineDeterministicAdversary:
    """Deterministic offline re-identification adversary (FR-007 / FR-010).

    Satisfies the :class:`~..base.Adversary` Protocol: a version-pinned
    :attr:`adversary_id`, ``deterministic = True``, and :meth:`attack`. The default
    variant's id is :data:`OFFLINE_ADVERSARY_VERSION`; the distractor-augmented variant
    (``config.distractor_corpus_id`` set) version-stamps the id as
    ``"offline-deterministic-v1+distractor:<corpus_id>"`` (FR-010).

    Complexity: :meth:`attack` is ``O(|targets| · |C| · features)`` — note the candidate
    pool dominates; no benchmark tag at story scope (performance is advisory here).
    """

    deterministic = True

    def __init__(self, config: OfflineAdversaryConfig = DEFAULT_OFFLINE_CONFIG) -> None:
        self._config = config
        self.adversary_id = (
            OFFLINE_ADVERSARY_VERSION
            if config.distractor_corpus_id is None
            else f"{OFFLINE_ADVERSARY_VERSION}+distractor:{config.distractor_corpus_id}"
        )

    def attack(
        self,
        targets: Sequence[Target],
        candidates: Sequence[Persona],
        candidate_set_size: int,
    ) -> list[Guess]:
        """Re-link each pseudonymous ``Target`` against the real ``candidates`` pool.

        Deterministic algorithm (per §8b):

        1. Truncate the (optionally distractor-augmented) candidate pool to the closed-world
           ``candidate_set_size`` (|C|). The pool is sorted by ``persona_id`` first so the
           truncation — and therefore the measured |C| — is input-order-independent.
        2. For each target build a feature map from its post-anonymization signal and score
           every candidate by weighted Jaccard over the shared feature catalogue.
        3. Rank by ``(similarity desc, persona_id asc)`` — a TOTAL order, so the result is
           reproducible byte-for-byte across runs and candidate orderings.
        4. Emit ``Guess(target_id, guessed_persona_id=top.persona_id if top_sim >= threshold
           else None, score=top_sim)`` — abstaining below threshold.

        Returns exactly ``len(targets)`` guesses (one per target, in target order) so the
        non-abstain count is integer-countable for the integer-guarded Wilson in S3-04.
        """
        # Sort-then-truncate makes |C| deterministic and order-independent (AX-002). The
        # pool stays in persona_id order for the whole attack so the tie-break below is total.
        pool = sorted(candidates, key=lambda c: c.persona_id)[: max(0, candidate_set_size)]
        qi_weight = self._config.weight_of(_QI_FEATURE)
        # Precompute each candidate's real-side feature map AND its QI value strings once
        # (reused across ALL targets), preserving the persona_id ordering of ``pool``.
        candidate_features: list[tuple[Persona, dict[str, float], tuple[str, ...]]] = [
            (c, _candidate_feature_weights(c, self._config), _candidate_qi_values(c)) for c in pool
        ]

        guesses: list[Guess] = []
        for target in targets:
            # Candidate-INDEPENDENT target work, hoisted OUT of the candidate loop (perf):
            # the post-anonymization signal feature map (reidx-01) + the lowercased haystack.
            target_signal_features = _signal_feature_weights(target.observed_signals, self._config)
            haystack = target.anonymized_text.lower() if qi_weight > 0.0 else ""
            best_persona_id: str | None = None
            best_sim = 0.0
            # Candidates are already in ascending persona_id order; strict ``>`` keeps the
            # FIRST (lexicographically smallest persona_id) on ties → total, deterministic.
            for candidate, cand_features, cand_qi_values in candidate_features:
                # target features = shared signal map + the candidate's QI values that SURVIVED
                # anonymization (substring of the haystack) — the post-anon view only (reidx-01).
                target_features = dict(target_signal_features)
                if qi_weight > 0.0:
                    for value in cand_qi_values:
                        if value.lower() in haystack:
                            target_features[f"qi:{value}"] = qi_weight
                sim = _weighted_jaccard(target_features, cand_features)
                if sim > best_sim:
                    best_sim = sim
                    best_persona_id = candidate.persona_id
            committed = best_persona_id if best_sim >= self._config.score_threshold else None
            guesses.append(
                Guess(target_id=target.target_id, guessed_persona_id=committed, score=best_sim)
            )
        return guesses
