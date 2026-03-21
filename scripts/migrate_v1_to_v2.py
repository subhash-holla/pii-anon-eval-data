#!/usr/bin/env python3
"""
Migrate PII-Anon Evaluation Dataset from v1 to v2.

Reads all v1 JSONL files, filters to clean records (no template placeholders),
deduplicates by text content hash, canonicalizes entity types, applies unified
v2 schema, assigns primary_dimension, and writes a single canonical v2 JSONL file.

Usage:
    python scripts/migrate_v1_to_v2.py [--output-dir src/pii_anon_datasets/data]
"""

import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import uuid
from collections import Counter
from pathlib import Path
from typing import Any

# ─── Constants ───────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
V1_DIR = REPO_ROOT / "src" / "pii_anon_datasets"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "src" / "pii_anon_datasets" / "data"

V1_FILES = [
    V1_DIR / "benchmarks" / "data" / "pii_anon_benchmark_v1.jsonl",
    V1_DIR / "eval_framework" / "data" / "pii_anon_eval_v1.jsonl",
]

PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")

# ─── Entity Type Canonicalization ────────────────────────────────────────────

ENTITY_TYPE_MAP: dict[str, str] = {
    # Identity
    "PERSON_NAME": "PERSON_NAME",
    "NAME_PERSON": "PERSON_NAME",
    "ORGANIZATION": "ORGANIZATION_NAME",
    "NAME_ORGANIZATION": "ORGANIZATION_NAME",
    "LOCATION": "LOCATION_NAME",
    "NAME_LOCATION": "LOCATION_NAME",
    # Contact
    "EMAIL_ADDRESS": "EMAIL_ADDRESS",
    "PHONE_NUMBER": "PHONE_NUMBER",
    "FAX_NUMBER": "FAX_NUMBER",
    "PHONE_COUNTRY_CODE": "PHONE_COUNTRY_CODE",
    "PHONE_AREA_CODE": "PHONE_AREA_CODE",
    "PHONE_EXTENSION": "PHONE_EXTENSION",
    "MOBILE_DEVICE_ID": "MOBILE_DEVICE_ID",
    # Financial
    "CREDIT_CARD": "CREDIT_CARD_NUMBER",
    "CREDIT_CARD_NUMBER": "CREDIT_CARD_NUMBER",
    "CREDIT_CARD_FRAGMENT": "CREDIT_CARD_FRAGMENT",
    "BANK_ACCOUNT": "BANK_ACCOUNT_NUMBER",
    "BANK_ACCOUNT_NUMBER": "BANK_ACCOUNT_NUMBER",
    "ROUTING_NUMBER": "BANK_ROUTING_NUMBER",
    "BANK_ROUTING_NUMBER": "BANK_ROUTING_NUMBER",
    "IBAN": "IBAN",
    "SWIFT_CODE": "SWIFT_BIC_CODE",
    "SWIFT_BIC_CODE": "SWIFT_BIC_CODE",
    "CRYPTOCURRENCY_WALLET": "CRYPTOCURRENCY_ADDRESS",
    "CRYPTOCURRENCY_ADDRESS": "CRYPTOCURRENCY_ADDRESS",
    "TRANSACTION_ID": "TRANSACTION_ID",
    "TAX_ID": "TAX_ID",
    # Digital
    "USERNAME": "USERNAME",
    "PASSWORD": "PASSWORD",
    "API_KEY": "API_KEY",
    "AUTHENTICATION_TOKEN": "AUTHENTICATION_TOKEN",
    "SOCIAL_MEDIA_HANDLE": "SOCIAL_MEDIA_HANDLE",
    "URL_WITH_PII": "URL",
    "URL": "URL",
    "IP_ADDRESS": "IP_ADDRESS",
    "IP_V6_ADDRESS": "IPV6_ADDRESS",
    "IPV6_ADDRESS": "IPV6_ADDRESS",
    "MAC_ADDRESS": "MAC_ADDRESS",
    "DEVICE_ID": "DEVICE_IDENTIFIER",
    "DEVICE_IDENTIFIER": "DEVICE_IDENTIFIER",
    "BIOMETRIC_ID": "BIOMETRIC_ID",
    # Government
    "PASSPORT": "PASSPORT_NUMBER",
    "PASSPORT_NUMBER": "PASSPORT_NUMBER",
    "DRIVERS_LICENSE": "DRIVER_LICENSE_NUMBER",
    "DRIVER_LICENSE_NUMBER": "DRIVER_LICENSE_NUMBER",
    "US_SSN": "SOCIAL_SECURITY_NUMBER",
    "SOCIAL_SECURITY_NUMBER": "SOCIAL_SECURITY_NUMBER",
    "NATIONAL_ID": "NATIONAL_ID_NUMBER",
    "NATIONAL_ID_NUMBER": "NATIONAL_ID_NUMBER",
    "VISA_NUMBER": "VISA_NUMBER",
    "LICENSE_PLATE": "LICENSE_PLATE",
    # Medical
    "MEDICAL_RECORD_NUMBER": "MEDICAL_RECORD_NUMBER",
    "MEDICAL_DIAGNOSIS": "HEALTH_CONDITION",
    "HEALTH_CONDITION": "HEALTH_CONDITION",
    "HEALTH_INSURANCE_ID": "HEALTH_INSURANCE_ID",
    "INSURANCE_CLAIM_NUMBER": "INSURANCE_CLAIM_NUMBER",
    "MEDICATION_NAME": "MEDICATION_NAME",
    "PROCEDURE_NAME": "PROCEDURE_NAME",
    "GENETIC_MARKER": "GENETIC_MARKER",
    "PRESCRIPTION_NUMBER": "PRESCRIPTION_NUMBER",
    # Location & Temporal
    "ADDRESS": "STREET_ADDRESS",
    "STREET_ADDRESS": "STREET_ADDRESS",
    "POSTAL_CODE": "POSTAL_CODE",
    "ZIP_CODE": "POSTAL_CODE",
    "LATITUDE_LONGITUDE": "LATITUDE_LONGITUDE",
    "LOCATION_COORDINATES": "LATITUDE_LONGITUDE",
    "BUILDING_NAME": "BUILDING_NAME",
    "LOCATION_NAME": "LOCATION_NAME",
    "TIMESTAMP": "TIMESTAMP",
    "BIRTHDATE": "DATE_OF_BIRTH",
    "DATE_OF_BIRTH": "DATE_OF_BIRTH",
    "EVENT_DATE": "EVENT_DATE",
    # Employment
    "JOB_TITLE": "JOB_TITLE",
    "SALARY": "SALARY",
    "EMPLOYEE_ID": "EMPLOYEE_ID",
    "EDUCATION_LEVEL": "EDUCATION_LEVEL",
    # Special Category (GDPR Art. 9)
    "NATIONALITY": "NATIONALITY",
    "GENDER": "GENDER",
    "AGE": "AGE",
    "ETHNICITY": "ETHNICITY",
    "ETHNIC_ORIGIN": "ETHNICITY",
    "DISABILITY_STATUS": "DISABILITY_STATUS",
    "POLITICAL_OPINION": "POLITICAL_OPINION",
    "RELIGIOUS_BELIEF": "RELIGIOUS_BELIEF",
    "MARITAL_STATUS": "MARITAL_STATUS",
    "HOUSEHOLD_SIZE": "HOUSEHOLD_SIZE",
    "VEHICLE_IDENTIFICATION_NUMBER": "VEHICLE_IDENTIFICATION_NUMBER",
    "VEHICLE_MODEL": "VEHICLE_MODEL",
}

# Entity type -> category mapping
ENTITY_CATEGORY: dict[str, str] = {
    "PERSON_NAME": "identity_demographics",
    "ORGANIZATION_NAME": "identity_demographics",
    "LOCATION_NAME": "identity_demographics",
    "NATIONALITY": "identity_demographics",
    "GENDER": "identity_demographics",
    "AGE": "identity_demographics",
    "ETHNICITY": "identity_demographics",
    "DISABILITY_STATUS": "identity_demographics",
    "EMAIL_ADDRESS": "contact",
    "PHONE_NUMBER": "contact",
    "FAX_NUMBER": "contact",
    "PHONE_COUNTRY_CODE": "contact",
    "PHONE_AREA_CODE": "contact",
    "PHONE_EXTENSION": "contact",
    "MOBILE_DEVICE_ID": "contact",
    "CREDIT_CARD_NUMBER": "financial",
    "CREDIT_CARD_FRAGMENT": "financial",
    "BANK_ACCOUNT_NUMBER": "financial",
    "BANK_ROUTING_NUMBER": "financial",
    "IBAN": "financial",
    "SWIFT_BIC_CODE": "financial",
    "CRYPTOCURRENCY_ADDRESS": "financial",
    "TRANSACTION_ID": "financial",
    "TAX_ID": "financial",
    "USERNAME": "digital_online",
    "PASSWORD": "digital_online",
    "API_KEY": "digital_online",
    "AUTHENTICATION_TOKEN": "digital_online",
    "SOCIAL_MEDIA_HANDLE": "digital_online",
    "URL": "digital_online",
    "IP_ADDRESS": "digital_online",
    "IPV6_ADDRESS": "digital_online",
    "MAC_ADDRESS": "digital_online",
    "DEVICE_IDENTIFIER": "digital_online",
    "BIOMETRIC_ID": "digital_online",
    "PASSPORT_NUMBER": "government_legal",
    "DRIVER_LICENSE_NUMBER": "government_legal",
    "SOCIAL_SECURITY_NUMBER": "government_legal",
    "NATIONAL_ID_NUMBER": "government_legal",
    "VISA_NUMBER": "government_legal",
    "LICENSE_PLATE": "government_legal",
    "VEHICLE_IDENTIFICATION_NUMBER": "government_legal",
    "MEDICAL_RECORD_NUMBER": "medical_biological",
    "HEALTH_CONDITION": "medical_biological",
    "HEALTH_INSURANCE_ID": "medical_biological",
    "INSURANCE_CLAIM_NUMBER": "medical_biological",
    "MEDICATION_NAME": "medical_biological",
    "PROCEDURE_NAME": "medical_biological",
    "GENETIC_MARKER": "medical_biological",
    "PRESCRIPTION_NUMBER": "medical_biological",
    "STREET_ADDRESS": "location_temporal",
    "POSTAL_CODE": "location_temporal",
    "LATITUDE_LONGITUDE": "location_temporal",
    "BUILDING_NAME": "location_temporal",
    "LOCATION_NAME": "location_temporal",
    "TIMESTAMP": "location_temporal",
    "DATE_OF_BIRTH": "location_temporal",
    "EVENT_DATE": "location_temporal",
    "JOB_TITLE": "employment",
    "SALARY": "employment",
    "EMPLOYEE_ID": "employment",
    "EDUCATION_LEVEL": "employment",
    "POLITICAL_OPINION": "special_category",
    "RELIGIOUS_BELIEF": "special_category",
    "MARITAL_STATUS": "special_category",
    "HOUSEHOLD_SIZE": "special_category",
    "VEHICLE_MODEL": "special_category",
}

# Entity type -> sensitivity classification
SENSITIVITY_MAP: dict[str, str] = {
    # Direct identifiers — uniquely identify an individual
    "PERSON_NAME": "direct_identifier",
    "EMAIL_ADDRESS": "direct_identifier",
    "PHONE_NUMBER": "direct_identifier",
    "SOCIAL_SECURITY_NUMBER": "direct_identifier",
    "PASSPORT_NUMBER": "direct_identifier",
    "DRIVER_LICENSE_NUMBER": "direct_identifier",
    "NATIONAL_ID_NUMBER": "direct_identifier",
    "MEDICAL_RECORD_NUMBER": "direct_identifier",
    "CREDIT_CARD_NUMBER": "direct_identifier",
    "BANK_ACCOUNT_NUMBER": "direct_identifier",
    "IBAN": "direct_identifier",
    "IP_ADDRESS": "direct_identifier",
    "IPV6_ADDRESS": "direct_identifier",
    "MAC_ADDRESS": "direct_identifier",
    "LICENSE_PLATE": "direct_identifier",
    "BIOMETRIC_ID": "direct_identifier",
    "USERNAME": "direct_identifier",
    "VEHICLE_IDENTIFICATION_NUMBER": "direct_identifier",
    "VISA_NUMBER": "direct_identifier",
    "TAX_ID": "direct_identifier",
    "EMPLOYEE_ID": "direct_identifier",
    "HEALTH_INSURANCE_ID": "direct_identifier",
    "INSURANCE_CLAIM_NUMBER": "direct_identifier",
    "PRESCRIPTION_NUMBER": "direct_identifier",
    "DEVICE_IDENTIFIER": "direct_identifier",
    "MOBILE_DEVICE_ID": "direct_identifier",
    "CRYPTOCURRENCY_ADDRESS": "direct_identifier",
    "TRANSACTION_ID": "direct_identifier",
    "FAX_NUMBER": "direct_identifier",
    "SOCIAL_MEDIA_HANDLE": "direct_identifier",
    "URL": "direct_identifier",
    "API_KEY": "direct_identifier",
    "AUTHENTICATION_TOKEN": "direct_identifier",
    "PASSWORD": "direct_identifier",
    # Quasi-identifiers — identifying in combination
    "DATE_OF_BIRTH": "quasi_identifier",
    "STREET_ADDRESS": "quasi_identifier",
    "POSTAL_CODE": "quasi_identifier",
    "LATITUDE_LONGITUDE": "quasi_identifier",
    "AGE": "quasi_identifier",
    "GENDER": "quasi_identifier",
    "NATIONALITY": "quasi_identifier",
    "ETHNICITY": "quasi_identifier",
    "LOCATION_NAME": "quasi_identifier",
    "BUILDING_NAME": "quasi_identifier",
    "ORGANIZATION_NAME": "quasi_identifier",
    "JOB_TITLE": "quasi_identifier",
    "EDUCATION_LEVEL": "quasi_identifier",
    "SALARY": "quasi_identifier",
    "MARITAL_STATUS": "quasi_identifier",
    "HOUSEHOLD_SIZE": "quasi_identifier",
    "VEHICLE_MODEL": "quasi_identifier",
    "EVENT_DATE": "quasi_identifier",
    "TIMESTAMP": "quasi_identifier",
    "CREDIT_CARD_FRAGMENT": "quasi_identifier",
    "BANK_ROUTING_NUMBER": "quasi_identifier",
    "SWIFT_BIC_CODE": "quasi_identifier",
    "PHONE_COUNTRY_CODE": "quasi_identifier",
    "PHONE_AREA_CODE": "quasi_identifier",
    "PHONE_EXTENSION": "quasi_identifier",
    "DISABILITY_STATUS": "quasi_identifier",
    # Sensitive attributes — GDPR Article 9
    "HEALTH_CONDITION": "sensitive_attribute",
    "MEDICATION_NAME": "sensitive_attribute",
    "PROCEDURE_NAME": "sensitive_attribute",
    "GENETIC_MARKER": "sensitive_attribute",
    "POLITICAL_OPINION": "sensitive_attribute",
    "RELIGIOUS_BELIEF": "sensitive_attribute",
}

# ─── Dimension Assignment ────────────────────────────────────────────────────

# Map scenario_id/evaluation_dimension to v2 primary_dimension
DIMENSION_MAP: dict[str, str] = {
    # From benchmark evaluation_dimension field
    "multilingual": "multilingual",
    "context_preservation": "context_preservation",
    "context_loss": "context_preservation",
    "edge_cases": "edge_cases",
    "format_variations": "format_variations",
    "entity_tracking": "entity_tracking",
    "temporal_consistency": "temporal_consistency",
    # From benchmark scenario_id field
    "baseline": "diverse_pii_types",
    "entity_consistency": "entity_tracking",
    "continuity_tracking": "entity_tracking",
    "ambiguous": "edge_cases",
    "code_embedded_pii": "edge_cases",
    "dense_pii": "edge_cases",
    "false_positive": "edge_cases",
    "overlapping_entities": "edge_cases",
    "pii_in_url": "edge_cases",
    "unicode_edge_case": "edge_cases",
    "format_csv": "format_variations",
    "format_json": "format_variations",
    "format_table": "format_variations",
    "format_xml": "format_variations",
    # From eval framework scenarios
    "medical_record": "diverse_pii_types",
    "complex_medical": "diverse_pii_types",
    "multi_entity": "diverse_pii_types",
    "multi_entity_advanced": "diverse_pii_types",
    "travel_document": "diverse_pii_types",
    "financial_record": "diverse_pii_types",
    "employment_record": "diverse_pii_types",
    "log_entry": "format_variations",
    "api_log": "format_variations",
}

# Language family mapping
LANGUAGE_FAMILY_MAP: dict[str, str] = {
    "en": "Germanic", "de": "Germanic", "nl": "Germanic", "sv": "Germanic",
    "no": "Germanic", "da": "Germanic", "is": "Germanic", "af": "Germanic",
    "es": "Romance", "fr": "Romance", "it": "Romance", "pt": "Romance",
    "ro": "Romance", "ca": "Romance", "mt": "Romance",
    "pl": "Slavic", "ru": "Slavic", "uk": "Slavic", "cs": "Slavic",
    "sk": "Slavic", "hr": "Slavic", "sr": "Slavic", "bg": "Slavic",
    "mk": "Slavic", "be": "Slavic",
    "zh": "Sinitic", "zh-Hans": "Sinitic", "zh-Hant": "Sinitic",
    "ja": "Japonic", "ko": "Koreanic",
    "ar": "Semitic", "he": "Semitic",
    "hi": "Indo-Aryan", "bn": "Indo-Aryan", "ur": "Indo-Aryan",
    "fa": "Iranian", "ku": "Iranian", "ps": "Iranian",
    "tr": "Turkic", "kk": "Turkic", "az": "Turkic", "ug": "Turkic",
    "mn": "Mongolic",
    "th": "Tai", "lo": "Tai",
    "vi": "Vietic",
    "km": "Austroasiatic",
    "fi": "Uralic", "hu": "Uralic", "et": "Uralic",
    "lt": "Baltic", "lv": "Baltic",
    "ka": "Kartvelian", "hy": "Armenian", "el": "Hellenic",
    "sq": "Albanian",
    "sw": "Niger-Congo", "yo": "Niger-Congo", "zu": "Niger-Congo",
    "am": "Semitic",
    "si": "Indo-Aryan", "ne": "Indo-Aryan",
    "tl": "Austronesian", "ms": "Austronesian", "id": "Austronesian",
}

SCRIPT_MAP: dict[str, str] = {
    "en": "Latn", "es": "Latn", "fr": "Latn", "de": "Latn", "it": "Latn",
    "pt": "Latn", "nl": "Latn", "pl": "Latn", "tr": "Latn", "sv": "Latn",
    "no": "Latn", "da": "Latn", "fi": "Latn", "cs": "Latn", "ro": "Latn",
    "hu": "Latn", "sk": "Latn", "hr": "Latn", "lt": "Latn", "et": "Latn",
    "is": "Latn", "af": "Latn", "vi": "Latn", "mt": "Latn", "ca": "Latn",
    "sq": "Latn", "lv": "Latn", "sw": "Latn", "id": "Latn", "ms": "Latn",
    "tl": "Latn", "az": "Latn", "yo": "Latn", "zu": "Latn",
    "ru": "Cyrl", "uk": "Cyrl", "sr": "Cyrl", "bg": "Cyrl",
    "mk": "Cyrl", "be": "Cyrl", "mn": "Cyrl", "kk": "Cyrl",
    "ar": "Arab", "fa": "Arab", "ur": "Arab", "ps": "Arab", "ku": "Arab", "ug": "Arab",
    "zh": "Hans", "zh-Hans": "Hans", "zh-Hant": "Hant",
    "ja": "Jpan", "ko": "Kore",
    "el": "Grek", "hi": "Deva", "bn": "Beng", "th": "Thai",
    "he": "Hebr", "ka": "Geor", "hy": "Armn", "lo": "Laoo", "km": "Khmr",
    "am": "Ethi", "si": "Sinh", "ne": "Deva",
}

RESOURCE_LEVEL_MAP: dict[str, str] = {
    "en": "high", "es": "high", "fr": "high", "de": "high", "it": "high",
    "pt": "high", "nl": "high", "ru": "high", "zh": "high", "zh-Hans": "high",
    "zh-Hant": "high", "ja": "high", "ko": "high", "ar": "high", "hi": "high",
    "pl": "medium", "tr": "medium", "sv": "medium", "no": "medium",
    "da": "medium", "fi": "medium", "cs": "medium", "ro": "medium",
    "hu": "medium", "el": "medium", "he": "medium", "th": "medium",
    "vi": "medium", "id": "medium", "uk": "medium", "fa": "medium",
    "bn": "medium", "ca": "medium",
}


def canonicalize_entity_type(raw_type: str) -> str:
    """Map a v1 entity type name to canonical v2 name."""
    canonical = ENTITY_TYPE_MAP.get(raw_type)
    if canonical is None:
        print(f"  WARNING: Unknown entity type '{raw_type}', keeping as-is", file=sys.stderr)
        return raw_type
    return canonical


def get_category(entity_type: str) -> str:
    return ENTITY_CATEGORY.get(entity_type, "identity_demographics")


def get_sensitivity(entity_type: str) -> str:
    return SENSITIVITY_MAP.get(entity_type, "quasi_identifier")


def remove_nested_overlaps(annotations: list[dict]) -> list[dict]:
    """Remove overlapping annotations by keeping the longest span at each position.

    For entity tracking records, the same entity may appear as nested spans
    (e.g., "Lisa" within "Lisa Ramirez"). Keep the outermost span and drop
    any annotation whose [start, end) is fully contained within another.
    """
    if len(annotations) <= 1:
        return annotations

    # Sort by start ascending, then by span length descending (longest first)
    sorted_anns = sorted(annotations, key=lambda a: (a["start"], -(a["end"] - a["start"])))

    kept = []
    seen_spans: set[tuple[int, int, str]] = set()
    for ann in sorted_anns:
        span_key = (ann["start"], ann["end"], ann["entity_type"])
        # Skip exact duplicate spans (same position and type)
        if span_key in seen_spans:
            continue
        seen_spans.add(span_key)

        # Check if this annotation is fully contained within any already-kept annotation
        is_contained = False
        for k in kept:
            if k["start"] <= ann["start"] and ann["end"] <= k["end"] and (k["start"], k["end"]) != (ann["start"], ann["end"]):
                is_contained = True
                break
        if not is_contained:
            kept.append(ann)

    # Re-assign entity_ids
    for i, ann in enumerate(kept):
        ann["entity_id"] = f"e{i}"

    return kept


def text_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def has_placeholders(text: str) -> bool:
    return bool(PLACEHOLDER_RE.search(text))


def assign_primary_dimension(rec: dict[str, Any]) -> str:
    """Determine primary_dimension from v1 metadata."""
    # Try evaluation_dimension (benchmark files)
    eval_dim = rec.get("evaluation_dimension", "")
    if eval_dim and eval_dim in DIMENSION_MAP:
        return DIMENSION_MAP[eval_dim]

    # Try scenario_id
    scenario = rec.get("scenario_id", "")
    if scenario and scenario in DIMENSION_MAP:
        return DIMENSION_MAP[scenario]

    # Try dimension_tags (eval framework files)
    dim_tags = rec.get("dimension_tags", [])
    if isinstance(dim_tags, list) and dim_tags:
        for tag in dim_tags:
            mapped = DIMENSION_MAP.get(tag)
            if mapped:
                return mapped

    # Fallback: non-English -> multilingual, else diverse_pii_types
    lang = rec.get("language", "en")
    if lang != "en":
        return "multilingual"
    return "diverse_pii_types"


def compute_dimensions(rec: dict[str, Any], primary: str) -> list[str]:
    """Compute all applicable dimensions for a record."""
    dims = {primary}

    lang = rec.get("language", "en")
    if lang != "en":
        dims.add("multilingual")

    labels = rec.get("labels", [])
    entity_types = {l.get("entity_type", "") for l in labels}
    if len(entity_types) >= 4:
        dims.add("diverse_pii_types")

    # Coreference / entity tracking signals
    cluster_ids = {l.get("entity_cluster_id", "none") for l in labels}
    cluster_ids.discard("none")
    if len(cluster_ids) > 0:
        dims.add("entity_tracking")

    return sorted(dims)


def infer_data_type(rec: dict[str, Any]) -> str:
    """Infer data_type from v1 metadata."""
    # Check existing data_type or context_group
    dt = rec.get("data_type") or rec.get("context_group", "")
    if dt in ("unstructured_text", "structured", "semi_structured", "code", "logs"):
        return dt

    text = rec.get("text", "")
    scenario = rec.get("scenario_id", "")

    if scenario.startswith("format_json") or '{"' in text[:20]:
        return "structured"
    if scenario.startswith("format_xml") or text.strip().startswith("<"):
        return "semi_structured"
    if scenario.startswith("format_csv") or scenario.startswith("format_table"):
        return "structured"
    if scenario in ("log_entry", "api_log") or text.startswith("[INFO]") or text.startswith("[ERROR]"):
        return "logs"
    if scenario == "code_embedded_pii":
        return "code"

    return "unstructured_text"


def infer_domain(rec: dict[str, Any]) -> str:
    """Infer domain from scenario and entity types."""
    scenario = rec.get("scenario_id", "")
    if "medical" in scenario or "clinical" in scenario:
        return "clinical"
    if "financial" in scenario or "bank" in scenario:
        return "financial"
    if "legal" in scenario or "court" in scenario:
        return "legal"
    if "code" in scenario:
        return "technology"

    entity_types = {l.get("entity_type", "") for l in rec.get("labels", [])}
    medical_types = {"MEDICAL_RECORD_NUMBER", "MEDICAL_DIAGNOSIS", "HEALTH_CONDITION",
                     "HEALTH_INSURANCE_ID", "MEDICATION_NAME", "PROCEDURE_NAME",
                     "PRESCRIPTION_NUMBER", "GENETIC_MARKER", "INSURANCE_CLAIM_NUMBER"}
    if entity_types & medical_types:
        return "clinical"

    financial_types = {"CREDIT_CARD", "CREDIT_CARD_NUMBER", "BANK_ACCOUNT",
                       "BANK_ACCOUNT_NUMBER", "IBAN", "SWIFT_CODE", "SWIFT_BIC_CODE",
                       "CRYPTOCURRENCY_WALLET", "CRYPTOCURRENCY_ADDRESS", "ROUTING_NUMBER",
                       "BANK_ROUTING_NUMBER"}
    if entity_types & financial_types:
        return "financial"

    return "general"


def infer_context_length_tier(token_count: int) -> str:
    if token_count <= 50:
        return "short"
    if token_count <= 200:
        return "medium"
    if token_count <= 500:
        return "long"
    return "very_long"


def convert_record(rec: dict[str, Any], record_id: str) -> dict[str, Any]:
    """Convert a v1 record to v2 schema."""
    text = rec["text"]
    lang = rec.get("language", "en")

    # Build annotations
    annotations = []
    for i, label in enumerate(rec.get("labels", [])):
        raw_type = label.get("entity_type", "UNKNOWN")
        canonical_type = canonicalize_entity_type(raw_type)

        s = label.get("start", 0)
        e = label.get("end", 0)
        span_text = text[s:e] if 0 <= s < e <= len(text) else ""

        cluster_id = label.get("entity_cluster_id")
        if cluster_id == "none" or cluster_id is None:
            cluster_id = None

        mention_variant = label.get("mention_variant")
        if mention_variant == "none" or mention_variant is None:
            mention_variant = None

        annotations.append({
            "entity_id": f"e{i}",
            "entity_type": canonical_type,
            "start": s,
            "end": e,
            "text": span_text,
            "category": get_category(canonical_type),
            "sensitivity_class": get_sensitivity(canonical_type),
            "cluster_id": cluster_id,
            "mention_variant": mention_variant,
        })

    # Remove nested overlapping annotations (e.g., "Lisa" inside "Lisa Ramirez")
    annotations = remove_nested_overlaps(annotations)

    primary_dim = assign_primary_dimension(rec)
    dimensions = compute_dimensions(rec, primary_dim)
    data_type = infer_data_type(rec)
    domain = infer_domain(rec)
    token_count = rec.get("token_count") or max(1, len(text.split()))
    difficulty = rec.get("difficulty_level", "moderate")

    # Entity tracking metadata
    cluster_ids = {a["cluster_id"] for a in annotations if a["cluster_id"]}
    coreference_chains = rec.get("coreference_chains", [])
    if not coreference_chains and cluster_ids:
        chains = {}
        for a in annotations:
            if a["cluster_id"]:
                chains.setdefault(a["cluster_id"], []).append(a["entity_id"])
        coreference_chains = [ids for ids in chains.values() if len(ids) > 1]

    num_repeated = rec.get("num_repeated_entities", 0)
    if not num_repeated:
        type_counts = Counter(a["entity_type"] for a in annotations)
        num_repeated = sum(1 for c in type_counts.values() if c > 1)

    # Privacy risk
    quasi_ids = [a["entity_type"] for a in annotations if a["sensitivity_class"] == "quasi_identifier"]
    reident_risk = rec.get("reidentification_risk_tier", "low")
    if not reident_risk or reident_risk == "low":
        if len(set(quasi_ids)) >= 3:
            reident_risk = "high"
        elif len(set(quasi_ids)) >= 2:
            reident_risk = "moderate"
        else:
            reident_risk = "low"

    # Regulatory domains
    reg_domains = rec.get("regulatory_domain", [])
    if not reg_domains:
        reg_domains = ["gdpr"]
        entity_types = {a["entity_type"] for a in annotations}
        if entity_types & {"MEDICAL_RECORD_NUMBER", "HEALTH_CONDITION", "MEDICATION_NAME",
                           "PROCEDURE_NAME", "HEALTH_INSURANCE_ID", "PRESCRIPTION_NUMBER"}:
            reg_domains.append("hipaa")
        if entity_types & {"SOCIAL_SECURITY_NUMBER", "DRIVER_LICENSE_NUMBER"}:
            reg_domains.append("ccpa")

    v2_record = {
        "record_id": record_id,
        "text": text,
        "version": "2.0.0",
        "annotations": annotations,
        "language": lang,
        "script": rec.get("script") or SCRIPT_MAP.get(lang, "Latn"),
        "language_family": rec.get("language_family") or LANGUAGE_FAMILY_MAP.get(lang, "unknown"),
        "resource_level": rec.get("resource_level") or RESOURCE_LEVEL_MAP.get(lang, "low"),
        "primary_dimension": primary_dim,
        "dimensions": dimensions,
        "data_type": data_type,
        "document_type": None,
        "domain": domain,
        "difficulty_level": difficulty,
        "context_length_tier": rec.get("context_length_tier") or infer_context_length_tier(token_count),
        "token_count": token_count,
        "entity_tracking": {
            "num_repeated_entities": num_repeated,
            "coreference_chains": coreference_chains,
            "tracking_difficulty": rec.get("entity_tracking_difficulty", "none"),
            "num_distinct_persons": len(cluster_ids) if cluster_ids else 0,
        },
        "adversarial": {
            "type": rec.get("adversarial_type"),
            "difficulty": "clean",
            "techniques": [],
        },
        "privacy_risk": {
            "quasi_identifiers": sorted(set(quasi_ids)),
            "reidentification_risk": reident_risk,
            "k_anonymity_estimate": None,
        },
        "regulatory_domains": reg_domains,
        "query_context": None,
        "provenance": {
            "source_type": rec.get("source_type", "synthetic"),
            "license": rec.get("license", "CC0-1.0"),
            "generation_seed": 42,
            "v1_record_id": rec.get("id"),
        },
    }
    return v2_record


def main():
    parser = argparse.ArgumentParser(description="Migrate PII-Anon v1 to v2")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true", help="Print stats without writing")
    args = parser.parse_args()

    print("=" * 70)
    print("PII-Anon Dataset Migration: v1 -> v2")
    print("=" * 70)

    # Phase 1: Read and deduplicate
    seen_hashes: set[str] = set()
    clean_records: list[tuple[dict, str]] = []  # (record, source_file)
    stats = Counter()

    for fpath in V1_FILES:
        if not fpath.exists():
            print(f"WARNING: {fpath} not found, skipping", file=sys.stderr)
            continue

        fname = fpath.name
        print(f"\nReading {fname}...")
        file_total = 0
        file_clean = 0
        file_dup = 0

        with open(fpath) as f:
            for line in f:
                file_total += 1
                rec = json.loads(line)
                text = rec.get("text", "")

                # Skip records with template placeholders
                if has_placeholders(text):
                    stats["placeholder_skipped"] += 1
                    continue

                # Skip records with no labels
                if not rec.get("labels"):
                    stats["no_labels_skipped"] += 1
                    continue

                # Deduplicate by text hash
                h = text_hash(text)
                if h in seen_hashes:
                    file_dup += 1
                    stats["duplicates"] += 1
                    continue

                seen_hashes.add(h)
                clean_records.append((rec, fname))
                file_clean += 1

        print(f"  Total: {file_total}, Clean: {file_clean}, Duplicates: {file_dup}, "
              f"Placeholders: {file_total - file_clean - file_dup}")
        stats[f"from_{fname}"] = file_clean

    print(f"\nTotal unique clean records: {len(clean_records)}")
    print(f"Skipped: {stats['placeholder_skipped']} placeholders, "
          f"{stats['duplicates']} duplicates, "
          f"{stats.get('no_labels_skipped', 0)} no labels")

    if args.dry_run:
        print("\n[DRY RUN] Would write to:", args.output_dir)
        # Print dimension distribution preview
        dim_counts = Counter()
        for rec, _ in clean_records:
            dim = assign_primary_dimension(rec)
            dim_counts[dim] += 1
        print("\nPrimary dimension distribution:")
        total = len(clean_records)
        for dim, count in dim_counts.most_common():
            print(f"  {dim}: {count} ({count/total*100:.1f}%)")

        # Entity type distribution
        type_counts = Counter()
        for rec, _ in clean_records:
            for label in rec.get("labels", []):
                raw = label.get("entity_type", "")
                canonical = canonicalize_entity_type(raw)
                type_counts[canonical] += 1
        print(f"\nUnique entity types: {len(type_counts)}")
        for t, c in type_counts.most_common():
            print(f"  {t}: {c}")

        return

    # Phase 2: Convert and write
    print(f"\nConverting to v2 schema...")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_file = args.output_dir / "pii_anon_v2.jsonl"

    dim_counts = Counter()
    domain_counts = Counter()
    lang_counts = Counter()
    entity_type_counts = Counter()
    difficulty_counts = Counter()
    total_annotations = 0

    with open(output_file, "w") as out:
        for i, (rec, source) in enumerate(clean_records):
            record_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"pii-anon-v2:{i}:{text_hash(rec['text'])}"))
            v2_rec = convert_record(rec, record_id)

            out.write(json.dumps(v2_rec, ensure_ascii=False) + "\n")

            dim_counts[v2_rec["primary_dimension"]] += 1
            domain_counts[v2_rec["domain"]] += 1
            lang_counts[v2_rec["language"]] += 1
            difficulty_counts[v2_rec["difficulty_level"]] += 1
            for ann in v2_rec["annotations"]:
                entity_type_counts[ann["entity_type"]] += 1
                total_annotations += 1

            if (i + 1) % 10000 == 0:
                print(f"  Converted {i + 1}/{len(clean_records)} records...")

    print(f"\nWrote {len(clean_records)} records to {output_file}")

    # Phase 3: Generate metadata
    metadata = {
        "dataset": "pii_anon_v2",
        "version": "2.0.0",
        "total_records": len(clean_records),
        "total_annotations": total_annotations,
        "unique_entity_types": len(entity_type_counts),
        "unique_languages": len(lang_counts),
        "generation_seed": 42,
        "primary_dimension_distribution": dict(dim_counts.most_common()),
        "domain_distribution": dict(domain_counts.most_common()),
        "language_distribution": dict(lang_counts.most_common()),
        "entity_type_distribution": dict(entity_type_counts.most_common()),
        "difficulty_distribution": dict(difficulty_counts.most_common()),
        "migration_stats": {
            "source_files": [str(f) for f in V1_FILES],
            "placeholder_records_excluded": stats["placeholder_skipped"],
            "duplicate_records_excluded": stats["duplicates"],
        },
    }

    metadata_file = args.output_dir / "pii_anon_v2.metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Wrote metadata to {metadata_file}")

    # Phase 4: Compress
    print("Compressing...")
    gz_file = args.output_dir / "pii_anon_v2.jsonl.gz"
    with open(output_file, "rb") as f_in, gzip.open(gz_file, "wb", compresslevel=6) as f_out:
        while chunk := f_in.read(1024 * 1024):
            f_out.write(chunk)
    gz_size = gz_file.stat().st_size / (1024 * 1024)
    print(f"Compressed to {gz_file} ({gz_size:.1f} MB)")

    # Print summary
    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"Total v2 records: {len(clean_records)}")
    print(f"Total annotations: {total_annotations}")
    print(f"Unique entity types: {len(entity_type_counts)}")
    print(f"Unique languages: {len(lang_counts)}")
    print(f"\nPrimary dimension distribution:")
    total = len(clean_records)
    for dim, count in dim_counts.most_common():
        print(f"  {dim}: {count} ({count/total*100:.1f}%)")
    print(f"\nDomain distribution:")
    for dom, count in domain_counts.most_common():
        print(f"  {dom}: {count} ({count/total*100:.1f}%)")
    print(f"\nDifficulty distribution:")
    for diff, count in difficulty_counts.most_common():
        print(f"  {diff}: {count} ({count/total*100:.1f}%)")
    print(f"\nTop 15 entity types:")
    for t, c in entity_type_counts.most_common(15):
        print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
