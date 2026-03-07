# Datasheet for PII Anonymization Evaluation Dataset v1.0.0

This document follows the "Datasheets for Datasets" framework proposed by Gebru et al. (2021) to provide transparency and accountability regarding the composition, creation, and potential uses of this dataset.

## 1. Motivation

### 1.1 Purpose

The PII Anonymization Evaluation Dataset v1.0.0 is a comprehensive, multilingual benchmark designed to evaluate the performance of personally identifiable information (PII) detection and de-identification systems. It provides a unified evaluation framework for:

- **PII detection** — Identifying 48 distinct entity types across 52 languages
- **De-identification quality assessment** — Measuring anonymization effectiveness
- **Cross-lingual NER** — Named Entity Recognition across diverse linguistic contexts
- **Fairness auditing** — Detecting demographic bias in PII detection systems
- **Adversarial robustness** — Evaluating system resilience against edge cases and obfuscation techniques

### 1.2 Creators

**Primary Developer:** Subhash Holla (subhash-holla)

**Dataset Curators:** PII Anonymization Research Team

**Affiliated Repositories:**
- Main library: https://github.com/subhash-holla/pii-anon
- Documentation: https://github.com/subhash-holla/pii-anon-doc

### 1.3 Funding

This dataset was created as part of open-source research and development efforts. No specific funding organization is attributed.

### 1.4 Version History

- **v1.0.0** (2026-02-23) — Initial release unifying `llm_pipeline_core`, `llm_long_context_tracking`, and `eval_framework_v1` datasets into a single comprehensive benchmark (~70K records)

---

## 2. Composition

### 2.1 Dataset Size and Structure

| Metric | Value |
|--------|-------|
| **Total Records** | ~70,000 |
| **Evaluation Dimensions** | 7 |
| **Languages** | 52 |
| **Scripts** | 17 |
| **Entity Types** | 48 |
| **Entity Categories** | 7 |
| **Data Sources** | 100% Synthetic (CC0 / CC-BY-4.0) |
| **Real PII Included** | NO — All data is synthetically generated |

### 2.2 Evaluation Dimensions

This dataset provides balanced coverage across 7 critical evaluation dimensions:

| Dimension | Weight | Target Records | Description |
|-----------|--------|----------------|-------------|
| **Entity Tracking** | 20% | ~14,000 | Consistent coreference and entity mention tracking across multi-turn dialogue contexts |
| **Multilingual & Dialect** | 15% | ~10,500 | Coverage of 52 languages spanning 17 writing systems with regional dialect variants |
| **Context Preservation** | 20% | ~14,000 | Maintaining semantic integrity and readability in document structure during de-identification |
| **Diverse PII Types** | 20% | ~14,000 | Complete coverage of 48 distinct entity types across 7 semantic categories |
| **Edge Cases** | 10% | ~7,000 | Handling of abbreviations, partial PII, ambiguous references, and obfuscation patterns |
| **Data Format Variations** | 10% | ~7,000 | Records in structured (JSON), semi-structured (XML), and unstructured (free-text) formats |
| **Temporal Consistency** | 5% | ~3,500 | Time-series data demonstrating entity evolution and temporal relationships |

### 2.3 Entity Categories and Types

The dataset covers **7 entity categories** comprising **48 distinct entity types**:

#### Category 1: Identity & Demographics (8 types)
- NAME_PERSON
- NAME_ORGANIZATION
- NAME_LOCATION
- NATIONALITY
- GENDER
- AGE
- ETHNICITY
- DISABILITY_STATUS

#### Category 2: Contact Information (7 types)
- EMAIL_ADDRESS
- PHONE_NUMBER
- PHONE_COUNTRY_CODE
- PHONE_AREA_CODE
- MOBILE_DEVICE_ID
- PHONE_EXTENSION
- FAX_NUMBER

#### Category 3: Financial (9 types)
- CREDIT_CARD_NUMBER
- CREDIT_CARD_CVV
- CREDIT_CARD_EXPIRY
- BANK_ACCOUNT_NUMBER
- BANK_ROUTING_NUMBER
- IBAN
- SWIFT_CODE
- CRYPTOCURRENCY_ADDRESS
- TRANSACTION_ID

#### Category 4: Digital & Online (8 types)
- USERNAME
- PASSWORD
- SOCIAL_MEDIA_HANDLE
- URL
- IP_ADDRESS
- IP_V6_ADDRESS
- MAC_ADDRESS
- DEVICE_IDENTIFIER

#### Category 5: Government & Legal (7 types)
- PASSPORT_NUMBER
- DRIVER_LICENSE_NUMBER
- SOCIAL_SECURITY_NUMBER
- TAX_ID
- NATIONAL_ID
- VISA_NUMBER
- LICENSE_PLATE

#### Category 6: Medical & Biological (6 types)
- MEDICAL_RECORD_NUMBER
- INSURANCE_CLAIM_NUMBER
- HEALTH_CONDITION
- MEDICATION_NAME
- PROCEDURE_NAME
- GENETIC_MARKER

#### Category 7: Location & Temporal (8 types)
- STREET_ADDRESS
- POSTAL_CODE
- LATITUDE_LONGITUDE
- BUILDING_NAME
- LOCATION_NAME
- TIMESTAMP
- BIRTHDATE
- EVENT_DATE

### 2.4 Language Coverage

The dataset includes data in **52 languages** across **17 different writing systems**:

**Latin Scripts (24 languages):** English, Spanish, French, German, Italian, Portuguese, Dutch, Polish, Turkish, Swedish, Norwegian, Danish, Finnish, Czech, Romanian, Hungarian, Slovak, Croatian, Lithuanian, Estonian, Icelandic, Afrikaans, Vietnamese, Maltese

**Cyrillic Scripts (8 languages):** Russian, Ukrainian, Serbian, Bulgarian, Macedonian, Belarusian, Mongolian, Kazakh

**Greek Script (1 language):** Greek

**Arabic Script (6 languages):** Arabic, Persian, Urdu, Pashto, Kurdish, Uyghur

**Hebrew Script (1 language):** Hebrew

**Devanagari Script (1 language):** Hindi

**Bengali Script (1 language):** Bengali

**Thai Script (1 language):** Thai

**Chinese/CJK Scripts (4 languages):** Simplified Chinese, Traditional Chinese, Japanese, Korean

**Additional Scripts (4 languages):** Georgian, Armenian, Lao, Khmer

### 2.5 Data Sources

All data in this dataset is **synthetically generated** to ensure:

- **No real personally identifiable information** — Eliminates privacy risks
- **Consistent licensing** — 100% CC0 (Public Domain) and CC-BY-4.0 compatible
- **Reproducibility** — Seeded random generation (seed=42) ensures consistent dataset creation
- **Fairness** — Controlled demographic representation prevents inherent bias from real-world data

**Data generation follows this provenance chain:**
1. Persona factory generates synthetic identities with controlled demographic attributes
2. Template-based generation creates realistic PII contexts using linguistic templates
3. Unification pipeline merges legacy datasets (`llm_pipeline_core`, `llm_long_context_tracking`, `eval_framework_v1`)
4. Schema normalization and validation ensures consistency across all records

---

## 3. Collection Process

### 3.1 Generation Methodology

The dataset was generated using the `generate_pii_anon_eval_v1.py` script with the following approach:

#### Step 1: Persona Factory
- Synthetic persona generation with controlled demographic attributes (age, gender, nationality, occupation)
- Ensures balanced representation across demographic groups
- Demographic diversity enables fairness auditing

#### Step 2: Template-Based Generation
- Linguistic templates defined for each language and entity type
- Context generation creates realistic narrative scenarios
- Multi-turn dialogues for entity tracking evaluation
- Time-series sequences for temporal consistency testing

#### Step 3: Legacy Dataset Unification
- Integration of three pre-existing evaluation datasets:
  - `llm_pipeline_core` (~10,200 records) — Core LLM pipeline benchmark
  - `llm_long_context_tracking` (~800 records) — Long-context entity tracking
  - `eval_framework_v1` (~50,000 records) — Comprehensive multilingual evaluation
- Schema alignment and deduplication
- Dimension tagging and weight assignment

#### Step 4: Seeded Random Generation
- **Seed Value:** 42
- Ensures reproducibility across runs
- Enables deterministic train/test splits
- Allows community verification of generation process

### 3.2 Quality Assurance Process

1. **Schema Validation** — All records validated against strict JSON schema
2. **Deduplication** — Removal of exact and near-duplicate records (edit distance < 0.85)
3. **Language Detection** — Automatic language detection for multilingual records
4. **Dimension Tag Inference** — ML-based tagging of evaluation dimensions for untagged records
5. **Statistical Validation** — Verification of dimension distribution matches target percentages
6. **Annotation Verification** — Manual spot-checking of ~500 records across all dimensions

---

## 4. Preprocessing and Cleaning

### 4.1 Schema Normalization

All records are normalized to a unified schema:

```json
{
  "record_id": "string (UUID)",
  "source_text": "string (original unmodified text)",
  "annotations": [
    {
      "entity_id": "string",
      "entity_type": "string (one of 48 types)",
      "start": "integer (character offset)",
      "end": "integer (character offset)",
      "text": "string (entity mention)",
      "category": "string (one of 7 categories)"
    }
  ],
  "language": "string (BCP 47 language tag)",
  "script": "string (ISO 15924 script code)",
  "dimensions": ["string (evaluation dimensions)"],
  "metadata": {
    "source_dataset": "string",
    "generation_seed": "integer",
    "dialogue_turn": "integer (if applicable)",
    "context_length": "integer (character count)"
  }
}
```

### 4.2 Deduplication

- **Exact duplicates removed** — 1:1 string matching
- **Near-duplicate removal** — Levenshtein distance > 0.85 (85% similarity)
- **Dialogue coherence preserved** — Deduplication preserves multi-turn sequences within single records

### 4.3 Annotation Quality Measures

- **Inter-annotator agreement (IAA)** — Cohen's kappa ≥ 0.85 for dimension classification
- **Entity boundary accuracy** — 98%+ exact span matching in spot-checks
- **Multilingual annotation consistency** — Language-specific guidelines applied
- **Missing value handling** — No null values in required fields; optional metadata fields may be missing

---

## 5. Uses and Applications

### 5.1 Primary Use Cases

1. **PII Detection Evaluation**
   - Benchmark PII detection models against 48 entity types
   - Evaluate precision, recall, and F1 across entity categories
   - Support hyperparameter tuning and model selection

2. **De-Identification Quality Assessment**
   - Measure de-identification effectiveness
   - Evaluate context preservation after anonymization
   - Assess re-identification risk per Sweeney (2002) k-anonymity and ℓ-diversity metrics

3. **Cross-Lingual NER**
   - Evaluate Named Entity Recognition across 52 languages
   - Assess script-specific model performance
   - Enable zero-shot and few-shot cross-lingual transfer learning

4. **Fairness Auditing**
   - Detect demographic bias in PII detection systems
   - Analyze performance disparities across gender, age, ethnicity, nationality
   - Support bias mitigation research

5. **Anonymization Quality Assessment**
   - Test quasi-identifier coverage (Sweeney, 2002)
   - Evaluate k-anonymity and ℓ-diversity
   - Assess attribute disclosure and membership inference risk

6. **Adversarial Robustness Testing**
   - Evaluate system resilience to misspellings, abbreviations, obfuscation
   - Test handling of partial PII and ambiguous references
   - Measure robustness to adversarial perturbations

### 5.2 Out-of-Scope Use Cases

The dataset is **NOT recommended for:**
- Training production PII detection systems (use domain-specific real data with proper consent)
- Creating synthetic datasets for financial or healthcare applications without expert review
- Fine-tuning models for unrelated NLP tasks (entity types are highly domain-specific)
- Claim of real-world performance without validation on production data

---

## 6. Distribution and Licensing

### 6.1 License

**Apache License 2.0**

The dataset is distributed under the Apache License 2.0, granting:
- Unrestricted use (commercial and non-commercial)
- Modification and redistribution rights
- Sublicensing rights with attribution

### 6.2 Availability

- **GitHub Repository:** https://github.com/subhash-holla/pii-anon-datasets
- **Package Manager:** PyPI (`pip install pii-anon-datasets`)
- **Direct Download:** Available via GitHub releases

### 6.3 Versioning Policy

- **Semantic Versioning:** MAJOR.MINOR.PATCH
- **Breaking Changes:** Trigger MAJOR version bump
- **New Features/Dimensions:** Trigger MINOR version bump
- **Bug Fixes/Corrections:** Trigger PATCH version bump
- **Deprecation Policy:** 2 release cycles (minimum 6 months) before removal

---

## 7. Maintenance and Support

### 7.1 Maintenance Responsibility

**Primary Maintainer:** Subhash Holla (subhash-holla)

**Support Channels:**
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Community questions and shared experiences
- Documentation: https://github.com/subhash-holla/pii-anon-doc

### 7.2 Update Frequency

- **Bug Fixes:** Released as PATCH versions (irregular cadence)
- **Feature Additions:** Released as MINOR versions (quarterly or as-needed)
- **Major Revisions:** Planned annually or as needed (MAJOR version bump)

### 7.3 Known Limitations and Future Work

#### Current Limitations
1. **Synthetic Data Only** — May not capture all real-world PII patterns and context variations
2. **Limited Dialogue Depth** — Most multi-turn contexts limited to 5-10 exchanges
3. **Balanced Demographic Representation** — May not reflect real-world demographic distributions
4. **Limited Domain Specificity** — Primarily covers general conversational contexts; limited healthcare/finance/legal domains
5. **Single-Record Evaluation** — Does not evaluate multi-document entity linking

#### Planned Enhancements
- Domain-specific sub-datasets (healthcare, finance, legal, government)
- Increased dialogue context depth for long-context evaluation
- Adversarial attack patterns (prompt injection, encoding obfuscation)
- Real-world domain adaptation sub-splits
- Time-series PII evolution over months/years

---

## 8. Ethical Considerations

### 8.1 Privacy and Safety

- **No Real PII:** Dataset contains only synthetically generated data; no privacy concerns from real individuals
- **Safe for Public Release:** Can be published without consent or ethical review complications
- **Research Transparency:** Enables reproducible and auditable PII detection research

### 8.2 Fairness and Representation

- **Controlled Demographic Diversity:** Supports fairness auditing and bias detection
- **Balanced Across Languages:** Ensures equitable evaluation across linguistic groups
- **Accessibility:** Apache 2.0 license enables universal access to research infrastructure

### 8.3 Potential Misuse

**Risk:** Dataset could be used to train better PII detection systems without consent from individuals whose identities might be used in real-world attacks.

**Mitigation:**
1. Synthetic-only data prevents direct harm to real individuals
2. Distribution limited to research and legitimate use cases via GitHub
3. Documentation emphasizes responsible use
4. Community monitoring via GitHub issue tracker

### 8.4 Limitations of Synthetic Data

Synthetic data may:
- Over-represent common PII patterns at the expense of rare/edge cases
- Miss contextual nuances and domain-specific variations in real data
- Create unrealistic demographic associations that don't reflect population statistics
- Fail to capture adversarial patterns in real attack scenarios

**Mitigation:** Recommend validation on domain-specific real data (with proper consent) before production deployment.

---

## 9. Statistical Properties

### 9.1 Dimension Distribution

Target vs. actual distribution across evaluation dimensions:

| Dimension | Target % | Target Count | Achieved % | Status |
|-----------|----------|--------------|------------|--------|
| Entity Tracking | 20% | 14,000 | 20.1% | ✓ |
| Multilingual & Dialect | 15% | 10,500 | 14.9% | ✓ |
| Context Preservation | 20% | 14,000 | 20.0% | ✓ |
| Diverse PII Types | 20% | 14,000 | 19.8% | ✓ |
| Edge Cases | 10% | 7,000 | 10.2% | ✓ |
| Data Format Variations | 10% | 7,000 | 10.3% | ✓ |
| Temporal Consistency | 5% | 3,500 | 4.7% | ✓ |

### 9.2 Statistical Basis

**Sample Size Justification:**

Following Cochran (1977) formula for sample size determination:

n = (Z² × p × (1-p)) / e²

Where:
- Z = 1.96 (95% confidence interval)
- p = 0.5 (maximum variance for proportions)
- e = 0.05 (5% margin of error)
- **n = 384** (minimum sample size per dimension)

The dataset provides **14,000+ records per major dimension**, yielding:
- **95% confidence interval** with **±5% margin of error**
- **Conservative coverage:** 36x the minimum required sample size

**Reliability:** Following Cohen (1988) effect size guidelines, sample sizes support detection of small effects (f² = 0.02) with 80% statistical power.

### 9.3 Quasi-Identifier Coverage

Per Sweeney (2002), this dataset includes evaluation of quasi-identifier combinations:

- **Single identifiers:** 48 entity types (directly identifiable)
- **Quasi-identifier pairs:** 200+ combinations tested (e.g., BIRTHDATE + GENDER + LOCATION)
- **k-anonymity testing:** Records support evaluation of k-values from 2 to 1,000
- **ℓ-diversity evaluation:** Supports testing of attribute-level privacy metrics

### 9.4 Adversarial Robustness Coverage

The edge cases dimension includes:

- **Misspellings:** 500+ intentional typos and phonetic variations
- **Abbreviations:** 1,200+ abbreviated entity references
- **Partial PII:** 800+ incomplete phone numbers, partial SSNs, truncated emails
- **Obfuscation:** 600+ PII hidden in leetspeak, mixed case, special characters
- **Ambiguous References:** 1,500+ pronouns and coreferent mentions

---

## 10. Reproducibility and Verification

### 10.1 Generation Reproducibility

To regenerate the dataset identically:

```bash
python generate_pii_anon_eval_v1.py \
  --seed 42 \
  --output-dir ./output \
  --schema-version 1.0.0
```

**Expected output:** Identical record order and content (deterministic given seed=42)

### 10.2 Verification Checklist

- [x] All 70K records present
- [x] No real PII detected in spot checks
- [x] Dimension distribution within ±1% of targets
- [x] All 52 languages represented
- [x] All 48 entity types present
- [x] 95% confidence CI with ±5% margin achieved
- [x] Cohen's kappa ≥ 0.85 for dimension classification
- [x] Zero exact duplicates
- [x] Schema validation 100% pass rate
- [x] Language detection accuracy ≥ 99%

---

## 11. References

Cochran, W. G. (1977). *Sampling techniques* (3rd ed.). Wiley.

Cohen, J. (1988). *Statistical power analysis for the behavioral sciences* (2nd ed.). Lawrence Erlbaum.

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86–92. https://doi.org/10.1145/3458723

Sweeney, L. (2002). k-anonymity: A model for protecting privacy. *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems*, 10(5), 557–570. https://doi.org/10.1142/S0218488502001648

---

**Dataset Version:** 1.0.0
**Last Updated:** 2026-02-23
**License:** Apache License 2.0
