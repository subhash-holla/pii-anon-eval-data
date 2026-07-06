# NFR Verification Matrix — pii-anon-datasets v2.0.0

> Stage 5 · Wave T3 execution of every quantified / auditable Non-Functional Requirement from Stage 2.
> Produced by `dev-assist-testing-nfr-verifier`. Read-only on source; measurements re-run fresh this dispatch.

**Stage**: 05-Testing
**Date**: 2026-05-31
**Platform**: macOS (Darwin 25.5.0), Python 3.10.6, pytest 9.0.2, coverage 7.0.0; single host, AC, no contending load. **Results not portable** — the throughput dimension (NFR-010b/c) is explicitly deferred to a real-host Pass-2.
**Predecessor**: `dev-assist-artifacts/02-requirements/non-functional-requirements.md`
**Project-wide provisional status**: `AGENT_SIMULATED` (per `dev-assist-artifacts/02-requirements/traceability-matrix.md`). No NFR row carries an OPEN per-row `DIVERGED` flag; the only `real_user_needed: true` measurement is **NFR-010b/c** (throughput), which is PROVISIONAL pending Pass-2. All other rows are agent/test-layer VERIFIED.

---

## Matrix

| NFR ID | Class | Threshold | Measurement | Sample | Outcome | Delta | Verdict | Evidence |
|---|---|---|---|---|---|---|---|---|
| NFR-001 | Statistical power (marginals) | Every published committed-cell score has positives ≥ tiered target (≥1,522 / ≥753 / ≥200) or is excluded | `python3 scripts/validate.py` (NFR-018 gate, default streaming pass) | N=575,604 records, all committed cells | All committed cells meet their tiered power target; 0 validation errors; exit 0 | 0 shortfalls (margin ≥0 on every cell) | **PASS** | `scripts/validate.py`; `tests/test_validate_power_gate.py` (5/5); `tests/test_power.py` |
| NFR-002 | CI on every metric | 100% of metrics carry n + CI with **method named** (Wilson / Clopper-Pearson / paired-bootstrap / McNemar); zero bare points | `pytest tests/test_intervals.py tests/test_clopper_pearson.py tests/test_paired.py` | 21 stats tests | All 4 methods carry a named `method` field, asserted: `wilson`, `clopper-pearson`, `paired-bootstrap`, `mcnemar-exact`/`mcnemar-chi2-continuity` | 4/4 method labels present + round-trippable | **PASS** | `test_nfr_002_clopper_pearson_method_named`, `test_nfr_002_paired_bootstrap_method_named`, `test_wilson_point_and_brackets`, `test_fr_002_mcnemar_*`; src `stats/intervals.py:176`, `stats/power.py:13` |
| NFR-003 | Per-language + language×type power transparency | A per-language positive-count table AND a per-(language×entity-type) power matrix published; sub-tier cells labeled low-power | `pytest tests/test_language_power.py tests/test_power_table_reporting.py` + live reporter API probe | 10 tests | `reporting/language_power.py` exposes `per_language_table()` + `language_x_type_matrix()` + `render_csv/markdown`; low-power verdict ladder tested | Both required artifacts present | **PASS** | `test_nfr_003_*` (power_table + language_power); `reporting/language_power.py`, `reporting/power_table.py` |
| NFR-004 | Pure-stdlib core; heavy deps lazy | Deterministic generation; core imports with heavy deps absent (no top-level pyarrow/mlcroissant/spacy/anthropic) | `pytest -k "nfr004 or nfr_004"` (27 AST/lazy guards) + **direct lazy-import smoke** (blocked pyarrow/mlcroissant/spacy/anthropic, imported the 6 named subpkgs) | 27 guard tests + 6 direct imports | 27/27 guards pass; with all 4 heavy deps blocked, `distribution, cli, leaderboard, validation, subsets, compliance` all import OK | 6/6 lazy imports succeed; 0 banned top-level deps | **PASS** | 27× `test_nfr004_*` incl. `_imports_without_{mlcroissant,spacy,pyarrow,matplotlib}`; direct smoke (this dispatch) |
| NFR-005 | Anon/pseudo metric separation | **Zero** code paths merge anon + pseudo metric families into one headline score | `pytest tests/test_nfr005_separation.py` (AST + live-introspection audit) | 2 audit tests | `ParetoPoint` & `PseudonymizationReport`: no `__float__`, no merged/`combined`/`deid`/`overall`/`total_collisions` field; distinct return types; `scoring.__all__` carries no fused symbol | 0 merge paths found | **PASS** | `test_nfr_005_anon_and_pseudo_are_separate_modules`, `test_nfr_005_no_combined_deid_callable_in_scoring_public_api`; src `scoring/anonymization.py:12-17`, `scoring/pseudonymization.py:159` |
| NFR-006 | No real PII (AX-001 synthetic-only) | **Zero** real-PII leakage findings on corpus + fixtures; emitter payloads INERT | `pytest tests/test_payloads.py` (INERT) + synthetic-provenance guards; corpus provenance sample; `validate.py` (provenance REQUIRED field) | 575,604 records + payload/fixture tests | Every corpus record carries `provenance.source_type="synthetic_lattice_enrichment"` + seed + CC0; INERT payloads non-strippable disclaimer; validate.py 0 errors | 0 real-PII findings at test/corpus layer | **PASS** (test/corpus layer; canonical `--sensitive-data` + security-sast audit is the release gate) | `test_fr_017_payloads_are_inert`, `test_generated_records_are_synthetic_v2_and_provenanced`, `test_fr_025_contributing_has_provenance_and_synthetic_only`; AX-001 in `00-axioms/project-axioms.yaml` |
| NFR-008 | Calibration target (reference) | ECE per entity class; reference detectors target **ECE ≤ 0.05** (reported, NOT a pass/fail gate) | `pytest tests/test_calibration.py` | 8 tests | `meets_reference == (ece ≤ 0.05)` boolean; high-ECE input (0.29375) RETURNS without raising → reported-not-gated proven | n/a (reference, not gated) | **PASS** | `test_nfr_008_meets_reference_is_reported_not_gated`, `test_fr_005_ece_known_value`; src `stats/calibration.py` |
| NFR-010 | Scorer throughput + runtime | (a) per-class rec/sec reported, transformer/LLM exempt; **(b) lightweight path ≥5,000 rec/sec on 8-core + p50/p95/p99**; (c) batch wall-clock | None executable: no throughput harness / rec-sec emitter exists; `real_user_needed: true` (R10) | — (no benchmark to run) | **NOT MEASURED.** Throughput figure is agent-extrapolated from prod-gateway evidence; perf reviewers noted seam-scale only. No number fabricated. | n/a — Pass-2 outstanding | **PROVISIONAL** (`real_user_needed`) | `_threshold-validation/findings-summary.md:18,22` (010b/c `AGENT_SIMULATED, real_user_needed: true`) → see `05-pass2/` |
| NFR-012 | Croissant / HF loadability | Croissant **validates against spec AND loads via HF `datasets`** (not mere presence) | `pytest tests/test_croissant.py` | 18 tests (1 mlcroissant skip-if-absent) | `datasets.load_dataset('parquet', …)` round-trip loads exported Parquet with `reg_*` columns intact; mlcroissant absent → clear install `RuntimeError` (skip-if-absent) | Validate-AND-load both confirmed | **PASS** | `test_nfr_012_croissant_describes_loadable_parquet` (HF round-trip), `test_nfr_012_full_validation_skips_without_mlcroissant`; sprint-gate S5-03 (APPROVE 5/5) |
| NFR-013 | Documentation currency (no drift) | record count / entity-type count / version **identical across** README/TAXONOMY/DATASHEET/COMPARISON/Croissant; zero drift | `python3 -m pytest tests/test_doc_drift.py` | 6 tests | All 6 pass; canonical 575,604 / 2,486,438 / 63 / v2.0.0 pinned across 7 docs | 0 drift | **PASS** | `tests/test_doc_drift.py` (6/6); sprint-gate S5-07 (APPROVE 5/5) |
| NFR-014 | Governance neutrality (auditable) | GOVERNANCE.md + advisory roster + CoI present; leaderboard anti-gaming active; submission provenance logged | `pytest tests/test_governance.py tests/test_coi.py tests/test_leaderboard_policy.py tests/test_leaderboard_store.py` | 32 tests | GOVERNANCE.md + roster + CoI + bus-factor present; anti-gaming (rate-limit / rotation / contamination); provenance hash-chain + `verify_chain` tamper-detect | All 5 governance controls active | **PASS** | `test_nfr_014_governance_md_present`, `_rate_limit_blocks_excess`, `_held_out_rotation_epoch`, `_contamination_dup_check`, `_hash_chain_links_events`, `_verify_chain_detects_tampering`; sprint-gates S6-01/02/03/04-05 |
| NFR-016 | Harness test coverage | **≥85% line** on new/changed scorer modules **AND ≥70% branch** on scorer/statistical-computation modules; CI green | `pytest --cov=scoring --cov=stats --cov-branch` + full-suite green | scoring+stats: 1,493 stmts / 420 branches; full suite 347 tests | **LINE 95.18%** (1,421/1,493) · **BRANCH 84.52%** (355/420); full suite 346 passed / 1 skipped / 0 failed | line +10.18pp · branch +14.52pp | **PASS** | coverage JSON (this dispatch); full-suite green; cited scorer/stats tests |
| NFR-018 | Committed-lattice per-cell power (hard gate) | Every committed-lattice cell meets tiered positive target (≥1,522 / ≥753 / ≥200, NIST-derived); spec round-trips its generator (anti-drift) | `python3 scripts/validate.py` (exit 0) + `python3 -m pii_anon_datasets.stats.lattice --check` | 575,604 records; 730 committed cells | Gate: all committed cells pass, exit 0. Anti-drift: `eval_lattice.json` matches `build_committed_lattice()` — **730 cells** | 0 cell shortfalls; 0 drift | **PASS** | `scripts/validate.py`; `stats lattice --check`; `tests/test_lattice.py` (14), `test_lattice_audit.py` (6), `test_validate_power_gate.py` (5), `test_lattice_fill_determinism.py` (5); `_threshold-validation/findings-nfr-018-2026-05-29.md` |

---

## Aggregate

- **Total NFRs in scope (this dispatch)**: 13
- **PASS**: 12 — NFR-001, 002, 003, 004, 005, 006, 008, 012, 013, 014, 016, 018
- **PROVISIONAL** (real_user_needed / Pass-2 outstanding): 1 — NFR-010 (throughput dimension b/c)
- **FAIL**: 0

> Scope note: the Stage-2 NFR set has 18 entries. This dispatch verifies the 13 routed for T3. Not measured here: NFR-007 (adversary version-pinning — `test_adversary_port.py`/`test_llm_adversary.py`, audit), NFR-009 (cost budget + $0 offline mode — `test_offline_adversary.py`), NFR-011 (coverage 63/60/4 — `test_taxonomy.py`/`validate.py` coverage scan), NFR-015 (license/ethics audit), NFR-017 (`_threshold-validation/` completeness). These are auditable/boolean and were not in the T3 task list.

## FAIL Details

None.

## PROVISIONAL Details (real_user_needed Pass-2 outstanding)

### NFR-010 — PROVISIONAL (throughput dimension)

- **Why deferred**: R10 stratified the original single throughput gate into NFR-010a/b/c. **010b** (lightweight path ≥5,000 rec/sec on 8-core + p50/p95/p99) and **010c** (batch wall-clock) carry `provisional_status: AGENT_SIMULATED, real_user_needed: true`. The ≥5,000 figure is agent-extrapolated from prod-gateway evidence; the perf personas noted **seam-scale only**, and the DPO returned INSUFFICIENT_EVIDENCE on ops-NFRs (honest out-of-scope, not divergence).
- **Why not FAIL / not CATASTROPHIC-missing**: there is **no throughput benchmark harness or rec/sec emitter in the codebase** — by Stage-2/Stage-3 design this is a forward seam, not a Stage-4 deliverable that went missing. The runtime detection path that would emit per-class rec/sec is itself a Pass-2 build. No number was fabricated (discipline: do not assert PASS from extrapolation).
- **Agent-simulated outcome**: target ≥5,000 rec/sec (010b) / ~10k-row sampling guidance (010c) — unverified on real hardware.
- **Pass-2 protocol**: real-host measurement on an 8-core machine with a lightweight (regex) detection path; record rec/sec per detector-class + p50/p95/p99 latency + streaming/chunked input throughput. Route to `dev-assist-artifacts/05-testing/05-pass2/NFR-010/`.
- **Pass-2 confirmants** (from R10): a runtime privacy engineer (own-data transfer delta vs committed-cell prediction).
- **Verdict pending**: Pass-2 measurement → REAL_USER_VALIDATED → PASS, or threshold renegotiation → Stage-2.

## Per-NFR Detail (measurement protocols)

- **NFR-001 / NFR-018** — `python3 scripts/validate.py`: single streaming pass over `src/pii_anon_datasets/data/pii_anon.jsonl.gz` (575,604 records, 575,604 unique IDs, 0 errors), NFR-018 committed-cell power gate "All committed cells meet their tiered power target", exit 0. Anti-drift: `python3 -m pii_anon_datasets.stats.lattice --check` → "matches build_committed_lattice() — 730 cells", exit 0. Tiers (1,522/753/200) are NIST proportion-sized and R10-locked (`findings-nfr-018-2026-05-29.md`); scope to the detection track (RRS/utility re-id power ladder is a separate seam).
- **NFR-002** — every interval type stamps a non-strippable `method` label asserted by unit tests; `stats/power.py` projections stamp `method="wilson-projected"` so a design-time projection can never be mistaken for a measured CI.
- **NFR-004** — beyond the 27 keyword-matched `test_nfr004_*` guards (which monkeypatch heavy-dep absence), this dispatch ran a direct meta-path blocker over `{pyarrow, mlcroissant, spacy, anthropic}` and imported all 6 named subpackages successfully (RESULT: ALL 6 LAZY IMPORTS PASS, exit 0) — independent confirmation that lazy-import seams hold under genuine absence, not just simulated.
- **NFR-006** — corpus is synthetic-only by construction: `provenance` is a REQUIRED schema field (`validate.py` REQUIRED_FIELDS), validate.py passed 0/575,604, and a sampled record shows `source_type="synthetic_lattice_enrichment"`. The emitter/payload half is the INERT injection-payload library (`test_fr_017_payloads_are_inert`). The canonical AX-001 release gate (`/dev-assist-validate --sensitive-data` + `dev-assist-development-security-sast`, severity CATASTROPHIC) is a design-time audit hook layered above these test-level guards.
- **NFR-012** — round-trip executed because HF `datasets` IS present in this env; `mlcroissant` is absent so the full spec-validate test takes its skip-if-absent branch and asserts the clear `pip install pii-anon-datasets[croissant]` RuntimeError. Both directions covered.
- **NFR-016** — coverage scoped to `pii_anon_datasets.scoring` + `pii_anon_datasets.stats` with `--cov-branch`; line/branch extracted from coverage's own JSON (`covered_lines/num_statements`, `covered_branches/num_branches`). Full suite green is the CI gate.

## Methodology Notes

- **Statistical significance**: corpus-power NFRs (001/018) are **count-based, non-flaky** floors (positives-per-cell vs NIST-derived target), not sampled estimates — verdict is deterministic from a single streaming pass. CI-method NFRs (002) assert exact named methods + textbook values (e.g., Clopper-Pearson, McNemar exact-binomial) at 95% confidence.
- **Re-runs on failure**: policy is re-run 2× on first FAIL; **no FAIL occurred**, so no re-runs were needed. The single suite-level skip (`test_llm_adversary.py:234`, anthropic absent) is an expected optional-dep skip, not a failure.
- **Platform-portability disclaimer**: all results are this-host-specific. The corpus-power, separation, governance, doc-drift, coverage, and Croissant verdicts are platform-independent (deterministic given the frozen corpus + code). The **throughput** dimension (NFR-010b/c) is NOT portable and is the sole Pass-2 real-host item.
- **Outliers**: none applicable — no latency/throughput sampling was performed (NFR-010 deferred, not estimated).
- **Discipline**: read-only on source/tests; each verdict re-measured fresh this dispatch (no PASS asserted from prior runs); NFR-010 throughput number deliberately left unfabricated.

## Brownfield Mode — Source Signal vs Gaps

| Source signal (existing) | Gap (Stage 5 fills) |
|---|---|
| `scripts/validate.py` already enforces the NFR-018 committed-cell power gate + schema in CI | Formalized as the NFR-001/018 fresh measurement (575,604 records, 730 cells, exit 0) |
| `_threshold-validation/findings-*.md` record R10 outcomes (AGENT_SIMULATED) | NFR-010 carried as PROVISIONAL with explicit Pass-2 routing rather than a fabricated throughput figure |
| 27 in-suite `test_nfr004_*` lazy/AST guards (monkeypatched absence) | Independent direct meta-path-blocker smoke test confirming the 6 named subpkgs import under genuine heavy-dep absence |

---

**Template version**: 1.0 (developer-assistant v0.5.0)
