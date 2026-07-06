# Traceability Matrix

**Stage 2 · R8** · 2026-05-28 · `provisional_status` per row. Chain: PGO → UC → FR/NFR → (DC → Story → Test in later stages).

## Forward: UC → FR/NFR → priority
| UC | FRs | NFRs | Priority | provisional_status |
|---|---|---|---|---|
| UC-01 detection CI gate | FR-001, FR-002, FR-003 | NFR-002, NFR-016 | MUST | AGENT_SIMULATED |
| UC-02 powered per-slice + crossed cells | FR-004, FR-029 | NFR-001, NFR-002, NFR-003, NFR-018 | MUST | AGENT_SIMULATED |
| UC-03 calibration | FR-005 | NFR-008 | SHOULD | AGENT_SIMULATED |
| UC-04 anon residual+utility | FR-006 | NFR-005 | MUST | AGENT_SIMULATED |
| UC-05 measured RRS | FR-007, FR-008, FR-009, FR-010 | NFR-007 | MUST | AGENT_SIMULATED |
| UC-06 pseudo-integrity | FR-011, FR-012, FR-013 | NFR-005 | MUST (persona-stratified) | AGENT_SIMULATED |
| UC-07 query-aware | FR-014 | — | SHOULD | AGENT_SIMULATED |
| UC-08 agentic oracle | FR-017, FR-018, FR-020 | — | COULD | AGENT_SIMULATED |
| UC-09 transcript residual | FR-019 | — | COULD | AGENT_SIMULATED |
| UC-10 end-state + crosswalk | FR-021, FR-022 | NFR-005, NFR-015 | MUST | AGENT_SIMULATED |
| UC-11 neutral leaderboard | FR-023 | NFR-014 | MUST | AGENT_SIMULATED |
| UC-12 CC0 + contribution | FR-024, FR-025, FR-028 | NFR-011, NFR-012, NFR-013 | MUST (exports) / SHOULD (contrib) | AGENT_SIMULATED |
| UC-13 real-data correlation | FR-027 | NFR-003 | SHOULD (v1.1) | **PERSONA-CONDITIONAL** (Pass-2) |
| UC-14 shortlist/pre-screen | (leaderboard filter, via FR-023) | — | COULD | AGENT_SIMULATED |
| UC-15 governance lifecycle | FR-025, FR-026 | NFR-014 | MUST | AGENT_SIMULATED |
| (N1 coreference/quasi-id) | FR-015, FR-016 | — | SHOULD (v1.1) | **PERSONA-CONDITIONAL** |

## Reverse: every MUST FR/NFR → PGO source (orphan check)
All 16 MUST FRs trace to ≥1 PGO via the R0 bridge (`_bridge/uc-pgo-map.md`): FR-001/002↔builder-01/priveng-03; FR-003↔builder-01; FR-004↔researcher-03/acaddeid-01; FR-006↔builder-03/dpo-02; FR-007/008/009↔researcher-02/acaddeid-02; FR-011/012/013↔builder-03/dpo-01; FR-021/022↔dpo-01/dpo-03; FR-023↔builder-02/researcher-01; FR-024↔acaddeid-03; FR-026↔§0-governance/UC-15; FR-029↔researcher-03/acaddeid-01 (UC-02). MUST NFRs trace to project axioms AX-001/002/003/004 + brownfield findings M1/C1. **No orphan MUSTs. No UC with only COULD requirements that is itself MUST-priority.** ✅

## Axiom → NFR linkage
- AX-pii-anon-001 (no-real-PII) → NFR-006, NFR-015
- AX-pii-anon-002 (determinism) → NFR-004
- AX-pii-anon-003 (statistical power) → NFR-001, NFR-002, NFR-003, NFR-018, FR-029
- AX-pii-anon-004 (anon/pseudo separation) → NFR-005, FR-021

## Brownfield finding → requirement closure
- M6 (no running scorer) → FR-006, FR-007, FR-011 (the core build)
- M1 (doc/data drift) → NFR-013
- M2/M3 (no power/traceability) → NFR-001/002/003/018, FR-029, this matrix (committed-lattice gate + sha256 manifest)
- C1 (0 tests) → NFR-016
- o5 (train-vs-eval contradiction) → NFR-015

## Status Change Log
| Date | Req | From | To | Reason |
|---|---|---|---|---|
| 2026-05-28 | FR-027, FR-015, FR-016 | AGENT_SIMULATED | PERSONA-CONDITIONAL | academics MUST-for-citation but v1.1/Pass-2; carried as constrained extension seams |
| 2026-05-29 | NFR-018, FR-029 | (new) | AGENT_SIMULATED | S-PWR statistical-power work-stream: committed-lattice per-cell power gate + audit/enforcement/emission capability; extends AX-003 to crossed cells |
| 2026-05-29 | NFR-018 | (new) | ACCEPTED-WITH-CAVEATS | R10 10-persona panel: tier numbers (1,522/753/200) locked, 0 REVISE; 6 mechanism/framing refinements bound (corpus-power vs regression gate; track-scoping; non-strippable external-validity caveat; curated 2-way set). NFR-001 co-validated. See `_threshold-validation/findings-nfr-018-2026-05-29.md` |
| 2026-05-30 | FR-022, NFR-012 | AGENT_SIMULATED | AGENT_SIMULATED (verified) | Sprint S5: FR-022/gov-02 legally-distinct regulatory crosswalk verified-by S5-01; NFR-012 Croissant validate-AND-load (HF `datasets` round-trip, gov-02 reg_* columns intact) verified-by S5-03. Story gates APPROVE 5/5. |
| 2026-05-30 | FR-024 | AGENT_SIMULATED | AGENT_SIMULATED (verified, fully closed) | Sprint S5: CC0 standard exports + CLI — Parquet (S5-02), Croissant + dataset card (S5-03), spaCy + CoNLL (S5-04), `pii-anon` CLI (S5-05); JSONL pre-existing. FR-024 fully closed across the export surface. |
| 2026-05-30 | FR-021 | AGENT_SIMULATED | AGENT_SIMULATED (verified) | Sprint S5: DPIA-input end-state bundle (anon/pseudo evidence kept SEPARATE per NFR-005/AX-004; non-strippable disclaimer) verified-by S5-06. |
| 2026-05-30 | NFR-013 | AGENT_SIMULATED | AGENT_SIMULATED (verified) | Sprint S5: documentation-drift remediation — 7 docs at canonical 575,604/2,486,438/63/v2.0.0; `tests/test_doc_drift.py` pins zero current-state drift; verified-by S5-07. |
| 2026-05-31 | FR-023 | AGENT_SIMULATED | AGENT_SIMULATED (verified) | Sprint S6: neutral leaderboard — append-only hash-chained held-out store (S6-01, held-out gold never stored + `verify_chain`) + opt-in publish & anti-gaming policy (S6-02, rate-limit/rotation/contamination) + CoI recusal (S6-03). |
| 2026-05-31 | FR-026 | AGENT_SIMULATED | AGENT_SIMULATED (verified) | Sprint S6: governance charter — gov-03 `CoIRecord` (S6-03, non-strippable no-pre-pub attestation + recusal for maintainer/pii-anon-core) + GOVERNANCE.md (S6-04, charter + aspirational/AGENT_SIMULATED roster + CoI naming pii-anon-core + honest bus-factor=1). |
| 2026-05-31 | FR-025 | AGENT_SIMULATED | AGENT_SIMULATED (verified) | Sprint S6: contribution pipeline — CONTRIBUTING.md (S6-05): PR template + CC0 license-compat checklist + synthetic-only provenance gate (AX-001) + deprecation/erratum policy + semver dated releases. |
| 2026-05-31 | NFR-014 | AGENT_SIMULATED | AGENT_SIMULATED (verified) | Sprint S6: governance neutrality auditable — GOVERNANCE.md + advisory roster + CoI present (S6-04); leaderboard anti-gaming control active (S6-02); submission provenance logged (S6-01 `verify_chain` + forbidden-key reject; S6-03 attestation/recusal). |
| 2026-05-31 | FR-017 | AGENT_SIMULATED | AGENT_SIMULATED (verified, fully covered) | Sprint S7: PII-recognition oracle (S7-01, non-strippable "never agent-leakage scoring" guard) + injection payload library (S7-02, InjectionPayload tuples, 3 INERT faithful transforms base64/ocr/zero-width). Both halves ship. |
| 2026-05-31 | FR-027 | PERSONA-CONDITIONAL | PERSONA-CONDITIONAL (v1 SEAM verified; real-data correlation = Pass-2) | Sprint S7: correlation harness (S7-03) — Kendall-τ/Spearman + seeded bootstrap + Bland-Altman; real i2b2/TAB ABSENT → `RealDataAbsent` never-fabricate sentinel. Synthetic→real transfer delta carried to Stage-5 Pass-2. |
| 2026-05-31 | FR-015, FR-016 | PERSONA-CONDITIONAL | PERSONA-CONDITIONAL (v1 SEAM verified; full scoring = v1.1/Pass-2) | Sprint S7: coreference + quasi-id slice loaders (S7-04) with non-strippable ~72%-formulaic low-power caveat; the chain-as-a-unit / quasi-id-combination SCORING is v1.1/Pass-2. |
| 2026-05-31 | FR-018, FR-019, FR-020 | (roadmap) | DOCUMENTED (v1.x roadmap, NOT shipped) | Sprint S7: ROADMAP.md (S7-05) documents cross-turn fragmented leakage / transcript-residual / live-harness adapter as future v1.x, anchored to the v1 oracle/payload seams. |
| 2026-05-31 | NFR-010b (+010c) | PROVISIONAL (AGENT_SIMULATED, real_user_needed) | INSUFFICIENT_EVIDENCE (agent-env indicative; real 8-core reference-host run owed) | Stage-5 Pass-2: shipped `scripts/benchmark_throughput.py` (seeded `SEED_BENCHMARK=20260531`, 17 tests) — closes the "no throughput harness in-repo" gap. INDICATIVE agent-sandbox run (10-core Apple-Silicon, NOT the declared 8-core host): regex lightweight path **17,507 rec/s** (p50/p95/p99=39.8/147.7/191.1µs) vs ≥5,000 target; score_detection 50,317 rec/s; spaCy-NER 108 rec/s (NFR-010a, no floor); transformer/LLM exempt. Per protocol §8 (no canonical reference host provisioned), canonical NFR-010b stays **unmeasured**; release stays **SHIP-WITH-CAVEATS** (Caveat 5); **no T6 re-rule** (no real-host evidence). evidence dev-assist-artifacts/05-testing/05-pass2/NFR-010/outcome.md |
