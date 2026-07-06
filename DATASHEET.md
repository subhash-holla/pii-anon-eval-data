# Datasheet for PII-Anon Evaluation Dataset v2.2.0

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
782,677 records containing 3,107,240 annotations across 66 entity types.

The 159,891 `tier3_evaluation` records are the EVALUATION substrate of the 782,677-record corpus — behavioral-signal / RRS scoring runs on this substrate; the full corpus is the detection substrate. **79.2% of records carry `provenance.source_type="synthetic_lattice_enrichment"`** (the S-PWR formulaic enrichment that raises statistical power; it is not, by itself, evidence of real-world generalization).

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
Yes. Each annotation includes the entity type (66 types; canonical set in `pii_anon_datasets.taxonomy`), sensitivity class (direct_identifier, quasi_identifier, sensitive_attribute), and character offsets (start, end). The 9 special-category types include 6 powered GDPR Art-9 types (POLITICAL_OPINION, RELIGIOUS_BELIEF, ETHNICITY, SEXUAL_ORIENTATION, TRADE_UNION_MEMBERSHIP, GENETIC_DATA — all ≥400 spans, 12 languages; Art-9 synthetic values are English-anchored). `reg_gdpr` is now discriminative: a `_NON_PERSONAL` out-of-scope record set exists alongside in-scope records.

**8 of the 66** entity types are national/jurisdiction-specific identifiers (SSN, driver license, passport, national ID, tax ID, bank routing, health-insurance ID, license plate); this is **illustrative, NOT a per-jurisdiction completeness claim**.

**Is any information missing from individual instances?**
Optional fields (`query_context`, `adversarial.type`, `entity_tracking.coreference_chains`) are null/empty for records where they are not applicable.

**Are relationships between individual instances made explicit?**
Entity tracking records (25K+) contain coreference chains linking mentions of the same entity across the text. Ambiguous tracking records (3K) test disambiguation of shared name components.

**Are there recommended data splits?**
Yes. Stratified dev/test splits (10%/90%) are provided, stratified by dimension, language, and difficulty level.

**Are there any errors, sources of noise, or redundancies?**
All records have been validated for annotation offset accuracy (0 errors). Content hash deduplication removes exact duplicates. Template-based generation may produce similar structures across records.

**Gold-validity spot-check (single-pass author corroboration).** Beyond offset validation, a stratified ~500-span sample (6 priority scripts powered to n≥24; per-type coverage floor) was adjudicated by the author against the programmatic gold (`results/tier-a/gold_spotcheck.md`): **type-correctness 1.000** (Horvitz–Thompson inverse-probability-weighted to the corpus marginal; Wilson 95% [0.984, 1.000]), **realism 1.000**, a **blind type-recovery rate of 0.927** [0.868, 0.961] on the blind subset (124 spans) where the author named the entity type from context *before* the label was revealed (the anchoring-resistant complement to the self-adjudicated upper bound), and a **blind-realism rate of 1.000** [0.970, 1.000] (realism re-rated with the type label withheld). This is a **single-pass corroboration by ONE rater — NOT inter-annotator agreement / Cohen's kappa** (the corpus has no annotator panel; AX-002), and realism is the author's synthetic-plausibility judgment, **NOT external validity** (AX-001). It is a disclosed post-hoc audit (commissioned to address a "no human validation" reviewer objection) and does not substitute for real-text validation.

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

**What are the dataset's statistical-power limits?**
PII-Anon v2 is powered for all single-factor marginal recall claims (95% Wilson CIs; credential/financial-critical types to ±0.5pp at recall 0.99, standard to ±1pp at 0.98) and for three pre-registered 2-way interactions (language×entity-type on a committed rectangle, domain×track, adversarial-type×entity-type). The corpus carries a committed evaluation lattice powering **17 languages across 11 writing systems** (Latin, Han, Japanese, Hangul, Arabic, Devanagari, Cyrillic, Thai, Greek, Bengali, Hebrew) to statistically-calibrated positive-count targets (critical n≥1522, standard n≥753). It is not powered for the full multilingual×entity-type grid or any ≥3-way interaction; those are reported as exploratory. Synthetic-distribution power is not external validity — see the [External-Validity Protocol (FR-027)](docs/external-validity-protocol.md) and the real-data correlation slice.

**Honesty disclosures for utility, AI-era, and Tier-3 metrics (v2.1.0):**

*Utility metrics:* `semantic_similarity_*` fields in `context_preservation.utility_metrics` are **token-overlap Jaccard** (set intersection / union of whitespace tokens via `compute_token_overlap`), **not** semantic embedding similarity. `coherence_preserved_*` is an **assumed constant** (hardcoded `True`) rather than a measured coherence score. `information_loss_ratio` is an **entity-type prior** (a closed-form mapping over entity-type counts), not a measured information loss. Honest aliases `token_overlap_jaccard_*` are added in v2.1.0 and travel into the shipped data alongside the original fields.

*AI-era test cases:* The "250 each" headline counts (prompt-injection, RAG context, multi-agent, system-prompt-leakage) are full-corpus totals. The **test split** carries **51 / 50 / 57 / 41** records per category (prompt-injection / RAG context / multi-agent / system-prompt-leakage, by `document_type`; the full 250-each splits 70/10/20 across train/dev/test). These are **scenario fixtures** for detection evaluation, **not** a measured security evaluation. FR-017 (security-evaluation harness), FR-018, FR-019, and FR-020 (penetration-test-style adversarial generation) are not implemented in v2.x.

*Tier-3 / re-identification metrics:* **No record is demonstrated anonymised under GDPR Recital 26.** `tier3_risk_level` and `re_identification_resistance_score` (and its v2.1.0 alias `exposure_index_prior`) are **heuristic priors** computed from behavioral signal density, **not** the result of measured adversarial attacks. For a CI-bearing, attack-measured number, run the FR-007 MeasuredRRS adversary (see `results/tier-a/measured_rrs.md`). `anonymized_pseudonymized` and `anonymized_llm_sanitized` remain **personal data** under GDPR Art.4(5).

*Synthetic-value localization (v2.2 work-in-progress):* Non-name PII **values** (addresses, organizations, occupations, medical, identifiers, financial) are English/US-anchored synthetic across **all 60 languages**; per-language value localization is deferred to a later release (2D). Person-name values for `hi` and `th` are romanized Latin, not native-script (el/bn/he names ARE native-script: Greek/Bengali/Hebrew). `he` records mix right-to-left Hebrew names with left-to-right Latin identifiers/emails/URLs — a known display-realism limitation.

**What baseline detector numbers are published, and how should they be read?**
A reproducible leaderboard of the most-used PII pipelines — 8 local detectors (regex, Presidio, spaCy, GLiNER, Piiranha, scrubadub, Stanza, Flair) plus AWS/GCP/Azure cloud DLP (run on the full English test as a single budget-gated pass of non-deterministic managed services; an LLM detector remains behind a key) — is reported in [BASELINES.md](BASELINES.md), ranked by **F2** (recall-weighted — a missed PII is the costly error) with precision shown beside recall, per-entity-type / per-domain / per-language breakdowns, Wilson 95% CIs, and a per-detector label-map coverage (reachable / 66) disclosure. On the full English test, GLiNER (a free local model) matches AWS Comprehend on F2 (0.734 vs 0.736) through higher precision (0.813 vs 0.769), though a paired McNemar (χ²=145.9, p=1.4e-33) shows AWS holds a small but significant +1.19pp recall edge — a precision/recall trade-off, not a recall tie — and both outscore GCP DLP (0.704) and Azure AI Language (0.696). **Every number is a real detector on synthetic data (AX-001) — not an external-validity claim.** Headline matching is strict-v1 exact span match; a relaxed partial-overlap variant is reported separately and excluded from the CIs. The leaderboard is regenerable via `pii-anon baselines` and ships a run-record + sha256 provenance index.

## Distribution

**How will the dataset be distributed?**
Via GitHub repository and the `pii-anon-datasets` Python package (pip install).

**When was the dataset first released?**
v1.0.0: February 23, 2026. v1.1.0: March 21, 2026. v2.0.0: May 30, 2026.

**What license is the dataset distributed under?**
- Record content: CC0-1.0 (Public Domain Dedication -- no attribution required)
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
