# Pass-2 Protocol — Design & Thresholds Real-User Trial (the R10 panel was SIMULATED)

**Stage 5 · Wave T5 (Pass-2 coordination)** · 2026-05-31 · `pass2_required: false` (OPTIONAL; T6 → **SHIP-WITH-CAVEATS** for the AGENT_SIMULATED design rows if un-Pass-2'd, not DEFER).

**Pass-2 working files:** [`recruiting-checklist.md`](recruiting-checklist.md). **No `outcome.md` until real benchmark consumers (n=12–18) are interviewed out-of-band — a further agent-simulated cohort is REFUSED.**

> **NO agent-simulated cohort substitutes for this protocol — this item EXISTS because the design was only ever agent-simulated.** R10 (both the 6-persona 2026-05-28 panel and the 10-persona 2026-05-29 NFR-018 amendment) was an **agent-simulated** validator panel; `sampling-design.md §9` states plainly: *"no real-user trial of the design … provisional_status: AGENT_SIMULATED."* Running *another* simulated panel here would re-commit the exact gap. Pass-2 requires **real benchmark consumers**. Substituting any further agent-simulated cohort is a **CATASTROPHIC methodology violation** and is REFUSED.

---

## 1. Item under validation

| Field | Value |
|---|---|
| **Item** | The PII-Anon design + thresholds (sampling/power design, the 1,522/753/200 tiers, the anon/pseudo separation, the leaderboard/governance model, the agentic-track scoping) — **never validated with real benchmark consumers**. |
| **Source stage** | Design `sampling-design.md`, `D-implementation-ready-design.md`; Requirements R10 threshold-validation (`_threshold-validation/findings-nfr-018-2026-05-29.md`); Discovery concept-value study (`01-discovery/06-concept-value-study-synthesis.md`). |
| **Current status** | AGENT_SIMULATED across the design surface. R10 returned **ACCEPTED-WITH-CAVEATS** (tier numbers locked, 6 framing/mechanism refinements) — but **0 real users**. The concept-value study was **15 simulated agents**, explicitly *"NOT a substitute for real users; a real concept-value study is a Pass-2 follow-up."* |
| **Threshold under question** | Do the design's core value propositions and locked thresholds hold up with **real** ML/NLP researchers, privacy engineers, vendors, compliance reviewers, academic de-id researchers, and agentic red-teamers — i.e. is the simulated-panel ACCEPTED-WITH-CAVEATS verdict confirmed, refined, or invalidated by real consumers? |
| **Downstream impact** | The entire design rests on simulated signal. R10's own epistemic-honesty section names the real-user confirmations required (see §3). The concept-value study found the value score is *almost entirely gated by the synthetic-only ceiling* and that **neutral governance is a hard trust gate** ("if GOVERNANCE.md reads like a company's responsible-AI page, I'm out") — both are design bets that only real consumers can confirm. This is the broadest Pass-2 item; it underwrites the credibility of every AGENT_SIMULATED row. |

## 2. Why real USERS are needed (no simulation substitutes)

- Persona-pattern reasoning (however well web-grounded) is a *model* of a consumer, not a consumer. The design's load-bearing bets — "a synthetic-cell power gate reads as a methods strength," "the anon/pseudo separation maps 1:1 to legal end-states a DPO will rely on," "the agentic track is honest framing not a fig leaf," "neutral CC0 governance clears the trust gate" — are **acceptance** judgments that only real users in the role can render.
- The methodology is explicit that Pass-2 exists *precisely because* agent-simulated signal was insufficient at the source stage. Re-simulating would be circular.
- R10's caveats are **conditional** ("PERSONA-CONDITIONAL" for 6 of 10 sub-archetypes) — conditional on real-user confirmation. This protocol discharges those conditions.

## 3. Research questions (each maps to an R10 / concept-value open item)

> **RQ-1 (researcher / acad-deid):** Does a **synthetic-cell power gate** (the 1,522/753/200 tiers, NIST-derived) read as a methods *strength* in a real ACL/PETS/JAMIA de-id review — or as synthetic over-engineering? *(R10 caveat 1/3; concept-value "value capped at 6–7 by synthetic ceiling.")*
> **RQ-2 (tool-builder):** Does the **two-gate distinction** (corpus-power floor vs the FR-002 paired-McNemar detector-regression gate) match how a Presidio/GLiNER maintainer would actually run CI? *(R10 caveat 1.)*
> **RQ-3 (runtime priv-eng):** Does the committed-cell power *predict* own-data transfer well enough to use PII-Anon as a real **pre-screen**, and is the streaming/runtime story credible? *(R10 caveat 4; concept-value N4.)*
> **RQ-4 (DPO / compliance):** Is the **anon-vs-pseudo separation + regulatory crosswalk + RRS** defensible enough to surface in a real **DPIA** — and is the non-strippable caveat genuinely un-strippable in practice? *(R10 caveat 3; concept-value #4 "an engineer will strip it and hand me 'certified: anonymized'.")*
> **RQ-5 (agentic red-teamer):** Is the **agentic-track scoping** (recognition oracle + payload library + RRS-on-transcripts, live-harness adapter as roadmap) honest and useful — or does any "agent-leakage benchmark" framing lose the red-team community? *(R10 caveat 5; concept-value #7.)*
> **RQ-6 (all):** Is **neutral CC0 governance** (GOVERNANCE.md, advisory roster, CoI recusal) sufficient to clear the trust gate for citation/submission/DPIA use? *(concept-value #3, a hard gate.)*

## 4. Sample + cohort

- **n = 12–18 real participants**, **2–3 per persona** across the 6 (`personas.md`): P-mlnlp-researcher, P-tool-builder, P-acad-deid, P-priv-eng (incl. runtime + batch sub-types), P-dpo, P-agentic-redteam. Mirror the R10 10-sub-archetype split so the real study is comparable to the simulated one.
- **Sample-size justification:** qualitative **thematic saturation** for concept/threshold-acceptance studies is typically reached at ≈12–15 for a well-defined cohort (and the config sets `user_research_participants: 30` as the full-rigor ceiling; 2–3 per persona × 6 = 12–18 sits within it and matches the R10 panel granularity for direct comparison). This is acceptance confirmation per role, not a power calc.
- **Cohort criteria (per persona, match the role — do NOT cross-recruit):**
  - **P-mlnlp / P-acad-deid:** has published PII-detection / de-id / re-id work at ACL/EMNLP/NeurIPS-D&B/PETS/JAMIA; uses HF leaderboards.
  - **P-tool-builder:** maintains/authors a PII detector or anonymizer (Presidio, GLiNER-PII, Piiranha, a PII SDK).
  - **P-priv-eng:** operationalizes PII controls in production; runtime-gateway and batch-platform sub-types.
  - **P-dpo:** certifies lawful anon-vs-pseudo end-states; has touched a real DPIA.
  - **P-agentic-redteam:** red-teams live LLM agents for PII leakage (AgentDojo/InjecAgent/AgentLeak substrate).
- **Exclusion:** anyone whose role is only adjacent (e.g. a general ML engineer for the researcher slot, a generic security tester for the red-teamer slot, a privacy *researcher* for the DPO slot). Recruitment criteria must match the cohort under question — a wrong-role participant would produce off-target signal.

## 5. Recruitment channel

- **Organic (preferred for credibility):** the de-id / privacy-ML community (ACL/PETS/JAMIA authors, n2c2 participants, Presidio/GLiNER maintainers, DPO professional networks). Co-validation with a recognized de-id group also advances FR-027.
- **Paid (to fill gaps):** UserInterviews / Respondent with **hard role-screening** to the criteria above. Incentive: professional-rate honorarium (WTP ≈ $0 means no purchase intent, but research participation is paid).

## 6. Session structure (≈60 min semi-structured interview + artifact walkthrough)

- **0–5 min:** consent; framing (PII-Anon is a synthetic benchmark; we are validating the *design*, not selling).
- **5–15 min:** role + current benchmarking workflow + the pain PII-Anon targets (confirm the persona's real job-to-be-done).
- **15–35 min:** **artifact walkthrough** of the persona's gating design element (the power-gate / two-gate model / anon-pseudo separation / agentic scoping / governance charter) → the persona-specific RQ from §3. Show the real README power statement, GOVERNANCE.md, the sampling-design claim ladder.
- **35–50 min:** **threshold acceptance** — react to the locked 1,522/753/200 tiers (do they read as strength?), the non-strippable caveat (would your engineer strip it?), the neutral-governance bar (does it clear citation/DPIA/submission?).
- **50–60 min:** would you cite / submit-to / pre-screen-with / DPIA-cite this as-is; what one change would move you; would the FR-027 real-data slice change your answer.

## 7. Outcome capture

**Per-participant:** persona; accept / accept-with-condition / reject per design element; the threshold-acceptance reactions (power tiers, caveat un-strippability, governance bar); the "one change"; the stated dependency on FR-027.

**Roll-up (5-bucket ontology, mirroring R10 so the real study is directly comparable):** per-element distribution of ACCEPTED / PERSONA-CONDITIONAL / REVISE-TIGHTER / REVISE-LOOSER / DIVERGED; theme codes for recurring rationales; **which R10 caveats are confirmed vs newly-surfaced**; edge-case outliers.

## 8. Verdict mapping

| Outcome | Verdict | Status transition |
|---|---|---|
| Real consumers confirm the design elements + locked thresholds (≈R10's ACCEPTED-WITH-CAVEATS, no DIVERGED) | **REAL_USER_VALIDATED** | the AGENT_SIMULATED design rows → **AGENT_SIMULATED → REAL-USER-VALIDATED**; R10 caveats discharged; design credibility no longer rests on simulation. |
| Acceptance varies materially by persona | **PERSONA-STRATIFIED** | record per-persona acceptance; claims scoped to the personas that accept. |
| A threshold/element accepted-with-revision | **TIGHTENED / LOOSENED** | adjust the specific design element / threshold to the real-consumer operating point (numbers were "locked" only against the simulated panel). |
| A core bet is rejected by its gating persona (e.g. DPO won't DPIA-cite; red-team rejects the framing; governance fails the trust gate) | **PIVOT** | redesign that element before the dependent claim ships; ~10–20% of DIVERGED items invalidate the simulated-preferred choice — budgeted for. |
| No real participants recruited in-window | **INSUFFICIENT_EVIDENCE** | design stays AGENT_SIMULATED; the "no real-user trial of the design" caveat stands; **T6 → SHIP-WITH-CAVEATS**. |

**Status Change Log entry to write on outcome:**
`| <date> | (design surface: NFR-001/018, FR-021/023/026, agentic scoping) | AGENT_SIMULATED | <verdict> | Pass-2 real-user design/threshold trial (n=<...>, 6 personas): R10 caveats <confirmed/refined/pivoted>; evidence .../05-pass2/design-real-user-trial/outcome.md |`
