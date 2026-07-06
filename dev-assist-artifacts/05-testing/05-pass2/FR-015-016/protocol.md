# Pass-2 Protocol — FR-015 / FR-016 · Coreference-chain & Quasi-identifier-combination SCORING (v1.1)

**Stage 5 · Wave T5 (Pass-2 coordination)** · 2026-05-31 · `pass2_required: false` (OPTIONAL; T6 → **SHIP-WITH-CAVEATS** for these rows if un-Pass-2'd, not DEFER).

**Pass-2 working files:** [`recruiting-checklist.md`](recruiting-checklist.md) · shared [real-data acquisition](../_shared/real-data-acquisition-checklist.md). **No `outcome.md` until real annotated coref/qid data + the n=5–8 expert cohort land out-of-band.**

> **NO agent-simulated cohort and NO agent-generated coreference/quasi-id annotations substitute for this protocol.** The v1 slices (`coreference_slice`, `quasi_identifier_slice` in `src/pii_anon_datasets/subsets/slices.py`) ship a **non-strippable ~72%-formulaic LOW-POWER caveat** precisely because synthetic-distribution coverage is not external validity. Validating the *chain-as-a-unit / quasi-id-combination scoring* requires **real, human-annotated** coreference and quasi-identifier data. Substituting a synthetic or agent-generated annotation set here would re-commit the exact error the v1 caveat documents — REFUSED.

---

## 1. Item under validation

| Field | Value |
|---|---|
| **Items** | FR-015 — Coreference-chain scoring (as a unit); FR-016 — Quasi-identifier-combination scoring |
| **Source stage** | Requirements (N1; SHOULD / v1.1) → Build S7-04 (slice loaders) |
| **Current status** | PERSONA-CONDITIONAL (v1 SEAM verified; full scoring = v1.1/Pass-2) |
| **v1 seam shipped** | `slices.py`: `coreference_slice(records)` selects rows with non-empty `entity_tracking.coreference_chains`; `quasi_identifier_slice(records, min_qids=2)` selects rows with ≥2 `privacy_risk.quasi_identifiers`; each is a `Slice` value object with the non-strippable `SLICE_CAVEAT`. 4 tests pass (S7-04). **The loaders exist; the chain-as-a-unit / qid-combination SCORING does not.** |
| **Threshold under question** | (a) Does the **chain-as-a-unit** scoring rule (FR-015: a chain counts detected only if linked mentions are scored together, not as atomic spans) match how real de-id practitioners judge a chain detected? (b) Does the **quasi-id-combination** slice (FR-016: job-title+employer+city as one indirect identifier) measure indirect/contextual identification as it actually manifests in real legal/education/IRB de-id? |
| **Downstream impact** | N1 originated from the **legal/education de-id** persona, who named coreference + quasi-id-combination scoring as *"the dominant hard-case class"* that atomic-span scoring misses ("the student who transferred from Lincoln High in 2019"). This is the FR-015/016 adoption-credibility item for P-acad-deid. Because ~72% of the corpus is formulaic enrichment, the synthetic chains/qids are **low-power and low-realism** — the slice caveat says so; real annotated data is required to give the scoring rule external validity. |

## 2. Why real annotated DATA is needed (no simulation substitutes)

- Coreference chains and quasi-identifier combinations are **contextual, human-judgment-laden** constructs. The formulaic `synthetic_lattice_enrichment` generator produces chains/qids by *template*, so a scoring rule that looks correct on synthetic chains may not match how a real de-id annotator (or a real re-identification risk) treats a chain. The whole point of FR-015/016 is *indirect/contextual* identification — the hardest thing to synthesize faithfully.
- The v1 `SLICE_CAVEAT` already states the slices have "LIMITED statistical power and external validity" and "synthetic-distribution coverage is not external validity." Pass-2 closes exactly that gap with real annotations.
- A **low-power note** is mandatory and carried through: even the real validation cohort is small (real coreference/qid-annotated de-id corpora are tiny and gated), so the verdict is reported with explicit power limits, never as a high-confidence claim.

## 3. Research questions

> **RQ-1 (FR-015):** On real human-annotated coreference chains, does the **chain-as-a-unit** rule agree with expert de-id judgments of "chain detected" better than atomic-span scoring (i.e. is unit-scoring the right estimand)?
>
> **RQ-2 (FR-016):** On real quasi-identifier combinations, does the **≥2-qid combination slice** capture the indirect-identification cases that real de-id experts flag as re-identification risks, and does the combination (not the atomic spans) carry the risk signal?

## 4. Data source + cohort

**Primary — real annotated corpora (the data leg):**
| Source | Provides | Acquisition |
|---|---|---|
| **i2b2/n2c2** longitudinal notes with **coreference** annotations | real coreference chains (clinical) | DUA (as FR-027); derived chain-level judgments only, no note text egress (AX-pii-anon-001). |
| **TAB** (Text Anonymization Benchmark) — quasi-identifier / indirect-identifier annotations on ECHR cases | real quasi-id combinations (legal) | open research license; confirm derived-artifact compatibility. |
| **Education/IRB de-id exemplars** (where lawfully shareable) | the persona's named hard cases | via the de-id collaborator; only de-identified exemplars. |

**Confirmation cohort (the human-judgment leg) — small, justified:**
- **n = 5–8 expert de-id annotators** (clinical + legal/education de-id researchers / practitioners). Sample size justified by **inter-annotator-agreement saturation**: coreference/qid expert judgment is high-agreement on clear cases; 5–8 annotators give a stable Krippendorff's α and surface systematic disagreements. This is a *confirmation* cohort over real annotated items, not a discovery study.
- **Cohort criteria:** publishes/practises PHI or legal de-id; has annotated coreference or quasi-identifiers before; spans clinical **and** legal/education (the personas that raised N1). **Exclusion:** general-NLP annotators without de-id/re-id experience (they would not reliably judge indirect-identification risk).

## 5. Recruitment channel

- De-id collaborator network (the same channel as FR-027 — co-located, since both need i2b2/TAB access). Approach via ACL/PETS/JAMIA de-id community, n2c2 participants.
- Paid expert-annotation option for the confirmation cohort if organic recruiting is slow: UserInterviews / Respondent screened **hard** to de-id-practitioner criteria (exclude generic annotators). Incentive: expert honorarium.

## 6. Session / run structure

**Data run:** apply `coreference_slice` / `quasi_identifier_slice` logic to the **real** annotated corpora (chain-as-a-unit and ≥2-qid rules) → produce candidate detections.

**Expert session (≈45 min, semi-structured + scored task):**
- 0–5 min: framing (no real-PII; these are de-identified exemplars).
- 5–25 min: **chain-as-a-unit task** — annotator judges N real chains "detected as a unit / not"; compare to atomic-span scoring on the same chains.
- 25–40 min: **qid-combination task** — annotator flags which real ≥2-qid combinations carry re-identification risk; compare to the slice's selection.
- 40–45 min: where do the two rules disagree with expert judgment, and why.

## 7. Outcome capture

**Per-item / per-annotator:** chain-as-a-unit agreement with expert label; atomic-span agreement (the comparator); qid-combination risk agreement; Krippendorff's α across annotators; the **n of real chains/qids available** (the low-power figure — likely small, report it prominently).

**Roll-up:** does unit-scoring beat atomic-span scoring on real chains (FR-015)? does the ≥2-qid slice capture real indirect-id risk (FR-016)? recurring rationales for disagreement (theme codes); the explicit **low-power note** (real annotated n, the residual ~72%-formulaic dependence for any synthetic supplement).

## 8. Verdict mapping

| Outcome | Verdict | Status transition |
|---|---|---|
| Unit-scoring agrees with experts > atomic-span on real chains; ≥2-qid slice captures real indirect-id risk; α acceptable | **REAL_USER_VALIDATED (low-power)** | PERSONA-CONDITIONAL → **AGENT_SIMULATED → REAL-DATA-VALIDATED (v1.1, low-power note retained)**; the scoring rule is externally anchored; the ~72%-formulaic caveat softened to a power note. |
| Validated clinical, ambiguous legal/education (or vice-versa) | **PERSONA-STRATIFIED** | per-domain claim; the other domain stays caveated. |
| `min_qids=2` too loose/tight vs real risk judgments | **TIGHTENED / LOOSENED** | adjust the default `min_qids` (and/or the chain-as-a-unit linkage threshold) to the real-risk operating point. |
| Unit-scoring does **not** beat atomic-span / qid-combination does not track real risk | **PIVOT** | the FR-015/016 scoring estimand is wrong; redesign the rule (or descope to v1.x) before any published coreference/qid claim. |
| Real annotated data not acquired in-window | **INSUFFICIENT_EVIDENCE** | stays PERSONA-CONDITIONAL; slices keep the non-strippable low-power caveat; **T6 → SHIP-WITH-CAVEATS**. |

**Status Change Log entry to write on outcome:**
`| <date> | FR-015, FR-016 | PERSONA-CONDITIONAL | <verdict> | Pass-2 real coreference/qid validation: unit-vs-atomic agreement <...>, ≥2-qid risk capture <...>, n_real=<...> (low-power); evidence .../05-pass2/FR-015-016/outcome.md |`
