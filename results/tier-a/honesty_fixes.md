# Honesty-fix package (SME cheap fixes)

**Date:** 2026-06-15 · Branch `paper1-tier-a-experiments` · Implements the SME panel's "(a) cheap fixes" from
`research-assist-artifacts/_meta/sme-dataset-fitness-2026-06-15.md`.

**Philosophy — ADDITIVE, non-destructive.** The mislabeled fields (`semantic_similarity_*`,
`re_identification_resistance_score`, `k_anonymity_estimate`, `reg_hipaa_safe_harbor`) are read by the scorer,
tests, schema, and croissant metadata. A destructive rename would break those readers. So the migration
(`scripts/apply_honesty_fixes.py`) **keeps every old key** and ADDS honest aliases + the in-code caveats +
legal/residual flags. Old consumers keep working; new consumers get the honest signal. The destructive renames
and the data-gaps that additive edits can't fix are listed below as **reviewed follow-ups**.

---

## 1. Applied & validated (additive migration — `scripts/apply_honesty_fixes.py`)

Validated on `dist/hf/data/test_legal.parquet` (2,038 rows; a non-dump split). Independently reproduced the SME
SSN-tail finding: **951/2038 (46.7%)** records flagged `residual_quasi_identifier` on the generalized variant.

| # | Field / location | Additive change | SME gap |
|---|---|---|---|
| 1 | `context_preservation.utility_metrics.semantic_similarity_*` | + alias `token_overlap_jaccard_*` (same value) + `utility_metrics._caveat` ("set-token Jaccard, NOT semantic; coherence_preserved_* is an ASSUMED constant True; information_loss_ratio is an entity-type prior") | A-T2 / Q1 |
| 2 | `context_preservation` | + `legal_category` per variant (masked=redaction; generalized=generalization-may-retain-QIs; **pseudonymized = Art.4(5) STILL PERSONAL DATA**; **llm_sanitized = substitution STILL PERSONAL DATA**) + `_caveat` (no variant anonymised under Recital 26) | C-#3 / Q3 |
| 3 | `context_preservation` | + `residual_quasi_identifier` flag (True per-variant when a partial identifier like `***-**-NNNN` is retained) | C-#? / Q3 |
| 4 | `tier3_evaluation.re_identification_resistance_score` | + alias `exposure_index_prior` (same value) + `_caveat` = the real `EXPOSURE_INDEX_NOTE` ("DETERMINISTIC pre-screen PRIOR … NOT measured RRS … MUST NOT be reported as a re-identification result"), pointing to the FR-007 MeasuredRRS run | B-#2, C / Q2,Q3 |
| 5 | `privacy_risk.k_anonymity_estimate` | + `_caveat` ("QI-TYPE-count proxy 1→100/2→20/3→5/4+→2, NOT an equivalence-class k over values; null where QIs absent") | C-#2 / Q3 |
| 6 | top-level columns | + `reg_hipaa_phi_present` (= `reg_hipaa_safe_harbor`; honest name — it models PHI-content presence, NOT the 18-identifier Safe Harbor standard) | C-#5 / Q3 |
| 7 | file-level schema metadata | + `crosswalk_disclaimer`, `exposure_index_note`, `ax_001`, `reg_gdpr_note`, `honesty_fixes_applied` (the in-code caveats now travel with the FILE) | C-#1 / Q3 (the "honesty doesn't travel into the data" gap) |

**Apply to the full corpus (reviewed dataset-version step — do AFTER the per-record dump releases `test.parquet`/`test_adversarial.parquet`):**
```bash
for f in dist/hf/data/*.parquet dist/pii_anon.parquet; do
  python scripts/apply_honesty_fixes.py --in "$f" --out "${f%.parquet}.honest.parquet"
done
# then regenerate the release artifacts that hash/describe the data:
#   - dist/SHA256SUMS.txt   (re-hash the migrated parquets)
#   - dist/croissant.json   (pii-anon export --format croissant ...; new field descriptions)
#   - CHANGELOG.md / version bump (additive schema change → minor version, e.g. 2.1.0)
```
> NOT auto-applied to the shipped files here: it mutates a published CC0 artifact (DOI, SHA256SUMS, croissant) and
> is a dataset-version bump — it needs your review + the release-artifact regeneration above.

---

## 2. Reviewed follow-ups — destructive renames (coordinated change: data + scorer + tests + schema + croissant)

These are the SME's "renames" but they are NOT cheap *mechanically* (readers break). Do them as one coordinated PR:

| Old key | → Honest name | Readers to update |
|---|---|---|
| `semantic_similarity_*` | `token_overlap_jaccard_*` | `scripts/enrich_context_preservation.py`, schema, croissant, any consumer; drop the alias once migrated |
| `re_identification_resistance_score` | `exposure_index_prior` | `scripts/enrich_behavioral_signals.py`, `scoring/reidentification.py` (already has `ExposureIndex`), schema, croissant |
| `coherence_preserved_*` (hardcoded `True`) | remove, or `coherence_assumed=true` | enrichment script; it carries zero signal (zero variance) — stop counting it as utility |
| `k_anonymity_estimate` | `qid_type_count_risk_label` | `scripts/` generator, schema; or keep name but add the real computation (§3) |
| `reg_hipaa_safe_harbor` | `reg_hipaa_phi_present` | crosswalk + generator; differentiate from `reg_hipaa_expert_determination` (currently byte-identical) |

Source-script edits should follow the SAME additive-first philosophy (emit honest name; deprecate old over one version).

---

## 3. Reviewed follow-ups — data/measurement gaps (additive edits can't fix these)

| Gap | Why a migration can't fix it | Owner |
|---|---|---|
| `reg_gdpr` is a 100% constant | Needs genuinely **non-personal / out-of-scope records** (the `_NON_PERSONAL` set exists in code but the corpus has none) — net-new generation | [ROADMAP §C / SME T-c] |
| No agent-task **answerability** scorer (the PRIMARY-question keystone) | Net-new harness + gold answers per variant | SME §5(b) / Paper 2 |
| Real **k-anonymity / singling-out / attribute-inference** (WP29 triad) | Net-new computation over QI values | SME §5(b) / Paper 2 |
| **Art.9** special categories under-covered | Net-new entity types + up-sampling (SEXUAL_ORIENTATION, TRADE_UNION, GENETIC absent; political/religious/ethnicity n=29/49/40) | SME C-#6 |
| Tier-3 can't grade variant **strength** (MeasuredRRS spread = 0.000, see `measured_rrs.md`) | Needs an LLM/semantic adversary and/or richer behavioral signals | SME B / Paper 2 |

---

## 4. README / DATASHEET disclosures (doc edits — recommended next)

- Clarify `semantic_similarity_*` is token-overlap Jaccard (not semantic) wherever the docs describe utility metrics.
- Per-split AI-era counts: README's "250 each" is full-corpus; the **test split** is ~41/50/57/60 — disclose, and mark the AI-era / adversarial sets as *scenario fixtures*, not a measured security eval (FR-017 / ROADMAP FR-018-020 not-implemented).
- State prominently that **no record is demonstrated anonymised under Recital 26**, and that `tier3_risk_level`/RRS are priors, not measured attacks.

---

_All edits are on branch `paper1-tier-a-experiments`, no commits. The migration is additive and round-trips through
pyarrow; the full-corpus application + release-artifact regeneration is a reviewed version-bump step._
