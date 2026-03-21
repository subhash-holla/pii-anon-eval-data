# Changelog

All notable changes to the PII-Anon Evaluation Dataset are documented here.

## [1.1.0] - 2026-03-21

### Major Restructuring

**Schema & Organization**
- Unified 5 v1 JSONL files (2 lineages, inconsistent schemas) into single canonical `pii_anon.jsonl.gz`
- Removed old `benchmarks/` and `eval_framework/` directories
- Added `subsets/` directory with dimension, domain, and difficulty breakdowns
- Added stratified `splits/` with 10/90 dev/test split
- Defined JSON Schema (`pii_anon.schema.json`) for record validation

**Data Quality**
- Excluded ~50K records with unresolved template placeholders and broken annotation offsets
- Fixed overlapping and duplicate annotations in entity tracking records
- Canonicalized entity type names (e.g., `CREDIT_CARD` -> `CREDIT_CARD_NUMBER`, `US_SSN` -> `SOCIAL_SECURITY_NUMBER`)
- Validated all 117K records: 0 annotation offset errors

**Content Expansion**
- Scaled from 68K clean migrated records to 117K total with 49K new generated records
- Expanded languages from 52 to 60 (added Sinhala, Nepali, Azerbaijani, Catalan, Albanian, Zulu, Welsh, Latvian)
- Expanded entity types from 50 to 57
- Added 4 domain subsets: clinical (11.7K), financial (14.6K), legal (3K), technology (7.3K)
- Grew entity tracking from 10.6K to 25.2K records (21.4% of dataset)
- Added 3K ambiguous entity tracking records (shared first/last names between distinct persons)
- Grew edge cases from 3.9K to 12.4K records with adversarial taxonomy
- Grew temporal consistency from 2.7K to 7.4K records
- Grew format variations from 1.5K to 7.2K records

**Statistical Coverage**
- Every language × dimension cell (60 × 7 = 420 cells) has ≥30 records
- Coverage fill script (`generate_coverage_fill.py`) ensures statistically meaningful evaluation per language per dimension
- Name databases for 28 languages support native name generation

**New Capabilities**
- Sensitivity classification on all 914K annotations (`direct_identifier`, `quasi_identifier`, `sensitive_attribute`)
- Query-aware PII detection annotations on 8.2K records (`query_context` field)
- Structured adversarial taxonomy on 15.6K records (leetspeak, partial redaction, format noise, name collision, etc.)
- Ambiguous entity tracking: 3K records with shared name components and `tracking_difficulty: "ambiguous"`
- Regulatory domain tagging with 7 frameworks (GDPR, HIPAA, CCPA, PCI-DSS, SOX, LGPD, PIPA)
- Per-record re-identification risk scoring with k-anonymity estimates
- Coreference chains in entity tracking records (`cluster_id`, `mention_variant`)

**Documentation**
- `TAXONOMY.md`: Complete entity type taxonomy with definitions, sensitivity classes, and regulatory mapping
- `COMPARISON.md`: Head-to-head comparison with 7 competing benchmarks
- `DATASHEET.md`: Gebru et al. (2021) datasheet for transparency and accountability
- `MIGRATION.md`: v1.0.0 → v1.1.0 migration guide with schema changes and entity type mapping
- `CHANGELOG.md`: This file
- Updated `README.md` with v1.1.0 structure, statistics, and usage examples

**Pipeline Scripts**
- `scripts/migrate_v1_to_v2.py`: v1.0.0-to-v1.1.0 migration with deduplication, canonicalization, and placeholder filtering
- `scripts/generate_records.py`: Template-based record generation with PIIFactory (40+ generators, 28 languages, ambiguous tracking)
- `scripts/generate_coverage_fill.py`: Fill language×dimension coverage matrix to ≥30 per cell
- `scripts/merge_and_rebuild.py`: Merge migrated + generated records, build metadata
- `scripts/validate.py`: Comprehensive validation (offsets, overlaps, entity types, placeholders, schema)
- `scripts/generate_subsets.py`: Generate dimension/domain/difficulty subsets and stratified splits
- `scripts/enrich.py`: Add query_context, adversarial taxonomy, k-anonymity, and regulatory tags

## [1.0.0] - 2026-02-23

### Initial Release
- 3 dataset lineages: `llm_pipeline_core` (10.2K), `llm_long_context_tracking` (800), `eval_framework_v1` (~50K)
- 52 languages, 48 entity types (inconsistent naming across lineages)
- 7 evaluation dimensions (imbalanced: 74% multilingual, 2% entity tracking)
- Known issues: ~50K records with template placeholders, overlapping annotations
