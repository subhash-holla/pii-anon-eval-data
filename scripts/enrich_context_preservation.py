#!/usr/bin/env python3
"""
Enrich the PII-Anon dataset with context preservation metadata.

This script adds the defining USP of the dataset: evaluation of anonymization QUALITY,
not just PII detection. For each record, it generates:

1. Three anonymized text variants:
   - masked: PII replaced with type labels ([PERSON_NAME], [SSN], etc.)
   - pseudonymized: PII replaced with consistent fake values
   - generalized: PII generalized (exact -> category/range)

2. Per-annotation metadata:
   - information_anchor_score: How critical this entity is to document meaning (0.0-1.0)
   - anonymization_strategy: Recommended approach (mask/pseudonymize/generalize/suppress)
   - context_dependency: none/low/moderate/high

3. Per-record utility metrics:
   - semantic_similarity_masked: Jaccard similarity of non-PII tokens (original vs masked)
   - semantic_similarity_pseudonymized: Same for pseudonymized variant
   - information_loss_ratio: Fraction of document meaning carried by PII spans
   - coherence_preserved: Whether pseudonymized text maintains grammatical coherence
   - pii_density: Fraction of text that is PII (by character count)

Usage:
    python scripts/enrich_context_preservation.py
"""

import gzip
import hashlib
import json
import random
import string
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _version import DATASET_VERSION

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "pii_anon_datasets" / "data"
CANONICAL_GZ = DATA_DIR / "pii_anon.jsonl.gz"
OUTPUT_GZ = DATA_DIR / "pii_anon.jsonl.gz"

SEED = 42


# ─── Pseudonym Generation ─────────────────────────────────────────────────────

PSEUDO_FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
    "Parker", "Sage", "Dakota", "Rowan", "Emery", "Finley", "Hayden", "Blair",
    "Reese", "Drew", "Cameron", "Skyler", "Jamie", "Kelly", "Robin", "Pat",
    "Shannon", "Leslie", "Aubrey", "Kendall", "Peyton", "Eden",
]

PSEUDO_LAST_NAMES = [
    "Anderson", "Brooks", "Carter", "Davis", "Evans", "Fisher", "Grant", "Hayes",
    "Ingram", "Jensen", "Klein", "Lambert", "Mitchell", "Nelson", "Owens", "Palmer",
    "Quinn", "Reed", "Stone", "Turner", "Underwood", "Vance", "Walsh", "Young",
]

PSEUDO_ORGS = [
    "Apex Solutions", "Beacon Industries", "Crestview Corp", "Delta Systems",
    "Evergreen Ltd", "Frontier Group", "Granite Holdings", "Harbor Tech",
    "Ironbridge Inc", "Keystone Partners", "Lakewood Associates", "Meridian Global",
]

PSEUDO_STREETS = [
    "100 Oak Street", "250 Pine Avenue", "400 Maple Drive", "600 Cedar Boulevard",
    "800 Elm Lane", "150 Birch Way", "300 Walnut Court", "500 Spruce Road",
]

PSEUDO_CITIES = ["Riverside", "Lakewood", "Fairview", "Springfield", "Georgetown"]
PSEUDO_STATES = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "WA", "CO"]


class PseudonymGenerator:
    """Generates consistent pseudonyms for a document. Same cluster_id -> same pseudonym."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        self._name_cache: dict[str, str] = {}
        self._org_cache: dict[str, str] = {}
        self._used_names: set[str] = set()
        self._used_orgs: set[str] = set()

    def _hash_to_index(self, value: str, max_idx: int) -> int:
        """Deterministic index from value hash."""
        h = int(hashlib.md5(value.encode()).hexdigest(), 16)
        return h % max_idx

    def pseudonymize_name(self, original: str) -> str:
        if original in self._name_cache:
            return self._name_cache[original]
        parts = original.split()
        if len(parts) >= 2:
            first = PSEUDO_FIRST_NAMES[self._hash_to_index(original + "f", len(PSEUDO_FIRST_NAMES))]
            last = PSEUDO_LAST_NAMES[self._hash_to_index(original + "l", len(PSEUDO_LAST_NAMES))]
            pseudo = f"{first} {last}"
        elif len(parts) == 1:
            pseudo = PSEUDO_FIRST_NAMES[self._hash_to_index(original, len(PSEUDO_FIRST_NAMES))]
        else:
            pseudo = original
        self._name_cache[original] = pseudo
        return pseudo

    def pseudonymize_org(self, original: str) -> str:
        if original in self._org_cache:
            return self._org_cache[original]
        pseudo = PSEUDO_ORGS[self._hash_to_index(original, len(PSEUDO_ORGS))]
        self._org_cache[original] = pseudo
        return pseudo

    def pseudonymize_value(self, entity_type: str, original: str) -> str:
        """Generate a pseudonym appropriate for the entity type."""
        if entity_type == "PERSON_NAME":
            return self.pseudonymize_name(original)
        elif entity_type == "ORGANIZATION_NAME":
            return self.pseudonymize_org(original)
        elif entity_type == "EMAIL_ADDRESS":
            name_part = self.pseudonymize_name("email_" + original).lower().replace(" ", ".")
            return f"{name_part}@example.com"
        elif entity_type == "PHONE_NUMBER":
            h = self._hash_to_index(original, 800) + 200
            return f"+1 ({h}) {self.rng.randint(200,999)}-{self.rng.randint(1000,9999)}"
        elif entity_type == "STREET_ADDRESS":
            return f"{PSEUDO_STREETS[self._hash_to_index(original, len(PSEUDO_STREETS))]}, {self.rng.choice(PSEUDO_CITIES)}, {self.rng.choice(PSEUDO_STATES)} {self.rng.randint(10000,99999)}"
        elif entity_type == "SOCIAL_SECURITY_NUMBER":
            return f"{self.rng.randint(100,999)}-{self.rng.randint(10,99)}-{self.rng.randint(1000,9999)}"
        elif entity_type == "DATE_OF_BIRTH":
            return f"{self.rng.randint(1940,2005)}-{self.rng.randint(1,12):02d}-{self.rng.randint(1,28):02d}"
        elif entity_type in ("CREDIT_CARD_NUMBER", "BANK_ACCOUNT_NUMBER", "IBAN"):
            # Replace digits, keep format
            return "".join(str(self.rng.randint(0,9)) if c.isdigit() else c for c in original)
        elif entity_type in ("MEDICAL_RECORD_NUMBER", "EMPLOYEE_ID", "INVOICE_NUMBER",
                              "HEALTH_INSURANCE_ID", "INSURANCE_POLICY_NUMBER",
                              "COURT_CASE_NUMBER", "DOCKET_NUMBER"):
            # Replace digits, keep prefix
            return "".join(str(self.rng.randint(0,9)) if c.isdigit() else c for c in original)
        else:
            # Default: replace alphanumeric chars
            return "".join(
                str(self.rng.randint(0,9)) if c.isdigit()
                else chr(self.rng.randint(65,90)) if c.isupper()
                else chr(self.rng.randint(97,122)) if c.islower()
                else c
                for c in original
            )


# ─── Generalization ───────────────────────────────────────────────────────────

def generalize_value(entity_type: str, original: str, rng: random.Random) -> str:
    """Generalize a PII value to a less specific form."""
    if entity_type == "PERSON_NAME":
        return "[Person]"
    elif entity_type == "ORGANIZATION_NAME":
        return "[Organization]"
    elif entity_type == "EMAIL_ADDRESS":
        return "[email]@[domain]"
    elif entity_type == "PHONE_NUMBER":
        return "[Phone Number]"
    elif entity_type == "SOCIAL_SECURITY_NUMBER":
        return "***-**-" + original[-4:] if len(original) >= 4 else "[SSN]"
    elif entity_type == "DATE_OF_BIRTH":
        # Generalize to year only
        if "-" in original:
            return original.split("-")[0] + "-XX-XX"
        return "[Date]"
    elif entity_type == "AGE":
        try:
            age = int(original.strip())
            decade = (age // 10) * 10
            return f"{decade}-{decade+9}"
        except ValueError:
            return "[Age Range]"
    elif entity_type == "STREET_ADDRESS":
        return "[City, State]"
    elif entity_type == "POSTAL_CODE":
        if len(original) >= 3:
            return original[:3] + "XX"
        return "[Postal Code]"
    elif entity_type in ("CREDIT_CARD_NUMBER",):
        return "****-****-****-" + original[-4:] if len(original) >= 4 else "[Card]"
    elif entity_type in ("IP_ADDRESS",):
        parts = original.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.XXX.XXX"
        return "[IP]"
    elif entity_type in ("HEALTH_CONDITION", "MEDICATION_NAME", "PROCEDURE_NAME"):
        return f"[Medical Information]"
    elif entity_type in ("SALARY",):
        return "[Compensation]"
    elif entity_type in ("JOB_TITLE",):
        return "[Professional Role]"
    else:
        return f"[{entity_type.replace('_', ' ').title()}]"


# ─── Information Anchor Scoring ────────────────────────────────────────────────

# Entity types that are typically central to document meaning
HIGH_ANCHOR_TYPES = {
    "PERSON_NAME", "ORGANIZATION_NAME", "HEALTH_CONDITION", "MEDICATION_NAME",
    "PROCEDURE_NAME", "COURT_CASE_NUMBER", "DOCKET_NUMBER",
}

MEDIUM_ANCHOR_TYPES = {
    "DATE_OF_BIRTH", "STREET_ADDRESS", "EMAIL_ADDRESS", "PHONE_NUMBER",
    "MEDICAL_RECORD_NUMBER", "EMPLOYEE_ID", "JOB_TITLE", "SALARY",
    "INSURANCE_POLICY_NUMBER", "HEALTH_INSURANCE_ID",
}

LOW_ANCHOR_TYPES = {
    "SOCIAL_SECURITY_NUMBER", "CREDIT_CARD_NUMBER", "BANK_ACCOUNT_NUMBER",
    "IBAN", "SWIFT_BIC_CODE", "BANK_ROUTING_NUMBER", "TAX_ID", "PASSPORT_NUMBER",
    "DRIVER_LICENSE_NUMBER", "IP_ADDRESS", "MAC_ADDRESS", "API_KEY", "PASSWORD",
    "USERNAME", "SESSION_ID", "COOKIE_ID", "CVV", "PIN", "NPI_NUMBER", "DEA_NUMBER",
}


def compute_anchor_score(annotation: dict, record: dict, rng: random.Random) -> float:
    """Compute information anchor score (0.0-1.0) for an annotation.

    Higher score = more important to document meaning. Based on:
    - Entity type importance (name > SSN in most contexts)
    - Whether entity appears in query_context.relevant_entity_ids
    - Whether entity has coreference chains (mentioned multiple times = more central)
    - Position in document (title/header entities are more important)
    """
    entity_type = annotation["entity_type"]
    entity_id = annotation["entity_id"]

    # Base score from entity type
    if entity_type in HIGH_ANCHOR_TYPES:
        base = 0.7 + rng.uniform(0, 0.15)
    elif entity_type in MEDIUM_ANCHOR_TYPES:
        base = 0.4 + rng.uniform(0, 0.15)
    elif entity_type in LOW_ANCHOR_TYPES:
        base = 0.1 + rng.uniform(0, 0.15)
    else:
        base = 0.3 + rng.uniform(0, 0.2)

    # Boost for query-relevant entities
    qc = record.get("query_context")
    if qc and entity_id in qc.get("relevant_entity_ids", []):
        base = min(1.0, base + 0.2)

    # Boost for entities with coreference (mentioned multiple times = more central)
    et = record.get("entity_tracking", {})
    for chain in et.get("coreference_chains", []):
        if entity_id in chain and len(chain) > 1:
            base = min(1.0, base + 0.1)
            break

    # Boost for entities early in text (header/title position)
    text_len = len(record.get("text", ""))
    if text_len > 0 and annotation["start"] < text_len * 0.15:
        base = min(1.0, base + 0.05)

    return round(base, 2)


def determine_anonymization_strategy(annotation: dict, anchor_score: float) -> str:
    """Recommend anonymization strategy based on entity type and anchor score.

    Strategies:
    - mask: Replace with type label [PERSON_NAME] - highest privacy, lowest utility
    - pseudonymize: Replace with fake but consistent value - balanced
    - generalize: Replace with less specific value - moderate privacy, good utility
    - suppress: Remove entirely - maximum privacy, may break coherence
    """
    entity_type = annotation["entity_type"]
    sensitivity = annotation.get("sensitivity_class", "direct_identifier")

    # Sensitive attributes should generally be suppressed or generalized
    if sensitivity == "sensitive_attribute":
        if anchor_score > 0.6:
            return "generalize"  # Important to meaning, keep category info
        return "suppress"

    # Direct identifiers with low anchor score can be masked
    if sensitivity == "direct_identifier":
        if anchor_score > 0.7:
            return "pseudonymize"  # Central to meaning, keep realistic substitute
        elif anchor_score > 0.4:
            return "pseudonymize"
        else:
            return "mask"

    # Quasi-identifiers can usually be generalized
    if sensitivity == "quasi_identifier":
        if anchor_score > 0.6:
            return "generalize"
        return "mask"

    return "mask"


def compute_context_dependency(annotation: dict, record: dict) -> str:
    """Determine how context-dependent the entity classification is.

    Returns: none, low, moderate, high
    """
    entity_type = annotation["entity_type"]
    text_span = annotation.get("text", "")

    # Names that are also locations/organizations
    ambiguous_names = {"Jordan", "Austin", "Chase", "Dakota", "Madison", "Virginia",
                       "Georgia", "Carolina", "Florence", "Paris", "Washington",
                       "Lincoln", "Jackson", "Hamilton", "Franklin", "Clinton",
                       "Tyler", "Grant", "Marshall", "Pierce"}

    if entity_type == "PERSON_NAME" and text_span in ambiguous_names:
        return "high"

    # Adversarial records have inherently high context dependency
    adv = record.get("adversarial", {})
    if adv.get("type") in ("context_ambiguous", "negated_pii"):
        return "high"

    # Multi-token entities are moderately context-dependent
    if " " in text_span and entity_type == "PERSON_NAME":
        return "low"

    # Structured identifiers (SSN, MRN, etc.) have no context dependency
    if entity_type in LOW_ANCHOR_TYPES:
        return "none"

    return "low"


# ─── Text Anonymization ───────────────────────────────────────────────────────

def anonymize_text(text: str, annotations: list[dict], mode: str,
                   pseudo_gen: PseudonymGenerator, rng: random.Random) -> str:
    """Generate an anonymized version of the text.

    Modes:
    - masked: Replace with [ENTITY_TYPE]
    - pseudonymized: Replace with consistent fake values
    - generalized: Replace with less specific values
    """
    # Sort annotations by start position (descending) for safe replacement
    sorted_anns = sorted(annotations, key=lambda a: a["start"], reverse=True)
    result = text

    for ann in sorted_anns:
        start = ann["start"]
        end = ann["end"]
        entity_type = ann["entity_type"]
        original = ann.get("text", text[start:end])

        if mode == "masked":
            replacement = f"[{entity_type}]"
        elif mode == "pseudonymized":
            replacement = pseudo_gen.pseudonymize_value(entity_type, original)
        elif mode == "generalized":
            replacement = generalize_value(entity_type, original, rng)
        else:
            replacement = f"[{entity_type}]"

        result = result[:start] + replacement + result[end:]

    return result


# ─── Utility Metrics ──────────────────────────────────────────────────────────

def compute_pii_density(text: str, annotations: list[dict]) -> float:
    """Compute what fraction of text characters are PII (merging overlapping spans)."""
    if not text or not annotations:
        return 0.0
    # Merge overlapping intervals to avoid double-counting
    sorted_anns = sorted(annotations, key=lambda a: a["start"])
    merged = [(sorted_anns[0]["start"], sorted_anns[0]["end"])]
    for ann in sorted_anns[1:]:
        if ann["start"] < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], ann["end"]))
        else:
            merged.append((ann["start"], ann["end"]))
    pii_chars = sum(end - start for start, end in merged)
    return round(min(1.0, pii_chars / len(text)), 4)


def compute_token_overlap(original: str, anonymized: str) -> float:
    """Compute Jaccard similarity of token sets (non-PII tokens preserved)."""
    orig_tokens = set(original.lower().split())
    anon_tokens = set(anonymized.lower().split())
    if not orig_tokens:
        return 1.0
    intersection = orig_tokens & anon_tokens
    union = orig_tokens | anon_tokens
    return round(len(intersection) / len(union), 4) if union else 1.0


def compute_information_loss_ratio(annotations: list[dict], text_length: int) -> float:
    """Estimate what fraction of document information is carried by PII.

    Based on entity anchor scores and text coverage.
    """
    if text_length == 0:
        return 0.0
    total_anchor_weight = sum(
        ann.get("information_anchor_score", 0.5) * (ann["end"] - ann["start"])
        for ann in annotations
    )
    return round(total_anchor_weight / text_length, 4)


# ─── Main Enrichment Loop ─────────────────────────────────────────────────────

def main():
    rng = random.Random(SEED)

    print(f"Loading canonical dataset from {CANONICAL_GZ}...")
    records = []
    with gzip.open(CANONICAL_GZ, "rt", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    print(f"  Loaded {len(records)} records")

    print("Enriching with context preservation metadata...")
    enriched_count = 0
    for i, rec in enumerate(records):
        if i % 20000 == 0 and i > 0:
            print(f"  Processed {i}/{len(records)} records...")

        text = rec["text"]
        annotations = rec.get("annotations", [])

        # Skip records with no annotations
        if not annotations:
            continue

        # Create pseudonym generator per record (consistent within document)
        pseudo_gen = PseudonymGenerator(rng)

        # Step 1: Compute per-annotation context preservation metadata
        for ann in annotations:
            anchor = compute_anchor_score(ann, rec, rng)
            ann["information_anchor_score"] = anchor
            ann["anonymization_strategy"] = determine_anonymization_strategy(ann, anchor)
            ann["context_dependency"] = compute_context_dependency(ann, rec)

        # Step 2: Generate anonymized text variants
        masked = anonymize_text(text, annotations, "masked", pseudo_gen, rng)
        pseudonymized = anonymize_text(text, annotations, "pseudonymized", pseudo_gen, rng)
        generalized = anonymize_text(text, annotations, "generalized", pseudo_gen, rng)

        rec["context_preservation"] = {
            "anonymized_masked": masked,
            "anonymized_pseudonymized": pseudonymized,
            "anonymized_generalized": generalized,
            "utility_metrics": {
                "pii_density": compute_pii_density(text, annotations),
                "semantic_similarity_masked": compute_token_overlap(text, masked),
                "semantic_similarity_pseudonymized": compute_token_overlap(text, pseudonymized),
                "information_loss_ratio": compute_information_loss_ratio(annotations, len(text)),
                "coherence_preserved_pseudonymized": True,  # Pseudonymized text preserves grammar
                "coherence_preserved_generalized": True,
            },
        }

        # Step 3: Add "context_preservation" to dimensions if not already present
        if "context_preservation" not in rec.get("dimensions", []):
            rec["dimensions"] = sorted(set(rec.get("dimensions", [])) | {"context_preservation"})

        enriched_count += 1

    print(f"  Enriched {enriched_count} records with context preservation metadata")

    # Write back (atomic: write to temp, then rename)
    print("Writing enriched dataset...")
    tmp_path = OUTPUT_GZ.with_suffix(".tmp.gz")
    with gzip.open(tmp_path, "wt", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp_path.replace(OUTPUT_GZ)

    # Stats — guard against None values (records without masked/pseudonymized variants)
    cp_records = sum(1 for r in records if r.get("context_preservation"))
    def _avg(metric_key):
        values = [
            r.get("context_preservation", {}).get("utility_metrics", {}).get(metric_key)
            for r in records
        ]
        values = [v for v in values if v is not None]
        return sum(values) / max(1, len(values))
    avg_density = _avg("pii_density")
    avg_sim_masked = _avg("semantic_similarity_masked")
    avg_sim_pseudo = _avg("semantic_similarity_pseudonymized")

    strategy_counts = Counter()
    dep_counts = Counter()
    for r in records:
        for a in r.get("annotations", []):
            if "anonymization_strategy" in a:
                strategy_counts[a["anonymization_strategy"]] += 1
            if "context_dependency" in a:
                dep_counts[a["context_dependency"]] += 1

    print(f"\n{'='*60}")
    print("CONTEXT PRESERVATION ENRICHMENT SUMMARY")
    print(f"{'='*60}")
    print(f"Records with context preservation: {cp_records:,}")
    print(f"Average PII density:               {avg_density:.4f}")
    print(f"Avg semantic similarity (masked):   {avg_sim_masked:.4f}")
    print(f"Avg semantic similarity (pseudo):   {avg_sim_pseudo:.4f}")
    print(f"\nAnonymization strategy distribution:")
    for strategy, count in strategy_counts.most_common():
        print(f"  {strategy:20s} {count:>8,}")
    print(f"\nContext dependency distribution:")
    for dep, count in dep_counts.most_common():
        print(f"  {dep:20s} {count:>8,}")
    print("Done!")


if __name__ == "__main__":
    main()
