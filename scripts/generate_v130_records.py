#!/usr/bin/env python3
"""
Generate v1.3.0 Tier 3 evaluation records.

Produces 7,000+ records purpose-built for evaluating LLM-based re-identification
resistance (Lermen et al. 2026 / paper Section 4.2.1):

1. Paired Profile Records (5,000 records, 2,500 personas × 2 profiles each):
   - Pseudonymous forum profile (no direct PII, full behavioral signals)
   - Real-identity profile (LinkedIn-style, full direct PII)
   - Same persona_id allows ESRC-attack matching evaluation

2. ESRC-Attack Evaluation Records (2,000 records):
   - 800 records: entity-level de-id succeeded, behavioral signals intact
   - 800 records: behavioral signals removal attempted (LLM-sanitized)
   - 400 records: adversarial behavioral signal injection (fake signals)

3. Stylometric Adversarial Records (1,000 records, 4 categories × 250):
   - stylometric_obfuscation: deliberately altered writing style
   - interest_diversification: off-topic content mixed in
   - temporal_pattern_disruption: randomized temporal markers
   - paraphrased_content: LLM-rewritten preserving meaning

Usage:
    PYTHONPATH=. python scripts/generate_v130_records.py --all
"""

import argparse
import json
import random
import sys
import uuid
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _version import DATASET_VERSION
from scripts.generate_records import (
    PIIFactory,
    PIIValue,
    build_record,
    SEED,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "src" / "pii_anon_datasets" / "data" / "pii_anon_v130_generated.jsonl"


# ─── Persona Configuration ────────────────────────────────────────────────────

DOMAIN_DISTRIBUTION = {
    "technology": 1000,
    "clinical": 500,
    "financial": 500,
    "legal": 250,
    "academic": 250,
}

# Industry jargon snippets used to inject professional behavioral signals
DOMAIN_JARGON_SNIPPETS = {
    "technology": [
        "Spent the morning debugging a race condition in our microservices.",
        "Finally got the kubernetes deployment working — TLS was the issue.",
        "Our CI/CD pipeline is broken again, regex matching gone sideways.",
        "Anyone else seeing weird gRPC latency since the last patch?",
        "Switched from REST to GraphQL last month, throughput doubled.",
    ],
    "clinical": [
        "Patient presented with classic differential — workup was unremarkable.",
        "Need to rule out cardiac etiology before discharge.",
        "BID dosing per protocol; no adverse reactions on the floor.",
        "EHR migration is a nightmare — orders aren't propagating to pharmacy.",
        "Prior auth for the new oncology agent took three weeks.",
    ],
    "financial": [
        "EBITDA margin compression across the sector — Q3 should be telling.",
        "Filed our SAR last week, AML team flagged structured deposits.",
        "Yield curve inversion is real this time, not just noise.",
        "Reviewing GAAP vs IFRS treatment for the new lease standard.",
        "FX hedge expired before the EUR drop — painful basis adjustment.",
    ],
    "legal": [
        "Plaintiff is leaning hard on stare decisis but the precedent is shaky.",
        "Filed a motion in limine to exclude the deposition transcripts.",
        "Pursuant to Rule 26, we still owe them the supplemental discovery.",
        "Pro se litigant filed a writ that's barely coherent — pure noise.",
        "The interrogatories are due Friday, no extension this time.",
    ],
    "academic": [
        "Reviewer 2 wants me to redo the entire methodology section. Again.",
        "Tenure committee meets next month, the manuscript needs to be in.",
        "My advisor wants more p-values, the lit review wants fewer.",
        "Postdoc applications are brutal this cycle — applied to twelve places.",
        "Grant proposal due Monday, methodology section still half-written.",
    ],
}

# Local references inject location signals
LOCATION_SNIPPETS = {
    "boston": [
        "The T was down again this morning, walked from Back Bay.",
        "Spent the weekend at the Cape, leaf-peeping was peak.",
        "JP is finally getting a decent coffee shop, took long enough.",
    ],
    "nyc": [
        "L train was packed, switched to the 6 at Union Square.",
        "Williamsburg used to be cheap — those days are long gone.",
        "Stopped at the bodega for breakfast, $7 for a bagel and coffee.",
    ],
    "sf": [
        "BART was running late, Muni was worse, the Mission was crowded.",
        "Spent the afternoon at Outer Sunset, fog was insane.",
        "The Peninsula commute is killing me, considering moving back to the city.",
    ],
    "la": [
        "405 was a parking lot, took surface streets through Hollywood.",
        "Spent the morning hiking in the canyons, light was perfect.",
        "K-town for dinner, then drove back to the Valley.",
    ],
    "chicago": [
        "Rode the L from Wrigleyville, transferred at the Loop.",
        "Lake effect snow shut down I-90 again.",
        "Pilsen has the best tacos, fight me.",
    ],
    "london": [
        "Tube strike again, walked from Camden to Shoreditch.",
        "Thames is high after the rain, footbridges flooded.",
        "Zone 1 rent is insane, considering moving to Zone 3.",
    ],
}

# Topic / interest snippets
INTEREST_SNIPPETS = {
    "fitness": [
        "Hit a PR on deadlift today — finally cleared 4 plates.",
        "Cycling AMRAP into next week, deload was overdue.",
        "Macros are off, dropping carbs and seeing how I feel.",
    ],
    "investing": [
        "Sold puts on the dip, IV was rich enough to justify the risk.",
        "Tax-loss harvesting season is here, time to clean up the lots.",
        "Expense ratio matters more than people realize, basis points add up.",
    ],
    "gaming": [
        "Patch notes nerfed my main, time to find a new build.",
        "Raid wiped on phase 3 again — the meta has shifted.",
        "Speedrun PB is sitting at 1:42, gunning for sub-1:40 this weekend.",
    ],
    "tech_enthusiast": [
        "Built a new rig last weekend — 64GB RAM, the GPU was the bottleneck.",
        "Self-hosting my email finally, took a weekend to get DKIM right.",
        "Open-source alternative to the proprietary tool actually works better.",
    ],
}

# Personal anecdote snippets
ANECDOTE_SNIPPETS = [
    "When I was a kid we used to spend summers at my grandparents' place upstate.",
    "My wife and I just got back from a trip to Portugal, highly recommend.",
    "My commute is brutal — 45 minutes each way, three days a week in the office.",
    "Grew up in a small town in the Midwest, moved to the coast for grad school.",
    "My kids are finally old enough that we can travel without it being a disaster.",
]


# ─── Profile Generators ───────────────────────────────────────────────────────

def _make_pseudonymous_username(rng: random.Random, persona_id: str) -> str:
    """Generate a pseudonymous handle (forum-style)."""
    adjectives = ["quiet", "fast", "sleepy", "curious", "happy", "cosmic", "blue", "green",
                  "obscure", "lazy", "dancing", "hungry", "midnight", "amber", "silent"]
    nouns = ["fox", "panda", "wolf", "raven", "tiger", "kraken", "phoenix", "sparrow",
             "otter", "narwhal", "lynx", "puma", "hawk", "moose", "badger"]
    suffix = rng.randint(10, 999)
    return f"{rng.choice(adjectives)}_{rng.choice(nouns)}{suffix}"


def generate_pseudonymous_profile(rng: random.Random, persona_id: str, domain: str,
                                    location_region: str | None,
                                    interest: str | None,
                                    include_anecdote: bool) -> dict:
    """Generate a pseudonymous forum-style profile post.

    Contains zero direct PII (no real name, email, address) but rich behavioral
    signals: industry jargon, optional location reference, optional interest topic,
    optional personal anecdote, distinctive writing style.
    """
    handle = _make_pseudonymous_username(rng, persona_id)

    # Build a 3-5 paragraph forum post combining behavioral signals
    paragraphs = []

    # Opening: industry jargon
    jargon = rng.choice(DOMAIN_JARGON_SNIPPETS[domain])
    paragraphs.append(jargon)

    # Optional location reference
    if location_region:
        paragraphs.append(rng.choice(LOCATION_SNIPPETS[location_region]))

    # Optional interest topic
    if interest:
        paragraphs.append(rng.choice(INTEREST_SNIPPETS[interest]))

    # Optional personal anecdote
    if include_anecdote:
        paragraphs.append(rng.choice(ANECDOTE_SNIPPETS))

    # Closing: open question or opinion (style marker)
    closings = [
        "Anyone else dealing with this? Curious what's working.",
        "Probably overthinking it but it's been on my mind all week.",
        "Hot take — the conventional wisdom is wrong on this one.",
        "Open to suggestions if anyone has navigated this before.",
    ]
    paragraphs.append(rng.choice(closings))

    body = "\n\n".join(paragraphs)
    text = f"@{handle}:\n\n{body}"

    rec = build_record(
        text_template=text,
        slots={},
        language="en",
        primary_dimension="context_preservation",
        data_type="unstructured_text",
        domain=domain if domain != "academic" else "general",
        document_type="paired_profile_pseudonymous",
        difficulty="hard",
    )

    rec["tier3_evaluation"] = {
        "is_paired_profile": True,
        "persona_id": persona_id,
        "profile_type": "pseudonymous_forum",
        "linked_profile_id": f"{persona_id}_real",
        "esrc_attack_target": True,
        "expected_reidentification_difficulty": "moderate" if location_region else "hard",
        "behavioral_signal_removal_attempted": False,
    }
    return rec


def generate_real_identity_profile(rng: random.Random, persona_id: str, domain: str) -> dict:
    """Generate a real-identity LinkedIn-style profile.

    Contains direct PII (name, email, employer, location) but minimal behavioral
    signals (formal corporate style, no anecdotes).
    """
    factory = PIIFactory(rng, "en")
    name = factory.person_name()
    email = factory.email(name.value)
    org = factory.org()
    title = factory.job_title()
    phone = factory.phone()
    address = factory.address()

    domain_intro = {
        "technology": "Software engineer with experience in distributed systems and platform infrastructure.",
        "clinical": "Healthcare professional focused on patient outcomes and clinical operations.",
        "financial": "Finance professional specializing in risk management and regulatory compliance.",
        "legal": "Attorney with expertise in commercial litigation and regulatory matters.",
        "academic": "Researcher focused on applied methodology and quantitative analysis.",
    }

    template = (
        f"{{name}} — {{title}} at {{org}}\n\n"
        f"{domain_intro[domain]}\n\n"
        f"Contact: {{email}} | {{phone}}\n"
        f"Location: {{address}}\n\n"
        f"Experience\n"
        f"  {{title}} — {{org}} (2021–present)\n"
        f"  Previous role at a similar organization (2017–2021)\n\n"
        f"Education\n"
        f"  Graduate program, completed 2017\n"
    )

    slots = {
        "name": name,
        "email": email,
        "org": org,
        "title": title,
        "phone": phone,
        "address": address,
    }

    rec = build_record(
        text_template=template,
        slots=slots,
        language="en",
        primary_dimension="diverse_pii_types",
        data_type="form",
        domain=domain if domain != "academic" else "general",
        document_type="paired_profile_real",
        difficulty="easy",
    )

    rec["tier3_evaluation"] = {
        "is_paired_profile": True,
        "persona_id": f"{persona_id}_real",
        "profile_type": "real_identity",
        "linked_profile_id": persona_id,
        "esrc_attack_target": False,
        "expected_reidentification_difficulty": "easy",
        "behavioral_signal_removal_attempted": False,
    }
    return rec


def generate_paired_profiles(rng: random.Random) -> list[dict]:
    """Generate 5,000 paired profile records (2,500 personas × 2 profiles)."""
    records = []
    persona_counter = 0

    for domain, persona_count in DOMAIN_DISTRIBUTION.items():
        # Halve persona_count because we generate 2 profiles per persona
        for _ in range(persona_count):
            persona_id = f"persona_{persona_counter:05d}"
            persona_counter += 1

            # Decide which behavioral signals to include for this persona
            location_region = rng.choice([None] + list(LOCATION_SNIPPETS.keys())) if rng.random() < 0.55 else None
            interest = rng.choice(list(INTEREST_SNIPPETS.keys())) if rng.random() < 0.45 else None
            include_anecdote = rng.random() < 0.40

            records.append(
                generate_pseudonymous_profile(
                    rng, persona_id, domain, location_region, interest, include_anecdote
                )
            )
            records.append(generate_real_identity_profile(rng, persona_id, domain))

    return records


# ─── ESRC-Attack Evaluation Records ──────────────────────────────────────────

def generate_esrc_signals_intact(rng: random.Random, count: int) -> list[dict]:
    """Records where entity-level de-id succeeded but behavioral signals are intact.

    These should be re-identifiable by an ESRC pipeline.
    """
    records = []
    for i in range(count):
        domain = rng.choice(list(DOMAIN_JARGON_SNIPPETS.keys()))
        location_region = rng.choice(list(LOCATION_SNIPPETS.keys()))
        interest = rng.choice(list(INTEREST_SNIPPETS.keys()))

        body_parts = [
            rng.choice(DOMAIN_JARGON_SNIPPETS[domain]),
            rng.choice(LOCATION_SNIPPETS[location_region]),
            rng.choice(INTEREST_SNIPPETS[interest]),
            rng.choice(ANECDOTE_SNIPPETS),
        ]
        text = "\n\n".join(body_parts)

        rec = build_record(
            text_template=text,
            slots={},  # No PII annotations — this is the de-identified text
            language="en",
            primary_dimension="edge_cases",
            data_type="unstructured_text",
            domain=domain if domain != "academic" else "general",
            document_type="esrc_target_signals_intact",
            difficulty="challenging",
            adversarial_type="esrc_attack_target",
            adversarial_difficulty="severe",
            adversarial_techniques=["entity_removed", "behavioral_signals_intact"],
        )

        rec["tier3_evaluation"] = {
            "is_paired_profile": False,
            "persona_id": None,
            "profile_type": None,
            "linked_profile_id": None,
            "esrc_attack_target": True,
            "expected_reidentification_difficulty": "easy",
            "behavioral_signal_removal_attempted": False,
        }
        records.append(rec)
    return records


def generate_esrc_signals_removed(rng: random.Random, count: int) -> list[dict]:
    """Records where behavioral signals were ALSO removed (LLM-sanitized style).

    These should resist ESRC re-identification. Text is generic and bland.
    """
    generic_templates = [
        "An update on the project: progress has been made on the current milestone. The team is on track for the planned deliverable. No major blockers at this time.",
        "Work continues on the assigned tasks. The schedule is being maintained. Communication with stakeholders is regular.",
        "The current quarter is progressing as expected. Performance metrics are within normal ranges. Plans for the next period are being finalized.",
        "Recent activity includes completion of standard tasks. The workflow is established and routine. No noteworthy events to report.",
        "Tasks are being completed on schedule. Standard processes are in place. Outcomes are aligned with expectations.",
        "Operations remain stable. Routine activities are proceeding as planned. No exceptional circumstances to note.",
    ]
    suffixes = [
        " Additional details are available upon request through standard channels.",
        " Standard reporting will continue on the established cadence.",
        " The information presented reflects current operational status.",
        " Further inquiry should be directed to designated coordinators.",
        " Outcomes align with the established framework for this initiative.",
    ]

    records = []
    for i in range(count):
        # Combine multiple templates and a unique sequence number to ensure variation
        text_parts = [rng.choice(generic_templates), rng.choice(generic_templates)]
        text_parts.append(rng.choice(suffixes))
        text = " ".join(text_parts)
        text = f"Memo Reference: M-{i:04d}\n\n{text}"

        rec = build_record(
            text_template=text,
            slots={},
            language="en",
            primary_dimension="edge_cases",
            data_type="unstructured_text",
            domain="general",
            document_type="esrc_target_signals_removed",
            difficulty="challenging",
            adversarial_type="esrc_defense_sanitized",
            adversarial_difficulty="severe",
            adversarial_techniques=["entity_removed", "behavioral_signals_removed", "llm_sanitized"],
        )

        rec["tier3_evaluation"] = {
            "is_paired_profile": False,
            "persona_id": None,
            "profile_type": None,
            "linked_profile_id": None,
            "esrc_attack_target": True,
            "expected_reidentification_difficulty": "very_hard",
            "behavioral_signal_removal_attempted": True,
        }
        records.append(rec)
    return records


def generate_esrc_signal_injection(rng: random.Random, count: int) -> list[dict]:
    """Records with adversarial behavioral signal injection (fake signals to confuse matching)."""
    records = []
    domains = list(DOMAIN_JARGON_SNIPPETS.keys())
    locations = list(LOCATION_SNIPPETS.keys())

    for i in range(count):
        # Mix multiple incompatible signals (real domain + 2 unrelated location refs +
        # 2 unrelated interests) to create a "confused" persona
        primary_domain = rng.choice(domains)
        decoy_domains = rng.sample([d for d in domains if d != primary_domain], 2)
        decoy_locations = rng.sample(locations, 2)
        decoy_interests = rng.sample(list(INTEREST_SNIPPETS.keys()), 2)

        body_parts = [
            rng.choice(DOMAIN_JARGON_SNIPPETS[primary_domain]),
            rng.choice(DOMAIN_JARGON_SNIPPETS[decoy_domains[0]]),  # Wrong domain
            rng.choice(LOCATION_SNIPPETS[decoy_locations[0]]),
            rng.choice(LOCATION_SNIPPETS[decoy_locations[1]]),  # Two locations
            rng.choice(INTEREST_SNIPPETS[decoy_interests[0]]),
            rng.choice(INTEREST_SNIPPETS[decoy_interests[1]]),
            rng.choice(DOMAIN_JARGON_SNIPPETS[decoy_domains[1]]),
        ]
        rng.shuffle(body_parts)
        text = "\n\n".join(body_parts)

        rec = build_record(
            text_template=text,
            slots={},
            language="en",
            primary_dimension="edge_cases",
            data_type="unstructured_text",
            domain="general",
            document_type="esrc_signal_injection",
            difficulty="challenging",
            adversarial_type="esrc_defense_injection",
            adversarial_difficulty="severe",
            adversarial_techniques=["fake_signal_injection", "domain_confusion", "location_confusion"],
        )

        rec["tier3_evaluation"] = {
            "is_paired_profile": False,
            "persona_id": None,
            "profile_type": None,
            "linked_profile_id": None,
            "esrc_attack_target": True,
            "expected_reidentification_difficulty": "very_hard",
            "behavioral_signal_removal_attempted": True,
        }
        records.append(rec)
    return records


# ─── Stylometric Adversarial Records ─────────────────────────────────────────

def generate_stylometric_obfuscation(rng: random.Random, count: int) -> list[dict]:
    """Writing style deliberately altered (formal/informal swap, paraphrased)."""
    records = []
    base_pairs = [
        ("Hey, so I think we should probably take another look at this.",
         "Kindly reconsider the current approach with appropriate diligence."),
        ("Yeah, that didn't work — gonna try something else tomorrow.",
         "The implementation was unsuccessful; an alternative will be evaluated subsequently."),
        ("Honestly, the whole thing is kind of a mess right now.",
         "The current state of affairs may warrant a comprehensive reassessment."),
        ("Tbh I'm not sure what they were thinking on this one.",
         "The rationale underlying this decision merits further examination."),
        ("Quick update: shipped the fix, looks good so far.",
         "Status notification: the remediation has been deployed; preliminary indicators are positive."),
        ("Look, this is getting out of hand — we need to talk.",
         "It is increasingly evident that a substantive discussion is warranted."),
        ("Kinda surprised this took as long as it did.",
         "The duration required for completion exceeded initial expectations."),
        ("Don't worry about it, we'll figure it out.",
         "Resolution of this matter will be achieved through subsequent collaborative effort."),
    ]
    contexts = [
        "Slack message", "Email draft", "Code review comment", "Meeting notes",
        "Pull request description", "Bug report", "Status update", "Retro feedback",
    ]
    for i in range(count):
        original, obfuscated = rng.choice(base_pairs)
        ctx = rng.choice(contexts)
        seq = i  # uniqueness anchor
        text = (
            f"{ctx} #{seq:04d}\n\n"
            f"Original style: {original}\n\n"
            f"Obfuscated style: {obfuscated}\n\n"
            f"Note: writing register shifted from informal to formal to defeat stylometric matching."
        )
        rec = build_record(
            text_template=text,
            slots={},
            language="en",
            primary_dimension="edge_cases",
            data_type="unstructured_text",
            domain="general",
            document_type="stylometric_obfuscation",
            difficulty="hard",
            adversarial_type="stylometric_obfuscation",
            adversarial_difficulty="hard",
            adversarial_techniques=["register_shift", "formality_swap"],
        )
        records.append(rec)
    return records


def generate_interest_diversification(rng: random.Random, count: int) -> list[dict]:
    """Off-topic content mixed in to defeat topic-based matching."""
    records = []
    for i in range(count):
        primary = rng.choice(list(INTEREST_SNIPPETS.keys()))
        # Pick 3 unrelated topics
        decoys = rng.sample([t for t in INTEREST_SNIPPETS.keys() if t != primary],
                            min(3, len(INTEREST_SNIPPETS) - 1))
        snippets = [rng.choice(INTEREST_SNIPPETS[primary])]
        snippets.extend(rng.choice(INTEREST_SNIPPETS[t]) for t in decoys)
        rng.shuffle(snippets)
        text = "\n\n".join(snippets)

        rec = build_record(
            text_template=text,
            slots={},
            language="en",
            primary_dimension="edge_cases",
            data_type="unstructured_text",
            domain="general",
            document_type="interest_diversification",
            difficulty="hard",
            adversarial_type="interest_diversification",
            adversarial_difficulty="hard",
            adversarial_techniques=["topic_confusion", "off_topic_injection"],
        )
        records.append(rec)
    return records


def generate_temporal_disruption(rng: random.Random, count: int) -> list[dict]:
    """Randomized temporal markers / posting time disruption."""
    records = []
    timezones = ["EST", "PST", "GMT", "JST", "AEDT", "CET", "IST"]
    for i in range(count):
        # Mix multiple timezones in the same record
        tzs = rng.sample(timezones, 3)
        text = (
            f"Posted at 9am {tzs[0]}: morning standup notes here.\n\n"
            f"Updated at 3pm {tzs[1]}: revisited the discussion after lunch.\n\n"
            f"Closing thoughts at 11pm {tzs[2]}: finalizing for tomorrow."
        )
        rec = build_record(
            text_template=text,
            slots={},
            language="en",
            primary_dimension="edge_cases",
            data_type="unstructured_text",
            domain="general",
            document_type="temporal_pattern_disruption",
            difficulty="hard",
            adversarial_type="temporal_pattern_disruption",
            adversarial_difficulty="hard",
            adversarial_techniques=["timezone_confusion", "schedule_randomization"],
        )
        records.append(rec)
    return records


def generate_paraphrased_content(rng: random.Random, count: int) -> list[dict]:
    """LLM-rewritten preserving meaning but removing style fingerprints."""
    records = []
    paraphrase_pairs = [
        ("I love how this team handles ambiguous requirements — best I've worked with.",
         "The team demonstrates effective management of unclear specifications."),
        ("Honestly the docs are kind of a disaster, took me forever to figure it out.",
         "The documentation presents comprehension challenges and required substantial time investment."),
        ("Quick win this week: finally automated that report nobody wanted to do.",
         "An efficiency improvement was achieved through automation of a manual reporting task."),
        ("Such a relief that the deploy went smoothly — last week was rough.",
         "The deployment was completed without incident, contrasting with prior difficulties."),
        ("Honestly surprised more people aren't talking about this approach.",
         "This methodology appears underrepresented in current professional discourse."),
        ("Took me a while but I finally cracked the bug — was a stupid off-by-one.",
         "Investigation eventually identified the defect as an indexing arithmetic error."),
        ("Wish leadership would just commit to a direction and stick with it.",
         "Consistency of strategic direction would benefit overall execution."),
        ("Spent the whole afternoon on what should have been a 10-minute task.",
         "An expected brief task expanded substantially in elapsed duration."),
    ]
    sources = ["forum_post", "code_review", "team_chat", "design_doc", "1on1_notes",
               "retrospective", "interview_feedback", "blog_post"]
    for i in range(count):
        original, paraphrased = rng.choice(paraphrase_pairs)
        src = rng.choice(sources)
        seq = i
        text = (
            f"Source: {src} (record #{seq:04d})\n\n"
            f"Original: {original}\n\n"
            f"Paraphrased: {paraphrased}\n\n"
            f"Note: LLM paraphrase removes stylometric fingerprints while preserving semantic content."
        )
        rec = build_record(
            text_template=text,
            slots={},
            language="en",
            primary_dimension="edge_cases",
            data_type="unstructured_text",
            domain="general",
            document_type="paraphrased_content",
            difficulty="hard",
            adversarial_type="paraphrased_content",
            adversarial_difficulty="hard",
            adversarial_techniques=["llm_paraphrase", "style_neutralization"],
        )
        records.append(rec)
    return records


# ─── Main ────────────────────────────────────────────────────────────────────

GENERATORS_V130 = {
    "paired_profiles": (generate_paired_profiles, None),  # generates fixed 5000 from DOMAIN_DISTRIBUTION
    "esrc_signals_intact": (generate_esrc_signals_intact, 800),
    "esrc_signals_removed": (generate_esrc_signals_removed, 800),
    "esrc_signal_injection": (generate_esrc_signal_injection, 400),
    "stylometric_obfuscation": (generate_stylometric_obfuscation, 250),
    "interest_diversification": (generate_interest_diversification, 250),
    "temporal_disruption": (generate_temporal_disruption, 250),
    "paraphrased_content": (generate_paraphrased_content, 250),
}


def main():
    parser = argparse.ArgumentParser(description="Generate v1.3.0 Tier 3 records")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--category", type=str, choices=list(GENERATORS_V130.keys()))
    parser.add_argument("--count", type=int, help="Override record count")
    parser.add_argument("--all", action="store_true", help="Generate all categories")
    parser.add_argument("--seed", type=int, default=SEED + 130)
    args = parser.parse_args()

    rng = random.Random(args.seed)

    if args.category:
        gen_func, default_count = GENERATORS_V130[args.category]
        if default_count is None:
            print(f"Generating paired_profiles (5,000 records, fixed)...")
            records = gen_func(rng)
        else:
            count = args.count or default_count
            print(f"Generating {count} {args.category} records...")
            records = gen_func(rng, count)
    elif args.all:
        records = []
        for name, (gen_func, default_count) in GENERATORS_V130.items():
            if default_count is None:
                print(f"Generating {name} (5,000 records, fixed)...")
                batch = gen_func(rng)
            else:
                print(f"Generating {default_count} {name} records...")
                batch = gen_func(rng, default_count)
            records.extend(batch)
            print(f"  Generated {len(batch)} records")
    else:
        parser.print_help()
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(records)} records to {args.output}")

    # Stats
    doc_types = Counter(r.get("document_type") for r in records)
    adv_types = Counter(r.get("adversarial", {}).get("type") for r in records
                        if r.get("adversarial", {}).get("type"))
    domains = Counter(r["domain"] for r in records)

    print(f"\nDocument type distribution:")
    for d, c in doc_types.most_common():
        print(f"  {d}: {c}")
    print(f"\nDomain distribution:")
    for d, c in domains.most_common():
        print(f"  {d}: {c}")
    if adv_types:
        print(f"\nAdversarial type distribution:")
        for t, c in adv_types.most_common():
            print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
