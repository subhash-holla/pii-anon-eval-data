#!/usr/bin/env python3
"""
Fill the language×dimension coverage matrix so every cell has ≥30 records.

Reads the current canonical dataset, computes the coverage matrix,
then generates records for any cell below 30. Also introduces new
languages (52→60) and new entity types.

Usage:
    PYTHONPATH=. python scripts/generate_coverage_fill.py
    PYTHONPATH=. python scripts/generate_coverage_fill.py --min-per-cell 50
"""

import argparse
import gzip
import json
import random
import string
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "src" / "pii_anon_datasets" / "data" / "pii_anon.jsonl.gz"
DEFAULT_OUTPUT = REPO_ROOT / "src" / "pii_anon_datasets" / "data" / "pii_anon_coverage.jsonl"

SEED = 4242  # Different seed from generate_records.py

from scripts.generate_records import (
    PIIFactory, PIIValue, NAME_DB, build_record,
    ORGS, DIAGNOSES, MEDICATIONS, PROCEDURES,
)

# All 60 target languages
ALL_LANGUAGES = sorted(NAME_DB.keys()) + [
    # Languages from v1 that have no name DB — will use English names
    "no", "da", "fi", "cs", "ro", "hu", "sk", "hr", "lt", "et",
    "is", "af", "mt", "uk", "sr", "bg", "mk", "be",
    "zh-Hant", "el", "bn", "he", "ka", "hy",
    "fa", "ur", "ps", "ku", "ug", "mn",
    "lo", "km", "kk",
]
# Deduplicate and sort
ALL_LANGUAGES = sorted(set(ALL_LANGUAGES))

DIMENSIONS = [
    "diverse_pii_types",
    "multilingual",
    "entity_tracking",
    "edge_cases",
    "context_preservation",
    "temporal_consistency",
    "format_variations",
]


# ─── Dimension-specific template generators ─────────────────────────────────

def gen_diverse_pii(factory: PIIFactory, lang: str, rng: random.Random) -> dict:
    """Generate a diverse PII types record."""
    templates = [
        "Name: {name}, Email: {email}, Phone: {phone}, SSN: {ssn}, Address: {address}.",
        "Employee {name} (ID: {emp_id}) works as {job_title} at {org}. Contact: {email}, {phone}.",
        "{name} holds passport {passport} and driver's license {license}. DOB: {dob}. Phone: {phone}.",
        "Customer {name} (Email: {email}) placed order from {address}. Credit card: {cc}. Phone: {phone}.",
    ]
    template = rng.choice(templates)
    slots: dict[str, PIIValue] = {"name": factory.person_name()}
    if "{email}" in template: slots["email"] = factory.email(slots["name"].value)
    if "{phone}" in template: slots["phone"] = factory.phone()
    if "{ssn}" in template: slots["ssn"] = factory.ssn()
    if "{address}" in template: slots["address"] = factory.address()
    if "{emp_id}" in template: slots["emp_id"] = factory.employee_id()
    if "{job_title}" in template: slots["job_title"] = factory.job_title()
    if "{org}" in template: slots["org"] = factory.org()
    if "{passport}" in template: slots["passport"] = factory.passport()
    if "{license}" in template: slots["license"] = factory.driver_license()
    if "{dob}" in template: slots["dob"] = factory.dob()
    if "{cc}" in template: slots["cc"] = factory.credit_card()

    return build_record(template, slots, language=lang,
                        primary_dimension="diverse_pii_types", domain="general",
                        difficulty=rng.choice(["easy", "moderate", "hard"]),
                        rng=rng)


def gen_multilingual(factory: PIIFactory, lang: str, rng: random.Random) -> dict:
    """Generate a multilingual record."""
    templates = [
        "{name} — {email} — {phone} — {org}.",
        "Contact: {name}, Email: {email}, Phone: {phone}. Address: {address}.",
        "{name} ({job_title}) at {org}. Reach at {email} or {phone}.",
    ]
    template = rng.choice(templates)
    slots: dict[str, PIIValue] = {"name": factory.person_name()}
    if "{email}" in template: slots["email"] = factory.email(slots["name"].value)
    if "{phone}" in template: slots["phone"] = factory.phone()
    if "{org}" in template: slots["org"] = factory.org()
    if "{address}" in template: slots["address"] = factory.address()
    if "{job_title}" in template: slots["job_title"] = factory.job_title()

    return build_record(template, slots, language=lang,
                        primary_dimension="multilingual", domain="general",
                        difficulty="moderate", rng=rng)


def gen_entity_tracking(factory: PIIFactory, lang: str, rng: random.Random, idx: int) -> dict:
    """Generate an entity tracking record with coreference."""
    templates = [
        "Employee {name1} (ID: {emp_id}) works at {org}. Contact {name1} at {email}. {name1_formal}'s manager approved the request. Phone: {phone}.",
        "{name1} submitted a report. In the meeting, {name1_first} presented findings. {name1_formal} concluded that action was needed. Email: {email}. Phone: {phone}.",
        "Customer {name1} (Account: {acct}) reported an issue. Our agent spoke with {name1_formal}. {name1_first} can be reached at {phone} or {email}.",
    ]
    template = rng.choice(templates)
    cluster1 = f"cov_{idx}_p1"
    name1_full = factory.person_name(cluster_id=cluster1, variant="full_name")
    first = name1_full.value.split()[0] if " " in name1_full.value else name1_full.value
    last = name1_full.value.split()[-1] if " " in name1_full.value else name1_full.value
    formal_prefix = rng.choice(["Mr.", "Ms.", "Dr."])

    slots: dict[str, PIIValue] = {"name1": name1_full}
    if "{name1_first}" in template:
        slots["name1_first"] = PIIValue("PERSON_NAME", first, "identity_demographics",
                                         "direct_identifier", cluster_id=cluster1, mention_variant="first_name")
    if "{name1_formal}" in template:
        slots["name1_formal"] = PIIValue("PERSON_NAME", f"{formal_prefix} {last}", "identity_demographics",
                                          "direct_identifier", cluster_id=cluster1, mention_variant="formal")
    if "{email}" in template: slots["email"] = factory.email(name1_full.value)
    if "{phone}" in template: slots["phone"] = factory.phone()
    if "{org}" in template: slots["org"] = factory.org()
    if "{emp_id}" in template: slots["emp_id"] = factory.employee_id()
    if "{acct}" in template: slots["acct"] = factory.bank_account()

    rec = build_record(template, slots, language=lang,
                       primary_dimension="entity_tracking", domain="general",
                       difficulty=rng.choice(["moderate", "hard"]), rng=rng)

    # Fix entity tracking metadata
    chains: dict[str, list[str]] = {}
    for a in rec["annotations"]:
        cid = a.get("cluster_id")
        if cid:
            chains.setdefault(cid, []).append(a["entity_id"])
    coref_chains = [ids for ids in chains.values() if len(ids) > 1]
    rec["entity_tracking"] = {
        "num_repeated_entities": len(coref_chains),
        "coreference_chains": coref_chains,
        "tracking_difficulty": "complex" if len(coref_chains) > 1 else "moderate",
        "num_distinct_persons": len(chains),
    }
    return rec


def gen_edge_cases(factory: PIIFactory, lang: str, rng: random.Random) -> dict:
    """Generate an edge case/adversarial record."""
    case_type = rng.choice(["leetspeak", "mixed_case", "dense_pii", "format_noise"])
    name = factory.person_name()
    email = factory.email(name.value)
    phone = factory.phone()
    ssn = factory.ssn()

    if case_type == "leetspeak":
        template = "Usr {name} - em4il: {email} - ph0ne: {phone} - s0cial: {ssn}"
        adv_type, adv_diff, techniques = "leetspeak", "moderate", ["character_substitution"]
    elif case_type == "mixed_case":
        template = "CONTACT: {name} EMAIL: {email} PHONE: {phone} SSN: {ssn}"
        adv_type, adv_diff, techniques = "mixed_case", "mild", ["case_variation"]
    elif case_type == "dense_pii":
        template = "{name}|{email}|{phone}|{ssn}|{address}"
        adv_type, adv_diff, techniques = "dense_pii", "challenging", ["high_density"]
    else:
        template = "Name:   {name}  \t Email:\t{email}\n\nPhone:  {phone}  SSN: {ssn}"
        adv_type, adv_diff, techniques = "format_noise", "moderate", ["whitespace_variation"]

    slots: dict[str, PIIValue] = {"name": name, "email": email, "phone": phone, "ssn": ssn}
    if "{address}" in template: slots["address"] = factory.address()

    return build_record(template, slots, language=lang,
                        primary_dimension="edge_cases", domain="general",
                        difficulty=rng.choice(["hard", "challenging"]),
                        adversarial_type=adv_type,
                        adversarial_difficulty=adv_diff,
                        adversarial_techniques=techniques, rng=rng)


def gen_context_preservation(factory: PIIFactory, lang: str, rng: random.Random) -> dict:
    """Generate a context preservation record (longer text with semantic context)."""
    templates = [
        "Dear {name},\n\nThank you for your inquiry regarding account {acct}. Our records show your address as {address}. Please contact us at {phone} or {email} if this information is incorrect.\n\nBest regards,\n{org}",
        "Meeting Notes - {timestamp}\nAttendees: {name1}, {name2}\nOrganization: {org}\n\n{name1} presented the quarterly results. {name2} raised concerns about budget. Action items will be sent to {email1}.\n\nNext meeting: TBD.",
        "Dear {name},\n\nYour application for the {job_title} position at {org} has been received. We have your contact details: {email}, {phone}, and address {address}. Your employee ID will be {emp_id} upon onboarding.\n\nHR Department",
    ]
    template = rng.choice(templates)
    slots: dict[str, PIIValue] = {}
    if "{name}" in template: slots["name"] = factory.person_name()
    if "{name1}" in template: slots["name1"] = factory.person_name()
    if "{name2}" in template: slots["name2"] = factory.person_name()
    if "{email}" in template:
        ref = slots.get("name", slots.get("name1"))
        slots["email"] = factory.email(ref.value if ref else None)
    if "{email1}" in template:
        slots["email1"] = factory.email(slots["name1"].value)
    if "{phone}" in template: slots["phone"] = factory.phone()
    if "{address}" in template: slots["address"] = factory.address()
    if "{org}" in template: slots["org"] = factory.org()
    if "{acct}" in template: slots["acct"] = factory.bank_account()
    if "{timestamp}" in template: slots["timestamp"] = factory.timestamp()
    if "{job_title}" in template: slots["job_title"] = factory.job_title()
    if "{emp_id}" in template: slots["emp_id"] = factory.employee_id()

    return build_record(template, slots, language=lang,
                        primary_dimension="context_preservation", domain="general",
                        difficulty=rng.choice(["moderate", "hard"]), rng=rng)


def gen_temporal_consistency(factory: PIIFactory, lang: str, rng: random.Random) -> dict:
    """Generate a temporal consistency record."""
    name = factory.person_name()
    ts1 = factory.timestamp()
    ts2 = factory.timestamp()
    ip1 = factory.ip_address()
    ip2 = factory.ip_address()
    email = factory.email(name.value)

    text = (f"[{ts1.value}] {name.value} logged in from {ip1.value}. Email: {email.value}\n"
            f"[{ts2.value}] {name.value} changed password from {ip2.value}.")

    # Build annotations by scanning
    import re
    annotations = []
    # Find all name occurrences
    start = 0
    while True:
        idx = text.find(name.value, start)
        if idx == -1:
            break
        annotations.append({
            "entity_id": f"e{len(annotations)}",
            "entity_type": "PERSON_NAME", "start": idx, "end": idx + len(name.value),
            "text": name.value, "category": "identity_demographics",
            "sensitivity_class": "direct_identifier", "cluster_id": "p0", "mention_variant": None,
        })
        start = idx + len(name.value)

    # Find email
    idx = text.find(email.value)
    if idx != -1:
        annotations.append({
            "entity_id": f"e{len(annotations)}",
            "entity_type": "EMAIL_ADDRESS", "start": idx, "end": idx + len(email.value),
            "text": email.value, "category": "contact",
            "sensitivity_class": "direct_identifier", "cluster_id": None, "mention_variant": None,
        })

    # Find timestamps
    for match in re.finditer(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', text):
        annotations.append({
            "entity_id": f"e{len(annotations)}",
            "entity_type": "TIMESTAMP", "start": match.start(), "end": match.end(),
            "text": match.group(), "category": "location_temporal",
            "sensitivity_class": "quasi_identifier", "cluster_id": None, "mention_variant": None,
        })

    # Find IPs
    for match in re.finditer(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text):
        annotations.append({
            "entity_id": f"e{len(annotations)}",
            "entity_type": "IP_ADDRESS", "start": match.start(), "end": match.end(),
            "text": match.group(), "category": "digital_online",
            "sensitivity_class": "direct_identifier", "cluster_id": None, "mention_variant": None,
        })

    # Sort and re-ID
    annotations.sort(key=lambda a: (a["start"], a["end"]))
    for j, a in enumerate(annotations):
        a["entity_id"] = f"e{j}"

    from scripts.migrate_v1_to_v2 import SCRIPT_MAP, LANGUAGE_FAMILY_MAP, RESOURCE_LEVEL_MAP
    import uuid

    token_count = max(1, len(text.split()))
    dimensions = ["temporal_consistency"]
    if lang != "en":
        dimensions.append("multilingual")
    dimensions.sort()

    return {
        "record_id": str(uuid.uuid4()),
        "text": text,
        "version": "1.1.0",
        "annotations": annotations,
        "language": lang,
        "script": SCRIPT_MAP.get(lang, "Latn"),
        "language_family": LANGUAGE_FAMILY_MAP.get(lang, "unknown"),
        "resource_level": RESOURCE_LEVEL_MAP.get(lang, "low"),
        "primary_dimension": "temporal_consistency",
        "dimensions": dimensions,
        "data_type": "logs",
        "document_type": "audit_log",
        "domain": "technology",
        "difficulty_level": "hard",
        "context_length_tier": "short" if token_count <= 50 else "medium" if token_count <= 200 else "long",
        "token_count": token_count,
        "entity_tracking": {
            "num_repeated_entities": 1,
            "coreference_chains": [],
            "tracking_difficulty": "moderate",
            "num_distinct_persons": 1,
        },
        "adversarial": {"type": None, "difficulty": "clean", "techniques": []},
        "privacy_risk": {
            "quasi_identifiers": ["TIMESTAMP"],
            "reidentification_risk": "low",
            "k_anonymity_estimate": None,
        },
        "regulatory_domains": ["gdpr"],
        "query_context": None,
        "provenance": {"source_type": "synthetic", "license": "CC0-1.0", "generation_seed": SEED, "v1_record_id": None},
    }


def gen_format_variations(factory: PIIFactory, lang: str, rng: random.Random) -> dict:
    """Generate a format variation record (forms, tables, CSV)."""
    templates = [
        "FORM: Employee Registration\nName: {name}\nSSN: {ssn}\nEmail: {email}\nPhone: {phone}\nEmployer: {org}",
        "name,email,phone,ssn\n{name},{email},{phone},{ssn}",
        "| Field | Value |\n|-------|-------|\n| Name | {name} |\n| Email | {email} |\n| Phone | {phone} |\n| Org | {org} |",
    ]
    template = rng.choice(templates)
    name = factory.person_name()
    slots: dict[str, PIIValue] = {"name": name}
    if "{email}" in template: slots["email"] = factory.email(name.value)
    if "{phone}" in template: slots["phone"] = factory.phone()
    if "{ssn}" in template: slots["ssn"] = factory.ssn()
    if "{org}" in template: slots["org"] = factory.org()

    data_type = "table" if "|" in template else "form" if "FORM" in template else "csv"
    return build_record(template, slots, language=lang,
                        primary_dimension="format_variations", data_type=data_type,
                        domain="general", difficulty="moderate", rng=rng)


# Dimension → generator function mapping
DIM_GENERATORS = {
    "diverse_pii_types": lambda f, l, r, i: gen_diverse_pii(f, l, r),
    "multilingual": lambda f, l, r, i: gen_multilingual(f, l, r),
    "entity_tracking": gen_entity_tracking,
    "edge_cases": lambda f, l, r, i: gen_edge_cases(f, l, r),
    "context_preservation": lambda f, l, r, i: gen_context_preservation(f, l, r),
    "temporal_consistency": lambda f, l, r, i: gen_temporal_consistency(f, l, r),
    "format_variations": lambda f, l, r, i: gen_format_variations(f, l, r),
}


def compute_coverage(input_path: Path) -> dict[tuple[str, str], int]:
    """Compute current language×dimension cell counts."""
    matrix: dict[tuple[str, str], int] = defaultdict(int)
    opener = gzip.open if input_path.suffix == ".gz" else open
    with opener(input_path, "rt", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            lang = rec["language"]
            dim = rec["primary_dimension"]
            matrix[(lang, dim)] += 1
    return dict(matrix)


def main():
    parser = argparse.ArgumentParser(description="Fill language×dimension coverage matrix")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--min-per-cell", type=int, default=30)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    rng = random.Random(args.seed)

    # Step 1: Compute current coverage
    print(f"Reading current dataset from {args.input}...")
    matrix = compute_coverage(args.input)

    # Collect all languages present in dataset + new ones
    existing_langs = {k[0] for k in matrix.keys()}
    target_langs = existing_langs | set(NAME_DB.keys())
    print(f"Existing languages: {len(existing_langs)}")
    print(f"Target languages (with name DBs): {len(target_langs)}")

    # Step 2: Determine gaps
    total_needed = 0
    gaps: list[tuple[str, str, int]] = []
    for lang in sorted(target_langs):
        for dim in DIMENSIONS:
            current = matrix.get((lang, dim), 0)
            if current < args.min_per_cell:
                needed = args.min_per_cell - current
                gaps.append((lang, dim, needed))
                total_needed += needed

    print(f"\nCoverage gaps: {len(gaps)} cells need filling")
    print(f"Total records needed: {total_needed}")

    # Step 3: Generate records
    records = []
    idx = 0
    for lang, dim, needed in gaps:
        factory = PIIFactory(rng, lang)
        gen_fn = DIM_GENERATORS[dim]
        for _ in range(needed):
            try:
                rec = gen_fn(factory, lang, rng, idx)
                records.append(rec)
                idx += 1
            except Exception as e:
                print(f"  Error generating {lang}/{dim}: {e}")
                continue

    print(f"\nGenerated {len(records)} coverage fill records")

    # Step 4: Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {len(records)} records to {args.output}")

    # Stats
    dim_counts = Counter(r["primary_dimension"] for r in records)
    lang_counts = Counter(r["language"] for r in records)

    print(f"\nDimension distribution:")
    for d, c in dim_counts.most_common():
        print(f"  {d}: {c}")
    print(f"\nLanguage distribution (top 20):")
    for l, c in lang_counts.most_common(20):
        print(f"  {l}: {c}")
    print(f"  ... ({len(lang_counts)} languages total)")


if __name__ == "__main__":
    main()
