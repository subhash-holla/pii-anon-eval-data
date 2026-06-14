"""Pseudonymization-integrity scorer — "the moat" (DC-08; FR-011/012/013; NFR-005/AX-004).

This is the threat-modeled, collision-separated, EDPB-Art-4(5)-aware pseudonymization
scorer the COMPARISON doc claims no competitor benchmark has. It is a SEPARATE module from
anonymization (NFR-005/AX-004): the :class:`PseudonymizationReport` deliberately carries no
``utility`` / ``residual_risk`` / ``combined`` / ``deid`` / ``overall`` field — pseudonymity
and anonymity are different legal/technical properties and are never merged into one score.

What it emits, given a pseudonymizer-under-test + an enumerated attacker-capability
:class:`ThreatModel`:

* **Unauthorized vs authorized reversal rates** (FR-011) — threat-conditioned, each an
  integer ``(k, n)`` fed to :func:`wilson_interval` (NFR-002; never a fractional count).
* **Collision-type SEPARATION** (FR-012, the moat guarantee) — an *intended* deterministic-
  linkage collision (same real value → same pseudonym) is a **feature** and is reported in
  ``intended_linkage_collisions``; an *unintended cryptographic* collision (two DIFFERENT
  reals → one pseudonym) is a **fault** in ``unintended_crypto_collisions``. The two integers
  are **NEVER summed** — a correct deterministic pseudonymizer has
  ``unintended_crypto_collisions == 0`` and is not penalized for its (feature) linkage.
* **Referential integrity** (FR-013) — the same real entity across records maps to the same
  pseudonym (the join key is stable).
* **Key rotation** (FR-013) — a new epoch's key still authorizes reversal, while an attacker
  holding both epochs' artifacts cannot link the same entity across epochs.
* **Key/state SEPARATION — EDPB Art 4(5)** (FR-013, decisive) — can records be re-joined from
  the artifact ALONE, with no external secret? A keyless deterministic scheme (e.g. bare md5
  of the input — exactly the shape of the real
  ``scripts/enrich_context_preservation.py::PseudonymGenerator``) → ``True``: it FAILS
  separation, which is the correct, important finding to EXPRESS, not a bug to hide. A
  salted + keyed scheme → ``False``.

Determinism (AX-002 / NFR-004): pure stdlib, ``hashlib`` only (deterministic). No RNG, no
clock — statically guarded by an import-purity AST test (S3-07 §6 test 10).
"""
from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from ..stats.intervals import Interval, wilson_interval

PSEUDONYMIZATION_SCORER_VERSION = "pseudo-scorer-v1"

# EDPB Guidelines 01/2025 on pseudonymisation read against GDPR Art. 4(5): pseudonymisation
# means data can no longer be attributed to a specific subject "without the use of additional
# information", kept separately and under technical/organisational safeguards. A scheme whose
# pseudonym is a deterministic function of the input ALONE (no separately-held secret) does
# NOT meet this bar — the artifact is self-rejoinable.
_EDPB_ART_4_5_CITATION = "EDPB / GDPR Art. 4(5)"

# The keyless public constructions an ARTIFACT_ONLY attacker can compute over a candidate
# plaintext space (no secret required). md5 is the real PseudonymGenerator's primitive; we
# also probe sha256 so the dictionary attack admits the common keyless variants.
_KEYLESS_DIGESTS = ("md5", "sha256")


# --------------------------------------------------------------------------------------
# Threat model
# --------------------------------------------------------------------------------------
class AttackerCapability(str, Enum):
    """Enumerated attacker capabilities (the threat model is explicit, not implicit)."""

    ARTIFACT_ONLY = "artifact_only"  # sees pseudonymized output only (Art 4(5) baseline)
    ARTIFACT_PLUS_AUX = "artifact_plus_auxiliary"  # + web-like auxiliary
    KNOWN_PLAINTEXT_SUBSET = "known_plaintext_subset"  # knows some (real→pseudo) pairs
    CROSS_EPOCH_LINKAGE = "cross_epoch_linkage"  # artifacts from 2 key epochs
    HOLDS_KEY = "holds_key"  # authorized reversal (legitimate holder)


@dataclass(frozen=True)
class ThreatModel:
    """A version-pinned, frozen enumeration of attacker capabilities.

    ``model_id`` is pinned onto every :class:`PseudonymizationReport` so a reversal rate is
    always cited *against a named model* ("unauthorized reversal vs pseudo-threat-v1") —
    NFR-007 flavour. ``capabilities`` is stored sorted for a canonical, hashable identity.
    """

    capabilities: tuple[AttackerCapability, ...]
    model_id: str

    def __post_init__(self) -> None:
        if not self.model_id:
            raise ValueError("ThreatModel.model_id must be non-empty (version-pinning).")
        if not self.capabilities:
            raise ValueError("ThreatModel.capabilities must be non-empty.")
        ordered = tuple(sorted(self.capabilities, key=lambda c: c.value))
        object.__setattr__(self, "capabilities", ordered)

    def has(self, capability: AttackerCapability) -> bool:
        return capability in self.capabilities


# --------------------------------------------------------------------------------------
# Outbound port: the pseudonymizer under test
# --------------------------------------------------------------------------------------
@runtime_checkable
class Pseudonymizer(Protocol):
    """Outbound port for an interchangeable pseudonymizer-under-test (FR-011).

    A conforming object exposes a version-pinned ``pseudonymizer_id``; ``pseudonymize`` maps
    a real ``value`` (of ``entity_type``, under a ``context_key`` document scope) to a
    pseudonym; ``reverse`` recovers the plaintext ONLY for a holder of the matching
    ``secret`` (the held key/state), returning ``None`` when unauthorized or impossible.

    The real ``scripts/enrich_context_preservation.py::PseudonymGenerator`` conforms to this
    port — and is precisely the keyless ``md5(value)`` shape that the key/state-separation
    check flags as failing EDPB Art 4(5).
    """

    pseudonymizer_id: str

    def pseudonymize(self, value: str, entity_type: str, *, context_key: str) -> str: ...

    def reverse(self, pseudonym: str, entity_type: str, *, secret: object) -> str | None: ...


# --------------------------------------------------------------------------------------
# Frozen sub-results
# --------------------------------------------------------------------------------------
@dataclass(frozen=True)
class ReferentialIntegrityResult:
    """Is the pseudonym a stable join key (same real entity → same pseudonym)?"""

    join_consistent: bool
    n_joins: int
    broken_joins: int


@dataclass(frozen=True)
class KeyRotationResult:
    """Epoch A vs B: the new key still authorizes reversal, and cross-epoch linkage fails."""

    post_rotation_authorized_reversal_succeeds: bool
    cross_epoch_unauthorized_linkage_fails: bool


@dataclass(frozen=True)
class KeyStateSeparationResult:
    """The decisive EDPB Art 4(5) verdict.

    ``rejoinable_from_artifact_alone`` is ``True`` when records can be re-linked to subjects
    using ONLY the artifact, with no separately-held secret — i.e. the scheme FAILS
    pseudonymisation's "additional information held separately" requirement. ``note`` MUST
    cite EDPB Art 4(5) and is validated non-empty.
    """

    rejoinable_from_artifact_alone: bool
    note: str

    def __post_init__(self) -> None:
        if not self.note or not self.note.strip():
            raise ValueError("KeyStateSeparationResult.note must be non-empty and cite EDPB Art 4(5).")


# --------------------------------------------------------------------------------------
# The report (deliberately NO merged/combined/deid/overall/utility/residual_risk field)
# --------------------------------------------------------------------------------------
@dataclass(frozen=True)
class PseudonymizationReport:
    """Frozen pseudonymization-integrity report (DC-08).

    NFR-005/AX-004: there is DELIBERATELY no ``total_collisions`` / ``combined`` / ``deid`` /
    ``overall`` / ``utility`` / ``residual_risk`` field. Pseudonymity is not anonymity; the
    two collision integers are reported separately and never summed.
    """

    threat_model: ThreatModel
    unauthorized_reversal: Interval
    authorized_reversal: Interval
    intended_linkage_collisions: int  # same real → same pseudonym (FEATURE) — SEPARATE
    unintended_crypto_collisions: int  # distinct reals → same pseudonym (FAULT) — SEPARATE
    crypto_collision_ci: Interval
    referential_integrity: ReferentialIntegrityResult
    key_rotation: KeyRotationResult
    key_state_separation: KeyStateSeparationResult
    pseudonymizer_id: str
    scorer_version: str = PSEUDONYMIZATION_SCORER_VERSION

    def as_dict(self) -> dict[str, object]:
        """Serialize. Carries NO merged/combined field (AX-004 within-module guard)."""
        return {
            "scorer_version": self.scorer_version,
            "pseudonymizer_id": self.pseudonymizer_id,
            "threat_model": {
                "model_id": self.threat_model.model_id,
                "capabilities": [c.value for c in self.threat_model.capabilities],
            },
            "unauthorized_reversal": self.unauthorized_reversal.as_dict(),
            "authorized_reversal": self.authorized_reversal.as_dict(),
            # The two collision integers stay SEPARATE — never a sum (FR-012 moat guarantee).
            "intended_linkage_collisions": self.intended_linkage_collisions,
            "unintended_crypto_collisions": self.unintended_crypto_collisions,
            "crypto_collision_ci": self.crypto_collision_ci.as_dict(),
            "referential_integrity": {
                "join_consistent": self.referential_integrity.join_consistent,
                "n_joins": self.referential_integrity.n_joins,
                "broken_joins": self.referential_integrity.broken_joins,
            },
            "key_rotation": {
                "post_rotation_authorized_reversal_succeeds": (
                    self.key_rotation.post_rotation_authorized_reversal_succeeds
                ),
                "cross_epoch_unauthorized_linkage_fails": (
                    self.key_rotation.cross_epoch_unauthorized_linkage_fails
                ),
            },
            "key_state_separation": {
                "rejoinable_from_artifact_alone": (
                    self.key_state_separation.rejoinable_from_artifact_alone
                ),
                "note": self.key_state_separation.note,
            },
        }


# --------------------------------------------------------------------------------------
# Record normalization
# --------------------------------------------------------------------------------------
def _normalize(records: Iterable[Mapping[str, str] | Sequence[str]]) -> list[tuple[str, str]]:
    """Coerce records into ``(value, entity_type)`` pairs.

    Accepts ``{"value", "entity_type"}`` mappings or ``(value, entity_type)`` sequences.
    """
    out: list[tuple[str, str]] = []
    for rec in records:
        if isinstance(rec, Mapping):
            out.append((str(rec["value"]), str(rec.get("entity_type", "ENTITY"))))
        else:
            value, entity_type = rec[0], rec[1] if len(rec) > 1 else "ENTITY"
            out.append((str(value), str(entity_type)))
    return out


# --------------------------------------------------------------------------------------
# Pure check functions (each integer (k, n) → Wilson)
# --------------------------------------------------------------------------------------
def _collision_counts(pairs: Sequence[tuple[str, str]], tokens: Sequence[str]) -> tuple[int, int, int]:
    """Separate intended-linkage from unintended-crypto collisions.

    Group inputs by pseudonym. Within a pseudonym group:
      * inputs sharing the SAME real value contribute an INTENDED linkage collision (feature),
      * inputs with DIFFERENT real values contribute an UNINTENDED crypto collision (fault).

    Returns ``(intended_linkage_collisions, unintended_crypto_collisions, n_distinct_inputs)``.
    Counts are over distinct real values: ``n_distinct_inputs`` is the Wilson denominator and
    ``unintended_crypto_collisions`` counts distinct reals that share a pseudonym with a
    different real (so the rate is "fraction of distinct inputs caught in a crypto collision").
    """
    token_to_reals: dict[str, set[str]] = {}
    real_to_tokens: dict[str, set[str]] = {}
    for (value, _et), tok in zip(pairs, tokens, strict=True):
        token_to_reals.setdefault(tok, set()).add(value)
        real_to_tokens.setdefault(value, set()).add(tok)

    # Intended linkage: a real value that resolves to a single pseudonym shared by >1
    # occurrence of THAT SAME value (the deterministic-linkage feature).
    occurrences: dict[str, int] = {}
    for value, _et in pairs:
        occurrences[value] = occurrences.get(value, 0) + 1
    intended = sum(
        1
        for value, n in occurrences.items()
        if n > 1 and len(real_to_tokens.get(value, set())) == 1
    )

    # Unintended crypto collision: distinct reals colliding on one pseudonym (a fault).
    crypto_reals: set[str] = set()
    for _tok, reals in token_to_reals.items():
        if len(reals) > 1:
            crypto_reals |= reals
    n_distinct = len(real_to_tokens)
    return intended, len(crypto_reals), n_distinct


def _referential_integrity(pairs: Sequence[tuple[str, str]], tokens: Sequence[str]) -> ReferentialIntegrityResult:
    """Same real entity across records → same pseudonym (a stable join key)?

    Single pass (O(n)): build the real→pseudonyms map and a per-real occurrence count
    together, then a join is "repeated" when its real value occurs more than once
    (``occurrences[v] > 1``, equivalent to the old per-value rescan but without the
    accidental O(n²)). A join is BROKEN when that repeated real maps to >1 pseudonym.
    """
    real_to_tokens: dict[str, set[str]] = {}
    occurrences: dict[str, int] = {}
    for (value, _et), tok in zip(pairs, tokens, strict=True):
        real_to_tokens.setdefault(value, set()).add(tok)
        occurrences[value] = occurrences.get(value, 0) + 1
    repeated = {v: toks for v, toks in real_to_tokens.items() if occurrences[v] > 1}
    n_joins = len(repeated)
    broken = sum(1 for toks in repeated.values() if len(toks) != 1)
    return ReferentialIntegrityResult(
        join_consistent=(broken == 0), n_joins=n_joins, broken_joins=broken
    )


def _keyless_rejoinable(pairs: Sequence[tuple[str, str]], tokens: Sequence[str]) -> bool:
    """EDPB Art 4(5): can the artifact be re-joined to subjects with NO external secret?

    The attacker re-derives, over the OBSERVED candidate plaintext space (the real values in
    the artifact's own scope — a closed-world dictionary), the keyless public digests of each
    candidate, and checks whether any reproduces an actual artifact token. If a keyless
    construction reproduces ≥1 token, the pseudonym is a deterministic function of the input
    ALONE (no separately-held secret) → records are rejoinable from the artifact alone →
    the scheme FAILS pseudonymisation separation. This is exactly the bare-md5 finding.
    """
    artifact_tokens = set(tokens)
    candidates = {value for value, _et in pairs}
    for value in candidates:
        raw = value.encode("utf-8")
        for digest in _KEYLESS_DIGESTS:
            h = hashlib.new(digest, raw).hexdigest()
            # Probe the full digest and common truncations a keyless scheme might emit.
            derived = {h, h[:12], h[:16], "MD5_" + h[:12], "MD5_" + h[:16], "PSN_" + h[:12]}
            if derived & artifact_tokens:
                return True
    return False


def _unauthorized_reversal(
    pairs: Sequence[tuple[str, str]], tokens: Sequence[str], confidence: float
) -> Interval:
    """ARTIFACT_ONLY/AUX dictionary attack: recover plaintext WITHOUT the secret.

    For each pseudonym, the secret-less attacker tries the keyless public digests of every
    candidate plaintext (closed-world). A recovery is a token reproduced by ``digest(value)``.
    Rate = recovered distinct pseudonyms / n distinct pseudonyms (integer → Wilson).
    """
    candidates = {value for value, _et in pairs}
    derived_index: dict[str, str] = {}
    for value in candidates:
        raw = value.encode("utf-8")
        for digest in _KEYLESS_DIGESTS:
            h = hashlib.new(digest, raw).hexdigest()
            for form in (h, h[:12], h[:16], "MD5_" + h[:12], "MD5_" + h[:16], "PSN_" + h[:12]):
                derived_index[form] = value
    distinct_tokens = list(dict.fromkeys(tokens))
    n = len(distinct_tokens)
    recovered = sum(1 for tok in distinct_tokens if tok in derived_index)
    return wilson_interval(recovered, n, confidence)


def _authorized_reversal(
    pseudonymizer: Pseudonymizer,
    pairs: Sequence[tuple[str, str]],
    tokens: Sequence[str],
    secret: object,
    confidence: float,
) -> Interval:
    """HOLDS_KEY: the legitimate holder calls ``reverse(token, secret=key)``.

    Rate = pseudonyms whose ``reverse`` returns the original plaintext / n distinct pseudonyms.
    """
    first_real_for_token: dict[str, str] = {}
    entity_for_token: dict[str, str] = {}
    for (value, et), tok in zip(pairs, tokens, strict=True):
        first_real_for_token.setdefault(tok, value)
        entity_for_token.setdefault(tok, et)
    distinct = list(first_real_for_token.items())
    n = len(distinct)
    ok = 0
    for tok, value in distinct:
        et = entity_for_token[tok]
        recovered = pseudonymizer.reverse(tok, et, secret=secret)
        if recovered == value:
            ok += 1
    return wilson_interval(ok, n, confidence)


def _key_rotation(
    pseudonymizer: Pseudonymizer,
    rotated: Pseudonymizer | None,
    pairs: Sequence[tuple[str, str]],
    secret: object,
) -> KeyRotationResult:
    """Epoch A vs B. With no rotated epoch supplied, the verdicts are vacuously satisfied
    (a single-epoch deployment trivially "succeeds" post-(no-)rotation and has no cross-epoch
    artifacts to link)."""
    if rotated is None:
        return KeyRotationResult(
            post_rotation_authorized_reversal_succeeds=True,
            cross_epoch_unauthorized_linkage_fails=True,
        )
    # 1) The NEW epoch still authorizes reversal for its legitimate holder.
    post_ok = True
    for value, et in pairs:
        tok_b = rotated.pseudonymize(value, et, context_key="doc")
        if rotated.reverse(tok_b, et, secret=_held_secret_of(rotated, secret)) != value:
            post_ok = False
            break
    # 2) An attacker with BOTH epochs' artifacts cannot link the same entity across epochs:
    #    epoch A and epoch B must NOT produce the same pseudonym for the same real value.
    cross_fail = True
    for value, et in pairs:
        tok_a = pseudonymizer.pseudonymize(value, et, context_key="doc")
        tok_b = rotated.pseudonymize(value, et, context_key="doc")
        if tok_a == tok_b:
            cross_fail = False
            break
    return KeyRotationResult(
        post_rotation_authorized_reversal_succeeds=post_ok,
        cross_epoch_unauthorized_linkage_fails=cross_fail,
    )


def _held_secret_of(rotated: Pseudonymizer, fallback: object) -> object:
    """Best-effort: the rotated epoch's own held secret if it exposes one, else the fallback.

    Keeps the scorer's authorized-reversal probe honest for a rotated instance that holds a
    different key than the primary, without widening the Protocol surface.
    """
    secret = getattr(rotated, "_secret", None)
    return secret if secret is not None else fallback


# --------------------------------------------------------------------------------------
# Orchestrator
# --------------------------------------------------------------------------------------
def score_pseudonymization(
    pseudonymizer: Pseudonymizer,
    records: Iterable[Mapping[str, str] | Sequence[str]],
    threat_model: ThreatModel,
    *,
    secret: object,
    rotated_pseudonymizer: Pseudonymizer | None = None,
    confidence: float = 0.95,
) -> PseudonymizationReport:
    """Score a pseudonymizer's integrity against an enumerated :class:`ThreatModel`.

    Pins ``threat_model.model_id`` onto the report (FR-011), reports the two collision
    integers SEPARATELY (FR-012), and emits referential-integrity / key-rotation /
    EDPB-Art-4(5) key-state-separation verdicts (FR-013). Carries no merged/combined field
    (NFR-005/AX-004).
    """
    pairs = _normalize(records)
    tokens = [pseudonymizer.pseudonymize(v, et, context_key="doc") for v, et in pairs]

    intended, crypto_collisions, n_distinct = _collision_counts(pairs, tokens)
    crypto_ci = wilson_interval(crypto_collisions, n_distinct, confidence)

    unauthorized = _unauthorized_reversal(pairs, tokens, confidence)
    authorized = _authorized_reversal(pseudonymizer, pairs, tokens, secret, confidence)

    ref_integrity = _referential_integrity(pairs, tokens)
    rotation = _key_rotation(pseudonymizer, rotated_pseudonymizer, pairs, secret)

    rejoinable = _keyless_rejoinable(pairs, tokens)
    if rejoinable:
        note = (
            f"{_EDPB_ART_4_5_CITATION}: pseudonym is a deterministic function of the input "
            "with no separately-held secret (keyless, e.g. md5(value)); the artifact is "
            "self-rejoinable via a closed-world dictionary attack, so it does NOT satisfy "
            "pseudonymisation's 'additional information held separately' requirement. The real "
            "scripts/enrich_context_preservation.py::PseudonymGenerator has exactly this shape."
        )
    else:
        note = (
            f"{_EDPB_ART_4_5_CITATION}: pseudonyms require a separately-held secret (salted+keyed); "
            "the artifact alone does not permit re-attribution to subjects — consistent with the "
            "Art 4(5) 'additional information held separately' safeguard."
        )
    key_state = KeyStateSeparationResult(rejoinable_from_artifact_alone=rejoinable, note=note)

    return PseudonymizationReport(
        threat_model=threat_model,
        unauthorized_reversal=unauthorized,
        authorized_reversal=authorized,
        intended_linkage_collisions=intended,
        unintended_crypto_collisions=crypto_collisions,
        crypto_collision_ci=crypto_ci,
        referential_integrity=ref_integrity,
        key_rotation=rotation,
        key_state_separation=key_state,
        pseudonymizer_id=pseudonymizer.pseudonymizer_id,
    )
