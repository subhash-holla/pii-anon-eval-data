# R7 — Survey Analysis (raw aggregate)

**Stage 2 · R7** · 2026-05-28 · 12 R6 respondents (researcher-academic, researcher-reid, tool-builder-oss, tool-builder-commercial, acad-deid-clinical, acad-deid-legal, redteam-frontier, redteam-enterprise, priv-eng-runtime, priv-eng-batch, dpo-eu, dpo-us). Full MoSCoW tally + decisions in `prioritization-decisions.md`.

## Cross-persona patterns
- **Near-unanimous MUSTs (low variance):** B6 measured-RRS (12/12), B7 non-strippable caveat (11/12), B5 anon-Pareto (11/12), B12 end-state+crosswalk (10/12). These are the consensus core — safe to lock.
- **Clean persona-split (high variance, expected):**
  - **Pseudonymization (B8):** MUST for tool-builder/DPO/batch; SHOULD/irrelevant for clinical-de-id (irreversible removal) + red-teamers. → persona-stratified MUST.
  - **Agentic (B11):** the ONLY bundle red-teamers rank MUST; everyone else COULD. → COULD.
  - **Coreference/quasi-id (B10):** MUST/SHOULD for legal-de-id + re-id specialist; SHOULD/COULD elsewhere. → SHOULD (v1.1), flagged as the highest-value SHOULD.
  - **Governance/citation (B13/B16):** MUST/high for DPO/researcher/OSS; low for red-teamers/commercial ("written for a research audience"). → B13 MUST (trust gate), B16 SHOULD.
- **Trade-off discriminators:** T4 (governance 7–5) and T5 (statistical power 10–2) were the most decisive; T1/T2/T3 split ~6–6 (confirming "ship both / defer depth & real-data to v1.1").
- **Recurring qualitative refinements (→ R9/Design):** several respondents flagged that **B11 bundles FR-018/020 (cross-turn fragmented payloads + live-harness adapter) too coarsely** — red-teamers want FR-018 escalated; and **B12 bundles two distinct artifacts** (DPIA evidence bundle vs regulatory crosswalk) that DPOs treat separately. Noted for Design granularity.

## Distribution check
Natural ~30/55/15 MUST/SHOULD/COULD; no majority-W bundle → no OUT items (UCs were SME-pre-filtered). Healthy.
