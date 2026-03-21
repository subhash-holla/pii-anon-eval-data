# Migration Guide: v1.0.0 → v1.1.0

This guide covers the changes between PII-Anon Evaluation Dataset v1.0.0 and v1.1.0, and how to update your code.

## Schema Changes

### Renamed Fields

| v1 Field | v1.1 Field | Notes |
|----------|----------|-------|
| `source_id` | `record_id` | UUIDs regenerated for all records |
| `entity_label` | `entity_type` | Canonical names (see Entity Type Mapping) |
| `span_start` | `start` (in annotation) | Same semantics |
| `span_end` | `end` (in annotation) | Same semantics |
| `entity_text` | `text` (in annotation) | Same semantics |

### New Fields in v1.1.0

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Always `"1.1.0"` |
| `annotations[].entity_id` | string | Record-local ID (`e0`, `e1`, ...) |
| `annotations[].category` | string | One of 9 entity categories |
| `annotations[].sensitivity_class` | string | `direct_identifier`, `quasi_identifier`, or `sensitive_attribute` |
| `annotations[].cluster_id` | string/null | Coreference cluster for entity tracking |
| `annotations[].mention_variant` | string/null | `full_name`, `first_name`, `formal`, etc. |
| `script` | string | ISO 15924 writing script code |
| `language_family` | string | Language family classification |
| `resource_level` | string | `high`, `medium`, or `low` |
| `primary_dimension` | string | Primary evaluation dimension |
| `dimensions` | array | All applicable dimensions |
| `data_type` | string | `unstructured_text`, `code`, `form`, etc. |
| `document_type` | string/null | Specific document type |
| `domain` | string | `general`, `clinical`, `financial`, `legal`, `technology` |
| `difficulty_level` | string | `easy`, `moderate`, `hard`, `challenging` |
| `context_length_tier` | string | `short`, `medium`, `long`, `very_long` |
| `token_count` | integer | Approximate word count |
| `entity_tracking` | object | Coreference chain metadata |
| `adversarial` | object | Adversarial technique classification |
| `privacy_risk` | object | Quasi-identifier analysis and k-anonymity |
| `regulatory_domains` | array | Applicable frameworks (GDPR, HIPAA, etc.) |
| `query_context` | object/null | Query-aware PII detection context |
| `provenance` | object | Source type, license, generation seed |

### Removed Fields

| v1 Field | Notes |
|----------|-------|
| `source_dataset` | Replaced by `provenance.source_type` |
| `generation_method` | Replaced by `provenance` object |
| `raw_label` | Replaced by canonical `entity_type` |

## Entity Type Mapping

Entity types were canonicalized in v1.1.0. Key renames:

| v1 Type | v1.1 Type |
|---------|---------|
| `CREDIT_CARD` | `CREDIT_CARD_NUMBER` |
| `US_SSN` | `SOCIAL_SECURITY_NUMBER` |
| `SSN` | `SOCIAL_SECURITY_NUMBER` |
| `FULL_NAME` | `PERSON_NAME` |
| `FIRST_NAME` | `PERSON_NAME` |
| `LAST_NAME` | `PERSON_NAME` |
| `NAME` | `PERSON_NAME` |
| `ORGANIZATION` | `ORGANIZATION_NAME` |
| `LOCATION` | `LOCATION_NAME` |
| `EMAIL` | `EMAIL_ADDRESS` |
| `PHONE` | `PHONE_NUMBER` |
| `ADDRESS` | `STREET_ADDRESS` |
| `DOB` | `DATE_OF_BIRTH` |
| `IP` | `IP_ADDRESS` |
| `BANK_ACCOUNT` | `BANK_ACCOUNT_NUMBER` |
| `ROUTING_NUMBER` | `BANK_ROUTING_NUMBER` |
| `LICENSE_NUMBER` | `DRIVER_LICENSE_NUMBER` |
| `PASSPORT` | `PASSPORT_NUMBER` |
| `INSURANCE_ID` | `HEALTH_INSURANCE_ID` |
| `MRN` | `MEDICAL_RECORD_NUMBER` |
| `DIAGNOSIS` | `HEALTH_CONDITION` |
| `MEDICATION` | `MEDICATION_NAME` |
| `VIN` | `VEHICLE_IDENTIFICATION_NUMBER` |

Full mapping is in `scripts/migrate_v1_to_v2.py` → `ENTITY_TYPE_MAP`. (The script retains the "v1_to_v2" name for historical clarity.)

## File Structure Changes

### v1 Structure
```
benchmarks/
  llm_pipeline_core/
    pii_core_benchmark.jsonl
    pii_core_benchmark_multilingual.jsonl
  llm_long_context_tracking/
    tracking_scenarios.jsonl
  eval_framework_v1/
    eval_v1_full.jsonl.gz
    eval_v1_corrections.jsonl.gz
```

### v1.1.0 Structure
```
src/pii_anon_datasets/
  data/
    pii_anon.jsonl.gz             # Single canonical dataset
    pii_anon.metadata.json        # Distribution statistics
    pii_anon.schema.json          # JSON Schema
  subsets/
    by_dimension/                 # 7 dimension subsets
    by_domain/                    # 4 domain subsets
    by_difficulty/                # 4 difficulty subsets
  splits/
    dev.jsonl.gz                  # 10% stratified dev set
    test.jsonl.gz                 # 90% stratified test set
```

## API Changes

### v1 Usage
```python
# v1 had no unified API — files were loaded manually
import json
with open("benchmarks/llm_pipeline_core/pii_core_benchmark.jsonl") as f:
    records = [json.loads(line) for line in f]
```

### v1.1.0 Usage
```python
from pii_anon_datasets import load_dataset

# Load full dataset
records = load_dataset()

# Load by dimension, domain, split, or language
entity_tracking = load_dataset(subset="entity_tracking")
clinical = load_dataset(domain="clinical")
dev = load_dataset(split="dev")
german = load_dataset(language="de")
```

## Running the Migration Pipeline

To reproduce the v1.0.0 → v1.1.0 migration:

```bash
# 1. Migrate v1 records to v1.1.0 schema
python scripts/migrate_v1_to_v2.py

# 2. Generate new synthetic records
PYTHONPATH=. python scripts/generate_records.py --all

# 3. Merge migrated + generated records
python scripts/merge_and_rebuild.py

# 4. Enrich with query context, adversarial taxonomy, k-anonymity
python scripts/enrich.py

# 5. Fill coverage matrix (every language×dimension ≥ 30 records)
PYTHONPATH=. python scripts/generate_coverage_fill.py

# 6. Validate
PYTHONPATH=. python scripts/validate.py

# 7. Generate subsets and splits
PYTHONPATH=. python scripts/generate_subsets.py
```

## Data Quality Improvements

Records excluded during migration:
- ~50K records with unresolved template placeholders (`{name}`, `{email}`, etc.)
- Records with annotation offsets that don't match the source text
- Exact duplicate records (by content hash)
- Records with overlapping annotations (resolved by keeping the longest span)

## Statistics Comparison

| Property | v1.0.0 | v1.1.0 |
|----------|--------|--------|
| Total records | ~68K (clean) | 117,752 |
| Entity types | 48 (inconsistent naming) | 57 (canonical) |
| Languages | 52 | 60 |
| Writing scripts | 23 | 23+ |
| Evaluation dimensions | 7 (imbalanced) | 7 (balanced, ≥30 per cell) |
| Domain subsets | 0 | 4 |
| Coreference records | ~800 | 25,207 |
| Ambiguous tracking | 0 | 3,000 |
| Query-aware records | 0 | 8,168 |
| Adversarial records | 0 | 15,565 |
| Sensitivity classes | No | All records |
| Regulatory tags | No | All records |
| Dev/test splits | No | Stratified 10/90 |
