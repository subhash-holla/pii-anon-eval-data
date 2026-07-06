---
dev_assist_config: ./developer-assistant.yaml
schema_version: 2
---

# pii-anon-eval-data — PDLC Stage Manifest

> Single source of truth for stage progress, sub-phase status, agent deployments, sign-offs, and test mode. Updated by stage skills as work progresses; reconcile manually via `/dev-assist-manifest-update`.
>
> Per-project plugin configuration lives in `developer-assistant.yaml` (see `dev_assist_config` in frontmatter).

## Stage Status

| Stage | Status | Started | Completed |
|-------|--------|---------|-----------|
| 00-Brownfield Assessment | COMPLETE | 2026-05-28 | 2026-05-28 |
| 01-Discovery | COMPLETE | 2026-05-28 | 2026-05-28 |
| 02-Requirements | COMPLETE | 2026-05-28 | 2026-05-28 |
| 03-Design | COMPLETE | 2026-05-28 | 2026-05-28 |
| 04-Development | COMPLETE | 2026-05-28 | 2026-05-31 (all 7 sprints + S-PWR done) |
| 05-Testing | COMPLETE | 2026-05-31 | 2026-05-31 (SHIP-WITH-CAVEATS) |

Valid status values: `NOT_STARTED`, `IN_PROGRESS`, `COMPLETE`, `BLOCKED`, `DEFERRED`, `SUPERSEDED`.

## Project Metadata

| Field | Value |
|---|---|
| Project name | pii-anon-eval-data |
| Created | 2026-05-28 |
| Plugin version | 0.1.0 |
| Plan reference (current stage) | .claude/plans/luminous-pangolin.md (Discovery) · master: .claude/plans/users-subhashholla-library-mobile-docum-spicy-mochi.md |
| Language profile | python |
| Active domain packs | none |
| Test mode | tests-as-stage |
| Scope | brownfield (existing v1.3.0 benchmark) |
| Run depth | full rigor (interviews 30 / surveys 60 / research 30 / SME 9) |

## Discovery Phase Progress

| Section | Status | Artifact | User Approved? |
|---------|--------|----------|----------------|
| 0. POV Stress Test | VALIDATED | 01-discovery/00-pov-stress-test.md | ✅ 2026-05-28 |
| 1. Motivation & Background | VALIDATED | 01-discovery/01-motivation-background.md | ✅ 2026-05-28 |
| 2. Personas & Workflows | VALIDATED | 01-discovery/personas.md, workflow-maps.md | ✅ 2026-05-28 (6 personas: 3 high / 3 medium) |
| 3. Market Research (Pugh + JTBD + Kano) | VALIDATED | 01-discovery/03-market-research.md | ✅ 2026-05-28 (competitors verified; PII-Anon ranks #2 behind RAT-Bench until M6 closed) |
| 4. Use Cases | VALIDATED | 01-discovery/04-use-cases.md (v2), 08-use-case-review-synthesis.md | ✅ 2026-05-28 (15 UCs; 5-SME panel; 3 CATASTROPHIC resolved) |
| 5. Concept Value Study | VALIDATED | 01-discovery/06-concept-value-study-synthesis.md | ✅ 2026-05-28 (15-member cohort; 9 new items forward-deferred) |
| 6. Final Discovery Report | VALIDATED | 01-discovery/discovery-report.md | ✅ 2026-05-28 (canonical) |

## Requirements Phase Progress

| Phase | Status | Artifact | Notes |
|-------|--------|----------|-------|
| R0. UC↔P/G/O Bridge | VALIDATED | _bridge/uc-pgo-map.md | ✅ 0% orphan |
| R1. Low-Fidelity Requirements | VALIDATED | (folded into R4) | ✅ |
| R2. Interview Guide | VALIDATED | interview-guide.md | ✅ |
| R3. Simulated Interviews | VALIDATED | interview-synthesis.md | ✅ (re-analyzed §5 cohort; see methodology) |
| R4. High-Fidelity Requirements | VALIDATED | functional-requirements.md, non-functional-requirements.md | ✅ 28 FR + 17 NFR |
| R5. Prioritization Survey | VALIDATED | survey-instrument.md | ✅ |
| R6. Simulated Survey Responses | VALIDATED | survey-analysis.md | ✅ 12 respondents (representative) |
| R7. Prioritization Analysis | VALIDATED | prioritization-decisions.md | ✅ 30/55/15 MUST/SHOULD/COULD |
| R8. Final Requirements Artifacts | VALIDATED | requirements-document.md + traceability-matrix.md + methodology.md | ✅ canonical |
| R9. Cleanup + Verification-Strengthening | VALIDATED | audit-report.md | ✅ 4 strengthened |
| R10. NFR Threshold Validation | VALIDATED | _threshold-validation/findings-summary.md | ✅ 0 DIVERGED · 2 VALIDATED · 2 CAVEATS · 1 PERSONA-STRATIFIED |

## Design Phase Progress

| Diamond | Status | Artifacts | Outcome |
|---------|--------|-----------|---------|
| Prep | VALIDATED | 06-synthesis/D-implementation-ready-design.md §D0 | ✅ tensions + 4 axioms |
| D1 Design Cases | VALIDATED | §D1 | ✅ 15 DCs (JTBD lens) |
| D2 Workflow | VALIDATED | §D2 | ✅ Linear batch + callable scorer |
| D3 UI (consumer surfaces) | VALIDATED | §D3 | ✅ Minimalist CLI + Info-Dense reports (a11y de-scoped) |
| D4 System | VALIDATED | §D4 | ✅ Modular |
| D5 Architecture | VALIDATED | §D5 | ✅ Hexagonal (Clean inside stats) |
| D6 Synthesis | VALIDATED | 06-synthesis/D-implementation-ready-design.md + sme-heuristic-findings.md | ✅ + 3 audits + 3-SME panel (1 CAT + 9 MAJ resolved) |

## Development Phase Progress

| Wave | Status | Artifacts | Notes |
|------|--------|-----------|-------|
| W1. Preflight | COMPLETE | git tag v1.3.0; src layout decided (DX-01) | ✅ |
| W2. Planning | COMPLETE | 04-development/development-log.md (7-sprint plan) | ✅ |
| W3. Quality | COMPLETE | pyproject extras + branch coverage + Beta classifier | ✅ |
| W4. Testing setup | COMPLETE | pytest config (pythonpath=src) + tests/ scaffold | ✅ closes C1 |
| W5. Stories | COMPLETE | S1 + S2 + **S-PWR** + **S3** + **S4** + **S5** + **S6** + **S7** done (sprint-3: 8; sprint-4: 5; sprint-5: 7; sprint-6: 5; sprint-7: 5 stories) | ✅ |
| W6. Execution | IN_PROGRESS | S1 + S2 + **S-PWR** + **S3 scorer trio** (DC-06/07/08; M6 closed) + **S4 stats/reporting** (DC-09; FR-005 complete) + **S5 exports/CLI + compliance + doc-drift** (DC-12/DC-11/NFR-013: streaming Parquet + Croissant 1.0 JSON-LD + HF dataset card + spaCy DocBin + CoNLL + `pii-anon` 5-verb CLI — **FR-024 fully closed**; **NFR-012** Croissant validate-AND-load; **FR-021** DPIA-input EndStateBundle (anon/pseudo SEPARATE); **NFR-013** 7 docs canonical) + **S6 leaderboard + governance** (DC-13: held-out store + opt-in/anti-gaming + gov-03 CoI recusal + GOVERNANCE.md + CONTRIBUTING.md — **FR-023/025/026 + NFR-014 verified**) + **S7 extension seams** (DC-10/14/01: PII-recognition oracle + INERT injection payloads (**FR-017 fully covered**) + never-fabricate real-data correlation harness (FR-027 SEAM) + coreference/quasi-id slices (FR-015/016 SEAM) + FR-018/019/020 ROADMAP — 5 non-strippable scope-honesty guards; 5 story gates + S7 sprint gate APPROVE; **346 tests green / 1 skip**, every new module ≥85% cov; eval_lattice/corpus/tags untouched). **Development COMPLETE (8 sprints).** | ✅ all gates APPROVE |

## Testing Phase Progress

**Stage 5 verdict: SHIP-WITH-CAVEATS** (`05-testing/release-readiness-report.md`, 2026-05-31) — 12 NFR PASS / 1 PROVISIONAL (NFR-010 throughput, real-host Pass-2) / 0 FAIL; 5 non-strippable caveats; no MUST-track failure → no DEFER. Guardrails held (lattice 730 cells @ `47c3a8f`; tags intact; NFR-018 gate PASS; doc-drift 0).

| Section | Status | Artifact | Notes |
|---------|--------|----------|-------|
| Test architecture | COMPLETE | `05-testing/02-architecture/test-architecture.md` | pyramid; 96.4% line / 88.7% branch agg; scoring+stats 95.18%/84.52% (NFR-016 cleared) |
| NFR verification matrix | COMPLETE | `05-testing/03-nfr-verification/nfr-verification-matrix.md` | 12 PASS / 1 PROVISIONAL / 0 FAIL |
| Accessibility test plan | COMPLETE (N/A) | `05-testing/04-accessibility/accessibility-audit-results.md` | N/A — no UI surface (library + CLI) |
| Benchmark harnesses | HARNESS SHIPPED; canonical run owed | `scripts/benchmark_throughput.py` + `05-testing/05-pass2/NFR-010/{benchmark-plan,outcome}.md` + `run-record-agent-env.json` | NFR-010 throughput harness SHIPPED (seeded `SEED_BENCHMARK`, 17 tests; closes the "no harness in-repo" gap). INDICATIVE agent-env run: regex lightweight path 17,507 rec/s vs ≥5,000 (10-core Apple-Silicon — NOT the declared 8-core host). Canonical NFR-010b = INSUFFICIENT_EVIDENCE (real reference-host run still owed) → release **unchanged: SHIP-WITH-CAVEATS** (Caveat 5); no T6 re-rule |
| Examples and tests catalog | COMPLETE | `05-testing/examples-and-tests-catalog.md` | 29 FR + 18 NFR, 0 orphans; FR-014/028 noted SHOULD-scope gaps |
| Pass-2 protocols | COMPLETE (protocols only) | `05-testing/05-pass2/*/protocol.md` | 5 protocols (FR-027 / FR-015-016 / NFR-010 / design-real-user-trial / formulaic-monoculture); outcomes out-of-band; NO substitution |
| Release readiness | COMPLETE | `05-testing/release-readiness-report.md` | **SHIP-WITH-CAVEATS** |

## Sign-offs

| Sign-off ID | Date | Type | Scope | Signer | File |
|---|---|---|---|---|---|
| SO-01-spwr | 2026-05-29 | work-stream-close | S-PWR statistical-power & sampling-design (Reqs amendment + Design note + Dev sprint S-PWR + Full-Broad enrichment) | AGENT_SIMULATED | `_signoffs/SO-01-spwr.yaml` |
| SO-02-s3 | 2026-05-29 | work-stream-close | Sprint S3 — scorer trio (DC-06/07/08) + adversary port + reid power seam; M6 closed (4 privacy directions runnable); 8 stories, all gates APPROVE; 169 tests green | AGENT_SIMULATED | `_signoffs/SO-02-s3.yaml` |
| SO-03-s4 | 2026-05-29 | work-stream-close | Sprint S4 — stats/reporting completion (DC-09): Clopper-Pearson · paired McNemar/bootstrap · ECE/Brier · per-language power table · viz `[viz]` extra; FR-005 complete; 5 stories, all gates APPROVE; 211 tests green | AGENT_SIMULATED | `_signoffs/SO-03-s4.yaml` |
| SO-04-s5 | 2026-05-30 | work-stream-close | Sprint S5 — exports/CLI (DC-12) + compliance end-state bundle (DC-11) + doc-drift (NFR-013): streaming Parquet + Croissant 1.0 + HF card + spaCy/CoNLL + `pii-anon` CLI (**FR-024 fully closed**); **NFR-012** Croissant validate-AND-load; **FR-021** DPIA bundle (anon/pseudo SEPARATE); **NFR-013** 7 docs canonical; 7 stories, all gates APPROVE; 290 tests green | AGENT_SIMULATED | `_signoffs/SO-04-s5.yaml` |
| SO-05-s6 | 2026-05-31 | work-stream-close | Sprint S6 — leaderboard & governance (DC-13): append-only hash-chained held-out store (gold never stored + `verify_chain`) + opt-in/anti-gaming policy + gov-03 CoI recusal + GOVERNANCE.md + CONTRIBUTING.md; **FR-023/025/026 + NFR-014 verified**; 5 stories, all gates APPROVE; 325 tests green | AGENT_SIMULATED | `_signoffs/SO-05-s6.yaml` |
| SO-06-s7 | 2026-05-31 | work-stream-close | Sprint S7 — extension seams (DC-10/14/01): PII-recognition oracle + INERT injection payloads (**FR-017 fully covered**) + never-fabricate real-data correlation harness (FR-027 SEAM) + coreference/quasi-id slices (FR-015/016 SEAM) + FR-018/019/020 ROADMAP; 5 stories, all gates APPROVE; 346 tests green. **Closes Development.** | AGENT_SIMULATED | `_signoffs/SO-06-s7.yaml` |

## Methodology Notes

- **Cadence**: User validates at each stage checkpoint (CHECKPOINT 1–5 in the plan).
- **Evidence**: Two user-supplied research briefs (`pii_enterprise_landscape_may26.md`, `pii_eval_may26.md`) + own web research + existing project docs (README, TAXONOMY, DATASHEET, COMPARISON, CHANGELOG, MIGRATION).
- **Plan reference (current stage)**: `.claude/plans/users-subhashholla-library-mobile-docum-spicy-mochi.md`

### Benchmark-dataset adaptation (why the vocabulary is remapped)

This project is a **synthetic PII benchmark dataset + Python evaluation harness**, not a product with human end-users and a UI. The PDLC is run with a deliberate framing remap (also encoded in `developer-assistant.yaml.vocabulary`):

| PDLC concept | This project |
|---|---|
| Persona / user | Benchmark consumer (ML/NLP researcher, enterprise privacy engineer, privacy-tool vendor, compliance/legal reviewer, academic de-id researcher, agentic-security red-teamer) |
| PGO (Benchmark Goal) | e.g. "credibly compare detectors across contextual / multilingual / adversarial slices with stated statistical power" |
| UC (Evaluation Scenario) | e.g. "score query-aware masking on RAG prompts", "test pseudonym reversal integrity" |
| FR (Benchmark Capability) | a dataset property OR a harness capability |
| NFR (Quality Attribute) | coverage, statistical power (≥753 positives/slice for recall≈0.98 ±1pp), determinism, calibration reporting, synthetic-only/license/ethics, Datasheet+Croissant completeness |
| UI / screens | consumer surfaces: HF dataset card + Croissant metadata + leaderboard, CLI, exports (JSONL/Parquet/CoNLL/spaCy) |
| DC (Benchmark Component) | corpus/slices · schema/annotation model · generation pipeline · evaluation harness/metrics · scoring/reporting/leaderboard · distribution/exports |
| Accessibility/WCAG | de-scoped (no interactive web UI); documentation clarity only |

Three privacy directions get first-class, separate treatment: **detection** (span P/R/F1/F2 + calibration), **anonymization** (residual re-id risk + utility/Pareto), **pseudonymization** (reversal/collision/referential-integrity), plus cross-cutting **agentic leakage**.

## Handoff Signals

### Handoff signal to Requirements (post-Discovery, 2026-05-28)
> Discovery complete. 15 use cases (→ R0 bridge), 6 personas (3 high / 3 medium), arms-length-neutral governance, refined POV (re-id-resistance + pseudonymization-integrity + multilingual breadth, one CC0 artifact). Methodology: 3 POV critics + 6 persona researchers + 3 market analysts (2026 competitors verified live) + 5-SME UC panel + 15-member concept-value cohort. **Top Requirements priority: close M6 (turn precomputed annotations into running scorers).** 9 new items (N1–N9) forward-deferred. Ready for Requirements. Run: `/dev-assist-requirements`

### Handoff signal to Design (post-Requirements, 2026-05-28)
> Requirements complete. **28 FRs + 17 NFRs = 45 requirements**. Priority: ~30% MUST / ~55% SHOULD / ~15% COULD. Every FR has boolean-testable Given/When/Then; every NFR quantified or boolean-auditable. 5 quantified NFR thresholds stress-tested (6-persona representative panel): **2 VALIDATED · 2 ACCEPTED-WITH-CAVEATS · 1 PERSONA-STRATIFIED · 0 DIVERGED**. All `provisional_status: AGENT_SIMULATED` (FR-015/016/027 PERSONA-CONDITIONAL) pending real-user Pass-2. **Top Design inputs:** (1) the scorer architecture closing M6 [the central new component]; (2) de-circularized RRS; (3) pseudonymization-integrity engine; (4) statistical-power layer; (5) **v2.0.0 schema + migration**; (6) HF/Croissant/leaderboard + governance; (7) pytest+CI baseline. Methodology: representative-scale cohorts (R3 from §5; R6 n=12; R10 6-persona) per single-session limit — documented in `methodology.md`. Ready for Design. Run: `/dev-assist-design`

### Handoff signal to Development (post-Design, 2026-05-28)
> Design complete. Hybrid: **Modular system + Hexagonal scoring core (Clean inside stats) + Linear-batch data-prep + Minimalist-CLI/Info-Dense-reports**. **15 DCs** locked (DC↔FR traced, 0 orphan); 3 audits pass (persona-service, axiom-saturation, requirements-to-design). A 3-SME heuristic panel caught **1 CATASTROPHIC + 9 MAJOR** (incl. real bugs in `evaluate.py` CI math + `export_parquet.py` regime-flattening + package-rename break) — all resolved into 11 locked design revisions. Target `src/pii_anon[_datasets]/` layout + `v1_3_0_to_v2_0_0.py` migration. **Build sequence:** (1) pytest+CI baseline [DC-15] + scoring core/IO-contract/Presidio adapter [DC-04] → (2) v2.0.0 schema+migration [DC-02, tag v1.3.0 first] → (3) scorers detection→anon→pseudo→RRS → (4) stats/reporting → (5) compliance+distribution → (6) leaderboard/governance → (7) extension seams. **⚠ Development writes/modifies REAL production code + migrates the 159,891-record corpus to v2.0.0 — the first repo-mutating stage (CHECKPOINT 5).** Ready for Development. Run: `/dev-assist-development`

## Pivots Log

| Date | Stage(s) affected | Source finding | Plan file |
|---|---|---|---|
| _(empty)_ | | | |

## Directory Structure

```
dev-assist-artifacts/
├── MANIFEST.md                           ← this file (status tracker)
├── 00-axioms/                            ← project-axioms.yaml (no-real-PII, determinism, statistical-power)
├── 00-security/                          ← security-checklist + exceptions (no-real-PII invariant)
├── 00-brownfield-assessment/             ← Stage 0 gap analysis (created by /dev-assist-assess)
├── 01-discovery/                         ← Stage 1 outputs
├── 02-requirements/                      ← Stage 2 outputs
├── 03-design/                            ← Stage 3 outputs
├── 04-development/                       ← Stage 4 outputs
└── 05-testing/                           ← Stage 5 outputs
```

Sibling files:
- `developer-assistant.yaml` — plugin configuration.

## Agent Deployment Ledger

| Stage | Agents deployed | Running total |
|---|---|---|
| Discovery | 32 | 32 |
| Requirements | 18 | 50 |
| Design | 3 | 53 |
| Development | 91 (S3: 58 · S4: 33 — 5 executors + 25 story-gate + 3 sprint-gate reviewers) | 144 |
| Testing | 0 | 144 |
| **Total** | **144** | **144** |

---

# Capability 2 — Powered Assessment Workflow (CAP-02)

> **Second PDLC cycle (new capability)** tracked in this single canonical MANIFEST per the user's structural
> decision (2026-06-01). Cycle-1 — the v2.0.0 dataset PDLC, **all sections above** — is **sealed and untouched**.
> Capability-2 artifacts live under `dev-assist-artifacts/assessment-workflow/`. IDs continue **globally**
> (UC-16+ / FR-030+ / NFR-019+ / DC-16+ / sprints S8+ / signoffs SO-07+; never renumber/reuse). Axioms
> AX-pii-anon-001..004 are **inherited**; AX-pii-anon-005 (pre-registered, reproducible assessment) added in
> Requirements if confirmed.
>
> **Capability:** an academically-sound, repeatable, reportable assessment workflow that runs the existing
> `pii-rate-elo` tournament against PII-Anon **v2.0.0** over a **powered representative sample (default)** /
> **full corpus (opt-in)** / **smoke (fast)** — with observability + reporting integrated at **every** stage.
> **Architecture (locked):** eval-data OWNS sampling + observability + reporting; `pii-rate-elo` CONSUMES.

## CAP-02 Stage Status
| Stage | Status | Started | Completed |
|-------|--------|---------|-----------|
| 01-Discovery | COMPLETE | 2026-06-01 | 2026-06-01 (8 UCs UC-16..23; 3 CAT+15 MAJ resolved; concept validated-with-caveats) |
| 02-Requirements | COMPLETE | 2026-06-01 | 2026-06-01 (62 reqs: 25 FR + 37 NFR; AX-005 CONFIRMED; 0 orphans; R10 1 tightened) |
| 03-Design | COMPLETE | 2026-06-01 | 2026-06-01 (16 DCs DC-16..31; 5-diamond; 3 audits PASS; 11 MAJOR SME resolved) |
| 04-Development | COMPLETE | 2026-06-01 | 2026-06-01 (S8-S12; sampler+manifest+audited-report+ENTRY-A/B; real-data E2E proven; both suites green) |
| 05-Testing | COMPLETE | 2026-06-01 | 2026-06-01 **RE-RULED** (SHIP-WITH-CAVEATS; **24 NFR PASS / 0 PARTIAL / 0 DEFERRED / 0 FAIL**; caveats minimized to synthetic-only AX-001 + pending-external; INDICATIVE→**real-systems** (E1); full-corpus census (E2); SO-12) |

## CAP-02 Project Metadata
| Field | Value |
|---|---|
| Capability ID | CAP-02 |
| Capability name | Powered Assessment Workflow |
| Started | 2026-06-01 |
| Artifact root | `dev-assist-artifacts/assessment-workflow/` |
| ID offsets | UC-16+ · FR-030+ · NFR-019+ · DC-16+ · S8+ · SO-07+ |
| Run depth | representative-scale (documented single-session limits) |
| Consumes (sister repo) | `pii-rate-elo-pipeline` @ `feat/elo-paper-slate-v2` (separate git repo) |
| Code lands in | eval-data `src/pii_anon_datasets/assessment/` + pii-rate-elo `configs/` `cli.py` `schema.py` converter |

## CAP-02 Discovery Phase Progress
| Section | Status | Artifact | Approved? |
|---------|--------|----------|-----------|
| 0. POV Stress Test | VALIDATED | `assessment-workflow/01-discovery/00-pov-stress-test.md` | ✅ 2026-06-01 (3 critics → REFINE; refined POV adopted) |
| 1. Motivation & Background | VALIDATED | `…/01-motivation-background.md` | ✅ 2026-06-01 (3 code-verified drift defects) |
| 2. Personas & Workflows | VALIDATED | `…/personas.md`, `workflow-maps.md` | ✅ 2026-06-01 (6 personas 3H/3M; +2 folded sub-archetypes) |
| 3. Market Research | VALIDATED | `…/03-market-research.md` | ✅ 2026-06-01 (Pugh: CAP-02 4.84 vs HELM 2.96 / full-as-is 2.45) |
| 4. Use Cases (UC-16+) | VALIDATED | `…/04-use-cases.md`, `08-use-case-review-synthesis.md` | ✅ 2026-06-01 (UC-16..23; 5-SME panel; 3 CAT+15 MAJ resolved) |
| 5. Concept Value Study | VALIDATED | `…/06-concept-value-study-synthesis.md` | ✅ 2026-06-01 (n=5/6; median 7/10; DPO lens un-sampled→Pass-2) |
| 6. Discovery Report | VALIDATED | `…/discovery-report.md` | ✅ 2026-06-01 (canonical; handoff signal ready) |

## CAP-02 Requirements Phase Progress
| Phase | Status | Artifact | Notes |
|-------|--------|----------|-------|
| R0. UC↔PGO Bridge | VALIDATED | `02-requirements/_bridge/uc-pgo-map.md` | ✅ 0% true orphan (22 PGO triples; 3 re-id MUST-PGOs scoped-out w/ roadmap hooks) |
| R1–R4. FR/NFR (low→high) | VALIDATED | `functional-requirements.md`, `non-functional-requirements.md` | ✅ 25 FR (FR-030..054) + 37 NFR (NFR-019..055) |
| R2–R3. Interviews | VALIDATED | `interview-guide.md`, `interview-synthesis.md` | ✅ 6 simulated interviewees |
| R5–R7. Prioritization | VALIDATED | `survey-instrument.md`, `survey-analysis.md`, `prioritization-decisions.md` | ✅ 6 respondents; 48 MUST / 12 SHOULD / 2 COULD |
| R8. Canonical | VALIDATED | `requirements-document.md`, `traceability-matrix.md`, `methodology.md` | ✅ 0 orphans (0/8 UC, 0/25 FR, 0/37 NFR); AX-001..005 wired |
| R9. Strengthen | VALIDATED | `audit-report.md` | ✅ verification criteria hardened in place |
| R10. Threshold Validation | VALIDATED | `_threshold-validation/findings-summary.md` | ✅ NFR-038 + NFR-035 ACCEPTED; NFR-023 DIVERGED→tightened (small_n_cutoff 30→15) |

**AX-pii-anon-005 (pre-registered/reproducible assessment, 6-element bar) — CONFIRMED at R7; added to `00-axioms/project-axioms.yaml`.**

## CAP-02 Design Phase Progress
| Diamond | Status | Outcome |
|---------|--------|---------|
| D1 Design Cases | VALIDATED | 16 DCs (DC-16..31); Frame C (Workflow-arc-led) — one DC per spine stage + observability + governance + release |
| D2 Workflow | VALIDATED | Linear-batch-pipeline (datum); fail-closed gates as named predicates; NO resume engine (recovery = byte-identical re-run) |
| D3 UI | VALIDATED | Minimalist-CLI + Info-Dense reports; 2 CLIs (sampler ENTRY-A + assessment ENTRY-B); a11y N/A |
| D4 System | VALIDATED | Modular; **L4 RESOLVED** (fix pii-rate-elo bundled parser; reserve load_dataset for sampler side); one-way dep |
| D5 Architecture | VALIDATED | Hexagonal (Clean inside `stats`); §9 static-AST import-gate makes significance.py unreachable (P1) |
| D6 Synthesis | VALIDATED | implementation-ready design + 3 audits PASS (0-orphan traceability / axiom-saturation / persona-service) + 5-SME panel (11 MAJOR resolved); build sequence S8-S12 |

**Key design decisions:** L4 = fix bundled parser (load_dataset has no version arg); P1 = two-predicate static-AST import-gate + run_significance_tests:false; sampler = per-cell child RNG `random.Random((seed,cell_id))` (Algorithm-R order-dependence); Holm WITHIN (metric,scoring-family) partition; full-corpus = descriptive-census (no-CI default); `stats/multitest.py` Holm is net-new. **UT-1 corrected:** pii-rate-elo IS populated locally (verified firsthand; 253 tests green) — the design's "biggest risk" is moot.

## CAP-02 Development Phase Progress (S8–S12, strict TDD RED→GREEN, 2 repos)
| Sprint | Status | DCs | Deliverables | Gates |
|--------|--------|-----|--------------|-------|
| S8 Preconditions (seam + P1) | COMPLETE | DC-16, DC-22(gate) | `stats/multitest.py` Holm (net-new, 13 tests); v2.0.0 seam fix + 5-tuple contract; `configs/assessment.yaml` (run_significance_tests:false + run-type enum); P1 fabrication-lint + one-way-import guard + `assessment/` pkg skeleton | RED→GREEN both repos; eval-data 357/6, pii-rate-elo 263/2; ruff clean; lattice --check 730 green; 0 regressions. **Full static-AST entrypoint closure deferred → S10** |
| S9 Sampler + manifest | COMPLETE | DC-17/18/19 | `assessment/{sample,verdicts,manifest}.py` (§7 powered draw; per-cell **string-seeded** RNG; 4-state power vs realized positives; manifest DTO + byte-repro) + ENTRY-A CLI | eval-data 374/6; ruff; 17 tests incl cross-process byte-repro; lattice green |
| S10 Run path + audited stats | COMPLETE | DC-21/22/23/25 | `report.py` (audited Wilson/CP CIs + adjacent-pair McNemar + Holm + paired-bootstrap Δ + tie-gating + honest verdicts); `runrecord.py`; `prereg.py`; ENTRY-B `assessment_runner` + `pii-rate-elo assessment` CLI; **P1 full closure** (lazy significance + closure tests) | eval-data 394/6; pii-rate-elo 268/1; real-data E2E proven |
| S11 Report + honesty + pre-reg | COMPLETE (figures/DC-29 governance → roadmap) | DC-24/26/28 | leaderboard.{json,md} + honest-verdict bundle + non-strippable caveat + self-verifying header + pre-registration (plan-hash, recomputed-verify). Figures (lazy matplotlib, env-absent) + governance block = honest roadmap | E2E byte-repro green |
| S12 E2E + one-command | COMPLETE (run-type-enforce/DC-30 crosswalk/DC-31 DOI → roadmap) | DC-20 / (30·31 roadmap) | **one-command example** (`scripts/run_powered_assessment.sh` + ONE-COMMAND-EXAMPLE.md) proven on REAL v2.0.0 (test_technology: 1822-rec powered sample, 15,569 positives, paired-significant leaderboard, SMALL verdict + 122 named shortfalls). run-type plumbed; rigor-bar enforcement + crosswalk + DOI = roadmap | real E2E ~20s; both suites green |

**Development executed MAIN-THREAD-LED strict TDD (RED→GREEN per unit, local commits in both repos) for reliable cross-repo access + real gate verification.** Roadmap (honest, cycle-1 seam+roadmap pattern): figures (lazy matplotlib, absent in agent-env), run-type rigor-bar enforcement (smoke CI-suppression), DC-29 governance block, DC-30 regulatory crosswalk, DC-31 DOI release, real-detector systems (INDICATIVE → Pass-2), real-data correlation slice (cycle-1 UC-13 → Pass-2).

## CAP-02 Testing Phase Progress
**Stage 5 verdict: SHIP-WITH-CAVEATS — RE-RULED 2026-06-01** (caveats minimized; `assessment-workflow/05-testing/release-readiness-report.md` + `HUMAN-ONLY-TODO.md`).
| Section | Status | Notes |
|---|---|---|
| Test architecture | COMPLETE | TDD per-story in Stage 4 + close-out; pyramid = unit (stats / sampler / verdicts / report / observability / governance / tracks / operating-point / honesty) + integration (cross-repo E2E + real-systems) |
| NFR verification matrix (NFR-019..055) | COMPLETE | **RE-RULED: 24 PASS (+1 inherited) / 0 PARTIAL / 0 DEFERRED / 0 FAIL** (was 18/4/2/0; the 4 PARTIAL + 2 DEFERRED closed by C2/C3/C4/C7/C8) |
| a11y | N/A | library + 2 CLIs (no web UI) |
| Real-systems E2E | **PROVEN (real detectors)** | E1: Presidio/GLiNER/Piiranha on 1822-rec powered sample · 15,569 positives · presidio 0.616 [0.608,0.624] > gliner 0.558 > piiranha 0.285 · Holm-significant paired McNemar (χ²-continuity) · prereg verified. INDICATIVE→real-systems. `runs/real-systems-powered/` |
| Full-corpus census | **PROVEN** | E2: 575,604 records / 2,486,438 positives · descriptive-census · CI+p-values SUPPRESSED at full scale (NFR-025) · LARGE. `runs/full-corpus-census-synthetic/` |
| Guardrails (final sweep) | GREEN | eval-data **502/7** · pii-rate-elo **296/1** · **mypy 0 issues** · ruff · lattice 730@47c3a8f · doc-drift 0 · **NFR-018 power gate PASS (575,604, 0 errors)** · corpus/lattice/tags git-verified untouched |
| Caveats (minimized + classified) | — | 🔒 synthetic-only AX-001 (permanent) · ⏳ FR-027 / NFR-010b / real-user / real-CI / DOI (pending-external; seams + commands shipped) · ✅ C1-C13 + McNemar fix (closed) |
| Wave-7 adversarial review | CLEAN | honesty CLEAN · AX-004 no-collapse · traceability strong (MAJOR/MINOR/OBS all resolved) |
| Release readiness | COMPLETE | **SHIP-WITH-CAVEATS (re-ruled; minimized)** (`05-testing/release-readiness-report.md`) |

## CAP-02 Sign-offs
| Sign-off ID | Date | Type | Scope | Signer | File |
|---|---|---|---|---|---|
| SO-07-cap02-discovery | 2026-06-01 | stage-close | CAP-02 Discovery — 8 UCs (UC-16..23); 3 CAT+15 MAJ resolved; concept validated-with-caveats; 3 hard preconditions identified (audited-stats run path · seam reconcile · powered sampler) | AGENT_SIMULATED | `assessment-workflow/_signoffs/SO-07-cap02-discovery.yaml` |
| SO-08-cap02-requirements | 2026-06-01 | stage-close | CAP-02 Requirements — 62 reqs (25 FR-030..054 + 37 NFR-019..055); AX-005 CONFIRMED + registered; 0 orphans; R10 NFR-023 tightened (small_n_cutoff 30→15) | AGENT_SIMULATED | `assessment-workflow/_signoffs/SO-08-cap02-requirements.yaml` |
| SO-09-cap02-design | 2026-06-01 | stage-close | CAP-02 Design — 16 DCs (DC-16..31); 5-diamond cascade + synthesis; 3 audits PASS (0-orphan); 5-SME (11 MAJOR resolved); build seq S8-S12; L4/P1 resolved; UT-1 corrected (pii-rate-elo populated+green) | AGENT_SIMULATED | `assessment-workflow/_signoffs/SO-09-cap02-design.yaml` |
| SO-10-cap02-development | 2026-06-01 | stage-close | CAP-02 Development (S8-S12, main-thread strict TDD, 2 repos). Sampler+manifest+4-state verdicts+Holm+v2.0.0 seam fix+P1 quarantine+audited report+ENTRY-A/B CLIs. Real-data E2E proven (test_technology: 1822-rec powered sample, 15,569 positives, paired-significant). eval-data 394/6 · pii-rate-elo 268/1 · ruff clean · guardrails green. Roadmap: figures/run-type-enforce/crosswalk/DOI/governance/real-detectors(INDICATIVE→Pass-2) | AGENT_SIMULATED | `assessment-workflow/_signoffs/SO-10-cap02-development.yaml` |
| SO-11-cap02-testing | 2026-06-01 | stage-close | CAP-02 Testing — **SHIP-WITH-CAVEATS**. NFR-019..055 matrix: 18 PASS (+1 inherited) / 4 PARTIAL / 2 roadmap / 0 FAIL. Final guardrail sweep green incl. **NFR-018 power gate PASS on 575,604 records**. Caveats: INDICATIVE synthetic systems (real detectors Pass-2), real-data correlation slice (Pass-2), named roadmap (figures/run-type-enforce/governance/operating-point/crosswalk/DOI). **CAP-02 capability COMPLETE through Stage 5.** | AGENT_SIMULATED | `assessment-workflow/_signoffs/SO-11-cap02-testing.yaml` |
| **SO-12-cap02-rerule** | 2026-06-01 | **stage-rerule** | v2-scoring-harness close-out re-rule (both cycles). Closed every code-achievable caveat (C1-C13 + McNemar-overflow fix, strict TDD, both repos); NFR matrix re-ruled **24 PASS / 0 PARTIAL / 0 DEFERRED / 0 FAIL**. **INDICATIVE→real-systems** (E1: real Presidio/GLiNER/Piiranha, 15,569 positives, Holm-significant) + **full-corpus census** (E2: 575,604 records, CI-suppressed). Wave-7 honesty review CLEAN. Caveats minimized + classified (🔒 synthetic-only AX-001 permanent · ⏳ FR-027/NFR-010b/real-user/real-CI/DOI pending-external). eval-data 502/7 · pii-rate-elo 296/1 · mypy 0 · guardrails git-verified. | AGENT_SIMULATED | `assessment-workflow/_signoffs/SO-12-cap02-rerule.yaml` |

## CAP-02 Agent Deployment Ledger
| Stage | Agents deployed | Running total |
|---|---|---|
| Discovery | 30 (3 POV + 5 persona + 3 market + 4 writers + 1 UC + 5 SME + 6 CVS + 3 synth) | 30 |
| Requirements | 28 (1 bridge + 1 guide + 6 interviewees + 1 iv-synth + 2 FR/NFR + 1 survey + 6 respondents + 1 prio + 1 canon + 1 audit + 6 threshold + 1 tv-synth) | 58 |
| Design | 27 (15 diamond frame-explorers + 5 Pugh/writers + 1 synthesis + 5 SME + 1 SME-apply) | 85 |
| Development | 0 (MAIN-THREAD-LED strict TDD across 2 repos; ~30 RED/GREEN commits) | 85 |

---

_Scaffolded by developer-assistant `/dev-assist-start` (adapted for a benchmark-dataset brownfield project)._
_Capability 2 (CAP-02) scaffolded 2026-06-01 as a second PDLC cycle in the same canonical MANIFEST._
