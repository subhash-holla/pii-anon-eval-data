# v1.3.0 Behavioral Signals & Tier 3 Re-identification Resistance

**Target Release**: 2026-04-15
**Status**: Implementation
**Drives**: Paper1-PII-Rate-Elo-Framework Tier 3 extension (Section 4.2.1)
**Addresses**: Lermen et al. (2026) "Large-scale online deanonymization with LLMs" (arXiv:2602.16800)

## Motivation

The Lermen et al. paper demonstrates that LLMs achieve **67% recall at 90% precision** re-identifying users after **all direct PII entities are removed**, using quasi-identifiers and behavioral signals. This invalidates the assumption that entity-level de-identification (the focus of v1.0–v1.2) is sufficient for privacy protection.

The PII-Rate-Elo paper proposes a **Tier 3 evaluation extension** for LLM-based semantic re-identification resistance. v1.3.0 provides the dataset infrastructure required to evaluate Tier 3 systems.

## Schema Extensions

### 1. Per-Record `behavioral_signals` Field

Added to every record, scoring 6 categories of identity-revealing signals that survive entity-level de-identification:

```json
"behavioral_signals": {
  "writing_style": {
    "present": true,
    "uniqueness": "moderate",
    "indicators": ["sentence_length_distribution", "punctuation_pattern"]
  },
  "professional_domain": {
    "present": true,
    "uniqueness": "high",
    "indicators": ["industry_jargon:medical", "technical_terminology"]
  },
  "interest_topics": {
    "present": false,
    "uniqueness": "low",
    "indicators": []
  },
  "temporal_patterns": {
    "present": true,
    "uniqueness": "low",
    "indicators": ["timezone_hint:UTC-5"]
  },
  "location_signals": {
    "present": true,
    "uniqueness": "high",
    "indicators": ["local_reference:the_T_Boston"]
  },
  "personal_anecdote": {
    "present": false,
    "uniqueness": "none",
    "indicators": []
  },
  "behavioral_signal_density": 0.42,
  "reidentification_contribution": "moderate"
}
```

**Uniqueness scale**: `none`, `low`, `moderate`, `high`, `very_high`
**Behavioral signal density**: 0.0–1.0 (analogous to `pii_density` but for quasi-identifiers)
**Reidentification contribution**: `low`, `moderate`, `high`, `critical` (categorical risk level)

### 2. Per-Record `tier3_evaluation` Field

For records designed to test Tier 3 (LLM re-identification resistance):

```json
"tier3_evaluation": {
  "is_paired_profile": true,
  "persona_id": "persona_0001",
  "profile_type": "pseudonymous_forum",
  "linked_profile_id": "persona_0001_real",
  "esrc_attack_target": false,
  "expected_reidentification_difficulty": "moderate",
  "behavioral_signal_removal_attempted": false
}
```

**Profile types**: `pseudonymous_forum`, `real_identity`, `cross_platform_github`, `cross_platform_stackoverflow`, etc.
**Expected difficulty**: `easy`, `moderate`, `hard`, `very_hard` (estimates how easy it would be for an ESRC pipeline to match this profile)

### 3. New Adversarial Type Categories

Added to `adversarial.type` enum:

- `stylometric_obfuscation`: Writing style deliberately altered (paraphrased, register-shifted)
- `interest_diversification`: Off-topic content mixed in to confuse topic-based matching
- `temporal_pattern_disruption`: Posting time/sequence randomized
- `paraphrased_content`: LLM-rewritten preserving meaning but removing style fingerprints

### 4. Fourth Anonymized Variant: `anonymized_llm_sanitized`

Extends `context_preservation` from 3 variants to 4:

```json
"context_preservation": {
  "anonymized_masked": "...",
  "anonymized_pseudonymized": "...",
  "anonymized_generalized": "...",
  "anonymized_llm_sanitized": "...",   // NEW: removes both PII AND behavioral signals
  "utility_metrics": {
    "...": "...",
    "semantic_similarity_llm_sanitized": 0.71,   // NEW
    "behavioral_signal_residual": 0.18           // NEW: how much behavioral info leaks through
  }
}
```

### 5. Re-identification Resistance Score (RRS)

Added to `privacy_risk` block:

```json
"privacy_risk": {
  "...": "...",
  "re_identification_resistance_score": 0.62,   // NEW: 0.0=easy reid, 1.0=resistant
  "estimated_reid_recall": 0.38,                // NEW: estimated ESRC attack recall
  "tier3_risk_level": "moderate"                // NEW: low/moderate/high/critical
}
```

**RRS formula** (computed from behavioral_signal_density and uniqueness levels):
```
RRS = 1.0 - (signal_density × uniqueness_weight)

where uniqueness_weight ∈ [0.2, 1.0] based on the most unique signal in the record.
```

This directly maps to the paper's recommendation:
```
RRS = 1 - (re-identification_recall × re-identification_precision)
```

## New Records Generated

### 5,000 Paired Profile Records

**Structure**: 2,500 personas × 2 profiles each (pseudonymous + real-identity)

For each persona:
- **Pseudonymous forum profile**: Writing posts about interests, opinions, technical questions (no direct PII, full behavioral signals)
- **Real-identity profile**: LinkedIn-style — full name, employer, role, location (direct PII present)

Same `persona_id` + `linked_profile_id` enables matching evaluation. Designed to mirror the Hacker News ↔ LinkedIn experiment in Lermen et al.

**Domains**: Tech (1000 personas), healthcare (500), finance (500), legal (250), academic (250)

### 2,000 ESRC-Attack Evaluation Records

Three sub-categories:
1. **Successful entity-level de-id, behavioral signals intact** (800 records): All PII entities removed but writing style, interests, location refs intact — should be re-identifiable
2. **Behavioral signal removal attempted** (800 records): Both PII AND behavioral signals removed (e.g., LLM-sanitized) — should resist re-identification
3. **Adversarial signal injection** (400 records): Fake behavioral signals injected to confuse matching

## Implementation

Three new pipeline scripts:

1. **`scripts/enrich_behavioral_signals.py`**: Adds `behavioral_signals` to all 151,752 existing records. Detects signal presence using lexical patterns and entity-type composition.

2. **`scripts/generate_v130_records.py`**: Generates 5,000 paired profiles + 2,000 ESRC-attack records.

3. **`scripts/enrich_tier3_metrics.py`**: Computes RRS and `re_identification_resistance_score` from behavioral signal annotations. Adds 4th anonymized variant via template-based behavioral-signal removal (the LLM-sanitized variant uses pattern-based behavioral signal substitution since the dataset is fully synthetic).

## Final Stats Target

| Metric | v1.2.0 | v1.3.0 |
|--------|--------|--------|
| Records | 151,752 | ~158,750 |
| Document types | 31 | 35+ (paired_profile_pseudonymous, paired_profile_real, esrc_target, etc.) |
| Adversarial categories | 13 | 17 (4 new behavioral) |
| Anonymized variants | 3 | 4 (adds llm_sanitized) |
| Behavioral signal annotations | 0 | 158,750 (100%) |
| Tier 3 evaluation records | 0 | 7,000 |
| Per-record RRS | 0 | 158,750 (100%) |
| Paired persona pairs | 0 | 2,500 |

## Paper Alignment

This release directly enables the research paper's Tier 3 extension (Section 4.2.1, lines 381–399):

| Paper Component | Dataset Feature |
|-----------------|-----------------|
| Tier 3 ESRC pipeline evaluation | 2,000 ESRC-attack records |
| Candidate set of 1K–10K profiles | 5,000 paired profiles (2,500 personas × 2 profiles) |
| Re-identification precision/recall metric | Per-record RRS scoring |
| Quasi-identifier extraction targets | `behavioral_signals` annotations |
| LLM-based sanitization defense | 4th `anonymized_llm_sanitized` variant |

## Backward Compatibility

All new fields are **additive and optional**. v1.2.0 consumers continue to work unchanged. v1.3.0 consumers gain access to:
- `record.behavioral_signals` (per record)
- `record.tier3_evaluation` (per Tier 3 record only)
- `record.privacy_risk.re_identification_resistance_score`
- `record.context_preservation.anonymized_llm_sanitized`
- `record.context_preservation.utility_metrics.semantic_similarity_llm_sanitized`
- `record.context_preservation.utility_metrics.behavioral_signal_residual`
