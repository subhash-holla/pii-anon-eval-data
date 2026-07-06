"""Canonical entity-type registry — the SINGLE SOURCE OF TRUTH (DC-02; fixes M1/NFR-013).

Brownfield finding: the entity-type count drifted three ways — `validate.py` allowed
48, README claimed 65, TAXONOMY.md listed ~80. The ACTUAL set present in the v1.3.0
corpus is **66 types across 9 categories** (derived by scanning every annotation; 63
original + 3 GDPR Art-9 additions: GENETIC_DATA, SEXUAL_ORIENTATION, TRADE_UNION_MEMBERSHIP).
This module is that authoritative set; `validate.py`, the migration, TAXONOMY.md and
README all derive their counts from here so the drift cannot recur.
"""
from __future__ import annotations

# entity_type -> category, grounded in the actual corpus (one entry per observed type).
ENTITY_REGISTRY: dict[str, str] = {
    # contact (2)
    "EMAIL_ADDRESS": "contact", "PHONE_NUMBER": "contact",
    # digital_online (10)
    "API_KEY": "digital_online", "AUTHENTICATION_TOKEN": "digital_online",
    "BIOMETRIC_ID": "digital_online", "DEVICE_IDENTIFIER": "digital_online",
    "IP_ADDRESS": "digital_online", "MAC_ADDRESS": "digital_online",
    "PASSWORD": "digital_online", "SOCIAL_MEDIA_HANDLE": "digital_online",
    "URL": "digital_online", "USERNAME": "digital_online",
    # employment (4)
    "EDUCATION_LEVEL": "employment", "EMPLOYEE_ID": "employment",
    "JOB_TITLE": "employment", "SALARY": "employment",
    # financial (12)
    "BANK_ACCOUNT_NUMBER": "financial", "BANK_ROUTING_NUMBER": "financial",
    "CREDIT_CARD_FRAGMENT": "financial", "CREDIT_CARD_NUMBER": "financial",
    "CRYPTOCURRENCY_ADDRESS": "financial", "CVV": "financial", "IBAN": "financial",
    "INSURANCE_POLICY_NUMBER": "financial", "INVOICE_NUMBER": "financial",
    "PIN": "financial", "SWIFT_BIC_CODE": "financial", "TAX_ID": "financial",
    # government_legal (10)
    "BAR_NUMBER": "government_legal", "COURT_CASE_NUMBER": "government_legal",
    "DOCKET_NUMBER": "government_legal", "DRIVER_LICENSE_NUMBER": "government_legal",
    "LICENSE_PLATE": "government_legal", "NATIONAL_ID_NUMBER": "government_legal",
    "PASSPORT_NUMBER": "government_legal", "SOCIAL_SECURITY_NUMBER": "government_legal",
    "VEHICLE_IDENTIFICATION_NUMBER": "government_legal", "VISA_NUMBER": "government_legal",
    # identity_demographics (6)
    "AGE": "identity_demographics", "ETHNICITY": "identity_demographics",
    "GENDER": "identity_demographics", "NATIONALITY": "identity_demographics",
    "ORGANIZATION_NAME": "identity_demographics", "PERSON_NAME": "identity_demographics",
    # location_temporal (6)
    "DATE_OF_BIRTH": "location_temporal", "LATITUDE_LONGITUDE": "location_temporal",
    "LOCATION_NAME": "location_temporal", "POSTAL_CODE": "location_temporal",
    "STREET_ADDRESS": "location_temporal", "TIMESTAMP": "location_temporal",
    # medical_biological (8)
    "DEA_NUMBER": "medical_biological", "HEALTH_CONDITION": "medical_biological",
    "HEALTH_INSURANCE_ID": "medical_biological", "MEDICAL_RECORD_NUMBER": "medical_biological",
    "MEDICATION_NAME": "medical_biological", "NPI_NUMBER": "medical_biological",
    "PRESCRIPTION_NUMBER": "medical_biological", "PROCEDURE_NAME": "medical_biological",
    # special_category (8)
    "GENETIC_DATA": "special_category", "HOUSEHOLD_SIZE": "special_category",
    "MARITAL_STATUS": "special_category", "POLITICAL_OPINION": "special_category",
    "RELIGIOUS_BELIEF": "special_category", "SEXUAL_ORIENTATION": "special_category",
    "TRADE_UNION_MEMBERSHIP": "special_category", "VEHICLE_MODEL": "special_category",
}

CANONICAL_ENTITY_TYPES: frozenset[str] = frozenset(ENTITY_REGISTRY)
CATEGORIES: frozenset[str] = frozenset(ENTITY_REGISTRY.values())
SENSITIVITY_CLASSES: frozenset[str] = frozenset(
    {"direct_identifier", "quasi_identifier", "sensitive_attribute"}
)

ENTITY_TYPE_COUNT = len(CANONICAL_ENTITY_TYPES)   # 66 — cite this everywhere, not a literal
CATEGORY_COUNT = len(CATEGORIES)                  # 9

# B-7: national / jurisdiction-specific identifier types. Curated + EXPLICITLY NON-EXHAUSTIVE — the dataset
# does NOT claim per-jurisdiction completeness; this is an illustrative coverage count for the CL-01/H-01 guard.
JURISDICTION_IDENTIFIER_TYPES: frozenset[str] = frozenset({
    "SOCIAL_SECURITY_NUMBER", "DRIVER_LICENSE_NUMBER", "PASSPORT_NUMBER", "NATIONAL_ID_NUMBER",
    "TAX_ID", "BANK_ROUTING_NUMBER", "HEALTH_INSURANCE_ID", "LICENSE_PLATE",
})
assert JURISDICTION_IDENTIFIER_TYPES <= set(CANONICAL_ENTITY_TYPES), "jurisdiction list drifted from taxonomy"
JURISDICTION_IDENTIFIER_COUNT: int = len(JURISDICTION_IDENTIFIER_TYPES)


def is_known_entity_type(entity_type: str) -> bool:
    return entity_type in CANONICAL_ENTITY_TYPES


def category_of(entity_type: str) -> str | None:
    return ENTITY_REGISTRY.get(entity_type)


def types_in_category(category: str) -> list[str]:
    return sorted(t for t, c in ENTITY_REGISTRY.items() if c == category)


# ── Risk tiers for statistical-power targets (S-PWR; 03-design/sampling-design.md §3.4) ──
# Govern the per-cell positive target (critical→1,522 / standard→753 / long_tail→200).
# DERIVED from ENTITY_REGISTRY — never a hand-maintained parallel count.
RISK_TIERS: frozenset[str] = frozenset({"critical", "standard", "long_tail"})

# Credential / secret types (the "one leak = breach" set within digital_online).
_CREDENTIAL_TYPES: frozenset[str] = frozenset(
    {"API_KEY", "PASSWORD", "AUTHENTICATION_TOKEN", "BIOMETRIC_ID", "DEVICE_IDENTIFIER"}
)
# Strong government identifiers (single-span breach risk) pulled up from government_legal.
_STRONG_GOVID_TYPES: frozenset[str] = frozenset(
    {"SOCIAL_SECURITY_NUMBER", "NATIONAL_ID_NUMBER", "PASSPORT_NUMBER",
     "DRIVER_LICENSE_NUMBER", "VISA_NUMBER"}
)
# Inherently rare / lower-stakes-as-a-single-span sensitive attributes + soft demographics.
_LONG_TAIL_TYPES: frozenset[str] = frozenset(
    {"POLITICAL_OPINION", "RELIGIOUS_BELIEF", "MARITAL_STATUS", "HOUSEHOLD_SIZE",
     "ETHNICITY", "AGE", "GENDER", "NATIONALITY", "EDUCATION_LEVEL", "VEHICLE_MODEL",
     "SEXUAL_ORIENTATION", "TRADE_UNION_MEMBERSHIP", "GENETIC_DATA"}
)


def risk_tier(entity_type: str) -> str:
    """Risk tier governing a type's statistical-power target (sampling-design.md §3.4).

    critical  → financial category ∪ credential/secret ∪ strong gov-id ("one miss = breach")
    long_tail → inherently rare / lower-stakes sensitive attributes & soft demographics
    standard  → everything else
    Fail-loud on an unknown type (M1 single-source-of-truth discipline).
    """
    if entity_type not in ENTITY_REGISTRY:
        raise KeyError(f"unknown entity_type {entity_type!r} (not in canonical registry)")
    if (
        ENTITY_REGISTRY[entity_type] == "financial"
        or entity_type in _CREDENTIAL_TYPES
        or entity_type in _STRONG_GOVID_TYPES
    ):
        return "critical"
    if entity_type in _LONG_TAIL_TYPES:
        return "long_tail"
    return "standard"


def types_in_tier(tier: str) -> list[str]:
    """Canonical entity types in a risk tier (sorted, derived)."""
    if tier not in RISK_TIERS:
        raise ValueError(f"unknown risk tier {tier!r}; expected one of {sorted(RISK_TIERS)}")
    return sorted(t for t in ENTITY_REGISTRY if risk_tier(t) == tier)
