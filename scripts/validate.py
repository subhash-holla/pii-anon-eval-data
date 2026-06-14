#!/usr/bin/env python3
"""
Validate PII-Anon Evaluation Dataset for data quality.

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
    python scripts/validate.py [--input src/pii_anon_datasets/data/pii_anon.jsonl]
"""

import argparse
import gzip
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from _version import DATASET_VERSION
# Single source of truth for the entity-type set (fixes M1 drift): the canonical registry.
from pii_anon_datasets.taxonomy import (
    CANONICAL_ENTITY_TYPES as VALID_ENTITY_TYPES,
    CATEGORIES as VALID_CATEGORIES,
    SENSITIVITY_CLASSES as VALID_SENSITIVITIES,
)

SCHEMA_VERSION = "2.0.0"

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "src" / "pii_anon_datasets" / "data" / "pii_anon.jsonl.gz"
DEFAULT_LATTICE = REPO_ROOT / "src" / "pii_anon_datasets" / "data" / "eval_lattice.json"


def check_committed_cell_power(corpus_path: Path, lattice_path: Path) -> list[str]:
    """NFR-018 gate: every COMMITTED count-gated cell must hold ≥ its tiered positive target.

    Streams the corpus once via the shared lattice_audit (same counting the enrichment fill uses,
    so "what we fill" == "what we enforce"). Returns one error per under-powered committed cell.
    """
    import lattice_audit as audit
    if not Path(lattice_path).exists():
        return [f"[lattice] eval_lattice.json not found at {lattice_path}"]
    lattice = audit.load_lattice(lattice_path)
    counts = audit.audit_positives(corpus_path, lattice)
    errs = []
    for d in audit.deficits(counts, lattice):
        dims = "/".join(f"{k}={v}" for k, v in sorted(d["dimensions"].items()))
        errs.append(
            f"[lattice {d['id']}] UNDER-POWERED ({dims}): tier={d['tier']} "
            f"observed={d['observed']} < target={d['target_n']} (deficit {d['deficit']})"
        )
    return errs

PLACEHOLDER_RE = re.compile(r"\{\w+\}")

VALID_DIMENSIONS = {"entity_tracking", "multilingual", "context_preservation", "diverse_pii_types", "edge_cases", "format_variations", "temporal_consistency"}
VALID_DATA_TYPES = {"unstructured_text", "structured", "semi_structured", "code", "logs", "form", "table", "csv", "mixed"}
VALID_DOMAINS = {"general", "clinical", "financial", "legal", "technology", "government", "education", "mixed"}
VALID_DIFFICULTIES = {"easy", "moderate", "hard", "challenging"}
# VALID_ENTITY_TYPES / VALID_SENSITIVITIES / VALID_CATEGORIES are imported from
# pii_anon_datasets.taxonomy (the canonical registry) — single source of truth.

# v2.0.0 adds schema_version + the consolidated tier3_evaluation wrapper.
REQUIRED_FIELDS = {"record_id", "text", "version", "schema_version", "annotations", "language", "script", "primary_dimension", "dimensions", "data_type", "domain", "difficulty_level", "provenance"}


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
    if rec.get("version") != DATASET_VERSION:
        errors.append(f"[{rid}] Invalid version: {rec.get('version')} (expected {DATASET_VERSION})")

    # v2.0.0 schema checks
    if rec.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"[{rid}] Invalid schema_version: {rec.get('schema_version')} (expected {SCHEMA_VERSION})")
    if "tier3_evaluation" not in rec:
        errors.append(f"[{rid}] Missing tier3_evaluation (v2.0.0 consolidated wrapper)")

    # Annotations
    # NOTE: Tier 3 evaluation records (v1.3.0) include intentionally de-identified text
    # with zero PII annotations — they are the "after de-identification" reference for
    # evaluating LLM-based re-identification resistance.
    DEID_DOC_TYPES = {
        "paired_profile_pseudonymous",
        "esrc_target_signals_intact",
        "esrc_target_signals_removed",
        "esrc_signal_injection",
        "stylometric_obfuscation",
        "interest_diversification",
        "temporal_pattern_disruption",
        "paraphrased_content",
    }
    annotations = rec.get("annotations", [])
    if not annotations:
        if rec.get("document_type") in DEID_DOC_TYPES:
            return errors  # Empty annotations are intentional for Tier 3 records
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
    parser = argparse.ArgumentParser(description="Validate PII-Anon dataset")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--max-errors", type=int, default=100, help="Stop after N errors")
    parser.add_argument("--summary-only", action="store_true", help="Only print summary stats")
    parser.add_argument("--lattice", type=Path, default=DEFAULT_LATTICE,
                        help="Committed-lattice spec for the NFR-018 power gate")
    parser.add_argument("--no-power-gate", action="store_true",
                        help="Skip the committed-cell power gate (schema-only validation)")
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

    # Committed-cell power gate (NFR-018) — separate full pass (correct even if --max-errors broke early)
    if not args.no_power_gate:
        print("Running committed-cell power gate (NFR-018)...")
        lattice_errors = check_committed_cell_power(args.input, args.lattice)
        if lattice_errors:
            total_errors += len(lattice_errors)
            error_categories["committed_cell_underpowered"] += len(lattice_errors)
            print(f"  {len(lattice_errors)} under-powered committed cells (NFR-018 FAIL)")
            if not args.summary_only:
                all_errors.extend(lattice_errors)
        else:
            print("  All committed cells meet their tiered power target ✓")

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
