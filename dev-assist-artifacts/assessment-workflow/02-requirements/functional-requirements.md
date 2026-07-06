# CAP-02 Functional Requirements — Benchmark / Assessment Capabilities

**Capability**: CAP-02 — an academically-sound, repeatable, reportable assessment **workflow** that runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0** over a **powered, lattice-stratified sample (default)** / **full corpus (opt-in, citable)** / **smoke (fast CI)**, with epistemic instrumentation + reporting at every spine stage: `load → sample → run systems → score → rate → report`.
**Stage**: assessment-workflow / 02-Requirements · R4 (Functional Requirements authoring)
**Date**: 2026-06-01
**provisional_status**: AGENT_SIMULATED — these FRs are authored from agent-simulated single-session Discovery + R3 interview research; the *code/version/line evidence* they bind to is direct file-read at HEAD on 2026-06-01 in `pii-anon-eval-data` (and the cited `pii-rate-elo` lines are from the Discovery file-reads at HEAD, that repo not being checked out on this machine). Agent-simulated research is **NOT** a substitute for real users; real-user validation of the FRs is a Pass-2 follow-up.

> **Vocabulary remap (project framing — synthetic PII benchmark).** FR = **Benchmark / Assessment Capability**; UC = **Evaluation Scenario**; NFR = **Quality Attribute**; DC = **Benchmark Component**; Persona = assessment consumer. Each FR = a workflow capability with a **boolean-testable Given/When/Then** a CI job can assert true/false.

> **Locked architecture every FR assumes.** `load → sample → run systems → score → rate → report`. **eval-data OWNS** sampling + observability + reporting; **`pii-rate-elo` CONSUMES** — extend it, do **NOT** rebuild the engine / metrics / significance. Where an FR says "wire", it means *call the consumer seam*, not re-implement it.

> **ID discipline (load-bearing).** Cycle-1 ended at **FR-029**. CAP-02 FRs are **FR-030 …** (global numbering continued, never renumbered or reused). NFR IDs (NFR-019+) are authored separately (R4 NFR doc); this doc cross-references the candidate NFR family by descriptive name where an FR's *quality bar* is an NFR's job. Inherited binding axioms **AX-pii-anon-001/002/003/004** still apply; the candidate **AX-pii-anon-005** (pre-registered/reproducible assessment: no published metric without a CI + a paired test + a convergence statement + provenance + the non-strippable synthetic-only caveat) is **proposed here for confirmation** (see §AX-pii-anon-005 below) and the relevant FRs wire to it.

> **Trace contract.** Every FR cites the **UC(s)** it serves; the UC↔PGO bridge (`_bridge/uc-pgo-map.md`) resolves each UC to its PGO(s) → persona → goal. Chain: **persona → PGO → UC → FR**. Discovery anchors cited inline: Open Items 1–13, anti-over-claim rails **G1–G7**, decision-forks **DF-1…DF-5**, concept-value items **C1–C10**, and the R3 net-new candidates **N-01…N-15** (`interview-synthesis.md`).

---

## FR family map (what each group delivers, and the spine stage it binds)

| Group | Spine stage(s) | FRs | Core UC(s) |
|---|---|---|---|
| **A. Dataset seam + load contract** | LOAD | FR-030, FR-031 | UC-21 |
| **B. Powered lattice-stratified sampler + manifest** | SAMPLE | FR-032, FR-033, FR-034 | UC-16 |
| **C. Preset trio + run-type designation** | SAMPLE/RUN | FR-035, FR-036, FR-037, FR-038 | UC-19, UC-20, (UC-16/17 default) |
| **D. Run path: engine + audited stats + quarantine** | RUN/SCORE/RATE | FR-039, FR-040, FR-041, FR-042, FR-043 | UC-17 |
| **E. Pre-registration** | X/REPORT | FR-044 | UC-18 |
| **F. Observability run-records + provenance** | X (all stages) | FR-045, FR-046 | UC-22 |
| **G. Reporting: leaderboard + figures + honest verdicts** | REPORT/X | FR-047, FR-048, FR-049, FR-050 | UC-23 |
| **H. Governance / anti-gaming / compliance crosswalk** | X | FR-051, FR-052, FR-053 | UC-17/18/23 |
| **I. Citation + release** | X | FR-054 | UC-23 (C2) |

**Count: 25 FRs (FR-030 … FR-054).** Priority split (provisional, finalized R7): **19 MUST · 6 SHOULD · 0 COULD**.

---

## A. Dataset seam reconciliation + load contract (LOAD)

### FR-030 — Reconcile the `pii-rate-elo` dataset seam to PII-Anon v2.0.0
- **Serves:** UC-21 · PGO-builder-02 [theme] (foundational to every researcher/builder/acad-deid PGO — nothing downstream is correct until this lands)
- **Priority:** **MUST** (P2 precondition; CATASTROPHIC-as-wired)
- **GIVEN** the consumer dataset seam pins the stale corpus — `datasets/converters/pii_anon_eval.py` `num_records=159891` (L93), `license="CC-BY-4.0"` (L221), `citation="…v1.3.0"` (L222), and `schema.py` `version="1.3.0"` (L137) — while the live artifact is **v2.0.0 / 575,604 / CC0 / `annotations`** (63 entity types, 60 languages, 5 domains),
- **WHEN** the seam is reconciled and the dataset is loaded through `pii-rate-elo`,
- **THEN** the loader reports `version == "2.0.0"`, `license == "CC0-1.0"` (or `"CC0"`), a citation string referencing v2.0.0, AND yields the v2.0.0 record count (575,604 for the full corpus), **resolved from the version-pinned loader, not a literal**; AND the row parser continues to read `annotations`-shaped rows (the `schema.py:349` `annotations`→`labels` fallback is preserved — this FR is metadata-provenance reconciliation, NOT field-reading rework).
- **Boolean test:** load v2.0.0 through the reconciled seam → `(version == "2.0.0") and (license in {"CC0-1.0","CC0"}) and (record_count == dataset.record_count("2.0.0")) and ("2.0.0" in citation) and annotations_rows_parse_ok` → `True`/`False`.
- **Reuse / grounding:** crosswalk delivered via a **versioned artifact** (FR-031); record count resolved via `scripts/_version.py::DATASET_VERSION`/`get_version()` + the loader's `record_count(version)`. Resolves SME finding MEI-04 (retarget to count + version pins, not field-reading).

### FR-031 — Versioned dataset-seam crosswalk + regression contract
- **Serves:** UC-21 · PGO-builder-02 [theme] · C1 · N-08
- **Priority:** **MUST** (P2 precondition; the anti-drift guarantee, justified by two confirmed multi-week/multi-month silent-drift burns — INT-01 "6-month reanalysis", INT-03 "a week tracing the delta")
- **GIVEN** the reconciled seam (FR-030) and the live v2.0.0 corpus,
- **WHEN** a versioned crosswalk artifact (v1.3.0/`labels`/159,891 → v2.0.0/`annotations`/575,604) is committed **with a lossless-or-explicit-lossy test**, and a regression contract pins **{version, record-count, 63-entity-type count, schema fingerprint (annotation-key set + 63-type vocabulary), dataset content hash}**,
- **THEN** a committed regression test turns **RED** if **any** pinned value reverts or mutates: version → v1.3.0, record-count → 159,891, entity-type count ≠ 63, schema fingerprint changes (mutated annotation schema at the same count), **or** the dataset content hash changes (silent same-count content substitution — GAME-07); AND the crosswalk's field-mapping is asserted either lossless or, where lossy, each dropped/transformed field is explicitly enumerated and tested.
- **Boolean test:** mutate each of the five pinned values in turn (and inject a same-count content swap) → the regression test goes RED on every mutation AND green on the true v2.0.0 values → `True`/`False`.
- **Reuse / grounding:** content hash via `scripts/write_manifest.py` (`MANIFEST.sha256`, stdlib `hashlib`); the contract value is also surfaced as a **run-record field** (FR-045) so it is assertable in a paper's methods section, not only a crosswalk doc (INT-02). Resolves SME findings REPRO-05/DOM-06 (schema fingerprint + 63-type vocab), GAME-07 (content hash vs same-count swap).

---

## B. Powered, lattice-stratified sampler + sample manifest (SAMPLE)

### FR-032 — Powered, lattice-stratified, seeded sampler
- **Serves:** UC-16 · PGO-researcher-03, PGO-acaddeid-01, PGO-priveng-03 [theme]
- **Priority:** **MUST** (the capability's reason to exist — the net-new contribution `pii-rate-elo`'s naive `max_samples` head-truncation cannot provide)
- **GIVEN** the v2.0.0 corpus and the **frozen 730-cell committed lattice** (`eval_lattice.json` @ `47c3a8f`), and a declared **power design point** per risk tier — CRITICAL `(p_ref=0.99, half_width=0.005) → 1,522`, STANDARD `(0.98, 0.010) → 753`, LONG_TAIL `(0.95, 0.03025) → 200`, each `target_n` **derived via `stats/power.py::required_n(p_ref, half_width, α)`, never hand-typed**,
- **WHEN** the `powered-representative` preset is requested with a seed,
- **THEN** eval-data draws a **seeded, deterministic, lattice-stratified** sample targeting each committed cell's tier `target_n` against the cell's **realized positive count** (the measured `CellAudit.n`, NOT a `target_n` label), in a single streaming pass; AND the draw never uses naive file-order head-truncation.
- **Boolean test:** for every committed cell the sampler attempts to reach `target_n` positives where `target_n == required_n(*tier_design_point)` AND classification is evaluated on realized positives AND the draw is seeded; the no-head-truncation guarantee is asserted by a **named two-part oracle** — **(i)** a static/import-graph assertion that the assessment sampler entrypoint does NOT reference the `max_samples` head-truncation symbol (converter `L82-84` / loader `L73`), AND **(ii)** a behavioral assertion on a fixture corpus whose positives are deliberately **back-loaded** (placed after record N): the seeded draw still reaches each cell's `target_n` (a head-truncation path would fail this) — either oracle failing ⇒ `False` → `True`/`False`.
- **Reuse / grounding:** `stats/power.py` (`required_n`, `TIER_SPECS`, `classify`, `pick_tier`); `stats/lattice.py` (`build_committed_lattice`/`load_lattice`, `--check` = 730 cells); `scripts/lattice_audit.py` (`audit_positives`/`deficits`, streaming realized counts); `subsets/slices.py`; seeded reservoir pattern from `scripts/benchmark_throughput.py::reservoir_sample` (Algorithm-R, AX-002). Resolves SME findings STATS-01 (design point), STATS-02 (realized positives).

### FR-033 — PowerMatrix verdict + per-cell named-shortfall report artifact (against realized positives)
- **Serves:** UC-16, UC-23(d) · PGO-researcher-03, PGO-acaddeid-01 · DF-3 (resolved zero-dissent) · C5
- **Priority:** **MUST** (the honest UNDER-POWERED path — the study's single strongest *delight*; the P3 precondition's report artifact)
- **GIVEN** the drawn sample (FR-032) and each committed cell's realized positive count vs the full corpus's realized positive count for that cell,
- **WHEN** the power matrix is emitted,
- **THEN** every committed cell carries a `power_class ∈ {WELL_POWERED, UNDER_SAMPLED, CORPUS_LIMITED, EMPTY}` — **WELL_POWERED** (realized positives ≥ tier target), **UNDER_SAMPLED** (full corpus has enough positives — fixable by drawing more), **CORPUS_LIMITED** (the full corpus itself has fewer positives than `target_n` — irreducible), **EMPTY** (n == 0, structural) — each under-tier cell carrying a **named shortfall expressed in realized positive counts** ("short by N realized positives vs the ADEQUATE threshold", NOT "needs more data" and NOT a `target_n` label); AND a corpus-level **`PowerMatrix.verdict()` ∈ {SMALL, ADEQUATE, LARGE}** is reported (LARGE only when well-powered fraction ≥ 0.999, ADEQUATE ≥ 0.80, else SMALL — never silently LARGE, G3); AND critical entity types outside the lattice coverage envelope surface as **`NOT_ASSESSED`**, never silently absent.
- **Boolean test:** every committed cell has a `power_class` in the 4-state set evaluated on realized positives; every under-tier cell has a shortfall integer in realized positives; the corpus verdict ∈ {SMALL,ADEQUATE,LARGE}; no committed cell is unclassified; no uncovered critical type is silently absent (each is `NOT_ASSESSED`) → `True`/`False`.
- **Reuse / grounding:** `stats/power.py::PowerMatrix.verdict()` (SMALL/ADEQUATE/LARGE thresholds 0.80/0.999 confirmed), `CellAudit` (`n`, `target_n`, `shortfall`, `power_class`), `classify`; the UNDER_SAMPLED-vs-CORPUS_LIMITED distinction extends `classify` (which today is 3-state WELL/UNDER/EMPTY) by comparing the sample's realized `n` against the **full-corpus** realized positives from `scripts/lattice_audit.py::audit_positives`. Resolves SME findings MEI-03 (CORPUS_LIMITED vs UNDER_SAMPLED), DOM-03 (coverage envelope / NOT_ASSESSED), STATS-02 (realized positives).

### FR-034 — Reproducible sample manifest with full draw provenance + non-strippable caveat
- **Serves:** UC-16 · PGO-acaddeid-03 (byte-for-byte reproducibility) · AX-002 · C8 · N-01 (run-type backing)
- **Priority:** **MUST**
- **GIVEN** a completed powered draw (FR-032) and its power matrix (FR-033),
- **WHEN** the sample manifest is emitted,
- **THEN** the manifest records: the **drawn record ids**; **per-cell draw provenance** (cell id, tier, design-point triple `(p_ref, half_width, α)`, `target_n`, realized positives, `power_class`, named shortfall); the **seed**; the **RNG/environment fingerprint** (RNG algorithm + seed-derivation, not just the seed integer); the **`lattice_version`** (lattice content hash / commit pin) and **sampler version** (commit/hash of `subsets/slices.py` + `stats/power.py`); the **PowerMatrix verdict**; the **entity-type coverage envelope**; and a **non-strippable synthetic-only caveat** (cannot serialize empty); AND re-running the sampler reproduces the manifest under **canonical-form equality** (sorted keys + fixed float repr) given the same seed AND the same recorded environment/RNG fingerprint AND the same sampler version.
- **Boolean test:** re-run the sampler with the recorded `{seed, RNG fingerprint, sampler version}` → the manifest is canonical-form-equal to the original AND contains all enumerated fields (ids, per-cell provenance, seed, RNG fingerprint, lattice_version, sampler version, verdict, coverage envelope, non-empty caveat) → `True`/`False`.
- **Reuse / grounding:** `scripts/write_manifest.py` pattern (deterministic sha256); `subsets/slices.py::SLICE_CAVEAT` + `Slice.__post_init__` (raises on empty caveat) for the non-strippable caveat; canonical-form-equality acceptance signal from UC-16. Resolves SME findings REPRO-03/GAME-04 (canonical-form + env/RNG + sampler-version), DOM-03 (coverage envelope).

---

## C. Preset trio + run-type designation (SAMPLE / RUN)

### FR-035 — Three assessment presets (powered-representative default / full-corpus opt-in / smoke)
- **Serves:** UC-16 (default), UC-19, UC-20 · PGO-acaddeid-01/03, PGO-researcher-01, PGO-builder-01 · DF-1 (resolved: locked default holds) · G2/G3
- **Priority:** **MUST**
- **GIVEN** the CLI assessment surface,
- **WHEN** a preset is selected,
- **THEN** exactly three presets exist with the locked defaults: **`powered-representative`** is the **DEFAULT** (lattice-stratified powered sample, always labelled with its PowerMatrix verdict + named shortfall, FR-033); **`full-corpus`** is reachable **only via explicit opt-in** (never the default) and is **declared the citable leaderboard mode**; **`smoke`** is the fast CI/dev preset; AND default invocation (no preset flag) yields the powered-representative sample, never silently the full corpus and never silently LARGE.
- **Boolean test:** default invocation → `preset == "powered-representative"` with a power verdict label present; full-corpus is unreachable without the opt-in flag; the **CLI preset enumeration equals exactly the closed set `{powered-representative, full-corpus, smoke}`** (set equality — not a "no fourth" prose check), AND any preset that emits a scored artifact (metrics / CI / leaderboard) but is not in that set ⇒ `False` (this operationalizes "results-bearing" as "emits a scored artifact") → `True`/`False`.
- **Reuse / grounding:** `pii-rate-elo/cli.py` (Typer) extended (consume sample mode, do not rebuild); detection is compute-cheap so full is reasonable while sampling binds where LLM-adversary cost binds (G2). Resolves DF-1 (split-by-use; locked default holds, citable-vs-pre-screen made first-class).

### FR-036 — Full-corpus opt-in run (descriptive census; record-count from the version-pinned loader)
- **Serves:** UC-19 · PGO-acaddeid-01/03, PGO-researcher-01 · DF-1
- **Priority:** **SHOULD** (real demand; the powered sample is the default path, full-corpus is the deliberate opt-in)
- **GIVEN** the full-corpus preset selected explicitly (FR-035),
- **WHEN** the identical `load → … → report` pipeline runs over all records,
- **THEN** the run-record stamps `preset == "full"` and **`records_scored == dataset.record_count(version)`** (resolved from the version-pinned loader, **NOT** a literal `575604`); AND a pre-registration exists for the run (UC-18 parity, FR-044); AND the report declares the **inferential target** — **exact-on-corpus (descriptive census) → metrics labelled descriptive / no-CI by default**, with CIs retained **only** when the report explicitly states a **super-population** (future-inputs) target.
- **Boolean test:** full-corpus invocation → `preset == "full"` AND `records_scored == dataset.record_count(version)` (not a magic constant) AND a pre-registration record exists AND the inferential-target label is present (descriptive→no-CI, or super-population→CI) → `True`/`False`.
- **Reuse / grounding:** `scripts/benchmark_throughput.py::build_run_record`; version-pinned `record_count` from the reconciled loader (FR-030). Resolves SME findings REPRO-04 (`dataset.record_count(version)` + UC-18 parity), STATS-08 (descriptive-census vs super-population target).

### FR-037 — Smoke run with suppressed inferential outputs
- **Serves:** UC-20 · PGO-builder-01 · C4 · N-10
- **Priority:** **SHOULD** (developer-velocity / CI enabler; explicitly not a results path)
- **GIVEN** the smoke preset on a fixed seeded tiny slice,
- **WHEN** the full spine runs (`load → sample → run → score → rate → report`),
- **THEN** the output artifact carries `preset == "smoke"` AND a **non-strippable `not_statistically_valid: true`** (or equivalent "smoke / not powered / not citable") caveat AND **every CI field and every p-value field is suppressed / null** — so a smoke result can neither be mistaken for, nor surface numbers that look like, a powered result; AND the spine completes end-to-end (green/red signal).
- **Boolean test:** smoke invocation → `preset == "smoke"` AND `not_statistically_valid == true` AND no CI field and no p-value field is non-null anywhere in the artifact AND the spine ran to completion → `True`/`False`.
- **Reuse / grounding:** non-strippable-caveat pattern from `subsets/slices.py`; suppression (not merely flagging) per UC-20. Resolves SME finding STATS-09 (suppress CI/p-value emission in smoke, not just flag).

### FR-038 — Run-type designation scoping pre-registration + the AX-005 rigor bar + backing sample mode
- **Serves:** UC-18, UC-19, UC-20 · DF-1 + DF-2 + the AX-005 universality tension (§4 #2 of `interview-synthesis.md`) · N-01 (the single highest-leverage net-new item R3 surfaced)
- **Priority:** **MUST**
- **GIVEN** the workflow surface and a declared **run-type** (`smoke` / `dev` / `leaderboard-submission` / `filing-grade`, names finalizable in Design) exposed as a CLI flag/preset ("not a philosophy" — INT-03),
- **WHEN** a run is launched under a run-type,
- **THEN** the run-type **selects** (a) the **enforced rigor bar** — the full AX-005 bar (CI + paired test + convergence statement + provenance + non-strippable synthetic-only caveat) binds `leaderboard-submission` and `filing-grade`; `smoke`/`dev` **suppress** CI/p-value emission (FR-037) rather than emit an un-rigorous number; (b) whether **pre-registration is enforced** (enforced for `leaderboard-submission`/`filing-grade`, opt-in for `dev`, off for `smoke`); and (c) the **backing sample mode** (filing-grade/leaderboard may bind full-corpus per DF-1; dev/smoke bind the sample); AND the chosen run-type is stamped in the run-record.
- **Boolean test:** the run-type→profile mapping is a **committed enum/fixture the test reads** (names finalizable in Design, but the *table* is referenced): the test asserts **(a)** the enum is non-empty and every member maps to a **total** triple `{rigor_bar ∈ {full-AX005, suppressed}, prereg ∈ {enforced, opt-in, off}, sample_mode ∈ {full, sample}}` with **no field unset**, AND **(b)** four behavioral invariants hold regardless of the chosen names — a `full-AX005` member omitting any AX-005 element ⇒ `False`; a `suppressed` member emitting any non-null CI/p-value field ⇒ `False`; the chosen run-type is recorded in the run-record; pre-reg enforcement equals the member's `prereg` value → `True`/`False`.
- **Reuse / grounding:** wires FR-037 (smoke suppression), FR-044 (pre-reg), FR-035/036 (sample modes), and the AX-005 bar (§AX-pii-anon-005). Resolves DF-2 (Open Item 6) and the AX-005 universality tension; carries INT-05's filing-grade-full-corpus pushback as the `filing-grade` backing-mode profile (to be confirmed R6/R7 + Pass-2).

---

## D. Run path: engine + audited statistics + quarantine (RUN / SCORE / RATE)

### FR-039 — Assessment run wired to the existing engine + convergence (no rebuild)
- **Serves:** UC-17, UC-19 · PGO-researcher-01/03, PGO-builder-01, PGO-acaddeid-01
- **Priority:** **MUST**
- **GIVEN** ≥2 systems and the UC-16 powered sample (or the full corpus, FR-036),
- **WHEN** the assessment preset config + CLI path runs the tournament,
- **THEN** systems are rated through the **existing `tournament/engine.py::PIIRateEloEngine`** (consumed, not rebuilt), wired via `config.py::PipelineConfig.from_yaml` and the extended `cli.py`, with **Glicko RD-convergence** evaluated by the **existing `tournament/convergence.py::ConvergenceChecker`** (RD threshold default 100); AND spans are scored through the **existing `evaluation/metrics_bridge.py::compute_span_metrics`** at a **declared span-match mode** (exact vs relaxed/overlap).
- **Boolean test:** a run consumes the powered sample (or full corpus) and produces ratings via `PIIRateEloEngine`, a convergence verdict via `ConvergenceChecker`, and span metrics via `compute_span_metrics`; the span-match mode is asserted to be in the **closed set `span_match_mode ∈ {exact, relaxed-overlap}`** AND the **declared mode equals the mode `compute_span_metrics` was actually invoked with** (a declared-but-unused or out-of-set value ⇒ `False`); no re-implemented engine/metrics on the path → `True`/`False`.
- **Reuse / grounding:** `engine.py`, `convergence.py`, `metrics_bridge.py`, `config.py`, `cli.py` (all consumed). Resolves SME finding DOM-04 (span-match mode declared).

### FR-040 — Per-metric confidence intervals under a deterministic interval-selection rule
- **Serves:** UC-17(a), UC-23(a) · PGO-researcher-03, PGO-acaddeid-01 · AX-003, AX-005 · C3 · Open Item 5
- **Priority:** **MUST**
- **GIVEN** any reported rating or metric with its integer positive count `n`,
- **WHEN** a CI is attached,
- **THEN** the CI is assigned by a **deterministic, disclosed interval-selection rule** — proportions → **Wilson** (default); **boundary** (`k∈{0,n}`) → **Clopper-Pearson** (load-bearing branch — fixes Wilson at `p̂=0|1`); small-n (`n < small_n_cutoff`, where **`small_n_cutoff` is a single integer RECORDED in the manifest + pre-registration**, committed default **`small_n_cutoff = 15`** — *R10 DIVERGED edit: lowered 30 → 15 toward the Wilson-robust zone (both personas + cited literature agree the n-switch is over-conservative; no canonical integer exists); R10-DIRECTIONAL / `real_user_needed: true`*, never a silent constant) → **Clopper-Pearson**; paired differences → **paired-bootstrap** — with the selected `method ∈ {wilson, clopper-pearson, paired-bootstrap}` recorded on every metric; AND **two inference families are declared and labelled**: per-cell CIs are **simultaneous-uncorrected / exploratory** (not headline claims), while confirmatory pairwise claims carry the family verdict (FR-041); AND no metric is emitted with a bare Wald/point interval or with an undisclosed method.
- **Boolean test:** every emitted metric has a non-null CI whose `method` **equals the method the recorded `small_n_cutoff` dictates for that metric's `(k, n)`** (Wilson for a proportion with `n ≥ cutoff` and `k ∉ {0,n}`; Clopper-Pearson for `k ∈ {0,n}` or `n < cutoff`; paired-bootstrap for differences), and is labelled by inference family; a `method` inconsistent with the recorded cutoff, an undisclosed-method, or a bare-Wald CI ⇒ `False` → `True`/`False`.
- **Reuse / grounding:** `stats/intervals.py::wilson_interval(k:int,n:int)` + `clopper_pearson_interval(k:int,n:int)` (integer-guarded); `stats/paired.py::paired_bootstrap_recall_delta` for differences. Resolves SME finding STATS-05 (interval-selection rule).

### FR-041 — Paired system-vs-system significance with Holm–Bonferroni + declared multiplicity family
- **Serves:** UC-17(b), UC-23(b) · PGO-researcher-01, PGO-acaddeid-01, PGO-builder-01 · AX-005 · C4 · Open Item 5
- **Priority:** **MUST**
- **GIVEN** any system-vs-system (pairwise) claim,
- **WHEN** significance is computed,
- **THEN** each pairwise claim carries a **McNemar verdict** (exact binomial for small discordant-pair counts, Edwards continuity-corrected χ² otherwise) **AND a paired-bootstrap recall-delta CI** (seeded, LOCAL RNG); AND the **confirmatory** set carries a **Holm–Bonferroni** decision with the **family size reported** (# pairs × metrics in the confirmatory set); AND the two-family split (exploratory per-cell uncorrected vs confirmatory pairwise Holm-corrected) is stated in the **report text**, not only in code (reviewers will ask — INT-01/02).
- **Boolean test:** every confirmatory pairwise claim has a McNemar p-value AND a paired-bootstrap delta CI AND a Holm–Bonferroni decision; the exploratory/confirmatory split is asserted via a **structured `inference_families` block** carrying exactly the two labels `{exploratory, confirmatory}` with `confirmatory.family_size` an integer **`== #pairs × #metrics in the confirmatory set`** (computed, not free-typed) — the report prose renders from this block, so the linter asserts the block (a missing block, only one family, or `family_size ≠` the computed product ⇒ `False`) → `True`/`False`.
- **Reuse / grounding:** `stats/paired.py::mcnemar_exact` + `mcnemar_chi2(continuity=True)` + `paired_bootstrap_recall_delta(seed=…)` (LOCAL `random.Random(seed)`, byte-identical, NFR-004). **Holm–Bonferroni is the one net-new statistical primitive** — added to the audited `stats/paired.py` (or a sibling in `stats/`), NOT to the quarantined `significance.py`. Resolves SME findings STATS-03/MEI-01 (multiplicity families + size + Holm).

### FR-042 — Quarantine the fabricated `significance.py` from the run surface (CI-enforced)
- **Serves:** UC-17 · PGO-researcher-01/03 · P1 (SHOWSTOPPER) · Open Item 1 · N-07
- **Priority:** **MUST** (the unanimous walk-away trigger; demanded CI-enforced, not documented — INT-02/03)
- **GIVEN** the fabricated consumer significance code — `analysis/significance.py` bootstrap `se = metric*(1-metric)/100` + Gaussian noise (L205-206) and McNemar `n_approx=100` / `z=difference*sqrt(n_approx)/0.05` / `pooled_sd=0.1` (L271-281),
- **WHEN** any statistic is computed on the run path,
- **THEN** **all** CIs and paired tests route through the audited `eval-data/stats` core (`paired.py` + `intervals.py`, FR-040/FR-041) and the fabricated `significance.py` path is **unreachable from the run surface**; AND a committed test asserts both directions — the audited path is always taken AND the fabricated `SignificanceTester` is not instantiated/imported on any run code path (e.g., `cli.py:242`-style instantiation is gone or guarded unreachable).
- **Boolean test:** a CI test asserts (a) no `analysis/significance.py` symbol is reachable from the `run`/`score`/`rate` entry points AND (b) the audited `stats/paired.py` + `stats/intervals.py` symbols are the ones invoked → both assertions green → `True`/`False`.
- **Reuse / grounding:** audited `stats/paired.py` + `stats/intervals.py`; quarantine is a run-surface assertion test (an NFR with a verification method — wired to the NFR doc). Resolves SME-adjacent Open Item 1; the load-bearing P1 precondition.

### FR-043 — Scoring-family separation (anon vs pseudo) + contamination status + seed-variance scope
- **Serves:** UC-17(c)(d)(e), UC-23 · PGO-researcher-01, PGO-builder-01/03 (separation), PGO-dpo-01 · AX-004 · DF-5 · C10 · N-09, N-11
- **Priority:** **MUST**
- **GIVEN** a run of ≥2 systems,
- **WHEN** the run executes,
- **THEN** (a) the **`scoring_family ∈ {anonymization, pseudonymization}`** is declared (AX-004) so pseudonymization is scored by consistency / reversibility / linkage metrics and **never** by bare span-F1, and the two families are **never merged**; (b) each system carries a **`contamination_status ∈ {disclosed-unseen, disclosed-trained-on-corpus, undisclosed}`** with **`unknown` rejected/flagged** (the public synthetic corpus invites train-on-test inflation), where "flagged" is operationalized as: `contamination_status == unknown` ⇒ a `contamination-uncontrolled` boolean is set **True on every downstream metric of that system**; (c) the run records **`seed_variance_scope`** — either **multi-seed with `len(seeds) ≥ MIN_SEEDS` (committed `MIN_SEEDS = 3`, INT-02's named floor — *R10 may relax to 2 with recorded rationale*) + rank-stability via Kendall-τ reported as a first-class output field** **or** an explicit `single-seed` flag carried to UC-23 as **`rank-volatility: UNMEASURED`**; AND the **AX-004 separation rationale** is written in the report/docs methodology, not only enforced in code.
- **Boolean test:** `scoring_family` declared and pseudo not scored by bare span-F1; every system has a `contamination_status`, and any `contamination_status == unknown` carries the `contamination-uncontrolled` flag set True on **all** of that system's metrics (absence on any ⇒ `False`); `seed_variance_scope` recorded — if `multi-seed` then `len(seeds) ≥ MIN_SEEDS (==3)` AND a Kendall-τ value is present, else `single-seed` AND `rank-volatility: UNMEASURED` carried; AX-004 rationale prose present → `True`/`False`.
- **Reuse / grounding:** scoring families separated per the four-metric-families guardrail (never merged); contamination + Kendall-τ are new run-record fields (governance hygiene, FR-051). Resolves SME findings DOM-01 (AX-004 enforced), GAME-01 (contamination_status), STATS-04/GAME-02 (seed-variance scope + Kendall-τ).

---

## E. Pre-registration (X / REPORT)

### FR-044 — Pre-register the run BEFORE any system is scored (git-commit-anchored + hash-chained)
- **Serves:** UC-18, UC-19 · PGO-acaddeid-03, PGO-complreviewer-01, PGO-tool-vendor-02 [theme] · AX-002, AX-005 · DF-2 · Open Item 6
- **Priority:** **MUST** (opt-in rigor per DF-2, but **enforced** for the high-stakes run-types via FR-038; the mechanism is MUST)
- **GIVEN** a run whose run-type enforces pre-registration (FR-038),
- **WHEN** the `sample` stage completes and before the first system is scored,
- **THEN** a **pre-registration record** is emitted and frozen, pinning the **full design + analysis plan**: dataset **version** + sample-manifest hash + seed + system list + metric set + RD **stopping rule** + **interval-selection rule** (per metric class) + **multiplicity family + size** + **power design point** + **span-match mode** + **scoring family** + **tie/exclusion rules**; the record is **committed and the commit pushed to remote**, and the **commit SHA + hash are chained into the first run-record** (the first `run`/`score` record references the pre-reg commit) so ordering is **git-SHA-anchored** (a back-datable local clock is at most a secondary check); each pre-registration is **immutable**; AND the report later discloses the **count of prior pre-registered runs for the same system set (run-lineage)** so re-roll-until-favorable is visible.
- **Boolean test:** for an enforcing run-type, a pre-reg record exists bound to a commit SHA that is **reachable on the configured remote** — the "pushed" clause is asserted by the named oracle **`git branch -r --contains <sha>` non-empty against the configured origin** (or an equivalent remote-existence API check); an SHA that exists only locally ⇒ `False` — and that SHA is referenced by the first run-record (hash-chain); its payload contains every pinned design+analysis-plan field; a later `pre_registration_matches: true` equality check covers that field set; the report states the run-lineage count — any missing pinned field, a local-only/unchained commit, or an absent lineage count ⇒ `False` → `True`/`False`.
- **Reuse / grounding:** `scripts/write_manifest.py` hashing pattern; chained into the FR-045 run-record. Resolves SME findings MEI-02/REPRO-01 (commit-anchor + hash-chain + dataset_version + rd_stopping_rule in match set), STATS-06/DOM-05 (full analysis plan in payload + match set), GAME-05 (immutable + run-lineage).

---

## F. Observability run-records + provenance (X — every stage)

### FR-045 — Per-stage observability run-record across the full spine
- **Serves:** UC-22 · PGO-priveng-02 [theme], PGO-complreviewer-01 · AX-002 · Open Item 7 · G5 (epistemic instrumentation, not generic logging)
- **Priority:** **MUST**
- **GIVEN** an end-to-end run,
- **WHEN** it executes,
- **THEN** eval-data emits **one structured run-record per spine stage** (`load`, `sample`, `run systems`, `score`, `rate`, `report`), each stamped with **`{dataset_version, record_count, schema_fingerprint, seed, stage, code_commit}` plus a toolchain fingerprint** and the stage timing; the records **share one run id** so the chain is traversable; AND the **regression-contract values** (FR-031) are surfaced as structured fields in the run-record JSON (assertable in a methods section — INT-02).
- **Boolean test:** a single run emits exactly one record per spine stage, each carrying the full key set incl. `code_commit` + toolchain fingerprint, all sharing one run id; the regression-contract fields are present — a missing stage record, an unlinked record, or an absent `code_commit` fails → `True`/`False`.
- **Reuse / grounding:** `scripts/benchmark_throughput.py::build_run_record` (seeded JSON run-record schema) extended per-stage; `scripts/write_manifest.py`. Resolves SME finding REPRO-06 (`code_commit` + toolchain fingerprint per stage). **G5:** "observability" here means statistical/epistemic instrumentation, not generic logging.

### FR-046 — File-level provenance on every emitted artifact
- **Serves:** UC-22, UC-23 · PGO-complreviewer-01, PGO-priveng-02 · C5 · N-04
- **Priority:** **SHOULD** (audit-admissibility for filing-grade consumers; "which file produced this number?" — INT-04/05)
- **GIVEN** any emitted artifact (manifest, run-record, leaderboard, figure, pre-reg),
- **WHEN** it is written,
- **THEN** it carries **file-level provenance** — its own content hash, the producing `code_commit`, the run id, and the producing stage — so a consumer can answer "which file (not just which run) produced this number" for an Art-11-grade filing.
- **Boolean test:** every emitted artifact embeds `{content_hash, code_commit, run_id, stage}` → `True`/`False`.
- **Reuse / grounding:** `scripts/write_manifest.py` (per-file sha256). Maps to EU AI Act Art-11 provenance (INT-05).

---

## G. Reporting: leaderboard + figures + honest verdicts (REPORT / X)

### FR-047 — Honest reportable leaderboard with paired-test-gated ranks
- **Serves:** UC-23 · PGO-researcher-01, PGO-builder-02, PGO-tool-vendor-01, PGO-priveng-01, PGO-dpo-01/02, PGO-complreviewer-02 · AX-005 · Open Item 8
- **Priority:** **MUST** (the report is the deliverable)
- **GIVEN** the UC-17 results,
- **WHEN** the leaderboard is rendered,
- **THEN** each system's metric is shown **with its CI** (FR-040); **ranks are gated by the paired-test verdict** — systems whose pairwise difference is not significant after Holm–Bonferroni (FR-041) are grouped/greyed as **statistical ties** (no rank out-runs the paired evidence); AND **anon vs pseudo are reported in separate metric families** (AX-004, never collapsed into one "redaction quality" number); AND the **artifact-first register** is academic-vocabulary **LaTeX tabular + CSV** with labeled headers — product verdict language ("SHIP-WITH-CAVEATS") must **not** appear verbatim (INT-01, C7).
- **Boolean test:** ("honest" is defined by this conjunction of sub-tests) every ranked number carries a CI; non-significant pairs are greyed/grouped as ties; anon and pseudo families are not merged; LaTeX + CSV registers emit; AND a scan of the registers finds **none of the committed forbidden product-verdict tokens `{"SHIP-WITH-CAVEATS", "SHIP", "DEFER", "GO/NO-GO"}`** (extensible list) — a register containing any listed token ⇒ `False` → `True`/`False`.
- **Reuse / grounding:** `reporting/*`; `stats/paired.py` (tie-gating verdict); `convergence.py`. Resolves SME findings STATS-07 (rank gated by paired test / ties greyed), and C7 (artifact-first register).

### FR-048 — Operating-point reporting (recall-priority Fβ / FN:FP cost + AUPRC at the pre-registered operating point)
- **Serves:** UC-23(a) · PGO-priveng-01, PGO-dpo-02 · DOM-02 · N-03 (a net-new capability from the MEDIUM personas)
- **Priority:** **MUST** (the false-positive tax — a confirmed real burn: F1=0.91 → precision 0.71 at recall 0.93 → "34k FPs / 10k entities" / 3× license cost — INT-04)
- **GIVEN** detection/anonymization scores,
- **WHEN** the report renders the operating-point view,
- **THEN** it shows a **recall-priority Fβ with β RECORDED in the manifest/pre-reg and `β ≥ 2`** (committed default **`β = 2`** — *R10-to-confirm*) **or a stated integer FN:FP cost ratio** that names the de-id recall/precision asymmetry (a missed SSN is a breach; a false positive is over-redaction), **AND a threshold-free AUPRC** alongside the **pre-registered operating point** (threshold rule fixed pre-scoring, FR-044) so the curve is not a single point post-hoc tuned to the eval set; AND a **precision-at-fixed-recall** readout (non-null) at a **recall target RECORDED in the pre-reg** (committed default **`recall = 0.90`**, within INT-04's 0.90–0.93 band — *R10-to-confirm*) — **never a lone F1**.
- **Boolean test:** the report shows {Fβ with `β` recorded and `β ≥ 2` OR a stated integer FN:FP cost} AND AUPRC present AND the operating point equals the pre-registered threshold rule AND precision-at-fixed-recall present (non-null) at the recorded recall target — a lone F1, a free/undeclared `β`, an absent precision-at-recall, or a post-hoc-tuned single threshold ⇒ `False` → `True`/`False`.
- **Reuse / grounding:** `evaluation/metrics_bridge.py` (extended for Fβ/AUPRC); pre-reg operating point from FR-044. Resolves SME findings DOM-02 (recall/precision asymmetry), GAME-03/MEI-05 (pre-registered operating point + AUPRC, not a faux curve).

### FR-049 — Non-strippable honesty-flag bundle on every figure + RD-convergence reporting
- **Serves:** UC-23(c)(d) · PGO-complreviewer-02, PGO-dpo-01 · AX-001/003, AX-005 · G4 · C6 · N-15
- **Priority:** **MUST**
- **GIVEN** a rendered report/figure,
- **WHEN** it is emitted (and exported / copy-pasted into Confluence / Excel / a regulatory system),
- **THEN** it carries, **inline per-metric and non-strippably** (cannot be serialized away as a removable header/footer/appendix — INT-04/05), the following **closed, enumerated honesty-signal set**: the **non-strippable synthetic-only / anti-anonymity caveat** (`DesignProvenance`, AX-001/003); the **RD-convergence verdict** reported as **achieved max-RD ± 2RD with the number of Glicko rounds stated** (never "converged" hand-wave; an extrapolated round count is forbidden — G4) with **RD-NOT-CONVERGED propagated as a blocking honesty flag** from FR-039; the per-cell **UNDER-POWERED / UNDER-SAMPLED / CORPUS-LIMITED** flags (FR-033); the **contamination-uncontrolled** flags (FR-043); the **rank-volatility scope** (FR-043); the **worst-language recall** = `min over the languages present in the run's coverage envelope of per-language recall`, reported **with the language label that realizes the min** (an `argmin`, fully computable) AND the **low-resource recall** = recall restricted to the **enumerable committed set of languages whose realized positive count is `< 200`** (the LONG_TAIL tier target) — both replacing the prior undefined "worst-language / low-resource" prose; AND the **correlation-study "named-and-pending"** flag (until cycle-1 UC-13 lands — INT-04/05).
- **Boolean test:** stripping **any** signal from the enumerated honesty set {synthetic-only caveat / convergence block / per-cell power_class flag / contamination-uncontrolled flag / rank-volatility scope / worst-language `argmin`+label / low-resource-set recall / named-and-pending correlation flag} invalidates the artifact; the convergence verdict is `max-RD ± 2RD + rounds` (not a round-count extrapolation); the worst-language `argmin` carries its language label and the low-resource recall is computed over the `<200`-realized-positive set → `True`/`False`.
- **Reuse / grounding:** `scoring/detection.py::DesignProvenance` (raises on empty caveat; `to_dict` carries the caveat through serializers); `convergence.py` (`is_converged`, `max_rd`, `rd_threshold`); G4 RD-reporting rail. Resolves SME findings STATS-04/GAME-02 (rank-volatility surfaced), DOM-07 (worst-language recall), C6 (non-strippable export survival).

### FR-050 — Self-verifying report (embeds pre-reg hash + run id) — reproducible-from-manifest end-to-end
- **Serves:** UC-23(e), UC-18, UC-22 · PGO-complreviewer-01, PGO-acaddeid-03 · AX-002 · Open Item 8 · REPRO-07
- **Priority:** **MUST**
- **GIVEN** a completed run with its pre-registration (FR-044) and run-records (FR-045),
- **WHEN** the final report is rendered,
- **THEN** it **embeds the pre-registration hash + commit SHA + run id** so any consumer can reproduce the result from the manifest end-to-end and confirm the scored design equals the pre-registered design; AND the report is the filing-grade artifact whose every metric cell carries its **CI + provenance hash + synthetic-only caveat inline** (the JSON run-record is necessary but insufficient — the filed artifact format is itself gated, INT-05); AND a named **Art-11 alignment label** indicates which fields satisfy EU AI Act Art-10/11.
- **Boolean test:** the report embeds {pre-reg hash, commit SHA, run id}; every metric cell carries inline {CI, provenance hash, synthetic-only caveat}; the Art-11 alignment label is present; the run reproduces from the manifest → `True`/`False`.
- **Reuse / grounding:** chains FR-044 (pre-reg) + FR-045 (run-records) + FR-046 (file-level provenance). Resolves SME finding REPRO-07 (embed pre-reg hash + run id); N-04 (filing-grade format + Art-11 label).

---

## H. Governance / anti-gaming / compliance crosswalk (X)

### FR-051 — Leaderboard hygiene: blind/provenance-stamped submission + contamination control + held-out-non-exposure attestation
- **Serves:** UC-17(d), UC-23 · PGO-tool-vendor-01/02, PGO-builder-02, PGO-complreviewer-01 · DF-5 · Open Items 8/9 · N-11 (justified by the `P-tool-vendor` threat-model sub-archetype)
- **Priority:** **MUST**
- **GIVEN** a leaderboard submission,
- **WHEN** it is processed,
- **THEN** held-out labels stay undistributed; submission is **blind/provenance-stamped** (evaluator runs inference; held-out labels genuinely held out; the submitter may sign an attestation rather than open-source weights); each entry carries a per-system **`contamination_status`** with **`unknown` rejected/flagged** (FR-043) **plus a signed attestation that held-out labels were not exposed** (INT-03's 6th AX-005 element); AND a leaderboard that accepts `contamination_status: unknown` is rejected.
- **Boolean test:** "genuinely held out" is asserted by the **scoring-API-surface oracle** — a call sequence to the scoring endpoint returns a response whose schema **excludes the held-out label field** (labels never returned); every accepted entry has a provenance stamp + a `contamination_status ≠ unknown`; the held-out-non-exposure attestation is a **structured record present and well-formed** (required fields `{submitter_id, statement, signature, signed_at}` all non-empty) AND, where a signing scheme is configured, the `signature` **verifies against the configured public key** (a missing/malformed attestation, or a failed signature when a key is configured ⇒ `False`); an `unknown`-contamination entry is rejected → `True`/`False`.
- **Reuse / grounding:** extends the run-record (FR-045) with submission-provenance fields; mirrors cycle-1 FR-023 (neutral leaderboard) at the workflow layer. Resolves DF-5 (Open Items 8,9).

### FR-052 — Neutrality / governance statement field + recusal record
- **Serves:** UC-23, UC-18 · PGO-complreviewer-01, PGO-priveng-01 · DF-5 · Open Item 9 · N-12
- **Priority:** **SHOULD** (inadmissibility-grade for the assurance/procurement consumers — INT-04/05: vendor self-benchmarks are "inadmissible"; but the v0.1 results path runs without it, so SHOULD)
- **GIVEN** a published run/report,
- **WHEN** it is emitted,
- **THEN** a **named neutrality/governance statement** (who controls the corpus, who holds the held-out labels, who runs the eval) appears as a **structured field in the run-record AND on every report page** (not a general caveat); AND a managed conflict (e.g., an academic group with a system in the leaderboard) is recorded with an **explicit disclosure + recusal record**.
- **Boolean test:** the governance block `{corpus_owner, label_holder, evaluator}` (all non-empty) is a structured run-record field AND is rendered on **each emitted report page/section** (per-page presence asserted by the report linter, not a single front-matter check); the recusal requirement is a **computable conditional** — *if* any `evaluator` identity appears in the submitting-system ownership metadata of any leaderboard entry, *then* a `recusal_record` for that identity must be present (the trigger-without-record case ⇒ `False`) → `True`/`False`.
- **Reuse / grounding:** run-record field (FR-045); aligns with cycle-1 FR-026 (governance charter) at the workflow layer.

### FR-053 — Regulatory taxonomy crosswalk (63 types → GDPR / HIPAA / CCPA / GLBA), auditable + updateable
- **Serves:** UC-23 · PGO-dpo-03, PGO-priveng-03 · AX-004 · Open Item 10 (author-or-defer fork) · N-05 (EU AI Act Art-10/11 Aug-2026 driver)
- **Priority:** **SHOULD** (resolved AUTHOR-not-defer per INT-04/05 — "more load-bearing than the pre-registration question" (INT-04); SHOULD because it is consumed by the MEDIUM compliance personas, not the HIGH results path)
- **GIVEN** the 63 v2.0.0 entity types,
- **WHEN** the crosswalk artifact is produced,
- **THEN** it maps each entity type to its **regulatory regimes** — GDPR (incl. Art-9 special categories) / HIPAA PHI / CCPA / GLBA — kept **legally distinct at the display layer** (no cross-regime equivalence asserted); AND the mapping is **auditable and updateable** (a versioned artifact with provenance, not hard-coded), so a consumer uses it with caveats rather than rebuilding it each cycle.
- **Boolean test:** every one of the 63 types has a regulatory-regime mapping kept legally distinct per regime; the artifact is versioned/updateable with provenance → `True`/`False`.
- **Reuse / grounding:** extends cycle-1 FR-022 (legally-distinct regulatory crosswalk) to the v2.0.0 63-type vocabulary at the workflow layer; AX-004 anon/pseudo separation. Resolves Open Item 10 (AUTHOR), N-05.

---

## I. Citation + release (X)

### FR-054 — Citable / DOI-able release with frictionless citation + claims policy
- **Serves:** UC-23 · PGO-acaddeid-03, PGO-tool-vendor-01 · C2 · N-13
- **Priority:** **SHOULD** (MUST-level for the P-acad-deid citation cohort — a **Zenodo DOI is a hard citation gate**, a GitHub SHA "is insufficient and link-rots" (INT-01, confirmed INT-02); SHOULD overall because the CI-gate / procurement / oracle uses do not need a DOI — persona-stratified per §4 #5 of `interview-synthesis.md`)
- **GIVEN** a published assessment release,
- **WHEN** a consumer cites it,
- **THEN** a **persistent identifier (Zenodo DOI or equivalent)** is minted (not only a git SHA), AND a ready **BibTeX + recommended citation template** is provided, AND a **claims policy** states what the synthetic-only result does and does not support (the ceiling caveat — AX-001/003).
- **Boolean test:** the release has a persistent DOI (not only a SHA) AND ships BibTeX + a citation template AND a synthetic-only claims policy → `True`/`False`.
- **Reuse / grounding:** mirrors cycle-1 FR-028 (frictionless citation) at the workflow-release layer; ceiling caveat from `DesignProvenance`.

---

## Candidate axiom — AX-pii-anon-005 (proposed for confirmation)

> **AX-pii-anon-005 (pre-registered / reproducible assessment).** **No published metric without (1) a confidence interval [method disclosed], (2) a paired significance test for any system-vs-system claim [with the multiplicity family + size declared — exploratory per-cell uncorrected vs confirmatory Holm–Bonferroni], (3) a convergence statement [achieved max-RD ± 2RD with rounds stated], (4) complete provenance [dataset_version, record_count, schema_fingerprint, seed, stage, code_commit, toolchain, file-level], (5) the non-strippable synthetic-only / anti-anonymity caveat, and (6) for leaderboard entries, a contamination disclosure + signed held-out-non-exposure attestation.** **Enforcement scope is run-type-bound** (FR-038): the full bar binds `leaderboard-submission` / `filing-grade`; `smoke` / `dev` suppress inferential outputs entirely rather than emit an un-rigorous number. **Manifest-reproducibility is UNIVERSAL** (binds all run-types, AX-002); **pre-registration is opt-in** (enforced only for the high-stakes run-types).

- **Status:** PROPOSED (R4) — to be confirmed in the R-stage NFR/threshold pass. Wired to: FR-040 (CI), FR-041 (paired + Holm + multiplicity), FR-049 (convergence + caveat), FR-044 (pre-reg), FR-045/046 (provenance), FR-043/FR-051 (contamination + attestation), FR-038 (run-type scoping). Confirmed by all R3 interviewees who reached the AX-005 probe as "the right bar," with two sharpenings adopted above (multiplicity-family-in-text from INT-01/02; the 6th contamination element from INT-03).
- **Inherited axioms still binding:** AX-pii-anon-001 (synthetic-only / no real PII), -002 (deterministic/seeded/byte-reproducible), -003 (stated power — every metric declares n + CI), -004 (anon vs pseudo scored by separate metric families).

---

## Coverage & trace

### FR → UC coverage (every brief-required coverage point lands on ≥1 FR)

| Brief-required capability | FR(s) | UC |
|---|---|---|
| Powered lattice-stratified sampler (seeded/deterministic, meets committed-cell tiers) | FR-032 | UC-16 |
| Sample-manifest emission (record ids + per-cell draw provenance + seed + lattice_version + tier targets + power verdict + non-strippable caveat) | FR-034 | UC-16 |
| PowerMatrix verdict + per-cell shortfall report vs realized positives | FR-033 | UC-16/23 |
| Preset trio (powered-representative default / full opt-in citable / smoke CI) | FR-035 (+FR-036, FR-037, FR-038) | UC-16/19/20 |
| Dataset-seam reconciliation to v2.0.0 + versioned crosswalk | FR-030, FR-031 | UC-21 |
| Regression contract (version+count+63-type+schema-fingerprint+content-hash) | FR-031 | UC-21 |
| Per-stage observability run-record across the spine | FR-045 (+FR-046 file-level) | UC-22 |
| Pre-registration artifact (opt-in, hash-chained) | FR-044 (scoped by FR-038) | UC-18 |
| Assessment preset config + CLI path consuming sample/full + wiring engine+convergence+audited stats | FR-039 (+FR-035, FR-038) | UC-17/19 |
| Per-metric CI integration | FR-040 | UC-17/23 |
| Paired-significance integration (McNemar + paired-bootstrap + Holm–Bonferroni) | FR-041 | UC-17/23 |
| RD-convergence reporting (achieved max-RD ± 2RD) | FR-049 (+FR-039 verdict source) | UC-17/23 |
| Reportable leaderboard + figures with honest-verdict flags + artifact-first register (LaTeX/CSV) | FR-047, FR-049, FR-050 | UC-23 |
| Honest-verdict engine | FR-049 (+FR-047 tie-gating, FR-033 power flags) | UC-23 |
| Anon-vs-pseudo separation preserved in reporting | FR-043 (run) + FR-047 (report) | UC-17/23 |
| Quarantine fabricated significance.py (P1) | FR-042 | UC-17 |
| Run-type designation (N-01) | FR-038 | UC-18/19/20 |
| Operating-point / false-positive-tax view (N-03) | FR-048 | UC-23 |
| Leaderboard hygiene / contamination / neutrality (DF-5) | FR-051, FR-052 | UC-17/23 |
| Regulatory crosswalk (Open Item 10, AUTHOR) | FR-053 | UC-23 |
| Citable DOI release (C2) | FR-054 | UC-23 |

### UC → FR (every UC served by ≥1 FR)
- **UC-16** → FR-032, FR-033, FR-034 (+FR-035 default)
- **UC-17** → FR-039, FR-040, FR-041, FR-042, FR-043 (+FR-047/048/049 downstream)
- **UC-18** → FR-044 (+FR-038 scoping, FR-050 embedding)
- **UC-19** → FR-036 (+FR-035, FR-038, FR-039, FR-044 parity)
- **UC-20** → FR-037 (+FR-035, FR-038)
- **UC-21** → FR-030, FR-031
- **UC-22** → FR-045, FR-046
- **UC-23** → FR-047, FR-048, FR-049, FR-050, FR-053, FR-054 (+FR-033 power flags, FR-043 anon/pseudo, FR-051/052 governance)

**0 orphan UCs** (all 8 served) · **0 orphan FRs** (all 25 trace to ≥1 UC).

### Carried as deferred-with-rationale (NOT silently dropped — per the bridge §4)
- **Re-id / RRS family** (PGO-acaddeid-02, PGO-researcher-02, PGO-builder-03): out of CAP-02 v0.1 — re-id power uses the distinct `stats/power.py::REID_TIER_SPECS` ladder (897/385 *pairs*, op-point p≈0.1–0.5), RRS scenarios live in cycle-1 UC-08/09. Named roadmap (Open Item 13 / MEI-06). The anon-vs-pseudo *separation* (AX-004) IS in-scope (FR-043/047); the RRS *figure* is roadmap.
- **Agentic recognition-oracle / RRS-on-transcripts** (PGO-redteam-01/02/03): cycle-1 UC-08/09 + live-harness-adapter roadmap; CAP-02 is the static powered-assessment workflow, honestly bounded.
- **Oracle throughput SLA** (N-06; INT-06: ≤50 ms p95 / ≥500 rps): routes to the oracle track (cycle-1 UC-08 / C9). Not a CAP-02-v0.1 blocker; surfaced by making `scripts/benchmark_throughput.py` output machine-readable in FR-049/050 reporting. Carried as a named MEDIUM-persona quality attribute to the NFR doc.

---

## Methodology & Epistemic Honesty
- **FRs are agent-authored** from the canonical Discovery artifacts (`discovery-report.md` §8 Open Items 1–13 / G1–G7 / C1–C10; `04-use-cases.md` UC-16…23 + acceptance signals; `personas.md`; `workflow-maps.md` PGO triples) + the R0 `_bridge/uc-pgo-map.md` + the R3 `interview-synthesis.md` (DF-1…5 resolutions, N-01…N-15 candidates, §2 threshold signals), grounded against direct file-reads of the `pii-anon-eval-data` code seams at HEAD on 2026-06-01 (`stats/power.py` TIER_SPECS 1522/753/200 + REID_TIER_SPECS + `PowerClass` + `PowerMatrix.verdict()` thresholds 0.80/0.999; `stats/intervals.py` Wilson/Clopper-Pearson; `stats/paired.py` McNemar exact/χ² + seeded paired-bootstrap; `stats/lattice.py --check`; `subsets/slices.py` + `scoring/detection.py` non-strippable caveats; `scripts/benchmark_throughput.py` seeded run-record; `scripts/lattice_audit.py` realized-positive streaming; `scripts/write_manifest.py` content hash; `scripts/_version.py` version resolver). The cited `pii-rate-elo` line numbers (`significance.py` L205-206/L271-281; `pii_anon_eval.py` L93/L221/L222; `schema.py` L137/L349) are from the Discovery file-reads — that repo is not checked out on this machine.
- **provisional_status: AGENT_SIMULATED.** Every persona/PGO/UC/interview signal these FRs trace to is agent-simulated single-session research; the quantified thresholds embedded in FR text (e.g., <10 min smoke, ≤50 ms/≥500 rps, 34k-FP false-positive tax, 3-seed Kendall-τ minimum, the 0.80/0.999 verdict cuts) are **directional** — the NFR-author proposes them and the R9 threshold-validator pressure-tests them; they are NOT committed values. Real-user validation of the FRs and thresholds is a Pass-2 follow-up.
- **Two inherited structural caveats** (R2/R3): (1) the **P-dpo / assurance lens is first-contact** (INT-05) — the compliance FRs (FR-046/050/052/053) trace to a single un-re-confirmed lens; real-user DPO interviews remain a Pass-2 must. (2) The **real-data correlation slice** (cycle-1 UC-13, vs i2b2-2014/TAB) is the named citation unlock and is **out-of-band / not v0.1-blocking** — surfaced here only as the "named-and-pending" report flag (FR-049).
- **ID discipline:** FR-030 … FR-054, global numbering continued, never renumbered/reused. NFR IDs (NFR-019+) are the NFR doc's job; this doc names the quality bars descriptively and wires AX-pii-anon-005 (proposed) to the relevant FRs.
- **No corpus regeneration; frozen guardrails respected** — lattice 730 cells @ `47c3a8f` (FR-032/033 consume, never rebuild it); four metric families never merged (FR-043/047); pure-stdlib cores + lazy heavy-dep guards; `pii-rate-elo` is consumed, not rebuilt (FR-039), and its own gates (pytest/ruff/mypy) stay green.

✅ **R4 Functional Requirements complete (2026-06-01).** **25 FRs (FR-030 … FR-054; 19 MUST · 6 SHOULD · 0 COULD)**, every brief-required capability covered, every FR traced to ≥1 UC (→ PGO → persona), 0 orphans both directions. Candidate **AX-pii-anon-005 proposed** (6-element, run-type-scoped) and wired. Re-id/RRS family + agentic oracle + throughput SLA carried as deferred-with-rationale. `provisional_status: AGENT_SIMULATED`; thresholds directional (R9 to validate); DPO lens first-contact; real-data slice Pass-2. Ready for the NFR pass (NFR-019+).
