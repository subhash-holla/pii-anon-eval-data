"""Tests for the canonical entity-type registry (fixes M1 48/65/80 drift)."""
from pii_anon_datasets import taxonomy as tx


def test_canonical_counts():
    assert tx.ENTITY_TYPE_COUNT == 63
    assert tx.CATEGORY_COUNT == 9
    assert len(tx.CANONICAL_ENTITY_TYPES) == 63
    assert len(tx.SENSITIVITY_CLASSES) == 3


def test_every_type_has_a_known_category():
    assert tx.CATEGORIES == frozenset(
        {
            "contact", "digital_online", "employment", "financial", "government_legal",
            "identity_demographics", "location_temporal", "medical_biological",
            "special_category",
        }
    )
    for t in tx.CANONICAL_ENTITY_TYPES:
        assert tx.category_of(t) in tx.CATEGORIES


def test_helpers():
    assert tx.is_known_entity_type("PERSON_NAME")
    assert not tx.is_known_entity_type("NOT_A_REAL_TYPE")
    assert tx.category_of("EMAIL_ADDRESS") == "contact"
    assert "PERSON_NAME" in tx.types_in_category("identity_demographics")


def test_category_partition_sums_to_total():
    counts = {c: len(tx.types_in_category(c)) for c in tx.CATEGORIES}
    assert sum(counts.values()) == tx.ENTITY_TYPE_COUNT
    # spot-check a few category sizes from the corpus scan
    assert counts["financial"] == 12
    assert counts["digital_online"] == 10
    assert counts["contact"] == 2
