#!/usr/bin/env python3
"""
PR3 enrichment: Add query_context to ~5K records and refine adversarial metadata.

Usage:
    python scripts/enrich_pr3.py
"""

import gzip
import json
import random
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "pii_anon_datasets" / "data"
INPUT_GZ = DATA_DIR / "pii_anon_v2.jsonl.gz"
OUTPUT_GZ = DATA_DIR / "pii_anon_v2.jsonl.gz"
METADATA = DATA_DIR / "pii_anon_v2.metadata.json"

SEED = 42

# ─── Query templates by entity type ─────────────────────────────────────────

QUERY_TEMPLATES = {
    "PERSON_NAME": [
        "What is the name of the {role}?",
        "Who is mentioned in this document?",
        "Identify all person names in this text.",
        "What is the patient's name?",
        "Who submitted this report?",
    ],
    "EMAIL_ADDRESS": [
        "What is the email address on file?",
        "How can I contact this person by email?",
        "What email was used for registration?",
    ],
    "PHONE_NUMBER": [
        "What is the contact phone number?",
        "How can I reach this person by phone?",
        "What phone number is listed?",
    ],
    "STREET_ADDRESS": [
        "What is the address on file?",
        "Where does this person live?",
        "What is the mailing address?",
    ],
    "SOCIAL_SECURITY_NUMBER": [
        "What is the SSN listed?",
        "What social security number is in this document?",
    ],
    "DATE_OF_BIRTH": [
        "What is the date of birth?",
        "When was this person born?",
    ],
    "MEDICAL_RECORD_NUMBER": [
        "What is the patient's MRN?",
        "What medical record number is referenced?",
    ],
    "HEALTH_CONDITION": [
        "What diagnosis is documented?",
        "What medical condition does the patient have?",
    ],
    "CREDIT_CARD_NUMBER": [
        "What credit card number is on file?",
        "What payment card was used?",
    ],
    "BANK_ACCOUNT_NUMBER": [
        "What bank account number is listed?",
        "What is the account number for the transfer?",
    ],
    "PASSPORT_NUMBER": [
        "What is the passport number?",
        "What travel document ID is listed?",
    ],
    "ORGANIZATION_NAME": [
        "What organization is mentioned?",
        "What company is referenced in this document?",
    ],
    "IP_ADDRESS": [
        "What IP address was used?",
        "What is the source IP?",
    ],
    "API_KEY": [
        "What API key is embedded in this code?",
        "What credentials are exposed?",
    ],
    "EMPLOYEE_ID": [
        "What is the employee ID?",
        "What staff identifier is listed?",
    ],
}

ROLES = ["patient", "applicant", "customer", "employee", "defendant", "claimant", "user"]


def add_query_context(records: list[dict], rng: random.Random, target_count: int = 5000) -> int:
    """Add query_context to records that have relevant entity types."""
    eligible = []
    for i, rec in enumerate(records):
        if rec.get("query_context"):
            continue
        entity_types = {a["entity_type"] for a in rec.get("annotations", [])}
        matching_types = entity_types & set(QUERY_TEMPLATES.keys())
        if len(matching_types) >= 2:
            eligible.append((i, matching_types))

    rng.shuffle(eligible)
    selected = eligible[:target_count]

    enriched = 0
    for idx, matching_types in selected:
        rec = records[idx]
        annotations = rec["annotations"]
        entity_types = list(matching_types)

        # Pick 1-2 entity types to query about
        query_types = rng.sample(entity_types, min(2, len(entity_types)))
        primary_type = query_types[0]

        # Select query template
        templates = QUERY_TEMPLATES[primary_type]
        query = rng.choice(templates)
        if "{role}" in query:
            query = query.replace("{role}", rng.choice(ROLES))

        # Find relevant entity IDs
        relevant_ids = [
            a["entity_id"] for a in annotations
            if a["entity_type"] in query_types
        ]

        rec["query_context"] = {
            "query": query,
            "relevant_entity_ids": relevant_ids,
        }

        # Add context_preservation to dimensions if not present
        if "context_preservation" not in rec.get("dimensions", []):
            rec["dimensions"] = sorted(set(rec.get("dimensions", []) + ["context_preservation"]))

        enriched += 1

    return enriched


def refine_adversarial_metadata(records: list[dict]) -> int:
    """Ensure all edge_cases records have structured adversarial metadata."""
    refined = 0
    for rec in records:
        if rec.get("primary_dimension") != "edge_cases":
            continue
        adv = rec.get("adversarial", {})
        if adv.get("type") is not None:
            continue

        # Infer adversarial type from text characteristics
        text = rec.get("text", "")
        if any(c in text for c in ["0" , "4", "3"]) and any(w in text.lower() for w in ["em4il", "ph0ne", "s0cial", "usr"]):
            adv_type = "leetspeak"
            difficulty = "moderate"
            techniques = ["character_substitution"]
        elif "***" in text or "XXX" in text:
            adv_type = "partial_redaction"
            difficulty = "hard"
            techniques = ["partial_masking"]
        elif text == text.upper() and len(text) > 20:
            adv_type = "mixed_case"
            difficulty = "mild"
            techniques = ["case_variation"]
        elif "|" in text and text.count("|") >= 3:
            adv_type = "dense_pii"
            difficulty = "challenging"
            techniques = ["high_density"]
        elif "\t" in text or "  " in text:
            adv_type = "format_noise"
            difficulty = "moderate"
            techniques = ["whitespace_variation"]
        else:
            adv_type = "mixed"
            difficulty = "moderate"
            techniques = ["mixed_patterns"]

        rec["adversarial"] = {
            "type": adv_type,
            "difficulty": difficulty,
            "techniques": techniques,
        }
        refined += 1

    return refined


def compute_k_anonymity_estimates(records: list[dict]) -> int:
    """Add k-anonymity estimates to privacy_risk based on quasi-identifier count."""
    updated = 0
    for rec in records:
        pr = rec.get("privacy_risk", {})
        if pr.get("k_anonymity_estimate") is not None:
            continue

        quasi_ids = pr.get("quasi_identifiers", [])
        n_quasi = len(quasi_ids)

        if n_quasi == 0:
            k_est = None
        elif n_quasi == 1:
            k_est = 100
        elif n_quasi == 2:
            k_est = 20
        elif n_quasi == 3:
            k_est = 5
        else:
            k_est = 2

        pr["k_anonymity_estimate"] = k_est
        rec["privacy_risk"] = pr
        updated += 1

    return updated


def main():
    rng = random.Random(SEED)

    # Load all records
    print("Loading canonical dataset...")
    records = []
    with gzip.open(INPUT_GZ, "rt", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    print(f"  Loaded {len(records)} records")

    # Enrich
    print("\nAdding query_context...")
    n_query = add_query_context(records, rng, target_count=5000)
    print(f"  Added query_context to {n_query} records")

    print("\nRefining adversarial metadata...")
    n_adv = refine_adversarial_metadata(records)
    print(f"  Refined adversarial metadata on {n_adv} records")

    print("\nComputing k-anonymity estimates...")
    n_kanon = compute_k_anonymity_estimates(records)
    print(f"  Added k-anonymity estimates to {n_kanon} records")

    # Write back
    print("\nWriting enriched dataset...")
    with gzip.open(OUTPUT_GZ, "wt", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Update metadata
    print("Updating metadata...")
    query_count = sum(1 for r in records if r.get("query_context"))
    adv_count = sum(1 for r in records if r.get("adversarial", {}).get("type"))
    kanon_count = sum(1 for r in records if r.get("privacy_risk", {}).get("k_anonymity_estimate") is not None)

    dim_counts = Counter(r["primary_dimension"] for r in records)
    lang_counts = Counter(r["language"] for r in records)
    domain_counts = Counter(r["domain"] for r in records)
    diff_counts = Counter(r["difficulty_level"] for r in records)
    entity_type_counts = Counter()
    category_counts = Counter()
    total_annotations = 0
    for r in records:
        for a in r["annotations"]:
            entity_type_counts[a["entity_type"]] += 1
            category_counts[a["category"]] += 1
            total_annotations += 1

    script_counts = Counter(r.get("script", "unknown") for r in records)
    data_type_counts = Counter(r.get("data_type", "unknown") for r in records)

    metadata = {
        "version": "2.0.0",
        "total_records": len(records),
        "total_annotations": total_annotations,
        "entity_types": len(entity_type_counts),
        "entity_categories": len(category_counts),
        "languages": len(lang_counts),
        "writing_scripts": len(script_counts),
        "evaluation_dimensions": len(dim_counts),
        "query_aware_records": query_count,
        "adversarial_typed_records": adv_count,
        "k_anonymity_estimated_records": kanon_count,
        "distributions": {
            "by_dimension": dict(dim_counts.most_common()),
            "by_language": dict(lang_counts.most_common()),
            "by_domain": dict(domain_counts.most_common()),
            "by_difficulty": dict(diff_counts.most_common()),
            "by_entity_type": dict(entity_type_counts.most_common()),
            "by_category": dict(category_counts.most_common()),
            "by_script": dict(script_counts.most_common()),
            "by_data_type": dict(data_type_counts.most_common()),
        },
    }

    with open(METADATA, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"PR3 ENRICHMENT SUMMARY")
    print(f"{'='*60}")
    print(f"Total records:              {len(records):,}")
    print(f"Query-aware records:        {query_count:,}")
    print(f"Adversarial-typed records:  {adv_count:,}")
    print(f"K-anonymity estimated:      {kanon_count:,}")
    print("Done!")


if __name__ == "__main__":
    main()
