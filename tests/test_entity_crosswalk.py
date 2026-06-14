"""Tests for compliance.entity_crosswalk (FR-053 / DC-30: per-entity-type regulatory crosswalk).

C5 — extends the cycle-1 record-tag crosswalk (S5-01 / FR-022) DOWN to the per-ENTITY-TYPE
level and ADDS GLBA. Each of the canonical 63 entity types (``taxonomy.ENTITY_REGISTRY``) maps
to a record carrying FIVE SEPARATE, legally-distinct regime fields — and NO merged verdict.

LOAD-BEARING (FR-053 / DC-30, mirroring AX-004 separation + gov-02 stance):
* EVERY one of the 63 taxonomy types has an entry (derived from taxonomy, never a stale list);
* each entry exposes EXACTLY the 5 legally-distinct keys (``gdpr``,
  ``gdpr_art9_special_category``, ``hipaa_phi``, ``ccpa``, ``glba_nonpublic_personal_info``);
* there is NO merged / roll-up verdict key (no ``overall`` / ``deidentified`` / ``compliant`` /
  ``equivalent`` / ``regime``) — regimes are legally distinct, no cross-regime equivalence;
* the crosswalk is VERSIONED + provenance-stamped with an INJECTABLE ``generated_at`` so the
  build is byte-reproducible (AX-002);
* the disclaimer is NON-STRIPPABLE — the carrier dataclass raises on an empty disclaimer
  (mirrors ``scoring.detection.DesignProvenance`` / ``assessment.manifest.ASSESSMENT_CAVEAT``);
* at least one GDPR Art-9 special-category type is flagged True and at least one GLBA
  nonpublic-personal-info type is flagged in-scope.
"""
import json

import pytest
from pii_anon_datasets.compliance import entity_crosswalk as ecx
from pii_anon_datasets.compliance.entity_crosswalk import (
    CROSSWALK_DISCLAIMER,
    ENTITY_REGULATORY_CROSSWALK_VERSION,
    REGIME_KEYS,
    build_entity_crosswalk,
)
from pii_anon_datasets.taxonomy import CANONICAL_ENTITY_TYPES, ENTITY_TYPE_COUNT

# The 5 legally-distinct, independently-addressable regime keys (FR-053 / DC-30).
EXPECTED_REGIME_KEYS = (
    "gdpr",
    "gdpr_art9_special_category",
    "hipaa_phi",
    "ccpa",
    "glba_nonpublic_personal_info",
)

# Anything resembling a merged / roll-up cross-regime verdict is FORBIDDEN (legally distinct).
_FORBIDDEN_MERGED_KEYS = frozenset(
    {"overall", "deidentified", "compliant", "equivalent", "regime", "verdict", "merged"}
)


def test_fr_053_covers_every_one_of_the_63_taxonomy_types() -> None:
    """``build_entity_crosswalk`` has an entry for EXACTLY the canonical 63 types — [UNIT-TEST].

    Derived from ``taxonomy`` (no stale hand-list): the entry keyset equals the canonical set,
    so the crosswalk can never silently drift out of sync with the registry (DC-30).
    """
    xwalk = build_entity_crosswalk()
    entries = xwalk["entries"]
    assert set(entries) == set(CANONICAL_ENTITY_TYPES)
    assert len(entries) == ENTITY_TYPE_COUNT == 63


def test_fr_053_each_entry_has_the_five_legally_distinct_keys_and_no_merged_verdict() -> None:
    """Every entry exposes EXACTLY the 5 separate regime keys, NO merged verdict — [UNIT-TEST].

    AX-004 separation / gov-02 stance: regimes are legally distinct, never collapsed into an
    ``overall`` / ``deidentified`` roll-up.
    """
    xwalk = build_entity_crosswalk()
    assert REGIME_KEYS == EXPECTED_REGIME_KEYS
    for etype, entry in xwalk["entries"].items():
        assert tuple(entry.keys()) == EXPECTED_REGIME_KEYS, etype
        assert len(entry) == 5, etype
        # No merged / roll-up verdict key may appear anywhere in an entry.
        assert _FORBIDDEN_MERGED_KEYS.isdisjoint(entry.keys()), etype
        # Each regime field is a bool / scope SIGNAL — legally distinct, independently typed.
        for key in EXPECTED_REGIME_KEYS:
            assert isinstance(entry[key], bool), (etype, key)


def test_fr_053_no_merged_verdict_key_anywhere_in_the_bundle() -> None:
    """Neither the top-level bundle nor any entry carries a merged cross-regime verdict — [UNIT-TEST]."""
    xwalk = build_entity_crosswalk()
    assert _FORBIDDEN_MERGED_KEYS.isdisjoint(xwalk.keys())
    # And the regime keyset itself contains nothing that smells like a roll-up.
    assert _FORBIDDEN_MERGED_KEYS.isdisjoint(set(REGIME_KEYS))


def test_fr_053_versioned_provenance_and_injectable_generated_at_byte_reproducible() -> None:
    """Versioned + provenance-stamped with an INJECTABLE ``generated_at`` → byte-repro — [UNIT-TEST].

    Two builds with the SAME injected timestamp serialise byte-identically (AX-002); a different
    timestamp changes only the provenance block, never the entries.
    """
    xwalk = build_entity_crosswalk()
    assert xwalk["version"] == ENTITY_REGULATORY_CROSSWALK_VERSION
    prov = xwalk["provenance"]
    assert set(prov) >= {"version", "source", "generated_at"}
    assert prov["version"] == ENTITY_REGULATORY_CROSSWALK_VERSION

    a = build_entity_crosswalk(generated_at="2026-06-01T00:00:00Z")
    b = build_entity_crosswalk(generated_at="2026-06-01T00:00:00Z")
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["provenance"]["generated_at"] == "2026-06-01T00:00:00Z"

    c = build_entity_crosswalk(generated_at="1999-12-31T23:59:59Z")
    assert c["provenance"]["generated_at"] == "1999-12-31T23:59:59Z"
    # Only the timestamp moved; the substantive entries are identical.
    assert a["entries"] == c["entries"]


def test_fr_053_disclaimer_is_non_strippable() -> None:
    """The disclaimer carrier raises on an empty disclaimer — [UNIT-TEST].

    Mirrors ``DesignProvenance`` / ``ASSESSMENT_CAVEAT``: a crosswalk that cannot disclaim its
    own "signal not determination" status must not be constructible.
    """
    assert CROSSWALK_DISCLAIMER.strip()
    assert build_entity_crosswalk()["disclaimer"] == CROSSWALK_DISCLAIMER
    # The dataclass that carries the disclaimer must reject empty / whitespace.
    carrier = ecx.EntityCrosswalkBundle
    with pytest.raises(ValueError):
        carrier(
            version=ENTITY_REGULATORY_CROSSWALK_VERSION,
            provenance={"version": ENTITY_REGULATORY_CROSSWALK_VERSION, "source": "x",
                        "generated_at": "2026-06-01T00:00:00Z"},
            entries={},
            disclaimer="   ",
        )


def test_fr_053_signal_not_determination_in_disclaimer() -> None:
    """The disclaimer states the crosswalk is a SIGNAL, not a determination — [UNIT-TEST]."""
    text = CROSSWALK_DISCLAIMER.lower()
    assert "signal" in text
    assert "determination" in text or "determine" in text


def test_fr_053_art9_special_category_and_glba_in_scope_examples() -> None:
    """At least one Art-9 special-category type True AND one GLBA-in-scope type — [UNIT-TEST].

    Sanity that the conservative mappings actually fire: health/biometric/genetic kinds land in
    GDPR Art-9 + HIPAA PHI; financial-account/card kinds land in GLBA nonpublic-personal-info.
    """
    entries = build_entity_crosswalk()["entries"]

    art9 = [t for t, e in entries.items() if e["gdpr_art9_special_category"]]
    assert art9, "expected at least one GDPR Art-9 special-category type"
    # Health condition is the canonical Art-9 example and must also be HIPAA PHI.
    assert entries["HEALTH_CONDITION"]["gdpr_art9_special_category"] is True
    assert entries["HEALTH_CONDITION"]["hipaa_phi"] is True

    glba = [t for t, e in entries.items() if e["glba_nonpublic_personal_info"]]
    assert glba, "expected at least one GLBA nonpublic-personal-info type"
    assert entries["BANK_ACCOUNT_NUMBER"]["glba_nonpublic_personal_info"] is True
    assert entries["CREDIT_CARD_NUMBER"]["glba_nonpublic_personal_info"] is True


def test_fr_053_core_direct_identifiers_in_gdpr_and_ccpa_scope() -> None:
    """Name / email / phone / address / SSN are GDPR + CCPA in-scope — [UNIT-TEST]."""
    entries = build_entity_crosswalk()["entries"]
    for t in ("PERSON_NAME", "EMAIL_ADDRESS", "PHONE_NUMBER", "STREET_ADDRESS",
              "SOCIAL_SECURITY_NUMBER"):
        assert entries[t]["gdpr"] is True, t
        assert entries[t]["ccpa"] is True, t
    # SSN is NOT itself HIPAA PHI absent a health context, and IS GLBA-relevant (a financial id).
    assert entries["SOCIAL_SECURITY_NUMBER"]["glba_nonpublic_personal_info"] is True
