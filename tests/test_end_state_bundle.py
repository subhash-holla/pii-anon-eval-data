"""S5-06 — DPIA-input end-state evidence bundle (DC-11; FR-021, supporting NFR-005/AX-004).

Tokened ``fr_021`` / ``nfr_005`` / ``nfr004`` so the traceability gate can map test->requirement
and ``pytest -k`` selects them. The bundle assembles a Data-Protection-Impact-Assessment INPUT for a
transformation's output, keeping the **anonymization** evidence (DC-06 ``ParetoPoint``:
residual-risk ``MeasuredRRS`` + ``UtilityScore``) and the **pseudonymization** evidence
(DC-08 ``PseudonymizationReport``: integrity) as **two SEPARATE sub-objects** -- DELIBERATELY no
merged/combined de-id verdict, no ``__float__`` (NFR-005 / AX-004). It surfaces the per-record
regulatory crosswalk (S5-01) and carries a **non-strippable** "informs, does not make, a
determination" disclaimer.

Construction discipline (§6): REUSE the ``ParetoPoint`` / ``PseudonymizationReport`` construction
patterns from ``tests/test_anonymization.py`` + ``tests/test_pseudonymization.py`` to compose minimal
REAL scorer outputs into the bundle for tests #1/#6 -- the scorers are NOT re-tested here.
Deterministic; pure-stdlib.
"""

from __future__ import annotations

import ast
import hashlib
import pathlib
from collections.abc import Sequence

import pytest
from pii_anon_datasets.compliance import end_state_bundle as bundle_mod
from pii_anon_datasets.compliance.end_state_bundle import (
    DPIA_DISCLAIMER,
    EndStateBundle,
    assemble_end_state_bundle,
)
from pii_anon_datasets.scoring.adversary.base import Guess, Persona, Target
from pii_anon_datasets.scoring.anonymization import ParetoPoint, score_anonymization
from pii_anon_datasets.scoring.pseudonymization import (
    AttackerCapability,
    PseudonymizationReport,
    ThreatModel,
    score_pseudonymization,
)
from pii_anon_datasets.scoring.signals import extract


# --------------------------------------------------------------------------------------
# Minimal REAL scorer outputs (reused construction patterns -- the scorers are NOT re-tested)
# --------------------------------------------------------------------------------------
class _StubAdversary:
    """Scripted adversary returning a fixed guesses list verbatim (from test_anonymization)."""

    def __init__(self, guesses: list[Guess], *, adversary_id: str = "stub-adversary-v0") -> None:
        self._guesses = guesses
        self.adversary_id = adversary_id
        self.deterministic = True

    def attack(self, targets: Sequence[Target], candidates: Sequence[Persona], candidate_set_size: int) -> list[Guess]:
        return list(self._guesses)


_ORIGINAL = (
    "Jane Doe lives at 42 Beacon Street in Boston and her account number is 1234. "
    "She called the clinic about her prognosis on Tuesday."
)
_REDACTED = (
    "[NAME] lives at [ADDRESS] in [CITY] and her account number is [ACCT]. "
    "She called the clinic about her prognosis on [DAY]."
)


def _make_pareto_point() -> ParetoPoint:
    """A minimal real ``ParetoPoint`` (DC-06): privacy ``MeasuredRRS`` + utility ``UtilityScore``."""
    targets = [
        Target(target_id="t1", anonymized_text="", observed_signals=extract("")),
        Target(target_id="t2", anonymized_text="", observed_signals=extract("")),
    ]
    return score_anonymization(
        _StubAdversary(
            [
                Guess(target_id="t1", guessed_persona_id="t1", score=0.9),
                Guess(target_id="t2", guessed_persona_id="t2", score=0.9),
            ]
        ),
        targets,
        [],
        candidate_set_size=10,
        original_text=_ORIGINAL,
        anonymized_text=_REDACTED,
        variant="anonymized_redacted",
    )


class _BareMd5Pseudonymizer:
    """Keyless md5 pseudonymizer (from test_pseudonymization) -- fails EDPB Art 4(5) separation."""

    pseudonymizer_id = "bare-md5"

    def pseudonymize(self, value: str, entity_type: str, *, context_key: str) -> str:
        return "MD5_" + hashlib.md5(value.encode("utf-8")).hexdigest()[:12]

    def reverse(self, pseudonym: str, entity_type: str, *, secret: object) -> str | None:
        return None


_PSEUDO_RECORDS = [
    {"value": "Alice", "entity_type": "PERSON_NAME"},
    {"value": "Bob", "entity_type": "PERSON_NAME"},
    {"value": "Alice", "entity_type": "PERSON_NAME"},  # repeat -> intended linkage collision
    {"value": "Carol", "entity_type": "PERSON_NAME"},
]
_TM = ThreatModel(
    capabilities=(AttackerCapability.ARTIFACT_ONLY, AttackerCapability.ARTIFACT_PLUS_AUX),
    model_id="pseudo-threat-v1",
)


def _make_pseudo_report() -> PseudonymizationReport:
    """A minimal real ``PseudonymizationReport`` (DC-08). The bare-md5 scheme makes the
    EDPB Art 4(5) note the 'rejoinable-from-artifact-alone' variant, so the 4(5) citation travels."""
    return score_pseudonymization(_BareMd5Pseudonymizer(), _PSEUDO_RECORDS, _TM, secret=None)


def _record(*domains: str) -> dict[str, object]:
    """A record carrying ``regulatory_domains`` tags (the crosswalk's input surface, S5-01)."""
    return {"regulatory_domains": list(domains)}


# --------------------------------------------------------------------------------------
# 1. [UNIT-TEST] the two evidence axes are SEPARATE keys; no combined/total_collisions
# --------------------------------------------------------------------------------------
def test_fr_021_bundle_separates_anon_and_pseudo():
    """``EndStateBundle.as_dict()`` has the two SEPARATE keys ``anonymization_evidence`` +
    ``pseudonymization_evidence``; the anon sub-object nests ``privacy`` + ``utility`` (no
    ``combined``), the pseudo sub-object nests the integrity fields (no ``total_collisions``)."""
    bundle = assemble_end_state_bundle(
        _record("hipaa"),
        anonymization=_make_pareto_point(),
        pseudonymization=_make_pseudo_report(),
    )
    d = bundle.as_dict()
    # two SEPARATE evidence keys (plus the crosswalk + disclaimer); NO merged key
    assert "anonymization_evidence" in d and "pseudonymization_evidence" in d
    assert d["anonymization_evidence"] is not d["pseudonymization_evidence"]
    for forbidden in ("combined", "overall", "overall_score", "deid", "de_identification_score", "score"):
        assert forbidden not in d, f"as_dict leaked merged key '{forbidden}'"
    # anon sub-object: the two Pareto axes kept separate (privacy + utility), no combined
    anon = d["anonymization_evidence"]
    assert isinstance(anon, dict)
    assert "privacy" in anon and "utility" in anon
    assert "combined" not in anon
    # pseudo sub-object: integrity fields, the two collision integers kept SEPARATE (never summed)
    pseudo = d["pseudonymization_evidence"]
    assert isinstance(pseudo, dict)
    assert "intended_linkage_collisions" in pseudo and "unintended_crypto_collisions" in pseudo
    assert "total_collisions" not in pseudo


# --------------------------------------------------------------------------------------
# 2. [AUDIT] NFR-005 / AX-004: NO merged-verdict name anywhere; no __float__; source grep clean
# --------------------------------------------------------------------------------------
def test_nfr_005_bundle_has_no_merged_verdict():
    """``EndStateBundle`` exposes NO attribute/field named ``combined`` / ``overall`` /
    ``overall_score`` / ``deid`` / ``de_identification_score`` / ``score``, and NO ``__float__``
    (``float(bundle)`` raises ``TypeError``); a source grep of ``end_state_bundle.py`` finds no
    merged-verdict symbol."""
    bundle = assemble_end_state_bundle(_record("gdpr"), anonymization=_make_pareto_point())
    forbidden = {"combined", "overall", "overall_score", "deid", "de_identification_score", "score"}
    # (A) introspection: no forbidden attribute/property on instance or class
    for name in forbidden:
        assert not hasattr(bundle, name), f"EndStateBundle must not expose merged metric '{name}'"
        assert not hasattr(EndStateBundle, name), f"EndStateBundle class must not define '{name}'"
    # no __float__ -> the bundle cannot collapse to a single de-id number
    assert not hasattr(bundle, "__float__")
    with pytest.raises(TypeError):
        float(bundle)  # type: ignore[arg-type]
    # (B) as_dict() leaks no merged key
    assert forbidden.isdisjoint(bundle.as_dict().keys())
    # (C) source grep: end_state_bundle.py defines none of the forbidden names as a merged metric
    src = pathlib.Path(bundle_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    defined: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined.add(node.name)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            defined.add(node.target.id)
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    defined.add(tgt.id)
    leaked = forbidden & defined
    assert not leaked, f"end_state_bundle.py defines forbidden merged-metric name(s): {sorted(leaked)}"


# --------------------------------------------------------------------------------------
# 3. [UNIT-TEST] FR-021: the DPIA disclaimer is mandatory + validated (non-strippable)
# --------------------------------------------------------------------------------------
def test_fr_021_disclaimer_is_non_strippable():
    """``disclaimer`` is mandatory + validated: ``__post_init__`` raises ``ValueError`` on an
    empty/whitespace disclaimer; ``DPIA_DISCLAIMER`` contains 'input' + 'inform' +
    ('does not make' / 'not make'+'determination') + 'determination'."""
    point = _make_pareto_point()
    crosswalk = assemble_end_state_bundle(_record("gdpr"), anonymization=point).regulatory_crosswalk
    # an empty / whitespace disclaimer is rejected at construction
    with pytest.raises(ValueError):
        EndStateBundle(regulatory_crosswalk=crosswalk, anonymization_evidence=point, disclaimer="")
    with pytest.raises(ValueError):
        EndStateBundle(regulatory_crosswalk=crosswalk, anonymization_evidence=point, disclaimer="   ")
    # the canonical disclaimer carries the "input -> informs -> does NOT MAKE a determination" language
    low = DPIA_DISCLAIMER.lower()
    assert "input" in low
    assert "inform" in low
    assert "does not make" in low or ("not make" in low and "determination" in low)
    assert "determination" in low
    # and it travels onto the assembled bundle's as_dict() unstripped
    assert assemble_end_state_bundle(_record(), anonymization=point).as_dict()["disclaimer"] == DPIA_DISCLAIMER


# --------------------------------------------------------------------------------------
# 4. [UNIT-TEST] FR-021: at least one evidence axis is required
# --------------------------------------------------------------------------------------
def test_fr_021_bundle_requires_at_least_one_axis():
    """Constructing ``EndStateBundle`` with BOTH evidence axes ``None`` raises ``ValueError``
    (a bundle with no evidence is meaningless)."""
    crosswalk = assemble_end_state_bundle(_record("gdpr"), anonymization=_make_pareto_point()).regulatory_crosswalk
    with pytest.raises(ValueError):
        EndStateBundle(
            regulatory_crosswalk=crosswalk,
            anonymization_evidence=None,
            pseudonymization_evidence=None,
        )
    # but a single axis is sufficient (no raise)
    assert (
        EndStateBundle(
            regulatory_crosswalk=crosswalk, anonymization_evidence=_make_pareto_point()
        ).anonymization_evidence
        is not None
    )


# --------------------------------------------------------------------------------------
# 5. [INTEGRATION-TEST] FR-021: the per-record S5-01 regulatory crosswalk is surfaced
# --------------------------------------------------------------------------------------
def test_fr_021_bundle_surfaces_regulatory_crosswalk():
    """``assemble_end_state_bundle(record, ...)`` derives the ``RegulatoryCrosswalk`` from the
    record's ``regulatory_domains`` tags (S5-01); a record tagged ``hipaa`` -> BOTH
    ``reg_hipaa_safe_harbor`` and ``reg_hipaa_expert_determination`` IN_SCOPE in the crosswalk."""
    bundle = assemble_end_state_bundle(_record("hipaa"), anonymization=_make_pareto_point())
    xwalk = bundle.as_dict()["regulatory_crosswalk"]
    assert isinstance(xwalk, dict)
    # hipaa fans out to BOTH legally-distinct HIPAA de-identification methods, both IN_SCOPE
    assert xwalk["hipaa_safe_harbor"] == "in_scope"
    assert xwalk["hipaa_expert_determination"] == "in_scope"
    # a regime with no mapping tag stays OUT_OF_SCOPE (a signal, not a determination)
    assert xwalk["gdpr"] == "out_of_scope_of_dataset"


# --------------------------------------------------------------------------------------
# 6. [INTEGRATION-TEST] FR-021: the FR-009 + EDPB Art 4(5) caveats travel with each axis
# --------------------------------------------------------------------------------------
def test_fr_021_caveats_travel_with_each_axis():
    """With a real ``ParetoPoint`` + ``PseudonymizationReport`` composed into the bundle,
    ``as_dict()`` carries the FR-009 anti-anonymity caveat inside ``anonymization_evidence`` (the
    nested ``MeasuredRRS`` caveat) AND the EDPB Art 4(5) note inside ``pseudonymization_evidence``
    -- the caveats are never stripped on assembly."""
    bundle = assemble_end_state_bundle(
        _record("hipaa"),
        anonymization=_make_pareto_point(),
        pseudonymization=_make_pseudo_report(),
    )
    d = bundle.as_dict()
    # FR-009 anti-anonymity caveat -> anonymization_evidence -> privacy -> rrs -> caveat
    anon_caveat = d["anonymization_evidence"]["privacy"]["rrs"]["caveat"]
    assert "MUST NOT be cited" in anon_caveat
    # EDPB Art 4(5) note -> pseudonymization_evidence -> key_state_separation -> note
    pseudo_note = d["pseudonymization_evidence"]["key_state_separation"]["note"]
    assert "4(5)" in pseudo_note
    assert "art" in pseudo_note.lower()


# --------------------------------------------------------------------------------------
# 7. [PROPERTY-TEST] NFR-004 / AX-002: pure-stdlib, deterministic (no clock/RNG)
# --------------------------------------------------------------------------------------
def test_nfr004_end_state_bundle_pure_stdlib():
    """AST guard: ``end_state_bundle.py`` imports none of {random, time, uuid, datetime, secrets}
    (pure-stdlib, deterministic)."""
    src = pathlib.Path(bundle_mod.__file__).read_text(encoding="utf-8")
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
        f"end_state_bundle.py imports nondeterministic modules: {sorted(banned & imported)}"
    )
