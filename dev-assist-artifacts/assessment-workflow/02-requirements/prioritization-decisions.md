# CAP-02 R7 — Prioritization Analysis + Decisions

**Capability**: CAP-02 — academically-sound, repeatable, reportable assessment **workflow** that runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 / CC0 / `annotations`** over a **powered, lattice-stratified sample (default)** / **full corpus (opt-in, citable)** / **smoke (fast)**, with statistical/epistemic observability + reporting at every spine stage (`load → sample → run → score → rate → report`).
**Stage**: assessment-workflow / 02-Requirements · R7 (prioritization decisions) · input: 6 R6 responses aggregated in `survey-analysis.md` + the R3 `interview-synthesis.md`
**Date**: 2026-06-01
**Vocabulary remap**: FR = Benchmark/Assessment Capability; NFR = Quality Attribute; Persona = assessment consumer.
**provisional_status**: AGENT_SIMULATED — the prioritization rests on 6 agent-simulated R6 respondents (all HIGH-cohort/sub-archetype seats) + the R3 interview synthesis. Agent-simulated research is **NOT** a substitute for real users; real-respondent Pass-2 is still required for load-bearing MUSTs and for every MEDIUM-owned bundle (the 3 MEDIUM personas were not seated this round). Thresholds remain directional (R9 validates).

> **Scale + sampling note (load-bearing).** R6 ran at representative **n=6** (single-session limit) versus the ≥2-per-persona plan. **All 6 seats are HIGH-cohort or its folded sub-archetypes** (3× P-mlnlp-researcher, 1× P-acad-deid, 1× P-tool-builder/OSS, 1× P-tool-builder/`P-tool-vendor`); **the 3 MEDIUM personas (P-priv-eng, P-dpo/`P-complreviewer`, P-agentic-redteam) were NOT seated.** Where a bundle is MEDIUM-persona-owned (B12/B14/B16-governance/B17 + the T6 throughput route), the HIGH cohort's signal **systematically under-weights it**, and the prioritization falls back to the R3 interviews (INT-04/05/06) + the R4 FR/NFR-author's UC-mandated priority rather than letting the absent-seat vote de-scope it. Every such adjudication is flagged below and carries `real_user_needed: true` to Pass-2.

---

## 0. Method — how a bundle's final class is decided

1. **Preconditions are floor-locked to MUST.** B1 (P1), B2 (P2), B3 + B4 (P3) land in MUST **regardless of vote** — the locked brief mandates it, and a low precondition score is a comprehension flag, not a de-scope signal (R5 reading rule). None scored low (lowest precondition credibility-impact = B4 @ 4.50). **This is the explicit instruction that the 3 preconditions land in MUST — satisfied.**
2. **Baseline gates (G-eng / G-norg) are not de-scopable** ([GATE][NR]) — treated as MUST-grade engineering invariants, excluded from the feature MUST/SHOULD/COULD headline but committed.
3. **Unanimous / HIGH-convergent MoSCoW → that class**, unless a precondition/gate/axiom-spine override applies.
4. **Persona-stratified splits (Tier-C T5/T7 + the B17/B18 MoSCoW spreads) are adjudicated explicitly** — kept SHOULD/COULD *overall* with a documented persona-MUST carve-out, rather than averaged into a false universal.
5. **MEDIUM-owned bundles are NOT de-scoped by the absent-seat vote** — they fall back to the R3-elicited MEDIUM priority. A 6× COULD from HIGH seats on a P-priv-eng-core bundle is read as a missing-seat artifact (D5), not a verdict.
6. **The R4 FR-level priority is the floor for intra-bundle granularity** — a SHOULD bundle keeps its R4-MUST sub-FR as MUST (e.g. FR-051 held-out hygiene inside the SHOULD-leaning B17).

---

## 1. Aggregate MoSCoW (6 respondents) + bundle verdict

| Bundle | M | S | C | W | Modal | **R7 verdict** | Decision ref |
|---|---|---|---|---|---|---|---|
| **B1** audited-stats + quarantine **[P1]** | 6 | 0 | 0 | 0 | M | **MUST** | precondition floor |
| **B2** seam→v2.0.0 + regression contract **[P2]** | 6 | 0 | 0 | 0 | M | **MUST** | precondition floor |
| **B3** powered seeded sampler **[P3]** | 6 | 0 | 0 | 0 | M | **MUST** | precondition floor |
| **B4** PowerMatrix verdict + shortfall **[P3]** | 5 | 1 | 0 | 0 | M | **MUST** | precondition floor |
| **B5** run-type designation + AX-005 scoping | 2 | 4 | 0 | 0 | S | **MUST** | **D2** (mechanism MUST) |
| **B6** preset trio | 6 | 0 | 0 | 0 | M | **MUST** | unanimous |
| **B7** engine/convergence/bridge reuse | 4 | 2 | 0 | 0 | M | **MUST** | HIGH-converge |
| **B8** CI on every metric **[AX5-1]** | 6 | 0 | 0 | 0 | M | **MUST** | unanimous + Tier-A #1 |
| **B9** paired test + Holm + 2 families **[AX5-2]** | 4 | 2 | 0 | 0 | M | **MUST** | HIGH-converge; AX-005 spine |
| **B10** anon/pseudo + contamination + seed-variance **[NR]** | 0 | 6 | 0 | 0 | S | **SHOULD** | **D6** (NR core via G-norg) |
| **B11** pre-registration **[AX5-4]** | 2 | 2 | 2 | 0 | M(tie) | **MUST** | **D3** (mechanism MUST, enforcement opt-in) |
| **B12** observability run-records + file provenance **[AX5-4]** | 0 | 6 | 0 | 0 | S | **SHOULD** | **D4** (MEDIUM-owned) |
| **B13** honest leaderboard | 6 | 0 | 0 | 0 | M | **MUST** | unanimous — the deliverable |
| **B14** operating-point view | 0 | 0 | 6 | 0 | C | **COULD** (persona-MUST) | **D5** (MEDIUM-owned, absent seat) |
| **B15** convergence + honesty-flag bundle **[AX5-3/5]** | 3 | 3 | 0 | 0 | M(tie) | **MUST** | **D7** (non-strippable caveat) |
| **B16** reproducible manifest + self-verifying report **[AX5-4]** | 6 | 0 | 0 | 0 | M | **MUST** | unanimous — universal repro |
| **B17** hygiene + governance + crosswalk **[AX5-6]** | 1 | 2 | 3 | 0 | C | **SPLIT** | **D8** (hygiene MUST / governance+crosswalk SHOULD) |
| **B18** DOI release | 2 | 2 | 2 | 0 | M(tie) | **SHOULD** (acad-MUST) | **D9** (persona-stratified) |
| **G-eng** pure-stdlib cores **[GATE][NR]** | 1 | 5 | 0 | 0 | S | **GATE (MUST-grade)** | **D10** (not de-scopable) |
| **G-norg** no-regression guardrails **[GATE][NR]** | 5 | 1 | 0 | 0 | M | **GATE (MUST-grade)** | **D10** (not de-scopable) |

---

## 2. Forced trade-off outcomes (Tier C)

- **T1 (default-mode labelling vs filing-grade-full-corpus-first):** **6–0 B6.** Powered-representative-default-always-power-labelled is the v0.1 priority; full-corpus is the opt-in citable upgrade. **Confirms DF-1's locked default holds.** Both modes ship (FR-035/036); the default is not flipped.
- **T2 (AX-005 universality vs run-type scoping):** **6–0 B5.** Scope enforcement by run-type + **suppress** inferential outputs on smoke/dev. **Resolves the §4#2 universality tension** — the run-type mechanism (B5/FR-038) is the reconciliation. → reinforces D2.
- **T3 (audited-stats quarantine vs powered sampler — which precondition first):** **6–0 B1.** Under sequencing pressure, fabricated statistics outrank a missing power verdict as the walk-away trigger. **Both stay MUST; B1 is must-land-first** → sequencing note in §5.
- **T4 (paired-test depth vs operating-point view):** **6–0 B9.** Paired-test rigor is the reviewer-acceptance gate for the present (all-HIGH) cohort. **This result is HIGH-cohort-biased** — the P-priv-eng seat that owns B14 was absent; R3 (INT-04) makes B14 a real MEDIUM-MUST. → B9 MUST (confirmed), B14 NOT de-scoped on the strength of T4 (D5).
- **T5 (DOI vs leaderboard hygiene + governance):** **SPLIT 3–3** — B18 from the publication-track seats (SRV-01 acad-deid, SRV-02/05 methods-publication), B17 from the builder/vendor/methods-depth seats (SRV-03/04/06). **Clean persona-split, exactly as the instrument predicted: both are persona-stratified, neither universal.** → D8 (B17) + D9 (B18).
- **T6 (provenance reproducibility vs throughput-SLA pre-gate):** **6–0 B12+B16.** Byte-reproducible provenance is binding; the **oracle throughput SLA is correctly off the CAP-02-v0.1 critical path** (no red-team seat present to dissent; consistent with R3 INT-06 being the lone throughput voice). → throughput stays a named MEDIUM-persona roadmap item (D12).
- **T7 (regulatory crosswalk: author now vs defer):** **SPLIT 3–3** — author from SRV-04 (vendor, GDPR/HIPAA defensibility) + SRV-01 (acad legal framing) + SRV-02; defer from SRV-03 (OSS) + SRV-05/06 (methods-depth). **R3 had resolved this AUTHOR via INT-04/05 — the MEDIUM compliance personas that most want the crosswalk were not seated.** → D8 keeps the crosswalk in-scope (SHOULD, authored-not-deferred), honoring the R3 resolution over the absent-seat tie.

---

## 3. Boundary-item + persona-stratified adjudications (rationale)

- **D1 — Preconditions B1/B2/B3/B4 = MUST (floor-locked).** B1 (P1 audited-stats + `significance.py` quarantine — the SHOWSTOPPER), B2 (P2 seam→v2.0.0 + regression contract — the CATASTROPHIC-as-wired), B3 + B4 (P3 powered sampler + PowerMatrix verdict). All four scored MUST/near-MUST and high credibility-impact (no comprehension flag). **The brief's hard requirement — the 3 preconditions land in MUST — is satisfied** (P1=B1, P2=B2, P3=B3+B4). T3 confirms B1 is the must-land-**first** of the four.

- **D2 — B5 run-type designation = MUST** (despite modal SHOULD, 2M/4S). The MoSCoW skew is **sequencing, not de-scope**: respondents rated it SHOULD as a *feature-ordering* signal while T2 went **6–0** for run-type-scoping as the enforcement model, and the R4 author made FR-038 MUST. B5 is the single mechanism that resolves **DF-1 (citable-vs-pre-screen) + DF-2 (pre-reg scoping) + the AX-005 universality tension** — the "single highest-leverage net-new item" (N-01). Locked **MUST**. NFR-033/034 (run-type mapping + smoke suppression) MUST.

- **D3 — B11 pre-registration = MUST (mechanism), enforcement opt-in.** The 3-way MoSCoW split (2M/2S/2C) **is** the DF-2 opt-in-rigor stratification — publication/leaderboard seats rate it M, fast-iteration OSS/vendor seats rate it C. DF-2 resolved unanimously: opt-in for dev, enforced for high-stakes run-types, **never a global on/off**. So the *mechanism* (commit-anchored + hash-chained + immutable pre-reg, scoped by run-type via B5) is **MUST** (FR-044, NFR-031/032); the *enforcement* is run-type-bound, not universal. Manifest-reproducibility (B16) is the universal commitment, pre-registration is not.

- **D4 — B12 observability run-records = SHOULD (MEDIUM-owned).** Unanimous SHOULD from the 6 HIGH seats — but B12 is **P-priv-eng / P-complreviewer-owned** (the per-stage run-record is audit-admissibility; INT-04/05 treat it as a "first-six hard send-back" floor). The HIGH cohort values it for a methods section (INT-02) but at lower urgency, which is exactly the SHOULD signal. **Kept SHOULD overall, but FR-045 (per-stage run-record) is the assurance-MUST sub-part** — Design must not let "SHOULD" weaken the 6-stage provenance floor for filing-grade consumers. `real_user_needed: true` (DPO lens first-contact + unseated this round).

- **D5 — B14 operating-point view = COULD overall / MUST-for-P-priv-eng (absent-seat carve-out).** **6× COULD from the present seats** — but R5 explicitly flagged B14 as P-priv-eng-core / HIGH-peripheral, **and no P-priv-eng seat was administered.** R3 (INT-04) documents the false-positive tax as a confirmed real burn (F1=0.91 → precision 0.71 @ recall 0.93 → 34k FPs/10k entities → 3× license cost in Q1), and the R4 author made FR-048 **MUST**. The honest reconciliation: **the bundle is COULD for the seats present, but its owning persona makes FR-048 a MUST-for-procurement.** Recorded as **COULD-overall with a persona-stratified-MUST flag** rather than a flat MUST (which the present votes do not support) or a flat de-scope (which the owning persona forbids). **This is the bundle most distorted by the sampling gap — Pass-2 with a real P-priv-eng seat is the single highest-priority re-elicitation.** `real_user_needed: true`.

- **D6 — B10 anon/pseudo + contamination + seed-variance = SHOULD, NR-core preserved.** Unanimous SHOULD on the *new* sub-parts (contamination_status, seed-variance scope) — affinity dragged down by the clinical/methods seats for whom pseudonymization is low-salience (the persona-stratified AX-004 finding, C-10/R3 §4#3). **But B10 carries an [NR] invariant — the four metric families never merged (NFR-055, inheriting cycle-1 NFR-005) — which is NOT de-scopable.** Adjudication: **bundle priority SHOULD; the NFR-055 never-merge invariant rides G-norg as a MUST-grade no-regression guardrail.** AX-004 stays a binding axiom; the clinical lens's indifference does not weaken it (R3 §4#3).

- **D7 — B15 convergence + honesty-flag bundle = MUST** (even 3M/3S split). The bundle contains the **non-strippable synthetic-only / anti-anonymity caveat (AX5-5, FR-049/NFR-044)** — confirmed UNANIMOUS in R3 (C-6), escalated to anxiety=strong by the assurance/procurement consumers, and a binding axiom (AX-001/003). A bundle whose core is a *binding-axiom non-strippable caveat* cannot sit below MUST. The even MoSCoW split reflects respondents weighing the *RD-convergence* sub-part (lower urgency for some) against the *caveat* sub-part (universal MUST). Locked **MUST**.

- **D8 — B17 = SPLIT: leaderboard hygiene MUST / neutrality+crosswalk SHOULD (authored-not-deferred).** Modal COULD (1M/2S/3C); only the `P-tool-vendor` seat (SRV-04 — whose gaming incentive *is* the forcing function for hygiene) rates it MUST. The bundle conflates three things with different verdicts:
  - **Held-out-label hygiene + contamination disclosure + signed attestation (FR-051, NFR-048/049, AX5-6):** **MUST** — R3 DF-5 resolved this across all threat-model personas; it is the anti-gaming floor and AX-005 element 6 (which SRV-04 wants *strengthened* to bind leaderboard-submission, not just filing-grade — adopted, see §4).
  - **Neutrality/governance statement + recusal record (FR-052):** **SHOULD** — inadmissibility-grade for the assurance/procurement consumers (INT-04/05) who were **not seated**; the v0.1 results path runs without it. R4 = SHOULD.
  - **63-type → GDPR/HIPAA/CCPA/GLBA crosswalk (FR-053):** **SHOULD, AUTHORED not deferred.** T7 tied 3–3, but R3 resolved it **AUTHOR** via the two MEDIUM compliance personas (INT-04 called it "more load-bearing than the pre-registration question"; INT-05 "author it, but auditable/updateable") — both unseated this round. The R3 resolution governs over the absent-seat tie. Honors Open Item 10's AUTHOR resolution.
  - `real_user_needed: true` (DPO/assurance lens first-contact + unseated).

- **D9 — B18 DOI = SHOULD overall / MUST-for-P-acad-deid (persona-stratified).** 3-way MoSCoW split + T5 splitting exactly on the publication-vs-tooling axis = textbook persona-stratification (R3 §4#5). A **Zenodo DOI is a HARD citation gate** for the academic-citation cohort (INT-01: won't cite a link-rotting SHA in JAMIA/ACL; INT-02 confirms) and **silent for the CI-gate / procurement / oracle uses.** R4 = SHOULD (FR-054). Locked **SHOULD overall with a MUST-for-the-P-acad-deid-citation-cohort flag.** Cheapest bundle to ship (Tier-A effort 1.17) so the SHOULD is low-cost to honor early.

- **D10 — G-eng / G-norg baseline gates = MUST-grade, not de-scopable.** Scored Tier-A only (excluded from Tier-C). G-norg (no-regression: lattice 730@`47c3a8f`, NFR-018 power gate ON, doc-drift=0, four-families-never-merged) modal MUST (5M); G-eng (pure-stdlib cores + lazy heavy-dep guards) modal SHOULD (5S) **but a [GATE][NR] item is not de-scopable regardless of score** — a low rank flags a respondent under-weighting regression/engineering risk, per the R5 reading rule. Both committed as **MUST-grade engineering invariants** (NFR-050 / NFR-052/053/054), held outside the feature headline count.

- **D11 — Real-data correlation slice (cycle-1 UC-13) = named COULD-scope stub + carried open item.** **The strongest convergent missing-capability signal of the round** — 4 of 6 respondents (SRV-01/02/05/06) independently named it as the single citation unlock absent from all 18 bundles. It is already Discovery Open Item 11 + the FR-049 "named-and-pending" report flag, **out-of-band / gated on external DUA / explicitly NOT v0.1-blocking** (DF-4, unanimous). Adjudication: **carry as an explicit COULD-scope named roadmap stub** (so the citation barrier is visible, not implicit) + a carried open item to Design + Testing Pass-2. Does **not** mint a new FR this cycle (it has no v0.1 acceptance path); recorded so R7 does not silently drop the cohort's top forward-looking ask.

- **D12 — Oracle throughput SLA = roadmap (off CAP-02-v0.1 critical path).** T6 confirmed 6–0 that provenance/reproducibility binds and throughput does not; R3 §4#6 routes the ≤50 ms p95 / ≥500 rps SLA to the oracle track (cycle-1 UC-08 / C9). Surfaced only by making `benchmark_throughput.py` output machine-readable in the report (FR-049/050). Carried as a **named MEDIUM-persona (P-agentic-redteam) roadmap item**, not a v0.1 requirement. Inherited NFR-010b lightweight-detection floor stays INSUFFICIENT_EVIDENCE / `real_user_needed: true` (CAP-02 does not re-pin it).

---

## 4. AX-pii-anon-005 — CONFIRMED as a binding CAP-02 axiom

**6 of 6 respondents voted Yes (one Yes-with-change).** The candidate axiom moves from PROPOSED (R4) to **CONFIRMED / binding**, pending PO sign-off.

> **AX-pii-anon-005 (Pre-registered / reproducible assessment) — CONFIRMED.** No published metric ships without (1) a **confidence interval** [method disclosed]; (2) a **paired test** for every system-vs-system claim [multiplicity family + size declared — exploratory per-cell uncorrected vs confirmatory Holm-Bonferroni]; (3) a **convergence statement** [achieved max-RD ± 2RD with rounds stated]; (4) **provenance** sufficient to reproduce from the manifest [`{dataset_version, record_count, schema_fingerprint, seed, stage, code_commit, toolchain}` + file-level]; (5) a **non-strippable synthetic-only / anti-anonymity caveat**; and (6) for **leaderboard/published entries**, a **contamination disclosure** [`contamination_status` with `unknown` rejected] + a **signed held-out-non-exposure attestation**. **Enforcement scope is run-type-bound** (FR-038): the full bar binds `leaderboard-submission` / `filing-grade`; `smoke` / `dev` suppress inferential outputs entirely. **Manifest-reproducibility is UNIVERSAL** (binds all run-types); **pre-registration is opt-in** (high-stakes run-types only).

**Adopted sharpening (SRV-04, the gaming/threat-model seat):** element **(6) binds `leaderboard-submission` AND `filing-grade`**, not filing-grade only. Consistent with FR-051/NFR-048 ("leaderboard/published entries"); the survey confirms element 6 must not be narrowed to filing-grade. **No change to the 6-element core or the run-type-bound/manifest-universal split.**

**Wiring (unchanged from R4):** (1)→NFR-023/024/025 (B8); (2)→NFR-026/027/028 (B9); (3)→NFR-029 (B15); (4)→NFR-030/031/032/042/043 (B16/B11/B12); (5)→NFR-044 (B15); (6)→NFR-048/049 (B17 hygiene-MUST sub-part); enforcement scope→NFR-033/034 (B5). **AX-005 spine bundles (B1, B8, B9, B15, B16 + the B5 enforcement mechanism) all land in MUST**, which is what makes the axiom enforceable rather than aspirational.

**Run-type names** (`smoke`/`dev`/`leaderboard-submission`/`filing-grade`): accepted directionally; aliasing (`leaderboard`) + the `dev` rename are Design-deferred (FR-038). No blocking objection.

---

## 5. Resulting FR / NFR priority assignment

**MUST (16 FRs):** FR-030, FR-031, FR-032, FR-033, FR-034, FR-035, FR-038, FR-039, FR-040, FR-041, FR-042, FR-044, FR-047, FR-049, FR-050, FR-051.
**SHOULD (8 FRs):** FR-036, FR-037, FR-043, FR-045, FR-046, FR-052, FR-053, FR-054.
**COULD (1 FR):** FR-048 *(operating-point view — COULD-overall, MUST-for-P-priv-eng; D5)*.

**MUST (32 NFRs):** NFR-019, NFR-020, NFR-021, NFR-022, NFR-023, NFR-024, NFR-025, NFR-026, NFR-027, NFR-028, NFR-029, NFR-030, NFR-031, NFR-032, NFR-033, NFR-034, NFR-035, NFR-036, NFR-037, NFR-038, NFR-039, NFR-040, NFR-041, NFR-044, NFR-047, NFR-048, NFR-049, NFR-050, NFR-051, NFR-052, NFR-053, NFR-054.
**SHOULD (4 NFRs):** NFR-042, NFR-043, NFR-045, NFR-055.
**COULD (1 NFR):** NFR-046 *(operating-point reporting — rides FR-048; D5)*.

> **Note on the R4→R7 deltas (FR MUST 19→16).** R7 demoted three R4-provisional MUSTs on honest persona signal: **FR-043** (B10 anon/pseudo new sub-parts → SHOULD; the never-merge NR-core stays MUST via NFR-055/G-norg), **FR-045** (B12 per-stage run-record → SHOULD overall; assurance-MUST sub-part flagged, D4), and **FR-048** (B14 operating-point → COULD-overall/persona-MUST, D5). All three demotions are driven by the **sampling gap** (the MEDIUM personas that make them MUST were unseated) and are **explicitly reversible at Pass-2** — they are demotions of *confidence in the present cohort*, not judgements that the capabilities are low-value. FR-051 was held at MUST (held-out hygiene) inside the otherwise-SHOULD B17 (D8 carve-out).

**Bundle headline (18 feature bundles):** **13 MUST · 3 SHOULD · 1 SPLIT (B17) · 1 COULD (B14)** + **2 baseline gates (MUST-grade, NFR-050/052/053/054)**.

---

## 6. Distribution check

**Combined 62 requirements: 48 MUST (77.4%) · 12 SHOULD (19.4%) · 2 COULD (3.2%).**

This is **MUST-heavy versus the natural ~30/55/15 shape** (and versus cycle-1's healthy ~30/55/15). The deviation is **structural and documented, not a prioritization failure**, for three converging reasons:
1. **The requirement set entered R6 pre-concentrated.** The UCs were SME-pre-filtered (3 CATASTROPHIC + 15 MAJOR resolved in place, 0 new IDs); the R4 FRs were authored 19-MUST / 6-SHOULD / 0-COULD. The academic-soundness spine *is* the capability — there is little legitimate SHOULD/COULD tail to find.
2. **3 of the 4 precondition bundles + the AX-005 enforcement spine are floor-locked MUST** by the brief — they cannot populate a SHOULD/COULD tail no matter how respondents vote.
3. **The round is all-HIGH-cohort.** The seats that would have pushed B12/B14/B17 down (the 3 MEDIUM personas) were unseated, so the SHOULD/COULD tail is under-populated this round. The R3-fallback adjudications (D4/D5/D8) recover *some* tail (FR-048→COULD, FR-043/045→SHOULD, B17 split), but a real-user Pass-2 with the MEDIUM personas is expected to **lengthen the SHOULD/COULD tail further**.

**No bundle scored majority-WON'T → no OUT items** (consistent with the SME-pre-filtered UC set; nothing was de-scoped to out-of-cycle). The 2 COULD items (B14/FR-048 + NFR-046) are the operating-point view, honestly parked as persona-stratified-MUST-pending-its-seat. **The MUST-skew is the honest shape of a precondition-heavy, all-gating-cohort round — flagged here rather than smoothed by artificially demoting preconditions.**

---

## 7. Persona-stratification register (do not mistake for universal demand)

| Bundle / FR | Universal verdict | Persona-stratified reality |
|---|---|---|
| **B18 / FR-054** DOI | SHOULD | **MUST** for P-acad-deid citation cohort; silent for CI-gate/procurement/oracle (D9) |
| **B14 / FR-048** operating-point | COULD | **MUST** for P-priv-eng (false-positive tax — INT-04); peripheral for HIGH cohort (D5) |
| **B17 / FR-052/053** governance + crosswalk | SHOULD | **inadmissibility-grade** for P-dpo/`P-complreviewer` + P-priv-eng procurement (INT-04/05); FR-051 hygiene MUST universally (D8) |
| **B12 / FR-045** per-stage run-record | SHOULD | **audit-MUST** for P-complreviewer (Art-11 send-back floor — INT-05); methods-section-nice for HIGH cohort (D4) |
| **B10 / FR-043** anon/pseudo separation | SHOULD | **legally load-bearing** for P-dpo (AX-004); low-salience for clinical-de-id (irreversible removal) — but NFR-055 never-merge invariant is MUST-grade universally (D6) |
| Throughput SLA (D12) | roadmap | **HARD pre-gate** for P-agentic-redteam (≤50 ms p95 / ≥500 rps — INT-06); absent for everyone else |

This register exists so Design + Pass-2 do not read a SHOULD/COULD as "low-value universally" — five of these six are MUST-grade for a *specific* (mostly unseated) persona.

---

## 8. Methodology & Epistemic Honesty

- **Decisions rest on 6 agent-simulated R6 respondents** (all HIGH-cohort/sub-archetype seats) + the R3 interview synthesis (INT-01…06). **Representative-scale, single-session, AGENT_SIMULATED** — directional, not confirmatory.
- **The sampling gap is the dominant caveat and shapes the adjudication method:** the 3 MEDIUM personas were unseated, so MEDIUM-owned bundles (B12/B14/B17 + throughput) are adjudicated against the R3-elicited MEDIUM priority + the R4 UC-mandated FR priority, never de-scoped on the absent-seat vote. D4/D5/D8/D12 carry `real_user_needed: true`; the **P-dpo/assurance lens remains first-contact** (compounded flag).
- **The 3 hard preconditions land in MUST** (P1=B1, P2=B2, P3=B3+B4) — floor-locked per the locked brief, and independently MUST-voted (no comprehension flag). **AX-pii-anon-005 CONFIRMED** (6/6, one adopted sharpening) with its spine bundles (B1/B5/B8/B9/B15/B16) all in MUST so the axiom is enforceable.
- **No FR/NFR IDs minted or renumbered.** R7 prioritizes the existing FR-030…054 / NFR-019…055 set verbatim. R4→R7 deltas (3 FR demotions) are documented + reversible at Pass-2. The real-data correlation slice (D11) is carried as a named COULD-scope stub + open item, not a new FR.
- **Thresholds remain directional** (R9 threshold-validator). The MUST-heavy distribution (77%) is documented as a structural property of a precondition-heavy, all-gating-cohort round, with the natural-shape deviation explained rather than smoothed.
- **Source artifacts:** `survey-analysis.md` (this round's aggregate), R3 `interview-synthesis.md` (DF-1…5, INT-01…06, N-01…15), R4 `functional-requirements.md` (FR-030…054) + `non-functional-requirements.md` (NFR-019…055), R5 `survey-instrument.md` (18 bundles + 2 gates + coverage table), canonical Discovery (`discovery-report.md` §8 / `04-use-cases.md` / `personas.md`). Cycle-1 `02-requirements/prioritization-decisions.md` provided the format + boundary-adjudication + distribution-check convention.

✅ **R7 prioritization decisions complete (2026-06-01).** Final committed split: **FR 16 MUST / 8 SHOULD / 1 COULD · NFR 32 MUST / 4 SHOULD / 1 COULD · combined 62 = 48 MUST / 12 SHOULD / 2 COULD** (+ 2 MUST-grade baseline gates). Bundle headline: 13 MUST / 3 SHOULD / 1 SPLIT / 1 COULD + 2 gates. **All 3 preconditions in MUST** (P1/P2/P3); **AX-pii-anon-005 CONFIRMED binding** (one adopted sharpening); 12 boundary/persona-stratified adjudications (D1–D12) with rationale; sampling gap (3 MEDIUM personas unseated) documented as the dominant caveat with R3-fallback + Pass-2 carry; real-data correlation slice carried as a named COULD-scope stub. `provisional_status: AGENT_SIMULATED`. Ready for R8/R9 (verification-criteria strengthening + threshold validation).
