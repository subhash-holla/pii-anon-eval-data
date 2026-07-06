# Functional Requirements (Benchmark Capabilities)

**Stage 2 · R1+R4 (folded) → R8/R9** · 2026-05-28 · `provisional_status: AGENT_SIMULATED` (all, pending real-user Pass-2)
Vocabulary: FR = **Benchmark Capability**. Each FR = a dataset property OR a harness capability with boolean-testable Given/When/Then.

> **Note on phase folding (epistemic honesty):** R1 (low-fi) and R4 (hi-fi) were authored together from the rich Discovery signal (15 SME-reviewed UCs + 5 SME reviews + 15 concept-value interviews). R3 simulated interviews then run as a **validation/refinement** pass against this set (see `interview-synthesis.md`); refinements are applied in place and logged. Drafting agents (fr-author) were not separately dispatched — authoring drew on the identical Discovery inputs they would have read.

## Detection track (DET)
- **FR-001 — Multilingual/adversarial detection scoring.** GIVEN a detector's spans on a test slice, WHEN scored, THEN strict + partial P/R/F1/F2 are emitted **per language and per attack-type slice**. *(UC-01; MUST)*
- **FR-002 — Deterministic CI regression gate.** GIVEN a fixed seed + split, WHEN a detector is re-scored, THEN results are byte-identical AND CI fails on an F2 regression beyond tolerance OR a known-injected homoglyph/ZWSP/BiDi/encoded bypass that goes undetected. *(UC-01; MUST)*
- **FR-003 — Scorer I/O contract + reference adapter.** GIVEN a system's native output schema, WHEN adapted, THEN a documented entity-type crosswalk + offset convention + span-matching policy (exact/partial/type-relaxed) maps it, AND a working **Presidio reference adapter** ships. *(UC-01 cross-cutting; MUST)*
- **FR-004 — Per-slice scoring with confidence intervals.** GIVEN scores on a slice with n positives, WHEN reported, THEN a **Wilson or Clopper-Pearson** CI accompanies each metric (never bare Wald/point). *(UC-02; MUST)*
- **FR-005 — Calibration + abstain-to-review.** GIVEN a detector emitting confidences, WHEN evaluated, THEN ECE + Brier + a reliability diagram per entity class AND an abstention coverage-risk curve are produced. *(UC-03; SHOULD)*

## Anonymization track (ANON)
- **FR-006 — Anonymization output scorer (Pareto).** GIVEN a *system's anonymized text* (not precomputed annotations), WHEN scored, THEN residual-re-id-risk (under a declared threat model) AND downstream utility (under a pinned probe) are emitted as a **privacy-utility Pareto point**, never merged into one number. *(UC-04; MUST — closes M6)*
- **FR-007 — Measured-attack RRS.** GIVEN anonymized output + 2,500 paired pseudonymous↔real personas, WHEN the version-pinned LLM adversary runs over candidate set |C|=N, THEN empirical re-id recall AND precision (with Wilson CIs) are measured and **RRS = 1 − recall×precision** reported, with |C| as a stated parameter. *(UC-05; MUST — headline)*
- **FR-008 — Exposure-index pre-screen.** GIVEN behavioral-signal annotations, WHEN computed, THEN a deterministic exposure index is emitted **explicitly labeled a pre-screen prior, NOT RRS**, AND the index↔measured-RRS correlation is reported. *(UC-05; MUST)*
- **FR-009 — Non-strippable anti-anonymity caveat.** GIVEN any emitted RRS/residual-risk artifact, WHEN exported, THEN the caveat ("relative metric under a synthetic adversary; NOT an anonymity threshold; MUST NOT be cited as 'anonymized' under GDPR/HIPAA") is embedded in the artifact itself, not only docs. *(UC-05/10; MUST)*
- **FR-010 — Adversary pluggability.** GIVEN a consumer-named adversary model, WHEN configured, THEN RRS runs against it with full version-pinning recorded ("vs adversary@version"); ≥1 distractor-augmented (web-like auxiliary) variant is available. *(UC-05, N3; SHOULD)*

## Pseudonymization track (PSEUDO — the moat)
- **FR-011 — Pseudonymization-integrity scorer (threat-modeled).** GIVEN a pseudonymizer's output + an enumerated attacker-capability threat model, WHEN scored, THEN unauthorized-reversal rate (against that model) AND authorized-reversal success are emitted. *(UC-06; MUST)*
- **FR-012 — Collision-type-separated scoring.** GIVEN tokens, WHEN collisions are counted, THEN intended deterministic-linkage collisions (a referential-integrity feature) are reported separately from unintended cryptographic collisions (a fault); correct deterministic pseudonymizers are never penalized. *(UC-06; MUST)*
- **FR-013 — Referential integrity + key-rotation + key/state separation.** GIVEN a pseudonymized corpus, WHEN tested, THEN: referential integrity verified on reference joins; key-rotation pass/fail (post-rotation authorized reversal succeeds, cross-epoch unauthorized linkage fails); AND a key/state-separation test (can records be re-joined from the artifact **alone** without the external secret — EDPB Art. 4(5)). *(UC-06; MUST)*

## Query-aware + contextual identification
- **FR-014 — Query-aware masking scorer.** GIVEN a query + context with relevant + irrelevant PII, WHEN scored, THEN PII-relevance P/R + answer-quality delta + over-redaction + false-retention rates are emitted on the 8K+ query-aware records. *(UC-07; SHOULD)*
- **FR-015 — Coreference-chain scoring (as a unit).** GIVEN coreference chains, WHEN scored, THEN a chain is counted detected only if the linked mentions are scored as a unit (not atomic spans). *(N1; SHOULD)*
- **FR-016 — Quasi-identifier-combination scoring.** GIVEN multi-span indirect identifiers (e.g., job-title+employer+city), WHEN scored, THEN a quasi-identifier-combination slice measures indirect/contextual identification distinct from direct-span detection. *(N1; SHOULD — v1.1)*

## Agentic track (bounded)
- **FR-017 — PII-recognition oracle + payload library.** GIVEN a live agent harness, WHEN it calls PII-Anon, THEN a callable oracle API returns labeled-entity verdicts, AND injection payloads ship as (obfuscated-span + injection-carrier-template + intent-tag) tuples (multilingual/obfuscated); **never marketed as agent-leakage scoring**. *(UC-08; SHOULD)*
- **FR-018 — Cross-turn fragmented-leakage payloads.** GIVEN multi-turn agent scenarios, WHEN seeded, THEN payloads that fragment an identity across turns (partial name turn 1 + partial DOB turn 4, reassembled) are available. *(N6, UC-08; COULD)*
- **FR-019 — Transcript residual-leakage estimate.** GIVEN agent transcripts, WHEN evaluated per-channel/per-turn, THEN a behavioral-signal-residual estimate is emitted with a transcript-distribution caveat (final-output-only "low risk" is out of scope). *(UC-09; COULD)*
- **FR-020 — Live-harness adapter (roadmap).** GIVEN AgentDojo/InjecAgent, WHEN integrated, THEN the oracle is invoked at each of AgentLeak's 7 channel boundaries. *(UC-08; COULD — v1.x roadmap)*

## Compliance / end-state
- **FR-021 — Anon-vs-pseudo end-state evidence bundle.** GIVEN a transformation's output, WHEN assembled, THEN a DPIA **input** bundle separates anonymization (residual-risk+utility) from pseudonymization (integrity) evidence; labeled "informs, does not make, a determination." *(UC-10; MUST)*
- **FR-022 — Legally-distinct regulatory crosswalk.** GIVEN sensitivity-classed entities, WHEN crosswalked, THEN per-record GDPR / HIPAA-Safe-Harbor / HIPAA-Expert-Determination / CCPA-deidentified / PCI-DSS columns are kept **legally distinct at the display layer** (no cross-regime equivalence). *(UC-10, N9; MUST)*

## Distribution / governance
- **FR-023 — Neutral leaderboard.** GIVEN a submission, WHEN processed, THEN held-out labels stay undistributed; a published submission policy + anti-gaming control (rate-limit / held-out rotation / contamination check) + opt-in publish + private dry-run pre-score + config/version attestation + per-slice strengths apply. *(UC-11; MUST)*
- **FR-024 — CC0 corpus + standard exports.** GIVEN the corpus, WHEN exported, THEN JSONL + Parquet + **Croissant (validates + loads via HF datasets)** + spaCy + CoNLL formats + a dataset card are produced; deterministic load. *(UC-12; MUST)*
- **FR-025 — Contribution pipeline.** GIVEN an inbound contribution, WHEN submitted, THEN a PR template + provenance + CC0 license-compatibility check gate it; a deprecation/erratum policy + semantic-versioned dated releases exist. *(UC-12/15; MUST)*
- **FR-026 — Governance charter.** GIVEN the project, WHEN published, THEN GOVERNANCE.md + advisory-body roster + a CoI statement re: `pii-anon-core` + a bus-factor/succession note exist. *(UC-15; MUST)*
- **FR-027 — Real-data validation correlation harness.** GIVEN a shared model set, WHEN correlated vs i2b2-2014/TAB on the domain-matched English slice, THEN a pre-registered Kendall-τ/Spearman with bootstrap CI + Bland-Altman view is produced; co-publication governance terms recorded. *(UC-13; SHOULD — v1.1, Pass-2)*
- **FR-028 — Frictionless citation.** GIVEN a consumer, WHEN they cite, THEN a ready BibTeX + recommended citation template + a claims-policy (what synthetic-only does/doesn't support) are provided. *(N8; SHOULD)*

## Statistical-power audit & enforcement (cross-cutting)
- **FR-029 — Committed-lattice power audit, enforcement & per-cell provenance.** GIVEN the corpus + the frozen committed lattice (`eval_lattice.json`), WHEN audited, THEN positives-per-committed-cell are counted in one streaming pass, each cell is classified WELL-POWERED / UNDER-POWERED / EMPTY against its risk-tiered NIST target, a power matrix + slice heatmap are emitted, the build **FAILS** on any under-powered committed cell (`validate.py --lattice`), AND every published per-cell metric carries n + Wilson CI + design provenance (lattice cell id, tier, target_n, powered). *(UC-02; MUST — operationalizes NFR-001/003/018, AX-003; closes M2/M3)*

**Count: 29 FRs.** Priority hints: ~15 MUST · ~9 SHOULD · ~5 COULD (finalized in R7).
