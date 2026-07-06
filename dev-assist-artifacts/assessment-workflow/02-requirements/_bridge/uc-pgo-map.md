# CAP-02 Requirements R0 — UC ↔ PGO Bridge (canonical navigation)

**Capability**: CAP-02 — Powered, repeatable, reportable assessment workflow (runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0** over a powered representative sample (default) / full corpus (opt-in) / smoke (fast), with observability + reporting at every spine stage: `load → sample → run systems → score → rate → report`).
**Stage**: assessment-workflow / 02-Requirements · R0 (UC↔PGO bridge — the first Requirements gate)
**Date**: 2026-06-01
**provisional_status**: AGENT_SIMULATED — PGO triples + personas + use cases are agent-simulated single-session Discovery research; the code/version/line evidence behind them is direct file reads at HEAD on 2026-06-01. Agent-simulated research is **NOT** a substitute for real users (Pass-2 follow-up).
**Sources (canonical Discovery artifacts, read this session)**:
- `01-discovery/discovery-report.md` §3 (personas), §4 (the 18 PGO triples), §6 (UC-16..23)
- `01-discovery/workflow-maps.md` — the **authoritative definition of all 18 PGO triples** (persona · goal · outcome), incl. sub-archetype drivers
- `01-discovery/04-use-cases.md` — UC-16..23 with per-UC `Trace:` lines naming the PGOs each scenario serves
- `01-discovery/personas.md` — 6 personas (3 HIGH / 3 MEDIUM) + 2 folded sub-archetypes

> **Vocabulary remap (project framing).** PGO = a persona's (**P**ersona · **G**oal · **O**utcome) workflow triple; UC = **Evaluation Scenario**. This bridge is the forward/reverse navigation map between the two, plus an orphan scan. It is the contract Requirements (FR-030+, NFR-019+) traces back through: every FR/NFR must serve a UC, every UC must serve ≥1 PGO, every MUST-tier PGO must be served by ≥1 UC.

---

## 0. PGO catalogue (18 triples — persona · goal · outcome)

Carried verbatim-in-substance from `workflow-maps.md`. **Priority** is inherited from the owning persona (HIGH/MEDIUM) per `personas.md` §roster; sub-archetype PGOs are **MEDIUM governance/assurance drivers** (folded, not new gating consumers — `personas.md` §P-tool-builder / §P-dpo). **Tier** = the bridge's coverage obligation: a PGO whose owning persona is HIGH is a **MUST-cover** PGO (an uncovered MUST-cover PGO is a real orphan); a MEDIUM PGO is **SHOULD-cover**.

### HIGH personas (MUST-cover — the acceptance + credibility cohort)

| PGO | Persona | Goal (what they want to do) | Outcome (the artifact/result that satisfies them) | Tier |
|---|---|---|---|---|
| **PGO-acaddeid-01** | P-acad-deid | Benchmark a de-id model with adequate statistical power **per language/domain slice** | Publishable per-slice F1/F2 **with CIs**, powered to lattice tiers (infeasible on n≈1.3K real corpora) | MUST |
| **PGO-acaddeid-02** | P-acad-deid | Measure whether "anonymized" text **resists LLM re-identification** | An RRS / ESRC-attack-recall figure citable in a privacy paper | MUST |
| **PGO-acaddeid-03** | P-acad-deid | Share corpora + run ablations **without DUA/IRB delay** | CC0 dataset re-run **byte-for-byte from the manifest** (teaching, robustness, reproductions) | MUST |
| **PGO-researcher-01** | P-mlnlp-researcher | Benchmark a new anon/pseudo method against **re-id AND utility** on a shared reproducible corpus | Paper reports RRS + pseudonymization-integrity + utility on PII-Anon splits; reviewers accept as standard; method lands on the neutral leaderboard | MUST |
| **PGO-researcher-02** | P-mlnlp-researcher | Evaluate **LLM semantic re-identification** via paired pseudonymous/real profiles without IRB-blocked real data | Attack-resistance results on paired-persona + ESRC slices; safely shareable, reviewer-reproducible | MUST |
| **PGO-researcher-03** | P-mlnlp-researcher | Report **statistically credible per-slice performance** with power + calibration | Per-slice CIs + ECE/Brier on powered, stratified splits; subgroup recall gaps defensible in review | MUST |
| **PGO-builder-01** | P-tool-builder | **Gate every PR** against an external multilingual/adversarial PII corpus | CI fails on an F2 regression or a homoglyph/BiDi bypass before release | MUST |
| **PGO-builder-02** | P-tool-builder | Publish a **credible, reproducible** detection + anonymization score | A citable neutral-leaderboard entry with held-out test provenance, used in the model card/README | MUST |
| **PGO-builder-03** | P-tool-builder | Prove a pseudonymizer **resists LLM re-id while preserving utility** | An RRS + utility score (Tier 2/3) demonstrating the privacy/utility tradeoff | MUST |

### MEDIUM personas (SHOULD-cover — real but downstream/secondary)

| PGO | Persona | Goal | Outcome | Tier |
|---|---|---|---|---|
| **PGO-redteam-01** | P-agentic-redteam | Per-channel (C1–C7) leakage verdict using PII-Anon labeled entities **as the recognition oracle** | A per-channel leakage verdict (recognition-oracle role, not agent-leakage scoring) | SHOULD |
| **PGO-redteam-02** | P-agentic-redteam | **Seed reproducible exfiltration payloads** (adversarial/multilingual, known ground truth) into AgentDojo/AgentLeak-style runs | A reproducible payload seed library with known ground truth | SHOULD |
| **PGO-redteam-03** | P-agentic-redteam | **RRS / behavioral-signal-residual** score on agent transcripts | A transcript RRS confirming low re-id risk | SHOULD |
| **PGO-priveng-01** | P-priv-eng | **Narrow a vendor/tool shortlist** to 1–2 finalists before spending POC budget | A statistical pre-screen (recall-vs-precision operating point, not a single F1) that drops breadth-failing tools | SHOULD |
| **PGO-priveng-02** | P-priv-eng | **Stand up a credible internal eval harness** without building scoring from scratch | A reusable harness scaffold (Wilson/CP intervals, McNemar, NIST power tiers, seeded manifest, per-stage observability) | SHOULD |
| **PGO-priveng-03** | P-priv-eng | **Enumerate entity types + adversarial patterns** to cover before writing detection policy | The 63-type taxonomy + regulatory crosswalk as a coverage checklist | SHOULD |
| **PGO-dpo-01** | P-dpo | Certify whether a release is lawfully **anonymized vs merely pseudonymized** | Documented end-state classification with cited residual-re-id evidence | SHOULD |
| **PGO-dpo-02** | P-dpo | Justify a **motivated-intruder / "very small risk"** determination with quantitative backing | A DPIA artifact citing per-record RRS / residual-risk, not bare span-F1 | SHOULD |
| **PGO-dpo-03** | P-dpo | Map a transformation's technical output to **GDPR/HIPAA/CCPA obligations** | A class-by-class regulatory crosswalk | SHOULD |

### Sub-archetype drivers (folded — MEDIUM governance/assurance, not new gating consumers)

| PGO | Sub-archetype (parent) | Goal | Outcome | Tier |
|---|---|---|---|---|
| **PGO-tool-vendor-01** | P-tool-vendor (← P-tool-builder) | Earn a **citable third-party rank** vs named competitors | A permalinked entry with manifest + CI usable in sales/whitepapers | SHOULD (driver) |
| **PGO-tool-vendor-02** | P-tool-vendor (← P-tool-builder) | **Submit without exposing weights or leaking the held-out set** | A blind/provenance-stamped submission accepted; anti-gaming controls satisfied | SHOULD (driver) |
| **PGO-complreviewer-01** | P-complreviewer (← P-dpo) | Produce **audit-ready, reproducible-from-manifest** evidence a PII control was soundly evaluated | An **Article-11-fileable** artifact an external assessor accepts without rework | SHOULD (driver) |
| **PGO-complreviewer-02** | P-complreviewer (← P-dpo) | Ensure **no over-claim survives** into the compliance record | Every metric carries a CI + the non-strippable synthetic-only caveat (AX-001/003); anon-vs-pseudo never collapsed | SHOULD (driver) |

**PGO count:** 18 primary (9 HIGH MUST-cover + 9 MEDIUM SHOULD-cover) + 4 sub-archetype drivers = **22 triples total** (matching `discovery-report.md` §4: "18 PGO triples … plus sub-archetype drivers PGO-tool-vendor-01/02 and PGO-complreviewer-01/02").

---

## 1. Forward map — PGO → UC (which Evaluation Scenario serves each goal)

Derived from the `Trace:` line of each UC in `04-use-cases.md` (authoritative), supplemented for UC-21/UC-22 — whose `Trace:` lines name workflow **themes** rather than PGO IDs — by mapping through the UC's declared primary/secondary personas + intent to the matching PGO outcome (each such inference is marked **[theme→PGO]** and justified in the note column).

| PGO | Tier | Served by UC(s) | Note / justification |
|---|---|---|---|
| **PGO-acaddeid-01** | MUST | UC-16, UC-17, UC-19 | Powered per-slice F1/F2 with CIs (UC-16 sample → UC-17 scoring with CIs); UC-19 full-corpus census option |
| **PGO-acaddeid-02** | MUST | — (roadmap) | RRS / LLM re-id resistance — **out of CAP-02 v0.1** (re-id power uses the distinct `REID_TIER_SPECS` ladder; RRS scenarios live in cycle-1 UC-08/09). Named roadmap item per `04-use-cases.md` §scope-boundary + Open Item 13 / MEI-06. See §3 orphan scan. |
| **PGO-acaddeid-03** | MUST | UC-18, UC-19 | Byte-for-byte reproducibility from manifest: UC-18 pre-registration + UC-19 reproducible-from-manifest full run (UC-18 `Trace` names PGO-acaddeid-03; UC-19 `Trace` names PGO-acaddeid-03) |
| **PGO-researcher-01** | MUST | UC-17, UC-19, UC-23 | Benchmark a method, reviewers accept as standard, lands on leaderboard (UC-17 run/score/rate + UC-23 leaderboard; UC-19 full-corpus option) |
| **PGO-researcher-02** | MUST | — (roadmap) | LLM semantic re-id via paired pseudonymous/real profiles — **out of CAP-02 v0.1** (re-id / ESRC track; same roadmap boundary as PGO-acaddeid-02). See §3 orphan scan. |
| **PGO-researcher-03** | MUST | UC-16, UC-17 | Statistically credible per-slice performance with power + calibration (UC-16 powered sample + UC-17 per-metric CIs/paired tests — both name PGO-researcher-03 in `Trace`) |
| **PGO-builder-01** | MUST | UC-17, UC-20 | CI gate on F2 regression / homoglyph-BiDi bypass: UC-20 smoke (fast CI inner loop) + UC-17 paired regression verdict (both name PGO-builder-01 in `Trace`) |
| **PGO-builder-02** | MUST | UC-21, UC-23 | Credible reproducible score on the corpus: UC-23 leaderboard entry (`Trace` names PGO-builder-02) **[theme→PGO]** UC-21 reconciles the dataset seam so the corpus is loadable at all — the precondition for any "credible reproducible score" |
| **PGO-builder-03** | MUST | — (roadmap) | Pseudonymizer RRS + utility (Tier 2/3 re-id resistance) — **out of CAP-02 v0.1** (re-id track). The anon-vs-pseudo *separation* (AX-004) is in-scope at UC-17/23, but the RRS *figure* this PGO wants is roadmap. See §3 orphan scan. |
| **PGO-redteam-01** | SHOULD | — (cycle-1 / roadmap) | Per-channel C1–C7 leakage verdict — recognition-oracle role lives in **cycle-1 UC-08/09**; CAP-02 is the static powered-assessment workflow, honestly bounded (`04-use-cases.md` §persona-coverage). See §3. |
| **PGO-redteam-02** | SHOULD | — (cycle-1 / roadmap) | Payload seed library — cycle-1 / live-harness-adapter roadmap. See §3. |
| **PGO-redteam-03** | SHOULD | — (cycle-1 / roadmap) | RRS on agent transcripts — cycle-1 UC-08/09 + re-id track. See §3. |
| **PGO-priveng-01** | SHOULD | UC-23 | Narrow a shortlist via the recall-vs-precision operating-point pre-screen (UC-23 `Trace` names PGO-priveng-01; UC-23 mandates Fβ/AUPRC operating-point view) |
| **PGO-priveng-02** | SHOULD | UC-22 | Borrow the harness scaffold incl. per-stage observability **[theme→PGO]** UC-22 (P-priv-eng primary) emits the run-record observability backbone — the reusable harness instrumentation this PGO wants to borrow |
| **PGO-priveng-03** | SHOULD | UC-16, UC-23 | 63-type taxonomy + crosswalk coverage checklist **[theme→PGO]** UC-16 surfaces the entity-type coverage envelope (`NOT_ASSESSED` for uncovered critical types); UC-23 reports per-type/worst-language coverage. Partial (the standalone regulatory-crosswalk *checklist* is thin — see §3 weak-coverage note). |
| **PGO-dpo-01** | SHOULD | UC-23 | Anon-vs-pseudo end-state classification with residual-risk evidence (UC-23 `Trace` names PGO-dpo-01; AX-004 separation surfaced) |
| **PGO-dpo-02** | SHOULD | UC-23 | DPIA-citable per-record residual-risk, not bare span-F1 (UC-23 `Trace` names PGO-dpo-02; UC-23 mandates honest non-F1 operating-point view). Note: full per-record **RRS** is roadmap (re-id track); UC-23 delivers the detection-side residual evidence. |
| **PGO-dpo-03** | SHOULD | — (partial / roadmap) | Class-by-class GDPR/HIPAA/CCPA regulatory crosswalk — touched by AX-004 anon/pseudo separation at UC-18/23 but the **full crosswalk artifact** is a thin/named-forward item (Open Item 10). See §3 weak-coverage note. |
| **PGO-tool-vendor-01** | SHOULD (driver) | UC-23 | Citable third-party rank with manifest + CI — UC-23 leaderboard entry (its gaming incentive is the *forcing function*; satisfied as a leaderboard consumer) |
| **PGO-tool-vendor-02** | SHOULD (driver) | UC-18, UC-23 | Blind/provenance-stamped submission, anti-gaming **[theme→PGO]** UC-18 pre-registration + run-lineage disclosure + UC-23 provenance-stamped leaderboard supply the blind/held-out submission hygiene (Open Item 9 governance NFRs) |
| **PGO-complreviewer-01** | SHOULD (driver) | UC-18, UC-22, UC-23 | Article-11-fileable artifact (UC-18 `Trace` names PGO-complreviewer-01; UC-22 provenance chain + UC-23 self-verifying report) |
| **PGO-complreviewer-02** | SHOULD (driver) | UC-23 | No over-claim survives (CI + non-strippable synthetic-only caveat on every metric; anon-vs-pseudo never collapsed) — UC-23 honesty-flag mandate |

---

## 2. Reverse map — UC → PGO (which goals each Evaluation Scenario serves)

The unit carried into Requirements is the UC; this is the reverse index Requirements authors read when tracing an FR/NFR back to the consumer goal it serves.

| UC | Title (abbrev.) | Priority | Serves PGO(s) | Primary persona(s) |
|---|---|---|---|---|
| **UC-16** | Powered lattice-stratified sample meeting committed-lattice tiers | MUST | PGO-researcher-03, PGO-acaddeid-01, PGO-priveng-03 [theme] | P-mlnlp-researcher, P-acad-deid |
| **UC-17** | Elo/Glicko run with per-metric CIs, paired tests, RD-convergence | MUST | PGO-researcher-01, PGO-researcher-03, PGO-builder-01, PGO-acaddeid-01 | P-mlnlp-researcher, P-acad-deid, P-tool-builder |
| **UC-18** | Pre-register the run BEFORE any system is scored | MUST | PGO-acaddeid-03, PGO-complreviewer-01, PGO-tool-vendor-02 [theme] | P-acad-deid, P-mlnlp-researcher, P-complreviewer |
| **UC-19** | Full-corpus opt-in run (descriptive census) | SHOULD | PGO-acaddeid-01, PGO-acaddeid-03, PGO-researcher-01 | P-acad-deid, P-mlnlp-researcher |
| **UC-20** | Smoke run for fast CI/dev iteration | SHOULD | PGO-builder-01 | P-tool-builder, P-mlnlp-researcher |
| **UC-21** | Reconcile dataset seam to v2.0.0 + pin regression contract | MUST | PGO-builder-02 [theme] (foundational to all researcher/builder/acaddeid PGOs) | P-mlnlp-researcher, P-tool-builder, P-acad-deid |
| **UC-22** | Observability run-record at every spine stage | MUST | PGO-priveng-02 [theme], PGO-complreviewer-01 | P-priv-eng, P-mlnlp-researcher, P-complreviewer |
| **UC-23** | Reportable leaderboard + figures with HONEST verdicts | MUST | PGO-researcher-01, PGO-builder-02, PGO-dpo-01, PGO-dpo-02, PGO-priveng-01, PGO-complreviewer-02, PGO-tool-vendor-01 | P-mlnlp-researcher, P-tool-builder, P-dpo, P-priv-eng |

**Every UC serves ≥1 PGO → zero forward orphans (no UC exists without a consumer goal).**

---

## 3. Orphan scan

Two directions, per the R0 contract: (A) any **UC with no PGO** (a scenario nobody asked for); (B) any **MUST-tier PGO with no UC** (a gating goal no scenario serves). Plus a weak-coverage note for SHOULD PGOs covered only partially.

### (A) UCs with no PGO — **0 orphans**
All 8 UCs (UC-16..23) map to ≥1 PGO in the reverse map above. No scenario is consumer-orphaned.

### (B) MUST-tier (HIGH-persona) PGOs with no UC — **0 *in-scope* orphans; 3 explicitly-scoped-OUT (not orphans)**
Of the **9 MUST-cover (HIGH) PGOs**, **6 are covered by ≥1 UC** (PGO-acaddeid-01, PGO-acaddeid-03, PGO-researcher-01, PGO-researcher-03, PGO-builder-01, PGO-builder-02).

The **3 uncovered MUST-cover PGOs are all the re-identification / RRS family**, and all **3 are closed by the same explicit, documented out-of-scope boundary — not by silent omission**:

| MUST PGO | Why no in-scope UC | Authoritative boundary |
|---|---|---|
| **PGO-acaddeid-02** (RRS / LLM re-id resistance figure) | Re-id power uses the distinct `stats/power.py::REID_TIER_SPECS` ladder (op point p≈0.1–0.5, 897/385 *pairs*), not the 0.95–0.99 detection tiers CAP-02 v0.1 scores | `04-use-cases.md` UC-23 §scope-boundary + §scope-boundaries (1); `discovery-report.md` Open Item 13 / MEI-06; G-rail: detection-only v0.1 |
| **PGO-researcher-02** (LLM semantic re-id via paired profiles) | Same re-id / ESRC track; RRS scenarios live in cycle-1 UC-08/09 | `04-use-cases.md` §persona-coverage + §scope-boundaries (1); `discovery-report.md` Open Item 13 |
| **PGO-builder-03** (pseudonymizer RRS + utility, Tier 2/3) | Re-id resistance figure is roadmap; the anon-vs-pseudo *separation* (AX-004) IS in-scope at UC-17/23, but the RRS *number* is not | `04-use-cases.md` UC-23 §scope-boundary; `discovery-report.md` Open Item 13 (REID_TIER_SPECS named) |

**These are NOT bridge orphans.** An orphan is a goal that *should* be served by CAP-02 v0.1 but is silently unserved. Each of these three is (a) explicitly declared out-of-scope in the Discovery use-cases doc, (b) tied to a named roadmap item with a concrete reuse hook (`REID_TIER_SPECS`), and (c) consistent with the locked POV ("CAP-02 v0.1 scores detection/anonymization power only; re-identification power is OUT — roadmap"). The boundary is honest and load-bearing, exactly as G-rails require. Requirements should record them as **deferred-with-rationale**, not as gaps to close in this cycle.

### MEDIUM (SHOULD-cover) PGO coverage — informational
- **Covered by a UC:** PGO-priveng-01 (UC-23), PGO-priveng-02 (UC-22), PGO-priveng-03 (UC-16/23, partial), PGO-dpo-01 (UC-23), PGO-dpo-02 (UC-23, detection-side), PGO-tool-vendor-01 (UC-23), PGO-tool-vendor-02 (UC-18/23), PGO-complreviewer-01 (UC-18/22/23), PGO-complreviewer-02 (UC-23). → **9 of 13 MEDIUM PGOs covered.**
- **Out-of-scope (cycle-1 / roadmap, documented):** PGO-redteam-01/02/03 — the agentic recognition-oracle / RRS-on-transcripts scenarios live in **cycle-1 UC-08/09**; CAP-02 is the static powered-assessment workflow, honestly bounded (`04-use-cases.md` §persona-coverage; `discovery-report.md` §scope-boundary (4)). Not orphans — explicitly bounded.
- **Weak / partial coverage (flag for Requirements, NOT orphans):**
  - **PGO-priveng-03** & **PGO-dpo-03** — the **regulatory crosswalk** (GDPR/HIPAA/CCPA class-by-class) and the standalone **63-type coverage checklist** are only *touched* (via UC-16's coverage envelope + AX-004 anon/pseudo separation at UC-18/23). The full crosswalk artifact is a thin, named-forward item (`discovery-report.md` Open Item 10, sharpened by the EU-AI-Act Art. 10/11 Aug-2026 driver). **Recommendation:** Requirements should either author an FR for the regulatory-crosswalk artifact or explicitly defer it with rationale — do not let it drift.

### Orphan rate
- **UC orphan rate (UCs with no PGO):** **0 / 8 = 0.0%.**
- **MUST-PGO orphan rate (HIGH-persona PGOs with no UC, *excluding* the 3 explicitly-scoped-OUT re-id PGOs):** **0 / 6 = 0.0%.**
- **MUST-PGO orphan rate (raw, *counting* the 3 scoped-OUT re-id PGOs as uncovered):** 3 / 9 = 33% — but all 3 are documented out-of-scope-with-roadmap, so the **true (honest) orphan rate is 0.0%** and the 33% is the in-scope-boundary, not a gap.

**Bridge verdict: ~0% orphan rate.** No UC lacks a consumer goal; no in-scope MUST-cover PGO lacks a serving UC. The only MUST PGOs without a UC are the three re-id/RRS goals, each closed by an explicit, documented out-of-scope boundary with a named roadmap reuse hook — the bound is honest, not silent. Two SHOULD PGOs (priveng-03, dpo-03 — the regulatory crosswalk) are weakly covered and flagged for Requirements to author-or-defer-with-rationale.

---

## 4. Handoff to Requirements (R1+)

- **Trace contract going forward:** FR-030+ / NFR-019+ each cite the UC(s) they implement; this bridge resolves each UC to the PGO(s) (and thereby the persona + goal + outcome) it serves. The chain is **persona → PGO → UC → FR/NFR**, fully navigable in both directions.
- **Carry as deferred-with-rationale (do NOT silently drop):** PGO-acaddeid-02, PGO-researcher-02, PGO-builder-03 (re-id/RRS family — `REID_TIER_SPECS` roadmap); PGO-redteam-01/02/03 (cycle-1 UC-08/09 / live-harness-adapter roadmap).
- **Carry as author-or-defer (weak coverage):** PGO-priveng-03 + PGO-dpo-03 (regulatory crosswalk / 63-type coverage checklist — Open Item 10, EU-AI-Act Art. 11 Aug-2026 driver).
- **provisional_status: AGENT_SIMULATED** rides this bridge; real-user validation of the personas/PGOs is a Pass-2 follow-up.

✅ **R0 complete (2026-06-01).** UC↔PGO bridge established — forward + reverse navigation tables, 22 PGO triples catalogued, orphan scan run. **Orphan rate ≈ 0%** (0/8 UCs orphaned; 0/6 in-scope MUST PGOs orphaned; the 3 uncovered MUST PGOs are explicitly scoped-OUT re-id/RRS goals with named roadmap hooks). Ready for R1.
