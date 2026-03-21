# PII Anonymization Evaluation Dataset v1.1.0

A comprehensive, multilingual benchmark dataset for evaluating PII detection and de-identification systems. Provides unified evaluation across 60 languages, 57 entity types, and 7 evaluation dimensions with 117,000+ high-quality synthetic records.

## Overview

The **PII-Anon Evaluation Dataset v1.1.0** is a major restructuring and quality improvement over v1.0.0. Key changes:

- **Unified schema**: Single canonical dataset with consistent field names across all records
- **Clean data only**: All records with template placeholders or broken annotations excluded
- **117K+ records**: Scaled from 68K to 117K with new domain-specific, entity tracking, and coverage fill records
- **Dimension-based organization**: Subset files organized by evaluation dimension, domain, and difficulty
- **4 domain subsets**: Clinical, financial, legal, and technology verticals
- **Sensitivity classification**: Every annotation tagged as `direct_identifier`, `quasi_identifier`, or `sensitive_attribute`
- **60 languages**: Expanded from 52 to 60 languages with ≥30 records per language per dimension
- **Regulatory domain tagging**: Records tagged with applicable regulatory frameworks (GDPR, HIPAA, CCPA, PCI-DSS, SOX, LGPD, PIPA)
- **Coreference tracking**: 25K+ entity tracking records with coreference chains, including 3K ambiguous-name records
- **Statistical coverage**: Every language × dimension cell has ≥30 records for statistically meaningful evaluation
- **Dev/test splits**: Stratified 10/90 split by dimension, language, and difficulty

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

# Load dev/test splits
dev = load_dataset(split="dev")
test = load_dataset(split="test")

# Filter by language
german = load_dataset(language="de")
```

## Dataset Structure

```
src/pii_anon_datasets/
  data/
    pii_anon.jsonl.gz          # Canonical dataset (117K records)
    pii_anon.metadata.json     # Distribution statistics
    pii_anon.schema.json       # JSON Schema for validation
  subsets/
    by_dimension/                 # 7 evaluation dimension subsets
    by_domain/                    # Domain-specific subsets (clinical, financial, legal, technology)
    by_difficulty/                # 4 difficulty levels
  splits/
    dev.jsonl.gz                  # 10% stratified dev set
    test.jsonl.gz                 # 90% stratified test set
```

## Dataset Summary

| Property | Value |
|----------|-------|
| **Total Records** | 117,752 |
| **Total Annotations** | 913,983 |
| **Entity Types** | 57 |
| **Entity Categories** | 9 |
| **Languages** | 60 |
| **Writing Scripts** | 32 |
| **Evaluation Dimensions** | 7 |
| **Domain Subsets** | 4 (clinical, financial, legal, technology) |
| **Query-Aware Records** | 8,168 |
| **Adversarial Records** | 15,565 |
| **Ambiguous Entity Tracking** | 3,000 |
| **Coverage Guarantee** | ≥30 records per language × dimension |
| **Regulatory Frameworks** | 7 (GDPR, HIPAA, CCPA, PCI-DSS, SOX, LGPD, PIPA) |
| **Data Source** | 100% Synthetic (CC0/CC-BY-4.0) |
| **Real PII** | None |
| **License** | Apache 2.0 |

## Record Schema

Each record follows a unified schema:

```json
{
  "record_id": "uuid-v5",
  "text": "Source text with PII entities",
  "version": "1.1.0",
  "annotations": [{
    "entity_id": "e0",
    "entity_type": "PERSON_NAME",
    "start": 0, "end": 10,
    "text": "John Smith",
    "category": "identity_demographics",
    "sensitivity_class": "direct_identifier",
    "cluster_id": null,
    "mention_variant": null
  }],
  "language": "en",
  "script": "Latn",
  "language_family": "Germanic",
  "resource_level": "high",
  "primary_dimension": "diverse_pii_types",
  "dimensions": ["diverse_pii_types", "context_preservation"],
  "data_type": "unstructured_text",
  "domain": "general",
  "difficulty_level": "moderate",
  "context_length_tier": "medium",
  "token_count": 42,
  "entity_tracking": {
    "num_repeated_entities": 3,
    "coreference_chains": [["e0","e3","e5"]],
    "tracking_difficulty": "complex",
    "num_distinct_persons": 2
  },
  "adversarial": {
    "type": "leetspeak",
    "difficulty": "moderate",
    "techniques": ["character_substitution"]
  },
  "privacy_risk": {
    "quasi_identifiers": ["AGE", "POSTAL_CODE"],
    "reidentification_risk": "moderate",
    "k_anonymity_estimate": 20
  },
  "query_context": {
    "query": "What is the patient's name?",
    "relevant_entity_ids": ["e0", "e3"]
  },
  "regulatory_domains": ["gdpr", "ccpa"],
  "provenance": { "source_type": "synthetic", "license": "CC0-1.0" }
}
```

## Evaluation Dimensions

| Dimension | Records | % | Description |
|-----------|---------|---|-------------|
| **Diverse PII Types** | 32,414 | 27.5% | Coverage of all 57 entity types |
| **Entity Tracking** | 25,207 | 21.4% | Coreference across multi-turn contexts (incl. 3K ambiguous) |
| **Multilingual & Dialect** | 22,716 | 19.3% | 60 languages across 32 writing systems |
| **Edge Cases** | 12,377 | 10.5% | Misspellings, abbreviations, obfuscation |
| **Context Preservation** | 10,538 | 8.9% | Semantic integrity during anonymization |
| **Temporal Consistency** | 7,350 | 6.2% | Time-series entity evolution |
| **Format Variations** | 7,150 | 6.1% | JSON, XML, CSV, tables, forms |

## Entity Categories (9 categories, 57 types)

| Category | Count | Examples |
|----------|-------|---------|
| **Identity & Demographics** | 8 | PERSON_NAME, ORGANIZATION_NAME, NATIONALITY, GENDER |
| **Contact** | 7 | EMAIL_ADDRESS, PHONE_NUMBER, FAX_NUMBER |
| **Financial** | 11 | CREDIT_CARD_NUMBER, IBAN, SWIFT_BIC_CODE, TAX_ID, INVOICE_NUMBER, INSURANCE_POLICY_NUMBER |
| **Digital & Online** | 13 | USERNAME, API_KEY, IP_ADDRESS, MAC_ADDRESS, SESSION_ID, PASSWORD |
| **Government & Legal** | 9 | PASSPORT_NUMBER, SOCIAL_SECURITY_NUMBER, LICENSE_PLATE, COURT_CASE_NUMBER, VEHICLE_REGISTRATION |
| **Medical & Biological** | 8 | MEDICAL_RECORD_NUMBER, HEALTH_CONDITION, MEDICATION_NAME, PROCEDURE_NAME |
| **Location & Temporal** | 7 | STREET_ADDRESS, POSTAL_CODE, DATE_OF_BIRTH, TIMESTAMP |
| **Employment** | 4 | JOB_TITLE, SALARY, EMPLOYEE_ID, EDUCATION_LEVEL |
| **Special Category** | 5 | POLITICAL_OPINION, RELIGIOUS_BELIEF, MARITAL_STATUS |

## Language Coverage

60 languages across 32 writing systems:

| Writing System | Count | Languages |
|---|---|---|
| **Latin** | 32 | English, Spanish, French, German, Italian, Portuguese, Dutch, Polish, Turkish, Swedish, Norwegian, Danish, Finnish, Czech, Romanian, Hungarian, Slovak, Croatian, Lithuanian, Estonian, Icelandic, Afrikaans, Vietnamese, Maltese, Catalan, Albanian, Welsh, Latvian, Azerbaijani, Zulu, Indonesian + more |
| **Cyrillic** | 8 | Russian, Ukrainian, Serbian, Bulgarian, Macedonian, Belarusian, Mongolian, Kazakh |
| **Arabic** | 6 | Arabic, Persian, Urdu, Pashto, Kurdish, Uyghur |
| **CJK** | 4 | Simplified Chinese, Traditional Chinese, Japanese, Korean |
| **Indic** | 4 | Hindi, Bengali, Sinhala, Nepali |
| **Other** | 6 | Greek, Thai, Hebrew, Georgian, Armenian, Lao, Khmer + more |

## Domain Coverage

| Domain | Records | Key Entity Types |
|--------|---------|-----------------|
| **General** | 81,142 | All types |
| **Financial** | 14,596 | CREDIT_CARD_NUMBER, IBAN, BANK_ACCOUNT_NUMBER, INVOICE_NUMBER |
| **Clinical** | 11,698 | MEDICAL_RECORD_NUMBER, HEALTH_CONDITION, MEDICATION_NAME |
| **Technology** | 7,316 | API_KEY, IP_ADDRESS, MAC_ADDRESS, PASSWORD |
| **Legal** | 3,000 | COURT_CASE_NUMBER, NATIONAL_ID_NUMBER, PASSPORT_NUMBER |

## Advanced Features

### Query-Aware PII Detection
8,168 records include `query_context` with a natural language query and the entity IDs relevant to that query. This enables evaluation of context-aware PII masking for RAG systems.

### Ambiguous Entity Tracking
3,000 records include two or more people who share a first name (e.g., "Jack Davis" and "Jack Marshall") or last name, testing whether a pipeline can correctly disambiguate and independently track each person. These records have `tracking_difficulty: "ambiguous"` and `adversarial.type: "name_collision"`.

### Adversarial Taxonomy
15,565 records include structured `adversarial` metadata classifying the obfuscation technique (leetspeak, partial redaction, format noise, dense PII, abbreviation, name collision, etc.) and difficulty level.

### Re-identification Risk Scoring
Every record includes `privacy_risk` with a list of quasi-identifiers, a re-identification risk level, and a k-anonymity estimate based on the quasi-identifier combination.

### Regulatory Domain Tagging
Every record is tagged with applicable regulatory frameworks (`gdpr`, `hipaa`, `ccpa`, `pci_dss`, `sox`, `lgpd`, `pipa`) based on the entity types, domain, and language.

### Statistical Coverage Guarantee
Every language × dimension cell in the 60×7 matrix has ≥30 records, ensuring statistically meaningful evaluation per language per dimension.

## Documentation

- **[TAXONOMY.md](TAXONOMY.md)** — Complete entity type taxonomy with definitions, sensitivity classes, and regulatory mapping
- **[COMPARISON.md](COMPARISON.md)** — Head-to-head comparison with 7 competing PII benchmarks
- **[DATASHEET.md](DATASHEET.md)** — Gebru et al. (2021) datasheet for transparency and accountability
- **[MIGRATION.md](MIGRATION.md)** — v1.0.0 → v1.1.0 migration guide with schema changes and entity type mapping
- **[CHANGELOG.md](CHANGELOG.md)** — Version history and detailed change log

## Scripts

The `scripts/` directory contains the full data pipeline:

```bash
# Migrate from v1.0.0 (reads v1 files, outputs canonical format)
python scripts/migrate_v1_to_v2.py

# Generate new synthetic records (entity tracking, clinical, financial, etc.)
PYTHONPATH=. python scripts/generate_records.py --all

# Merge migrated + generated records into canonical file
python scripts/merge_and_rebuild.py

# Enrich with query_context, adversarial taxonomy, k-anonymity, regulatory tags
python scripts/enrich.py

# Fill coverage matrix (every language×dimension ≥ 30 records)
PYTHONPATH=. python scripts/generate_coverage_fill.py

# Validate the dataset
PYTHONPATH=. python scripts/validate.py

# Generate subset files from canonical dataset
PYTHONPATH=. python scripts/generate_subsets.py
```

## Citation

```bibtex
@dataset{holla2026pii_anon_eval,
  title={PII Anonymization Evaluation Dataset v1.1.0},
  author={Holla, Subhash},
  year={2026},
  publisher={GitHub},
  howpublished={\url{https://github.com/subhash-holla/pii-anon-eval-data}},
  note={Comprehensive multilingual benchmark with 117K records across 60 languages and 57 entity types}
}
```

## License

**Apache License 2.0**

- Record content: CC0 (Public Domain) / CC-BY-4.0 (requires attribution)
- Schema and code: Apache 2.0

## Version History

- **v1.1.0** (2026-03-21) — Major restructuring: unified schema, 117K records, 60 languages, statistical coverage guarantee, ambiguous entity tracking, 7 regulatory frameworks, dev/test splits
- **v1.0.0** (2026-02-23) — Initial release with `llm_pipeline_core`, `llm_long_context_tracking`, and `eval_framework_v1`

## Acknowledgements

This dataset was built with the assistance of AI coding agents, primarily [Claude Code](https://claude.ai/claude-code) by Anthropic. All AI-generated output was reviewed and validated by the project maintainers.
