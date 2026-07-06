# Measured Tier-3 re-identification (real attack, supersedes the heuristic RRS prior)

Adversary: `offline-deterministic-v1` (deterministic, offline). Closed-world **|C| = 2000** paired personas. RRS = 1 − recall×precision; higher = more re-id-resistant. Wilson 95% CIs on recall.

| Target | n | committed | correct | recall [95% CI] | precision | **RRS** |
|---|---:|---:|---:|---:|---:|---:|
| original_control ⟵ control | 2000 | 2000 | 1768 | 0.884 [0.869, 0.897] | 0.884 | **0.219** |
| masked | 2000 | 2000 | 5 | 0.003 [0.001, 0.006] | 0.003 | **1.000** |
| generalized | 2000 | 1969 | 10 | 0.005 [0.003, 0.009] | 0.005 | **1.000** |
| pseudonymized | 2000 | 2000 | 4 | 0.002 [0.001, 0.005] | 0.002 | **1.000** |
| llm_sanitized | 2000 | 2000 | 4 | 0.002 [0.001, 0.005] | 0.002 | **1.000** |

## Diagnosis

- **Control (original text) recall = 0.884, RRS = 0.219.** The attack CAN re-identify when identifying tokens survive — the testbed is functional.
- **Spread of RRS across the 4 anonymized variants = 0.000.** The variants are **indistinguishable** to this attack (RRS spread < 0.05): every variant removes the surviving QI tokens the attack relies on, and the behavioral signals are too sparse to separate strengths. An LLM adversary and/or richer behavioral signals would be needed to grade variant strength.

## Honesty note

This is the FR-007 measured attack (deterministic offline adversary) — a real, CI-bearing number that replaces the shipped `re_identification_resistance_score`, which is a heuristic prior over `behavioral_signal_density` with no attacker (rename recommended: `exposure_index_prior`). Per the dataset's FR-009 caveat, an RRS measured on SYNTHETIC data MUST NOT be cited as evidence that any record is anonymised under GDPR Recital 26. AX-001: synthetic-distribution precision, not external validity.
