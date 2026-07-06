# Pass-2 Protocol — FR-027 · Synthetic→Real Transfer Delta (binding external-validity item)

**Stage 5 · Wave T5 (Pass-2 coordination)** · 2026-05-31 · `developer-assistant.yaml testing.pass2_required: false` (Pass-2 OPTIONAL; this document lets the user execute; T6 downgrades **SHIP → SHIP-WITH-CAVEATS** for this row if un-Pass-2'd, it does **not** DEFER).

**Pass-2 working files:** [`recruiting-checklist.md`](recruiting-checklist.md) · [`preregistration.md`](preregistration.md) (stub) · [`copublication-terms.md`](copublication-terms.md) (stub) · shared [real-data acquisition](../_shared/real-data-acquisition-checklist.md). **No `outcome.md` until real i2b2/TAB results land out-of-band.**

> **NO agent-simulated cohort substitutes for this protocol.** Substituting an agent-generated "real" i2b2-2014 / TAB score vector — or any agent-simulated correlation — for the licensed real-data run is a **CATASTROPHIC methodology violation** and is REFUSED. The v1 harness already encodes this: `correlate(synthetic, real_scores=None)` returns the `RealDataAbsent` sentinel and **never fabricates** a correlation (`src/pii_anon_datasets/validation/correlation.py`). This protocol acquires the **real** licensed corpora and runs the **real** correlation; outcomes land out-of-band.

---

## 1. Item under validation

| Field | Value |
|---|---|
| **Item** | FR-027 — Real-data validation correlation harness |
| **Source stage** | Requirements (UC-13; SHOULD / v1.1 / Pass-2) → Design `sampling-design.md §9` → Build S7-03 |
| **Current status** | PERSONA-CONDITIONAL (v1 SEAM verified; real-data correlation = Pass-2) |
| **v1 seam shipped** | `correlation.py`: `correlate()`, `kendall_tau` (tau-b), `spearman_rho`, `bland_altman`, seeded `_bootstrap_ci`, `RealDataAbsent` sentinel, non-strippable `CORRELATION_CAVEAT`. 5 tests pass (S7-03). |
| **Threshold under question** | Do PII-Anon **synthetic** detector/scorer rankings *track* **real** i2b2-2014 / TAB rankings on the domain-matched English slice — i.e. is the synthetic distribution a valid *proxy* for ranking systems? |
| **Downstream impact** | This is **the** binding external-validity item. `sampling-design.md §6` + the README power statement state plainly: *"synthetic-distribution power is not external validity — see the real-data correlation slice."* Every committed-cell metric carries a non-strippable caveat that it is *"not citable as a standalone recall claim absent the real-data correlation slice (FR-027)."* 4 of 6 personas name the **synthetic-only citation ceiling** as their adoption cap; the concept-value study found "nearly every persona says the real-data validation slice lifts them to 8.5–9" (from a 6–7 median). Validating FR-027 is the single highest-leverage credibility unlock; failing/omitting it is precisely the SHIP-WITH-CAVEATS condition. |

## 2. Why real DATA is needed (no simulation substitutes)

- The claim under test is **transfer**: synthetic→real. A synthetic proxy for the "real" leg is definitionally circular — it would measure synthetic-vs-synthetic agreement and tell us nothing about external validity. The question only has content if the second score vector comes from a **real, independently-collected** PII/PHI corpus.
- The personas that gate this (P-acad-deid, P-mlnlp-researcher) explicitly reject synthetic *framed as a replacement* for real PHI. The unlock they name is a **correlation study showing PII-Anon model rankings track i2b2-2014/TAB rankings**, ideally co-published with a recognized de-id group.
- This is not a user-preference question (no cohort of humans is interviewed here); it is a **real-data acquisition + pre-registered statistical run**. The "sample" is paired model scores on real vs synthetic corpora, not people.

## 3. Research question (pre-registered)

> **RQ:** Across a shared set of K≥12 detectors/anonymizers scored on (a) the PII-Anon synthetic domain-matched English slice and (b) the real i2b2-2014 (clinical) and TAB (legal) corpora, do the **system rankings agree** at Kendall τ-b ≥ τ\* with a bootstrap CI lower bound above the pre-registered floor, and does the Bland-Altman view show **no systematic score bias** beyond a pre-registered limit?

Pre-registration (timestamp + freeze before any real score is computed): the K-system list, the metric (recall@entity-type on the domain-matched English slice), the τ\* floor, the bootstrap seed + `n_boot`, and the Bland-Altman acceptance band. Freeze as `pass2/FR-027/preregistration.md` (out-of-band) with a content hash committed before real scores exist.

## 4. Data source + acquisition (the "sample")

| Corpus | Role | Acquisition path | Gate |
|---|---|---|---|
| **i2b2 / n2c2 2014 de-id** (1,304 clinical notes) | real clinical leg | DBMI Data Portal DUA (https://www.i2b2.org / n2c2 via Harvard DBMI). Named-PI data-use agreement; IRB or IRB-exempt determination; data stays on an access-controlled host. | DUA executed; **real PHI never enters this repo** (AX-pii-anon-001) — only the *derived paired score table* (K × entity-type aggregates, no record text) is exported. |
| **TAB — Text Anonymization Benchmark** (1,268 ECHR legal cases) | real legal leg | TAB is openly licensed (research use); acquire from the official release. Confirm license compatibility with derived-artifact publication. | License recorded; derived score table only. |
| **PII-Anon synthetic domain-matched English slice** | synthetic leg | already in-repo: `src/pii_anon_datasets/data/pii_anon.jsonl.gz` + `slices` filtered to the English clinical/legal-domain rows that *match* i2b2/TAB entity types. | the domain-match map (PII-Anon 63-type taxonomy → i2b2 PHI / TAB entity types) is pre-registered. |

**Acquisition criteria (match the threshold, exclude the rest):**
- **Domain-matched English slice only.** i2b2 = clinical English; TAB = legal English. Correlate against the PII-Anon **English** rows in the matching domains — never the full 60-language corpus (that would confound language with the transfer signal).
- **Entity-type alignment is mandatory.** Only entity types present in *both* the real corpus and the PII-Anon taxonomy enter the paired vector (e.g. NAME/PERSON, DATE, LOCATION, AGE, ID). Types absent from i2b2/TAB are **excluded** from the correlation (reported separately as "no real anchor").
- **Exclusion:** any synthetic row whose `provenance.source_type="synthetic_lattice_enrichment"` enrichment *inflates* an entity type beyond what the real corpus could anchor is down-weighted to the real corpus's type mix, OR the analysis is run twice (raw + reweighted) and both reported — pre-registered which is primary.

**No real-PHI egress.** Real scoring runs on the DUA-host; only the K-system × entity-type **aggregate score matrix** (no note text, no spans) is exported for `correlate()`. This keeps AX-pii-anon-001 (no-real-PII) intact.

## 5. Recruitment / collaboration channel

- This Pass-2 needs a **real-data-holding collaborator**, not a paid user panel. Channel: a recognized clinical/legal de-id group with an existing i2b2/n2c2 DUA (the persona work names "co-published with a recognized de-id group" as the unlock). Approach ACL/PETS/JAMIA de-id authors; the i2b2/n2c2 community; a TAB-affiliated lab.
- **Co-publication governance terms** (FR-027 explicitly requires these recorded): authorship, data-handling responsibilities, who runs the real leg on the DUA-host, embargo, and the non-strippable caveat that PII-Anon remains synthetic. Record in `pass2/FR-027/copublication-terms.md`.
- Incentive: co-authorship / citation, not cash (WTP ≈ $0 across personas; value is reputational).

## 6. Run structure (not minute-by-minute — a data-run sequence)

1. **Pre-register** (freeze K-list, metric, τ\*, seed, n_boot, Bland-Altman band, domain-match map). Commit hash.
2. **Score the K systems** on the PII-Anon synthetic domain-matched slice (in-repo, reproducible).
3. **Score the same K systems** on i2b2-2014 + TAB **on the DUA-host**; export only the aggregate score matrix.
4. **Run `correlate(synthetic_scores, real_scores, seed=<preregistered>)`** → `CorrelationResult` (τ-b, ρ, seeded bootstrap CIs, Bland-Altman mean diff + ±1.96·sd limits). Run i2b2 and TAB as two separate paired vectors **and** pooled (pre-register primary).
5. **Capture** the `CorrelationResult` verbatim (it self-attaches the non-strippable `CORRELATION_CAVEAT`).

## 7. Outcome capture

**Per-run data points:** K (number of paired systems); entity types in the paired vector; `kendall_tau`, `spearman_rho`; `tau_ci`, `rho_ci` (seeded — must reproduce byte-identically, AX-002); `bland_altman_mean_diff`, `bland_altman_limits`; raw-vs-reweighted both.

**Roll-up:** per-corpus (i2b2 / TAB) and pooled τ-b + CI; which entity types drive disagreement (Bland-Altman outliers — the types where synthetic over/under-predicts real difficulty); the co-publication terms recorded.

## 8. Verdict mapping

| Outcome | Verdict | Status transition |
|---|---|---|
| τ-b ≥ τ\* on i2b2 **and** TAB, bootstrap-CI lower bound above floor, Bland-Altman within band | **REAL_USER_VALIDATED** (real-data-validated) | PERSONA-CONDITIONAL → **AGENT_SIMULATED → REAL-DATA-VALIDATED**; lift the synthetic-only citation ceiling; per-cell caveat may cite the correlation. |
| τ-b ≥ τ\* on one corpus, below on the other | **PERSONA-STRATIFIED** | validated for the matching domain (e.g. clinical), caveated for the other; per-domain claim language. |
| τ-b below floor, but a *clear* monotone-after-reweighting signal | **TIGHTENED** (transfer holds only under the real type-mix) | publish with mandatory reweighting + a tightened claim ("rankings transfer only on the real type distribution"). |
| τ-b below floor, Bland-Altman shows large systematic bias | **PIVOT** (the simulated-preferred "synthetic-as-proxy" framing is invalidated) | the synthetic distribution does **not** rank systems like real data; the benchmark is repositioned as a *stress-test / pre-screen only* (the persona "bounce" outcome), and the headline-recall framing is withdrawn. ~10–20% of DIVERGED items land here; the methodology budgets for it. |
| Real data not acquired (no DUA / no collaborator) within the window | **INSUFFICIENT_EVIDENCE** | stays PERSONA-CONDITIONAL; `RealDataAbsent` remains the shipped truth; **T6 → SHIP-WITH-CAVEATS** (the synthetic-only ceiling stands, documented). |

**Status Change Log entry to write on outcome** (into `02-requirements/traceability-matrix.md`):
`| <date> | FR-027 | PERSONA-CONDITIONAL | <verdict> | Pass-2 real-data correlation: τ-b=<...> CI[<...>] on i2b2/TAB domain-matched English slice; evidence dev-assist-artifacts/05-testing/05-pass2/FR-027/outcome.md |`
