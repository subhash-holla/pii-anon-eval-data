# CAP-02 — D6 SYNTHESIS: Implementation-Ready Design (Powered Assessment Workflow)

**Capability**: CAP-02 — an academically-sound, repeatable, reportable assessment **workflow** that runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 / CC0 / `annotations`** over a **powered-representative lattice-stratified sample (CLI default)** / **full corpus (opt-in, citable)** / **smoke (fast CI)**, with statistical/epistemic observability + reporting at every spine stage `load → sample → run → score → rate → report`.
**Stage**: assessment-workflow / 03-Design · **Diamond 6 (Synthesis) — the implementation-ready design**
**Date**: 2026-06-01
**provisional_status**: AGENT_SIMULATED — the persona/PGO/UC/interview chain this design serves is agent-simulated single-session research; the **code / version / line / API evidence is direct file-read at HEAD on 2026-06-01** (eval-data side firsthand and re-verified this session — see §0.1; the `pii-rate-elo` side carried from Discovery file-reads because **that repo is not populated on this machine** — re-confirm every cited line before editing). One high-stakes commitment is flagged for Pass-2: **non-interactive batch with no per-stage consent** (the single human decision — preset + run-type — is upfront; SP-W4/SP-U6).

> **Vocabulary remap.** DC = **Benchmark Component**; FR = Assessment Capability; UC = Evaluation Scenario; NFR = Quality Attribute; AX = binding axiom; PGO = Benchmark Goal; Persona = assessment consumer.

> **ID discipline (load-bearing).** Cycle-1 ended at **DC-15** (verified: `03-design/06-synthesis/D-implementation-ready-design.md` ends at DC-15). CAP-02 DCs are **DC-16 … DC-31**, global numbering continued, **never renumbered or reused**. UC-16…23 / FR-030…054 / NFR-019…055 / AX-pii-anon-001…005 are the cycle-2 ranges.

> **Locked architecture (every diamond honored; this synthesis ratifies).** eval-data **OWNS** sampling + observability + reporting; `pii-rate-elo` **CONSUMES** (extend, do **NOT** rebuild the engine / metrics / convergence). The **sample-manifest is the L1 SEAM** (the sole cross-process data coupling). Two CLI entrypoints (L3). Cycle-1 hybrid held: **Modular system (D4) + Hexagonal scoring core with Clean inside `stats` (D5) + Linear-batch data-prep (D2) + Minimalist-CLI / Info-Dense-reports (D3)**; a11y **N/A** (library + two CLIs, no web UI).

> **D6 SME panel absorbed (2026-06-01).** This design has been revised in place against the 5-SME heuristic panel (Nielsen usability / statistical-methodology rigor / reproducibility-provenance / architecture-testability / scientific-reporting-integrity; consolidated in `06-synthesis/sme-heuristic-findings.md`). **All 11 MAJOR findings are resolved here** (inline-tagged at each edit site): the sampler's shared-RNG determinism hole → **per-cell child `random.Random((seed, cell_id))`** + full-closure fingerprint (repro-01/02, §7/§2.3); Holm multiplicity → **within (metric, scoring-family) partition, family-size from the confirmatory set** (stat-01/integrity-MINOR-4, §8/§6/§4); **adjacent-pair paired-Δ as the rank oracle, marginal CIs descriptive-only** (stat-02, §6/§8); **power_class scoped to recall@p_ref, others NOT_ASSESSED** (stat-03, §7/§2.3/§6); **full-corpus census = no-CI by default via `inferential_target`** (FR-036/integrity-MAJOR-1, §3/§4/§6); **verdict token bound to the synthetic-only/sample-scope caveat** (integrity-MAJOR-2, §6/§2.3); **named fatal-exit messages** on every gate (nielsen-01, §7/§9/§10); **ENTRY-B fail-closed manifest↔corpus precondition** (nielsen-02, §2.3/§9); **static-AST import-closure** (arch-01, §9); and the **runner→report `OutcomeDTO` seam + contract test** (arch-02, §2.1/§2.4). Two of these (Holm family; descriptive-census CIs) re-anchor the design to requirements it had drifted from (NFR-027, FR-036). MINOR/SUGGESTION items are folded into the adjacent payloads; PRAISE controls (significance-quarantine, audited LOCAL-RNG bootstrap, non-strippable caveat, single all-edges import gate) are protected from regression.

---

## 0. The five preferred diamonds, integrated

| Diamond | Preferred | One-line carry-forward into this design |
|---|---|---|
| **D1 Design Cases** | **Frame C (Workflow-arc-led), +0.85** — enriched with A's axiom-narration + B's persona-ownership | **16 DCs (DC-16…31)** = one per spine stage + observability + governance + release X-stage artifacts; the partition *is* the spine and *is* the L6 module map. |
| **D2 Workflow** | **Frame A (Linear-batch-pipeline), datum** — enriched with B's gate-as-named-predicate + honest-halt/re-run | A **fail-closed linear batch** across the two-CLI manifest seam; gates = named predicates over the run-record evaluated inline; **no resume engine** (recovery = byte-identical re-run, NFR-030); **no per-stage consent**. |
| **D3 UI** | **Frame A (Minimalist-CLI + Info-Dense-Reports), datum (A 0.00 / B +0.08 / C −0.40)** — enriched with B's dense-per-cell content + machine-stdout discipline | **Two terse CLIs** (one upfront decision: preset + run-type) + an **Info-Dense LaTeX/CSV deliverable**; PowerMatrix verdict banner (never silently LARGE); `FAIL`/`FLAG`/`OK` gate vocabulary; stdout = manifest path only on ENTRY-A. |
| **D4 System** | **Frame B (Modular), datum (B 0.00 / A −0.12 / C −0.34)** — enriched with A's in-process grain + static-import-gate; C's immutability discipline | **In-process modules in one shared venv**, one-way import (`pii-rate-elo → pii_anon_datasets.{assessment,stats}`); **L4 RESOLVED = FIX the bundled parser** + 5-tuple regression contract; write-once content-hashed JSON (not event sourcing); Holm = net-new audited `stats/` primitive. |
| **D5 Architecture** | **Frame A (Hexagonal, Ports & Adapters), datum (A 0.00 / B 0.00 / C −0.02)** — B absorbed as the pure `stats/` Clean inner ring; C's authority-by-placement carried as SP-A2 | **Domain hexagon + 5 ports** + manifest DTO + constructor-wired composition root; the **import-boundary rule (§9)** makes the fabricated `analysis.significance` **module** unreachable from both assessment entrypoints (canonical NFR-019 gate, module-level). |

### 0.1 Firsthand verification ledger (eval-data side, re-confirmed THIS session 2026-06-01)

All reuse APIs the diamonds compose were re-read at HEAD this session and **confirmed present** (paths are real; the diamonds occasionally wrote `scripts/X` — the scripts live at the **repo-root `scripts/`**, not under `src/` — corrected throughout this design):

- `src/pii_anon_datasets/__init__.py:55` — `load_dataset(*, subset, domain, split, language, dimension)` (**no `version` arg** — the load-bearing fact behind the L4 decision). ✔
- `src/pii_anon_datasets/stats/power.py` — `Tier`:54, `PowerClass`:60 (WELL/UNDER/EMPTY, 3-state today), `required_n`:67, `TIER_SPECS`:95 (→ 1522/753/200), `REID_TIER_SPECS`:152 (897/385 *pairs*, out-of-scope), `classify`:235, `CellAudit`:289, `PowerMatrix`:320, `PowerMatrix.verdict()`:351 (**LARGE iff frac≥0.999, ADEQUATE iff ≥0.80, else SMALL** — body read this session), `audit_crossing`:428. ✔
- `src/pii_anon_datasets/stats/intervals.py` — `_require_int_counts`:39, `wilson_interval`:65, `clopper_pearson_interval`:170 (integer-guarded). ✔
- `src/pii_anon_datasets/stats/paired.py` — `mcnemar_exact`:62, `mcnemar_chi2(...,continuity=True)`:82, `paired_bootstrap_recall_delta`:112 with **LOCAL `random.Random(seed)`:140**. ✔
- **Holm–Bonferroni / `multitest` is ABSENT** from `src/pii_anon_datasets/stats/*` (grep returned zero hits this session) → it is the **one net-new audited primitive** (SP-S4). ✔
- `scripts/lattice_audit.py` — `committed_index`:31, `record_increments`:68, `audit_positives`:83, `deficits`:103 (streaming single-pass realized positives). ✔
- `scripts/benchmark_throughput.py` — `SEED_BENCHMARK=20260531`:63, **`RUNRECORD_SCHEMA="pii-anon-nfr010-runrecord/v1"`:65**, `HARNESS_VERSION="1.0.0"`:66, `reservoir_sample`:92 (Algorithm-R — **order-dependent: deterministic only for ONE iterable + ONE RNG in fixed order; this is the load-bearing fact behind the repro-01 per-cell-child-RNG requirement in §7**), `host_spec()`:311 (**always `is_reference_host=False`**), `build_run_record(..., timestamp=None)`:359 (**injectable timestamp**), and the **`provenance` block** `{is_reference_host, environment, canonical_verdict, reason}`:418. This is the exact L5 RUNRECORD pattern to reuse. ✔
- `scripts/write_manifest.py` — `_sha256`:26, `compute_manifest`:48, `--check` exit-1-on-drift (stdlib `hashlib`, no heavy deps). ✔
- `scripts/_version.py` — `get_version()`:8, `DATASET_VERSION`:17. ✔
- `scripts/validate.py` — `--lattice` (`DEFAULT_LATTICE`:41) + `check_committed_cell_power`:44 streams via `lattice_audit`, `--no-power-gate` exists (the gate it must keep ON), `sys.exit(1)`:204. ✔
- `src/pii_anon_datasets/scoring/detection.py` — `DESIGN_CAVEAT`:17, `DesignProvenance`:30 with `__post_init__`:44 **raising on empty caveat**:46. ✔
- `src/pii_anon_datasets/subsets/slices.py` — `SLICE_CAVEAT`:25, `Slice.__post_init__`:40 **raising on empty caveat**:42. ✔
- `python -m pii_anon_datasets.stats.lattice --check` → **"OK … 730 cells"**, exit 0, run THIS session (NFR-052 green). ✔

**`pii-rate-elo` side — NOT firsthand.** The repo at `pii-anon-research-paper/pii-rate-elo-pipeline/` contains **zero `.py` files on this machine** (confirmed this session). Every cited consumer line (`significance.py:90`/`:409`, `cli.py:33`/`:240`/`:242`, `pii_anon_eval.py:93`/`:221`/`:222`/`:82`, `schema.py:137`/`:349`/`:583`/`:627`, `engine.py`/`convergence.py`/`metrics_bridge.py`) is carried from Discovery and **MUST be re-confirmed against a checkout before S8 edits** (S8 begins with that re-verification; this is the single biggest implementation risk and is tracked in §15 Unresolved Tensions UT-1).

---

## 1. The locked Design-Case set (DC-16 … DC-31)

16 Benchmark Components, one per spine stage plus the two cross-cutting spines (observability, governance) and the release/crosswalk X-stage artifacts. Each row = **DC → bundled FR/NFR → spine stage → reused modules → owning persona-tier → axioms saturated → R7 priority → the module/port that builds it (D4/D5)**.

### LOAD

**DC-16 — Dataset-seam reconciliation + regression contract (v2.0.0)** [P2]
- **FR:** FR-030, FR-031 · **NFR:** NFR-040, NFR-041, NFR-054 · **Spine:** LOAD · **Precondition:** P2 (CATASTROPHIC-as-wired).
- **Owner persona:** P-tool-builder (T1). **Axioms:** correctness precondition (enables AX-002/003/004 downstream). **Priority:** MUST.
- **Builds:** pii-rate-elo `datasets/converters/pii_anon_eval.py` + `schema.py` v2.0.0 metadata pins + the **5-tuple regression contract**; eval-data side reuses `scripts/_version.py`, `scripts/write_manifest.py` hashing, `tests/test_doc_drift.py` canonical pins, `taxonomy.ENTITY_TYPE_COUNT` (=63 derived). **Port:** `CorpusReader` ← `JsonlCorpusAdapter` (the fixed bundled parser). **L4 RESOLVED (D4 §4): FIX the bundled parser; reserve `load_dataset` for the eval-data sampler side.**

### SAMPLE

**DC-17 — Powered, lattice-stratified, seeded sampler** [P3]
- **FR:** FR-032 · **NFR:** NFR-035, NFR-038, NFR-039, NFR-053 · **Spine:** SAMPLE.
- **Owner:** P-mlnlp-researcher (T1); P-acad-deid (T1); P-priveng (T2). **Axioms:** AX-002 (seeded/single-pass deterministic), AX-003 (tiered targets derived). **Priority:** MUST.
- **Builds:** `assessment/sample.py`. **Reuses:** `stats/power.py` (`required_n`, `TIER_SPECS`, `classify`, `pick_tier`, `Tier`), `stats/lattice.py` (`build_committed_lattice`/`load_lattice`, `--check` 730@`47c3a8f`), `scripts/lattice_audit.py` (`committed_index`/`audit_positives`/`deficits`), `subsets/slices.py`, `scripts/benchmark_throughput.py::reservoir_sample` (Algorithm-R, `SEED_BENCHMARK`). **Pure domain logic — no port** (sampling is not swappable infrastructure, SP-A4). **Determinism contract (repro-01/02):** a **per-cell child RNG `random.Random((seed, cell_id))`** (never one shared RNG fanned across cells — Algorithm-R is order-dependent); the byte-repro guarantee is **conditional on pinned {corpus content_hash, lattice_version, seed}**; `repro.sampler_version` fingerprints the FULL §7 closure (incl. `lattice_audit` + `reservoir_sample`) and `repro.ut5_integers` is frozen into the hashed payload.

**DC-18 — PowerMatrix verdict + per-cell realized-positive shortfall** [P3]
- **FR:** FR-033 · **NFR:** NFR-035, NFR-036, NFR-037 · **Spine:** SAMPLE.
- **Owner:** P-mlnlp-researcher (T1); P-acad-deid (T1). **Axioms:** AX-003. **Priority:** MUST.
- **Builds:** `assessment/verdicts.py` (power-class derivation) feeding `assessment/sample.py`. **Reuses:** `stats/power.py::PowerMatrix.verdict()` (SMALL/ADEQUATE/LARGE @ 0.80/0.999), `CellAudit`, `classify`. **The 4-state extension** (`UNDER_SAMPLED` vs `CORPUS_LIMITED`) compares sample realized `n` to **full-corpus** realized positives via `lattice_audit.audit_positives` — `classify` is 3-state today; the 4th state is derived in `verdicts.py`, NOT by mutating `power.py` (keeps the audited core unchanged). **Power-operating-point scope (stat-03):** every `power_class` records `power_operating_point = recall@p_ref` and applies to **recall only**; precision/Fβ/AUPRC/pseudo-re-id are `NOT_ASSESSED` unless re-sized by a matching ladder — the recall verdict is never reused as their label. **Verdict-token caveat (integrity-MAJOR-2):** `verdicts.py` renders the corpus verdict as the non-strippable unit `<verdict> · conditional-on-this-sample · synthetic-only`; a sample run never emits a bare `LARGE` (G3).

**DC-19 — Reproducible sample manifest (the L1 SEAM) + non-strippable caveat** [P3]
- **FR:** FR-034 · **NFR:** NFR-030, NFR-039 · **Spine:** SAMPLE/X · **The L1 SEAM.**
- **Owner:** P-acad-deid (T1, byte-for-byte reproducibility). **Axioms:** AX-002 (canonical-form-equal re-run), AX-001 (non-strippable synthetic-only caveat). **Priority:** MUST.
- **Builds:** `assessment/manifest.py`. **Reuses:** `scripts/write_manifest.py` (deterministic sha256, canonical form), `subsets/slices.py::SLICE_CAVEAT` + `Slice.__post_init__` (raise-on-empty → non-strippable), `scoring/detection.py::DesignProvenance`. **The manifest is a serialized JSON DTO, not a Protocol** (D5 SP-A4).

### SAMPLE / RUN

**DC-20 — Preset trio + run-type → rigor-bar profile** [the L3 surface]
- **FR:** FR-035, FR-036, FR-037, FR-038 · **NFR:** NFR-025, NFR-033, NFR-034 · **Spine:** SAMPLE/RUN.
- **Owner:** P-acad-deid (T1, full-corpus citable) + P-tool-builder (T1, smoke); P-mlnlp-researcher (T1, default). **Axioms:** AX-002, AX-005 (enforcement scope via run-type binding). **Priority:** MUST (FR-036/037 SHOULD; the run-type mechanism FR-038 is MUST).
- **Builds:** the two CLIs (ENTRY-A `assessment.sample`; ENTRY-B `pii-rate-elo assessment`) + `configs/assessment.yaml` + the **committed run-type→profile enum** (`smoke`/`dev`/`leaderboard-submission`/`filing-grade` → `{rigor_bar, prereg, sample_mode}` total triple) + **`preset`×`run-type` coherence validation at parse time (nielsen-04)**. **Inferential-target (integrity-MAJOR-1 / FR-036):** `preset=full` ⇒ `inferential_target = descriptive-census` (metrics labelled descriptive, **no CI by default**) unless `--super-population` is set; stamped into manifest + prereg + run-record; the report suppresses the CI column under descriptive-census. **Reuses:** pii-rate-elo `cli.py` (Typer, extend), `config.py::PipelineConfig.from_yaml`; eval-data `benchmark_throughput::build_run_record`; version-pinned `record_count` from DC-16 (FR-036 `records_scored == dataset.record_count(version)`, never literal `575604`).

### RUN / RATE

**DC-21 — Thin assessment orchestrator: engine + Glicko convergence (consume, no rebuild)** [the L2 orchestrator]
- **FR:** FR-039 · **NFR:** NFR-029 (convergence verdict source), NFR-051 · **Spine:** RUN/RATE.
- **Owner:** P-mlnlp-researcher (T1); P-tool-builder (T1); P-acad-deid (T1). **Axioms:** AX-005 (element 3, convergence), AX-002. **Priority:** MUST.
- **Builds:** pii-rate-elo `cli.py assessment` command + the **thin assessment adapter** (`EloEngineAdapter`). **Reuses (consumed, none re-implemented):** `tournament/engine.py::PIIRateEloEngine`, `tournament/convergence.py::ConvergenceChecker` (Glicko RD, default threshold 100), `tournament/organizer.py`, `evaluation/metrics_bridge.py::compute_span_metrics` (declared `span_match_mode ∈ {exact, relaxed-overlap}`), `config.py`, `cli.py`. **Port:** `TournamentRunner` ← `EloEngineAdapter` (the single cross-repo import surface).

**DC-22 — Audited statistics core: CIs + paired tests + Holm (P1 quarantine)** [SHOWSTOPPER, P1]
- **FR:** FR-040, FR-041, FR-042 · **NFR:** NFR-019, NFR-020, NFR-021, NFR-022, NFR-023, NFR-024, NFR-026, NFR-027, NFR-050 · **Spine:** SCORE/RATE · **Precondition:** P1 (one indivisible integrity surface — SP-2; NOT split).
- **Owner:** P-mlnlp-researcher (T1); P-acad-deid (T1); P-tool-builder (T1). **Axioms:** AX-002, AX-003, AX-005 (elements 1, 2). **Priority:** MUST (SHOWSTOPPER).
- **Builds:** `assessment/report.py` (calls the audited stats) + the **net-new `stats/multitest.py` Holm–Bonferroni** primitive (verified absent). **Reuses:** `stats/intervals.py` (`wilson_interval`, `clopper_pearson_interval`, `_require_int_counts`), `stats/paired.py` (`mcnemar_exact`, `mcnemar_chi2`, `paired_bootstrap_recall_delta`). **Multiplicity partition (stat-01 / NFR-027):** Holm is applied **WITHIN each (metric, scoring-family) partition — never pooled across metrics or across anon/pseudo (AX-004)**; confirmatory `family_size = #pairs × #metrics in the confirmatory set` (computed from the structured `inference_families` block, asserted == prereg). **Quarantine target:** pii-rate-elo `analysis/significance.py::SignificanceTester` (fabricated; module-level eager instantiation `:409` per Discovery) → set `run_significance_tests:false` + **static-AST import-graph guard** (§9) + fabrication-regex lint.

### SCORE

**DC-23 — Scoring-family separation (anon/pseudo) + contamination + seed-variance scope**
- **FR:** FR-043 · **NFR:** NFR-045, NFR-048, NFR-055 · **Spine:** SCORE.
- **Owner:** P-mlnlp-researcher (T1); P-tool-builder (T1); P-dpo (T2, separation). **Axioms:** AX-004 (separate families, never merged), AX-005. **Priority:** SHOULD (R7 demotion; **NR-core "four families never merged" stays MUST via NFR-055 / G-norg**; reversible at Pass-2).
- **Builds:** `assessment/report.py` + run-record fields in `assessment/runrecord.py`: `scoring_family ∈ {anonymization, pseudonymization}`, `contamination_status` (+ `contamination-uncontrolled` propagation when `unknown`), `seed_variance_scope` (multi-seed `len(seeds) ≥ MIN_SEEDS=3` + Kendall-τ, or `single-seed` → `rank-volatility: UNMEASURED`). **Reuses:** the four-metric-families-never-merged guardrail (cycle-1 NFR-005, extended by NFR-055 static check).

### X / REPORT (pre-registration)

**DC-24 — Pre-registration: git-anchored + hash-chained**
- **FR:** FR-044 · **NFR:** NFR-031, NFR-032 · **Spine:** X/REPORT (after `sample`, before first score).
- **Owner:** P-acad-deid (T1); P-complreviewer (T3), P-tool-vendor (T3). **Axioms:** AX-002, AX-005 (element 4). **Priority:** MUST (mechanism MUST; enforcement run-type-scoped per DC-20).
- **Builds:** `assessment/prereg.py`. **Reuses:** `scripts/write_manifest.py` hashing; commit-on-remote oracle `git branch -r --contains <sha>` (subprocess). **Port:** `PreregSink` ← `PreregAdapter`. **Immutable payload** pins {version, manifest hash, seed, systems, metrics, RD stopping rule, interval rule, multiplicity family+size, power design point, span-match mode, scoring family, tie/exclusion rules}; + run-lineage count.

### X (observability — all stages)

**DC-25 — Per-stage observability run-records + file-level provenance** [the L5 spine]
- **FR:** FR-045, FR-046 · **NFR:** NFR-042, NFR-043 · **Spine:** X (cross-cuts all 6 stages).
- **Owner:** P-priveng (T2); P-complreviewer (T3, Art-11). **FIRST-CONTACT assurance lens (Pass-2 caveat).** **Axioms:** AX-002, AX-005 (element 4). **Priority:** SHOULD (R7; **the 6-stage provenance floor is the assurance-MUST sub-part**; reversible at Pass-2).
- **Builds:** `assessment/runrecord.py`. **Reuses:** `scripts/benchmark_throughput.py` RUNRECORD pattern (`RUNRECORD_SCHEMA`, `HARNESS_VERSION`, injectable `timestamp`, `seed`, `host_spec()`, `provenance{is_reference_host, environment, canonical_verdict}`) extended per-stage; `scripts/write_manifest.py` per-file sha256. **6 stage records** {load, sample, run, score, rate, report}, shared `run_id`. **Port:** `RunRecordSink` ← `JsonRunRecordAdapter`.

### REPORT

**DC-26 — Honest leaderboard: paired-test-gated ranks + AX-004 separate families + artifact-first register** [the deliverable]
- **FR:** FR-047 · **NFR:** NFR-028, NFR-044 · **Spine:** REPORT.
- **Owner:** P-mlnlp-researcher (T1); P-acad-deid (T1); P-dpo/P-complreviewer (T2/T3). **Axioms:** AX-001, AX-004, AX-005 (element 2). **Priority:** MUST.
- **Builds:** `assessment/report.py` (LaTeX tabular + CSV register; tie-gating from `stats/paired.py` + `stats/multitest.py` Holm; non-significant pairs greyed). **Rank oracle (stat-02):** for every **adjacent rank pair** the report prints the paired **Δ + bootstrap CI + McNemar p** as the rank-governing statistics (NFR-026); per-system marginal Wilson CIs are **descriptive-only** and never decide a tie. **Forbidden product-verdict tokens** `{SHIP-WITH-CAVEATS, SHIP, DEFER, GO/NO-GO}` banned by scan.

**DC-27 — Operating-point reporting (recall-priority Fβ / FN:FP cost + AUPRC)** [false-positive tax]
- **FR:** FR-048 · **NFR:** NFR-046 · **Spine:** REPORT.
- **Owner:** P-priveng (T2); P-dpo (T2). **FIRST-CONTACT P-priv-eng lens; unseated at R6.** **Axioms:** AX-005. **Priority:** COULD-overall / **MUST-for-P-priv-eng** (R7; the bundle most distorted by the sampling gap — **highest-priority Pass-2 re-elicitation**).
- **Builds:** `assessment/report.py` figures via the `FigureRenderer` port. **Reuses:** pii-rate-elo `evaluation/metrics_bridge.py` extended for recall-priority Fβ (β≥2 recorded) / stated integer FN:FP cost + threshold-free AUPRC at the pre-registered operating point + precision-at-fixed-recall. **Port:** `FigureRenderer` ← `MatplotlibFigureAdapter` (the **sole** lazy numpy/matplotlib).

**DC-28 — Non-strippable honesty-flag bundle + RD-convergence + self-verifying report**
- **FR:** FR-049, FR-050 · **NFR:** NFR-029, NFR-047 · **Spine:** REPORT/X (terminal spine DC).
- **Owner:** P-complreviewer (T3) + P-dpo (T2); P-mlnlp-researcher (T1); P-acad-deid (T1). **Axioms:** AX-001, AX-003, AX-005 (elements 3, 4, 5). **Priority:** MUST.
- **Builds:** `assessment/verdicts.py` (honesty-flag derivation) + `assessment/report.py` (self-verifying header). **Reuses:** `scoring/detection.py::DesignProvenance` (carries caveat through serializers); pii-rate-elo `convergence.py` (`is_converged`, `max_rd`, `rd_threshold` → achieved max-RD ± 2RD + rounds; NOT-CONVERGED as blocking flag). **Closed honesty set** (NFR-047): synthetic-only caveat / RD-NOT-CONVERGED / per-cell power_class / contamination-uncontrolled / rank-volatility scope / worst-language recall (argmin+label) / low-resource (<200-positive set) recall / named-and-pending correlation flag; self-verifying header embeds {pre-reg hash, commit SHA, run id} + Art-11 alignment label.

### X (governance / anti-gaming)

**DC-29 — Leaderboard hygiene + neutrality/recusal governance**
- **FR:** FR-051, FR-052 · **NFR:** NFR-048, NFR-049 · **Spine:** X.
- **Owner:** P-tool-vendor (T3, forcing function); P-complreviewer (T3); P-priveng (T2). **Axioms:** AX-005 (element 6). **Priority:** MUST (FR-052 SHOULD).
- **Builds:** `assessment/runrecord.py` (submission-provenance fields) + `assessment/report.py` (governance block per page). **Reuses:** scoring-API-surface oracle (held-out labels never returned); `contamination_status` source (DC-23) with `unknown` rejected + signed held-out-non-exposure attestation `{submitter_id, statement, signature, signed_at}`; computable recusal record.

**DC-30 — Regulatory taxonomy crosswalk (63 types → GDPR / HIPAA / CCPA / GLBA)**
- **FR:** FR-053 · **NFR:** — (AX-004 linkage) · **Spine:** X · Feeds DC-26/28 report.
- **Owner:** P-dpo (T2); P-priveng (T2). **FIRST-CONTACT DPO lens (Pass-2 caveat).** **Axioms:** AX-004 (legally-distinct families). **Priority:** **SHOULD, AUTHOR-not-defer** (R7).
- **Builds:** a versioned, provenance-stamped, updateable crosswalk artifact in `compliance/` (cycle-1 home of regulatory mapping) consumed by `assessment/report.py`; legally distinct per regime at the display layer (no cross-regime equivalence). **Reuses:** the 63-type vocabulary from DC-16 (`taxonomy.ENTITY_TYPE_COUNT`).

**DC-31 — Citable / DOI-able release + claims policy**
- **FR:** FR-054 · **NFR:** — (AX-001/003 linkage) · **Spine:** X (terminal release).
- **Owner:** P-acad-deid (T1 — MUST-for-this-persona); P-tool-vendor (T3). **Axioms:** AX-001 (claims-policy ceiling caveat). **Priority:** **SHOULD, MUST-for-P-acad-deid** (R7).
- **Builds:** a release artifact (Zenodo DOI or equivalent + BibTeX + recommended citation template + synthetic-only claims policy) in `distribution/` (cycle-1 home of release packaging). **Reuses:** `DesignProvenance` ceiling caveat (AX-001/003).

**Coverage self-check (carried verbatim from D1, re-validated): 25/25 FRs · 37/37 NFRs · 8/8 UCs — 0 orphans, both directions.** (Full per-DC bind list in §13.1.)

### 1.1 Cross-cutting CI-gate constraints (the dissolved SP-3 "gate" — NOT a DC)

The no-regression / engineering NFRs are **panel-wide blocking CI gates** every DC's acceptance criteria inherit (resolving D1 SP-3 without minting a non-component DC), attached to their nearest spine DC for ownership:

| Constraint (NFR) | Pins | Nearest-DC owner | Enforced as |
|---|---|---|---|
| **NFR-050** | Pure-stdlib stat cores + lazy heavy-dep guards | DC-22 | import-graph CI gate (cores import no 3rd-party numeric lib; `report.py` figure code is the sole lazy numpy/matplotlib) |
| **NFR-051** | pii-rate-elo gates green (pytest + ruff + mypy) | DC-21 | the three gates in the `pii-rate-elo-pipeline` venv |
| **NFR-052** | Lattice frozen 730 cells @ `47c3a8f` | DC-17 | `python -m pii_anon_datasets.stats.lattice --check` (green this session) |
| **NFR-053** | NFR-018 committed-lattice power gate stays ON | DC-17 | `validate.py --lattice` exits non-zero on shortfall + re-enable-if-disabled test |
| **NFR-054** | Doc-drift = 0 (575,604 / 2,486,438 / 63 / 2.0.0 identical) | DC-16 | `pytest -k nfr_013` (`test_doc_drift.py`) |
| **NFR-055** | Four metric families never merged | DC-23 | static check over the CAP-02-added module set |

**Plus global rails:** no corpus regeneration; four families never merged (AX-004); PURE-STDLIB cores + lazy heavy-dep guards; `pii-rate-elo` consumed not rebuilt; eval-data NEVER imports pii-rate-elo.

---

## 2. The concrete module / file plan (BOTH repos) + the seam contract

**Deployment grain (D4 SP-S1):** two pip-installable packages in **one shared venv** (`pii-anon-core/.venv`, py 3.10.6); **in-process modules, NOT services** (no bus/broker/queue). One-way dependency (D4 §5.2 / D5 §4.5): `pii-rate-elo → pii_anon_datasets.{assessment, stats}`; **eval-data NEVER imports pii-rate-elo** (FORBIDDEN EDGE). The **sample-manifest is the sole cross-process data coupling**.

### 2.1 eval-data — `src/pii_anon_datasets/assessment/` (NEW package; confirmed absent at HEAD)

OWNS sample + observability + reporting. Pure-stdlib cores; `report.py` the **sole** lazy-heavy-dep module (D5 SP-S5).

| Module | DC(s) | Responsibility | Ring/Port role (D5) | Heavy deps |
|---|---|---|---|---|
| `__init__.py` | — | re-export the `assessment` surface + `stats` passthrough; define `ports.py` exports | — | stdlib |
| `ports.py` | — | the **5 Protocols** (`CorpusReader`, `TournamentRunner`, `RunRecordSink`, `PreregSink`, `FigureRenderer`) + the **manifest DTO** dataclasses + the **`OutcomeDTO`** runner→report contract (arch-02): per-pair discordant `(b, c)` counts, per-system per-record correct/incorrect, per-cell `(n, k)`, `scoring_family`, operating-point — the **second cross-process seam**, schema owned here, satisfied by `EloEngineAdapter`, enforced by a consumer-driven contract test parallel to the L1 manifest seam | domain ports | stdlib |
| `sample.py` | DC-17/18 | single-streaming-pass seeded lattice sampler (Algorithm-R) → builds manifest DTO | domain logic (no port) | **stdlib only** |
| `manifest.py` | DC-19 | read/write the L1 SEAM manifest; canonical-form (sorted keys + fixed float repr); non-strippable caveat | domain logic (DTO) | **stdlib only** |
| `verdicts.py` | DC-18/28 | pure power-class (4-state) / convergence / honesty-flag derivation (closed-set enums) | domain logic (no port) | **stdlib only** |
| `prereg.py` | DC-24 | immutable, commit-anchored, hash-chained pre-registration | domain logic; `PreregSink` | **stdlib only** |
| `runrecord.py` | DC-25/23/29 | write-once 6-stage run-record assembly; shared run id; provenance + submission-provenance fields | domain logic; `RunRecordSink` | **stdlib only** |
| `report.py` | DC-22/23/26/27/28/30 | **SPLIT (arch-03) into a pure `report/projection.py` (audited-stats → tables/CSV; stdlib; unit-testable without matplotlib; calls the Clean `stats/` ring directly, SP-A1) and `report/render.py` + `report/lint.py` adapters** (LaTeX/CSV render + forbidden-token/honesty-set/family-separation/recomputed-prereg-equality linters; the sole lazy numpy/matplotlib lives in the figure renderer). Projection never imports matplotlib | domain orchestration (projection) + render/lint adapters | stdlib core; **lazy numpy/matplotlib in figure code only** |

**`stats/` (EXISTING — extend in place, the Clean inner ring, D5 SP-A1):** add **`stats/multitest.py`** = Holm–Bonferroni (net-new, verified absent), pure-stdlib, deterministic, integer/float-guarded, unit-tested like its siblings. The ring (`intervals`, `paired`, `power`, `lattice`, `multitest`) is **pure functions with zero outward imports**; `report.py` calls them directly (NO port wraps them).

### 2.2 pii-rate-elo (CONSUMES — thin; do NOT rebuild engine/metrics/convergence)

| Artifact | DC(s) | Responsibility |
|---|---|---|
| `configs/assessment.yaml` | DC-20 | the assessment preset; **`analysis.run_significance_tests: false`** (P1) + the run-type→profile enum |
| `cli.py` `assessment` command | DC-20/21 | the second L3 entrypoint: `pii-rate-elo assessment --sample manifest.json --config configs/assessment.yaml --out results/` |
| thin assessment adapter (`EloEngineAdapter`, `JsonlCorpusAdapter`) | DC-21/16 | **verify manifest↔corpus (content_hash + lattice_version) fail-closed before scoring (nielsen-02)** → load manifest → run `PIIRateEloEngine` + `ConvergenceChecker` + `compute_span_metrics` → hand per-system/per-record outcomes to `pii_anon_datasets.assessment.report` **as the `OutcomeDTO` defined in eval-data `ports.py` (arch-02), validated by the consumer-driven contract test** |
| `datasets/converters/pii_anon_eval.py` + `schema.py` fix | DC-16 | v2.0.0 metadata pins + the 5-tuple regression contract |

### 2.3 The seam contract (the load-bearing L1 schema — `assessment/manifest.py` writes; the pii-rate-elo adapter reads)

The **sample-manifest** is the sole data coupling. Canonical-form equality (NFR-030): **sorted keys + fixed float repr**; re-running the sampler from the `repro` block reproduces the manifest under canonical-form equality and every seeded artifact byte-identically.

| Field group | Contents | Serves |
|---|---|---|
| `schema` | `"pii-anon-assessment-manifest/v1"` (mirrors the RUNRECORD schema-id discipline) | versioning |
| `record_ids` | the exact corpus record ids the run scores (the adapter scores **only** these) | L1 seam; FR-034 |
| `per_cell_draw[]` | per (entity-type × language) cell: `cell_id`, `tier`, `target_n`, `realized_positive_count`, draw provenance, `power_class ∈ {WELL_POWERED, UNDER_SAMPLED, CORPUS_LIMITED, EMPTY, NOT_ASSESSED}`, **`power_operating_point` (= `recall@p_ref`; the verdict applies to recall only — stat-03)**, integer `realized_positive_shortfall` | NFR-035/036/037 |
| `design_point` | per-tier `(p_ref, half_width, α)` triple + the coverage envelope (which of 63 types × 60 langs × 5 domains committed) | NFR-039 |
| `inferential_target` | `descriptive-census` (full-corpus exact → no-CI default) \| `super-population` (CIs retained) — **FR-036 / integrity-MAJOR-1** | FR-036 |
| `power_verdict` | `PowerMatrix.verdict() ∈ {SMALL, ADEQUATE, LARGE}` **rendered with the token-bound caveat `<verdict> · conditional-on-this-sample · synthetic-only`; a sample run never carries a bare `LARGE` (integrity-MAJOR-2)** | NFR-035 |
| `repro` | `seed`, **`rng_fingerprint` = `"random.Random((seed, cell_id))"` per-cell derivation (repro-01)**, `lattice_version` (730@`47c3a8f`), **`sampler_version` = sha256 of the FULL §7 sampler closure {`subsets/slices.py`, `stats/power.py`, `scripts/lattice_audit.py`, `scripts/benchmark_throughput.py::reservoir_sample`, `assessment/sample.py`, `assessment/verdicts.py`} (repro-02)**, **`ut5_integers` {small_n_cutoff, beta, recall_target, min_seeds} frozen IN this hashed block (repro-02)** | NFR-030/021/038 |
| `run_type` / `preset` | the upfront selector (`smoke`/`dev`/`leaderboard-submission`/`filing-grade`; preset `powered-representative`/`full`/`smoke`) | NFR-033/034 |
| `caveat` | non-strippable synthetic-only / anti-anonymity caveat (`DesignProvenance.__post_init__` raises on empty) | NFR-044 |
| `provenance` | producing `{run_id, stage, code_commit, content_hash}` | NFR-042/043 |

**Standalone invariant (L1/L4):** the manifest is the only thing pii-rate-elo needs from eval-data's *data* side; its bundled parser independently reads the on-disk v2.0.0 corpus via `resolve_eval_dataset_path` / `PII_ANON_DATASET_ROOT` (no shared import).

**ENTRY-B fail-closed precondition (nielsen-02 — closes "two parsers, one corpus" silent divergence):** before scoring **any** record, the pii-rate-elo `assessment` command verifies the manifest's `content_hash` + `lattice_version` against the corpus the bundled parser resolves (and checks `seed`/`sampler_version` on a warning channel). On mismatch it **aborts before the first record** with a named message stating the field + the manifest value + the resolved-corpus value. A stale or mismatched manifest can no longer silently score the wrong records.

### 2.4 The dependency-direction rule (the architectural invariant, D5 §4.5)

```
   DOMAIN HEXAGON (eval-data: pii_anon_datasets.{stats, assessment})
   imports ONLY stdlib + its own ports.py; NEVER an adapter; NEVER pii-rate-elo
        │ defines ports                              ▲ report calls the Clean stats ring DIRECTLY (no port, SP-A1)
        ▼                                            │
   ADAPTERS (infrastructure — the only code that names pii-rate-elo or heavy deps):
     • EloEngineAdapter      → pii-rate-elo engine   (SINGLE cross-repo import surface)
     • JsonlCorpusAdapter    → bundled v2.0.0 parser (standalone-installable)
     • MatplotlibFigureAdapter → numpy/matplotlib    (lazy, figure code only)
     • analysis.significance → NOT an adapter; on a DISJOINT sub-graph (unreachable, §9)
        ▲ wired by
   COMPOSITION ROOT (the two CLIs): constructor injection, NO DI framework (SP-A5)

   DATA SEAMS: (1) L1 cross-process = sample-manifest.json (DTO); (2) in-process runner→report = OutcomeDTO
               in ports.py (arch-02), schema owned by eval-data, satisfied by EloEngineAdapter, contract-tested
   FORBIDDEN EDGES: domain ↛ adapter/pii-rate-elo ; assessment ↛ analysis.significance ; EloEngineAdapter ↛ stats/*
```

---

## 3. Finalized schema — the observability run-record (reuse the `benchmark_throughput` pattern, L5/DC-25)

One **write-once** record per spine stage, **6 records** under a shared `run_id` (NFR-042). Reuses the verified `benchmark_throughput.build_run_record` pattern: a schema id, `harness_version`, **injectable `timestamp`**, `seed`, `host` (via `host_spec()`, always `is_reference_host=False`), and the **`provenance` block**.

```jsonc
{
  "schema": "pii-anon-assessment-runrecord/v1",   // mirrors RUNRECORD_SCHEMA discipline (benchmark_throughput.py:65)
  "harness_version": "<assessment harness semver>",// cf. HARNESS_VERSION (:66)
  "timestamp": "<injectable ISO-8601 UTC>",        // injectable for byte-repro (build_run_record :361 pattern)
  "run_id": "<shared across all 6 stage records>",
  "stage": "load|sample|run|score|rate|report",   // one record per stage
  "seed": 7,
  "dataset_version": "2.0.0",                       // the DC-16 5-tuple surfaced as fields (FR-031→FR-045)
  "record_count": 575604,                          // resolved from version-pinned loader, never a literal at runtime
  "entity_type_count": 63,                          // derived from taxonomy.ENTITY_TYPE_COUNT
  "schema_fingerprint": "<annotation-key-set + 63-type vocab hash>",
  "inferential_target": "descriptive-census|super-population",  // integrity-MAJOR-1: stamped per run; full-corpus census ⇒ no-CI default
  "content_hash": "<sha256 via write_manifest._sha256 over a FIXED sorted file enumeration>",  // canonicalization pinned (repro-03); same-count-swap guard (GAME-07)
  "code_commit": "<git sha of the producing executable>",
  "toolchain": { "python": "3.10.6", "key_deps": {} },
  "host": { "...": "host_spec(); is_reference_host: false" },
  "stage_timing": { "wall_seconds": 0.0 },
  "provenance": {                                   // reused block shape (benchmark_throughput.py:418)
    "is_reference_host": false,
    "environment": "agent-execution-sandbox",
    "canonical_verdict": "INSUFFICIENT_EVIDENCE",   // for any inherited perf claim (NFR-010b stays as-is)
    "rng_fingerprint": "random.Random((seed, cell_id)) per cell",  // repro-05: echoed from the manifest into the run-record for closure
    "stage_inputs": ["<content_hash of each consumed artifact>"]
  },
  "prereg_ref": { "commit_sha": "...", "prereg_hash": "..." }  // chained into the FIRST scoring record (DC-24→DC-25)
}
```

**File-level provenance (FR-046/NFR-043):** *every* emitted artifact (manifest, run-records, leaderboard, figures, pre-reg) additionally carries `{content_hash, code_commit, run_id, stage}` (via `write_manifest._sha256` + a `MANIFEST.sha256`-style index). **Write-once discipline (D4 SP-S3):** run-records and the pre-reg are immutable once written — plain content-hashed JSON, **not** an event-sourcing store.

---

## 4. Finalized schema — the pre-registration artifact (DC-24; AX-005 element 4)

Immutable, git-commit-anchored, hash-chained (`assessment/prereg.py`).

```jsonc
{
  "schema": "pii-anon-assessment-prereg/v1",
  "prereg_hash": "<sha256 of the canonical payload below>",
  "commit_sha": "<SHA committed AND pushed to a NAMED remote/branch>",   // oracle: git branch -r --contains <sha> non-empty AGAINST the configured origin; local-only SHA fails (repro-04)
  "remote_url": "<the configured origin URL — recorded IN the hashed payload>",  // repro-04: the oracle can't pass on an unrelated remote
  "run_id": "<chained into the first run/score record>",
  "created_utc": "<ISO-8601>",
  "run_type": "leaderboard-submission|filing-grade|dev",  // enforcement scope (NFR-031/033)
  "inferential_target": "descriptive-census|super-population",  // integrity-MAJOR-1 / FR-036: full-corpus census ⇒ descriptive (no CI) unless super-population
  "run_lineage_count": 0,                                  // # prior pre-registered runs for this system set (GAME-05)
  "design_and_analysis_plan": {                            // the immutable equality set (NFR-031)
    "dataset_version": "2.0.0",
    "sample_manifest_hash": "<sha256 of the consumed manifest>",
    "seed": 7,
    "rng_fingerprint": "random.Random((seed, cell_id)) per cell",  // repro-01: the per-cell derivation, pinned
    "sampler_version": "<sha256 of the full §7 sampler closure>",   // repro-02: ALL modules the draw touches
    "system_list": ["..."],
    "metric_set": ["recall","precision","f_beta","auprc"],
    "rd_stopping_rule": { "rd_threshold": 100, "max_rounds": 0 },
    "interval_selection_rule": { "default": "wilson", "boundary": "clopper-pearson",
                                 "small_n": "clopper-pearson", "small_n_cutoff": 15, "differences": "paired-bootstrap" },
    // multiplicity (stat-01 / NFR-027): Holm WITHIN each (metric, scoring-family) partition — NEVER pooled across
    // metrics or across anon/pseudo (AX-004). family_size is the COMPUTED #pairs × #metrics in the confirmatory set,
    // per partition (no longer the "0" placeholder); the report asserts its printed family == this value.
    "multiplicity": { "families": ["exploratory","confirmatory"], "method": "holm-bonferroni",
                      "partition": "per (metric, scoring_family)", "family_size": "<computed = #pairs × #metrics in confirmatory set>" },
    "n_boot": 10000,                                       // stat-06: replicate count affects CI width → pre-registered, not a hidden constant
    "min_seeds": 3,                                        // stat-06 / UT-5: seed count pre-registered
    "power_design_point": { "CRITICAL": [0.99,0.005], "STANDARD": [0.98,0.010], "LONG_TAIL": [0.95,0.03025] },
    "power_operating_point": "recall@p_ref",              // stat-03: the verdict covers RECALL only; other metrics NOT_ASSESSED unless re-sized
    "span_match_mode": "exact|relaxed-overlap",
    "scoring_family": "anonymization|pseudonymization",
    "operating_point": { "beta": 2, "recall_target": 0.90, "fn_fp_cost": null },
    "ut5_integers": { "small_n_cutoff": 15, "beta": 2, "recall_target": 0.90, "min_seeds": 3 },  // repro-02: frozen INTO the hashed payload, not adjacent
    "tie_exclusion_rules": "..."
  }
}
```

The final report (FR-050) embeds `{prereg_hash, commit_sha, run_id}` and a `pre_registration_matches` flag that is a **recomputed hash-equality** — the honesty linter independently re-derives the hash of the report's realized plan and compares it to `prereg_hash` over `design_and_analysis_plan` (NOT a self-asserted boolean the report writes about its own plan; integrity-MINOR-3). A drifted run cannot emit `true`.

---

## 5. Finalized — `configs/assessment.yaml` (DC-20; the pii-rate-elo consumer config)

```yaml
# pii-rate-elo assessment preset — CONSUMER side. P1: run_significance_tests MUST be false.
analysis:
  run_significance_tests: false          # P1 / NFR-019 (belt-and-suspenders with the §9 import-graph gate)

assessment:
  manifest: null                          # set by --sample (the L1 seam)
  out_dir: results/
  span_match_mode: exact                  # FR-039; ∈ {exact, relaxed-overlap}; echoed + pre-registered
  block_on_underpower: false              # SP-U4 default; --block-on-underpower flips GATE-P3 fatal on the default preset

  # The committed run-type → profile enum (NFR-033; a table the test READS, names finalizable but the table is referenced):
  run_types:
    smoke:                 { rigor_bar: suppressed,  prereg: off,      sample_mode: sample }
    dev:                   { rigor_bar: suppressed,  prereg: opt-in,   sample_mode: sample }
    leaderboard-submission:{ rigor_bar: full-AX005,  prereg: enforced, sample_mode: sample }
    filing-grade:          { rigor_bar: full-AX005,  prereg: enforced, sample_mode: full }   # DF-1 filing-grade may bind full-corpus

stats:                                    # all audited eval-data stats/ (P1); NO pii-rate-elo significance
  interval_default: wilson
  interval_boundary: clopper-pearson
  small_n_cutoff: 15                       # recorded in manifest + pre-reg; R10-DIRECTIONAL (real_user_needed)
  multiplicity: holm-bonferroni           # → stats/multitest.py (net-new audited primitive)
  min_seeds: 3                             # Kendall-τ rank stability OR single-seed → rank-volatility UNMEASURED
  operating_point: { beta: 2, recall_target: 0.90 }
```

The eval-data **ENTRY-A** sampler takes its knobs as CLI flags (`--preset`/`--seed`/`--run-type`/`--out`/`--block-on-underpower`/`--show-cells`/`--quiet|--json-only`/`--no-color`/`--help|--help-advanced`; advanced = `--alpha`/`--lattice`/`--small-n-cutoff`/`--seeds`); the run-type→profile enum is shared with the YAML so both CLIs agree (DC-20). **Coherence validation (nielsen-04):** `--preset` × `--run-type` is validated at parse time against the `run_types` table's `sample_mode` — contradictory combos (e.g. `preset=smoke` + `run-type=filing-grade`, whose `sample_mode` is `full`) are **rejected with a message** rather than silently producing an incoherent run; the table is the single source of truth. The chosen `inferential_target` (descriptive-census for `preset=full` unless `--super-population` is set; integrity-MAJOR-1) is recorded into the manifest + prereg + run-record.

---

## 6. Finalized — the report / leaderboard schema (DC-26/27/28; the Info-Dense register)

`results/` layout (artifact-first; LaTeX + CSV primary, JSON run-records the reproduction substrate):

```
results/
├── leaderboard.tex            # PRIMARY citable register (FR-047)
├── leaderboard.csv            # machine register (same content + same gating)
├── report.{tex,pdf}           # full info-dense report (header + tables + figures + honesty bundle)
├── figures/                   # AUPRC / Fβ-asymmetry / per-language-recall (matplotlib, lazy-imported — DC-27)
├── run-records/run-<run_id>.jsonl   # 6 chained records (L5/NFR-042; audit deliverable, SP-W5)
├── prereg.json                # FR-044; embedded into the report header
└── manifest.copy.json         # the consumed L1 manifest (provenance closure)
```

**Leaderboard `tabular` columns** (the Info-Dense core; each cell carries its CI + method inline; AX-004 anon/pseudo as **separate metric families, never merged**):

| column | content | requirement |
|---|---|---|
| system | id + `contamination_status ∈ {disclosed-unseen, disclosed-trained-on-corpus, undisclosed}` (`unknown` ⇒ rejected/flagged) | NFR-048 |
| family | **anon** \| **pseudo** as separate families (never one "redaction quality" number); Holm multiplicity is corrected **within** each (metric, family) partition, never across (stat-01) | AX-004 / FR-047 |
| metric (per family) | recall / precision / Fβ / AUPRC. **CI behaviour is `inferential_target`-scoped (integrity-MAJOR-1):** for the **inferential** targets (powered sample / `super-population`) each metric carries its CI + `method ∈ {wilson, clopper-pearson, paired-bootstrap}` inline + `scope: conditional-on-this-sample` (cells within ±1 of `small_n_cutoff` flagged, stat-04); for a **full-corpus `descriptive-census`** the CI column is **suppressed / labelled descriptive-only — no CI by default** (FR-036). The per-system marginal CI is **descriptive-only** and does **not** govern rank (stat-02) | FR-036/040 / NFR-024 |
| Δ vs next rank (**rank oracle**, stat-02) | for every **adjacent rank pair**: the paired **Δ with its bootstrap CI** + the **McNemar p** (the rank-governing statistics, NFR-026) | NFR-026/028 |
| rank | **gated by the paired Δ / McNemar verdict** — adjacent pairs not significant after Holm–Bonferroni (confirmatory **family size = #pairs × #metrics in the confirmatory set, stated, == prereg**; stat-01/integrity-MINOR-4) greyed/grouped as ties; overlapping marginal CIs alone never decide a tie (stat-02) | FR-041/047 / NFR-027/028 |
| power | per-cell `power_class` roll-up + corpus verdict, **each carrying `power_operating_point` (= recall@p_ref); precision/Fβ/AUPRC/pseudo-re-id show `NOT_ASSESSED` unless sized by a matching ladder (stat-03)**; under-tier carries named shortfall in realized positives | FR-033 / NFR-035/037 |
| caveat | non-strippable synthetic-only / anti-anonymity caveat, inline per metric | AX-001/003 / NFR-044 |

**Honesty bundle (NFR-047 closed set, inline + non-strippable — stripping any one invalidates the artifact):** `RD-NOT-CONVERGED` (achieved max-RD ± 2RD + rounds + stopping rule; **labelled strictly as tournament-rating convergence — it does NOT certify the recall estimate's interval validity; NOT-CONVERGED blocks ranking, not CI validity**, stat-05) · per-cell `UNDER-POWERED / UNDER-SAMPLED / CORPUS-LIMITED` (each with `power_operating_point`, stat-03) · `contamination-uncontrolled` · `rank-volatility: UNMEASURED` (single-seed) or Kendall-τ **reported with the seed count inline** (≥3 seeds; not over-read as established stability, stat-06) · **worst-language recall** = `argmin` over coverage-envelope languages + label · **low-resource recall** = recall over committed languages with realized positives `< 200` · `correlation-study: named-and-pending` · `NOT_ASSESSED` for critical types outside the envelope. **Self-verifying header (FR-050):** `{prereg_hash, commit_sha, run_id}` + `inferential_target` (descriptive-census | super-population, integrity-MAJOR-1) + run-lineage count + run-type contract triple + seed + RNG fingerprint + **the corpus `PowerMatrix.verdict()` rendered as one non-strippable unit `<verdict> · conditional-on-this-sample · synthetic-only` — a sample run NEVER renders a bare `LARGE` (integrity-MAJOR-2, G3)** + Art-11 alignment label. **`pre_registration_matches` is a recomputed hash-equality the honesty linter independently re-derives (prereg `prereg_hash` vs a recomputed hash of the report's realized plan), not a self-asserted boolean (integrity-MINOR-3).**

**Forbidden-token lint (FR-047/C7):** the LaTeX + CSV registers contain **none** of `{SHIP-WITH-CAVEATS, SHIP, DEFER, GO/NO-GO}` (extensible). **Smoke register (FR-037/NFR-034):** every CI + p-value field suppressed/null; `not_statistically_valid: true`; banner `NOT STATISTICALLY VALID`.

---

## 7. The stratified-covering sampler ALGORITHM (DC-17/18; seeded; reuses the verified APIs)

`assessment/sample.py` — a **single streaming pass**, bounded by `O(#committed-cells)=O(730)` working-set keys (NFR-038), seeded reservoir per cell, emitting the manifest + the PowerMatrix verdict + per-cell realized-positive shortfall.

**Inputs:** `preset ∈ {powered-representative, full-corpus, smoke}`, `seed`, `run_type`, the frozen lattice (`load_lattice`, 730@`47c3a8f`), the on-disk v2.0.0 corpus.

```
1.  lattice  = stats.lattice.load_lattice()                 # 730 committed cells @ 47c3a8f (NFR-052)
    index    = scripts.lattice_audit.committed_index(lattice)
    # PER-CELL CHILD RNG (repro-01): NEVER one shared rng fanned across cells — Algorithm-R is
    # deterministic only for ONE iterable consuming ONE RNG in fixed order; a shared rng drawn
    # interleaved in corpus order makes each cell's draw depend on iteration interleaving + multi-cell
    # membership. Derive an INDEPENDENT child RNG per cell so a cell's reservoir is invariant to
    # interleaving and to other cells' membership.
    cell_rng = lambda cell_id: random.Random((seed, cell_id))   # LOCAL, deterministic, per-cell (NFR-021)
    targets  = { cell: required_n(*TIER_SPECS[tier(cell)].design_point) }   # DERIVED, never hand-typed (FR-032/NFR-035)

2.  # ----- FULL-CORPUS realized positives, ONE streaming pass (the irreducible denominator for CORPUS_LIMITED) -----
    full_counts = scripts.lattice_audit.audit_positives(corpus_path, lattice)   # streaming; O(730) keys (NFR-038)

3.  # ----- preset dispatch -----
    if preset == "full-corpus":          # FR-036: descriptive census; records_scored == dataset.record_count(version)
        record_ids = ALL record ids (no draw); sample_counts = full_counts
    elif preset == "smoke":              # FR-037: fixed seeded tiny slice; inferential output suppressed downstream
        record_ids = a fixed seeded slice across cells; statistically inert
    else:                                # powered-representative (DEFAULT, FR-035; never silently full, never silently LARGE)
        # ----- ONE streaming pass: per-cell seeded reservoir to each cell's target_n positives -----
        per_cell_reservoir = { cell: ReservoirR(k=targets[cell], rng=cell_rng(cell)) }  # INDEPENDENT child RNG per cell (repro-01); Algorithm-R = benchmark_throughput.reservoir_sample
        for record in iter_corpus(corpus_path):              # generator; NEVER materialize the corpus (NFR-038)
            for cell in record_increments(record, index):    # candidate cells this record's positives hit
                per_cell_reservoir[cell].offer(record_id)     # back-loaded positives still reachable (no head-truncation, FR-032)
        record_ids   = ∪ reservoir.selected for all cells
        sample_counts = realized positive counts in the drawn set

4.  # ----- per-cell power classification AGAINST REALIZED POSITIVES (verdicts.py; 4-state extends classify) -----
    #     POWER SCOPING (stat-03): required_n / TIER_SPECS size the RECALL operating point only
    #     (p_ref 0.95–0.99). The power_class therefore covers RECALL AT power_operating_point and NOTHING
    #     else; precision / Fβ / AUPRC / pseudo re-id have different variance and were NOT sized here.
    power_operating_point = "recall@p_ref"       # recorded per cell; the verdict applies ONLY to this metric
    for cell in lattice:
        n_sample = sample_counts[cell];  n_full = full_counts[cell];  t = targets[cell]
        if   cell not in coverage_envelope: power_class = NOT_ASSESSED          # uncovered critical type (NFR-039)
        elif n_sample == 0 and n_full == 0: power_class = EMPTY                  # structural
        elif n_sample >= t:                 power_class = WELL_POWERED           # RECALL operating point ONLY (stat-03)
        elif n_full   >= t:                 power_class = UNDER_SAMPLED          # fixable: draw more (NFR-037)
        else:                               power_class = CORPUS_LIMITED         # irreducible: corpus itself short (NFR-037)
        shortfall = max(0, t - n_sample)    # NAMED in REALIZED positives, integer (NFR-036), non-strippable
        # precision / Fβ / AUPRC / pseudo-re-id are NOT sized by this ladder → power_class = NOT_ASSESSED for
        # those metrics unless a matching ladder (e.g. REID_TIER_SPECS) sizes them; the recall verdict is
        # NEVER reused as their power label (stat-03). Each cell records {power_class, power_operating_point}.

5.  # ----- corpus verdict + manifest emission -----
    verdict  = PowerMatrix(cells).verdict()        # SMALL/ADEQUATE/LARGE @ 0.80/0.999 (NFR-035; never silently LARGE, G3)
    # repro.rng_fingerprint records the PER-CELL derivation algorithm "random.Random((seed, cell_id))" (repro-01),
    # NOT just the seed. repro.sampler_version is the FULL sampler-closure hash over EVERY module the draw touches
    # (repro-02): {subsets/slices.py, stats/power.py, scripts/lattice_audit.py,
    # scripts/benchmark_throughput.py::reservoir_sample, assessment/sample.py, assessment/verdicts.py}.
    # The UT-5 tuning integers {small_n_cutoff, beta, recall_target, MIN_SEEDS} are written INTO the hashed
    # payload (not adjacent), so a patched lattice_audit or a changed cutoff CANNOT diverge under an unchanged
    # fingerprint (repro-02).
    manifest = manifest.write(record_ids, per_cell_draw=[...{cell_id, power_class, power_operating_point, shortfall}...],
                              design_point, verdict,
                              repro={seed,
                                     rng_fingerprint="random.Random((seed, cell_id)) per cell",
                                     lattice_version="730@47c3a8f",
                                     sampler_version="<sha256 of the full §7 sampler closure>",
                                     ut5_integers={small_n_cutoff:15, beta:2, recall_target:0.90, min_seeds:3}},
                              run_type, preset, inferential_target,   # descriptive-census | super-population (integrity-MAJOR-1)
                              caveat=DesignProvenance().caveat, provenance={...})
    # canonical-form (sorted keys + fixed float repr) ⇒ byte-repro GIVEN pinned {corpus content_hash,
    # lattice_version, seed} (repro-01 — NOT an unconditional "byte-repro from repro block alone") (NFR-030)

6.  # ----- GATE-P3 (run-type-scoped, SP-W2) -----
    if preset == "full-corpus"/leaderboard AND any shortfall:
        # FATAL MESSAGE (nielsen-01) — never a bare exit code. Enumerate, to stderr, each offending cell:
        #   cell_id · power_class · integer realized-positive shortfall · the ACTIONABLE remedy:
        #     UNDER_SAMPLED  → "draw more: raise sample size / re-run with a larger draw"
        #     CORPUS_LIMITED → "IRREDUCIBLE: the corpus itself has only <n_full> realized positives for this
        #                       cell; drawing more cannot fix it" (do NOT tell the user to draw more)
        # then exit non-zero. (validate.py --lattice semantics, NFR-053)
        exit non-zero
    elif default AND under-tier:  CONTINUE, carry power_class as a non-fatal honesty FLAG  # the study's strongest delight
    if --block-on-underpower:     promote the default flag to a hard halt with the SAME enumerated message (SP-U4)
```

**Determinism (AX-002/NFR-030; repro-01 corrected):** a **per-cell child `random.Random((seed, cell_id))`** (NOT one shared RNG fanned across cells — Algorithm-R is order-dependent), the single deterministic pass, and the canonical-form manifest make the draw **byte-reproducible given pinned {corpus content_hash, lattice_version, seed}** (recorded in `repro.rng_fingerprint`). **Progress (nielsen-03):** the `run`/`sample` stages emit per-stage progress (records scored / cells complete) to **stderr** only (stdout stays the machine channel, SP-U2); on interruption the `run_id` + "re-run byte-identical to resume" is printed. **No head-truncation (FR-032 two-part oracle):** (i) static — the sampler entrypoint never references the `max_samples` symbol; (ii) behavioral — a back-loaded fixture still reaches each cell's `target_n` (a head-truncation path fails this). **Reuse, not reinvent:** `required_n`/`TIER_SPECS`/`classify`/`PowerMatrix.verdict()` from `power.py`; `committed_index`/`record_increments`/`audit_positives`/`deficits` from `lattice_audit.py`; `reservoir_sample` from `benchmark_throughput.py`; `load_lattice` from `lattice.py`.

---

## 8. The audited-stats wiring (intervals/paired/multitest) + the significance.py quarantine (P1, DC-22)

**The run path computes ALL inference with the AUDITED eval-data stats** (the SHOWSTOPPER P1). `report.py` (the only module that touches inference) calls the Clean `stats/` ring **directly** (D5 SP-A1 — no port over `wilson_interval`):

| Inference | Audited call | Rule |
|---|---|---|
| proportion CI (interior) | `stats.intervals.wilson_interval(k:int, n:int)` | FR-040 default; integer-guarded (`_require_int_counts`) |
| proportion CI (boundary `k∈{0,n}` or `n < small_n_cutoff`) | `stats.intervals.clopper_pearson_interval(k:int, n:int)` | FR-040 load-bearing branch; `small_n_cutoff=15` recorded in manifest+prereg |
| paired difference CI (**rank oracle**, stat-02) | `stats.paired.paired_bootstrap_recall_delta(..., seed=…)` | LOCAL `random.Random(seed)` (NFR-021), byte-identical; computed for **every adjacent rank pair** (NFR-026) — this Δ CI + the McNemar p **govern the rank**, the per-system marginal Wilson CIs are **descriptive-only** |
| pairwise significance | `stats.paired.mcnemar_exact(b,c)` / `mcnemar_chi2(b,c,continuity=True)` | exact for small discordant counts, Edwards χ² otherwise (NFR-026) |
| multiplicity correction | **`stats.multitest.holm_bonferroni(pvalues)`** (NET-NEW) | Holm **WITHIN each (metric, scoring-family) partition — NEVER pooled across metrics or across anon/pseudo (AX-004)** (stat-01); confirmatory family size = **#pairs × #metrics in the confirmatory set** (NFR-027, computed from the structured `inference_families` block, NOT "printed"); asserted **== prereg family_size** (integrity-MINOR-3/4) |

**The quarantine (NFR-019/020, the canonical mechanism = D5 §9, summarized in §9 below):** a **two-predicate CI gate** ("green requires no human"): (a) the fabricated **module** `pii_rate_elo_pipeline.analysis.significance` is absent from the **static-AST import-closure** (arch-01 — NOT a runtime `sys.modules` snapshot) of both assessment entrypoints (module-level per SP-A3, because the eager `:409` `_tester_instance = SignificanceTester()` means *any* import constructs the fabricated tester), AND (b) `analysis.run_significance_tests == False` in the loaded config. Plus a **fabrication-regex lint** (NFR-020) over the declared run-path module set for the three verified signatures `{*(1-*)/100, np.random.normal, (n_approx|pooled_sd=0.1|sqrt(n_approx)/0.05)}` — zero matches. **Holm lands in audited `stats/`, NEVER in `significance.py`** (SP-S4). **Authority-by-placement (SP-A2):** the audited inference functions are imported **only** by `report.py`; the `EloEngineAdapter` has **no import edge** to `stats/*` — so the fabricated path is on a sub-graph disjoint from the assessment call path.

---

## 9. THE import-boundary rule that makes `significance.py` unreachable (P1 — the canonical NFR-019 gate; D5's load-bearing deliverable)

P1 is enforced as a **conjunction of two CI predicates** living in **eval-data** (the OWNS side), with a mirror import-lint in pii-rate-elo CI (NFR-051):

**Predicate (a) — static import-graph unreachability of the FABRICATED MODULE (module-level, SP-A3):**
Build the transitive import closure from **both** assessment entrypoints — (1) the eval-data sampler CLI `pii_anon_datasets.assessment.sample`, and (2) the pii-rate-elo `assessment` command + its `EloEngineAdapter`. **CLOSURE MECHANISM = a static AST import walk (arch-01):** a `grimp`/`modulefinder`-class **static** import-graph walk over both entrypoints — **NOT** a runtime `sys.modules` snapshot. The distinction is load-bearing: a runtime snapshot only proves *the path you exercised didn't import the module*; the static AST walk proves **unreachability** (the actual P1 claim). **S8 story-0 emits a pinned module-node list the test asserts against**, so the gate is real *before* the unverified pii-rate-elo adapter exists (UT-1). **Assert the module node `pii_rate_elo_pipeline.analysis.significance` is NOT in either closure.** Module-level (not symbol-level) because the eager `_tester_instance = SignificanceTester()` at module scope (Discovery: `significance.py:409`) means importing the module at all constructs the fabricated tester; if the S8 re-confirm finds the eager instantiation gone, SP-A3 relaxes to symbol-level — and **both** the module-level and symbol-level guard tests are authored in S8 so the active regime is a recorded choice, not improvised (arch-04). The `assessment` adapter imports `tournament.engine` / `tournament.convergence` / `evaluation.metrics_bridge` **directly**, never the `cli` module's `from .analysis.significance import SignificanceTester` line (Discovery: `cli.py:33`).

**Import-gate FATAL MESSAGE (nielsen-01):** on failure the gate does not emit a bare pass/fail — it names the **offending edge** (importer module → `pii_rate_elo_pipeline.analysis.significance`) and the **module node** that pulled it into the closure, so the diagnosis is actionable.

**ENTRY-B manifest↔corpus precondition (nielsen-02 — fail-closed, before any scoring):** the pii-rate-elo `assessment` command, at start, verifies the manifest's `content_hash` + `lattice_version` (and `seed`/`sampler_version` for the warning channel) against the corpus the bundled parser resolves (`resolve_eval_dataset_path` / `PII_ANON_DATASET_ROOT`). On mismatch it **aborts before scoring any record** with a named message stating the field, the manifest value, and the resolved-corpus value (closes the "two parsers, one corpus" silent-divergence vector). This guard lives on the consumer side but mirrors the eval-data hashing (`write_manifest._sha256`).

**Predicate (b) — runtime config assertion:** `configs/assessment.yaml` sets `analysis.run_significance_tests: false`; a test asserts the loaded `PipelineConfig.analysis.run_significance_tests == False`. Belt-and-suspenders: even on the standalone `run` path the flag gates the (Discovery) `cli.py:242` instantiation; on the `assessment` path, (a) guarantees the module is never imported.

**True-by-construction:** the single import-graph test enforces all three forbidden edges at once — `domain ↛ adapter`, `assessment ↛ analysis.significance`, and `EloEngineAdapter ↛ stats/*`. Mutating either predicate (add the import edge; flip the flag `true`) turns the gate **RED**.

---

## 10. The v2.0.0 seam fix + regression-contract design (P2, DC-16; L4 RESOLVED)

**L4 decision (D4 §4, ratified): FIX the pii-rate-elo bundled parser to v2.0.0 + pin the 5-tuple regression contract; reserve `load_dataset` for the eval-data sampler side.** Grounded in the firsthand fact that `load_dataset` (`__init__.py:55`) takes **no `version` arg** — importing it into the consumer would couple the consumer's loader to eval-data's package layout for zero version-selection benefit and break the standalone invariant.

**What gets fixed** (Discovery line numbers — **re-confirm before editing**, UT-1):
- `datasets/converters/pii_anon_eval.py`: `num_records=159891` (L93) → **575604**; `license="CC-BY-4.0"` (L221) → **CC0 / CC0-1.0**; `citation="…v1.3.0"` (L222) → **v2.0.0**; docstring (L1). The naive `max_samples` head-truncation (L82) is **left as-is for standalone use** (CAP-02's powered sampler lives in eval-data; the converter's head-truncation must NOT be on the assessment path — FR-032 static oracle).
- `schema.py`: `version="1.3.0"` (L137) → **2.0.0** (+ any second occurrence); the normalizer `_normalize_eval_row` (L349, reads `annotations` with a `labels` fallback) **already speaks v2.0.0's shape** — so the drift is **metadata-provenance, NOT field-reading**.

**The 5-tuple regression contract (FR-031/NFR-041)** — a committed test (`tests/test_pii_anon_eval_v2_contract.py`, RED-first in S8) that mutates each pin in turn and asserts RED, green on the true values. **On failure the contract names the drifted tuple element + expected-vs-found (nielsen-01)** — e.g. `version: expected 2.0.0, found 1.3.0` — never a bare assertion error, so a maintainer diagnoses the regression at a glance:

| Pinned value | Canonical (eval-data `tests/test_doc_drift.py`) | Guards against |
|---|---|---|
| version | `2.0.0` | regression to v1.3.0 |
| record_count | `575,604` | regression to 159,891 |
| entity-type count | `63` (**derived** from `taxonomy.ENTITY_TYPE_COUNT`) | vocabulary drift |
| schema fingerprint | annotation-key set + 63-type vocab hash | same-count mutated annotation schema |
| dataset content hash | sha256 via `write_manifest._sha256` | silent same-count content swap (GAME-07) |

**Path coherence (verified-via-Discovery):** `resolve_eval_dataset_path` (`schema.py:583`) walks ancestors + honors `PII_ANON_DATASET_ROOT` (`schema.py:627`) → the bundled parser locates the **same** on-disk v2.0.0 corpus the eval-data sampler reads, **no shared import** — "two parsers, one corpus, one manifest seam."

---

## 11. Build sequence mapped to sprints S8–S12

Ordered by the precondition gates (P1 must land **first** per R7 T3) and the linear data dependency. Each story is RED→GREEN→REFACTOR (cycle-1 TDD discipline); both repos' gates (pytest/ruff/mypy) stay green at every sprint boundary (NFR-051).

| Sprint | Theme | DCs | Key deliverables | Exit gate |
|---|---|---|---|---|
| **S8** | **Preconditions: seam + quarantine scaffolding** | DC-16, DC-22 (P1 gate only) | **(0) RE-CONFIRM all pii-rate-elo line numbers against a checkout (UT-1); emit the pinned static-AST module-node list the §9 gate asserts against (arch-01); author BOTH the module-level and symbol-level import-guard tests, recording the active regime (arch-04).** v2.0.0 metadata pins + the 5-tuple regression contract (RED-first, **named-element failure message**, nielsen-01); `configs/assessment.yaml` with `run_significance_tests:false`; the **§9 two-predicate STATIC-AST import-graph gate** (P1) as a standalone contract test (named-edge failure message, nielsen-01); `stats/multitest.py` Holm (net-new, unit-tested, **per-(metric,family) partition**, stat-01). | P2 contract RED-on-drift green; **P1 gate green (module unreachable via static AST + flag false)**; pinned node list committed; doc-drift NFR-054 green; both venvs' gates green |
| **S9** | **Sampler + manifest (the L1 seam)** | DC-17, DC-18, DC-19 | `assessment/{sample,verdicts,manifest}.py` + the §7 algorithm; the manifest DTO + canonical-form equality test (NFR-030); 4-state power classification vs realized positives; ENTRY-A CLI (`assessment.sample`) with the banner + machine-stdout (SP-U2) + `--show-cells`/`--block-on-underpower`. | P3: lattice `--check` 730 green (NFR-052); `validate.py --lattice` ON (NFR-053); back-loaded-fixture no-head-truncation oracle green; manifest byte-repro green |
| **S10** | **Run path: orchestrator + audited stats wiring** | DC-21, DC-22 (full), DC-23, DC-25 | `EloEngineAdapter` (+ **ENTRY-B manifest↔corpus fail-closed precondition**, nielsen-02) + `JsonlCorpusAdapter` + pii-rate-elo `cli.py assessment`; the **`OutcomeDTO` in `ports.py` + the consumer-driven contract test** (arch-02); `report.py` split into projection vs render/lint (arch-03) — audited CIs (**`inferential_target`-scoped**, integrity-MAJOR-1) + **adjacent-pair paired-Δ rank oracle** (stat-02) + Holm **per-(metric,family) partition** (stat-01); `runrecord.py` 6-stage write-once records (reuse `build_run_record` pattern, **rng_fingerprint echoed**, repro-05); family-separation + contamination + seed-variance fields. | P1 full (audited path taken, fabricated unreachable via static AST); ENTRY-B precondition fail-closed green; OutcomeDTO contract test green; CI-on-every-(inferential-)metric + paired-Δ-on-every-adjacent-pair linters green; 6 run-records shared run_id (NFR-042); NFR-050 cores-stdlib green |
| **S11** | **Pre-reg + report + honesty bundle** | DC-24, DC-26, DC-27, DC-28, DC-29 | `prereg.py` (commit-anchored + hash-chained + remote oracle); `report.py` tie-gated leaderboard + LaTeX/CSV + forbidden-token lint + honesty-set linter + self-verifying header; `MatplotlibFigureAdapter` operating-point figures (lazy); governance block + hygiene attestation + recusal. | pre-reg↔report parity (NFR-031); tie-gating (NFR-028); honesty-set non-strippable (NFR-047); forbidden-token scan green; figures lazy-import-only (NFR-050) |
| **S12** | **Run-type scope, crosswalk, release, E2E** | DC-20 (full), DC-30, DC-31 | run-type→profile enum total-triple test (NFR-033) + smoke statistically-inert (NFR-034); regulatory crosswalk artifact (DC-30, AUTHOR-not-defer); DOI/citation release + claims policy (DC-31); the **one-command chain E2E** on smoke; full no-regression sweep. | run-type table green; smoke inert green; E2E chain green; all no-regression rails (NFR-052/053/054/055) green; both repos' gates green |

**Dependency note:** S8 (P1+P2) gates everything (R7: P1 must land first). S9's manifest is the seam S10 consumes. S11 depends on S10's audited-stats output (report DCs fan in on one statistical source of truth). The long `run` stage has **no sub-run resume** (D2 SP-W3) — recovery is byte-identical re-run.

---

## 12. AUDIT 1 — Requirements-to-design traceability (every FR-030…054 / NFR-019…055 → ≥1 DC)

### 12.1 FR coverage — all 25 FRs bound, 0 orphans
DC-16: FR-030/031 · DC-17: FR-032 · DC-18: FR-033 · DC-19: FR-034 · DC-20: FR-035/036/037/038 · DC-21: FR-039 · DC-22: FR-040/041/042 · DC-23: FR-043 · DC-24: FR-044 · DC-25: FR-045/046 · DC-26: FR-047 · DC-27: FR-048 · DC-28: FR-049/050 · DC-29: FR-051/052 · DC-30: FR-053 · DC-31: FR-054.
**Σ = 25 distinct FRs, each in exactly one DC. 0 orphan FRs.** ✔

### 12.2 NFR coverage — all 37 NFRs bound, 0 orphans
DC-16: NFR-040/041/054 · DC-17: NFR-035/038/039/052/053 · DC-18: NFR-035/036/037 · DC-19: NFR-030/039 · DC-20: NFR-025/033/034 · DC-21: NFR-029/051 · DC-22: NFR-019/020/021/022/023/024/026/027/050 · DC-23: NFR-045/048/055 · DC-24: NFR-031/032 · DC-25: NFR-042/043 · DC-26: NFR-028/044 · DC-27: NFR-046 · DC-28: NFR-029/047 · DC-29: NFR-048/049.
**All 37 land on ≥1 DC. 0 orphan NFRs.** ✔
(Shared-across-two-DCs quality attributes, each a single attribute exercised by the two DCs that jointly satisfy it, not a double-count: NFR-035 DC-17+DC-18; NFR-039 DC-17+DC-19; NFR-029 DC-21+DC-28; NFR-048 DC-23+DC-29.)

### 12.3 Precondition coverage
- **P1 (SHOWSTOPPER)** → DC-22 (+ §8/§9). **P2** → DC-16 (+ §10). **P3** → DC-17 + DC-18 + DC-19 (+ §7). ✔

### 12.4 The 6 R7-stratified requirements land with their stratified priority honored
FR-043 (SHOULD; NR-core MUST via NFR-055) → DC-23 ✔ · FR-045 (SHOULD; 6-stage floor assurance-MUST) → DC-25 ✔ · FR-048 (COULD/MUST-for-P-priv-eng) → DC-27 ✔ · FR-052 (SHOULD) → DC-29 ✔ · FR-053 (SHOULD, AUTHOR-not-defer) → DC-30 ✔ · FR-054 (SHOULD, MUST-for-P-acad-deid) → DC-31 ✔.

**Audit 1 verdict: PASS — 25/25 FRs and 37/37 NFRs each map to ≥1 DC; 0 orphans both directions; all 3 preconditions and all 6 stratified-priority requirements placed.**

---

## 13. AUDIT 2 — Axiom-saturation (AX-001…005 each covered at the touched layer)

Per D1 SP-5, AX-005 is a cross-cutting invariant tracked as a matrix (not a DC). Each axiom is shown saturating **its touched layers** (load/sample/run/score/rate/report/X), each by a concrete DC + the mechanism.

| Axiom | LOAD | SAMPLE | RUN/RATE | SCORE | REPORT | X (obs/gov/release) | Saturated? |
|---|---|---|---|---|---|---|---|
| **AX-001** (synthetic-only) | — | DC-19 (manifest caveat by construction) | — | — | DC-26/28 (inline non-strippable) | DC-31 (claims policy) | ✔ `DesignProvenance.__post_init__` raise-on-empty seeds it at the manifest; the linear data dependency carries it (NFR-044) |
| **AX-002** (deterministic/seeded/byte-repro) | — | DC-17 (LOCAL RNG, single pass), DC-19 (canonical-form) | DC-21 (consumed deterministically) | DC-22 (seeded paired-bootstrap) | DC-28 (self-verifying header) | DC-24/25 (hash-chain, repro block) | ✔ NFR-030/021/038/042 |
| **AX-003** (stated power: n + CI) | — | DC-17/18 (power class vs realized positives; design point) | — | DC-22 (integer-guarded CIs on every metric) | DC-28 (power flags as honesty bundle) | — | ✔ NFR-022/023/035/036/037/039 |
| **AX-004** (anon vs pseudo SEPARATE) | — | — | — | DC-23 (scoring_family; never merged) | DC-26 (separate families), DC-30 (legally-distinct regimes) | — | ✔ NFR-045/055 static no-merge check |
| **AX-005** (pre-registered/reproducible, 6 elements + scope) | — | DC-19/20 (run-type scope; manifest repro) | DC-21 (convergence), DC-22 (CI+paired+Holm) | DC-23 | DC-26/28 (tie-gating, convergence, honesty, self-verify) | DC-24 (pre-reg el.4), DC-25 (provenance el.4), DC-29 (contamination el.6) | ✔ the most cross-cutting; element→DC map below |

**AX-005 element → DC (the testable saturation):** (1) CI+method → DC-22 · (2) paired+Holm+2-families → DC-22/26 · (3) convergence max-RD±2RD → DC-21/28 · (4) provenance reproducible-from-manifest → DC-19/24/25/28 · (5) non-strippable caveat → DC-19/26/28 · (6) contamination + attestation → DC-23/29 · enforcement scope (run-type) → DC-20.

**Touched-layer rule honored:** AX-001/003/004/005 each saturate every spine layer they *touch* (e.g. AX-003 touches SAMPLE+SCORE+REPORT and is covered at each; it does not "touch" LOAD because power is a sampling/scoring property — its absence at LOAD is correct, not a gap). AX-002 reaches the most layers and is covered at each.

**Audit 2 verdict: PASS — all 5 axioms saturate every layer they touch, each via a named DC + mechanism; AX-005's 6 elements + enforcement scope each map to a DC.**

---

## 14. AUDIT 3 — Persona-service (each HIGH persona served)

The 3 HIGH (T1) personas are the acceptance + credibility cohort (Discovery §3). Each must be served at the layers it cares about, by a DC, with a built deliverable.

| HIGH persona | Core JTBD (Discovery §5) | Served by DCs | Built deliverable that serves them | Verdict |
|---|---|---|---|---|
| **P-acad-deid** (Academic De-id Researcher) | publish/cite a defensible result that survives peer + regulator review | DC-19 (byte-repro manifest), DC-20 (full-corpus citable), DC-24 (pre-reg), DC-28 (honest self-verifying report), DC-31 (**MUST-for-this-persona** DOI) | the citable LaTeX/CSV register + pre-reg + Zenodo DOI + claims policy; byte-identical re-run from the manifest | **SERVED** — incl. the persona-MUST DC-31 |
| **P-mlnlp-researcher** (ML/NLP Privacy Researcher) | rank PII systems on v2.0.0 over a right-sized seeded sample with a CI on every number | DC-17/18 (powered sampler + PowerMatrix), DC-21 (engine+convergence), DC-22 (audited CIs+paired+Holm), DC-26 (tie-gated leaderboard) | the powered sample + the honest tie-gated leaderboard with a CI + paired verdict on every claim | **SERVED** — the primary workflow consumer; every spine stage |
| **P-tool-builder** (Privacy-Tool Builder / OSS Maintainer) | an external reproducible CI/publication harness | DC-16 (seam fix — the tool literally cannot read v2.0.0 today), DC-20 (smoke fast-CI), DC-22 (audited stats) | the reconciled v2.0.0 seam + 5-tuple contract + the smoke preset (CI on-ramp, statistically inert) | **SERVED** — the correctness unlock + the DX on-ramp |

**MEDIUM (T2/T3) personas — served (SHOULD/persona-stratified), with the honest first-contact / unseated caveats carried (NOT silently resolved):**
- **P-priveng (T2):** DC-25 (observability), DC-27 (operating-point / false-positive tax — **MUST-for-this-persona**). *Caveat: P-priv-eng was UNSEATED at R6; FR-048/DC-27 is the highest-priority Pass-2 re-elicitation.*
- **P-dpo (T2):** DC-23 (anon/pseudo separation), DC-27, DC-30 (regulatory crosswalk). *Caveat: the DPO/assurance lens is FIRST-CONTACT (INT-05); DC-25/30 trace to a single un-re-confirmed lens → Pass-2.*
- **P-tool-vendor (T3, forcing function):** DC-29 (hygiene), DC-24, DC-31. **P-complreviewer (T3):** DC-24, DC-25 (Art-11 floor), DC-28, DC-29.

**Audit 3 verdict: PASS — all 3 HIGH personas served at every layer they care about (incl. both persona-MUST carve-outs: DC-31 for P-acad-deid, DC-27 for P-priv-eng); all MEDIUM personas served with their first-contact/unseated caveats explicitly carried to Pass-2, not silently resolved.**

---

## 15. Unresolved tensions (carried honestly, not hidden)

| # | Tension | Status / disposition |
|---|---|---|
| **UT-1** | **pii-rate-elo is NOT populated on this machine** — every consumer line number (significance.py:90/:409, cli.py:33/240/242, converter L93/221/222/82, schema.py L137/349/583/627, engine/convergence/metrics_bridge symbols) is carried from Discovery. | **The single biggest implementation risk.** S8 story 0 is "re-confirm against a checkout before any edit." The design is **structured to be robust to drift** (the §9 gate asserts the *module is unreachable* regardless of its internal line numbers; the §10 fix is metadata-provenance pins the contract test pins by value not by line). If the checkout differs materially (e.g. the eager `:409` instantiation is gone), SP-A3 relaxes from module-level to symbol-level — note it in the S8 decision record. |
| **UT-2** | **High-stakes UX commitment: non-interactive batch, no per-stage consent** (D2 SP-W4 / D3 SP-U6). | Flagged for **Pass-2 cognitive walkthrough with a real single-operator research user.** Defensible from NFR-019/033/034 (default + smoke MUST run unattended in CI), but never validated with a real operator. The design adds **no `--yes` escape hatch** (it isn't needed); reversal would mean adding per-stage cards (D2 Frame C, rejected). |
| **UT-3** | **FR-048 / DC-27 (operating-point) priority is COULD-overall but MUST-for-P-priv-eng, and P-priv-eng was unseated at R6.** | DC-27 is **built** (not deferred) but is the **highest-priority Pass-2 re-elicitation** with a real privacy-engineer seat. If Pass-2 re-seats the persona, FR-048 likely re-promotes to MUST — a priority change, not a design change (the DC already exists). |
| **UT-4** | **The DPO / assurance lens (DC-25/30, FR-045/046/050/052/053) is FIRST-CONTACT** (a single un-re-confirmed INT-05 lens). | The 6-stage provenance floor and the crosswalk are **authored** (R7 AUTHOR-not-defer for DC-30), but real-user DPO validation is a **named Pass-2 must.** Carried, not resolved. |
| **UT-5** | **`small_n_cutoff=15`, `β=2`, `recall_target=0.90`, `MIN_SEEDS=3` are R10-DIRECTIONAL** (no canonical integer; `real_user_needed: true`). | These are now **frozen INTO the manifest + pre-reg hashed payload** (`repro.ut5_integers` + `design_and_analysis_plan.ut5_integers`; per repro-02 — not merely adjacent), so a re-run on changed integers cannot diverge under an unchanged fingerprint, AND a Pass-2 reviewer can change them deliberately without touching the audited stats. `n_boot=10000` is likewise pre-registered (stat-06). The *contract* (deterministic, recorded-in-hash, boundary-clause firm) is locked; only the integers await a real ACL/PETS/de-id reviewer. |
| **UT-6** | **Real-data correlation slice (cycle-1 UC-13, vs i2b2-2014/TAB)** — the strongest credibility unlock — is out-of-band / DUA-gated / explicitly NOT v0.1-blocking. | Surfaced only as the DC-28 `correlation-study: named-and-pending` honesty flag. The synthetic-only ceiling (7–8) is acknowledged, not papered over. Roadmap. |
| **UT-7** | **NFR-010b throughput floor (≥5000 rec/sec, 8-core ref host)** inherited from cycle-1 stays **INSUFFICIENT_EVIDENCE** (the agent sandbox is not the reference host). | CAP-02 does **not** re-pin it; the run-record `provenance.canonical_verdict` carries `INSUFFICIENT_EVIDENCE` honestly. Needs an out-of-band reference-host run. |

---

## 16. What this hands to Stage 4 (Development)

A complete, implementation-ready design: **16 DCs (DC-16…31)** mapped 1:1 to the spine and the L6 module map; **the concrete module/file plan for both repos** + the L1 seam contract + the one-way dependency rule; **five finalized schemas** (sample-manifest, 6-stage run-record reusing `benchmark_throughput`, pre-registration, `configs/assessment.yaml` incl. `run_significance_tests:false`, the report/leaderboard register); **the seeded stratified-covering sampler algorithm** (§7) reusing `load_dataset`-adjacent `lattice_audit` + `power` + `reservoir_sample`; **the audited-stats wiring** (§8) + **the canonical P1 import-boundary gate** (§9); **the v2.0.0 seam fix + 5-tuple regression contract** (§10); **a build sequence S8–S12** gated by P1-first; and **three passing audits** (requirements-traceability 0-orphan, axiom-saturation, persona-service) with **seven honestly-carried unresolved tensions** (UT-1 the load-bearing one).

✅ **D6 SYNTHESIS complete (2026-06-01).** Integrated the 5 preferred diamonds (D1 Frame C / D2 Frame A / D3 Frame A / D4 Frame B / D5 Frame A). All eval-data reuse APIs re-verified firsthand this session (lattice `--check` 730 green; Holm verified absent → net-new; the `benchmark_throughput` RUNRECORD pattern read in full). pii-rate-elo side carried from Discovery (repo not populated locally — UT-1). `provisional_status: AGENT_SIMULATED`; Pass-2 commitments named (UT-2/3/4/6). No-regression rails honored (730@`47c3a8f`, NFR-018 gate ON, doc-drift 0, four families separate, no corpus regen, pii-rate-elo consumed not rebuilt). Ready for Stage 4 (Development).
