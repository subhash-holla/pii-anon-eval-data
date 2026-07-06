# Tier-A results synthesis — PII-Anon-Eval benchmark (Paper 1)

**Date:** 2026-07-03 (v2.2.0 cut) · Branch `paper1-tier-a-experiments`. Numbers are measured in *this*
environment from the keystone per-record dump + the re-scored `tier1-en-all` leaderboard (leaderboard-derived
rows are final; the per-record-dump-derived rows — paired significance + adversarial — are regenerated on
the frozen v2.2.0 substrate in this cut); every claim
cites the file that backs it. **Honesty bar (load-bearing): AX-001 synthetic-only** — every metric is
precision on the synthetic distribution, NOT external validity, NOT a compliance certification.

---

## 1. Executive summary

The English benchmark is solid and now *defensibly* so; the multilingual story is a genuine strength
(not just a claim); the AI-era tiers are honestly scoped as substrate. Headlines:

- **Free local GLiNER is F2-competitive with the best cloud DLP** on English (F2 0.7337 vs AWS 0.7360).
  The paired **McNemar (χ²=145.9, p=1.4e-33)** shows AWS has a small but *significant* **+1.19pp recall**
  edge (Δrecall gliner−aws = -0.0119 [95% CI -0.0138, -0.0100]) — which GLiNER offsets with **higher
  precision (0.813 vs 0.769)**, so the F2 score is within 0.0023 and GLiNER **wins under partial-overlap**
  (0.7787 vs 0.7663). The story is a precision/recall trade-off, not a recall tie.
- **Coverage ceiling is real and quantified** (Pearson r = 0.80 reachable↔recall) — a structural, novel
  benchmark finding, and the fairness audit shows it is not a handicap.
- **Local ranking is statistically robust** (6/6 adjacent pairs significant, Holm-corrected) and
  **detectors are complementary** (oracle-union recall 0.834 vs best single 0.716).
- **The dataset genuinely services 60 languages** — GLiNER holds ~0.8 F2 across *every* script and is
  *stronger* on non-English; English-tuned NER **collapses to ~0.04 F2 on CJK**.
- **Two reviewer-fatal liabilities closed:** the unbacked "94%→14%" adversarial line is **retracted**
  (replaced by a measured per-attack table), and the **fabricated Cohen's-κ** is gone (AX-002).
- **Tier-2/Tier-3 are substrate, not graded benchmarks** (measured RRS can't distinguish variant
  strength) — scoped honestly to avoid over-claiming.

---

## 2. Dataset-resource results  → Paper §Dataset / Datasheet

| Result | Number | File |
|---|---|---|
| Scale | 782,677 records / 3,107,240 annotations / 60 languages / 66 entity types / CC0 | `README.md`, `DATASHEET.md` |
| **Train/test contamination** | **0.00% exact-text** overlap; **19.36% template-skeleton** (expected for templated synthetic; NOT label leakage) | `results/tier-a/leakage_audit.md` |
| **Label-map fairness** | **FAIR** — 0 unfair drops; coverage ceiling structural; maps maximal+published; author system excluded but same crosswalk | `results/tier-a/fairness_audit.md` |
| Enrichment disclosure | ~15% of *en-test gold spans* are lattice-enriched (≠ the 79.2% corpus-record figure — state precisely) | `results/tier-a/enrichment_ablation.md` |
| Honesty travels into data | additive migration adds caveats/aliases/`legal_category`/`residual_quasi_identifier` (validated; non-breaking) | `scripts/apply_honesty_fixes.py`, `results/tier-a/honesty_fixes.md` |

---

## 3. Benchmark results (English Tier-1: 31,048 records / 201,880 gold)  → Paper §Results

| Finding | Numbers | File |
|---|---|---|
| **11-detector leaderboard** | AWS F2 0.7360 (#1) · GLiNER 0.7337 (#2, free/local) · GCP 0.7040 · Azure 0.6962 · Presidio 0.5262 · … scrubadub 0.201 | `BASELINES.md`, free bundle |
| **GLiNER vs AWS — paired McNemar** | Δrecall(gliner−aws) = -0.0119 [95% CI -0.0138, -0.0100] (**χ²=145.9, p=1.4e-33, significant**); GLiNER's higher precision (0.813 vs 0.769) makes F2 within 0.0023; GLiNER wins under partial-overlap. *Trade-off, not tie.* (AWS = single non-deterministic run) | `results/tier-a/cloud_mcnemar.md` |
| **Coverage-ceiling correlation** (signature finding) | r(reachable/66, micro-recall) = **0.80**; r(reachable, macro-F2) = **0.86** | `results/tier-a/coverage_ceiling.md` |
| **Micro→macro collapse** | AWS 0.736→**0.273**; GLiNER 0.734→**0.242** (long-tail blindness) | `results/tier-a/per_entity_type.md` |
| **Strict vs partial re-rank** | under partial credit **GLiNER 0.7787 > AWS 0.7663** (top-4 reorder) | `results/tier-a/strict_vs_partial.md` |
| **Paired significance** (7 local) | **6/6 adjacent rank pairs significant** (McNemar + Holm); GLiNER significantly #1 local | `results/tier-a/paired_significance.md` |
| **Complementarity** (novel) | oracle-union recall **0.834** vs best single 0.716 (**+0.118** recoverable by ensemble) | `results/tier-a/paired_significance.md` |
| **Enriched-vs-core ablation** | top-2 ordering **invariant** across core/enriched/curated → ranking not a fill artefact | `results/tier-a/enrichment_ablation.md` |
| **Reproducibility** | gliner/piiranha reproduce published *exactly*; **presidio drifts −0.021** (pip-NER env-sensitivity) | dump metas + dump logs |

---

## 4. Multilingual results (60 languages, 40,668 gold, cap 600/lang)  → Paper §Results (multilingual)

**This is the proof that the benchmark services far more than English.**

| Script | GLiNER | Piiranha | English-tuned NER (spaCy) |
|---|---:|---:|---|
| Latin (35 langs) | 0.814 | 0.402 | ~0.32 |
| Arabic | 0.823 | 0.404 | 0.157 |
| Han (Chinese) | 0.833 | **0.693** | **0.038** |
| Hangul (Korean) | 0.840 | 0.664 | 0.034 |
| Japanese | 0.811 | 0.477 | 0.058 |
| Devanagari (Hindi) | 0.832 | 0.395 | 0.350 |

- **Cross-script transfer:** GLiNER en 0.741 → Latin-non-EN 0.827 → non-Latin 0.824 (**better** off English);
  English-tuned spaCy/Stanza **collapse** on non-Latin (~0.19, ~0.04 on CJK).
- **Asian focus (GLiNER):** zh 0.833, ja 0.811, ko 0.840, hi 0.836, vi 0.867, th 0.833, id 0.840, ta 0.803, …
- **Data-quality finding:** 753 gold rows have script-field mislabels (Tamil/Telugu tagged `Latn`); analysis
  uses language-derived script and recommends canonicalizing the field.
- Files: `results/tier-a/multilingual_leaderboard.md`, `multilingual_by_script.md`.

---

## 5. Adversarial robustness (11,254 records, 13 attack types)  → Paper §Results (robustness)

- **"94%→14%" is RETRACTED** — never measured; no detector reaches 94% clean recall (GLiNER ~0.72).
  Replaced by a measured per-attack table.
- GLiNER most robust (0.73–0.83 on high-volume OCR/zero-width/base64; weakest on `context_ambiguous` 0.44).
  English-tuned NER hit literal **0.000 F2** on bidi / url-embedded / partial-redaction.
- Rare attacks (74–184 records) flagged underpowered.
- File: `results/tier-a/adversarial_table.md`.

---

## 6. Tier-2 / Tier-3 — substrate, not graded benchmarks  → Paper §Limitations / Future work

- **Measured Tier-3 RRS** (real offline adversary): original-text control re-identifies **88%** (attack
  works), but **all 4 anonymization variants drop to ~0% with RRS spread 0.000** — the attack cannot
  *grade* variant strength (needs an LLM/semantic adversary + richer behavioral signals). Supersedes the
  shipped heuristic prior. File: `results/tier-a/measured_rrs.md`.
- **SME fitness panels (agent-simulated):** context-preservation / security / GDPR are **substrate yes,
  measurement no** — utility metrics are token-Jaccard/hardcoded-constants; no answerability/attack/defense
  scorer. File: `research-assist-artifacts/_meta/sme-dataset-fitness-2026-06-15.md`.
- **Implication:** present Tier-2/Tier-3 as *infrastructure/substrate*, not calibrated benchmarks — protects
  against over-claiming and matches AX-001.

---

## 7. Honest limitations (must appear in the paper)

1. **AX-001 synthetic-only** — abstract + intro + limitations.
2. **AX-002** — NO Cohen's-κ / human-IAA (corpus is template-generated; the old drafts' κ≥0.85 is fabricated).
3. **Own system excluded** from the leaderboard (COI; deferred to Paper 3).
4. **GLiNER-vs-AWS is a precision/recall trade-off, not a recall tie** — the paired McNemar (χ²=145.9,
   p=1.4e-33, DONE) shows AWS's +1.19pp recall edge (Δrecall gliner−aws = -0.0119 [95% CI -0.0138, -0.0100])
   is significant; GLiNER matches on F2 via higher precision and wins under partial-overlap. AWS is a single
   non-deterministic run (the p-value reflects that run).
5. **flair excluded** from per-record deep-dives (rank-9, English-only, ~15h compute; in the aggregate JSON).
6. **Cloud DLP = single non-deterministic run.**
7. **Multilingual** is a cap-600 stratified subset; small Asian languages ~270 gold spans (moderately powered).
8. **Enrichment** is ~15% of en-test gold (state precisely, not the 79.2% corpus-record figure).
9. **presidio (and pip-NER detectors) drift across environments** — regenerate the final leaderboard in one
   pinned env; gliner/piiranha reproduce exactly.

---

## 8. Sustainability / availability  → Paper §Availability & Maintenance

Community language/dialect extension pathway: self-service validator + guide + issue template + scaffold +
"wanted" list (validated end-to-end). This is the dataset's **maintenance plan** (a D&B checklist item).
Files: `scripts/validate_contribution.py`, `docs/contributing-languages.md`, `docs/wanted-languages.md`,
`.github/ISSUE_TEMPLATE/language_contribution.yml`, `contrib/TEMPLATE-language-pack/`.

---

## 9. Deferred / next experiments (not blocking Paper 1)

- ~~GLiNER-vs-AWS paired McNemar~~ — **DONE** (`cloud_mcnemar.md`): AWS +1.19pp recall (χ²=145.9, p=1.4e-33), GLiNER F2-competitive via precision.
- flair fold-in (low value).
- LLM/semantic Tier-3 adversary to grade anonymization-variant strength (Paper 2).
- Agent answerability harness for the context-preservation question (Paper 2).
- Full-corpus apply of the honesty-fix migration + release-artifact regen (version bump).
- FR-027 real-data correlation slice (the only path to an external-validity statement).

---

## 10. File index (`results/tier-a/`)

`SUMMARY.md` (free-bundle synth) · `coverage_ceiling.md`+`.png` · `per_entity_type.md` · `strict_vs_partial.md` ·
`power_cliff.md` · `macro_vs_micro.png` · `leakage_audit.md` · `fairness_audit.md` · `paired_significance.md` ·
`enrichment_ablation.md` · `measured_rrs.md` · `honesty_fixes.md` · `multilingual_leaderboard.md` ·
`multilingual_by_script.md` · `adversarial_table.md` · `*.json` (machine-readable for each). Scripts in
`scripts/` (`per_record_dump`, `free_bundle`, `leakage_audit`, `fairness_audit`, `per_record_analysis`,
`measured_rrs`, `apply_honesty_fixes`, `multilingual_dump`/`_analysis`, `adversarial_analysis`,
`validate_contribution`).
