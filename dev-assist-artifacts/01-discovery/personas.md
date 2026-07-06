# Discovery §2 — Personas & Workflows (Roster)

**Stage**: 01-Discovery · Section 2
**Date**: 2026-05-28
**Method**: 6 parallel `persona-researcher` agents (one per candidate persona), each with live web research. Classification: **priority** (4B mode: high/medium/low + audience), not T1/T2/T3.

> **Brownfield Mode — Source Signal vs Gaps**
> - **From assessment (cited):** personas were *implicit* in `DATASHEET.md` "Uses" (rated WEAK, finding m1) — now formalized.
> - **Inferred but unconfirmed:** YoY adoption/headcount and willingness-to-pay are **agent-inferred** (no clean series found); WTP ≈ $0 across all personas (CC0/open expectation) — value is reputational/strategic, not subscription.
> - **Gaps the user must fill:** real-user validation of these personas is a **Pass-2 follow-up** (interview ACL/PETS authors, Presidio/GLiNER maintainers, i2b2/n2c2 participants, DPOs).
> - **Does NOT cover:** non-consumer stakeholders (e.g., a neutral benchmark host/governance body — captured as a stakeholder note below, per the arms-length governance decision, not as a consumer persona).

---

## Persona roster

| ID | Persona | Priority | One-line audience |
|---|---|---|---|
| **P-mlnlp-researcher** | ML/NLP Privacy Researcher | **HIGH** (gates v1) | Academic+industry scientists publishing PII-detection / anonymization / re-id methods at ACL/EMNLP/NeurIPS-D&B/PETS; distribute via HF |
| **P-tool-builder** | Privacy-Tool Builder / OSS Maintainer | **HIGH** (gates v1) | Maintainers/authors of PII detectors & anonymizers (Presidio, GLiNER-PII, Piiranha, PII SDKs) needing an external reproducible harness |
| **P-acad-deid** | Academic De-identification Researcher | **HIGH** (credibility) | Clinical/legal/education NLP researchers who benchmark & publish PHI/PII de-id; the citation audience that confers legitimacy |
| **P-agentic-redteam** | Agentic-Security Red-Teamer | **MEDIUM** | AI red-team/safety engineers testing live LLM agents for PII leakage across channels |
| **P-priv-eng** | Enterprise Privacy / Platform-Security Engineer | **MEDIUM** (downstream) | Engineers operationalizing PII controls in prod; use the benchmark to **shortlist** before own-data POC |
| **P-dpo** | Compliance / Privacy Counsel / DPO | **MEDIUM** | DPOs certifying lawful end-states (anon vs pseudo); consume benchmark *evidence* via technical teams |

3 HIGH / 3 MEDIUM — a natural distribution. The 3 HIGH personas are the v1-gating + credibility cohorts named by the refined POV; the 3 MEDIUM are real but downstream/secondary.

---

## Condensed profiles

### P-mlnlp-researcher — ML/NLP Privacy Researcher · HIGH
**Goals:** benchmark new anon/pseudo methods against re-id AND utility on a shared corpus; evaluate LLM semantic re-identification without IRB-blocked real data; report powered per-slice + calibrated results. **Pains:** domain-siloed benchmarks (i2b2/TAB are clinical/legal English-only); no shared anon/pseudo scoring; **synthetic-only external-validity attack in review**; bespoke re-id scoring; discovery harder since Papers-with-Code shutdown (Jul 2025) → HF leaderboards now canonical. **Adoption:** the re-id subfield is hot in 2026; PII-Anon's three gaps (multilingual breadth, RRS scoring, pseudonymization-integrity + paired personas) map to what current papers hand-roll. **Bounce:** synthetic-only citation ceiling — uses it as a *pre-screen*, withholds headline claims until the real-data validation slice lands.

### P-tool-builder — Privacy-Tool Builder / OSS Maintainer · HIGH
**Goals:** prove a change improves detection without silent regressions (CI gate); publish a credible neutral number; cover multilingual/adversarial edges; for anon/pseudo authors, show utility-preservation + re-id resistance (which **no public benchmark scores**). **Pains:** no standard yardstick (Presidio maintainer: *"no formal results, and it's somewhat intentional"*); thin Faker-based home-grown eval data; leaderboards get gamed. **Adoption:** already self-benchmark against borrowed HF sets; CC0 + stratified splits + CoNLL/Parquet + Tier-2/3 scoring fit CI + publishable results; likely to contribute recognizers. **Bounce:** synthetic-only (want real-data slice), any whiff of vendor capture, weak leaderboard hygiene (need held-out labels + submission provenance).

### P-acad-deid — Academic De-identification Researcher · HIGH
**Goals:** publish defensible de-id evaluations; share corpora without leaking PHI (+ prove low residual re-id); compare methods on a common well-powered benchmark. **Pains:** **synthetic citation ceiling** (load-bearing objection); real corpora tiny/gated (i2b2 2014 = 1,304 notes; TAB = 1,268 cases; OpenDeID = 2,100) → low per-slice power; schema fragmentation; new: LLMs re-identify even after PHI removal and no established benchmark measures resistance. **Adoption:** would cite as *supplementary/stress-test* today; first-class citation unlocked by a **correlation study** showing PII-Anon model rankings track i2b2-2014/TAB rankings, ideally co-published with a recognized de-id group. **Bounce:** synthetic framed as a *replacement* for real PHI; heuristic-looking behavioral signals not calibrated against a real ESRC-style attack.

### P-agentic-redteam — Agentic-Security Red-Teamer · MEDIUM
**Goals:** quantify *per-channel* leakage under attack (output/tool/memory/inter-agent), not just final output; reproducible defense-comparable metrics; map to OWASP LLM02 / SAIF 2.0. **Pains:** output-only audits miss most leaks (**AgentLeak: 41.7% missed**); building realistic multi-agent envs is heavy; no shared neutral leakage scoring. **Adoption (honest):** their substrate is the **live harness** (AgentDojo/InjecAgent/AgentLeak); PII-Anon's **1,000 static AI-era records are NOT their agent-leakage benchmark.** PII-Anon is useful to them as (a) a **PII-recognition oracle** (65-type taxonomy + adversarial obfuscations) that a channel-sniffer calls to decide "did PII cross C1–C7?", (b) an **injection-payload seed library**, (c) **RRS on agent transcripts**. **Roadmap pull:** a live-harness adapter. **Bounce:** positioning the static track as agent-leakage scoring.

### P-priv-eng — Enterprise Privacy / Platform-Security Engineer · MEDIUM (downstream)
**Goals:** high recall on direct+contextual identifiers in *their* domain without over-redaction; a defensible, correctly-labeled (pseudo vs anon) control; fast shortlisting so POC effort hits the 1–2 finalists. **Pains:** vendor/single-dataset scores don't transfer (Presidio "cannot guarantee"; PIIBench <0.14 F1 harmonized); domain shift; traces/logs/agent-memory as an unbudgeted new PII datastore. **Adoption:** a *pre-screen* to drop tools that fail on breadth; a *regression/harness scaffold* (adopt PII-Anon's per-slice power + calibration + Tier-2/3 design to test finalists on **their own** corpus); a *coverage map*. **Bounce:** treating a synthetic leaderboard as a procurement oracle (the explicit anti-pattern) — zero distribution overlap with their data.

### P-dpo — Compliance / Privacy Counsel / DPO · MEDIUM
**Goals:** reach a *defensible* end-state classification (anonymized vs pseudonymized) backed by documented residual-risk; avoid marketing pseudonymized output as anonymized (EDPB 2025: pseudonymized data remains personal data); audit-ready artifacts. **Pains:** technical teams report span-F1, which says nothing about residual re-id or contextual leakage; anon-vs-pseudo collapsed into one "redaction quality" score is legally meaningless; no standardized neutral residual-risk yardstick. **Adoption:** rarely runs a benchmark — it's an **input their technical teams surface**. Values the **anon-vs-pseudo metric separation** (maps 1:1 to legal end-states), the **regulatory crosswalk**, **RRS/residual-risk** as quantitative backing for a motivated-intruder / "very small risk" argument, and **neutral CC0 governance** (a vendor's self-benchmark isn't citable in a DPIA; an arms-length one is). **Caveat:** synthetic RRS is evidence *scaffolding*, not a legal determination.

---

## Cross-persona synthesis (the signals that shape Requirements)

1. **The synthetic-only citation ceiling is universal** (4 of 6 personas name it). → The **real-data validation slice** (a correlation study vs i2b2-2014/TAB) is not optional; it is the single highest-leverage credibility unlock. Carry as a top open item to Requirements.
2. **Neutral governance is a hard trust gate** (tool-builders won't submit if vendor-captured; DPOs can't cite a vendor benchmark; researchers distrust vendor benchmarks). → Validates the **arms-length** decision; Requirements must include governance/neutrality + leaderboard-hygiene (held-out labels, submission provenance) as quality attributes.
3. **The agentic track must be honestly bounded.** Static records are a recognition oracle + payload library, NOT an agent-leakage benchmark. → Scope the agentic-leakage track as "PII-recognition layer for live harnesses + RRS-on-transcripts", with a live-harness adapter as a *roadmap* item, not a v1 claim. (Tempers finding from §0.)
4. **Anon-vs-pseudo separation + regulatory crosswalk + RRS** is the real-world "why" of the core thesis (DPO persona). → Reinforces axiom AX-pii-anon-004.
5. **Per-slice statistical power** is a genuine differentiator vs the tiny real corpora (i2b2 1,304 / TAB 1,268 / OpenDeID 2,100). → Reinforces axiom AX-pii-anon-003.
6. **New 2026 competitors to verify in §3:** RAT-Bench (arXiv 2602.12806), "From Weak Cues to Real Identities" de-anon (2603.18382), GLiNER Guard (2605.05277), AgentLeak (2602.11510). Papers-with-Code shutdown (Jul 2025) → HF leaderboard is the discovery surface.

**Stakeholder note (non-persona):** the **neutral benchmark host / governance body** is a stakeholder created by the arms-length governance decision — not a consumer persona. Carried to Stage-3 Design (distribution + leaderboard governance), not the persona roster.

---

## Methodology & Epistemic Honesty
- Personas are **agent-researched** with live web evidence (sources cited per profile in the agent outputs; key dated sources: Presidio eval docs, TAB/i2b2/OpenDeID papers, AgentLeak/AgentDojo/InjecAgent, EDPB 2025, ICO, HHS, Papers-with-Code shutdown). Competitor papers dated 2026 are **to be re-verified in §3**.
- Adoption/headcount/WTP are **agent-inferred** (no clean series); WTP ≈ $0 (CC0) — priority rests on strategic centrality, not revenue.
- **Real-user validation of all 6 personas is a Pass-2 follow-up** and is NOT performed here.

✅ **Section 2 VALIDATED (2026-05-28)** — workflows captured in `workflow-maps.md`; proceeding to §3 Market Research.
