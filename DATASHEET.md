# Datasheet for PII-Anon Evaluation Dataset v1.1.0

Following the framework proposed by Gebru et al. (2021), "Datasheets for Datasets."

## Motivation

**For what purpose was the dataset created?**
The PII-Anon Evaluation Dataset was created to provide a comprehensive, multilingual benchmark for evaluating PII (Personally Identifiable Information) detection and de-identification systems. Existing benchmarks are predominantly English-only, limited in entity type coverage, and lack structured evaluation across multiple difficulty dimensions.

**Who created the dataset and on behalf of which entity?**
Subhash Holla, as part of the pii-anon-core project for PII anonymization and pseudonymization research.

**Who funded the creation of the dataset?**
Self-funded research project with no external funding.

## Composition

**What do the instances that comprise the dataset represent?**
Each instance is a text record containing one or more PII entities with character-level annotations. Records span unstructured text, structured forms, code snippets, log entries, CSV data, and other document types.

**How many instances are there in total?**
117,752 records containing 919,000+ annotations across 57 entity types.

**Does the dataset contain all possible instances or is it a sample?**
The dataset is a purposefully constructed sample designed to provide balanced coverage across 60 languages, 7 evaluation dimensions, 4 domain verticals, and 4 difficulty levels.

**What data does each instance consist of?**
Each record contains:
- `text`: The source text containing PII entities
- `annotations`: Array of character-level PII span annotations with entity type, sensitivity class, and coreference metadata
- Language and script metadata
- Evaluation dimension and difficulty classification
- Privacy risk scoring (quasi-identifiers, k-anonymity estimate)
- Regulatory domain tags (GDPR, HIPAA, CCPA, PCI-DSS, SOX, LGPD, PIPA)
- Optional query context for RAG evaluation

**Is there a label or target associated with each instance?**
Yes. Each annotation includes the entity type (57 types), sensitivity class (direct_identifier, quasi_identifier, sensitive_attribute), and character offsets (start, end).

**Is any information missing from individual instances?**
Optional fields (`query_context`, `adversarial.type`, `entity_tracking.coreference_chains`) are null/empty for records where they are not applicable.

**Are relationships between individual instances made explicit?**
Entity tracking records (25K+) contain coreference chains linking mentions of the same entity across the text. Ambiguous tracking records (3K) test disambiguation of shared name components.

**Are there recommended data splits?**
Yes. Stratified dev/test splits (10%/90%) are provided, stratified by dimension, language, and difficulty level.

**Are there any errors, sources of noise, or redundancies?**
All records have been validated for annotation offset accuracy (0 errors). Content hash deduplication removes exact duplicates. Template-based generation may produce similar structures across records.

**Is the dataset self-contained?**
Yes. No external data or resources are needed to use the dataset.

**Does the dataset contain data that might be considered confidential?**
No. All data is 100% synthetic. No real PII is present.

**Does the dataset contain data that might be considered offensive?**
No. Templates and PII values are designed to be neutral and inoffensive.

## Collection Process

**How was the data associated with each instance acquired?**
All data is synthetically generated using template-based expansion with the PIIFactory class, which produces realistic but entirely fictional PII values. V1 records were migrated from an earlier dataset version with schema canonicalization and quality filtering.

**What mechanisms or procedures were used to collect the data?**
1. Template-based record generation (`scripts/generate_records.py`) using 40+ PII value generators
2. V1-to-v1.1 migration (`scripts/migrate_v1_to_v2.py`) with deduplication and placeholder filtering
3. Coverage fill generation (`scripts/generate_coverage_fill.py`) to ensure statistical completeness
4. Enrichment (`scripts/enrich.py`) for query context, adversarial taxonomy, and k-anonymity

**If the dataset is a sample from a larger set, what was the sampling strategy?**
Not applicable — the dataset is constructed, not sampled.

**Who was involved in the data collection process?**
The dataset creator (Subhash Holla) with AI coding assistance from Claude Code (Anthropic). All AI-generated output was reviewed and validated.

**Over what timeframe was the data collected?**
February–March 2026.

**Were any ethical review processes conducted?**
No formal IRB review was required as all data is synthetic with no human subjects.

## Preprocessing/Cleaning/Labeling

**Was any preprocessing/cleaning/labeling of the data done?**
- Template placeholder filtering: Records with unresolved `{placeholder}` text were excluded
- Annotation offset validation: All character offsets verified against source text
- Overlapping annotation removal: Contained spans removed (longest span kept)
- Entity type canonicalization: V1 type names mapped to canonical v1.1.0 names
- Content hash deduplication: Exact duplicate records removed

**Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data?**
The v1 dataset is preserved in the git history. The migration and generation scripts are included for full reproducibility.

**Is the software that was used to preprocess/clean/label the data available?**
Yes. All scripts are included in the `scripts/` directory of this repository.

## Uses

**Has the dataset been used for any tasks already?**
The dataset is designed for benchmarking PII detection and de-identification systems within the pii-anon-core framework.

**What (other) tasks could the dataset be used for?**
- Named Entity Recognition (NER) for PII types
- Multilingual NER evaluation
- Coreference resolution evaluation
- Adversarial robustness testing for NLP systems
- Privacy risk assessment research
- Regulatory compliance evaluation

**Is there anything about the composition of the dataset or the way it was collected that might impact future uses?**
The dataset is 100% synthetic. Performance on this benchmark may not directly translate to performance on real-world PII detection tasks, particularly for domain-specific jargon, formatting patterns, or culturally specific PII formats not covered by the templates.

**Are there tasks for which the dataset should not be used?**
- Training PII detection models (the dataset is designed for evaluation, not training)
- As a source of "real" PII for any purpose
- As ground truth for regulatory compliance decisions

## Distribution

**How will the dataset be distributed?**
Via GitHub repository and the `pii-anon-datasets` Python package (pip install).

**When was the dataset first released?**
v1.0.0: February 23, 2026. v1.1.0: March 21, 2026.

**What license is the dataset distributed under?**
- Record content: CC0 (Public Domain) / CC-BY-4.0
- Schema and code: Apache License 2.0

**Are there any fees or access restrictions?**
No. The dataset is freely available.

## Maintenance

**Who maintains the dataset?**
Subhash Holla.

**How can the dataset be updated?**
New records can be generated using the included pipeline scripts. The dataset follows semantic versioning.

**Will older versions of the dataset continue to be supported?**
v1.0.0 is preserved in the git history. The `MIGRATION.md` file documents how to migrate from v1.0.0 to v1.1.0.

**How will updates be communicated?**
Through the `CHANGELOG.md` file and GitHub releases.
