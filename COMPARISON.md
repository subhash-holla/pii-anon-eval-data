# Benchmark Dataset Comparison

Head-to-head comparison of PII-Anon Evaluation Dataset v1.1.0 against major competing benchmarks for PII detection and de-identification evaluation.

## Feature Comparison Matrix

| Feature | PII-Anon v1.1 | Nemotron-PII | AI4Privacy | PII-Bench | TAB | PIILO | SPY | BigCode PII |
|---------|:-----------:|:------------:|:----------:|:---------:|:---:|:-----:|:---:|:-----------:|
| **Records** | **117K** | 100K | 220K+ | 2.8K | 1.3K | 22K | 6.6K | 12K |
| **Languages** | **60** | 1 | 6 | 1 | 1 | 1 | 1 | 1 |
| **Writing scripts** | **32** | 1 | 3 | 1 | 1 | 1 | 1 | 1 |
| **Entity types** | **57** | 55+ | 27-47 | 55 | Semantic | 14 | 11 | 6 |
| **Entity categories** | **9** | - | - | - | 2 | - | - | - |
| **Eval dimensions** | **7** | - | - | 2 | - | - | - | - |
| **Coreference** | **25K records** | No | No | No | Yes (small) | No | No | No |
| **Query-aware** | **8K records** | No | No | 2.8K | No | No | No | No |
| **Sensitivity class** | **All records** | No | No | No | Yes | No | No | No |
| **Domain subsets** | **4 domains** | 50+ industries | 3-4 | Multi | Legal | Education | General | Code |
| **Structured docs** | **Forms, invoices, tables** | Forms, invoices | No | No | No | No | No | Code |
| **Adversarial** | **Taxonomy + 15K records** | No | No | No | No | No | No | No |
| **Risk scoring** | **Per-record k-anonymity** | No | No | No | No | No | No | No |
| **Regulatory tags** | **GDPR, HIPAA, CCPA, PCI-DSS, SOX, LGPD, PIPA** | No | No | No | No | No | No | No |
| **Dev/test splits** | **Stratified 10/90** | Train/test | Yes | Yes | No | No | Yes | Yes |
| **Data source** | Synthetic | Synthetic | Mixed | Mixed | Real (courts) | Real (essays) | Real (notes) | Real (code) |
| **License** | Apache 2.0 / CC0 | CC BY 4.0 | Partial open | Open | Open | Kaggle | Restricted | Open |

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

Features available **only** in PII-Anon v1.1.0:

1. **Multilingual + query-aware PII**: The only dataset combining query-aware PII detection with multilingual support (60 languages)
2. **7 evaluation dimensions**: Systematic coverage of entity tracking, multilingual, context preservation, diverse PII types, edge cases, format variations, and temporal consistency
3. **Adversarial taxonomy**: Structured classification of adversarial techniques (leetspeak, partial redaction, format noise, etc.) with 15K labeled records
4. **Regulatory domain tagging**: Per-record tagging with 7 applicable frameworks (GDPR, HIPAA, CCPA, PCI-DSS, SOX, LGPD, PIPA)
5. **Re-identification risk scoring**: Per-record quasi-identifier analysis with k-anonymity estimates
6. **Sensitivity classification at scale**: Every annotation across 117K records tagged as direct_identifier, quasi_identifier, or sensitive_attribute
7. **Domain x Language matrix**: Clinical, financial, legal, and technology subsets available across multiple languages
8. **Ambiguous entity tracking**: 3K records with shared name components testing disambiguation

## Scale Comparison

```
AI4Privacy      ████████████████████████████████████████████ 220K
PII-Anon v1.1     ██████████████████████ 117K
Nemotron-PII    ███████████████████ 100K
PIILO           ████ 22K
BigCode PII     ██ 12K
Entity Tracking █████ 25K (PII-Anon subset alone)
SPY             █ 6.6K
PII-Bench       ▌ 2.8K
TAB             ▎ 1.3K
```

## Language Coverage Comparison

```
PII-Anon v1.1     ████████████████████████████████████████████████████████████ 60
AI4Privacy      ██████ 6
PIILO           █ 1
All others      █ 1
```
