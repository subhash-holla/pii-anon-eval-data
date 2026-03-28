# PII Anonymization Evaluation Dataset v1.2.0

A comprehensive, multilingual benchmark dataset for evaluating PII detection, anonymization quality, and context preservation. Provides unified evaluation across 60 languages, 65 entity types, 31 document formats, and 7 evaluation dimensions with 151,000+ high-quality synthetic records.

**What makes this dataset unique**: It is the only PII benchmark that evaluates both **detection** and **anonymization quality** -- every record includes three anonymized text variants (masked, pseudonymized, generalized) with utility metrics, information anchor scores, and anonymization strategy recommendations.

## Overview

| Property | Value |
|----------|-------|
| **Total Records** | 151,752 |
| **Total Annotations** | ~1.22M |
| **Entity Types** | 65 (9 categories) |
| **Languages** | 60 (32 writing systems) |
| **Document Types** | 31 (clinical, legal, financial, technology) |
| **Evaluation Dimensions** | 7 |
| **Adversarial Attack Categories** | 13+ |
| **AI-Era Test Cases** | 1,000 (prompt injection, RAG, multi-agent, system prompt leakage) |
| **Context Preservation** | 100% of records (anonymized variants + utility metrics) |
| **Nested Entity Annotations** | 136,000+ |
| **Train/Dev/Test Split** | 70/10/20 (template-level stratified) |
| **Regulatory Frameworks** | 7 (GDPR, HIPAA, CCPA, PCI-DSS, SOX, LGPD, PIPA) |
| **Data Source** | 100% Synthetic (CC0/CC-BY-4.0) |
| **License** | Apache 2.0 (code) / CC0 (data) |

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

Every record includes three anonymized text variants and utility metrics:

```python
record["context_preservation"] = {
    "anonymized_masked": "Patient [PERSON_NAME] (MRN: [MEDICAL_RECORD_NUMBER])...",
    "anonymized_pseudonymized": "Patient Alex Anderson (MRN: MRN-5678901)...",
    "anonymized_generalized": "Patient [Person] (MRN: [Medical Record Number])...",
    "utility_metrics": {
        "pii_density": 0.35,
        "semantic_similarity_masked": 0.62,
        "semantic_similarity_pseudonymized": 0.58,
        "information_loss_ratio": 0.28,
        "coherence_preserved_pseudonymized": true,
        "coherence_preserved_generalized": true
    }
}
```

Each annotation includes per-entity context metadata:

```python
annotation["information_anchor_score"] = 0.85  # How critical to document meaning (0-1)
annotation["anonymization_strategy"] = "pseudonymize"  # mask/pseudonymize/generalize/suppress
annotation["context_dependency"] = "low"  # none/low/moderate/high
```

### 2. AI-Era Test Cases (1,000 records)

Purpose-built evaluation scenarios for LLM and agentic systems:

- **Prompt injection PII** (250): Instruction overrides attempting to extract PII from system prompts
- **RAG context PII** (250): Retrieved documents with PII where only query-relevant info should be shared
- **Multi-agent PII sharing** (250): Cross-agent PII propagation audit scenarios
- **System prompt leakage** (250): Credentials and admin PII embedded in system configurations

### 3. Advanced Adversarial Patterns (13+ categories)

Attack patterns where production systems drop from 94% to 14% F1:

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

### 4. 31 Realistic Document Formats

**Healthcare (8)**: Progress notes (SOAP), nursing notes, radiology reports, pathology reports, doctor-patient transcripts, referral letters, prescriptions, insurance claims

**Legal (5)**: Deposition transcripts (Q&A), witness statements, legal memos, court opinions, discovery letters

**Financial (7)**: Customer complaint emails, support chat logs, analyst notes, loan narratives, SAR narratives, insurance claims, KYC onboarding notes

**Technology (4)**: Prompt injection scenarios, RAG contexts, multi-agent workflows, system prompt configurations

**General (7)**: Discharge summaries, wire transfers, court filings, forms, invoices, employee rosters, audit logs

### 5. Nested Entity Support

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
  "record_id": "uuid-v5",
  "text": "Source text with PII entities",
  "version": "1.2.0",
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
| **Diverse PII Types** | 57,414 | 37.8% | Coverage across all 65 entity types |
| **Entity Tracking** | 25,207 | 16.6% | Coreference across multi-turn contexts (incl. 3K ambiguous) |
| **Multilingual & Dialect** | 22,716 | 15.0% | 60 languages across 32 writing systems |
| **Edge Cases** | 20,377 | 13.4% | Adversarial patterns, obfuscation, AI-era test cases |
| **Context Preservation** | 10,538 | 6.9% | Query-aware PII for RAG systems |
| **Temporal Consistency** | 7,350 | 4.8% | Time-series entity evolution |
| **Format Variations** | 7,150 | 4.7% | JSON, XML, CSV, tables, forms |

## Entity Categories (9 categories, 65 types)

| Category | Types | Examples |
|----------|-------|---------|
| **Identity & Demographics** | 8 | PERSON_NAME, ORGANIZATION_NAME, NATIONALITY, GENDER, AGE, ETHNICITY |
| **Contact** | 7 | EMAIL_ADDRESS, PHONE_NUMBER, FAX_NUMBER, MOBILE_DEVICE_ID |
| **Financial** | 13 | CREDIT_CARD_NUMBER, IBAN, BANK_ACCOUNT_NUMBER, CVV, PIN, TAX_ID |
| **Digital & Online** | 14 | USERNAME, API_KEY, IP_ADDRESS, MAC_ADDRESS, PASSWORD, USER_AGENT_STRING |
| **Government & Legal** | 11 | PASSPORT_NUMBER, SSN, COURT_CASE_NUMBER, BAR_NUMBER, DOCKET_NUMBER |
| **Medical & Biological** | 11 | MEDICAL_RECORD_NUMBER, NPI_NUMBER, DEA_NUMBER, HEALTH_CONDITION, MEDICATION_NAME |
| **Location & Temporal** | 7 | STREET_ADDRESS, POSTAL_CODE, DATE_OF_BIRTH, TIMESTAMP |
| **Employment** | 4 | JOB_TITLE, SALARY, EMPLOYEE_ID, EDUCATION_LEVEL |
| **Special Category** | 5 | POLITICAL_OPINION, RELIGIOUS_BELIEF, MARITAL_STATUS |

## Domain Coverage

| Domain | Records | Key Document Types |
|--------|---------|-------------------|
| **General** | 89,142 | Discharge summaries, forms, employee rosters, audit logs |
| **Financial** | 23,346 | Complaint emails, support chats, SARs, KYC notes, loan narratives |
| **Clinical** | 21,698 | Progress notes, nursing notes, radiology/pathology reports, prescriptions |
| **Legal** | 9,250 | Depositions, witness statements, legal memos, court opinions |
| **Technology** | 7,316 | API logs, code, prompt injection, RAG contexts, multi-agent workflows |

## Evaluation Baselines

| Baseline | Script | Description |
|----------|--------|-------------|
| Regex patterns | `baselines/regex_baseline.py` | Pattern-matching lower bound |
| Microsoft Presidio | `baselines/presidio_baseline.py` | Industry-standard framework |
| LLM (GPT-4o, Claude, Llama) | `baselines/llm_baseline.py` | Zero-shot LLM detection |
| Shared evaluation harness | `baselines/evaluate.py` | Strict F1, partial F1, F2 (beta=2), per-type/domain |

## Tool Integrations

| Integration | Script | Description |
|-------------|--------|-------------|
| CoNLL BIO/BILOU | `integrations/conll_format.py` | Standard NER format for spaCy, Flair, HuggingFace |
| Parquet export | `scripts/export_parquet.py` | HuggingFace Hub distribution format |

## Scripts

```bash
# Generate v1.2.0 expansion records (document formats + adversarial)
PYTHONPATH=. python scripts/generate_v120_records.py --all

# Merge all records into canonical file
python scripts/merge_and_rebuild.py

# Enrich with query_context, k-anonymity, regulatory tags
python scripts/enrich.py

# Enrich with context preservation (anonymized variants + utility metrics)
python scripts/enrich_context_preservation.py

# Add nested entities and AI-era test cases
PYTHONPATH=. python scripts/enrich_nested_and_ai_era.py

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

- **[TAXONOMY.md](TAXONOMY.md)** -- 65 entity types with sensitivity classes and regulatory mapping
- **[COMPARISON.md](COMPARISON.md)** -- Pugh chart comparison with 10 competing benchmarks
- **[docs/PUGH_CHART_ANALYSIS.md](docs/PUGH_CHART_ANALYSIS.md)** -- Detailed competitive analysis with 8 weighted criteria
- **[DATASHEET.md](DATASHEET.md)** -- Gebru et al. (2021) datasheet for transparency
- **[MIGRATION.md](MIGRATION.md)** -- v1.0.0 to v1.1.0 migration guide
- **[CHANGELOG.md](CHANGELOG.md)** -- Complete version history

## Citation

```bibtex
@dataset{holla2026pii_anon_eval,
  title={PII Anonymization Evaluation Dataset v1.2.0},
  author={Holla, Subhash},
  year={2026},
  publisher={GitHub},
  howpublished={\url{https://github.com/subhash-holla/pii-anon-eval-data}},
  note={151K records, 65 entity types, 60 languages, context preservation evaluation}
}
```

## License

- **Code and scripts**: Apache License 2.0
- **Record content**: CC0 (Public Domain) / CC-BY-4.0 (requires attribution)
- **All data is 100% synthetic** -- no real personal information

## Version History

- **v1.2.0** (2026-03-27) -- Context preservation USP, 31 document formats, 13+ adversarial categories, AI-era test cases, nested entities, LLM baselines, 70/10/20 splits
- **v1.1.0** (2026-03-21) -- Unified schema, 117K records, 60 languages, statistical coverage guarantee, ambiguous entity tracking, regulatory tagging
- **v1.0.0** (2026-02-23) -- Initial release

## Acknowledgements

This dataset was built with the assistance of AI coding agents, primarily [Claude Code](https://claude.ai/claude-code) by Anthropic. All AI-generated output was reviewed and validated by the project maintainers.
