"""S3-07 — pseudonymization-integrity scorer (the moat, DC-08).

Tokened FR-011/FR-012/FR-013 + NFR-005/NFR-004. Every test fn carries an ``fr_NNN`` /
``nfr0NN`` token so the traceability gate can map test→requirement.

This is "the moat": threat-modeled reversal rates, collision-type SEPARATION (an intended
deterministic-linkage collision is a *feature* and is reported separately from an
unintended cryptographic collision, a *fault* — the two are NEVER summed), referential
integrity, key-rotation, and the decisive EDPB-Art-4(5) key/state-separation test.

Reference pseudonymizers are defined INLINE (no ``scripts/`` import) so the test pins the
:class:`Pseudonymizer` Protocol contract, not an enrichment implementation:

  * :class:`_ReversibleKeyedPseudonymizer` — the *correct* one (deterministic, salted+keyed;
    same real → same pseudonym; reversal requires the held secret).
  * :class:`_BareMd5Pseudonymizer` — md5-no-salt-no-secret; models the real
    ``scripts/enrich_context_preservation.py::PseudonymGenerator`` — *fails Art 4(5)*.
  * :class:`_CollidingPseudonymizer` — maps two DIFFERENT reals to the SAME pseudonym — *faulty*.
"""
from __future__ import annotations

import ast
import hashlib
import pathlib

import pytest
from pii_anon_datasets.scoring import pseudonymization as pseudo_mod
from pii_anon_datasets.scoring.pseudonymization import (
    AttackerCapability,
    KeyRotationResult,
    KeyStateSeparationResult,
    Pseudonymizer,
    ReferentialIntegrityResult,
    ThreatModel,
    score_pseudonymization,
)
from pii_anon_datasets.stats.intervals import Interval

# --------------------------------------------------------------------------------------
# Inline reference pseudonymizers (the Protocol's three archetypes). Pure stdlib.
# --------------------------------------------------------------------------------------

# A tiny closed candidate plaintext space so an ARTIFACT_ONLY dictionary attack on a
# *bare* (no-secret) pseudonymizer is feasible — this is how the scorer proves a keyless
# deterministic scheme is reversible from the artifact alone.
_CANDIDATE_PLAINTEXTS = ("Alice", "Bob", "Carol", "Dave", "Erin", "Frank")


class _ReversibleKeyedPseudonymizer:
    """The CORRECT pseudonymizer: deterministic, salted + keyed.

    Same real value → same pseudonym (referential integrity / intended linkage is a
    feature). The mapping is keyed HMAC(secret, salt||value), so an ARTIFACT_ONLY attacker
    cannot recover the plaintext (the salt+key are not in the artifact). Reversal needs the
    held secret (the legitimate key holder keeps the forward table).
    """

    def __init__(self, secret: str = "k3y", salt: str = "s4lt", epoch: str = "A") -> None:
        self.pseudonymizer_id = f"reversible-keyed@{epoch}"
        self._secret = secret
        self._salt = salt
        self._forward: dict[str, str] = {}
        self._reverse: dict[str, str] = {}

    def pseudonymize(self, value: str, entity_type: str, *, context_key: str) -> str:
        mac = hashlib.sha256(
            (self._secret + "|" + self._salt + "|" + entity_type + "|" + value).encode("utf-8")
        ).hexdigest()[:16]
        token = f"PSN_{entity_type}_{mac}"
        self._forward[value] = token
        self._reverse[token] = value
        return token

    def reverse(self, pseudonym: str, entity_type: str, *, secret: object) -> str | None:
        # Only the holder of the matching secret (the forward table is gated on it) can reverse.
        if secret != self._secret:
            return None
        return self._reverse.get(pseudonym)


class _BareMd5Pseudonymizer:
    """A KEYLESS pseudonymizer: md5(value), no salt, no secret.

    Models the real ``scripts/enrich_context_preservation.py::PseudonymGenerator`` shape
    (``int(hashlib.md5(value.encode()).hexdigest(), 16) % N``). Because the pseudonym is a
    pure deterministic function of the input with NO external secret, an attacker holding
    only the artifact can re-derive the mapping by hashing the candidate plaintext space —
    so records are RE-JOINABLE FROM THE ARTIFACT ALONE → it FAILS EDPB Art 4(5).
    """

    def __init__(self) -> None:
        self.pseudonymizer_id = "bare-md5"

    def pseudonymize(self, value: str, entity_type: str, *, context_key: str) -> str:
        return "MD5_" + hashlib.md5(value.encode("utf-8")).hexdigest()[:12]

    def reverse(self, pseudonym: str, entity_type: str, *, secret: object) -> str | None:
        # No held forward table; "reversal" is only possible via the public dictionary attack
        # the scorer performs (which is the whole point — it needs no secret).
        return None


class _CollidingPseudonymizer:
    """A FAULTY pseudonymizer: collapses two DIFFERENT real values onto ONE pseudonym.

    ``_collide`` maps {"Alice", "Bob"} → the same token (an UNINTENDED cryptographic
    collision — a fault), while still being deterministic for everything else.
    """

    def __init__(self, collide: tuple[str, str] = ("Alice", "Bob")) -> None:
        self.pseudonymizer_id = "colliding-faulty"
        self._collide = set(collide)

    def pseudonymize(self, value: str, entity_type: str, *, context_key: str) -> str:
        if value in self._collide:
            return "PSN_COLLIDED"
        return "PSN_" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]

    def reverse(self, pseudonym: str, entity_type: str, *, secret: object) -> str | None:
        return None


def _records(*pairs: tuple[str, str]) -> list[dict]:
    """Build records as ``{"value", "entity_type"}`` dicts. Repeating a value models the
    SAME real entity appearing in multiple records (the referential-integrity join key)."""
    return [{"value": v, "entity_type": et} for v, et in pairs]


_DEFAULT_RECORDS = _records(
    ("Alice", "PERSON_NAME"),
    ("Bob", "PERSON_NAME"),
    ("Carol", "PERSON_NAME"),
    ("Alice", "PERSON_NAME"),  # Alice repeats → intended linkage collision (a feature)
    ("Dave", "PERSON_NAME"),
)

_TM_UNAUTHORIZED = ThreatModel(
    capabilities=(AttackerCapability.ARTIFACT_ONLY, AttackerCapability.ARTIFACT_PLUS_AUX),
    model_id="pseudo-threat-v1",
)
_TM_AUTHORIZED = ThreatModel(
    capabilities=(AttackerCapability.HOLDS_KEY,),
    model_id="pseudo-threat-v1-authorized",
)


# --------------------------------------------------------------------------------------
# FR-012 — collision-type SEPARATION (the moat guarantee)
# --------------------------------------------------------------------------------------
def test_fr_012_correct_deterministic_has_zero_crypto_collisions():
    """[AUDIT] A correct deterministic pseudonymizer is NEVER penalized: its only
    collisions are intended (same real → same pseudonym = a feature). So
    ``unintended_crypto_collisions == 0`` while ``intended_linkage_collisions > 0``; and
    the report MUST NOT expose a ``total_collisions`` field (never sum the two)."""
    report = score_pseudonymization(
        _ReversibleKeyedPseudonymizer(),
        _DEFAULT_RECORDS,
        _TM_UNAUTHORIZED,
        secret="k3y",
    )
    assert report.unintended_crypto_collisions == 0
    assert report.intended_linkage_collisions > 0  # Alice repeated → an intended collision
    # The moat guarantee: the two integers are NEVER summed into one field.
    assert not hasattr(report, "total_collisions")
    assert "total_collisions" not in report.as_dict()


def test_fr_012_faulty_pseudonymizer_flags_crypto_collisions():
    """[UNIT-TEST] A pseudonymizer that maps two DIFFERENT reals to one pseudonym yields
    ``unintended_crypto_collisions > 0`` with a valid Wilson CI built from integer (k, n)."""
    report = score_pseudonymization(
        _CollidingPseudonymizer(("Alice", "Bob")),
        _DEFAULT_RECORDS,
        _TM_UNAUTHORIZED,
        secret=None,
    )
    assert report.unintended_crypto_collisions > 0
    assert isinstance(report.crypto_collision_ci, Interval)
    assert report.crypto_collision_ci.method == "wilson"
    assert isinstance(report.crypto_collision_ci.n, int)
    assert report.crypto_collision_ci.n > 0


# --------------------------------------------------------------------------------------
# FR-011 — threat-conditioned reversal rates (integer → Wilson)
# --------------------------------------------------------------------------------------
def test_fr_011_reversal_rates_are_threat_conditioned():
    """[UNIT-TEST] Reversal rates are Wilson Intervals with INTEGER denominators, and the
    report records WHICH ``ThreatModel.model_id`` they were measured against."""
    report = score_pseudonymization(
        _ReversibleKeyedPseudonymizer(),
        _DEFAULT_RECORDS,
        _TM_UNAUTHORIZED,
        secret="k3y",
    )
    assert isinstance(report.unauthorized_reversal, Interval)
    assert isinstance(report.authorized_reversal, Interval)
    assert isinstance(report.unauthorized_reversal.n, int)
    assert isinstance(report.authorized_reversal.n, int)
    assert report.unauthorized_reversal.method == "wilson"
    # The result is pinned to the threat model it was measured against (NFR-007 flavour).
    assert report.threat_model.model_id == "pseudo-threat-v1"


def test_fr_011_authorized_succeeds_unauthorized_fails_for_keyed():
    """[UNIT-TEST] For the correct keyed scheme: authorized (HOLDS_KEY) reversal ≈ 1.0;
    unauthorized (ARTIFACT_ONLY, no secret) ≈ 0 — the artifact does not leak the plaintext."""
    report = score_pseudonymization(
        _ReversibleKeyedPseudonymizer(),
        _DEFAULT_RECORDS,
        _TM_UNAUTHORIZED,
        secret="k3y",
    )
    assert report.authorized_reversal.point == pytest.approx(1.0)
    assert report.unauthorized_reversal.point == pytest.approx(0.0)


# --------------------------------------------------------------------------------------
# FR-013 — referential integrity / key-rotation / key-state separation
# --------------------------------------------------------------------------------------
def test_fr_013_referential_integrity_join_stable():
    """[UNIT-TEST] A real entity repeated across records → the SAME pseudonym
    (``join_consistent is True``, ``broken_joins == 0``). A non-deterministic pseudonymizer
    that re-randomises per call breaks the join."""
    ok = score_pseudonymization(
        _ReversibleKeyedPseudonymizer(),
        _DEFAULT_RECORDS,
        _TM_UNAUTHORIZED,
        secret="k3y",
    )
    assert isinstance(ok.referential_integrity, ReferentialIntegrityResult)
    assert ok.referential_integrity.join_consistent is True
    assert ok.referential_integrity.broken_joins == 0
    assert ok.referential_integrity.n_joins >= 1  # Alice repeats → at least one join checked

    class _NonDeterministic:
        pseudonymizer_id = "nondeterministic"

        def __init__(self) -> None:
            self._n = 0

        def pseudonymize(self, value: str, entity_type: str, *, context_key: str) -> str:
            self._n += 1
            return f"{value}_{self._n}"  # different token every call → join breaks

        def reverse(self, pseudonym: str, entity_type: str, *, secret: object) -> str | None:
            return None

    bad = score_pseudonymization(_NonDeterministic(), _DEFAULT_RECORDS, _TM_UNAUTHORIZED, secret=None)
    assert bad.referential_integrity.join_consistent is False
    assert bad.referential_integrity.broken_joins > 0


def test_fr_013_key_rotation():
    """[UNIT-TEST] For a rotating pseudonymizer: after rotation the NEW key still authorizes
    reversal (``post_rotation_authorized_reversal_succeeds is True``) AND an attacker holding
    BOTH epochs' artifacts cannot link the same entity across epochs
    (``cross_epoch_unauthorized_linkage_fails is True``)."""
    epoch_a = _ReversibleKeyedPseudonymizer(secret="keyA", salt="saltA", epoch="A")
    epoch_b = _ReversibleKeyedPseudonymizer(secret="keyB", salt="saltB", epoch="B")
    report = score_pseudonymization(
        epoch_a,
        _DEFAULT_RECORDS,
        _TM_AUTHORIZED,
        secret="keyA",
        rotated_pseudonymizer=epoch_b,
    )
    assert isinstance(report.key_rotation, KeyRotationResult)
    assert report.key_rotation.post_rotation_authorized_reversal_succeeds is True
    assert report.key_rotation.cross_epoch_unauthorized_linkage_fails is True


def test_fr_013_key_state_separation_edpb_art4_5():
    """[AUDIT] The decisive EDPB-Art-4(5) test. ``_BareMd5`` (deterministic fn of input, no
    secret) → ``rejoinable_from_artifact_alone is True`` — it CORRECTLY FAILS separation
    (re-joinable with no external secret). ``_ReversibleKeyed`` (salted) → ``False``. The
    result note MUST cite EDPB Art 4(5)."""
    bare = score_pseudonymization(_BareMd5Pseudonymizer(), _DEFAULT_RECORDS, _TM_UNAUTHORIZED, secret=None)
    assert isinstance(bare.key_state_separation, KeyStateSeparationResult)
    # The IMPORTANT finding, expressed (not hidden): keyless md5 IS re-joinable from artifact alone.
    assert bare.key_state_separation.rejoinable_from_artifact_alone is True
    assert "art" in bare.key_state_separation.note.lower()
    assert "4(5)" in bare.key_state_separation.note

    keyed = score_pseudonymization(
        _ReversibleKeyedPseudonymizer(), _DEFAULT_RECORDS, _TM_UNAUTHORIZED, secret="k3y"
    )
    assert keyed.key_state_separation.rejoinable_from_artifact_alone is False
    assert "4(5)" in keyed.key_state_separation.note


# --------------------------------------------------------------------------------------
# FR-011 — Pseudonymizer Protocol is runtime-checkable
# --------------------------------------------------------------------------------------
def test_fr_011_pseudonymizer_protocol_runtime_checkable():
    """[CONTRACT-TEST] A conforming implementation passes isinstance; an object missing a
    required member fails."""
    assert isinstance(_ReversibleKeyedPseudonymizer(), Pseudonymizer)
    assert isinstance(_BareMd5Pseudonymizer(), Pseudonymizer)

    class _MissingReverse:
        pseudonymizer_id = "broken"

        def pseudonymize(self, value: str, entity_type: str, *, context_key: str) -> str:
            return value

    assert not isinstance(_MissingReverse(), Pseudonymizer)


# --------------------------------------------------------------------------------------
# NFR-005 / AX-004 — within-module no-merge guard
# --------------------------------------------------------------------------------------
def test_nfr005_report_has_no_anonymization_or_combined_field():
    """[AUDIT] AX-004: the pseudonymization report exposes NO ``utility``/``residual_risk``/
    ``combined``/``deid``/``overall`` field or property, and ``as_dict`` carries no merged
    score. (The cross-module pairing guard is S3-08; this is the within-module guard.)"""
    report = score_pseudonymization(
        _ReversibleKeyedPseudonymizer(), _DEFAULT_RECORDS, _TM_UNAUTHORIZED, secret="k3y"
    )
    forbidden = {"utility", "residual_risk", "combined", "deid", "overall", "total_collisions"}
    for name in forbidden:
        assert not hasattr(report, name), f"report unexpectedly exposes '{name}' (AX-004 breach)"
    d = report.as_dict()
    assert forbidden.isdisjoint(d.keys()), f"as_dict leaked merged field(s): {forbidden & set(d.keys())}"


# --------------------------------------------------------------------------------------
# NFR-004 — import purity (deterministic; no RNG/clock)
# --------------------------------------------------------------------------------------
def test_fr_011_nfr004_pseudonymization_imports_no_nondeterminism():
    """[PROPERTY-TEST] AST guard: pseudonymization.py imports NONE of
    {random, time, uuid, datetime, secrets}. ``hashlib`` IS allowed — it is deterministic."""
    src = pathlib.Path(pseudo_mod.__file__).read_text(encoding="utf-8")
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
        f"pseudonymization.py imports nondeterministic modules: {sorted(banned & imported)}"
    )
    assert "hashlib" in imported  # the scorer's deterministic dictionary attack uses it
