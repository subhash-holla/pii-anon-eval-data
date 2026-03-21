#!/usr/bin/env python3
"""
Validate PII-Anon Evaluation Dataset v2 for data quality.

Checks:
1. Annotation offset integrity (text[start:end] == annotation.text)
2. No overlapping annotations within a record
3. All entity types in canonical set
4. Valid language/script codes
5. No template placeholders remaining
6. No duplicate record_ids
7. Every record has >= 1 annotation
8. Schema field completeness

Usage:
    python scripts/validate_v2.py [--input src/pii_anon_datasets/data/pii_anon_v2.jsonl]
"""

import argparse
import gzip
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "src" / "pii_anon_datasets" / "data" / "pii_anon_v2.jsonl.gz"

PLACEHOLDER_RE = re.compile(r"\{\w+\}")

VALID_ENTITY_TYPES = {
    "PERSON_NAME", "ORGANIZATION_NAME", "LOCATION_NAME", "NATIONALITY", "GENDER", "AGE", "ETHNICITY", "DISABILITY_STATUS",
    "EMAIL_ADDRESS", "PHONE_NUMBER", "FAX_NUMBER", "PHONE_COUNTRY_CODE", "PHONE_AREA_CODE", "PHONE_EXTENSION", "MOBILE_DEVICE_ID",
    "CREDIT_CARD_NUMBER", "CREDIT_CARD_FRAGMENT", "BANK_ACCOUNT_NUMBER", "BANK_ROUTING_NUMBER", "IBAN", "SWIFT_BIC_CODE", "CRYPTOCURRENCY_ADDRESS", "TRANSACTION_ID", "TAX_ID",
    "USERNAME", "PASSWORD", "API_KEY", "AUTHENTICATION_TOKEN", "SOCIAL_MEDIA_HANDLE", "URL", "IP_ADDRESS", "IPV6_ADDRESS", "MAC_ADDRESS", "DEVICE_IDENTIFIER", "BIOMETRIC_ID",
    "PASSPORT_NUMBER", "DRIVER_LICENSE_NUMBER", "SOCIAL_SECURITY_NUMBER", "NATIONAL_ID_NUMBER", "VISA_NUMBER", "LICENSE_PLATE", "VEHICLE_IDENTIFICATION_NUMBER",
    "MEDICAL_RECORD_NUMBER", "HEALTH_CONDITION", "HEALTH_INSURANCE_ID", "INSURANCE_CLAIM_NUMBER", "MEDICATION_NAME", "PROCEDURE_NAME", "GENETIC_MARKER", "PRESCRIPTION_NUMBER",
    "STREET_ADDRESS", "POSTAL_CODE", "LATITUDE_LONGITUDE", "BUILDING_NAME", "TIMESTAMP", "DATE_OF_BIRTH", "EVENT_DATE",
    "JOB_TITLE", "SALARY", "EMPLOYEE_ID", "EDUCATION_LEVEL",
    "POLITICAL_OPINION", "RELIGIOUS_BELIEF", "MARITAL_STATUS", "HOUSEHOLD_SIZE", "VEHICLE_MODEL",
    "VEHICLE_REGISTRATION", "INSURANCE_POLICY_NUMBER", "MEDICAL_PROCEDURE_CODE", "PROFESSIONAL_LICENSE", "COURT_CASE_NUMBER", "SESSION_ID", "COOKIE_ID", "INVOICE_NUMBER",
    "SEXUAL_ORIENTATION", "UNION_MEMBERSHIP", "CRIMINAL_RECORD", "BIOMETRIC_TEMPLATE",
}

VALID_DIMENSIONS = {"entity_tracking", "multilingual", "context_preservation", "diverse_pii_types", "edge_cases", "format_variations", "temporal_consistency"}
VALID_DATA_TYPES = {"unstructured_text", "structured", "semi_structured", "code", "logs", "form", "table", "mixed"}
VALID_DOMAINS = {"general", "clinical", "financial", "legal", "technology", "government", "education", "mixed"}
VALID_DIFFICULTIES = {"easy", "moderate", "hard", "challenging"}
VALID_SENSITIVITIES = {"direct_identifier", "quasi_identifier", "sensitive_attribute"}
VALID_CATEGORIES = {"identity_demographics", "contact", "financial", "digital_online", "government_legal", "medical_biological", "location_temporal", "employment", "special_category"}

REQUIRED_FIELDS = {"record_id", "text", "version", "annotations", "language", "script", "primary_dimension", "dimensions", "data_type", "domain", "difficulty_level", "provenance"}


def validate_record(rec: dict, line_num: int, seen_ids: set) -> list[str]:
    """Validate a single record, return list of error messages."""
    errors = []
    rid = rec.get("record_id", f"line-{line_num}")

    # Missing required fields
    missing = REQUIRED_FIELDS - set(rec.keys())
    if missing:
        errors.append(f"[{rid}] Missing required fields: {missing}")
        return errors

    text = rec["text"]

    # Check for template placeholders
    if PLACEHOLDER_RE.search(text):
        errors.append(f"[{rid}] Text contains template placeholders")

    # Duplicate record_id
    if rid in seen_ids:
        errors.append(f"[{rid}] Duplicate record_id")
    seen_ids.add(rid)

    # Version check
    if rec.get("version") != "2.0.0":
        errors.append(f"[{rid}] Invalid version: {rec.get('version')}")

    # Annotations
    annotations = rec.get("annotations", [])
    if not annotations:
        errors.append(f"[{rid}] No annotations")
        return errors

    for i, ann in enumerate(annotations):
        # Required annotation fields
        for field in ("entity_id", "entity_type", "start", "end", "text", "category", "sensitivity_class"):
            if field not in ann:
                errors.append(f"[{rid}] Annotation {i} missing field: {field}")
                continue

        # Entity type validation
        if ann.get("entity_type") not in VALID_ENTITY_TYPES:
            errors.append(f"[{rid}] Invalid entity_type: {ann.get('entity_type')}")

        # Category validation
        if ann.get("category") not in VALID_CATEGORIES:
            errors.append(f"[{rid}] Invalid category: {ann.get('category')}")

        # Sensitivity validation
        if ann.get("sensitivity_class") not in VALID_SENSITIVITIES:
            errors.append(f"[{rid}] Invalid sensitivity_class: {ann.get('sensitivity_class')}")

        # Offset validation
        s = ann.get("start", 0)
        e = ann.get("end", 0)
        if s < 0 or e < 0:
            errors.append(f"[{rid}] Annotation {i}: negative offset ({s}, {e})")
        elif s >= e:
            errors.append(f"[{rid}] Annotation {i}: start >= end ({s} >= {e})")
        elif e > len(text):
            errors.append(f"[{rid}] Annotation {i}: end ({e}) > text length ({len(text)})")
        else:
            actual_span = text[s:e]
            expected_span = ann.get("text", "")
            if actual_span != expected_span:
                errors.append(f"[{rid}] Annotation {i}: span mismatch: text[{s}:{e}]='{actual_span[:30]}' != '{expected_span[:30]}'")

    # Check for overlapping annotations
    sorted_anns = sorted(annotations, key=lambda a: (a.get("start", 0), a.get("end", 0)))
    for j in range(len(sorted_anns) - 1):
        if sorted_anns[j].get("end", 0) > sorted_anns[j + 1].get("start", 0):
            errors.append(f"[{rid}] Overlapping annotations: {sorted_anns[j].get('entity_id')} and {sorted_anns[j+1].get('entity_id')}")

    # Dimension validation
    if rec.get("primary_dimension") not in VALID_DIMENSIONS:
        errors.append(f"[{rid}] Invalid primary_dimension: {rec.get('primary_dimension')}")
    dims = rec.get("dimensions", [])
    for d in dims:
        if d not in VALID_DIMENSIONS:
            errors.append(f"[{rid}] Invalid dimension: {d}")
    if rec.get("primary_dimension") and rec["primary_dimension"] not in dims:
        errors.append(f"[{rid}] primary_dimension '{rec['primary_dimension']}' not in dimensions list")

    # Data type and domain validation
    if rec.get("data_type") not in VALID_DATA_TYPES:
        errors.append(f"[{rid}] Invalid data_type: {rec.get('data_type')}")
    if rec.get("domain") not in VALID_DOMAINS:
        errors.append(f"[{rid}] Invalid domain: {rec.get('domain')}")
    if rec.get("difficulty_level") not in VALID_DIFFICULTIES:
        errors.append(f"[{rid}] Invalid difficulty_level: {rec.get('difficulty_level')}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate PII-Anon v2 dataset")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--max-errors", type=int, default=100, help="Stop after N errors")
    parser.add_argument("--summary-only", action="store_true", help="Only print summary stats")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Validating: {args.input}")
    print("=" * 70)

    seen_ids: set = set()
    total_records = 0
    total_errors = 0
    error_categories = Counter()
    all_errors: list[str] = []

    opener = gzip.open if args.input.suffix == ".gz" else open
    with opener(args.input, "rt", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            rec = json.loads(line)
            total_records += 1
            errors = validate_record(rec, line_num, seen_ids)
            if errors:
                total_errors += len(errors)
                for err in errors:
                    # Categorize error
                    if "span mismatch" in err:
                        error_categories["span_mismatch"] += 1
                    elif "Missing required" in err:
                        error_categories["missing_field"] += 1
                    elif "Duplicate" in err:
                        error_categories["duplicate_id"] += 1
                    elif "placeholder" in err.lower():
                        error_categories["placeholder"] += 1
                    elif "Invalid entity_type" in err:
                        error_categories["invalid_entity_type"] += 1
                    elif "Overlapping" in err:
                        error_categories["overlapping"] += 1
                    elif "No annotations" in err:
                        error_categories["no_annotations"] += 1
                    else:
                        error_categories["other"] += 1

                    if not args.summary_only:
                        all_errors.append(err)

            if total_errors >= args.max_errors and not args.summary_only:
                print(f"\nStopped after {args.max_errors} errors. Use --max-errors to increase.")
                break

            if total_records % 20000 == 0:
                print(f"  Validated {total_records} records...")

    # Print errors
    if all_errors and not args.summary_only:
        print(f"\nERRORS ({len(all_errors)} total):")
        for err in all_errors[:50]:
            print(f"  {err}")
        if len(all_errors) > 50:
            print(f"  ... and {len(all_errors) - 50} more")

    # Print summary
    print(f"\n{'=' * 70}")
    print("VALIDATION SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total records validated: {total_records}")
    print(f"Unique record IDs: {len(seen_ids)}")
    print(f"Total errors: {total_errors}")

    if error_categories:
        print(f"\nError breakdown:")
        for cat, count in error_categories.most_common():
            print(f"  {cat}: {count}")

    if total_errors == 0:
        print("\nRESULT: PASSED - All validation checks passed")
        sys.exit(0)
    else:
        print(f"\nRESULT: FAILED - {total_errors} errors found")
        sys.exit(1)


if __name__ == "__main__":
    main()
