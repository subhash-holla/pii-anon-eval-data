# CAP-02 R7 — Survey Analysis (aggregate of 6 R6 respondents)

**Capability**: CAP-02 — academically-sound, repeatable, reportable assessment **workflow** that runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 / CC0 / `annotations`** over a **powered, lattice-stratified sample (default)** / **full corpus (opt-in, citable)** / **smoke (fast)** — with statistical/epistemic observability + reporting at every spine stage (`load → sample → run → score → rate → report`).
**Stage**: assessment-workflow / 02-Requirements · R7 (survey aggregation) · companion to `prioritization-decisions.md`
**Date**: 2026-06-01
**Vocabulary remap**: FR = Benchmark/Assessment Capability; NFR = Quality Attribute; UC = Evaluation Scenario; Persona = **assessment consumer**.
**provisional_status**: AGENT_SIMULATED — these 6 respondents (SRV-01 … SRV-06) are agent-simulated single-session personas administered the R5 `survey-instrument.md` (18 bundles B1–B18 + 2 baseline gates G-eng/G-norg). Agent-simulated research is **NOT** a substitute for real users; real-respondent administration + the first-contact P-dpo lens re-confirmation are Pass-2 musts. The trade-off thresholds the bundles reference are **directional** (R9 validates), not committed.

> **Scale note (carried from cycle-1).** R6 ran at representative **n=6** (one per administered seat) rather than literal n=20 — single-session execution limit. The respondent plan called for ≥2 per persona stratified across all 6 personas + the 2 folded sub-archetypes; the orchestrator seated **6 of the HIGH-cohort + sub-archetype lenses** (3× P-mlnlp-researcher incl. methods-depth, 1× P-acad-deid, 1× P-tool-builder/OSS, 1× P-tool-builder/`P-tool-vendor`). **The 3 MEDIUM personas (P-priv-eng, P-dpo/`P-complreviewer`, P-agentic-redteam) were NOT directly seated this round** — a documented sampling gap (see §4). Their net-new bundles (B14 operating-point; B12/B16/B17 filing-grade+governance; the throughput-SLA route in T6) are therefore evaluated **from the HIGH cohort's view of them**, and the MEDIUM-owned signal is reconstructed from the R3 interview synthesis (INT-04/05/06) rather than re-elicited. This is flagged everywhere it changes a verdict.

---

## 0. Respondent roster (who answered, what they gate)

| Resp | Persona seat (sub-archetype) | Cohort | Primary lens |
|---|---|---|---|
| **SRV-01** | P-acad-deid (publication/reproducibility-first) | HIGH | Citation legitimacy; DOI gate; correlation-slice unlock |
| **SRV-02** | P-mlnlp-researcher (academic-publication track) | HIGH | Reviewer-acceptance methods depth; ACL/EMNLP/PETS |
| **SRV-03** | P-tool-builder (**OSS maintainer**) | HIGH | CI regression gate; held-out hygiene; citable neutral rank |
| **SRV-04** | P-tool-builder (**`P-tool-vendor`** gaming/threat-model) | HIGH-seat / MEDIUM-priority | Citable competitive rank; leaderboard hygiene; DOI for model card |
| **SRV-05** | P-mlnlp-researcher (methods-publication) | HIGH | Statistical-rigor spine; seed-variance |
| **SRV-06** | P-mlnlp-researcher (methods-depth) | HIGH | Fabricated-stats walk-away; Kendall-τ rank stability |

All 6 seats fall in (or fold under) the **3 HIGH gating personas** — the acceptance + credibility cohort. Where all 6 converge on a MoSCoW class the signal is **gating**; where they split, the split is the persona-stratification the instrument was built to surface (Tier-A axis 3 is expected stratified, not uniform).

---

## 1. Tier B — MoSCoW aggregate (6 respondents)

| Bundle | M | S | C | W | Modal | Signal |
|---|---|---|---|---|---|---|
| **B1** audited-stats + `significance.py` quarantine **[P1]** | 6 | 0 | 0 | 0 | **MUST** | **UNANIMOUS** — the walk-away trigger |
| **B2** seam→v2.0.0 + regression contract **[P2]** | 6 | 0 | 0 | 0 | **MUST** | **UNANIMOUS** |
| **B3** powered seeded sampler **[P3]** | 6 | 0 | 0 | 0 | **MUST** | **UNANIMOUS** — net-new reason to exist |
| **B4** PowerMatrix verdict + named shortfall **[P3]** | 5 | 1 | 0 | 0 | **MUST** | near-unanimous (SRV-04 vendor → S; precondition holds MUST) |
| **B5** run-type designation + AX-005 scoping | 2 | 4 | 0 | 0 | **SHOULD** | mechanism MUST (see D2); MoSCoW skew = sequencing, not de-scope |
| **B6** preset trio (default/opt-in/smoke) | 6 | 0 | 0 | 0 | **MUST** | **UNANIMOUS** |
| **B7** engine/convergence/bridge reuse | 4 | 2 | 0 | 0 | **MUST** | HIGH-converge (acad-deid/vendor → S as consumers of the seam) |
| **B8** CI on every metric **[AX5-1]** | 6 | 0 | 0 | 0 | **MUST** | **UNANIMOUS** + top Tier-A (cred 5.00 / aff 5.00) |
| **B9** paired test + Holm + 2 families **[AX5-2]** | 4 | 2 | 0 | 0 | **MUST** | HIGH-converge; SRV-03/04 → S (accept shortly-after-CI) |
| **B10** anon/pseudo + contamination + seed-variance **[NR]** | 0 | 6 | 0 | 0 | **SHOULD** | unanimous SHOULD — but contains **NR** invariants (see D6) |
| **B11** pre-registration **[AX5-4]** | 2 | 2 | 2 | 0 | **MUST→boundary** | **3-way split** — opt-in-rigor persona stratification (D3) |
| **B12** observability run-records + file provenance **[AX5-4]** | 0 | 6 | 0 | 0 | **SHOULD** | unanimous SHOULD from HIGH seats; **MEDIUM-owned** (D4) |
| **B13** honest leaderboard | 6 | 0 | 0 | 0 | **MUST** | **UNANIMOUS** — the deliverable |
| **B14** operating-point view | 0 | 0 | 6 | 0 | **COULD** | **UNANIMOUS COULD from HIGH seats** — MEDIUM-owned (D5) |
| **B15** convergence + honesty-flag bundle **[AX5-3/5]** | 3 | 3 | 0 | 0 | **MUST→boundary** | even split; contains the non-strippable caveat (D7) |
| **B16** reproducible manifest + self-verifying report **[AX5-4]** | 6 | 0 | 0 | 0 | **MUST** | **UNANIMOUS** — universal reproducibility commitment |
| **B17** hygiene + governance + crosswalk **[AX5-6]** | 1 | 2 | 3 | 0 | **COULD→boundary** | persona-split; vendor seat (SRV-04) → MUST; **MEDIUM-owned** (D8) |
| **B18** DOI release | 2 | 2 | 2 | 0 | **MUST→boundary** | **3-way split** — academic-citation MUST / SHOULD-elsewhere (D9) |
| **G-eng** pure-stdlib cores **[GATE][NR]** | 1 | 5 | 0 | 0 | **SHOULD** | baseline gate — not de-scopable regardless (D10) |
| **G-norg** cycle-1 no-regression guardrails **[GATE][NR]** | 5 | 1 | 0 | 0 | **MUST** | baseline gate — not de-scopable regardless (D10) |

**Modal tally across all 20:** 14 MUST · 4 SHOULD · 2 COULD · 0 WON'T. (Final committed split in `prioritization-decisions.md` differs — preconditions/gates/axiom-spine are adjudicated above raw modal where the locked brief or NR/GATE status requires it.)

---

## 2. Tier A — 3-axis aggregate (means over 6) — ranked by credibility-impact × persona-affinity

The reading rule (R5 §Tier-A): rank by **credibility-impact × persona-affinity**, sanity-check against effort. **A precondition (B1–B4) or baseline gate scoring low on credibility-impact is a comprehension flag** — none triggered (the lowest precondition cred is B4 = 4.50; gates are correctly low-affinity, high-cred-for-norg).

| Rank | Bundle | cred-impact | effort | persona-aff | cred×aff | Note |
|---|---|---|---|---|---|---|
| 1 | **B8** CI on every metric | 5.00 | 2.00 | 5.00 | **25.00** | the cheapest credibility — unanimous top |
| 2 | **B1** audited-stats + quarantine | 5.00 | 3.00 | 4.67 | **23.33** | P1; cred maxed |
| 3 | **B3** powered sampler | 4.83 | 3.33 | 4.67 | **22.56** | P3; highest-effort of the top tier |
| 4 | **B9** paired test + Holm | 4.67 | 3.00 | 4.67 | **21.78** | methods-depth spine |
| 4 | **B16** reproducible manifest + self-verifying report | 4.67 | 3.00 | 4.67 | **21.78** | universal repro |
| 6 | **B13** honest leaderboard | 4.50 | 2.00 | 4.67 | **21.00** | high impact-per-effort |
| 7 | **B4** PowerMatrix verdict + shortfall | 4.50 | 2.33 | 4.50 | **20.25** | P3 |
| 8 | **B2** seam + regression contract | 4.83 | 2.17 | 4.17 | **20.14** | P2; best impact-per-effort of preconditions |
| 9 | **B5** run-type designation | 4.00 | 2.67 | 4.00 | **16.00** | the AX-005 enforcement mechanism |
| 9 | **B11** pre-registration | 4.00 | 2.33 | 4.00 | **16.00** | high cred but boundary MoSCoW |
| 11 | **B6** preset trio | 3.83 | 1.83 | 4.17 | **15.97** | unanimous MUST at low effort |
| 11 | **B18** DOI release | 3.83 | 1.17 | 4.17 | **15.97** | **lowest effort of any bundle (1.17)** |
| 13 | **B15** convergence + honesty-flag bundle | 4.00 | 2.00 | 3.67 | **14.67** | carries non-strippable caveat |
| 14 | **B10** anon/pseudo + contamination | 3.83 | 2.00 | 3.17 | **12.14** | affinity dragged by clinical/methods seats |
| 15 | **G-norg** no-regression guardrails | 3.83 | 1.00 | 2.83 | **10.86** | gate — low affinity expected |
| 16 | **B12** observability run-records | 3.50 | 3.00 | 3.00 | **10.50** | MEDIUM-owned; HIGH seats rate mid |
| 17 | **B17** hygiene + governance + crosswalk | 3.50 | 3.67 | 2.67 | **9.33** | **highest effort (3.67)**, lowest-affinity of features; MEDIUM-owned |
| 18 | **B7** engine reuse | 3.17 | 2.00 | 2.83 | **8.97** | consumed-not-built; low affinity (it is plumbing) |
| 19 | **B14** operating-point view | 3.00 | 2.17 | 2.33 | **7.00** | **lowest cred×aff** — MEDIUM-owned, HIGH seats peripheral |
| 20 | **G-eng** pure-stdlib cores | 2.83 | 1.00 | 2.00 | **5.67** | gate — lowest, as expected |

**Reads:**
- The **academic-soundness spine sorts to the top exactly as designed** — B8/B1/B3/B9/B16/B13/B4/B2 occupy ranks 1–8, all the preconditions + the CI/paired/repro stack.
- **B14 and B17 sort to the bottom of the *features***, and **only** because the seats administered are HIGH-cohort. The Tier-A axis-3 stratification is *working*: these are the two bundles the R5 instrument explicitly predicted would be MEDIUM-persona-core / HIGH-peripheral. Their low rank here is **not** a de-scope signal — it is the absence of the seat that owns them (see §4 + D5/D8).
- **B18 is the cheapest bundle to ship (effort 1.17)** with a high affinity for the academic seats — an easy MUST-for-the-citation-cohort even though its MoSCoW splits 2/2/2.

---

## 3. Tier C — forced trade-off outcomes (6 respondents)

| Pair | Outcome | Tally | Reading |
|---|---|---|---|
| **T1** — default-mode labelling vs filing-grade-full-corpus-first | **B6** | **6–0** | UNANIMOUS: powered-representative-default-always-power-labelled is the v0.1 priority; full-corpus is the opt-in citable upgrade. Confirms DF-1's locked default holds. |
| **T2** — AX-005 universality vs run-type scoping | **B5** | **6–0** | UNANIMOUS: scope enforcement by run-type + **suppress** inferential outputs on smoke/dev. Confirms the §4#2 reconciliation — "a half-formed CI on a dev run is worse noise than no CI." |
| **T3** — audited-stats quarantine vs powered sampler (which precondition first) | **B1** | **6–0** | UNANIMOUS: fabricated statistics are the higher walk-away trigger under sequencing pressure — "I can tolerate a cruder sample before a wrong test." Both stay MUST; B1 is must-land-**first**. |
| **T4** — paired-test depth vs operating-point view | **B9** | **6–0** | UNANIMOUS: paired-test rigor is the reviewer-acceptance gate; operating-point is secondary **for these seats**. (Result is HIGH-cohort-biased — see §4: P-priv-eng would pull toward B14.) |
| **T5** — DOI vs leaderboard hygiene + governance | **SPLIT 3–3** | B18 ×3 (SRV-01/02/05) / B17 ×3 (SRV-03/04/06) | **Clean persona-split, exactly as the instrument predicted.** The publication-track seats (acad-deid + 2 methods-publication) pick the DOI gate; the builder/vendor + methods-depth seats pick hygiene/governance. Confirms **both are persona-stratified, neither universal**. → adjudicated D8/D9. |
| **T6** — provenance reproducibility vs throughput-SLA pre-gate | **B12+B16** | **6–0** | UNANIMOUS: byte-reproducible provenance is the binding need; the oracle throughput SLA is correctly **off** the CAP-02-v0.1 critical path. (No red-team seat present to dissent — consistent with R3 INT-06 being the lone throughput voice.) |
| **T7** — regulatory crosswalk: author now vs defer | **SPLIT 3–3** | author ×3 (SRV-01/02/04) / defer ×3 (SRV-03/05/06) | **Genuine fork.** Vendor (SRV-04, enterprise-GDPR/HIPAA defensibility) + acad-deid (legal framing) + one methods seat → author; the OSS-maintainer + two methods-depth seats → defer ("no bearing on my model-card / methods-reproducibility bar"). R3 had resolved this AUTHOR via INT-04/05 (the MEDIUM compliance personas) — **the seats that most want the crosswalk were not administered this round.** → adjudicated D8. |

**Discriminating pairs:** T3 and T4 are the most discriminating for detecting methods-credibility-primary vs operational-utility-primary respondents (per the instrument's own design note) — both went unanimously to the methods-credibility option, which is the expected signature of an all-HIGH-cohort round. T5 and T7 are the two genuine live forks the aggregation must hand to R7 adjudication, and both split cleanly on the publication-vs-tooling/compliance axis.

---

## 4. Cross-persona patterns + the sampling gap

**Near-unanimous MUSTs (low variance — the consensus core, safe to lock):**
B1, B2, B3, B6, B8, B13, B16 (all **6/6 MUST**), plus B4 (5/6). These are the precondition spine (P1/P2/P3 minus the B5 mechanism) + the CI + the reproducible-manifest + the leaderboard deliverable. **No respondent ranked any precondition (B1–B4) low on credibility-impact** — zero comprehension flags; the precondition framing in the instrument worked.

**Clean persona-splits (high variance, expected — this is how persona-stratified priority is detected):**
- **DOI (B18):** MUST for the publication-track seats (SRV-01/02), C/S for the tooling/methods-depth seats. Tier-C T5 confirms (DOI ×3 from the same publication cluster). → **persona-stratified: MUST for P-acad-deid citation cohort, SHOULD elsewhere** (matches R3 §4#5 + FR-054 priority).
- **Governance/crosswalk (B17):** MUST **only** for the `P-tool-vendor` seat (SRV-04, whose gaming incentive *is* the forcing function for hygiene), C/S for everyone else. Tier-C T5 confirms (hygiene ×3). → **persona-stratified; MEDIUM-owned** (the assurance/procurement personas that gate on it were not seated).
- **Operating-point (B14):** unanimous **COULD** from the 6 HIGH seats — but this is exactly the bundle R5 flagged as P-priv-eng-core / HIGH-peripheral, and **no P-priv-eng seat was administered**. The R3 synthesis records it as a confirmed real burn (INT-04: F1=0.91 → precision 0.71 @ recall 0.93 → 34k FPs/10k entities → 3× license cost). → **do NOT read the 6× COULD as a de-scope; it is a missing-seat artifact** (D5).
- **Pre-registration (B11):** 3-way split (2M/2S/2C). The seats that gate publication/leaderboard rate it M; the OSS/vendor seats that iterate fast rate it C ("overhead for iterative dev cycles"). This **is** the opt-in-rigor stratification DF-2 resolved — the mechanism is MUST, the universality is not (D3).

**The sampling gap (load-bearing — carried to Pass-2 + flagged on every affected verdict).**
This round seated **6 HIGH-cohort / sub-archetype lenses** and **0 of the 3 MEDIUM personas** (P-priv-eng, P-dpo/`P-complreviewer`, P-agentic-redteam). The R5 respondent plan explicitly warned the MEDIUM personas "each own a net-new bundle the HIGH cohort under-weights … those signals must **not** be averaged out." Consequently:
- **B14** (P-priv-eng), **B12/B16/B17** filing-grade+governance (P-dpo/`P-complreviewer`), and the **T6 throughput route** (P-agentic-redteam) are evaluated *only from the HIGH cohort's view*. Their MoSCoW/Tier-A/Tier-C signal this round is **systematically deflated** for the MEDIUM-owned items.
- R7 adjudication therefore **does not let the HIGH cohort's under-weighting de-scope a MEDIUM-owned bundle** — it falls back to the R3 interview synthesis (INT-04/05/06), which directly elicited those personas, plus the FR/NFR author's MUST/SHOULD assignments. This is the single biggest caveat on this round's signal.
- This compounds the **inherited** R2/R3 caveat that the **P-dpo / assurance lens is first-contact** (never re-confirmed) — so B12/B16/B17/B14 carry a *double* "real-user-needed" flag into Pass-2.

**Trade-off discriminators:** T5 (3–3) and T7 (3–3) are the decisive persona-splitters; T1/T2/T3/T4/T6 were unanimous (6–0), confirming the precondition spine + the run-type reconciliation + the off-critical-path routing of throughput are **not** in tension for the gating cohort.

**Recurring qualitative refinements (→ R9 / Design):**
1. **The real-data correlation slice (cycle-1 UC-13, vs i2b2-2014/TAB) is named by 4 of 6 respondents as the single citation unlock not covered by any of the 18 bundles** — SRV-01 ("the synthetic-ceiling unlock but appears nowhere in the 18 bundles"), SRV-02 ("highest-leverage credibility unlock not covered … carry as a roadmap item with a named stub"), SRV-05/06 (correlation-study slice). **Strongest convergent missing-capability signal of the round.** It is already a named open item (Discovery Open Item 11, FR-049 "named-and-pending" flag), out-of-band / not v0.1-blocking — but R7 must surface it as an **explicit COULD-scope named stub + carried open item**, not leave it implicit. (See `prioritization-decisions.md` D11.)
2. **Multi-seed Kendall-τ rank-stability has no standalone bundle** — SRV-05 and SRV-06 both note seed-variance / Kendall-τ is folded inside B8/B10 prose with no first-class scoring surface, so it risks under-weighting; SRV-06 wants an explicit gate on whether seed-variance must be measured before a `leaderboard-submission` run-type is permitted. → Design granularity item (it is covered by NFR-024/FR-043 `seed_variance_scope`, but the *gate-interaction* with B11 pre-reg is underspecified).
3. **The submission interface itself is unspecified** — SRV-04 (vendor): how does a system get submitted (upload/API/PR)? B13/B17 presume a submission pathway that no bundle defines. → routes to Design (not a missing FR per se, but a named gap).
4. **CLI ergonomics on run-type names** — multiple respondents suggest `leaderboard` as an alias for `leaderboard-submission`; SRV-06 finds `dev` mildly ambiguous (suggests `pre-screen`/`exploratory`). → finalizable in Design (run-type names are explicitly Design-deferred per FR-038).
5. **GitHub Actions example workflow** calling the three presets (SRV-03) — a first-class CI-integration story for the OSS-maintainer seat. → Design/docs.

---

## 5. AX-pii-anon-005 confirmation (closing item)

**Verdict: CONFIRM as a binding CAP-02 axiom. 6 of 6 = "Yes" (one "Yes-with-change").**

| Resp | Vote | Note |
|---|---|---|
| SRV-01 | Yes | "the six elements collectively define what 'published metric' means … every element is necessary for reviewer acceptance." |
| SRV-02 | Yes | endorses the run-type-scoped enforcement model as the right reconciliation of the universality tension. |
| SRV-03 | Yes | "every result I publish needs a CI and a paired test; AX-005 as scoped by run-type is correct." |
| SRV-04 | **Yes-with-change** | confirm, **and** make element (6) — contamination disclosure + signed held-out-non-exposure attestation — **mandatory for every `leaderboard-submission` run-type, not just `filing-grade`.** |
| SRV-05 | Yes | "every element maps directly to the reviewer-acceptance bar … run-type-scoped enforcement is the right reconciliation." |
| SRV-06 | Yes | "CI + paired test + convergence + provenance + non-strippable caveat + contamination disclosure is the exact bar ACL/EMNLP reproducibility checklists now require." |

**Adopted sharpening (from SRV-04, the gaming/threat-model seat):** element (6) contamination disclosure + signed attestation binds **`leaderboard-submission` AND `filing-grade`** (not filing-grade only). This is consistent with FR-051/NFR-048, which already require the attestation for "leaderboard/published entries" — the survey confirms it should not be narrowed to filing-grade. **No change to the 6-element core or the run-type-bound / manifest-universal enforcement split.** → AX-005 recorded CONFIRMED in `prioritization-decisions.md`.

**Run-type names:** accepted as directionally correct (`smoke` / `dev` / `leaderboard-submission` / `filing-grade`); aliasing (`leaderboard`) and the `dev` rename are Design-deferred (FR-038 says names finalize in Design). No blocking objection.

---

## 6. Distribution check

Modal MoSCoW across the 18 feature bundles (excluding the 2 baseline gates): **13 M · 3 S · 2 C · 0 W** ≈ **72% M / 17% S / 11% C**. This is **MUST-heavy versus the natural ~30/55/15 shape** — but it is *expected and defensible* here, for three structural reasons documented rather than smoothed:
1. **The UCs were SME-pre-filtered** (Discovery: 3 CATASTROPHIC + 15 MAJOR resolved in place, 0 new UC IDs) and the FRs were authored 19-MUST / 6-SHOULD / 0-COULD — the requirement set entered R6 already concentrated on the academic-soundness spine, by design.
2. **3 of the 18 bundles are hard preconditions (B1–B4 minus the B5 mechanism)** that the locked brief mandates land in MUST regardless of vote — they cannot contribute to a SHOULD/COULD tail.
3. **The round is all-HIGH-cohort** — the seats that would have pushed B12/B14/B17 toward SHOULD/COULD (the MEDIUM personas) were not administered, so the MUST end is over-represented and the SHOULD/COULD tail is under-populated (§4 sampling gap).

After R7 adjudication (`prioritization-decisions.md`) — which pushes the MEDIUM-owned and boundary bundles down where the brief/NR/persona-stratification warrant — the committed split lands at a **healthier ~52% MUST / 33% SHOULD / 15% COULD** across the 18 bundles. **No bundle scored majority-WON'T → no OUT items** (consistent with the SME-pre-filtered UC set). The MUST-skew is a property of a precondition-heavy, all-gating-cohort round, **not** a prioritization failure — and the explicit MEDIUM-persona fallback is what keeps it honest.

---

## 7. Methodology & Epistemic Honesty

- **Aggregates 6 agent-simulated R6 respondents** (SRV-01 … SRV-06) administered the R5 `survey-instrument.md`. **Representative-scale, single-session, AGENT_SIMULATED** — directional, not confirmatory or saturated. Real-respondent administration is a Pass-2 must.
- **Sampling gap is the dominant caveat:** the 3 MEDIUM personas (P-priv-eng, P-dpo/`P-complreviewer`, P-agentic-redteam) were **not seated this round**; the `P-tool-vendor` sub-archetype (SRV-04) was seated but `P-complreviewer` was not. MEDIUM-owned bundles (B12/B14/B16/B17 governance/operating-point + the T6 throughput route) are adjudicated against the R3 interview synthesis (INT-04/05/06) rather than re-elicited, and carry a `real_user_needed: true` flag (compounded for the first-contact DPO lens).
- **Tier-A axis-3 (persona-affinity) divergence is signal, not noise** (instrument design): B14/B17 sorting low and B18/B8 sorting high reflects the seat composition, not bundle value.
- **No FR/NFR IDs minted or renumbered.** This analysis prioritizes the existing FR-030 … FR-054 / NFR-019 … NFR-055 set verbatim via the 18 bundles + 2 gates. AX-pii-anon-005 is recorded CONFIRMED (closing item) with one adopted sharpening; the candidate-axiom status moves to binding in `prioritization-decisions.md` for PO sign-off.
- **Thresholds remain directional** (R9 threshold-validator pressure-tests them); they are not committed values.
- **Source artifacts:** R5 `survey-instrument.md` (18 bundles + 2 gates + Tier-C pairs + AX-005 closing item), R4 `functional-requirements.md` (FR-030…054) + `non-functional-requirements.md` (NFR-019…055), R3 `interview-synthesis.md` (DF-1…5, INT-01…06, N-01…15), canonical Discovery (`discovery-report.md` §8 Open Items 1–13 / G1–G7 / C1–C10, `04-use-cases.md` UC-16…23, `personas.md` 6 personas + 2 sub-archetypes). The cycle-1 `02-requirements/{survey-analysis,prioritization-decisions}.md` provided the 3-tier aggregation format + the natural-distribution-check convention.

✅ **R7 survey analysis complete (2026-06-01).** 6 R6 respondents aggregated (all HIGH-cohort/sub-archetype seats); Tier-A 3-axis means + Tier-B MoSCoW tally + Tier-C 7-pair outcomes computed; 7 unanimous MUSTs locked; B11/B15/B18 boundary + B17/B14 MEDIUM-owned-deflated items surfaced; T5 + T7 persona-splits flagged for adjudication; AX-pii-anon-005 CONFIRMED (6/6, one adopted sharpening); sampling gap (3 MEDIUM personas unseated) documented as the dominant caveat with R3-fallback adjudication. Distribution MUST-heavy but structurally justified. `provisional_status: AGENT_SIMULATED`. Final MUST/SHOULD/COULD split in `prioritization-decisions.md`.
