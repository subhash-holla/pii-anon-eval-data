# PII Anonymization Evaluation Dataset v2.2.0

A comprehensive, multilingual benchmark dataset for evaluating PII detection, anonymization quality, context preservation, and **resistance to LLM-based semantic re-identification** (Tier 3). Provides unified evaluation across 60 languages, 66 entity types, 40 document formats, and 7 evaluation dimensions with 782,677 synthetic records (159,891 of which form the Tier-3 re-identification EVALUATION substrate).

> **v2.0.0 (schema):** the scattered Tier-3 re-identification-resistance signal (RRS, behavioral signals, tier3 risk) is consolidated into a single `tier3_evaluation` wrapper per record; `record_id` is now deterministic/content-addressed; the canonical entity-type set was **63** (single source: `pii_anon_datasets.taxonomy`). v1.3.0 records load via `pii_anon_datasets.compat.to_v1_record()`. See MIGRATION.md / CHANGELOG.md.

> **v2.1.0 (working/unarchived):** additive honesty release — honest field aliases + caveats travel into the shipped data (`token_overlap_jaccard_*`, `legal_category`, `residual_quasi_identifier`, `exposure_index_prior`, `_caveat` fields, `reg_hipaa_phi_present` column, file-level metadata disclaimers). No synthetic-content regeneration; no Zenodo/HF re-mint (deferred to Phase 2). All v2.0.0 keys preserved. Publication metadata and DOI remain at v2.0.0.

**What makes this dataset unique**: PII-Anon is the only benchmark that evaluates **all three tiers** of PII protection:
- **Tier 1**: Entity-level PII detection (precision, recall, F1, F2)
- **Tier 2**: Anonymization quality with 4 anonymized text variants (masked, pseudonymized, generalized, LLM-sanitized) plus utility metrics
- **Tier 3**: Resistance to LLM-based re-identification attacks (Lermen et al. 2026) via behavioral signal annotations, RRS scoring, and paired profile records

## Overview

| Property | Value |
|----------|-------|
| **Total Records** | 782,677 |
| **Total Annotations** | 3,107,240 |
| **Entity Types** | 66 (9 categories) |
| **Languages** | 60 (19 writing systems) |
| **Document Types** | 40 (clinical, legal, financial, technology, Tier 3 evaluation) |
| **Evaluation Dimensions** | 7 |
| **Adversarial Attack Categories** | 17+ |
| **AI-Era Test Cases** | 1,000 (prompt injection, RAG, multi-agent, system prompt leakage) |
| **Anonymized Variants per Record** | 4 (masked, pseudonymized, generalized, **LLM-sanitized**) |
| **Behavioral Signal Annotations** | **159,891 (27.6% — the Tier-3 evaluation substrate)** |
| **Tier 3 Evaluation Records** | **7,003** (paired profiles + ESRC + stylometric) |
| **Paired Personas** | **2,500** (5,000 records: pseudonymous + real-identity) |
| **Per-record RRS Score** | **159,891 (27.6% — Tier-3 evaluation substrate)** |
| **Avg Re-identification Resistance Score** | **0.78** |
| **Synthetic-lattice enrichment (S-PWR)** | 79.2% of records (provenance.source_type=synthetic_lattice_enrichment) |
| **Nested Entity Annotations** | 136,000+ |
| **Train/Dev/Test Split** | 70/10/20 (template-level stratified) |
| **Regulatory Frameworks** | 7 (GDPR, HIPAA, CCPA, PCI-DSS, SOX, LGPD, PIPA) |
| **Data Source** | 100% Synthetic (CC0-1.0) |
| **License** | Apache 2.0 (code) / CC0 (data) |

> **Train-vs-eval.** The 159,891 `tier3_evaluation` records are the EVALUATION substrate of the 782,677-record corpus — behavioral-signal / RRS scoring runs on this substrate; the full corpus is the detection substrate.

> **Statistical power (epistemic honesty).** PII-Anon v2 is powered for all single-factor marginal recall claims (95% Wilson CIs; credential/financial-critical types to ±0.5pp at recall 0.99, standard to ±1pp at 0.98) and for three pre-registered 2-way interactions (language×entity-type on a committed rectangle, domain×track, adversarial-type×entity-type). The corpus carries a committed evaluation lattice powering **17 languages across 11 writing systems** (Latin, Han, Japanese, Hangul, Arabic, Devanagari, Cyrillic, Thai, Greek, Bengali, Hebrew) to statistically-calibrated positive-count targets (critical n≥1522, standard n≥753). It is not powered for the full multilingual×entity-type grid or any ≥3-way interaction; those are reported as exploratory. Synthetic-distribution power is not external validity — see the [External-Validity Protocol (FR-027)](docs/external-validity-protocol.md) and the real-data correlation slice. 79.2% of records carry `provenance.source_type="synthetic_lattice_enrichment"` (S-PWR formulaic enrichment), which raises statistical power but does NOT establish real-world generalization.

## Installation

```bash
pip install pii-anon-datasets
```

## Quick Start

```python
from pii_anon_datasets import load_dataset

# Load the full canonical dataset
records = load_dataset()

# Load a specific evaluation dimension
entity_tracking = load_dataset(subset="entity_tracking")

# Load a domain subset
clinical = load_dataset(domain="clinical")

# Load train/dev/test splits
train = load_dataset(split="train")   # 70%
dev = load_dataset(split="dev")       # 10%
test = load_dataset(split="test")     # 20%

# Load adversarial test set (subset of test, no train contamination)
adversarial = load_dataset(split="test_adversarial")

# Load cross-domain test sets
test_clinical = load_dataset(split="test_clinical")

# Filter by language
german = load_dataset(language="de")
```

## Key Differentiators

### 1. Context Preservation (Unique Selling Proposition)

Every record includes **four** anonymized text variants and utility metrics:

```python
record["context_preservation"] = {
    "anonymized_masked": "Patient [PERSON_NAME] (MRN: [MEDICAL_RECORD_NUMBER])...",
    "anonymized_pseudonymized": "Patient Alex Anderson (MRN: MRN-5678901)...",
    "anonymized_generalized": "Patient [Person] (MRN: [Medical Record Number])...",
    "anonymized_llm_sanitized": "Patient [...] - clinical assessment unremarkable.",  # removes PII AND behavioral signals
    "utility_metrics": {
        "pii_density": 0.35,
        "semantic_similarity_masked": 0.62,
        "semantic_similarity_pseudonymized": 0.58,
        "semantic_similarity_llm_sanitized": 0.42,
        "information_loss_ratio": 0.28,
        "behavioral_signal_residual": 0.18,                    # how much identity info leaks through
        "coherence_preserved_pseudonymized": true,
        "coherence_preserved_generalized": true,
        "coherence_preserved_llm_sanitized": true
    }
}
```

> **Honesty disclosure (v2.1.0):** `semantic_similarity_*` is **token-overlap Jaccard** (set intersection / union of whitespace tokens via `compute_token_overlap`), **not** a semantic embedding or neural similarity measure. `coherence_preserved_*` is an **assumed constant** (hardcoded `True`) rather than a measured coherence score. `information_loss_ratio` is an **entity-type prior** (a closed-form mapping over entity-type counts), not a measured information loss. Honest aliases `token_overlap_jaccard_*` are added in v2.1.0 and travel into the shipped data.

### 2. Tier 3: Re-identification Resistance

Addresses the Lermen et al. (2026) finding that LLMs can re-identify users at **67% recall / 90% precision** even after all direct PII is removed. Every record includes:

```python
record["behavioral_signals"] = {
    "writing_style": {"present": True, "uniqueness": "moderate", "indicators": ["short_sentence_style", "first_person_voice"]},
    "professional_domain": {"present": True, "uniqueness": "high", "indicators": ["industry_jargon:medical:4"]},
    "interest_topics": {"present": False, "uniqueness": "none", "indicators": []},
    "temporal_patterns": {"present": True, "uniqueness": "low", "indicators": ["explicit_timezone"]},
    "location_signals": {"present": True, "uniqueness": "very_high", "indicators": ["local_reference:boston:the_T"]},
    "personal_anecdote": {"present": False, "uniqueness": "none", "indicators": []},
    "behavioral_signal_density": 0.42,                     # 0.0=none, 1.0=highly identifying
    "reidentification_contribution": "high"                # low/moderate/high/critical
}

record["privacy_risk"]["re_identification_resistance_score"] = 0.62   # RRS: 0.0=easy reid, 1.0=resistant
record["privacy_risk"]["estimated_reid_recall"] = 0.38                # estimated ESRC attack recall
record["privacy_risk"]["tier3_risk_level"] = "moderate"               # low/moderate/high/critical
```

> **Honesty disclosure (v2.1.0):** **No record is demonstrated anonymised under GDPR Recital 26.** `tier3_risk_level` and `re_identification_resistance_score` (and its v2.1.0 alias `exposure_index_prior`) are **heuristic priors** — closed-form scores computed from behavioral signal density — **not** the result of measured adversarial attacks. For a CI-bearing, attack-measured number, run the FR-007 MeasuredRRS adversary (see `results/tier-a/measured_rrs.md`). `anonymized_pseudonymized` and `anonymized_llm_sanitized` remain **personal data** under GDPR Art.4(5); neither constitutes anonymisation under Recital 26.

**Paired Profile Records (5,000 records, 2,500 personas):**
Each persona has both a pseudonymous forum profile (no direct PII, full behavioral signals) and a real-identity LinkedIn-style profile. Same `persona_id` enables ESRC-attack matching evaluation — directly mirroring the Hacker News ↔ LinkedIn experiment in Lermen et al.

```python
record["tier3_evaluation"] = {
    "is_paired_profile": True,
    "persona_id": "persona_00042",
    "profile_type": "pseudonymous_forum",
    "linked_profile_id": "persona_00042_real",
    "esrc_attack_target": True,
    "expected_reidentification_difficulty": "moderate",
    "behavioral_signal_removal_attempted": False
}
```

**ESRC-Attack Evaluation Records (2,003 records):**
- 791: entity-level de-id succeeded but behavioral signals intact (should be re-identifiable)
- 812: behavioral signals also removed via LLM sanitization (should resist re-identification)
- 400: adversarial fake-signal injection (confuses matching)

**Stylometric Adversarial (1,136 records):** stylometric_obfuscation, interest_diversification, temporal_pattern_disruption, paraphrased_content

Each annotation includes per-entity context metadata:

```python
annotation["information_anchor_score"] = 0.85  # How critical to document meaning (0-1)
annotation["anonymization_strategy"] = "pseudonymize"  # mask/pseudonymize/generalize/suppress
annotation["context_dependency"] = "low"  # none/low/moderate/high
```

### 3. AI-Era Test Cases (1,000 records)

Purpose-built evaluation scenarios for LLM and agentic systems:

- **Prompt injection PII** (250): Instruction overrides attempting to extract PII from system prompts
- **RAG context PII** (250): Retrieved documents with PII where only query-relevant info should be shared
- **Multi-agent PII sharing** (250): Cross-agent PII propagation audit scenarios
- **System prompt leakage** (250): Credentials and admin PII embedded in system configurations

> **Honesty disclosure (v2.1.0):** The "250 each" count above is for the **full corpus**. The **test split** carries fewer AI-era records (counted by `document_type`): **51 / 50 / 57 / 41** for prompt-injection / RAG / multi-agent / system-prompt-leakage respectively (the full 250-each splits 70/10/20 across train/dev/test). These are **scenario fixtures** designed to exercise detection, **not** a measured security evaluation. FR-017 (security-evaluation harness) was not implemented in v2.x; FR-018–FR-020 (penetration-test-style adversarial generation) are likewise not yet implemented.

### 4. Advanced Adversarial Patterns (17+ categories)

Attack patterns that stress off-the-shelf detectors — obfuscation, encoding, and context-ambiguity. Measured clean→adversarial recall drops are **attack- and detector-specific** (see `results/tier-a/adversarial_table.md`); the widely-quoted but **unbacked "94% → 14% F1" slogan is retracted** — no off-the-shelf detector reaches 94% clean recall (GLiNER's clean recall is ~0.72):

| Category | Technique | Records |
|----------|-----------|---------|
| Unicode homoglyphs | Cyrillic/Greek lookalike substitution | 1,000 |
| Zero-width characters | ZWJ/ZWSP/ZWNJ insertion | 800 |
| BiDi text attacks | RTL override characters | 500 |
| Base64/URL encoding | Encoded PII in structured context | 1,100 |
| OCR artifacts | 0/O, 1/l/I, rn/m confusions | 800 |
| Negated PII | "NOT John Smith" -- still PII | 600 |
| Context-dependent | "Washington" as name vs location | 600 |
| Code/URL embedded | PII in JSON, SQL, URL parameters | 1,000 |
| Mixed-script/Multi-token | Cross-language PII, compound names | 1,100 |

### 5. 40 Realistic Document Formats

**Healthcare (8)**: Progress notes (SOAP), nursing notes, radiology reports, pathology reports, doctor-patient transcripts, referral letters, prescriptions, insurance claims

**Legal (5)**: Deposition transcripts (Q&A), witness statements, legal memos, court opinions, discovery letters

**Financial (7)**: Customer complaint emails, support chat logs, analyst notes, loan narratives, SAR narratives, insurance claims, KYC onboarding notes

**Technology (4)**: Prompt injection scenarios, RAG contexts, multi-agent workflows, system prompt configurations

**General (7)**: Discharge summaries, wire transfers, court filings, forms, invoices, employee rosters, audit logs

**Tier 3 Evaluation (9)**: paired_profile_pseudonymous, paired_profile_real, esrc_target_signals_intact, esrc_target_signals_removed, esrc_signal_injection, stylometric_obfuscation, interest_diversification, temporal_pattern_disruption, paraphrased_content

### 6. Nested Entity Support

136,000+ annotations include `nested_entities` for overlapping spans:

```python
{
    "entity_type": "ORGANIZATION_NAME",
    "text": "Boston Children's Hospital",
    "nested_entities": [
        {"entity_type": "LOCATION_NAME", "text": "Boston", "start_offset": 0, "end_offset": 6}
    ]
}
```

## Record Schema

```json
{
  "record_id": "uuid-v5 (deterministic: sha256 of text + sorted annotation offsets)",
  "text": "Source text with PII entities",
  "version": "2.0.0",
  "schema_version": "2.0.0",
  "annotations": [{
    "entity_id": "e0",
    "entity_type": "PERSON_NAME",
    "start": 0, "end": 10,
    "text": "John Smith",
    "category": "identity_demographics",
    "sensitivity_class": "direct_identifier",
    "cluster_id": null,
    "mention_variant": null,
    "information_anchor_score": 0.85,
    "anonymization_strategy": "pseudonymize",
    "context_dependency": "low",
    "nested_entities": null
  }],
  "language": "en",
  "script": "Latn",
  "primary_dimension": "diverse_pii_types",
  "dimensions": ["diverse_pii_types", "context_preservation"],
  "data_type": "unstructured_text",
  "document_type": "progress_note",
  "domain": "clinical",
  "difficulty_level": "moderate",
  "entity_tracking": { "coreference_chains": [["e0","e3"]], "tracking_difficulty": "complex" },
  "adversarial": { "type": null, "difficulty": "clean", "techniques": [] },
  "privacy_risk": { "quasi_identifiers": ["AGE"], "reidentification_risk": "low", "k_anonymity_estimate": 100 },
  "query_context": { "query": "What is the patient's name?", "relevant_entity_ids": ["e0"] },
  "context_preservation": {
    "anonymized_masked": "...",
    "anonymized_pseudonymized": "...",
    "anonymized_generalized": "...",
    "utility_metrics": { "pii_density": 0.35, "semantic_similarity_masked": 0.62 }
  },
  "regulatory_domains": ["gdpr", "hipaa"],
  "provenance": { "source_type": "synthetic", "license": "CC0-1.0" }
}
```

## Evaluation Dimensions

| Dimension | Records | % | Description |
|-----------|---------|---|-------------|
| **Diverse PII Types** | 57,414 | 37.8% | Coverage across all 66 entity types |
| **Entity Tracking** | 25,207 | 16.6% | Coreference across multi-turn contexts (incl. 3K ambiguous) |
| **Multilingual & Dialect** | 22,716 | 15.0% | 60 languages across 19 writing systems (ISO 15924) |
| **Edge Cases** | 20,377 | 13.4% | Adversarial patterns, obfuscation, AI-era test cases |
| **Context Preservation** | 10,538 | 6.9% | Query-aware PII for RAG systems |
| **Temporal Consistency** | 7,350 | 4.8% | Time-series entity evolution |
| **Format Variations** | 7,150 | 4.7% | JSON, XML, CSV, tables, forms |

## Entity Categories (9 categories, 66 types)

The canonical 66 entity types live in `pii_anon_datasets.taxonomy` (single source of truth; see TAXONOMY.md). Per-category counts:

| Category | Types | Examples |
|----------|-------|---------|
| **Identity & Demographics** | 6 | PERSON_NAME, ORGANIZATION_NAME, NATIONALITY, GENDER, AGE, ETHNICITY |
| **Contact** | 2 | EMAIL_ADDRESS, PHONE_NUMBER |
| **Financial** | 12 | CREDIT_CARD_NUMBER, IBAN, BANK_ACCOUNT_NUMBER, CVV, PIN, TAX_ID |
| **Digital & Online** | 10 | USERNAME, API_KEY, IP_ADDRESS, MAC_ADDRESS, PASSWORD, SOCIAL_MEDIA_HANDLE |
| **Government & Legal** | 10 | PASSPORT_NUMBER, SOCIAL_SECURITY_NUMBER, COURT_CASE_NUMBER, BAR_NUMBER, DOCKET_NUMBER |
| **Medical & Biological** | 8 | MEDICAL_RECORD_NUMBER, NPI_NUMBER, DEA_NUMBER, HEALTH_CONDITION, MEDICATION_NAME |
| **Location & Temporal** | 6 | STREET_ADDRESS, POSTAL_CODE, DATE_OF_BIRTH, TIMESTAMP, LOCATION_NAME, LATITUDE_LONGITUDE |
| **Employment** | 4 | JOB_TITLE, SALARY, EMPLOYEE_ID, EDUCATION_LEVEL |
| **Special Category** | 8 | POLITICAL_OPINION, RELIGIOUS_BELIEF, SEXUAL_ORIENTATION, TRADE_UNION_MEMBERSHIP, GENETIC_DATA, MARITAL_STATUS, HOUSEHOLD_SIZE, VEHICLE_MODEL |

All 6 GDPR Art-9 types (POLITICAL_OPINION, RELIGIOUS_BELIEF, ETHNICITY, SEXUAL_ORIENTATION, TRADE_UNION_MEMBERSHIP, GENETIC_DATA) are powered to ≥400 spans across 12 languages. Art-9 synthetic values are English-anchored (per-language localization deferred). `reg_gdpr` is now discriminative — a `_NON_PERSONAL` out-of-scope record set exists (~417 records) alongside the in-scope records.

> **Honesty disclosures — synthetic-value localization (v2.2 work-in-progress).** Beyond the non-strippable synthetic-only ceiling (AX-001) and the Art-9 English-anchored values above:
> - Non-name PII **values** (addresses, organizations, occupations, medical, identifiers, financial) are English/US-anchored synthetic across **all 60 languages**; per-language value localization is deferred to a later release (2D).
> - Person-name values for `hi` and `th` are romanized Latin, not native-script (el/bn/he names ARE native-script: Greek/Bengali/Hebrew).
> - `he` records mix right-to-left Hebrew names with left-to-right Latin identifiers/emails/URLs — a known display-realism limitation.

## Domain Coverage

| Domain | Records | Key Document Types |
|--------|---------|-------------------|
| **General** | 89,142 | Discharge summaries, forms, employee rosters, audit logs |
| **Financial** | 23,346 | Complaint emails, support chats, SARs, KYC notes, loan narratives |
| **Clinical** | 21,698 | Progress notes, nursing notes, radiology/pathology reports, prescriptions |
| **Legal** | 9,250 | Depositions, witness statements, legal memos, court opinions |
| **Technology** | 7,316 | API logs, code, prompt injection, RAG contexts, multi-agent workflows |

## Evaluation Baselines

| Baseline | Adapter | Description |
|----------|---------|-------------|
| Regex patterns | `baselines/regex_baseline.py` | Pattern-matching lower bound |
| Microsoft Presidio | `baselines/presidio_baseline.py` | Industry-standard framework |
| spaCy NER | `baselines/spacy_baseline.py` | `en_core_web_lg` general NER |
| GLiNER | `baselines/gliner_baseline.py` | Zero-shot multi-PII (`gliner_multi_pii-v1`) |
| Piiranha | `baselines/piiranha_baseline.py` | Token-classification PII model |
| scrubadub | `baselines/scrubadub_baseline.py` | Rule-based detector |
| Stanza | `baselines/stanza_baseline.py` | Stanford NLP NER |
| Flair | `baselines/flair_baseline.py` | CoNLL-03 sequence tagger |
| LLM (GPT/Claude) | `baselines/llm_baseline.py` | Zero-shot LLM (behind an API key) |
| Cloud DLP (AWS/GCP/Azure) | `baselines/{aws_comprehend,gcp_dlp,azure}_baseline.py` | Run behind keys on the full English test (single run); budget-gated behind `--cloud` |
| Shared harness + audited scorer | `baselines/evaluate.py` · `scoring/detection.py` | Strict + partial F1/F2 (β=2), Wilson 95% CIs, per-type/domain |

## Baseline Detector Performance

How the most-used PII pipelines score on PII-Anon, ranked by **F2** (recall-weighted — a missed PII is the
costly error). Full leaderboard with per-entity-type / per-domain / per-language breakdowns, Wilson 95% CIs,
and the label-map coverage disclosure: **[BASELINES.md](BASELINES.md)**.

> **Synthetic-only (AX-001):** real detectors on *synthetic* data — these are not external-validity claims. See the [External-Validity Protocol (FR-027)](docs/external-validity-protocol.md) for the only path to lifting this ceiling.

> **Coverage note:** the leaderboard below is the re-scored **66-type** measured English run (the Coverage column reads `reachable/66`). The 3 GDPR Art-9 special-category types added in the 63→66 taxonomy expansion are unreachable by *every* off-the-shelf detector (recall 0 by construction) — see [art9_coverage_v22dev.md](results/tier-a/art9_coverage_v22dev.md).

<!-- BEGIN-LEADERBOARD-SUMMARY (generated from results/baselines/tier1-en-all; see BASELINES.md) -->
`test` split · `en` · 31,048 records / 201,880 gold spans · **11 detectors** (8 local + 3 cloud DLP), F2-ranked. Cloud rows are a **single run** of non-deterministic managed services.

| Rank | Detector | Precision | Recall | F1 | F2 | Recall 95% CI | Coverage |
|---|---|---:|---:|---:|---:|---|---:|
| 1 | aws | 0.769 | 0.728 | 0.748 | 0.736 | [0.726, 0.730] | 24/66 |
| 2 | gliner | 0.813 | 0.716 | 0.762 | 0.734 | [0.714, 0.718] | 23/66 |
| 3 | gcp | 0.722 | 0.700 | 0.711 | 0.704 | [0.698, 0.702] | 18/66 |
| 4 | azure | 0.730 | 0.688 | 0.709 | 0.696 | [0.686, 0.690] | 17/66 |
| 5 | presidio | 0.419 | 0.562 | 0.480 | 0.526 | [0.560, 0.564] | 20/66 |
| 6 | regex | 0.857 | 0.349 | 0.496 | 0.396 | [0.347, 0.351] | 9/66 |
| 7 | piiranha | 0.441 | 0.327 | 0.376 | 0.345 | [0.325, 0.329] | 16/66 |
| 8 | stanza | 0.583 | 0.308 | 0.403 | 0.340 | [0.306, 0.310] | 3/66 |
| 9 | flair | 0.565 | 0.295 | 0.388 | 0.326 | [0.293, 0.297] | 3/66 |
| 10 | spacy | 0.464 | 0.294 | 0.360 | 0.317 | [0.292, 0.296] | 3/66 |
| 11 | scrubadub | 0.818 | 0.169 | 0.280 | 0.201 | [0.167, 0.170] | 12/66 |

**GLiNER** (free, local) is F2-competitive with **AWS Comprehend** (F2 0.734 vs 0.736) — a precision/recall trade-off: AWS holds a paired-significant **+1.19pp recall** edge (McNemar p=1.4e-33) while GLiNER matches on F2 via higher precision; both beat GCP + Azure. Full per-domain / per-type / per-language breakdowns and Wilson CIs in **[BASELINES.md](BASELINES.md)**.
<!-- END-LEADERBOARD-SUMMARY -->

```bash
# Local detectors (deterministic, free):
pii-anon baselines --detectors regex,presidio,spacy,gliner,piiranha,scrubadub,stanza,flair \
  --split test --languages en --out results/baselines/tier1-en
# Cloud DLP (needs AWS/GCP/Azure credentials; budget-gated):
pii-anon baselines --cloud --detectors aws,gcp,azure \
  --split test --languages en --out results/baselines/cloud-en
```

## Tool Integrations

| Integration | Script | Description |
|-------------|--------|-------------|
| CoNLL BIO/BILOU | `integrations/conll_format.py` | Standard NER format for spaCy, Flair, HuggingFace |
| Parquet export | `scripts/export_parquet.py` | HuggingFace Hub distribution format |

## Scripts

```bash
# Generate v1.2.0 expansion records (document formats + adversarial)
PYTHONPATH=. python scripts/generate_v120_records.py --all

# Generate v1.3.0 Tier 3 records (paired profiles + ESRC attack + stylometric)
PYTHONPATH=. python scripts/generate_v130_records.py --all

# Merge all records into canonical file
python scripts/merge_and_rebuild.py

# Enrich with query_context, k-anonymity, regulatory tags
python scripts/enrich.py

# Enrich with context preservation (3 anonymized variants + utility metrics)
python scripts/enrich_context_preservation.py

# Add nested entities and AI-era test cases
PYTHONPATH=. python scripts/enrich_nested_and_ai_era.py

# v1.3.0: Add behavioral signal annotations + RRS scoring (Tier 3)
python scripts/enrich_behavioral_signals.py

# v1.3.0: Add 4th anonymized variant (LLM-sanitized) + behavioral_signal_residual
python scripts/enrich_llm_sanitized.py

# Validate the dataset (expect 0 errors)
PYTHONPATH=. python scripts/validate.py

# Generate subsets and 70/10/20 splits
PYTHONPATH=. python scripts/generate_subsets.py

# Run regex baseline
PYTHONPATH=. python baselines/regex_baseline.py

# Export to CoNLL format
PYTHONPATH=. python integrations/conll_format.py --split train
```

## Documentation

- **[TAXONOMY.md](TAXONOMY.md)** -- 66 entity types with sensitivity classes and regulatory mapping
- **[COMPARISON.md](COMPARISON.md)** -- Pugh chart comparison against major competing benchmarks
- **[docs/PUGH_CHART_ANALYSIS.md](docs/PUGH_CHART_ANALYSIS.md)** -- Detailed competitive analysis with 8 weighted criteria
- **[DATASHEET.md](DATASHEET.md)** -- Gebru et al. (2021) datasheet for transparency
- **[MIGRATION.md](MIGRATION.md)** -- version migration guide (v1.0.0 → v1.1.0 and v1.3.0 → v2.0.0)
- **[CHANGELOG.md](CHANGELOG.md)** -- Complete version history

## Citation

```bibtex
@dataset{holla2026pii_anon_eval,
  title={PII Anonymization Evaluation Dataset v2.0.0: Three-Tier Benchmark with Behavioral Signal Annotations},
  author={Holla, Subhash},
  year={2026},
  publisher={GitHub},
  howpublished={\url{https://github.com/subhash-holla/pii-anon-eval-data}},
  note={782,677 records, 66 entity types, 60 languages, 4 anonymized variants per record,
        behavioral signal annotations for Tier 3 LLM re-identification resistance evaluation}
}
```

## License

- **Code and scripts**: Apache License 2.0
- **Record content**: CC0-1.0 (Public Domain Dedication -- no attribution required)
- **All data is 100% synthetic** -- no real personal information

## Version History

- **v2.0.0** (2026-05-28) -- **Schema clean-up + running scorers**: consolidated the scattered Tier-3 signal into a single `tier3_evaluation` wrapper; deterministic content-addressed `record_id`; canonical 63-type entity registry (`pii_anon_datasets.taxonomy`) reconciling prior 48/65/80 doc drift; new Hexagonal scoring harness (`pii_anon_datasets.scoring` + `stats`) that *scores a system's output* (detection P/R/F1/F2 with Wilson CIs; non-strippable anti-anonymity caveat on RRS); first real test suite (pytest, ~95% cov on scorer modules) + CI config. Back-compat via `compat.to_v1_record()`; v1.3.0 pinned at git tag `v1.3.0`. (Note: canonical type count raised to 66 in v2.2-dev.)
- **v1.3.0** (2026-04-15) -- **Tier 3 evaluation infrastructure**: behavioral signal annotations on all records (6 categories), Re-identification Resistance Score (RRS), 4th anonymized variant (LLM-sanitized), 5K paired profile records (2.5K personas), 2K ESRC-attack records, 4 stylometric adversarial categories. Directly enables PII-Rate-Elo paper Tier 3 framework (addresses Lermen et al. 2026)
- **v1.2.0** (2026-03-27) -- Context preservation USP, 31 document formats, 13+ adversarial categories, AI-era test cases, nested entities, LLM baselines, 70/10/20 splits
- **v1.1.0** (2026-03-21) -- Unified schema, 117K records, 60 languages, statistical coverage guarantee, ambiguous entity tracking, regulatory tagging
- **v1.0.0** (2026-02-23) -- Initial release

## Acknowledgements

This dataset was built with the assistance of AI coding agents, primarily [Claude Code](https://claude.ai/claude-code) by Anthropic. All AI-generated output was reviewed and validated by the project maintainers.
