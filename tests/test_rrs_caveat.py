"""Tests for the non-strippable anti-anonymity caveat (FR-009 / gov-01).

The caveat must travel with the RRS NUMBER through any serializer — making it
structurally impossible to emit an RRS figure stripped of its caveat.
"""
import dataclasses

import pytest

from pii_anon_datasets.scoring.reidentification import ANTI_ANONYMITY_CAVEAT, RRSResult


def test_cannot_construct_without_caveat():
    # caveat is a mandatory, non-defaulted field → omitting it is a TypeError
    with pytest.raises(TypeError):
        RRSResult(  # type: ignore[call-arg]
            rrs=0.7,
            reid_recall=0.3,
            reid_precision=0.9,
            candidate_set_size=2500,
            adversary_id="offline-deterministic-v1",
            deterministic=True,
        )


def test_empty_caveat_rejected():
    with pytest.raises(ValueError):
        RRSResult(
            rrs=0.7,
            reid_recall=0.3,
            reid_precision=0.9,
            candidate_set_size=2500,
            adversary_id="offline-deterministic-v1",
            deterministic=True,
            caveat="   ",
        )


def test_from_attack_computes_rrs_and_sets_caveat():
    r = RRSResult.from_attack(
        reid_recall=0.3,
        reid_precision=0.9,
        candidate_set_size=2500,
        adversary_id="offline-deterministic-v1",
        deterministic=True,
    )
    assert r.rrs == pytest.approx(1.0 - 0.3 * 0.9)
    assert r.caveat == ANTI_ANONYMITY_CAVEAT
    assert r.deterministic is True
    assert r.candidate_set_size == 2500


def test_caveat_survives_serialization_gov01():
    r = RRSResult.from_attack(0.3, 0.9, 2500, "offline-deterministic-v1", True)
    d = r.as_dict()
    assert "caveat" in d
    assert "MUST NOT be cited" in d["caveat"]
    # every public field of the value object is serialized — none silently dropped
    field_names = {f.name for f in dataclasses.fields(r)}
    assert field_names.issubset(set(d.keys()))


def test_candidate_set_size_is_first_class():
    # |C| must be present (closed-world recall != open-world)
    r = RRSResult.from_attack(0.3, 0.9, 500, "claude@2026-05", False)
    assert r.as_dict()["candidate_set_size"] == 500
    assert r.deterministic is False  # LLM adversary is the SECONDARY, version-stamped figure
