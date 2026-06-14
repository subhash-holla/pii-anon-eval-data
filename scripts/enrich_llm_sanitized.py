#!/usr/bin/env python3
"""
Add the 4th anonymized variant: anonymized_llm_sanitized (v1.3.0).

Unlike the 3 existing variants (masked/pseudonymized/generalized) which only
remove direct PII entities, anonymized_llm_sanitized ALSO removes behavioral
signals (writing style, professional jargon, location refs, etc.) — simulating
defenses against LLM-based re-identification (Lermen et al. 2026).

This script must run AFTER:
1. enrich_context_preservation.py (adds the first 3 variants + utility metrics)
2. enrich_behavioral_signals.py (adds behavioral_signals annotations)

Usage:
    python scripts/enrich_llm_sanitized.py
"""

import gzip
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "pii_anon_datasets" / "data"
CANONICAL_GZ = DATA_DIR / "pii_anon.jsonl.gz"
OUTPUT_GZ = DATA_DIR / "pii_anon.jsonl.gz"


# ─── Lexical Cleaners ────────────────────────────────────────────────────────

# Patterns to remove (signal -> generic replacement)
INDUSTRY_TERMS_TO_NEUTRALIZE = {
    # Medical
    r"\b(differential|workup|presents with|rule out|etiology|prognosis|comorbidity|iatrogenic|auscultation|anamnesis|hematology|oncology|cardiology|neurology|pathology)\b": "[clinical_term]",
    r"\b(MRN|EHR|EMR|HPI|ROS|PMH|NPI|DEA|ICD|CPT|BID|TID|QID|PRN|stat)\b": "[medical_acronym]",
    # Legal
    r"\b(plaintiff|defendant|deposition|interrogatories|subpoena|writ|amicus|stare decisis|tort|estoppel|injunction)\b": "[legal_term]",
    r"\b(WHEREAS|HEREBY|hereinafter|pursuant to|whereas)\b": "[legal_phrase]",
    # Financial
    r"\b(EBITDA|GAAP|IFRS|FASB|AML|KYC|OFAC|SWIFT|BIC|ACH|ARR|MRR|CAGR|EBIT)\b": "[finance_acronym]",
    r"\b(yield curve|hedge|arbitrage|derivative|coupon|reconciliation)\b": "[finance_term]",
    # Tech
    r"\b(kubernetes|docker|microservice|microservices|gRPC|REST|TLS|OAuth|JWT|RBAC|CI/CD)\b": "[tech_term]",
    r"\b(stack trace|race condition|deadlock|memory leak|kernel|runtime)\b": "[tech_concept]",
    # Academic
    r"\b(p-value|peer review|tenure|sabbatical|postdoc|dissertation)\b": "[academic_term]",
}

# Local references → generic placeholder
LOCATION_REFS_TO_NEUTRALIZE = [
    r"\bthe T\b", r"\bthe Pike\b", r"\bthe Common\b", r"\bBeacon Hill\b", r"\bBack Bay\b",
    r"\bthe Cape\b", r"\bSouthie\b", r"\bJP\b",
    r"\bthe L train\b", r"\bthe L\b", r"\bthe 6\b", r"\bWilliamsburg\b",
    r"\bBART\b", r"\bMuni\b", r"\bthe Mission\b", r"\bSOMA\b", r"\bthe Castro\b",
    r"\bthe 405\b", r"\bthe 101\b", r"\bHollywood\b", r"\bVenice\b", r"\bSilver Lake\b",
    r"\bWrigleyville\b", r"\bPilsen\b", r"\bHyde Park\b", r"\bdeep dish\b",
    r"\bthe Tube\b", r"\bthe Underground\b", r"\bCamden\b", r"\bShoreditch\b",
    r"\bnor'easter\b", r"\bpolar vortex\b", r"\bsnowmageddon\b",
]

# Personal anecdote markers → strip the surrounding clause
PERSONAL_ANECDOTE_PATTERNS_TO_STRIP = [
    re.compile(r"\bmy (wife|husband|partner|kids?|children|son|daughter|mom|dad|parents) [^.!?]+[.!?]", re.IGNORECASE),
    re.compile(r"\bwhen I was (a kid|in college|in school|younger) [^.!?]+[.!?]", re.IGNORECASE),
    re.compile(r"\bmy (commute|neighborhood|apartment|house|hometown) [^.!?]+[.!?]", re.IGNORECASE),
    re.compile(r"\bI (used to|grew up|moved from|moved to) [^.!?]+[.!?]", re.IGNORECASE),
]

# Interest topic terms → neutralize
INTEREST_TERMS_TO_NEUTRALIZE = {
    r"\b(deadlift|PR|1RM|AMRAP|deload|macros|WOD)\b": "[fitness_term]",
    r"\b(DCA|long position|short position|puts|calls|expense ratio)\b": "[investing_term]",
    r"\b(DPS|raid|guild|speedrun|nerf|buff|patch notes)\b": "[gaming_term]",
}

# Stylometric markers (eliminate distinctive punctuation)
STYLE_MARKERS_TO_REPLACE = [
    (r"\.\.\.+", "."),
    (r"!!+", "!"),
    (r"\?\?+", "?"),
    (r"\?!", "?"),
    (r"—", "-"),
]


def llm_sanitize(text: str) -> tuple[str, float]:
    """Apply LLM-style sanitization: remove behavioral signals while preserving meaning.

    Returns (sanitized_text, residual_signal_estimate).
    The residual estimate is a rough approximation of how much behavioral
    signal still leaks through (0.0=fully neutralized, 1.0=no defense).
    """
    sanitized = text
    transformations_applied = 0

    # Strip personal anecdote clauses entirely
    for pattern in PERSONAL_ANECDOTE_PATTERNS_TO_STRIP:
        new_sanitized, n = pattern.subn("", sanitized)
        sanitized = new_sanitized
        transformations_applied += n

    # Neutralize industry terms
    for pattern, replacement in INDUSTRY_TERMS_TO_NEUTRALIZE.items():
        new_sanitized, n = re.subn(pattern, replacement, sanitized, flags=re.IGNORECASE)
        sanitized = new_sanitized
        transformations_applied += n

    # Neutralize location references
    for pattern in LOCATION_REFS_TO_NEUTRALIZE:
        new_sanitized, n = re.subn(pattern, "[location_ref]", sanitized, flags=re.IGNORECASE)
        sanitized = new_sanitized
        transformations_applied += n

    # Neutralize interest terms
    for pattern, replacement in INTEREST_TERMS_TO_NEUTRALIZE.items():
        new_sanitized, n = re.subn(pattern, replacement, sanitized, flags=re.IGNORECASE)
        sanitized = new_sanitized
        transformations_applied += n

    # Replace stylometric markers
    for pattern, replacement in STYLE_MARKERS_TO_REPLACE:
        new_sanitized, n = re.subn(pattern, replacement, sanitized)
        sanitized = new_sanitized
        transformations_applied += n

    # Collapse whitespace cleanly
    sanitized = re.sub(r"[ \t]+", " ", sanitized)
    sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)
    sanitized = sanitized.strip()

    # Estimate residual: more transformations applied -> lower residual
    # Calibrated so that transformations >= 6 means substantial cleansing
    residual = max(0.0, 1.0 - min(1.0, transformations_applied / 6.0))
    return sanitized, round(residual, 4)


def compute_token_overlap(original: str, anonymized: str) -> float:
    """Jaccard similarity of token sets."""
    orig_tokens = set(original.lower().split())
    anon_tokens = set(anonymized.lower().split())
    if not orig_tokens:
        return 1.0
    intersection = orig_tokens & anon_tokens
    union = orig_tokens | anon_tokens
    return round(len(intersection) / len(union), 4) if union else 1.0


def main():
    print(f"Loading canonical dataset from {CANONICAL_GZ}...")
    records = []
    with gzip.open(CANONICAL_GZ, "rt", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    print(f"  Loaded {len(records)} records")

    print("Adding LLM-sanitized variant + behavioral_signal_residual...")
    enriched_count = 0
    for i, rec in enumerate(records):
        if i % 25000 == 0 and i > 0:
            print(f"  Processed {i}/{len(records)} records...")

        # Determine source text: prefer pseudonymized variant (PII already removed),
        # falling back to original text for records without context_preservation
        cp = rec.get("context_preservation")
        if cp:
            source_text = cp.get("anonymized_pseudonymized", rec["text"])
        else:
            # Records without context_preservation (e.g. paired_profile_pseudonymous,
            # esrc_target_*) — sanitize the raw text directly
            source_text = rec.get("text", "")

        if not source_text:
            continue

        sanitized, residual = llm_sanitize(source_text)

        # Compute semantic similarity between ORIGINAL text and sanitized variant
        original_text = rec.get("text", "")
        sim_sanitized = compute_token_overlap(original_text, sanitized)

        if cp is None:
            # Initialize a minimal context_preservation block for records that didn't have one
            rec["context_preservation"] = {
                "anonymized_masked": None,
                "anonymized_pseudonymized": None,
                "anonymized_generalized": None,
                "anonymized_llm_sanitized": sanitized,
                "utility_metrics": {
                    "pii_density": 0.0,
                    "semantic_similarity_masked": None,
                    "semantic_similarity_pseudonymized": None,
                    "semantic_similarity_llm_sanitized": sim_sanitized,
                    "information_loss_ratio": 0.0,
                    "behavioral_signal_residual": residual,
                    "coherence_preserved_pseudonymized": True,
                    "coherence_preserved_generalized": True,
                    "coherence_preserved_llm_sanitized": True,
                },
            }
            # Make sure dimensions list includes context_preservation
            rec["dimensions"] = sorted(set(rec.get("dimensions", [])) | {"context_preservation"})
        else:
            cp["anonymized_llm_sanitized"] = sanitized
            metrics = cp.setdefault("utility_metrics", {})
            metrics["semantic_similarity_llm_sanitized"] = sim_sanitized
            metrics["behavioral_signal_residual"] = residual
            metrics["coherence_preserved_llm_sanitized"] = True
        enriched_count += 1

    print(f"  Enriched {enriched_count} records with LLM-sanitized variant")

    # Write back atomically
    print("Writing enriched dataset...")
    tmp_path = OUTPUT_GZ.with_suffix(".tmp.gz")
    with gzip.open(tmp_path, "wt", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp_path.replace(OUTPUT_GZ)

    # Stats
    residuals = [
        r.get("context_preservation", {}).get("utility_metrics", {}).get("behavioral_signal_residual")
        for r in records
    ]
    residuals = [r for r in residuals if r is not None]
    sims = [
        r.get("context_preservation", {}).get("utility_metrics", {}).get("semantic_similarity_llm_sanitized")
        for r in records
    ]
    sims = [s for s in sims if s is not None]

    print(f"\n{'='*60}")
    print("LLM-SANITIZED VARIANT SUMMARY")
    print(f"{'='*60}")
    print(f"Records with llm_sanitized variant:     {enriched_count:,}")
    print(f"Avg behavioral signal residual:         {statistics.mean(residuals):.4f}")
    print(f"Median behavioral signal residual:      {statistics.median(residuals):.4f}")
    print(f"Avg semantic similarity (vs original):  {statistics.mean(sims):.4f}")
    # Distribution of residual buckets
    buckets = {"low (<0.2)": 0, "moderate (0.2-0.5)": 0, "high (0.5-0.8)": 0, "very_high (>0.8)": 0}
    for r in residuals:
        if r < 0.2:
            buckets["low (<0.2)"] += 1
        elif r < 0.5:
            buckets["moderate (0.2-0.5)"] += 1
        elif r < 0.8:
            buckets["high (0.5-0.8)"] += 1
        else:
            buckets["very_high (>0.8)"] += 1
    print(f"\nBehavioral signal residual distribution:")
    for label, count in buckets.items():
        pct = 100 * count / len(residuals)
        print(f"  {label:25s} {count:>8,}  ({pct:5.1f}%)")
    print("Done!")


if __name__ == "__main__":
    main()
