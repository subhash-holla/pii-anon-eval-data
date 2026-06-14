"""Adversary port package (FR-010; DC-07; reidx-01).

Public surface: the frozen value objects + :class:`Adversary` Protocol (from
:mod:`.base`), the deterministic :func:`assemble_paired_set` that builds the paired
*pseudonymous↔real* set from the tier3 corpus substrate, and the headline deterministic
offline adversary (:class:`OfflineDeterministicAdversary` + config — S3-02). The LLM
adversary is S3-03.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .. import signals
from .base import (
    ADVERSARY_PORT_VERSION,
    Adversary,
    Guess,
    Persona,
    Target,
)

# SECONDARY LLM adversary (S3-03; FR-010 secondary). LOAD-BEARING (reidx-01 / NFR-009):
# this is a top-level import that MUST NOT pull in ``anthropic`` at load — ``llm_adversary``
# imports ``anthropic`` LAZILY (only inside ``_require_anthropic``), so this stays offline-safe.
from .llm_adversary import (
    LLM_ADVERSARY_VERSION,
    LLMAdversary,
    make_adversary_id,
)
from .offline_adversary import (
    DEFAULT_OFFLINE_CONFIG,
    OFFLINE_ADVERSARY_VERSION,
    OfflineAdversaryConfig,
    OfflineDeterministicAdversary,
)

# PII-recognition oracle (S7-01; FR-017; DC-10 bounded). Pure-stdlib; carries the
# non-strippable "NEVER agent-leakage scoring" scope guard (ORACLE_DISCLAIMER).
from .oracle import (
    ORACLE_DISCLAIMER,
    OracleVerdict,
    RecognizedEntity,
    recognize,
    recognize_span,
)

# Injection payload library (S7-02; FR-017; DC-10 bounded). INERT synthetic obfuscated-PII
# fixtures (AX-001) — the FR-017 (obfuscated_span, carrier_template, intent_tag) tuple over
# 3 committed faithful transforms (base64/ocr/zero_width); NEVER agent-leakage scoring.
# Pure-stdlib; deterministic (NFR-004 / AX-002).
from .payloads import (
    INERT_DISCLAIMER,
    INTENT_TAGS,
    InjectionPayload,
    build_payloads,
)

__all__ = [
    "ADVERSARY_PORT_VERSION",
    "Adversary",
    "Guess",
    "Persona",
    "Target",
    "DEFAULT_CANDIDATE_SET_SIZE",
    "assemble_paired_set",
    # offline deterministic adversary (S3-02; FR-007 headline / FR-010 distractor variant)
    "OfflineDeterministicAdversary",
    "OfflineAdversaryConfig",
    "DEFAULT_OFFLINE_CONFIG",
    "OFFLINE_ADVERSARY_VERSION",
    # LLM adversary — non-deterministic version-stamped SECONDARY (S3-03; FR-010 / reidx-01)
    "LLMAdversary",
    "make_adversary_id",
    "LLM_ADVERSARY_VERSION",
    # PII-recognition oracle (S7-01; FR-017) — recognition-only, NEVER agent-leakage scoring
    "OracleVerdict",
    "RecognizedEntity",
    "recognize",
    "recognize_span",
    "ORACLE_DISCLAIMER",
    # injection payload library (S7-02; FR-017) — INERT obfuscated-PII fixtures, NEVER agent-leakage scoring
    "InjectionPayload",
    "build_payloads",
    "INTENT_TAGS",
    "INERT_DISCLAIMER",
]

# A loaded corpus record (the JSON object shape ``load_dataset()`` yields).
Record = dict[str, Any]

# Documented default sample of the ~159,891 tier3 personas. |C| is a FIRST-CLASS
# parameter (closed-world recall != open-world): any N <= n_available is valid.
DEFAULT_CANDIDATE_SET_SIZE = 2500


def _quasi_identifiers(record: Record) -> tuple[tuple[str, str], ...]:
    """Sorted ``((entity_type, value), ...)`` from a record's annotations (deterministic)."""
    pairs = [
        (str(a["entity_type"]), str(a["text"]))
        for a in (record.get("annotations") or [])
        if a.get("entity_type") and a.get("text") is not None
    ]
    return tuple(sorted(pairs))


def _has_substrate(record: Record, variant: str) -> bool:
    """True iff the record carries BOTH the gold signals AND the anonymized variant."""
    tier3 = record.get("tier3_evaluation") or {}
    cp = record.get("context_preservation")
    if "behavioral_signals" not in tier3:
        return False
    if not cp:
        return False
    return bool(cp.get(f"anonymized_{variant}"))


def assemble_paired_set(
    records: Sequence[Record],
    *,
    candidate_set_size: int = DEFAULT_CANDIDATE_SET_SIZE,
    variant: str = "pseudonymized",
) -> tuple[list[Target], list[Persona]]:
    """Deterministically build the paired ``(targets, candidates)`` set (FR-010; DC-07).

    1. Filter to records carrying BOTH ``tier3_evaluation.behavioral_signals`` AND a
       ``context_preservation.anonymized_{variant}`` — records lacking either substrate
       are skipped silently (an all-empty input yields ``([], [])``).
    2. Sort deterministically by ``record_id`` (sort-based, no RNG — AX-002); take the
       first ``min(candidate_set_size, n_available)`` as the candidate pool.
    3. :class:`Persona` (the real side): ``persona_id == record_id``, sorted
       ``quasi_identifiers``, gold ``behavioral_signals``, original ``source_text``.
    4. :class:`Target` (the pseudonymous side): ``anonymized_text`` from the variant,
       ``observed_signals = signals.extract(anonymized_text)`` — RE-EXTRACTED, never
       copied from gold (reidx-01) — and ``target_id == persona_id`` (ground-truth link).
    """
    substrate = [r for r in records if _has_substrate(r, variant)]
    substrate.sort(key=lambda r: r["record_id"])
    selected = substrate[: max(0, candidate_set_size)]

    candidates: list[Persona] = []
    targets: list[Target] = []
    for record in selected:
        record_id = record["record_id"]
        gold_signals = record["tier3_evaluation"]["behavioral_signals"]
        anonymized_text = record["context_preservation"][f"anonymized_{variant}"]

        candidates.append(
            Persona(
                persona_id=record_id,
                record_id=record_id,
                quasi_identifiers=_quasi_identifiers(record),
                behavioral_signals=gold_signals,
                source_text=record.get("text", ""),
            )
        )
        targets.append(
            Target(
                target_id=record_id,
                anonymized_text=anonymized_text,
                observed_signals=signals.extract(anonymized_text),
            )
        )

    return targets, candidates
