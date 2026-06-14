"""Tests for the outbound adversary port (FR-010; DC-07; reidx-01) — S3-01 §6.

Pins: frozen value objects (Persona/Target/Guess), the runtime-checkable Adversary
Protocol, and the deterministic assemble_paired_set() over the tier3 substrate.
The LOAD-BEARING de-circularization guard proves Target.observed_signals are
RE-EXTRACTED from the anonymized text, never copied from gold.

Traceability: function names carry `fr_010` (adversary pluggability + version-pinning
port/value-objects) and `fr_007` (the paired-set the measured-attack RRS consumes);
the de-circularization guard carries `reidx01`. dc_07, ax_002 (determinism), nfr_004.
"""
import dataclasses

import pytest
from pii_anon_datasets.scoring.adversary import (
    DEFAULT_CANDIDATE_SET_SIZE,
    assemble_paired_set,
)
from pii_anon_datasets.scoring.adversary.base import (
    ADVERSARY_PORT_VERSION,
    Adversary,
    Guess,
    Persona,
    Target,
)

# ─── inline synthetic substrate (tiny, deterministic — never the full corpus) ───

def _bs(**cats: dict) -> dict:
    """Build a behavioral_signals block, defaulting absent categories to none."""
    block: dict = {}
    for cat in (
        "writing_style",
        "professional_domain",
        "interest_topics",
        "temporal_patterns",
        "location_signals",
        "personal_anecdote",
    ):
        block[cat] = cats.get(cat, {"present": False, "uniqueness": "none", "indicators": []})
    block["behavioral_signal_density"] = 0.0
    block["reidentification_contribution"] = "low"
    return block


def _record(rid: str, text: str, *, signals_block: dict, pseudonymized: str,
            annotations: list | None = None) -> dict:
    return {
        "record_id": rid,
        "text": text,
        "annotations": annotations
        or [{"entity_type": "PERSON_NAME", "start": 0, "end": 4, "text": text[:4]}],
        "tier3_evaluation": {"behavioral_signals": signals_block},
        "context_preservation": {
            "anonymized_pseudonymized": pseudonymized,
            "anonymized_masked": "[PERSON_NAME] ...",
        },
    }


def _basic_records() -> list[dict]:
    return [
        _record(
            "ccc-3",
            "Carla writes about fitness and her PR.",
            signals_block=_bs(),
            pseudonymized="Dana writes about fitness and her PR.",
            annotations=[{"entity_type": "PERSON_NAME", "start": 0, "end": 5, "text": "Carla"}],
        ),
        _record(
            "aaa-1",
            "Alice the attending physician.",
            signals_block=_bs(),
            pseudonymized="Robin the attending physician.",
            annotations=[
                {"entity_type": "PERSON_NAME", "start": 0, "end": 5, "text": "Alice"},
                {"entity_type": "JOB_TITLE", "start": 10, "end": 29, "text": "attending physician"},
            ],
        ),
        _record(
            "bbb-2",
            "Bob in Boston.",
            signals_block=_bs(),
            pseudonymized="Sam in Boston.",
            annotations=[{"entity_type": "PERSON_NAME", "start": 0, "end": 3, "text": "Bob"}],
        ),
    ]


# 3. ::test_fr_010_adversary_protocol_is_runtime_checkable  [CONTRACT-TEST]
class _GoodAdversary:
    adversary_id = "offline-deterministic-v1"
    deterministic = True

    def attack(self, targets, candidates, candidate_set_size):  # noqa: D401, ANN001
        return []


class _MissingAttack:
    adversary_id = "x"
    deterministic = True


class _MissingId:
    deterministic = True

    def attack(self, targets, candidates, candidate_set_size):  # noqa: ANN001
        return []


# 1. ::test_fr_010_persona_target_guess_are_frozen  [UNIT-TEST]
def test_fr_010_persona_target_guess_are_frozen():
    p = Persona(persona_id="p1", record_id="p1", quasi_identifiers=(("PERSON_NAME", "Alice"),),
                behavioral_signals={}, source_text="x")
    t = Target(target_id="p1", anonymized_text="y", observed_signals={})
    g = Guess(target_id="p1", guessed_persona_id="p1", score=0.5)
    for obj, field in ((p, "persona_id"), (t, "target_id"), (g, "score")):
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(obj, field, "mutated")
    assert dataclasses.is_dataclass(p) and dataclasses.is_dataclass(t) and dataclasses.is_dataclass(g)
    assert ADVERSARY_PORT_VERSION == "adversary-port-v1"


# 2. ::test_fr_010_guess_abstain_is_none_not_wrong  [UNIT-TEST]
def test_fr_010_guess_abstain_is_none_not_wrong():
    abstain = Guess(target_id="t1", guessed_persona_id=None, score=0.0)
    wrong = Guess(target_id="t1", guessed_persona_id="someone_else", score=0.9)
    assert abstain.guessed_persona_id is None          # abstention sentinel
    assert wrong.guessed_persona_id is not None         # a (wrong) commitment
    assert abstain != wrong


# 3.
def test_fr_010_adversary_protocol_is_runtime_checkable():
    assert isinstance(_GoodAdversary(), Adversary)      # has all three members
    assert not isinstance(_MissingAttack(), Adversary)  # missing attack()
    assert not isinstance(_MissingId(), Adversary)      # missing adversary_id


# 4. ::test_fr_007_assemble_paired_set_deterministic  [PROPERTY-TEST]
def test_fr_007_assemble_paired_set_deterministic():
    recs = _basic_records()
    t1, c1 = assemble_paired_set(recs, candidate_set_size=10)
    t2, c2 = assemble_paired_set(recs, candidate_set_size=10)
    assert [x.target_id for x in t1] == [x.target_id for x in t2]
    assert [x.persona_id for x in c1] == [x.persona_id for x in c2]
    # sort-based: order is by record_id ascending, NOT input order
    assert [c.record_id for c in c1] == ["aaa-1", "bbb-2", "ccc-3"]
    assert [t.target_id for t in t1] == ["aaa-1", "bbb-2", "ccc-3"]
    # ground-truth link: target_id == persona_id of its true source
    assert {t.target_id for t in t1} == {c.persona_id for c in c1}


# 5. ::test_fr_007_assemble_filters_to_tier3_substrate  [UNIT-TEST]
def test_fr_007_assemble_filters_to_tier3_substrate():
    good = _basic_records()[0]
    no_signals = {
        "record_id": "no-sig",
        "text": "t",
        "annotations": [],
        "tier3_evaluation": {},                       # missing behavioral_signals
        "context_preservation": {"anonymized_pseudonymized": "t"},
    }
    no_cp = {
        "record_id": "no-cp",
        "text": "t",
        "annotations": [],
        "tier3_evaluation": {"behavioral_signals": _bs()},
        "context_preservation": None,                 # missing context_preservation
    }
    neither = {"record_id": "neither", "text": "t", "annotations": []}
    targets, candidates = assemble_paired_set([good, no_signals, no_cp, neither], candidate_set_size=10)
    ids = {c.record_id for c in candidates}
    assert ids == {"ccc-3"}                            # only the fully-substrated record survives
    assert len(targets) == 1
    # all-empty input → empty sets, no error
    assert assemble_paired_set([], candidate_set_size=10) == ([], [])


# 6. ::test_fr_007_candidate_set_size_is_first_class  [UNIT-TEST]
def test_fr_007_candidate_set_size_is_first_class():
    assert DEFAULT_CANDIDATE_SET_SIZE == 2500
    recs = _basic_records()                            # 3 substrated records
    _, c_small = assemble_paired_set(recs, candidate_set_size=2)
    assert len(c_small) == 2                            # |C| honored when < n_available
    _, c_big = assemble_paired_set(recs, candidate_set_size=100)
    assert len(c_big) == 3                              # capped at n_available
    # |C| takes the deterministically-FIRST records (sorted by record_id)
    assert [c.record_id for c in c_small] == ["aaa-1", "bbb-2"]


# 7. ::test_fr_007_reidx01_observed_signals_reextracted_not_gold  (de-circularization, LOAD-BEARING)
def test_fr_007_reidx_01_observed_signals_reextracted_not_gold():
    # GOLD claims a very_high location signal (Boston "the T" / "Beacon Hill" present);
    # the pseudonymized variant STRIPS those local references entirely.
    gold = _bs(
        location_signals={
            "present": True,
            "uniqueness": "very_high",
            "indicators": ["local_reference:boston:the_t", "local_reference:boston:beacon_hill"],
        }
    )
    rec = _record(
        "reidx-1",
        "My commute on the T into Beacon Hill is brutal.",
        signals_block=gold,
        # behavioral signal stripped: no local references remain in the anonymized text
        pseudonymized="My commute downtown is brutal.",
    )
    targets, candidates = assemble_paired_set([rec], candidate_set_size=10)
    assert len(targets) == 1 and len(candidates) == 1
    target, persona = targets[0], candidates[0]

    # the gold (Persona) STILL carries the very_high location signal …
    assert persona.behavioral_signals["location_signals"]["uniqueness"] == "very_high"
    # … but the Target's observed signals were RE-EXTRACTED from the stripped text,
    # so the location signal is gone — they MUST differ (reidx-01).
    assert target.observed_signals != persona.behavioral_signals
    assert target.observed_signals["location_signals"]["present"] is False
    # and the link is preserved
    assert target.target_id == persona.persona_id == "reidx-1"
