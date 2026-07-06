"""Tests for scripts/normalize_sensitivity.py — normalize_record transform.

Unit-tests the pure per-record transform (no file I/O).  Covers:
- ETHNICITY annotation corrected from quasi_identifier → sensitive_attribute
- Unknown entity_type left unchanged (never invented)
- Unrelated annotations within the same record are untouched
- SENSITIVITY_MAP import check: ETHNICITY == "sensitive_attribute"
"""
from __future__ import annotations

import copy
import pathlib
import sys

# Make scripts/ importable so migrate_v1_to_v2 and normalize_sensitivity resolve
_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from migrate_v1_to_v2 import SENSITIVITY_MAP  # noqa: E402
from normalize_sensitivity import normalize_record  # noqa: E402

# ─── Sanity-check: SENSITIVITY_MAP has the Task-6 fix ────────────────────────


def test_sensitivity_map_ethnicity_is_sensitive_attribute():
    """SENSITIVITY_MAP["ETHNICITY"] must be "sensitive_attribute" (Task 6 fix)."""
    assert SENSITIVITY_MAP["ETHNICITY"] == "sensitive_attribute"


def test_sensitivity_map_has_expected_entries():
    """SENSITIVITY_MAP is a non-trivial complete dict of entity_type → sensitivity_class."""
    assert len(SENSITIVITY_MAP) >= 60, (
        f"Expected ≥60 entries in SENSITIVITY_MAP, got {len(SENSITIVITY_MAP)}"
    )
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in SENSITIVITY_MAP.items())


# ─── normalize_record: ETHNICITY correction ──────────────────────────────────


def _make_record(**overrides) -> dict:
    base: dict = {
        "record_id": "test-001",
        "text": "Her ethnicity is listed as Asian.",
        "annotations": [
            {
                "entity_id": "e0",
                "entity_type": "ETHNICITY",
                "start": 4,
                "end": 13,
                "text": "ethnicity",
                "category": "identity_demographics",
                "sensitivity_class": "quasi_identifier",  # old (wrong) value
                "cluster_id": None,
                "mention_variant": None,
            }
        ],
    }
    base.update(overrides)
    return base


def test_ethnicity_corrected_from_quasi_to_sensitive_attribute():
    """An ETHNICITY annotation with quasi_identifier must become sensitive_attribute."""
    rec = _make_record()
    result = normalize_record(rec)
    assert result["annotations"][0]["sensitivity_class"] == "sensitive_attribute"


def test_normalize_record_mutates_in_place():
    """normalize_record returns the same dict object it received."""
    rec = _make_record()
    returned = normalize_record(rec)
    assert returned is rec


# ─── Unknown entity_type left unchanged ──────────────────────────────────────


def test_unknown_entity_type_left_unchanged():
    """An annotation whose entity_type is absent from SENSITIVITY_MAP must not be altered."""
    rec: dict = {
        "record_id": "test-002",
        "text": "Some text.",
        "annotations": [
            {
                "entity_id": "e0",
                "entity_type": "TOTALLY_CUSTOM_TYPE",
                "start": 0,
                "end": 4,
                "text": "Some",
                "sensitivity_class": "direct_identifier",  # must remain
                "cluster_id": None,
                "mention_variant": None,
            }
        ],
    }
    assert "TOTALLY_CUSTOM_TYPE" not in SENSITIVITY_MAP, (
        "Test assumption violated: TOTALLY_CUSTOM_TYPE must not be in SENSITIVITY_MAP"
    )
    normalize_record(rec)
    assert rec["annotations"][0]["sensitivity_class"] == "direct_identifier"


# ─── Multi-annotation record: only the mapped ones change ────────────────────


def test_mixed_record_only_mapped_annotations_change():
    """In a multi-annotation record, mapped types are corrected; unmapped types are preserved."""
    rec: dict = {
        "record_id": "test-003",
        "text": "Alice's ethnicity is listed; UNKNOWN_TYPE kept.",
        "annotations": [
            {
                "entity_id": "e0",
                "entity_type": "ETHNICITY",
                "start": 0,
                "end": 7,
                "text": "Alice's",
                "sensitivity_class": "quasi_identifier",  # should change
                "cluster_id": None,
                "mention_variant": None,
            },
            {
                "entity_id": "e1",
                "entity_type": "PERSON_NAME",
                "start": 0,
                "end": 5,
                "text": "Alice",
                "sensitivity_class": "direct_identifier",  # correct already, must stay
                "cluster_id": None,
                "mention_variant": None,
            },
            {
                "entity_id": "e2",
                "entity_type": "UNKNOWN_CUSTOM",
                "start": 30,
                "end": 42,
                "text": "UNKNOWN_TYPE",
                "sensitivity_class": "quasi_identifier",  # unmapped; must stay
                "cluster_id": None,
                "mention_variant": None,
            },
        ],
    }
    original = copy.deepcopy(rec)
    normalize_record(rec)

    # ETHNICITY corrected
    assert rec["annotations"][0]["sensitivity_class"] == "sensitive_attribute"
    # PERSON_NAME stays direct_identifier (already correct per the map)
    assert rec["annotations"][1]["sensitivity_class"] == "direct_identifier"
    # UNKNOWN_CUSTOM untouched
    assert rec["annotations"][2]["sensitivity_class"] == original["annotations"][2]["sensitivity_class"]


# ─── Record with no annotations is safe ──────────────────────────────────────


def test_record_with_no_annotations_is_safe():
    """normalize_record must not raise on a record that has no annotations key."""
    rec: dict = {"record_id": "test-004", "text": "No PII here."}
    normalize_record(rec)  # must not raise
    assert "annotations" not in rec


def test_record_with_empty_annotations_is_safe():
    """normalize_record must not raise on a record with an empty annotations list."""
    rec: dict = {"record_id": "test-005", "text": "No PII here.", "annotations": []}
    normalize_record(rec)
    assert rec["annotations"] == []
