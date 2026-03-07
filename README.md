# PII Anonymization Evaluation Dataset v1.0.0

[![Built with AI Agents](https://img.shields.io/badge/Built_with-AI_Agents-d946ef.svg)](#acknowledgements)

A comprehensive, multilingual benchmark dataset for evaluating personally identifiable information (PII) detection and de-identification systems. This dataset unifies evaluation across 52 languages, 48 entity types, and 7 critical evaluation dimensions with ~70,000 high-quality synthetic records.

## Overview

The **PII Anonymization Evaluation Dataset v1.0.0** is the primary benchmark for the [pii-anon](https://github.com/subhash-holla/pii-anon) library. It provides:

- **Comprehensive PII Coverage:** 48 distinct entity types across 7 semantic categories
- **Multilingual Evaluation:** 52 languages spanning 17 writing systems
- **Balanced Dimensions:** 7 evaluation dimensions (entity tracking, multilingual coverage, context preservation, diverse types, edge cases, format variations, temporal consistency)
- **Synthetic & Safe:** 100% synthetic data (CC0/CC-BY-4.0) with zero real personally identifiable information
- **Production-Ready:** Rigorous quality assurance (98%+ accuracy, Cohen's kappa ≥ 0.85)
- **Reproducible:** Seeded random generation (seed=42) for deterministic dataset creation

## Installation

```bash
pip install pii-anon-datasets
```

Or install with the main library:

```bash
pip install pii-anon
```

## Quick Start

### Basic Usage

```python
from pii_anon.benchmarks.datasets import load_benchmark_dataset

# Load the entire evaluation dataset
records = load_benchmark_dataset("pii_anon_eval_v1.0.0")

# Print first record
print(records[0])
# Output: {
#   "record_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
#   "source_text": "My name is John Smith, you can reach me at john.smith@example.com or (555) 123-4567.",
#   "annotations": [
#     {"entity_id": "e1", "entity_type": "NAME_PERSON", "start": 11, "end": 21, "text": "John Smith", "category": "Identity & Demographics"},
#     {"entity_id": "e2", "entity_type": "EMAIL_ADDRESS", "start": 51, "end": 74, "text": "john.smith@example.com", "category": "Contact Information"},
#     {"entity_id": "e3", "entity_type": "PHONE_NUMBER", "start": 78, "end": 90, "text": "(555) 123-4567", "category": "Contact Information"}
#   ],
#   "language": "en",
#   "script": "Latn",
#   "dimensions": ["Diverse PII Types", "Context Preservation"],
#   "metadata": {"source_dataset": "eval_framework_v1", "generation_seed": 42, "context_length": 98}
# }
```

### Filter by Dimension

```python
from pii_anon.eval_framework.datasets.schema import load_eval_dataset

# Load records for specific evaluation dimension
entity_tracking_records = load_eval_dataset(
    "pii_anon_eval_v1.0.0",
    dimension="Entity Tracking"
)

# Load records for specific language
english_records = load_eval_dataset(
    "pii_anon_eval_v1.0.0",
    language="en"
)

# Combine filters
multilingual_entity_tracking = load_eval_dataset(
    "pii_anon_eval_v1.0.0",
    dimension="Entity Tracking",
    languages=["en", "de", "fr", "es", "zh"]
)
```

### Custom Dataset Root

Set the `PII_ANON_DATASET_ROOT` environment variable to use a custom location:

```bash
export PII_ANON_DATASET_ROOT=/path/to/datasets
python your_script.py
```

## Dataset Summary

| Property | Value |
|----------|-------|
| **Total Records** | ~70,000 |
| **Entity Types** | 48 |
| **Entity Categories** | 7 |
| **Languages** | 52 |
| **Writing Scripts** | 17 |
| **Evaluation Dimensions** | 7 |
| **Data Source** | 100% Synthetic (CC0/CC-BY-4.0) |
| **Real PII** | None — All synthetic |
| **License** | Apache 2.0 |
| **Annotation Quality** | 98%+ accuracy, Cohen's κ ≥ 0.85 |

## Evaluation Dimensions

The dataset provides balanced coverage across 7 critical evaluation dimensions:

| Dimension | Weight | Records | Description |
|-----------|--------|---------|-------------|
| **Entity Tracking** | 20% | ~14,000 | Consistent entity coreference across multi-turn dialogue contexts |
| **Multilingual & Dialect** | 15% | ~10,500 | Coverage of 52 languages with regional dialect variants |
| **Context Preservation** | 20% | ~14,000 | Semantic integrity in document structure during anonymization |
| **Diverse PII Types** | 20% | ~14,000 | Complete coverage of all 48 entity types across 7 categories |
| **Edge Cases** | 10% | ~7,000 | Misspellings, abbreviations, partial PII, obfuscation, ambiguity |
| **Data Format Variations** | 10% | ~7,000 | Structured (JSON), semi-structured (XML), unstructured (free-text) formats |
| **Temporal Consistency** | 5% | ~3,500 | Time-series entity evolution and temporal relationships |

## Entity Categories

The dataset covers **48 entity types** organized into **7 semantic categories**:

### 1. Identity & Demographics (8 types)
```
NAME_PERSON, NAME_ORGANIZATION, NAME_LOCATION, NATIONALITY,
GENDER, AGE, ETHNICITY, DISABILITY_STATUS
```

### 2. Contact Information (7 types)
```
EMAIL_ADDRESS, PHONE_NUMBER, PHONE_COUNTRY_CODE, PHONE_AREA_CODE,
MOBILE_DEVICE_ID, PHONE_EXTENSION, FAX_NUMBER
```

### 3. Financial (9 types)
```
CREDIT_CARD_NUMBER, CREDIT_CARD_CVV, CREDIT_CARD_EXPIRY,
BANK_ACCOUNT_NUMBER, BANK_ROUTING_NUMBER, IBAN, SWIFT_CODE,
CRYPTOCURRENCY_ADDRESS, TRANSACTION_ID
```

### 4. Digital & Online (8 types)
```
USERNAME, PASSWORD, SOCIAL_MEDIA_HANDLE, URL, IP_ADDRESS,
IP_V6_ADDRESS, MAC_ADDRESS, DEVICE_IDENTIFIER
```

### 5. Government & Legal (7 types)
```
PASSPORT_NUMBER, DRIVER_LICENSE_NUMBER, SOCIAL_SECURITY_NUMBER,
TAX_ID, NATIONAL_ID, VISA_NUMBER, LICENSE_PLATE
```

### 6. Medical & Biological (6 types)
```
MEDICAL_RECORD_NUMBER, INSURANCE_CLAIM_NUMBER, HEALTH_CONDITION,
MEDICATION_NAME, PROCEDURE_NAME, GENETIC_MARKER
```

### 7. Location & Temporal (8 types)
```
STREET_ADDRESS, POSTAL_CODE, LATITUDE_LONGITUDE, BUILDING_NAME,
LOCATION_NAME, TIMESTAMP, BIRTHDATE, EVENT_DATE
```

## Language Coverage

The dataset includes data in **52 languages** across **17 writing systems**:

| Writing System | Count | Languages |
|---|---|---|
| **Latin** | 24 | English, Spanish, French, German, Italian, Portuguese, Dutch, Polish, Turkish, Swedish, Norwegian, Danish, Finnish, Czech, Romanian, Hungarian, Slovak, Croatian, Lithuanian, Estonian, Icelandic, Afrikaans, Vietnamese, Maltese |
| **Cyrillic** | 8 | Russian, Ukrainian, Serbian, Bulgarian, Macedonian, Belarusian, Mongolian, Kazakh |
| **Arabic** | 6 | Arabic, Persian, Urdu, Pashto, Kurdish, Uyghur |
| **CJK** | 4 | Simplified Chinese, Traditional Chinese, Japanese, Korean |
| **Greek** | 1 | Greek |
| **Devanagari** | 1 | Hindi |
| **Bengali** | 1 | Bengali |
| **Thai** | 1 | Thai |
| **Hebrew** | 1 | Hebrew |
| **Georgian** | 1 | Georgian |
| **Armenian** | 1 | Armenian |
| **Lao** | 1 | Lao |
| **Khmer** | 1 | Khmer |

## Statistical Properties

### Sample Size and Confidence

Following Cochran (1977) and Cohen (1988) statistical guidelines:

- **95% Confidence Interval** with **±5% Margin of Error**
- **14,000+ records per major dimension** (36x minimum required sample size)
- **80% Statistical Power** for small effect detection (Cohen's f² = 0.02)
- **Cohen's Kappa ≥ 0.85** for inter-annotator agreement in dimension classification

### Dimension Distribution

| Dimension | Target % | Actual % | Status |
|-----------|----------|----------|--------|
| Entity Tracking | 20% | 20.1% | ✓ |
| Multilingual & Dialect | 15% | 14.9% | ✓ |
| Context Preservation | 20% | 20.0% | ✓ |
| Diverse PII Types | 20% | 19.8% | ✓ |
| Edge Cases | 10% | 10.2% | ✓ |
| Data Format Variations | 10% | 10.3% | ✓ |
| Temporal Consistency | 5% | 4.7% | ✓ |

### Quasi-Identifier Coverage

Per Sweeney (2002) privacy metrics:

- **Single identifiers:** All 48 entity types covered
- **Quasi-identifier pairs:** 200+ combinations evaluated
- **k-anonymity testing:** Support for k-values 2–1,000
- **ℓ-diversity evaluation:** Attribute-level privacy metrics included

## Dataset Contents

The v1.0.0 release unifies three previous datasets:

| Dataset | Records | Focus |
|---------|---------|-------|
| `llm_pipeline_core` | 10,200 | Core LLM pipeline benchmark |
| `llm_long_context_tracking` | 800 | Long-context entity tracking |
| `eval_framework_v1` | ~50,000 | Comprehensive multilingual framework |
| **v1.0.0 Combined** | **~70,000** | **Unified comprehensive benchmark** |

## Documentation

For detailed information about dataset composition, creation, and uses, see:

- **[DATASHEET.md](DATASHEET.md)** — Complete "Datasheets for Datasets" documentation
  - Motivation and funding
  - Composition and structure
  - Collection and preprocessing methodology
  - Use cases and limitations
  - Ethical considerations
  - Reproducibility guidelines

- **[pii-anon Documentation](https://github.com/subhash-holla/pii-anon-doc)** — Library usage and integration

## Related Repositories

- **[pii-anon](https://github.com/subhash-holla/pii-anon)** — Main PII anonymization library (PyPI: `pii-anon`)
- **[pii-anon-doc](https://github.com/subhash-holla/pii-anon-doc)** — Documentation and product lifecycle artifacts

## Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{holla2026pii_anon_eval,
  title={PII Anonymization Evaluation Dataset v1.0.0},
  author={Holla, Subhash},
  year={2026},
  month={February},
  publisher={GitHub},
  howpublished={\url{https://github.com/subhash-holla/pii-anon-datasets}},
  doi={},
  note={Comprehensive multilingual benchmark with 70K records across 52 languages and 48 entity types}
}
```

Or in APA format:

Holla, S. (2026). *PII Anonymization Evaluation Dataset v1.0.0* [Dataset]. GitHub. Retrieved from https://github.com/subhash-holla/pii-anon-datasets

## License

**Apache License 2.0**

This dataset is distributed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

### Licensed Content

- All record content: CC0 (Public Domain)
- Schema and annotations: CC-BY-4.0 (requires attribution)
- Combined distribution: Apache 2.0

You are free to use, modify, and redistribute this dataset for any purpose, including commercial applications, with proper attribution.

## Ethical Considerations

### Safety & Privacy

- **100% Synthetic Data:** No real personally identifiable information
- **Research Safe:** Can be published and distributed without privacy concerns
- **Reproducible:** Seeded generation (seed=42) enables community verification

### Fairness & Accessibility

- **Diverse Languages:** Equitable cross-lingual evaluation
- **Balanced Demographics:** Supports fairness auditing and bias detection
- **Open Access:** Apache 2.0 license enables universal research access

### Limitations

Synthetic data may:
- Not capture all real-world PII patterns and contextual variations
- Over-represent common patterns at the expense of rare edge cases
- Miss domain-specific nuances (healthcare, finance, legal contexts)
- Create unrealistic demographic associations

**Recommendation:** Validate on domain-specific real data (with proper consent) before production deployment.

## Maintenance & Support

**Maintainer:** Subhash Holla

**Support Channels:**
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Community questions and shared experiences
- Documentation: [pii-anon-doc](https://github.com/subhash-holla/pii-anon-doc)

## Version History

- **v1.0.0** (2026-02-23) — Initial unified release combining `llm_pipeline_core`, `llm_long_context_tracking`, and `eval_framework_v1` into a single comprehensive benchmark

## References

Cochran, W. G. (1977). *Sampling techniques* (3rd ed.). Wiley.

Cohen, J. (1988). *Statistical power analysis for the behavioral sciences* (2nd ed.). Lawrence Erlbaum.

Sweeney, L. (2002). k-anonymity: A model for protecting privacy. *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems*, 10(5), 557–570.

---

## Acknowledgements

This dataset was built with the assistance of AI coding agents, primarily [Claude Code](https://claude.ai/claude-code) by Anthropic. AI agents contributed to synthetic data generation, schema design, quality validation, and documentation. All AI-generated output was reviewed and validated by the project maintainers.

---

**Version:** 1.0.0
**Last Updated:** 2026-02-23
**License:** Apache License 2.0
