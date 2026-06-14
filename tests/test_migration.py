"""Tests for v1.3.0 → v2.0.0 migration (DC-02; AX-002 determinism; DX-01 back-compat)."""
import pytest

from pii_anon_datasets.compat import to_v1_record
from pii_anon_datasets.migration import (
    SCHEMA_VERSION,
    deterministic_record_id,
    migrate_record,
    unknown_entity_types,
)


def _v13_record(rid="old-uuid-1"):
    """A representative v1.3.0 record (tier3 signal scattered, as on disk)."""
    return {
        "record_id": rid,
        "text": "Patient Jane Doe, MRN 12345.",
        "version": "1.3.0",
        "annotations": [
            {"entity_type": "PERSON_NAME", "start": 8, "end": 16, "text": "Jane Doe"},
            {"entity_type": "MEDICAL_RECORD_NUMBER", "start": 22, "end": 27, "text": "12345"},
        ],
        "language": "en",
        "domain": "clinical",
        "primary_dimension": "diverse_pii_types",
        "behavioral_signals": {"writing_style": {"present": True}, "behavioral_signal_density": 0.4},
        "privacy_risk": {
            "quasi_identifiers": ["AGE"],
            "reidentification_risk": "low",
            "k_anonymity_estimate": 100,
            "re_identification_resistance_score": 0.78,
            "estimated_reid_recall": 0.12,
            "tier3_risk_level": "low",
        },
        "provenance": {"source_type": "synthetic", "license": "CC0-1.0"},
    }


def test_deterministic_record_id_stable_and_order_independent():
    text = "hello"
    anns = [
        {"start": 0, "end": 5, "entity_type": "A"},
        {"start": 10, "end": 12, "entity_type": "B"},
    ]
    a = deterministic_record_id(text, anns)
    b = deterministic_record_id(text, list(reversed(anns)))  # order must not matter
    assert a == b
    assert a == deterministic_record_id(text, anns)  # stable across calls (AX-002)
    assert deterministic_record_id("other", anns) != a  # content-sensitive


def test_tier3_consolidation_and_field_moves():
    out = migrate_record(_v13_record())
    t3 = out["tier3_evaluation"]
    # RRS + estimated_reid_recall + tier3_risk_level moved out of privacy_risk
    assert t3["re_identification_resistance_score"] == 0.78
    assert t3["estimated_reid_recall"] == 0.12
    assert t3["tier3_risk_level"] == "low"
    assert "re_identification_resistance_score" not in out["privacy_risk"]
    # behavioral_signals moved off the top level
    assert "behavioral_signals" not in out
    assert out["tier3_evaluation"]["behavioral_signals"]["behavioral_signal_density"] == 0.4
    # privacy_risk keeps its non-tier3 fields
    assert out["privacy_risk"]["k_anonymity_estimate"] == 100
    # version + lineage
    assert out["schema_version"] == SCHEMA_VERSION == "2.0.0"
    assert out["version"] == "2.0.0"
    assert out["provenance"]["v1_3_0_record_id"] == "old-uuid-1"


def test_existing_tier3_evaluation_not_clobbered():
    rec = _v13_record()
    rec["tier3_evaluation"] = {"is_paired_profile": True, "persona_id": "persona_00042",
                               "re_identification_resistance_score": 0.99}
    out = migrate_record(rec)
    # existing wrapper keys preserved; existing RRS NOT overwritten by privacy_risk value
    assert out["tier3_evaluation"]["is_paired_profile"] is True
    assert out["tier3_evaluation"]["persona_id"] == "persona_00042"
    assert out["tier3_evaluation"]["re_identification_resistance_score"] == 0.99


def test_migration_is_deterministic():
    r1 = migrate_record(_v13_record())
    r2 = migrate_record(_v13_record())
    assert r1 == r2  # byte-identical transform (AX-002)


def test_no_unknown_entity_types_on_valid_record():
    assert unknown_entity_types(_v13_record()) == set()
    bad = _v13_record()
    bad["annotations"].append({"entity_type": "FAKE_TYPE", "start": 0, "end": 1})
    assert unknown_entity_types(bad) == {"FAKE_TYPE"}


def test_round_trip_back_compat_dx01():
    original = _v13_record()
    restored = to_v1_record(migrate_record(original))
    # flat shape restored for legacy consumers
    assert restored["behavioral_signals"]["behavioral_signal_density"] == 0.4
    assert restored["privacy_risk"]["re_identification_resistance_score"] == 0.78
    assert restored["privacy_risk"]["tier3_risk_level"] == "low"
    assert restored["record_id"] == "old-uuid-1"  # original id restored from provenance
    assert "tier3_evaluation" not in restored  # wrapper removed (record had none in v1.3.0)
