# CAP-02 — D1 CONVERGE: Preferred Design-Case set (DC-16+)

**Capability**: CAP-02 — academically-sound, repeatable, reportable assessment **workflow** that runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 / CC0 / `annotations`** over a **powered, lattice-stratified sample (default)** / **full corpus (opt-in, citable)** / **smoke (fast CI)**, with statistical/epistemic observability + reporting at every spine stage `load → sample → run → score → rate → report`.
**Stage**: assessment-workflow / 03-Design · **Diamond 1 (Design Cases) — CONVERGE**
**Date**: 2026-06-01
**provisional_status**: AGENT_SIMULATED — the persona/PGO/UC/interview chain these DCs trace to is agent-simulated single-session research; the *code/version/line evidence* (reuse APIs, fabrication signatures, drift pins) is direct file-read at HEAD on 2026-06-01 in `pii-anon-eval-data` (the `pii-rate-elo` lines from Discovery file-reads). Real-user validation is a Pass-2 follow-up.

> **Vocabulary remap.** DC = **Benchmark Component**; FR = Benchmark/Assessment Capability; UC = Evaluation Scenario; NFR = Quality Attribute; AX = binding axiom; Persona = assessment consumer.

> **ID discipline (load-bearing).** Cycle-1 ended at **DC-15** (`03-design/06-synthesis/D-implementation-ready-design.md`). CAP-02 DCs are **DC-16 …**, global numbering continued, **never renumbered or reused**.

> **Locked architecture every DC honors.** eval-data **OWNS** sampling + observability + reporting; `pii-rate-elo` **CONSUMES** (extend, do **NOT** rebuild the engine / metrics / convergence). Cycle-1 hybrid held for consistency: **Modular system + Hexagonal scoring core (Clean inside `stats`) + Linear-batch data-prep + Minimalist-CLI / Info-Dense-reports**; a11y **N/A** (library + CLI, no web UI).

---

## 1. The three lens proposals (DIVERGE recap)

| Frame | Lens | DC count | Range | Signature move |
|---|---|---|---|---|
| **A** | **JTBD-led** — group by the underlying job a consumer "hires" | 13 | DC-16…28 | Surfaces P1/P2/P3 as the *enabling jobs*; distributes AX-005's 6 elements across the jobs they serve; adds a synthetic **DC-28 "frozen-guardrail gate"** (no FR) |
| **B** | **Persona-led** — group by which consumer's entry-point a component serves | 12 | DC-16…27 | Persona-stratified priority (HIGH=MUST spine; MEDIUM=SHOULD/COULD); names each DC's OWNS vs CONSUMES seam; AX-005 asserted per-DC |
| **C** | **Workflow-arc-led** — group by spine stage + the two cross-cutting spines (observability, governance) | 16 | DC-16…31 | 1:1 with the `load→…→report` spine **and** with the LOCKED module placement (L6) + two CLI entrypoints (L3); splits SAMPLE into 3 + REPORT into 3 |

All three: continue global numbering DC-16+, claim **0 orphan FRs/NFRs**, inherit `AGENT_SIMULATED`, and respect the no-regression guardrails.

---

## 2. Pugh comparison (weighted criteria from the brief)

**Datum** = Frame B (Persona-led) — the brief's middle proposal and the only one with no synthetic non-FR DC, so it is the conservative baseline. Scores: **+1** better than datum / **0** equal / **−1** worse. Weights are the brief's five named criteria (normalized to sum 1.00); the design-stage emphasis weights **spine alignment** and **reuse** highest because D1 feeds D2 (Workflow) + D4 (System) + D5 (Architecture), which are organized by the spine and by the reused module map.

| Criterion | Weight | A (JTBD) | B (Persona) = datum | C (Workflow-arc) |
|---|---:|:---:|:---:|:---:|
| **Requirements coverage** (all 25 FR + 37 NFR land; 0 orphan; R7 priority honored) | 0.20 | 0 | **0 (datum)** | **+1** |
| **Cohesion / coupling** (each DC = one buildable/testable seam; low cross-DC chatter) | 0.20 | 0 | **0 (datum)** | **+1** |
| **Traceability to UC/FR/NFR** (clean DC→FR→UC→PGO + axiom-saturation legibility) | 0.20 | **+1** | **0 (datum)** | 0 |
| **Alignment with the `load→…→report` spine** (the capability IS the pipeline) | 0.25 | −1 | **0 (datum)** | **+1** |
| **Reuse of eval-data modules** (DC names map to the LOCKED L6 module placement + the verified reuse APIs) | 0.15 | 0 | **0 (datum)** | **+1** |
| **Weighted total** | 1.00 | **−0.05** | **0.00** | **+0.85** |

### Score rationale (per criterion)

- **Requirements coverage — C +1.** All three reach 0 orphans, but only **C maps 1:1 to the FR family map** in `functional-requirements.md` §"FR family map" (A. seam / B. sampler+manifest / C. presets / D. run path / E. pre-reg / F. observability / G. reporting / H. governance / I. citation). That family map IS the workflow-arc, so C inherits the requirements doc's own grouping and the R8 traceability-matrix §7 brief-coverage rows land on C's DCs without reshuffling. A and B both re-cluster across the family map, which forces a re-derivation of coverage (correct, but lossy at the seams). **C honors the R7 priority drift cleanly** (FR-043/045/048 demotions stay localized to single DCs); B's persona-stratified priority is *expressive* of the drift but over-claims MUST in two bundles (see switch-points).
- **Cohesion / coupling — C +1.** C's split of SAMPLE into **sampler (FR-032) / PowerMatrix (FR-033) / manifest (FR-034)** and the deliberate **non-split of the audited-stats core (FR-040/041/042 as ONE DC)** match the real build seams: the manifest is the L1 SEAM artifact (its own contract), and the P1 quarantine + audited stats are "one indivisible integrity surface — splitting risks a reachable fabricated path" (C's own switch-point, and the correct call). A's DC-21 bundles 8 NFRs + 4 FRs across RUN/SCORE/RATE into one "rank systems" job — high internal coupling, hard to test as one unit. B's DC-18 fuses FR-040/041/042 (good) but its DC-17 fuses sampler+PowerMatrix+manifest into one DC (couples the SEAM artifact to the sampler internals).
- **Traceability — A +1.** This is A's genuine strength: grouping by JTBD makes the *axiom-saturation* and *persona-need* story most legible (each DC narrates "the job → the axiom it saturates"). B is equal-to-datum. C is 0 (equal): the spine grouping is trivially traceable FR→DC, but axiom-saturation is spread across stages (AX-005 touches 7 of C's DCs) — no worse than A/B, which also spread AX-005, but no better.
- **Spine alignment — C +1, A −1.** The brief's CONVERGE criterion names "alignment with the `load→…→report` spine" explicitly, and D2 (Workflow) is organized *by that spine*. C is the spine. **A actively cuts across it** ("Grouping by underlying job, not spine stage" — A's own frame rationale) — defensible for Discovery, but it fights the next diamond. B is neutral (persona entry-points partially track the spine).
- **Reuse of eval-data modules — C +1.** Only C's DC titles map 1:1 onto the **LOCKED L6 module placement** (`assessment/{sample, manifest, runrecord, prereg, report, verdicts}.py`) and the verified reuse APIs in `_engineering-findings-verified.md §3`. This is the criterion that most directly de-risks D4/D5: a DC set whose boundaries already match the module boundaries means the System/Architecture diamonds inherit the partition. A/B require a re-projection from job/persona onto modules.

**Pugh verdict: Frame C (Workflow-arc-led) is preferred (+0.85).** It is not unanimous on every axis — A wins traceability/axiom-narrative — so the preferred set **adopts C's spine partition and absorbs A's two best switch-points** (the JTBD axiom-saturation narration per DC, and A's explicit "gate" concern) plus **B's persona-ownership annotation** (each DC names its owning persona-tier so the persona-service audit in D6 has a hook). The result is C's 16 DCs, enriched, not a 4th frame.

---

## 3. Switch-points (named, per the brief)

The following are the decision forks where a *different* frame would have produced a *different* DC boundary. Each is resolved here and flagged for the downstream diamonds.

| # | Switch-point | Frames in tension | Resolution (locked for D2–D5) |
|---|---|---|---|
| **SP-1** | **Merge the SAMPLE trio** (sampler + PowerMatrix + manifest) into one DC vs keep 3 | C-split (DC-17/18/19) vs B/A-merged (one SAMPLE DC) | **KEEP SPLIT.** The manifest is the **L1 SEAM** artifact (`pii-rate-elo` consumes it; eval-data emits it) — it has its own contract, schema, and non-strippable-caveat invariant, distinct from the sampler algorithm and the PowerMatrix verdict logic. Splitting matches the P3 three-artifact separation and the `subsets/slices.py` + `stats/power.py` + `write_manifest.py` reuse boundaries. |
| **SP-2** | **Split the audited-stats core** into stats-vs-quarantine vs keep as ONE DC | C-merged (DC-22) vs a hypothetical split | **KEEP MERGED (one DC).** The audited stats (FR-040/041) and the P1 quarantine (FR-042) are **one indivisible integrity surface** — the quarantine assertion (`significance.py` unreachable) is only meaningful *because* the audited path is the one taken. Splitting them risks a design where the fabricated path is reachable between the two DCs. This is the SHOWSTOPPER (P1); it gets one cohesive DC. |
| **SP-3** | **Synthetic "frozen-guardrail gate" DC** (no FR) vs dissolve into per-DC acceptance criteria | A-has-it (A's DC-28) vs B/C-don't | **DISSOLVE — but keep the gate as a CROSS-CUTTING constraint, NOT a DC.** A's instinct (don't silently regress cycle-1) is right, but a DC with no FR is not a Benchmark Component. The no-regression NFRs (**NFR-052/053/054/055** + the engineering gates **NFR-050/051**) are attached to their nearest spine DC AND recorded as a **panel-wide CI-gate constraint** in §5. This preserves A's concern without minting a non-component. |
| **SP-4** | **Fold crosswalk + release** (FR-053/054) into the report DC vs keep as standalone X-stage DCs | C-folds-into-report? vs standalone | **KEEP STANDALONE (DC-30, DC-31).** The regulatory crosswalk (FR-053, AUTHOR-not-defer) and the DOI/citation release (FR-054) are **versioned artifacts with their own update cadence** (the crosswalk outlives any single run; the DOI is a release-layer act). Folding them into the report DC would couple a per-run artifact to cross-run artifacts. They are X-stage (cross-cutting) DCs, persona-stratified (DPO / acad-deid). |
| **SP-5** | **AX-005 localization** — spread across 7 DCs vs localize to run/report | (cross-cutting in all 3) | **SPREAD (accept the cross-cut).** AX-005 is a cross-cutting *invariant*, not a component — it correctly saturates DC-19/22/23/24/25/28/29. The axiom-saturation audit (D6) tracks it as a matrix, not a DC. This is the one place all three frames agree, and the preferred set keeps it. |
| **SP-6** | **Operating-point view** (FR-048) as its own DC vs folded into report | C-standalone (DC-27) vs folded | **KEEP STANDALONE (DC-27), priority COULD-overall / MUST-for-P-priv-eng.** Per R7, FR-048 is the bundle most distorted by the sampling gap (3 MEDIUM personas unseated at R6); isolating it as its own DC makes the Pass-2 re-elicitation surgical and keeps the MUST report spine (DC-26/28) independent of it. |

---

## 4. The preferred Design-Case set (DC-16 … DC-31) — LOCKED

**16 DCs**, one per spine stage plus the two cross-cutting spines (observability, governance) and the release/crosswalk X-stage artifacts. Each row: **DC → bundled FR/NFR → spine stage → reused eval-data / pii-rate-elo modules → owning persona-tier → axioms saturated → R7 priority**.

Priorities reflect the **R7-committed** classes from `traceability-matrix.md §8` (FR-043 SHOULD w/ NR-core MUST via NFR-055; FR-045 SHOULD w/ 6-stage floor assurance-MUST; FR-048 COULD-overall/MUST-for-P-priv-eng; FR-053 SHOULD AUTHOR-not-defer; FR-054 SHOULD/MUST-for-P-acad-deid).

### LOAD

#### DC-16 — Dataset-seam reconciliation + regression contract (v2.0.0)
- **FR:** FR-030, FR-031 · **NFR:** NFR-040, NFR-041, NFR-054
- **Spine:** LOAD · **Precondition:** **P2** (CATASTROPHIC-as-wired)
- **Reused modules:** `pii-rate-elo` `datasets/converters/pii_anon_eval.py` (fix `num_records` L93 / `license` L221 / `citation` L222) + `schema.py` (`version` L137; `_normalize_eval_row` L349 annotations-fallback preserved); eval-data `scripts/_version.py` (`DATASET_VERSION`/`get_version`), `scripts/write_manifest.py` (`hashlib` content hash), `tests/test_doc_drift.py` canonical pins, `taxonomy.ENTITY_TYPE_COUNT` (63, derived). **L4 LOADER STRATEGY decision deferred to D4/D5** (prefer fixing the bundled parser + regression contract; reserve `load_dataset` import for the sampler side).
- **Owning persona-tier:** P-tool-builder (T1) [owner]; foundational to all T1.
- **Axioms:** none directly (correctness precondition; enables AX-002/003/004 downstream).
- **Priority:** **MUST.**

### SAMPLE

#### DC-17 — Powered, lattice-stratified, seeded sampler
- **FR:** FR-032 · **NFR:** NFR-035, NFR-038, NFR-039, NFR-053
- **Spine:** SAMPLE · **Precondition:** **P3**
- **Reused modules:** eval-data `stats/power.py` (`required_n`, `TIER_SPECS` 1522/753/200, `classify`, `pick_tier`, `Tier`), `stats/lattice.py` (`build_committed_lattice`/`load_lattice`, `--check`=730 @ `47c3a8f`), `scripts/lattice_audit.py` (`committed_index`, `audit_positives`, `deficits` — streaming realized counts), `subsets/slices.py`, `scripts/benchmark_throughput.py::reservoir_sample` (Algorithm-R, seeded `SEED_BENCHMARK`).
- **Owning persona-tier:** P-mlnlp-researcher (T1) [owner]; P-acad-deid (T1); P-priveng (T2).
- **Axioms:** AX-pii-anon-002 (seeded/single-pass deterministic), AX-pii-anon-003 (tiered targets derived, never hand-typed).
- **Priority:** **MUST.**

#### DC-18 — PowerMatrix verdict + per-cell realized-positive shortfall
- **FR:** FR-033 · **NFR:** NFR-035, NFR-036, NFR-037
- **Spine:** SAMPLE · **Precondition:** **P3** (the honest UNDER-POWERED path — the study's strongest delight)
- **Reused modules:** eval-data `stats/power.py` (`PowerMatrix.verdict()` SMALL/ADEQUATE/LARGE @ 0.80/0.999 L351-361, `CellAudit` n/target_n/shortfall/power_class, `classify`); the UNDER_SAMPLED-vs-CORPUS_LIMITED 4th state extends the 3-state `classify` by comparing sample realized `n` to **full-corpus** realized positives via `scripts/lattice_audit.py::audit_positives`.
- **Owning persona-tier:** P-mlnlp-researcher (T1) [owner]; P-acad-deid (T1).
- **Axioms:** AX-pii-anon-003.
- **Priority:** **MUST.**

#### DC-19 — Reproducible sample manifest (the L1 SEAM artifact) + non-strippable caveat
- **FR:** FR-034 · **NFR:** NFR-030, NFR-039
- **Spine:** SAMPLE/X · **The L1 SEAM** (`pii-rate-elo` reads this; eval-data emits it)
- **Reused modules:** eval-data `scripts/write_manifest.py` (deterministic sha256, canonical-form equality), `subsets/slices.py::SLICE_CAVEAT` + `Slice.__post_init__` (raises on empty caveat → non-strippable), `scoring/detection.py::DesignProvenance`.
- **Owning persona-tier:** P-acad-deid (T1, byte-for-byte reproducibility) [owner].
- **Axioms:** AX-pii-anon-002 (canonical-form-equal re-run), AX-pii-anon-001 (non-strippable synthetic-only caveat seed).
- **Priority:** **MUST.**

### SAMPLE / RUN

#### DC-20 — Preset trio + run-type → rigor-bar profile
- **FR:** FR-035, FR-036, FR-037, FR-038 · **NFR:** NFR-025, NFR-033, NFR-034
- **Spine:** SAMPLE/RUN · The **L3** user-facing surface (selects the DC-17 sample + the DC-21 run + the DC-23 pre-reg gate)
- **Reused modules:** `pii-rate-elo` `cli.py` (Typer — extend, consume sample mode; do not rebuild), `config.py::PipelineConfig.from_yaml`; eval-data `scripts/benchmark_throughput.py::build_run_record`; version-pinned `record_count` from the DC-16 reconciled loader (FR-036 `records_scored == dataset.record_count(version)`, never literal `575604`); non-strippable-caveat + suppression patterns from `subsets/slices.py` (smoke).
- **Owning persona-tier:** P-acad-deid (T1, full-corpus citable) + P-tool-builder (T1, smoke) [co-owners]; P-mlnlp-researcher (T1, default).
- **Axioms:** AX-pii-anon-002, AX-pii-anon-005 (enforcement scope via run-type binding).
- **Priority:** **MUST** (FR-036/037 SHOULD; the run-type mechanism FR-038 is MUST).

### RUN / RATE

#### DC-21 — Thin assessment orchestrator: engine + Glicko convergence (consume, no rebuild)
- **FR:** FR-039 · **NFR:** NFR-029 (convergence verdict source), NFR-051
- **Spine:** RUN/RATE · The **L2** thin orchestrator (load manifest → run engine + convergence → hand outcomes to `assessment.report`)
- **Reused modules:** `pii-rate-elo` `tournament/engine.py::PIIRateEloEngine`, `tournament/convergence.py::ConvergenceChecker` (Glicko RD, default threshold 100), `tournament/organizer.py`, `evaluation/metrics_bridge.py::compute_span_metrics` (declared `span_match_mode ∈ {exact, relaxed-overlap}`) — **all consumed, none re-implemented**; `config.py`, `cli.py`.
- **Owning persona-tier:** P-mlnlp-researcher (T1) [owner]; P-tool-builder (T1); P-acad-deid (T1).
- **Axioms:** AX-pii-anon-005 (element 3, convergence), AX-pii-anon-002.
- **Priority:** **MUST.**

#### DC-22 — Audited statistics core: CIs + paired tests + Holm (P1 quarantine) **[SHOWSTOPPER]**
- **FR:** FR-040, FR-041, FR-042 · **NFR:** NFR-019, NFR-020, NFR-021, NFR-022, NFR-023, NFR-024, NFR-026, NFR-027, NFR-050
- **Spine:** SCORE/RATE · **Precondition:** **P1** (the unanimous walk-away trigger; one indivisible integrity surface — SP-2)
- **Reused modules:** eval-data `stats/intervals.py` (`wilson_interval`, `clopper_pearson_interval`, integer-guard `_require_int_counts` L39-51), `stats/paired.py` (`mcnemar_exact`, `mcnemar_chi2(continuity=True)`, `paired_bootstrap_recall_delta` seeded LOCAL `random.Random(seed)` L140); **Holm–Bonferroni is the one net-new primitive** → added to audited `stats/` (NOT to the quarantined `significance.py`). Quarantine targets `pii-rate-elo` `analysis/significance.py::SignificanceTester` (fabricated `se=metric*(1-metric)/100`+`np.random.normal` L205-206; `n_approx=100`/`pooled_sd=0.1`/`z=…/0.05` L271-281; instantiated `cli.py:242` behind `run_significance_tests` `cli.py:240`) → set `run_significance_tests:false` + import-graph guard + fabrication-regex lint.
- **Owning persona-tier:** P-mlnlp-researcher (T1) [owner]; P-acad-deid (T1); P-tool-builder (T1).
- **Axioms:** AX-pii-anon-002, AX-pii-anon-003, AX-pii-anon-005 (elements 1, 2).
- **Priority:** **MUST** (SHOWSTOPPER).

### SCORE

#### DC-23 — Scoring-family separation (anon/pseudo) + contamination + seed-variance scope
- **FR:** FR-043 · **NFR:** NFR-045, NFR-048, NFR-055
- **Spine:** SCORE
- **Reused modules:** four-metric-families-never-merged guardrail (cycle-1 NFR-005 static check, extended by NFR-055); `scoring_family ∈ {anonymization, pseudonymization}` declaration; new run-record fields `contamination_status` (+ `contamination-uncontrolled` propagation when `unknown`) and `seed_variance_scope` (multi-seed `len(seeds) ≥ MIN_SEEDS=3` + Kendall-τ, or `single-seed` → `rank-volatility: UNMEASURED`).
- **Owning persona-tier:** P-mlnlp-researcher (T1) [owner]; P-tool-builder (T1); P-dpo (T2, separation).
- **Axioms:** AX-pii-anon-004 (separate families, never merged), AX-pii-anon-005.
- **Priority:** **SHOULD** (R7 demotion; **NR-core "four families never merged" stays MUST via NFR-055 / G-norg**; reversible at Pass-2).

### X / REPORT (pre-registration)

#### DC-24 — Pre-registration: git-anchored + hash-chained
- **FR:** FR-044 · **NFR:** NFR-031, NFR-032
- **Spine:** X/REPORT (after `sample`, before first score) · Scopes the rigor of DC-22/DC-28
- **Reused modules:** eval-data `scripts/write_manifest.py` hashing; chained into the DC-25 run-record; commit-on-remote oracle `git branch -r --contains <sha>`; immutable payload pinning {version, manifest hash, seed, systems, metrics, RD stopping rule, interval rule, multiplicity family+size, power design point, span-match mode, scoring family, tie/exclusion rules}; run-lineage count.
- **Owning persona-tier:** P-acad-deid (T1) [owner]; P-complreviewer (T3), P-tool-vendor (T3).
- **Axioms:** AX-pii-anon-002, AX-pii-anon-005 (element 4).
- **Priority:** **MUST** (mechanism MUST; enforcement opt-in/run-type-scoped per DC-20).

### X (observability — all stages)

#### DC-25 — Per-stage observability run-records + file-level provenance
- **FR:** FR-045, FR-046 · **NFR:** NFR-042, NFR-043
- **Spine:** X (cross-cuts all 6 stages) · The **L5** observability spine (one record per stage, shared run id)
- **Reused modules:** eval-data `scripts/benchmark_throughput.py` RUNRECORD pattern (schema id, harness_version, injectable timestamp, seed, host, provenance {is_reference_host, environment, canonical_verdict}) extended per-stage; `scripts/write_manifest.py` (per-file sha256). Surfaces the DC-16 regression-contract 5-tuple as run-record fields. 6 stage records {load, sample, run, score, rate, report}, each `{dataset_version, record_count, schema_fingerprint, seed, stage, code_commit}` + toolchain; file-level `{content_hash, code_commit, run_id, stage}` on every artifact.
- **Owning persona-tier:** P-priveng (T2) [owner]; P-complreviewer (T3, Art-11 filing). **FIRST-CONTACT assurance lens (Pass-2 caveat).**
- **Axioms:** AX-pii-anon-002, AX-pii-anon-005 (element 4).
- **Priority:** **SHOULD** (R7; **the 6-stage provenance floor is the assurance-MUST sub-part**, D4; reversible at Pass-2).

### REPORT

#### DC-26 — Honest leaderboard: paired-test-gated ranks + AX-004 separate families + artifact-first register
- **FR:** FR-047 · **NFR:** NFR-028, NFR-044
- **Spine:** REPORT (the deliverable)
- **Reused modules:** eval-data reporting layer (`assessment.report`) computing CIs + tie-gating from `stats/paired.py` (non-significant pairs greyed post-Holm), `convergence.py` verdict; anon/pseudo in separate families (AX-004); artifact-first LaTeX tabular + CSV register (forbidden product-verdict tokens `{SHIP-WITH-CAVEATS, SHIP, DEFER, GO/NO-GO}` banned by scan).
- **Owning persona-tier:** P-mlnlp-researcher (T1) [owner]; P-acad-deid (T1); P-dpo/P-complreviewer (T2/T3).
- **Axioms:** AX-pii-anon-001, AX-pii-anon-004, AX-pii-anon-005 (element 2).
- **Priority:** **MUST.**

#### DC-27 — Operating-point reporting (recall-priority Fβ / FN:FP cost + AUPRC) [false-positive tax]
- **FR:** FR-048 · **NFR:** NFR-046
- **Spine:** REPORT (renders into the DC-26/28 surface)
- **Reused modules:** `pii-rate-elo` `evaluation/metrics_bridge.py` extended for recall-priority Fβ (β≥2 recorded) / stated integer FN:FP cost + threshold-free AUPRC at the pre-registered operating point (FR-044) + precision-at-fixed-recall (recall target recorded).
- **Owning persona-tier:** P-priveng (T2) [owner]; P-dpo (T2).
- **Axioms:** AX-pii-anon-005.
- **Priority:** **COULD-overall / MUST-for-P-priv-eng** (R7; the bundle most distorted by the sampling gap — **highest-priority Pass-2 re-elicitation**, D5).

#### DC-28 — Non-strippable honesty-flag bundle + RD-convergence + self-verifying report
- **FR:** FR-049, FR-050 · **NFR:** NFR-029, NFR-047
- **Spine:** REPORT/X (terminal spine DC)
- **Reused modules:** eval-data `scoring/detection.py::DesignProvenance` (raises on empty caveat; carries caveat through serializers); `pii-rate-elo` `convergence.py` (`is_converged`, `max_rd`, `rd_threshold` → reported as achieved max-RD ± 2RD + rounds, NOT-CONVERGED as blocking flag). Closed honesty set: synthetic-only caveat / convergence block / per-cell power_class flags (DC-18) / contamination-uncontrolled (DC-23) / rank-volatility scope (DC-23) / worst-language recall (argmin+label) / low-resource (<200-positive set) recall / named-and-pending correlation flag; self-verifying report embeds {pre-reg hash, commit SHA, run id} + Art-11 alignment label.
- **Owning persona-tier:** P-complreviewer (T3) + P-dpo (T2) [owners]; P-mlnlp-researcher (T1); P-acad-deid (T1).
- **Axioms:** AX-pii-anon-001, AX-pii-anon-003, AX-pii-anon-005 (elements 3, 4, 5).
- **Priority:** **MUST.**

### X (governance / anti-gaming)

#### DC-29 — Leaderboard hygiene + neutrality/recusal governance
- **FR:** FR-051, FR-052 · **NFR:** NFR-048, NFR-049
- **Spine:** X · Extends cycle-1 FR-023/026 + NFR-014 at the workflow layer
- **Reused modules:** run-record (DC-25) extended with submission-provenance fields; scoring-API-surface oracle (held-out labels never returned); `contamination_status` source (DC-23) with `unknown` rejected + signed held-out-non-exposure attestation `{submitter_id, statement, signature, signed_at}`; governance block `{corpus_owner, label_holder, evaluator}` per report page + computable recusal record.
- **Owning persona-tier:** P-tool-vendor (T3, forcing function) [owner]; P-complreviewer (T3); P-priveng (T2).
- **Axioms:** AX-pii-anon-005 (element 6).
- **Priority:** **MUST** (FR-052 SHOULD).

#### DC-30 — Regulatory taxonomy crosswalk (63 types → GDPR / HIPAA / CCPA / GLBA)
- **FR:** FR-053 · **NFR:** — (AX-004 linkage)
- **Spine:** X · Extends cycle-1 FR-022 to the v2.0.0 63-type vocabulary · Feeds DC-26/28 report
- **Reused modules:** the 63-type vocabulary from the DC-16 reconciled seam (`taxonomy.ENTITY_TYPE_COUNT`); a versioned, provenance-stamped, updateable crosswalk artifact, legally distinct per regime at the display layer (no cross-regime equivalence).
- **Owning persona-tier:** P-dpo (T2) [owner]; P-priveng (T2). **FIRST-CONTACT DPO lens (Pass-2 caveat).**
- **Axioms:** AX-pii-anon-004 (legally-distinct families).
- **Priority:** **SHOULD, AUTHOR-not-defer** (R7; resolves Open Item 10; D8).

### X (citation / release)

#### DC-31 — Citable / DOI-able release + claims policy
- **FR:** FR-054 · **NFR:** — (AX-001/003 linkage)
- **Spine:** X (terminal release; what DC-28 produces is what's released) · Mirrors cycle-1 FR-028
- **Reused modules:** minted persistent identifier (Zenodo DOI or equivalent, not only a git SHA) + BibTeX + recommended citation template + synthetic-only claims policy (the AX-001/003 ceiling caveat from `DesignProvenance`).
- **Owning persona-tier:** P-acad-deid (T1) [owner — MUST-for-this-persona]; P-tool-vendor (T3).
- **Axioms:** AX-pii-anon-001 (claims-policy ceiling caveat).
- **Priority:** **SHOULD, MUST-for-P-acad-deid** (R7; a Zenodo DOI is a hard citation gate for the academic cohort, silent elsewhere; D9).

---

## 5. Cross-cutting CI-gate constraints (the dissolved SP-3 "gate" — NOT a DC)

These no-regression / engineering NFRs are **panel-wide constraints** every DC's acceptance criteria inherit (resolving SP-3 without minting a non-component DC). They are enforced as **blocking CI gates**, attached to their nearest spine DC for ownership:

| Constraint (NFR) | What it pins | Nearest-DC owner | Enforced as |
|---|---|---|---|
| **NFR-050** | Pure-stdlib statistical cores + lazy heavy-dep guards (numpy/matplotlib lazy-imported only in figure code) | DC-22 | import-graph CI gate (cores import no 3rd-party numeric lib) |
| **NFR-051** | `pii-rate-elo` consumer gates green (pytest + ruff + mypy) | DC-21 | the three gates in the `pii-rate-elo-pipeline` venv |
| **NFR-052** | Lattice frozen: **730 cells @ `47c3a8f`** (`lattice --check` green) | DC-17 | `python -m pii_anon_datasets.stats.lattice --check` round-trip |
| **NFR-053** | NFR-018 committed-lattice power gate stays ON (`validate.py --lattice` exits non-zero on shortfall) | DC-17 | `validate.py --lattice` green + re-enable-if-disabled test |
| **NFR-054** | Documentation drift = 0 (575,604 / 2,486,438 / 63 / 2.0.0 identical across docs; NFR-013 green) | DC-16 | `pytest -k nfr_013` (`test_doc_drift.py`) |
| **NFR-055** | Four metric families never merged (NFR-005 invariant holds across CAP-02) | DC-23 | static check over the CAP-02-added module set |

**Plus the global no-regression rails:** no corpus regeneration; four metric families never merged (AX-004); the L6 PURE-STDLIB cores + lazy heavy-dep guards; `pii-rate-elo` consumed not rebuilt.

---

## 6. Coverage self-check (0 orphans, both directions)

### FR coverage — all 25 FRs (FR-030 … FR-054) bound, 0 orphans
DC-16: FR-030/031 · DC-17: FR-032 · DC-18: FR-033 · DC-19: FR-034 · DC-20: FR-035/036/037/038 · DC-21: FR-039 · DC-22: FR-040/041/042 · DC-23: FR-043 · DC-24: FR-044 · DC-25: FR-045/046 · DC-26: FR-047 · DC-27: FR-048 · DC-28: FR-049/050 · DC-29: FR-051/052 · DC-30: FR-053 · DC-31: FR-054.
**Σ = 25 distinct FRs, each in exactly one DC. 0 orphan FRs.**

### NFR coverage — all 37 NFRs (NFR-019 … NFR-055) bound, 0 orphans
DC-16: NFR-040/041/054 · DC-17: NFR-035/038/039/052/053 · DC-18: NFR-035/036/037 · DC-19: NFR-030/039 · DC-20: NFR-025/033/034 · DC-21: NFR-029/051 · DC-22: NFR-019/020/021/022/023/024/026/027/050 · DC-23: NFR-045/048/055 · DC-24: NFR-031/032 · DC-25: NFR-042/043 · DC-26: NFR-028/044 · DC-27: NFR-046 · DC-28: NFR-029/047 · DC-29: NFR-048/049.
(NFR-035 spans DC-17 sampler-classification + DC-18 verdict; NFR-039 spans DC-17 design-point + DC-19 manifest-write; NFR-029 spans DC-21 verdict-source + DC-28 report-render; NFR-048 spans DC-23 source + DC-29 leaderboard — each is a single quality attribute exercised across the two DCs that jointly satisfy it, not a double-count.) **All 37 NFRs land on ≥1 DC. 0 orphan NFRs.**

### Precondition coverage
- **P1** (SHOWSTOPPER) → **DC-22** (NFR-019/020/021/022 + FR-042 quarantine).
- **P2** → **DC-16** (FR-030/031 + NFR-040/041).
- **P3** → **DC-17 + DC-18 + DC-19** (FR-032/033/034 + NFR-035/036/037/038/039 + NFR-053 power gate).

### Axiom-saturation feasibility (the D6 audit's hooks)
- **AX-001** (synthetic-only) → DC-19, DC-26, DC-28, DC-31 (non-strippable-caveat-by-construction precedent: `DesignProvenance`).
- **AX-002** (deterministic/seeded/byte-reproducible) → DC-17, DC-19, DC-20, DC-21, DC-22, DC-24, DC-25.
- **AX-003** (stated power — n + CI) → DC-17, DC-18, DC-22, DC-28.
- **AX-004** (anon vs pseudo separate families) → DC-23, DC-26, DC-30.
- **AX-005** (pre-registered/reproducible — 6 elements + scope) → DC-19, DC-20, DC-21, DC-22, DC-23, DC-24, DC-25, DC-28, DC-29 (the most cross-cutting; tracked as a matrix in D6, per SP-5).

### Persona-tier coverage (the D6 persona-service audit's hooks)
- **T1 (HIGH):** P-acad-deid → DC-19/20/24/31; P-mlnlp-researcher → DC-17/18/21/22/26; P-tool-builder → DC-16/20/22.
- **T2 (MEDIUM):** P-priveng → DC-25/27; P-dpo → DC-23/27/30.
- **T3 (sub-archetypes):** P-tool-vendor → DC-29/24/31 (forcing function); P-complreviewer → DC-24/25/28/29.

### Orphans / explicitly-scoped-OUT (NOT orphans — documented roadmap)
**0 orphan FRs · 0 orphan NFRs · 0 orphan UCs** (UC-16→DC-17/18/19/20; UC-17→DC-21/22/23; UC-18→DC-24; UC-19→DC-20; UC-20→DC-20; UC-21→DC-16; UC-22→DC-25; UC-23→DC-26/27/28/29/30/31). Scoped-OUT with named hooks: re-id/RRS family (PGO-acaddeid-02/researcher-02/builder-03 → `REID_TIER_SPECS` roadmap); agentic recognition-oracle (PGO-redteam-01/02/03 → cycle-1 UC-08/09); oracle throughput SLA (N-06 → cycle-1 oracle track).

---

## 7. What feeds the next diamond (D2 Workflow)

The locked DC-16…31 set hands D2 a partition that is **already the spine** (`load`=DC-16 → `sample`=DC-17/18/19 → preset/run-type=DC-20 → `run`=DC-21 → `score`/`rate`=DC-22/23 → pre-reg=DC-24 → observability=DC-25 → `report`=DC-26/27/28 → governance/crosswalk/release=DC-29/30/31), and **already the LOCKED module map** (L6): eval-data `src/pii_anon_datasets/assessment/{sample(DC-17/18), manifest(DC-19), runrecord(DC-25), prereg(DC-24), report(DC-26/27/28), verdicts(DC-18 power + DC-28 honesty)}.py`; `pii-rate-elo` `configs/assessment.yaml` + `cli.py assessment` (DC-20/21) + `converters/pii_anon_eval.py` & `schema.py` v2.0.0 fix (DC-16) + a thin assessment adapter (DC-21). The two CLI entrypoints (L3) realize DC-20: (a) eval-data `python -m pii_anon_datasets.assessment.sample --preset … --seed … --out sample-manifest.json`; (b) `pii-rate-elo assessment --sample sample-manifest.json --config configs/assessment.yaml --out results/`.

**Open decisions explicitly carried to D4/D5** (per SO-08): **L4 loader strategy** (DC-16 — prefer fixing the bundled parser + regression contract, reserve `load_dataset` import for the sampler side); sample-manifest schema detail (DC-19); the stratified covering-sampler algorithm internals (DC-17); the observability run-record schema detail (DC-25).

---

✅ **D1 CONVERGE complete (2026-06-01).** Pugh-compared 3 lens frames (A JTBD / B Persona / C Workflow-arc); **Frame C preferred (+0.85)**, enriched with A's axiom-narration + "gate" concern (dissolved per SP-3) + B's persona-ownership annotation. **16 DCs locked (DC-16 … DC-31)**, each → bundled FR/NFR → spine stage → reused modules → owning persona-tier → axioms → R7 priority. **0 orphan FRs (25/25) · 0 orphan NFRs (37/37) · 0 orphan UCs (8/8).** Six switch-points named + resolved. No-regression rails encoded as panel-wide CI gates (SP-3). `provisional_status: AGENT_SIMULATED`. Ready for D2 (Workflow).
