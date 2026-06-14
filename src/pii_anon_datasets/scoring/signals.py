"""Behavioral-signal extractor (FR-008 exposure-index substrate; DC-07).

Ported FAITHFULLY out of ``scripts/enrich_behavioral_signals.py`` so ``src/`` stays
import-pure (NFR-004 — pure-stdlib, no numpy/scipy/pandas). The script becomes a thin
caller in a later cleanup; this module is the canonical home of the ``detect_*`` logic,
the ``UNIQUENESS_WEIGHT`` table, and ``compute_signal_density``.

reidx-01 (LOAD-BEARING): the re-identification scorer's ``Target.observed_signals`` are
produced by :func:`extract` over the *anonymized* text — they are RE-EXTRACTED, never
copied from the gold ``behavioral_signals``. Keeping the extractor here (not in scripts/)
is what lets the scoring core re-run it deterministically on the adversary's view.

Determinism (AX-002): every ``detect_*`` and :func:`extract` is a pure function of its
text input — no clock, no network, no filesystem, no RNG.
"""
from __future__ import annotations

import re
import statistics

SIGNAL_EXTRACTOR_VERSION = "signal-extractor-v1"

# A behavioral_signals block is a JSON-shaped mapping: per-category detector dicts
# (``{"present": bool, "uniqueness": str, "indicators": list[str]}``) plus the scalar
# ``behavioral_signal_density`` (float) and ``reidentification_contribution`` (str).
SignalsBlock = dict[str, object]

# ─── Lexical Pattern Catalogues (ported verbatim from enrich_behavioral_signals.py) ───

# Industry jargon by domain — presence of these words signals professional identity
INDUSTRY_JARGON: dict[str, list[str]] = {
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
LOCATION_REFERENCES: dict[str, list[str]] = {
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
CULTURAL_REFERENCES: list[str] = [
    "World Series", "Super Bowl", "March Madness", "the Final Four",
    "Black Friday", "Cyber Monday", "Prime Day",
    "tax season", "open enrollment", "fiscal year-end",
    "spring break", "fall semester", "winter break",
]

# Topic / interest signals
INTEREST_TOPICS: dict[str, list[str]] = {
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
PERSONAL_ANECDOTE_PATTERNS: list[str] = [
    r"\bmy (wife|husband|partner|kids?|children|son|daughter|mom|dad|parents)\b",
    r"\bwhen I was (a kid|in college|in school|younger)\b",
    r"\b(last|this|next) (week|month|year|summer|winter)\b",
    r"\bI (used to|grew up|lived in|moved from|moved to)\b",
    r"\bmy (commute|neighborhood|apartment|house|hometown)\b",
]

# Temporal pattern markers (timezone hints, posting time signals)
TIMEZONE_PATTERNS: list[tuple[str, str]] = [
    (r"\b(this morning|this afternoon|tonight|today)\b", "current_day_reference"),
    (r"\b(EST|PST|CST|MST|UTC|GMT|BST|JST|IST)\b", "explicit_timezone"),
    (r"\b\d{1,2}\s*(am|pm|AM|PM)\b", "explicit_time"),
    (r"\b(weekday|weekend|workday|business hours)\b", "schedule_reference"),
]

# Punctuation and stylometric markers
STYLE_MARKERS: dict[str, str | None] = {
    "ellipsis": "...",
    "em_dash": "—",
    "double_dash": "--",
    "exclamation_emphasis": "!!",
    "question_emphasis": "??",
    "interrobang": "?!",
    "all_caps_emphasis": None,  # detected separately
}


# ─── Detection Functions (ported verbatim) ────────────────────────────────────

def detect_writing_style(text: str) -> dict[str, object]:
    """Detect writing style fingerprints."""
    indicators: list[str] = []

    # Sentence length distribution
    sentences = re.split(r"[.!?]+", text)
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
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    if len(words) >= 30:
        ttr = len(set(words)) / len(words)
        if ttr > 0.7:
            indicators.append("rich_vocabulary")
        elif ttr < 0.4:
            indicators.append("repetitive_vocabulary")

    # First-person voice
    first_person = len(re.findall(r"\b(I|me|my|mine|myself)\b", text))
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


def detect_professional_domain(text: str, record_domain: str = "general") -> dict[str, object]:
    """Detect industry jargon and technical terminology.

    Ported from the script's ``detect_professional_domain(text, record_domain)``.
    ``record_domain`` defaults to ``"general"`` here so :func:`extract` can be a pure
    function of ``text`` alone (the adversary re-extracts from anonymized text and has
    no record-domain side channel). The only domain-gated branch is the structural
    SOAP/legal-filing indicator; with the default it is simply not asserted — the
    text-based ``INDUSTRY_JARGON`` detection (the dominant signal) is unaffected.
    """
    indicators: list[str] = []
    text_lower = text.lower()

    for domain, jargon_terms in INDUSTRY_JARGON.items():
        matches = [term for term in jargon_terms if term.lower() in text_lower]
        if matches:
            indicators.append(f"industry_jargon:{domain}:{len(matches)}")

    # Domain-specific structural signals (correlated with profession)
    if record_domain == "clinical":
        if re.search(r"\bSOAP\b|\bSubjective:|\bObjective:|\bAssessment:|\bPlan:", text):
            indicators.append("structural:soap_note")
    elif record_domain == "legal":
        if re.search(r"\bWHEREAS\b|\bIT IS HEREBY ORDERED\b|\bv\.\s+[A-Z]", text):
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


def detect_interest_topics(text: str) -> dict[str, object]:
    """Detect recurring topics / interest patterns."""
    indicators: list[str] = []
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


def detect_temporal_patterns(text: str) -> dict[str, object]:
    """Detect timezone and posting-time patterns."""
    indicators: list[str] = []
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


def detect_location_signals(text: str) -> dict[str, object]:
    """Detect implicit location signals (local references, dialect, weather)."""
    indicators: list[str] = []
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


def detect_personal_anecdote(text: str) -> dict[str, object]:
    """Detect personal anecdote markers (family, life experience)."""
    indicators: list[str] = []
    for pattern in PERSONAL_ANECDOTE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            indicators.append("anecdote_pattern")
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


# ─── Aggregate Scoring (ported verbatim) ───────────────────────────────────────

UNIQUENESS_WEIGHT: dict[str, float] = {
    "none": 0.0,
    "low": 0.15,
    "moderate": 0.35,
    "high": 0.65,
    "very_high": 1.0,
}


def compute_signal_density(signals: SignalsBlock) -> float:
    """Compute aggregate behavioral signal density (0.0-1.0).

    ``density = 0.6 * peak(w_c) + 0.4 * mean(w_c)`` over the six signal categories,
    where ``w_c = UNIQUENESS_WEIGHT[category.uniqueness]``. Rounded to 4 dp, clamped
    to [0, 1]. Ported verbatim from ``enrich_behavioral_signals.py``.
    """
    weights: list[float] = []
    for _category, sig in signals.items():
        if isinstance(sig, dict) and "uniqueness" in sig:
            weights.append(UNIQUENESS_WEIGHT.get(sig["uniqueness"], 0.0))
    if not weights:
        return 0.0
    avg = sum(weights) / len(weights)
    peak = max(weights)
    density = 0.6 * peak + 0.4 * avg
    return round(min(1.0, density), 4)


def categorize_reid_contribution(density: float) -> str:
    """Map density to categorical risk level (ported verbatim)."""
    if density >= 0.7:
        return "critical"
    if density >= 0.5:
        return "high"
    if density >= 0.25:
        return "moderate"
    return "low"


def extract(text: str) -> SignalsBlock:
    """Re-extract the ``behavioral_signals`` block from ``text`` (reidx-01).

    Produces the same shape the enrichment script writes per record: the six detector
    categories plus ``behavioral_signal_density`` and ``reidentification_contribution``.
    This is the function the re-identification scorer runs over a Target's *anonymized*
    text — its output is the adversary's observed view, deliberately decoupled from the
    gold ``Persona.behavioral_signals``.
    """
    signals: SignalsBlock = {
        "writing_style": detect_writing_style(text),
        "professional_domain": detect_professional_domain(text),
        "interest_topics": detect_interest_topics(text),
        "temporal_patterns": detect_temporal_patterns(text),
        "location_signals": detect_location_signals(text),
        "personal_anecdote": detect_personal_anecdote(text),
    }
    density = compute_signal_density(signals)
    signals["behavioral_signal_density"] = density
    signals["reidentification_contribution"] = categorize_reid_contribution(density)
    return signals
