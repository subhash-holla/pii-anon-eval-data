# Benchmark Dataset Comparison

Head-to-head comparison of PII-Anon Evaluation Dataset v1.3.0 against major competing benchmarks for PII detection, anonymization, and re-identification resistance evaluation.

## Three-Tier Evaluation Coverage

PII-Anon is the only dataset providing comprehensive coverage across all three tiers of PII protection:

| Tier | What It Evaluates | PII-Anon v1.3 | Nemotron | AI4Privacy | Gretel | PII-Bench | TAB | PIILO | SPY | BigCode |
|------|-------------------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **Tier 1**: Entity-level detection | Precision, recall, F1, F2 | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| **Tier 2**: Anonymization quality | Utility metrics + multiple variants | **YES (4 variants)** | No | No | Quality scores | No | Privacy/utility split | No | No | No |
| **Tier 3**: LLM re-identification resistance | Behavioral signals + RRS + paired profiles | **YES (NEW)** | No | No | No | No | No | No | No | No |

## Feature Comparison Matrix

| Feature | PII-Anon v1.3 | Nemotron-PII | AI4Privacy | Gretel Finance | PII-Bench | TAB | PIILO | SPY | BigCode PII |
|---------|:-----------:|:------------:|:----------:|:-----------:|:---------:|:---:|:-----:|:---:|:-----------:|
| **Records** | **160K** | 200K | 580K | 56K | 2.8K | 1.3K | 22K | 8.7K | 12K |
| **Languages** | **60** | 1 | 8 | 7 | 1 | 1 | 1 | 1 | 1 |
| **Writing scripts** | **32** | 1 | 3 | 1 | 1 | 1 | 1 | 1 | 1 |
| **Entity types** | **65** | 55+ | 20-54 | 18 | 55 | Semantic | 14 | 7 | 6 |
| **Document types** | **40** | 50+ | ~5 | 100+ | ~5 | 1 | 1 | 2 | Code |
| **Anonymized variants per record** | **4 (masked, pseudo, generalized, llm-sanitized)** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Behavioral signals (Tier 3)** | **All 160K records, 6 categories** | No | No | No | No | No | No | No | No |
| **Re-identification Resistance Score (RRS)** | **All 160K records** | No | No | No | No | No | No | No | No |
| **Paired persona profiles** | **2,500 personas / 5K records** | No | No | No | No | No | No | No | No |
| **ESRC-attack evaluation records** | **2,003** | No | No | No | No | No | No | No | No |
| **Eval dimensions** | **7** | - | - | - | 2 | - | - | - | - |
| **Coreference** | **25K records** | No | No | No | No | Yes (small) | No | No | No |
| **Query-aware** | **13K records** | No | No | No | 2.8K | No | No | No | No |
| **Sensitivity class** | **All records** | No | No | No | No | Yes | No | No | No |
| **Domain subsets** | **5 domains** | 50+ industries | 3-4 | Finance | Multi | Legal | Education | Medical/Legal | Code |
| **Adversarial** | **24K records, 17+ attack types** | No | No | No | No | No | No | No | No |
| **Risk scoring** | **k-anonymity + RRS** | No | No | Quality scores | No | No | No | No | No |
| **Regulatory tags** | **GDPR, HIPAA, CCPA, PCI-DSS, SOX, LGPD, PIPA** | No | No | No | No | No | No | No | No |
| **Train/dev/test** | **70/10/20 stratified** | 50/50 | 80/20 | 90/10 | Yes | 80/10/10 | Competition | No | No |
| **Baselines** | **Regex, Presidio, LLM, CoNLL export** | GLiNER-PII | DistilBERT | GLiNER | LLM baselines | Custom eval | Fine-tuned GPT | Presidio | StarPII |
| **Data source** | Synthetic | Synthetic | Synthetic | Synthetic | Synthetic | Real (courts) | Real (essays) | Synthetic | Real (code) |
| **License** | Apache 2.0 / CC0 | CC BY 4.0 | CC BY 4.0 | Apache 2.0 | Open | MIT | CC BY 4.0 | CC BY 4.0 | Gated |

## Detailed Competitor Analysis

### Nemotron-PII (NVIDIA, 2024)
- **Strengths**: Large scale (100K), 50+ industry categories, structured document types (forms, invoices), 55+ entity types
- **Weaknesses**: English-only, no coreference tracking, no adversarial evaluation, no query-aware detection
- **PII-Anon advantage**: 60 languages, coreference tracking (25K records), adversarial taxonomy, query-aware PII (8K records), regulatory tagging

### AI4Privacy (2023-2024)
- **Strengths**: Largest dataset (220K+), 6 languages, community-driven
- **Weaknesses**: Inconsistent annotation quality, limited entity types (27-47 depending on version), no structured evaluation dimensions, mixed real/synthetic data raises privacy concerns
- **PII-Anon advantage**: 60 languages (vs 6), 57 entity types, 7 evaluation dimensions, fully synthetic (no privacy risk), sensitivity classification

### PII-Bench (2024)
- **Strengths**: First query-aware PII benchmark (2.8K samples), multi-domain
- **Weaknesses**: Small scale, English-only, no coreference, limited adversarial coverage
- **PII-Anon advantage**: 42x scale (117K vs 2.8K), 60 languages, 8K query-aware records (nearly 3x), coreference tracking, adversarial taxonomy

### TAB - Text Anonymization Benchmark (Pilán et al., 2022)
- **Strengths**: Real court documents (authentic PII patterns), semantic entity types, direct/quasi identifier distinction, coreference support
- **Weaknesses**: Very small (1.3K documents), English-only, single domain (legal), no structured evaluation
- **PII-Anon advantage**: 80x scale, 60 languages, 4 domains, 7 evaluation dimensions, sensitivity classification inspired by TAB's approach

### PIILO (Pikkanen et al., 2024)
- **Strengths**: Educational domain focus, 22K samples, real student essays
- **Weaknesses**: Single domain, single language, 14 entity types only, no adversarial or coreference
- **PII-Anon advantage**: 5x scale, 60 languages, 57 entity types, 4 domains, full evaluation framework

### SPY (Mökander et al., 2023)
- **Strengths**: Clinical notes focus, 6.6K samples
- **Weaknesses**: Single domain/language, 11 entity types, restricted access
- **PII-Anon advantage**: Open license, 57 entity types, 60 languages, clinical domain subset (11.7K records alone)

### BigCode PII (Elazar et al., 2024)
- **Strengths**: Code-specific PII detection (12K), StarCoder training data
- **Weaknesses**: Limited to source code, 6 entity types only, English only
- **PII-Anon advantage**: Code subset (5.7K) with 57 entity types, plus 3 other domains, 60 languages

## Unique Differentiators

Features available **only** in PII-Anon v1.2.0:

1. **Multi-domain realistic document formats**: 23+ document types spanning clinical (SOAP notes, nursing notes, radiology/pathology reports, transcripts), legal (depositions, witness statements, memos, court opinions), and financial (complaint emails, chat logs, SARs, KYC notes)
2. **Advanced adversarial test set**: 13 attack categories including Unicode homoglyphs, zero-width chars, BiDi attacks, Base64 encoding, OCR artifacts, negated PII, and context-dependent ambiguity — failure modes where production systems drop from 94% to 14% F1
3. **Multilingual + query-aware PII**: The only dataset combining query-aware PII detection (13K records) with multilingual support (60 languages)
4. **7 evaluation dimensions**: Systematic coverage of entity tracking, multilingual, context preservation, diverse PII types, edge cases, format variations, and temporal consistency
5. **Regulatory domain tagging**: Per-record tagging with 7 applicable frameworks (GDPR, HIPAA, CCPA, PCI-DSS, SOX, LGPD, PIPA)
6. **Evaluation infrastructure**: 70/10/20 train/dev/test splits, cross-domain test sets, baseline scripts (regex, Presidio), CoNLL BIO export, Parquet export
7. **Re-identification risk scoring**: Per-record quasi-identifier analysis with k-anonymity estimates
8. **Sensitivity classification at scale**: Every annotation across 150K records tagged as direct_identifier, quasi_identifier, or sensitive_attribute
9. **Domain x Language matrix**: Clinical, financial, legal, and technology subsets available across multiple languages
10. **Ambiguous entity tracking**: 3K records with shared name components testing disambiguation

## Scale Comparison

```
AI4Privacy 500K ████████████████████████████████████████████████████████████ 580K
Nemotron-PII    ████████████████████ 200K
PII-Anon v1.2   ███████████████ 151K
Gretel Finance  █████████████ 56K
PIILO           ████ 22K
BigCode PII     ██ 12K
SPY             █ 8.7K
PII-Bench       ▌ 2.8K
TAB             ▎ 1.3K
```

## Language Coverage Comparison

```
PII-Anon v1.2   ████████████████████████████████████████████████████████████ 60
AI4Privacy      ████████ 8
Gretel Finance  ███████ 7
All others      █ 1
```
