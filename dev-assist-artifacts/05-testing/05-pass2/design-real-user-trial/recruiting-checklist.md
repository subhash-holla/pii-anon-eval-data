# Recruiting Checklist — Design & Thresholds Real-User Trial

**Stage 5 · Wave T5 (Pass-2)** · 2026-05-31 · companion to [`protocol.md`](protocol.md).
This item **exists because the design was only ever agent-simulated** (R10 panels + the 15-agent
concept-value study). Pass-2 requires **real benchmark consumers**. Running another simulated panel
re-commits the exact gap and is a **CATASTROPHIC methodology violation — REFUSED**.
**No `outcome.md` until real participants are interviewed.**

## Sample
- ☐ **n = 12–18 real participants**, **2–3 per persona** across the 6 (`01-discovery`/`personas.md`):
  P-mlnlp-researcher, P-tool-builder, P-acad-deid, P-priv-eng (runtime **and** batch sub-types), P-dpo,
  P-agentic-redteam.
- ☐ Mirror the **R10 10-sub-archetype split** so the real study is directly comparable to the simulated one.
- ☐ Sample-size justification recorded: qualitative **thematic saturation** (≈12–15 for a well-defined
  cohort); within the `user_research_participants: 30` ceiling.

## Per-persona screening (match the role — do NOT cross-recruit)
- ☐ **P-mlnlp / P-acad-deid:** published PII-detection / de-id / re-id work at ACL/EMNLP/NeurIPS-D&B/PETS/JAMIA; uses HF leaderboards.
- ☐ **P-tool-builder:** maintains/authors a PII detector or anonymizer (Presidio, GLiNER-PII, Piiranha, a PII SDK).
- ☐ **P-priv-eng:** operationalizes PII controls in production; runtime-gateway **and** batch-platform sub-types.
- ☐ **P-dpo:** certifies lawful anon-vs-pseudo end-states; has touched a **real DPIA**.
- ☐ **P-agentic-redteam:** red-teams live LLM agents for PII leakage (AgentDojo/InjecAgent/AgentLeak substrate).
- ☐ **Exclusion:** adjacent-only roles (general ML engineer for the researcher slot, generic security
  tester for the red-teamer slot, a privacy *researcher* for the DPO slot) — wrong-role = off-target signal.

## Channels
- ☐ **Organic (preferred):** ACL/PETS/JAMIA authors, n2c2 participants, Presidio/GLiNER maintainers, DPO
  professional networks. (Overlaps the FR-027 de-id collaborator channel — co-validation advances both.)
- ☐ **Paid (gap-fill):** UserInterviews / Respondent with **hard role-screening**; professional-rate
  honorarium (WTP ≈ $0 ⇒ no purchase intent, but participation is paid).
- ☐ Consent + recording logistics; data-handling for participant identities.

## Session (≈60 min semi-structured + artifact walkthrough — protocol §6)
- ☐ Role + current benchmarking workflow + the pain PII-Anon targets.
- ☐ **Artifact walkthrough** of the persona's gating element (power-gate / two-gate model / anon-pseudo
  separation / agentic scoping / governance charter) → the persona-specific RQ (protocol §3).
- ☐ **Threshold acceptance:** react to the locked **1,522/753/200** tiers (read as strength?); the
  **non-strippable caveat** (would your engineer strip it?); the **neutral-governance** bar (clears
  citation/DPIA/submission?).
- ☐ Would you cite / submit-to / pre-screen-with / DPIA-cite as-is; the "one change"; does the FR-027
  real-data slice change your answer.

## Write-up (mirror R10's 5-bucket ontology for comparability)
- ☐ Per-element distribution: ACCEPTED / PERSONA-CONDITIONAL / REVISE-TIGHTER / REVISE-LOOSER / DIVERGED;
  theme codes; **which R10 caveats are confirmed vs newly-surfaced**.
- ☐ Write `outcome.md` (verdict per protocol §8) + Status Change Log row; re-run `/dev-assist-testing` T6.

> Until then: the design stays **AGENT_SIMULATED**; the "no real-user trial of the design" caveat stands;
> release stays **SHIP-WITH-CAVEATS** (Caveat 2). No further agent-simulated cohort substitutes (REFUSED).
