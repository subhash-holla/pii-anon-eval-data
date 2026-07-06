# Requirements Document — PII-Anon Benchmark (canonical)

**Stage 2 · R8 (canonical output)** · 2026-05-28 · Ready for Stage 3 Design.
`provisional_status: AGENT_SIMULATED` (all requirements; real-user Pass-2 in Stage 5).
Vocabulary: FR = Benchmark Capability · NFR = Quality Attribute · UC = Evaluation Scenario · PGO = Benchmark Goal.

## Executive summary
PII-Anon's requirements operationalize the refined POV: an open (CC0), independently-governed benchmark that **scores** PII detection, anonymization (residual re-id + utility), and **pseudonymization-integrity** as separate, statistically-powered, multilingual tracks — with **LLM re-identification-resistance scoring** as the headline and **pseudonymization-integrity** as the moat. The dominant engineering theme is **closing finding M6**: turning the existing precomputed Tier-2/3 *annotations* into *running scorers* that ingest a system's output. The dominant credibility theme is the **real-data validation slice** (v1.1). Governance is **arms-length neutral** (no certification/paid-eval monetization).

## Counts
- **29 Functional Requirements** (`functional-requirements.md`) — 17 MUST · 8 SHOULD · 4 COULD.
- **18 Non-Functional Requirements** (`non-functional-requirements.md`) — quantified thresholds; 6 R10-stress-tested, rest audit-validated.
- **15 UCs · 18 PGOs · 6 personas** carried from Discovery (R0 bridge, 0% orphan).
- Total requirements: **47**.
- *(2026-05-29 S-PWR amendment: +FR-029 committed-lattice power audit/enforcement, +NFR-018 committed-lattice per-cell power; see `03-design/sampling-design.md`.)*

## Priority register
**MUST (v1 floor):**
FR-001 detection scoring · FR-002 deterministic CI gate · FR-003 scorer I/O contract + Presidio adapter · FR-004 per-slice CIs · FR-006 anon output Pareto · FR-007 measured RRS · FR-008 exposure-index (≠RRS) · FR-009 non-strippable caveat · FR-011 pseudo-integrity (threat-modeled) · FR-012 collision-type separation · FR-013 referential-integrity + key/state separation · FR-021 end-state evidence bundle · FR-022 legally-distinct crosswalk · FR-023 neutral leaderboard · FR-024 CC0 + exports (Croissant validates+loads) · FR-026 governance charter · FR-029 committed-lattice power audit & enforcement
NFR-001 statistical power · NFR-002 CI-on-every-metric · NFR-005 anon/pseudo separation · NFR-006 no-real-PII · NFR-007 adversary version-pinning · NFR-011 coverage (incl. financial PII) · NFR-012 Croissant/HF loadability · NFR-013 no doc/data drift · NFR-014 governance neutrality · NFR-015 license/ethics · NFR-016 harness test coverage · NFR-017 threshold-validation transparency · NFR-018 committed-lattice per-cell power

**SHOULD:**
FR-005 calibration · FR-010 adversary pluggability · FR-014 query-aware · FR-015 coreference scoring (v1.1) · FR-016 quasi-id-combination (v1.1) · FR-025 contribution pipeline · FR-027 real-data correlation (v1.1) · FR-028 frictionless citation
NFR-003 per-language power table · NFR-008 calibration target · NFR-009 eval-cost + cheap-adversary · NFR-010 throughput + runtime dimension

**COULD:**
FR-017 agentic oracle + payloads (SHOULD-for-redteam) · FR-018 cross-turn fragmented payloads · FR-019 transcript residual · FR-020 live-harness adapter (roadmap)

## Top Design inputs (the load-bearing decisions for Stage 3)
1. **Scorer architecture (closes M6):** a uniform scoring interface with a documented I/O contract (entity-type crosswalk + span-matching policy) + Presidio reference adapter, dispatching to detection / anon / pseudo / re-id scorers — the central new component.
2. **De-circularized RRS:** measured-attack pipeline (version-pinned + pluggable adversary, |C| param, Wilson CIs) + a separate exposure-index pre-screen + non-strippable caveat embedded in output.
3. **Pseudonymization-integrity engine:** threat-model + collision-type separation + key/state-separation test.
4. **Statistical-power layer:** per-slice n + Wilson/Clopper-Pearson CIs + paired comparison + stratified enrichment + per-language power table + a **committed evaluation lattice** (DOE: main effects + 3 named 2-way interactions; risk-tiered NIST targets; CI-blocking power gate) — see `03-design/sampling-design.md` + NFR-018/FR-029.
5. **v2.0.0 schema + migration** (restructuring is in scope) — reconcile the stale prior v2.0.0 commit; preserve v1.3.0 (git tag) + datasheet/migration update.
6. **Distribution + governance:** HF dataset card + Croissant + neutral leaderboard (held-out + opt-in + anti-gaming) + GOVERNANCE.md.
7. **Engineering baseline:** pytest suite + CI (closes C1, was 0%); doc/data drift fix (M1).

## DIVERGED / PERSONA-CONDITIONAL flags carried to Design
- **FR-027 real-data slice + FR-015/016 coreference/quasi-id:** PERSONA-CONDITIONAL (academics MUST-for-citation; v1.1) — Design carries them as constrained extension seams.
- **Pseudonymization-integrity:** persona-stratified MUST (audience documented).
- See `_threshold-validation/` (R10) for NFR threshold outcomes.

## See also
`functional-requirements.md` · `non-functional-requirements.md` · `traceability-matrix.md` · `methodology.md` · `_bridge/uc-pgo-map.md` · `prioritization-decisions.md`.
