#!/usr/bin/env python3
"""
Enrich the PII-Anon dataset with behavioral signal annotations (v1.3.0).

Addresses the Lermen et al. (2026) re-identification threat by annotating
quasi-identifier behavioral signals that survive entity-level de-identification:

1. Writing style fingerprints (sentence length, vocabulary richness, punctuation)
2. Professional domain signals (industry jargon, technical terminology)
3. Interest/topic signals (recurring topics, opinion patterns)
4. Temporal signals (posting time patterns, timezone indicators)
5. Location signals (local references, weather, cultural references)
6. Personal anecdote markers (life experiences, travel, family)

Adds:
- behavioral_signals object per record
- behavioral_signal_density (0.0-1.0)
- reidentification_contribution (low/moderate/high/critical)

Also computes Tier 3 metrics:
- privacy_risk.re_identification_resistance_score (RRS)
- privacy_risk.estimated_reid_recall
- privacy_risk.tier3_risk_level

Usage:
    python scripts/enrich_behavioral_signals.py
"""

import gzip
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _version import DATASET_VERSION

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "pii_anon_datasets" / "data"
CANONICAL_GZ = DATA_DIR / "pii_anon.jsonl.gz"
OUTPUT_GZ = DATA_DIR / "pii_anon.jsonl.gz"


# ─── Lexical Pattern Catalogues ───────────────────────────────────────────────

# Industry jargon by domain — presence of these words signals professional identity
INDUSTRY_JARGON = {
    "medical": [
        "diagnosis", "prognosis", "etiology", "anamnesis", "pathology", "hematology",
        "oncology", "cardiology", "neurology", "differential", "comorbidity", "iatrogenic",
        "presents with", "rule out", "follow-up", "workup", "vitals", "auscultation",
        "ICD", "CPT", "MRN", "NPI", "DEA", "EHR", "EMR", "HPI", "ROS", "PMH",
        "stat", "PRN", "BID", "TID", "QID",
    ],
    "legal": [
        "plaintiff", "defendant", "deposition", "motion", "discovery", "subpoena",
        "voir dire", "habeas corpus", "stare decisis", "tort", "estoppel",
        "interrogatories", "writ", "amicus", "pro se", "in camera",
        "esq", "pursuant to", "hereinafter", "whereas", "thereto",
        "case law", "precedent", "jurisdiction", "remedy", "injunction",
    ],
    "financial": [
        "EBITDA", "P/E", "ROI", "NPV", "IRR", "ARR", "MRR", "CAGR",
        "AML", "KYC", "OFAC", "GAAP", "IFRS", "FASB",
        "swap", "derivative", "hedge", "arbitrage", "yield", "coupon",
        "balance sheet", "income statement", "cash flow", "audit", "reconciliation",
        "wire transfer", "ACH", "SWIFT", "BIC", "IBAN", "FX",
    ],
    "technology": [
        "kubernetes", "docker", "microservice", "API endpoint", "REST", "gRPC",
        "TLS", "OAuth", "JWT", "RBAC", "CI/CD", "deploy",
        "kernel", "stack trace", "memory leak", "race condition", "deadlock",
        "regex", "compile", "runtime", "syntax", "framework",
        "git", "commit", "merge", "rebase", "fork", "PR",
    ],
    "academic": [
        "hypothesis", "methodology", "literature review", "p-value", "significance",
        "peer review", "tenure", "sabbatical", "PhD", "postdoc",
        "citation", "bibliography", "abstract", "thesis", "dissertation",
    ],
}

# Local / regional references — strong location signal
LOCATION_REFERENCES = {
    "boston": ["the T", "the Pike", "the Common", "Beacon Hill", "Back Bay",
               "the Cape", "Southie", "JP", "Allston-Brighton"],
    "nyc": ["the subway", "the L train", "the 6", "Brooklyn", "Queens",
            "Williamsburg", "the bodega", "the Village", "FiDi"],
    "la": ["the 405", "the 101", "Hollywood", "Venice", "Silver Lake",
           "the Valley", "the canyons", "K-town", "DTLA"],
    "sf": ["BART", "Muni", "the Mission", "SOMA", "the Castro", "Outer Sunset",
           "Marin", "the Peninsula", "the East Bay"],
    "chicago": ["the L", "the Loop", "Wrigleyville", "Pilsen", "Hyde Park",
                "the lake", "deep dish", "the Bears"],
    "london": ["the Tube", "the Underground", "Zone 1", "Camden", "Shoreditch",
               "the Thames", "the City", "Oxbridge"],
    "weather_temperate": ["snowmageddon", "polar vortex", "nor'easter", "lake effect"],
    "weather_tropical": ["hurricane season", "monsoon", "the rainy season"],
}

# Cultural / temporal references
CULTURAL_REFERENCES = [
    "World Series", "Super Bowl", "March Madness", "the Final Four",
    "Black Friday", "Cyber Monday", "Prime Day",
    "tax season", "open enrollment", "fiscal year-end",
    "spring break", "fall semester", "winter break",
]

# Topic / interest signals
INTEREST_TOPICS = {
    "tech_enthusiast": ["benchmark", "specs", "GPU", "RAM", "thread count", "build",
                         "framework", "open-source", "self-host"],
    "fitness": ["PR", "1RM", "macros", "split", "cycle", "deload", "AMRAP", "WOD"],
    "investing": ["DCA", "long position", "short", "options", "puts", "calls",
                  "expense ratio", "basis", "lots"],
    "gaming": ["DPS", "raid", "guild", "speedrun", "meta", "nerf", "buff", "patch notes"],
    "academic": ["literature", "field", "advisor", "committee", "lab", "grant",
                 "proposal", "manuscript"],
}

# Personal anecdote markers
PERSONAL_ANECDOTE_PATTERNS = [
    r"\bmy (wife|husband|partner|kids?|children|son|daughter|mom|dad|parents)\b",
    r"\bwhen I was (a kid|in college|in school|younger)\b",
    r"\b(last|this|next) (week|month|year|summer|winter)\b",
    r"\bI (used to|grew up|lived in|moved from|moved to)\b",
    r"\bmy (commute|neighborhood|apartment|house|hometown)\b",
]

# Temporal pattern markers (timezone hints, posting time signals)
TIMEZONE_PATTERNS = [
    (r"\b(this morning|this afternoon|tonight|today)\b", "current_day_reference"),
    (r"\b(EST|PST|CST|MST|UTC|GMT|BST|JST|IST)\b", "explicit_timezone"),
    (r"\b\d{1,2}\s*(am|pm|AM|PM)\b", "explicit_time"),
    (r"\b(weekday|weekend|workday|business hours)\b", "schedule_reference"),
]

# Punctuation and stylometric markers
STYLE_MARKERS = {
    "ellipsis": "...",
    "em_dash": "—",
    "double_dash": "--",
    "exclamation_emphasis": "!!",
    "question_emphasis": "??",
    "interrobang": "?!",
    "all_caps_emphasis": None,  # detected separately
}


# ─── Detection Functions ──────────────────────────────────────────────────────

def detect_writing_style(text: str) -> dict:
    """Detect writing style fingerprints."""
    indicators = []

    # Sentence length distribution
    sentences = re.split(r'[.!?]+', text)
    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    if sentence_lengths:
        avg_len = statistics.mean(sentence_lengths)
        if avg_len < 8:
            indicators.append("short_sentence_style")
        elif avg_len > 25:
            indicators.append("long_sentence_style")
        if len(sentence_lengths) > 2:
            stdev = statistics.stdev(sentence_lengths)
            if stdev > 15:
                indicators.append("high_sentence_variance")

    # Punctuation patterns
    for marker_name, marker in STYLE_MARKERS.items():
        if marker and marker in text:
            indicators.append(f"punctuation:{marker_name}")

    # All-caps emphasis (excluding short acronyms)
    caps_words = [w for w in text.split() if len(w) > 3 and w.isupper()]
    if len(caps_words) >= 2:
        indicators.append("all_caps_emphasis")

    # Vocabulary richness (type-token ratio)
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    if len(words) >= 30:
        ttr = len(set(words)) / len(words)
        if ttr > 0.7:
            indicators.append("rich_vocabulary")
        elif ttr < 0.4:
            indicators.append("repetitive_vocabulary")

    # First-person voice
    first_person = len(re.findall(r'\b(I|me|my|mine|myself)\b', text))
    if first_person >= 5:
        indicators.append("first_person_voice")

    present = len(indicators) > 0
    if len(indicators) >= 4:
        uniqueness = "high"
    elif len(indicators) >= 2:
        uniqueness = "moderate"
    elif len(indicators) == 1:
        uniqueness = "low"
    else:
        uniqueness = "none"

    return {"present": present, "uniqueness": uniqueness, "indicators": indicators}


def detect_professional_domain(text: str, record_domain: str) -> dict:
    """Detect industry jargon and technical terminology."""
    indicators = []
    text_lower = text.lower()

    for domain, jargon_terms in INDUSTRY_JARGON.items():
        matches = [term for term in jargon_terms if term.lower() in text_lower]
        if matches:
            indicators.append(f"industry_jargon:{domain}:{len(matches)}")

    # Domain-specific structural signals (correlated with profession)
    if record_domain == "clinical":
        if re.search(r'\bSOAP\b|\bSubjective:|\bObjective:|\bAssessment:|\bPlan:', text):
            indicators.append("structural:soap_note")
    elif record_domain == "legal":
        if re.search(r'\bWHEREAS\b|\bIT IS HEREBY ORDERED\b|\bv\.\s+[A-Z]', text):
            indicators.append("structural:legal_filing")

    present = len(indicators) > 0
    # Multiple jargon hits across domains is rare — strong identity signal
    if any("industry_jargon" in i and int(i.split(":")[2]) >= 3 for i in indicators):
        uniqueness = "very_high"
    elif len(indicators) >= 2:
        uniqueness = "high"
    elif len(indicators) == 1:
        uniqueness = "moderate"
    else:
        uniqueness = "none"

    return {"present": present, "uniqueness": uniqueness, "indicators": indicators}


def detect_interest_topics(text: str) -> dict:
    """Detect recurring topics / interest patterns."""
    indicators = []
    text_lower = text.lower()

    for topic, terms in INTEREST_TOPICS.items():
        matches = [t for t in terms if t.lower() in text_lower]
        if matches:
            indicators.append(f"topic:{topic}:{len(matches)}")

    present = len(indicators) > 0
    if len(indicators) >= 2:
        uniqueness = "high"
    elif len(indicators) == 1:
        uniqueness = "moderate"
    else:
        uniqueness = "none"

    return {"present": present, "uniqueness": uniqueness, "indicators": indicators}


def detect_temporal_patterns(text: str) -> dict:
    """Detect timezone and posting-time patterns."""
    indicators = []
    for pattern, label in TIMEZONE_PATTERNS:
        if re.search(pattern, text):
            indicators.append(label)

    # Cultural temporal references
    text_lower = text.lower()
    for ref in CULTURAL_REFERENCES:
        if ref.lower() in text_lower:
            indicators.append(f"cultural_temporal:{ref.lower().replace(' ', '_')}")
            break  # one is enough

    present = len(indicators) > 0
    if len(indicators) >= 2:
        uniqueness = "moderate"
    elif len(indicators) == 1:
        uniqueness = "low"
    else:
        uniqueness = "none"

    return {"present": present, "uniqueness": uniqueness, "indicators": indicators}


def detect_location_signals(text: str) -> dict:
    """Detect implicit location signals (local references, dialect, weather)."""
    indicators = []
    text_lower = text.lower()

    for region, refs in LOCATION_REFERENCES.items():
        for ref in refs:
            if ref.lower() in text_lower:
                indicators.append(f"local_reference:{region}:{ref.lower().replace(' ', '_')}")
                break  # one per region is enough

    present = len(indicators) > 0
    # Local references are highly identifying
    if len(indicators) >= 2:
        uniqueness = "very_high"
    elif len(indicators) == 1:
        uniqueness = "high"
    else:
        uniqueness = "none"

    return {"present": present, "uniqueness": uniqueness, "indicators": indicators}


def detect_personal_anecdote(text: str) -> dict:
    """Detect personal anecdote markers (family, life experience)."""
    indicators = []
    for pattern in PERSONAL_ANECDOTE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            # Capture the matched pattern category
            label = pattern.replace(r"\b", "").replace(r"\s", " ")[:30]
            indicators.append(f"anecdote_pattern")
            break

    # Travel mentions
    if re.search(r"\b(visited|trip to|vacation in|traveled to)\b", text, re.IGNORECASE):
        indicators.append("travel_mention")

    present = len(indicators) > 0
    if len(indicators) >= 2:
        uniqueness = "high"
    elif len(indicators) == 1:
        uniqueness = "moderate"
    else:
        uniqueness = "none"

    return {"present": present, "uniqueness": uniqueness, "indicators": indicators}


# ─── Aggregate Scoring ────────────────────────────────────────────────────────

UNIQUENESS_WEIGHT = {
    "none": 0.0,
    "low": 0.15,
    "moderate": 0.35,
    "high": 0.65,
    "very_high": 1.0,
}


def compute_signal_density(signals: dict) -> float:
    """Compute aggregate behavioral signal density (0.0-1.0)."""
    weights = []
    for category, sig in signals.items():
        if isinstance(sig, dict) and "uniqueness" in sig:
            weights.append(UNIQUENESS_WEIGHT.get(sig["uniqueness"], 0.0))
    if not weights:
        return 0.0
    # Average across the 6 categories, weighted by max
    avg = sum(weights) / len(weights)
    peak = max(weights)
    # Combine: peak signals dominate (60%), average density contributes (40%)
    density = 0.6 * peak + 0.4 * avg
    return round(min(1.0, density), 4)


def categorize_reid_contribution(density: float) -> str:
    """Map density to categorical risk level."""
    if density >= 0.7:
        return "critical"
    if density >= 0.5:
        return "high"
    if density >= 0.25:
        return "moderate"
    return "low"


def compute_rrs(behavioral_signals: dict, pii_density: float) -> tuple[float, float, str]:
    """Compute Re-identification Resistance Score (Tier 3 metric).

    RRS = 1 - (re-identification_recall × re-identification_precision)

    For our synthetic dataset, we estimate the components from behavioral signal
    density and the most-unique signal category. Higher behavioral signal density
    → lower RRS (easier to re-identify).

    Returns: (rrs, estimated_reid_recall, tier3_risk_level)
    """
    signal_density = behavioral_signals.get("behavioral_signal_density", 0.0)

    # Estimated ESRC attack recall, calibrated against Lermen et al. ranges:
    # Their ceiling is 67% recall on 89K candidates with full LLM pipeline.
    # We estimate per-record recall from signal density + uniqueness.
    estimated_reid_recall = round(min(0.85, signal_density * 0.85), 4)

    # Estimated precision of attack — increases with high-uniqueness signals
    peak_uniqueness = max(
        (UNIQUENESS_WEIGHT.get(s.get("uniqueness", "none"), 0.0)
         for s in behavioral_signals.values()
         if isinstance(s, dict) and "uniqueness" in s),
        default=0.0,
    )
    estimated_reid_precision = min(0.95, 0.5 + 0.45 * peak_uniqueness)

    rrs = round(1.0 - (estimated_reid_recall * estimated_reid_precision), 4)
    rrs = max(0.0, min(1.0, rrs))

    if rrs < 0.3:
        risk = "critical"
    elif rrs < 0.5:
        risk = "high"
    elif rrs < 0.75:
        risk = "moderate"
    else:
        risk = "low"

    return rrs, estimated_reid_recall, risk


# ─── Main ────────────────────────────────────────────────────────────────────

def enrich_record(rec: dict) -> None:
    """Add behavioral_signals and Tier 3 metrics to a single record (in-place)."""
    text = rec.get("text", "")
    record_domain = rec.get("domain", "general")

    signals = {
        "writing_style": detect_writing_style(text),
        "professional_domain": detect_professional_domain(text, record_domain),
        "interest_topics": detect_interest_topics(text),
        "temporal_patterns": detect_temporal_patterns(text),
        "location_signals": detect_location_signals(text),
        "personal_anecdote": detect_personal_anecdote(text),
    }

    density = compute_signal_density(signals)
    contribution = categorize_reid_contribution(density)

    signals["behavioral_signal_density"] = density
    signals["reidentification_contribution"] = contribution

    rec["behavioral_signals"] = signals

    # Tier 3 metrics (only added to privacy_risk if it exists)
    privacy_risk = rec.get("privacy_risk")
    if privacy_risk is not None:
        pii_density = (
            rec.get("context_preservation", {})
               .get("utility_metrics", {})
               .get("pii_density", 0.0)
        )
        rrs, est_recall, tier3_risk = compute_rrs(signals, pii_density)
        privacy_risk["re_identification_resistance_score"] = rrs
        privacy_risk["estimated_reid_recall"] = est_recall
        privacy_risk["tier3_risk_level"] = tier3_risk


def main():
    print(f"Loading canonical dataset from {CANONICAL_GZ}...")
    records = []
    with gzip.open(CANONICAL_GZ, "rt", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    print(f"  Loaded {len(records)} records")

    print("Enriching with behavioral signals + Tier 3 metrics...")
    for i, rec in enumerate(records):
        if i % 25000 == 0 and i > 0:
            print(f"  Processed {i}/{len(records)} records...")
        enrich_record(rec)

    print(f"  Enriched all {len(records)} records")

    # Stamp version
    for rec in records:
        rec["version"] = DATASET_VERSION

    # Write back atomically
    print("Writing enriched dataset...")
    tmp_path = OUTPUT_GZ.with_suffix(".tmp.gz")
    with gzip.open(tmp_path, "wt", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp_path.replace(OUTPUT_GZ)

    # Stats
    contribution_counts = Counter(r["behavioral_signals"]["reidentification_contribution"]
                                   for r in records)
    risk_counts = Counter(r.get("privacy_risk", {}).get("tier3_risk_level")
                          for r in records if r.get("privacy_risk"))
    densities = [r["behavioral_signals"]["behavioral_signal_density"] for r in records]
    rrss = [r.get("privacy_risk", {}).get("re_identification_resistance_score")
            for r in records if r.get("privacy_risk", {}).get("re_identification_resistance_score") is not None]

    # Per-category presence rates
    category_presence = {cat: 0 for cat in
                          ["writing_style", "professional_domain", "interest_topics",
                           "temporal_patterns", "location_signals", "personal_anecdote"]}
    for r in records:
        for cat in category_presence:
            if r["behavioral_signals"][cat]["present"]:
                category_presence[cat] += 1

    print(f"\n{'='*60}")
    print("BEHAVIORAL SIGNAL ENRICHMENT SUMMARY")
    print(f"{'='*60}")
    print(f"Total records:                      {len(records):,}")
    print(f"Avg behavioral signal density:      {statistics.mean(densities):.4f}")
    print(f"Avg RRS (Tier 3 resistance):        {statistics.mean(rrss):.4f}")
    print(f"\nReidentification contribution distribution:")
    for level, count in contribution_counts.most_common():
        print(f"  {level:12s} {count:>8,}")
    print(f"\nTier 3 risk level distribution:")
    for level, count in risk_counts.most_common():
        print(f"  {str(level):12s} {count:>8,}")
    print(f"\nBehavioral signal category presence rates:")
    for cat, count in category_presence.items():
        pct = 100 * count / len(records)
        print(f"  {cat:25s} {count:>8,}  ({pct:5.1f}%)")
    print("Done!")


if __name__ == "__main__":
    main()
