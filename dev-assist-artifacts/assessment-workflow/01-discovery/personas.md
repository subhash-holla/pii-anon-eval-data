# CAP-02 Discovery §2 — Consumer Personas (Assessment-Workflow Roster)

**Capability**: CAP-02 — Powered, repeatable, reportable assessment workflow (runs the existing `pii-rate-elo` tournament against PII-Anon **v2.0.0** over a powered representative sample / full corpus / smoke).
**Stage**: assessment-workflow / 01-Discovery · Section 2
**Date**: 2026-06-01
**Method**: 6 parallel `persona-researcher` agents with live 2025/2026 web research, each anchored to a cycle-1 candidate. Classification: **priority** (4B mode: high/medium/low + audience), not T1/T2/T3.

> **CAP-02 lens — what changed vs cycle-1.** Cycle-1 personas were consumers of *the dataset*. CAP-02 personas are consumers of *the assessment workflow* — the powered, seeded, CI-bearing, paired-tested, manifest-reproducible tournament run. The roster is **carried forward intact** (IDs stable with cycle-1 `01-discovery/personas.md`); two of the six refresh agents surfaced **near-neighbor commercial/assurance lenses** that the agents themselves recommended **folding as sub-archetypes** (not new gating consumers): `P-tool-vendor` → sub-archetype of `P-tool-builder`; `P-complreviewer` → sub-archetype of `P-dpo`. Honored here.

> **Brownfield Mode — Source Signal vs Gaps**
> - **Confirmed from cycle-1 (cited):** `01-discovery/personas.md` roster + `workflow-maps.md` PGO triples + `04-use-cases.md` traces.
> - **Refreshed with live 2025/2026 sources:** re-identification threat escalation, EU AI Act Art. 10/11 (bulk effect Aug 2026), false-positive tax, OpenAI Privacy Filter, Papers-with-Code shutdown (Jul 2025).
> - **Inferred but unconfirmed:** YoY adoption/headcount and WTP are **agent-inferred** (no clean series); WTP ≈ $0 across all personas (CC0/open expectation) — value is reputational/methodological/defensibility, not subscription.
> - **Gaps the user must fill (Pass-2):** real-user validation — interview ACL/PETS authors, Presidio/GLiNER maintainers, i2b2/n2c2 participants, privacy/platform-security engineers running bake-offs, and DPO-adjacent assessors. Tag `provisional_status: AGENT_SIMULATED`.
> - **Does NOT cover (non-persona stakeholder):** the neutral benchmark host / governance body — a stakeholder created by the arms-length governance decision, carried to Design, not the consumer roster.

---

## Persona roster

| ID | Persona | Priority | One-line audience |
|---|---|---|---|
| **P-acad-deid** | Academic De-identification Researcher | **HIGH** (credibility — gates citation legitimacy) | Clinical/legal/education NLP researchers who benchmark & *publish* PHI/PII de-id (i2b2/n2c2, TAB, OpenDeID lineage); the citation audience that confers legitimacy on CAP-02 |
| **P-mlnlp-researcher** | ML/NLP Privacy Researcher | **HIGH** (gates v1) | Academic+industry scientists publishing PII-detection / anonymization / re-id methods at ACL/EMNLP/NeurIPS-D&B/PETS; primary assessment-workflow consumer |
| **P-tool-builder** | Privacy-Tool Builder / OSS Maintainer | **HIGH** (gates v1) | Maintainers/authors of PII detectors & anonymizers (Presidio, GLiNER-PII, Piiranha, PII SDKs) needing an external reproducible CI/publication harness |
| **P-agentic-redteam** | Agentic-Security Red-Teamer | **MEDIUM** | AI red-team/safety engineers testing live LLM agents for per-channel PII leakage; CAP-02 = recognition oracle + payload seed + RRS-on-transcripts, not a live agent-leakage benchmark |
| **P-priv-eng** | Enterprise Privacy / Platform-Security Engineer | **MEDIUM** (downstream) | Engineers operationalizing PII controls in prod; use CAP-02 output to **pre-screen** finalists + borrow the harness design for an own-data POC |
| **P-dpo** | Compliance / Privacy Counsel / DPO | **MEDIUM** | DPOs certifying lawful end-states (anon vs pseudo); consume CAP-02 *evidence artifacts* (manifest + CIs + caveat) via technical teams |

**3 HIGH / 3 MEDIUM.** The 3 HIGH personas are CAP-02's acceptance + credibility cohorts — the academic-soundness bar (seeded/byte-reproducible, powered-to-lattice-tier, CI-per-metric, paired test, RD-convergence, pre-registered manifest) is built *for their standards*. The 3 MEDIUM are real but downstream/secondary.

---

## Condensed profiles (CAP-02-scoped)

### P-acad-deid — Academic De-identification Researcher · HIGH (credibility)
**Jobs-to-be-done.** (1) Produce publishable, **reproducible** de-id evaluations — seeded, manifest-driven (= CAP-02's byte-reproducibility bar, AX-pii-anon-002). (2) Compare methods on a **common, well-powered** benchmark with per-slice CIs and paired tests (CAP-02's lattice/power-tier reuse + Wilson/Clopper-Pearson + McNemar). (3) Share corpora without leaking PHI and quantify residual re-identification risk.
**Pains.** **Synthetic citation ceiling** (load-bearing objection) — synthetic data "may not capture the full complexity of real-user text" (arXiv 2510.07551); CAP-02's AX-001/003 non-strippable caveat is honest but caps headline claims. **Low per-slice power** in real corpora — i2b2-2014 ≈ 1,304 notes, TAB ≈ 1,268 cases, OpenDeID ≈ 2,100 → CAP-02's powered sample over 575,604 records is the genuine differentiator. No standardized rigor (inconsistent baselines, single-LLM dependence, exact-match-only, no CIs/significance). New 2025+ threat: LLMs re-identify even after PHI removal, with no established resistance benchmark (arXiv 2505.12859).
**Gains.** Per-slice power the tiny real corpora can't reach; a neutral CC0 yardstick citable as a stress-test; a reproducible-from-manifest artifact a reviewer can re-run.
**Adoption (agent-inferred).** Active 2025/2026 de-id-benchmarking + re-id publication stream; WTP ≈ $0 (citation/reputational value). Would cite CAP-02 as *supplementary/stress-test* today; **first-class citation unlocks via a correlation study** showing PII-Anon rankings track i2b2-2014/TAB rankings, ideally co-published with a recognized de-id group.
**Priority rationale: HIGH — gates credibility.** Without this persona's assent the benchmark lacks legitimacy. **Bounce:** synthetic framed as a *replacement* for real PHI; behavioral re-id signals not calibrated against a real attack.
**Anti-attribute.** NOT the enterprise privacy engineer (`P-priv-eng`) who needs in-domain procurement screening — this persona optimizes for *publishable, generalizable* rigor.
_Sources: cycle-1 `01-discovery/personas.md` (P-acad-deid); arXiv 2510.07551, 2505.12859; medRxiv 2025.05.05.25326979 (all ret. 2026-06-01)._

### P-mlnlp-researcher — ML/NLP Privacy Researcher · HIGH (gates v1)
**Jobs-to-be-done.** (1) Run the existing `pii-rate-elo` tournament against PII-Anon v2.0.0 over a **powered representative sample** and get a pre-registered, byte-reproducible verdict from a manifest. (2) Every rating/metric carries a **CI**; system-vs-system claims use a **paired test** (McNemar / paired bootstrap) with **RD-convergence** reported. (3) Per-slice power the tiny real corpora (i2b2 1,304 / TAB 1,268) can't match.
**Pains.** No shared anon/pseudo scoring (Presidio maintainer: "no formal results… somewhat intentional"); harmonized cross-source F1 collapses (PIIBench < 0.14); bespoke significance code; under-powered single-seed tables reviewers reject; synthetic-only external-validity attack in review; discovery harder since Papers-with-Code shutdown (Jul 2025 → HF leaderboards now canonical).
**Gains.** A turnkey powered+seeded+CI+paired-test harness; a citable neutral leaderboard entry; calibrated per-slice results that survive review.
**Adoption (agent-inferred).** Re-id subfield is hot (2026 deanon work reports up to ~68% recall @90% precision, ~79.2% identity reconstruction vs ~56% classical) — the threat CAP-02's RRS/paired-persona scoring targets. WTP ≈ $0 (methodological/reputational value).
**Priority rationale: HIGH — gates v1.** CAP-02's reason to exist (powered sample + CI + paired test + reproducible manifest) IS this persona's acceptance bar; if it doesn't satisfy them it satisfies no one.
**Anti-attribute.** NOT `P-priv-eng` (decides on own-data POC, not a public leaderboard); NOT `P-agentic-redteam` (needs a live harness; CAP-02's static sample is a recognition oracle, not agent-leakage scoring); NOT a leaderboard-host/governance body.
_Sources: cycle-1 `01-discovery/personas.md`, `00-pov-stress-test.md`; Microsoft Presidio eval docs; PIIBench (arXiv 2604.15776); arXiv 2602.16800, 2603.18382 (all ret. 2026-06-01)._

### P-tool-builder — Privacy-Tool Builder / OSS Maintainer · HIGH (gates v1)
**Jobs-to-be-done.** Prove a change improves detection without silent regressions (CI gate against a powered external corpus); publish a credible neutral number; cover multilingual/adversarial edges; for anon/pseudo authors, show utility-preservation + re-id resistance (which no public benchmark scores).
**Pains.** No standard yardstick; thin Faker-based home-grown eval data; leaderboards get gamed (held-out leakage, train-on-test). CAP-02 fixes this with held-out labels + submission provenance + seeded manifest + per-slice power.
**Gains.** A reproducible CI regression gate (fail on F2 drop / homoglyph-BiDi bypass); a permalinked leaderboard entry for the model card; likely upstream recognizer contribution.
**Adoption (agent-inferred).** Already self-benchmark on borrowed HF sets; CC0 + stratified splits + Tier-2/3 scoring fit CI + publishable results. WTP ≈ $0.
**Priority rationale: HIGH — gates v1.** Acceptance cohort for the leaderboard-hygiene + reproducibility attributes.
**Anti-attribute.** NOT the commercial vendor seeking a marketing number (see sub-archetype `P-tool-vendor`); NOT `P-priv-eng` (a buyer, not a tool author).
**Sub-archetype — `P-tool-vendor` (Privacy-Tool Vendor / Leaderboard Submitter).** Commercial PII-detector/anonymizer vendor (Private AI/Limina, Tonic, Skyflow, Nightfall, Protecto-class) wanting a citable competitive rank for sales/marketing. Distinct **commercial motive + gaming incentive** make it a **threat-model / governance-justifying persona**, not a new gating consumer: its existence is the forcing function for leaderboard hygiene (held-out labels, blind/provenance-stamped submission, non-strippable synthetic-only caveat). PGO-tool-vendor-01 (citable third-party rank w/ manifest + CI for sales decks) and PGO-tool-vendor-02 (blind submission w/o leaking held-out set / exposing weights). Priority **MEDIUM** (downstream/threat-model). **Hard bounce:** treating the synthetic leaderboard as a procurement oracle. Agent recommendation: keep folded under `P-tool-builder`; carry the gaming-defense requirement into Requirements as governance NFRs.
_Sources: cycle-1 `01-discovery/personas.md` (P-tool-builder, synthesis #2); Limina PII-detection-benchmark blog; Security Boulevard (OpenAI Privacy Filter benchmark, 2026-04) (ret. 2026-06-01)._

### P-agentic-redteam — Agentic-Security Red-Teamer · MEDIUM
**Jobs-to-be-done.** Quantify *per-channel* leakage under attack (output/tool/memory/inter-agent C1–C7), not just final output; reproducible defense-comparable metrics; map to OWASP LLM02 / SAIF 2.0.
**Pains.** Output-only audits miss most leaks (AgentLeak: 41.7% missed); realistic multi-agent envs are heavy; no shared neutral leakage scoring.
**Gains (honestly bounded).** Their substrate is the **live harness** (AgentDojo/InjecAgent/AgentLeak); PII-Anon's static AI-era records are **NOT** their agent-leakage benchmark. CAP-02 is useful as (a) a **PII-recognition oracle** a channel-sniffer calls to decide "did PII cross C1–C7?", (b) an **injection-payload seed library**, (c) **RRS on agent transcripts**. Roadmap pull: a live-harness adapter.
**Adoption (agent-inferred).** Hot 2026 subfield; WTP ≈ $0.
**Priority rationale: MEDIUM.** Real but the static sample is a recognition layer, not the leakage benchmark — does not gate v1.
**Anti-attribute.** NOT `P-mlnlp-researcher` (static-corpus consumer); NOT a live-harness vendor. **Bounce:** positioning the static track as agent-leakage scoring.
_Sources: cycle-1 `01-discovery/personas.md` (P-agentic-redteam); AgentLeak/AgentDojo/InjecAgent lineage (ret. 2026-06-01)._

### P-priv-eng — Enterprise Privacy / Platform-Security Engineer · MEDIUM (downstream)
**Jobs-to-be-done.** Use CAP-02 leaderboard output to **drop tools that fail on breadth** (multilingual, 63-type coverage) before POC; **borrow CAP-02's harness design** (Wilson/CP intervals, McNemar paired test, NIST power tiers, seeded manifest) to stand up a credible *internal* eval on their own corpus without rebuilding scoring; get a defensible recall-vs-precision operating-point view, not a single F1.
**Pains.** Vendor/single-dataset scores don't transfer (PIIBench < 0.14 harmonized); the **false-positive tax** (high-recall/low-precision → ~34K false positives per 10K real entities → reviewer cost + over-redaction; single-number F1 hides it); DLP TCO is 2–3× license cost so a wrong shortlist is expensive; OpenAI Privacy Filter (~96–97% F1, configurable operating points) raises the comparison bar.
**Gains.** A cheap statistical pre-screen to narrow to 1–2 finalists; a harness scaffold; a coverage map (63-type taxonomy + regulatory crosswalk).
**Adoption (agent-inferred).** Acute, rising role demand (LinkedIn Q4-2025: ~3.8 open roles per qualified candidate; senior comp ~$312K median); enterprise DLP budget $150–500K+/yr sits with security/procurement, not this persona. WTP for CAP-02 ≈ $0 (value = time saved + defensibility).
**Priority rationale: MEDIUM (downstream).** Consumes the assessment as a pre-screen + harness scaffold; does not gate v1.
**Anti-attribute.** NOT `P-tool-vendor` (the seller); NOT `P-acad-deid` (optimizes own-corpus procurement, not generalizable publication). **Hard bounce:** synthetic leaderboard as a procurement oracle — finalists always re-tested on internal data.
_Sources: cycle-1 `01-discovery/personas.md` (P-priv-eng), `workflow-maps.md` (PGO-priveng-01/02/03); anonym.legal false-positive-tax; OpenAI Privacy Filter / VentureBeat; Microsoft Presidio eval; stealthcloud.ai privacy-engineer market; Monetizely DLP pricing (all ret. 2026-06-01)._

### P-dpo — Compliance / Privacy Counsel / DPO · MEDIUM
**Jobs-to-be-done.** Reach a *defensible* end-state classification (anonymized vs pseudonymized) backed by documented residual-risk; avoid marketing pseudonymized output as anonymized (EDPB 2025: pseudonymized data remains personal data); produce/accept audit-ready artifacts.
**Pains.** Technical teams report span-F1, which says nothing about residual re-id or contextual leakage; anon-vs-pseudo collapsed into one "redaction quality" score is legally meaningless; no standardized neutral residual-risk yardstick; "synthetic-only" reads as a disqualifier to an assessor unless framed as scaffolding with an explicit ceiling.
**Gains.** CAP-02's **anon-vs-pseudo metric-family separation** (maps 1:1 to legal end-states, AX-pii-anon-004); the **regulatory crosswalk**; **RRS/residual-risk** as quantitative backing for a motivated-intruder / "very small risk" argument; **neutral CC0 governance** (a vendor self-benchmark isn't citable in a DPIA; an arms-length one is); a manifest + per-slice CIs + DesignProvenance non-strippable caveat that survive audit.
**Adoption (agent-inferred).** Rarely runs a benchmark — it's an **input technical teams surface**. WTP ≈ $0; value = defensibility, monetizable only adjacent (assurance/consulting). Tailwind: EU AI Act Art. 10/11 conformity assessment **bulk effect Aug 2026** demands versioned docs + data-provenance + test results as evidence.
**Priority rationale: MEDIUM.** Does not gate v1 and runs no scenario directly; but the project's defensibility features are *for* this persona, and the Aug-2026 clock makes them time-sensitive.
**Anti-attribute.** NOT `P-priv-eng` (does not run the benchmark or build recognizers — reads artifacts); NOT the neutral benchmark host/governance body. **Caveat:** synthetic RRS is evidence *scaffolding*, not a legal determination.
**Sub-archetype — `P-complreviewer` (Compliance / Legal Reviewer — Audit & Assurance).** The *assurance reader* (DPO-adjacent counsel, internal auditor, or **external assessor**) who must *attest* a PII control was evaluated soundly and file/accept the evidence under EU AI Act Art. 10/11 (Aug-2026). PGO-complreviewer-01 (Article-11-fileable artifact: seeded manifest + version pin + per-slice CIs + DesignProvenance caveat an external assessor accepts without rework) and PGO-complreviewer-02 (no over-claim survives — every metric carries a CI + the non-strippable synthetic-only caveat AX-001/003; anon-vs-pseudo never collapsed). Splits into (a) internal compliance/audit (wants reproducibility + caveats) vs (b) external assessor (neutrality/provenance strongest — treats vendor self-benchmarks as inadmissible). Priority **MEDIUM**. Agent recommendation: **fold as the audit/assurance sub-archetype of `P-dpo`**; carry the EU-AI-Act-Art.11 driver into Requirements as a quality-attribute trigger.
_Sources: cycle-1 `01-discovery/personas.md` (P-dpo), `04-use-cases.md`, `03-market-research.md` (J6); EDPB 2025; anonymize.solutions EU-AI-Act-PII; Secure Privacy implementation guide; Teleport EU-AI-Act docs (all ret. 2026-06-01)._

---

## Cross-persona synthesis (signals that shape CAP-02 Requirements)

1. **The synthetic-only citation ceiling is universal** (named by acad-deid, mlnlp, tool-builder, dpo). → The **real-data validation slice** (correlation study vs i2b2-2014/TAB) remains the single highest-leverage credibility unlock; carry as a top open item to Requirements + Testing Pass-2. The AX-001/003 non-strippable caveat (DesignProvenance) must ride every report.
2. **Neutral governance + leaderboard hygiene is a hard trust gate** — and `P-tool-vendor`'s gaming incentive is its forcing function. → Requirements must include governance/neutrality + held-out labels + blind/provenance-stamped submission as quality attributes (justified by the vendor threat-model sub-archetype).
3. **Academic-soundness is the through-line of the 3 HIGH personas.** Powered-to-lattice-tier (or flagged UNDER-POWERED with the shortfall named) + CI-per-metric (Wilson/Clopper-Pearson) + paired test (McNemar/paired-bootstrap) + RD-convergence + pre-registered manifest = the shared acceptance bar. This is the spine of CAP-02's reportable workflow.
4. **Anon-vs-pseudo separation + regulatory crosswalk + RRS** is the legal "why" (P-dpo + the `P-complreviewer` assurance lens), now sharpened by EU AI Act Art. 10/11 (Aug-2026) → carry the Art.11-evidence driver into Requirements; reinforces AX-pii-anon-004.
5. **The false-positive tax** (P-priv-eng) → CAP-02 reporting must expose a recall-vs-precision operating-point view, not a single F1 — an observability/reporting requirement at the score → report stage.
6. **The agentic track stays honestly bounded** — recognition oracle + payload seed + RRS-on-transcripts; a live-harness adapter is a *roadmap* item, not a v1 claim.

**Stakeholder note (non-persona):** the **neutral benchmark host / governance body** is a stakeholder (arms-length governance decision), carried to Design, not the consumer roster.

---

## Methodology & Epistemic Honesty
- Personas are **agent-researched** with live 2025/2026 web evidence (dated sources cited per profile). The roster is carried forward intact from cycle-1; two near-neighbor lenses were **folded as sub-archetypes per the research agents' own recommendations** to keep IDs stable and avoid roster inflation.
- Adoption/headcount/WTP are **agent-inferred** (no clean series); WTP ≈ $0 (CC0) — priority rests on strategic centrality + academic credibility, not revenue.
- **Real-user validation of all personas is a Pass-2 follow-up** and is NOT performed here. Tag `provisional_status: AGENT_SIMULATED`. Agent-simulated research is NOT a substitute for real users.
