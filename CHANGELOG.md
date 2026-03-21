# Changelog

All notable changes to the PII-Anon Evaluation Dataset are documented here.

## [2.0.0] - 2026-03-20

### Major Restructuring

**Schema & Organization**
- Unified 5 v1 JSONL files (2 lineages, inconsistent schemas) into single canonical `pii_anon_v2.jsonl.gz`
- Removed old `benchmarks/` and `eval_framework/` directories
- Added `subsets/` directory with dimension, domain, and difficulty breakdowns
- Added stratified `splits/` with 10/90 dev/test split
- Defined JSON Schema (`pii_anon_v2.schema.json`) for record validation

**Data Quality**
- Excluded ~50K records with unresolved template placeholders and broken annotation offsets
- Fixed overlapping and duplicate annotations in entity tracking records
- Canonicalized entity type names (e.g., `CREDIT_CARD` -> `CREDIT_CARD_NUMBER`, `US_SSN` -> `SOCIAL_SECURITY_NUMBER`)
- Validated all 105K records: 0 annotation offset errors

**Content Expansion**
- Scaled from 68K clean migrated records to 105K total with 37K new generated records
- Expanded entity types from 50 to 57
- Added 4 domain subsets: clinical (11.7K), financial (14.6K), legal (3K), technology (5.7K)
- Grew entity tracking from 10.6K to 20.6K records (19.6% of dataset)
- Grew edge cases from 3.9K to 10.9K records with adversarial taxonomy
- Grew temporal consistency from 2.7K to 5.7K records
- Grew format variations from 1.5K to 5.5K records

**New Capabilities**
- Sensitivity classification on all 830K annotations (`direct_identifier`, `quasi_identifier`, `sensitive_attribute`)
- Query-aware PII detection annotations on 5K records (`query_context` field)
- Structured adversarial taxonomy on 11K records (leetspeak, partial redaction, format noise, etc.)
- Regulatory domain tagging on all records (GDPR, HIPAA, CCPA, PCI-DSS)
- Per-record re-identification risk scoring with k-anonymity estimates
- Coreference chains in entity tracking records (`cluster_id`, `mention_variant`)

**Documentation**
- `TAXONOMY.md`: Complete entity type taxonomy with definitions, sensitivity classes, and regulatory mapping
- `COMPARISON.md`: Head-to-head comparison with 7 competing benchmarks
- `CHANGELOG.md`: This file
- Updated `README.md` with v2 structure, statistics, and usage examples

**Pipeline Scripts**
- `scripts/migrate_v1_to_v2.py`: V1-to-v2 migration with deduplication, canonicalization, and placeholder filtering
- `scripts/generate_records.py`: Template-based record generation with PIIFactory (40+ generators, 7 languages)
- `scripts/merge_and_rebuild.py`: Merge migrated + generated records, build metadata
- `scripts/validate_v2.py`: Comprehensive validation (offsets, overlaps, entity types, placeholders, schema)
- `scripts/generate_subsets.py`: Generate dimension/domain/difficulty subsets and stratified splits
- `scripts/enrich_pr3.py`: Add query_context, adversarial taxonomy, and k-anonymity estimates

## [1.0.0] - 2026-02-23

### Initial Release
- 3 dataset lineages: `llm_pipeline_core` (10.2K), `llm_long_context_tracking` (800), `eval_framework_v1` (~50K)
- 52 languages, 48 entity types (inconsistent naming across lineages)
- 7 evaluation dimensions (imbalanced: 74% multilingual, 2% entity tracking)
- Known issues: ~50K records with template placeholders, overlapping annotations
