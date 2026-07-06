# CAP-02 — D4 CONVERGE: Preferred System archetype

**Capability**: CAP-02 — academically-sound, repeatable, reportable assessment **workflow** that runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 / CC0 / `annotations`** over a **powered-representative sample (CLI default)** / **full corpus (opt-in, citable)** / **smoke (fast CI)**, with statistical/epistemic observability + reporting at every spine stage `load → sample → run → score → rate → report`.
**Stage**: assessment-workflow / 03-Design · **Diamond 4 (System) — CONVERGE**
**Date**: 2026-06-01
**provisional_status**: AGENT_SIMULATED — the archetype is selected by agent-simulated Pugh scoring against the requirements + the **verified code seams (direct file-read at HEAD 2026-06-01**; paths cited inline). No high-stakes user-validation commitment is introduced here that D2 did not already flag (the one such commitment — *no interactive per-stage consent*, D2 SP-W4 — is carried, not re-opened).

> **Vocabulary remap.** DC = **Benchmark Component**; FR = Assessment Capability; UC = Evaluation Scenario; NFR = Quality Attribute; AX = binding axiom.

> **Locked architecture this diamond honors.** eval-data **OWNS** sampling + observability + reporting; `pii-rate-elo` **CONSUMES** (extend, do **NOT** rebuild the engine / metrics / convergence). Two CLI entrypoints (L3); the **sample-manifest is the L1 SEAM** (the only cross-process data coupling). Cycle-1 precedent for this diamond = **Modular system + Hexagonal scoring core (Clean inside `stats`)**. D1 locked the L6 module map; D2 locked the Linear-batch spine + the manifest seam. **D4 picks the in-process system shape and RESOLVES the L4 loader decision.**

---

## 1. The three system proposals (DIVERGE recap)

| Frame | Archetype | Deployment grain | Replay | Op-complexity | Signature move |
|---|---|---|---|---|---|
| **A** | **Monolith** | one in-process Python package (`pii_anon_datasets.assessment`) + a thin pii-rate-elo adapter | partial (byte-repro-from-manifest) | **low** | In-process call-graph makes "`significance.py` unreachable" a trivial static-import gate; lowest orchestration overhead |
| **B** | **Modular** | the same package as N cohesive modules (`sample`/`manifest`/`runrecord`/`prereg`/`report`/`verdicts`) + thin adapter; manifest as cross-repo seam | partial (manifest + seed + RNG-fingerprint + sampler-commit) | **medium** | Clean module decomposition behind the L1 manifest seam; each module a unit-testable build seam matching the D1 DC partition |
| **C** | **Event-Sourced** | append-only stage-event log; report is a pure projection (fold) over the events | **native** | medium | The per-stage run-record (L5/NFR-042) **IS** the event log; manifest + pre-reg are immutable hash-chained events; replay = NFR-030 |

All three: two installable packages in one shared venv; one-way dependency (pii-rate-elo → `pii_anon_datasets.{assessment,stats}`, never the reverse); pure-stdlib cores + lazy heavy-dep guards (NFR-050); six per-stage run-records under a shared run id (NFR-042); the non-strippable synthetic-only caveat by construction (NFR-044); and **all three independently DECIDED L4 = FIX the bundled parser** (see §4).

---

## 2. Pugh comparison (the brief's five named criteria)

**Datum** = **Frame B (Modular)** — the **cycle-1 precedent** ("Modular system + Hexagonal scoring core" in the locked hybrid) and the D1-locked partition (the L6 module map IS a modular decomposition). Scores: **+1** better than datum / **0** equal / **−1** worse.

Weights are the brief's five named criteria, normalized to sum 1.00. **OWNS/CONSUMES boundary cleanliness** and **decoupling of the two repos** carry the highest weight: the locked architecture is *defined* by that boundary (eval-data OWNS, pii-rate-elo CONSUMES) and by keeping pii-rate-elo's bundled parser standalone-installable (L1/L4) — these are the load-bearing invariants D5 must inherit. **Testability/TDD** is weighted next (the whole stack is gated by `pytest`/`ruff`/`mypy` on both sides, NFR-051, and the P1 quarantine is itself a *testable* import-graph predicate, NFR-019). **Reuse of eval-data modules** and **simplicity** are real but secondary (reuse is already maximized by the verified-API map; simplicity is a tie-breaker the brief names last).

| Criterion | Weight | A (Monolith) | B (Modular) = datum | C (Event-Sourced) |
|---|---:|:---:|:---:|:---:|
| **OWNS/CONSUMES boundary cleanliness** (eval-data OWNS sample+obs+report; pii-rate-elo CONSUMES; manifest is the sole data seam) | 0.26 | 0 | **0 (datum)** | 0 |
| **Decoupling of the two repos** (bundled parser standalone-installable; one-way import; no import cycle) | 0.24 | −1 | **0 (datum)** | 0 |
| **Testability / TDD** (each seam unit-testable; P1 quarantine an isolatable predicate; gates green) | 0.22 | 0 | **0 (datum)** | −1 |
| **Reuse of eval-data modules** (DC titles map 1:1 to L6 + verified reuse APIs) | 0.16 | 0 | **0 (datum)** | 0 |
| **Simplicity** (fewest moving parts; consume-not-rebuild; cycle-1 consistency; no new persistence model) | 0.12 | **+1** | **0 (datum)** | −1 |
| **Weighted total** | 1.00 | **−0.12** | **0.00** | **−0.34** |

### Score rationale (per criterion)

- **OWNS/CONSUMES boundary cleanliness — all three 0 (equal).** This is the *locked* invariant, so no archetype can score above the datum on it without redefining the brief: eval-data's `pii_anon_datasets.assessment` package OWNS sampling/observability/reporting and pii-rate-elo's thin adapter CONSUMES, in **every** frame. The boundary is realized identically — the sample-manifest is the sole cross-process data coupling (D2/L1) and the shared-venv import surface is one-directional. A's monolith and C's event log both still place the OWNED logic in eval-data and the CONSUMED engine in pii-rate-elo; neither improves nor harms the boundary. **Equal to datum is the correct, honest score** (the brief LOCKED Modular precisely because this boundary is already the architecture).

- **Decoupling of the two repos — A −1; B datum; C 0.** The verified seam fact is decisive: eval-data's `load_dataset(*, subset, domain, split, language, dimension)` (`src/pii_anon_datasets/__init__.py:55`) takes **NO `version` argument** — it resolves the version from the package + a fixed corpus path. **A (Monolith)** has the strongest gravitational pull toward importing `load_dataset` directly into the consumer to avoid maintaining two parsers — but doing so couples pii-rate-elo's loader to eval-data's package layout and **breaks the L1 invariant** that the bundled parser stays standalone-installable. A can resist this (and the L4 decision below makes it resist it), but the monolith *grain* makes the wrong coupling the path of least resistance — hence −1 on this criterion. **B (datum)** keeps the modules behind the manifest seam, so the decoupling is structural, not a discipline. **C** is equal-to-datum: append-only events are still consumed across the same one-way seam; the event log adds no coupling B lacks (and removes none).

- **Testability / TDD — A 0; B datum; C −1.** **B's module split = the D1 DC partition** (`sample`=DC-17/18, `manifest`=DC-19, `runrecord`=DC-25, `prereg`=DC-24, `report`=DC-26/27/28, `verdicts`=DC-18/28), so each DC is a unit-testable build seam — the TDD RED→GREEN cycle has a natural target per module. The P1 quarantine (NFR-019) is an **import-graph / call-graph static check** that is equally assertable in a monolith (A 0 — a static-import gate over one package is, if anything, marginally simpler, but B's module boundary makes the *report* module's "imports only `stats/*`" assertion sharper). **C is −1**: an event-sourced design adds **event-schema versioning + projection-fold correctness** as new test surfaces (the report is now a fold over an append-only log, so tests must cover replay-equivalence and schema migration), enlarging the test matrix for zero requirement gain (no FR/NFR asks for event sourcing). The audited-stats correctness — the thing that actually matters (P1) — is identical work in all three.

- **Reuse of eval-data modules — all three 0 (equal).** Reuse is already maximized by `_engineering-findings-verified.md §3`: every frame composes the **same** verified APIs — `stats/intervals.py` (Wilson/Clopper-Pearson, integer-guard L39-51), `stats/paired.py` (`mcnemar_exact`/`mcnemar_chi2`/`paired_bootstrap_recall_delta`, LOCAL `random.Random(seed)` L140), `stats/power.py` (`TIER_SPECS`/`PowerMatrix.verdict()` L351-361), `scripts/lattice_audit.py` (`audit_positives`/`deficits` streaming), `scripts/benchmark_throughput.py` (RUNRECORD + `reservoir_sample` Algorithm-R), `scoring/detection.py::DesignProvenance`. The archetype does not change *which* modules are reused, so this criterion does not separate the frames.

- **Simplicity — A +1; B datum; C −1.** **A genuinely wins here**: a single in-process package with module boundaries inside it is the fewest moving parts, and "no event bus, no append-only store, no projection machinery" is the lowest orchestration overhead for a 6-stage linear spine (D2). **B (datum)** is nearly as simple — the modules are in-process function calls, not services — but carries a slightly larger surface (N module files + the cross-repo import contract). **C −1**: event sourcing introduces an append-only store, immutable-event discipline, and event-schema migration — real machinery for a flow D2 already proved is a *fixed total linear order* with one true branch point. **Decisive context:** A's simplicity win and B's structure are not actually in tension — B's "modules" ARE in-process (same deployable, same call-graph), so B captures ~all of A's simplicity while keeping the testable seams; the 0.12 weight on simplicity is why A's +1 cannot overcome B's decoupling edge.

**Pugh verdict: Frame B (Modular) is preferred (datum; the only non-negative total at 0.00; A −0.12, C −0.34).** This confirms the **cycle-1 precedent** the brief names. It is **not** unanimous on every axis — **A wins simplicity (+1)** and A/B tie C out on testability/decoupling — so the preferred system is **Modular, enriched with A's two best ideas as named switch-points**: (i) A's *in-process, single-deployable grain* (the modules are import-time function calls in one shared venv, **not** services — capturing A's simplicity), and (ii) A's observation that the **P1 quarantine is cleanest as a static-import gate** (adopted as the canonical NFR-019 mechanism). C contributes one keepable idea — its **append-only / immutable framing of the run-records + pre-reg** — absorbed as a *discipline* (run-records and pre-reg are write-once, never mutated) **without** building an event-sourcing engine. The result is B's module map, not a fourth archetype.

---

## 3. Switch-points (named, per the brief)

| # | Switch-point | Frames in tension | Resolution (locked for D5) |
|---|---|---|---|
| **SP-S1** | **Deployment grain**: in-process modules (B) vs single monolith package (A) vs event log + projection (C) | A vs B vs C | **IN-PROCESS MODULES IN ONE SHARED VENV (B with A's grain).** The `assessment` modules are import-time Python (one deployable artifact per package, two packages in `pii-anon-core/.venv`), **not** services and **not** an event bus. This captures A's simplicity (no inter-process orchestration inside a repo) while keeping B's per-module test seams. No service mesh, no broker, no message queue. |
| **SP-S2** | **P1 quarantine mechanism**: static-import/call-graph gate (A's clean monolith insight) vs runtime config-only (`run_significance_tests:false`) | A vs B/C | **BOTH, AS TWO CI PREDICATES (adopt A's static gate as canonical).** NFR-019's gate is the conjunction: (a) a **static import-graph / call-graph check** on the assessment entrypoint asserting `pii-rate-elo/analysis/significance.py::SignificanceTester` is **unreachable** (verified targets: imported `cli.py:33`, instantiated `cli.py:242` behind the `cli.py:240` flag), AND (b) a config assertion `analysis.run_significance_tests == False`. "Green requires no human" (NFR-019). A's monolith made this gate look trivial; B keeps it trivial because the consumer adapter is the single import surface to scan. |
| **SP-S3** | **Run-record / pre-reg persistence**: append-only event store (C) vs write-once JSON artifacts (B) | B vs C | **WRITE-ONCE ARTIFACTS WITH APPEND-ONLY *DISCIPLINE* (B, absorbing C's immutability).** The 6 stage run-records (NFR-042) and the pre-reg (NFR-031) are **immutable once written** (the pre-reg is hash-chained into the first run-record; run-records are never mutated in place) — C's correct instinct — but they are **plain content-hashed JSON files**, not an event-sourcing store with a projection engine. The report reads them; it does not "fold an event stream." This buys C's auditability/replay-equivalence (NFR-030 byte-repro) at B's complexity. |
| **SP-S4** | **Holm–Bonferroni placement**: net-new primitive in audited `stats/` vs anywhere reachable | (all 3 agree it must be audited) | **NET-NEW PRIMITIVE IN audited `stats/` (verified absent today).** Confirmed at HEAD: **no** `holm`/`bonferroni` symbol exists in `src/pii_anon_datasets/stats/*.py`. Holm–Bonferroni (NFR-027) lands as a new function in the audited, pure-stdlib `stats/` package (next to `paired.py`), **NEVER** in the quarantined `pii-rate-elo/analysis/significance.py`. It is unit-tested like the other audited primitives (integer-guarded, seeded where stochastic — Holm is deterministic). |
| **SP-S5** | **Heavy-dep boundary**: which module may import numpy/matplotlib | (all 3 agree on lazy guards) | **`report.py` IS THE SOLE LAZY-HEAVY-DEP MODULE (figure code only).** Cores (`sample`/`manifest`/`runrecord`/`prereg`/`verdicts` + the `stats/*` reused cores) import **only** the stdlib (NFR-050). `report.py` may lazy-import numpy/matplotlib **inside figure functions** (the `benchmark_throughput.py::_spacy_ner_detector` lazy-guard pattern). An import-graph test asserts "importing the assessment package triggers no heavy import." |
| **SP-S6** | **L4 loader strategy** (the deferred decision) | fix-bundled-parser vs import canonical `load_dataset` | **RESOLVED in §4 → FIX the bundled parser.** Carried here as the headline switch-point; decided below with code-grounded justification. |

---

## 4. L4 LOADER DECISION (RESOLVED) — **FIX the pii-rate-elo bundled parser; do NOT import the canonical loader**

**Decision.** Fix `pii-rate-elo`'s bundled parser to v2.0.0 + pin a regression contract; **reserve** eval-data's `pii_anon_datasets.load_dataset` for the **eval-data sampler side only**. (All three DIVERGE frames — Monolith, Modular, Event-Sourced — independently reached this same decision; D4 ratifies it.)

**What gets fixed (verified at HEAD 2026-06-01 — re-confirm line numbers before editing):**
- `pii-rate-elo-pipeline/src/pii_rate_elo_pipeline/datasets/converters/pii_anon_eval.py`: `num_records=159891` (**L93**) → **575604**; `license="CC-BY-4.0"` (**L221**) → **CC0** (or `CC0-1.0`); `citation="…v1.3.0"` (**L222**) → **v2.0.0**; docstring "v1.3.0" (**L1**). (The naive `max_samples` head-truncation at **L82** is **not** the powered sampler — that is exactly why CAP-02 adds one in eval-data; it is left as-is for standalone use.)
- `pii-rate-elo-pipeline/src/pii_rate_elo_pipeline/schema.py` (**package root**, not `datasets/`): `version: str = "1.3.0"` (**L137**) → **2.0.0**; the second `"version": "1.3.0"` (**L752**) → **2.0.0**; docstrings. The normalizer `_normalize_eval_row` (**L334**) already reads `annotations` with a `labels` fallback (**L349**) — so **the drift is metadata-provenance (count/version/license/citation), NOT field-reading**; the parser already speaks v2.0.0's annotation shape.
- A **versioned crosswalk** + the **5-tuple regression contract** (FR-030/031; NFR-040/041): pins `{version==2.0.0, record_count==575,604, entity-type count==63 (derived from `taxonomy.ENTITY_TYPE_COUNT`), schema fingerprint (annotation keys), dataset content hash}`. Canonical pins from eval-data `tests/test_doc_drift.py` (`CANONICAL_RECORDS="575,604"`, `CANONICAL_ANNOTATIONS="2,486,438"`, `CANONICAL_VERSION="2.0.0"`). The contract test mutates each pin in turn and asserts RED.

**Justification (grounded in firsthand code facts):**
1. **`load_dataset` takes NO version arg** (`src/pii_anon_datasets/__init__.py:55` — `load_dataset(*, subset, domain, split, language, dimension)`); it resolves the version from eval-data's package + a fixed corpus path. Importing it into pii-rate-elo would **couple the consumer's loader to eval-data's package layout** and surrender pii-rate-elo's ability to be installed/run standalone — for **zero** version-selection benefit (the consumer cannot even ask for a version).
2. **The fix is small and bounded** because the drift is metadata-provenance pins only (the normalizer already reads `annotations`). A 5-line metadata correction + a regression contract is a far smaller, more auditable change surface than a cross-repo import dependency, and it keeps the change inside NFR-040/041's bounds.
3. **Decoupling keeps the seam at the manifest, not a Python import** (L1). The cross-repo data contract is the **sample-manifest**; the dataset on disk is read by each side's own parser. A regression contract (5-tuple + content hash) red-flags any future drift **without** an import cycle.
4. **The reverse direction stays forbidden**: eval-data NEVER imports pii-rate-elo (eval-data OWNS reporting and must stay standalone). pii-rate-elo imports `pii_anon_datasets.{assessment,stats}` (one-way, shared venv).

**Path resolution note (verified):** `resolve_eval_dataset_path` (`schema.py:583`) walks ancestors to find the v2.0.0 corpus and honors `PII_ANON_DATASET_ROOT` (`schema.py:627`) — so the bundled parser locates the **same** on-disk v2.0.0 corpus the eval-data sampler reads, with no shared import. This is what makes "two parsers, one corpus, one manifest seam" coherent.

---

## 5. The preferred system — Modular (LOCKED)

Two pip-installable packages in one shared venv (`pii-anon-core/.venv`), a one-directional import boundary, and the **sample-manifest as the only cross-repo data coupling**. Pure-stdlib cores; `report.py` the sole lazy-heavy-dep module.

### 5.1 Module list (the L6 map, ratified)

**eval-data — `src/pii_anon_datasets/assessment/` (NEW package — confirmed absent at HEAD; OWNS sample + observability + reporting):**

| Module | DC(s) | Responsibility | Reuses (verified APIs) | Deps |
|---|---|---|---|---|
| `__init__.py` | — | re-export `assessment` surface + `stats` passthrough | — | stdlib |
| `sample.py` | DC-17/18 | single-streaming-pass seeded lattice sampler (Algorithm-R) → emits manifest | `stats/power.py` (`required_n`/`TIER_SPECS`/`classify`), `stats/lattice.py` (`build_committed_lattice`/`--check` 730@`47c3a8f`), `scripts/lattice_audit.py` (`audit_positives`/`deficits`), `subsets/slices.py`, `benchmark_throughput.py::reservoir_sample` | **stdlib only** |
| `manifest.py` | DC-19 | read/write the L1 SEAM manifest; canonical-form (sorted keys + fixed float repr); non-strippable caveat | `scripts/write_manifest.py` (sha256), `scoring/detection.py::DesignProvenance` | **stdlib only** |
| `runrecord.py` | DC-25 | append-only (write-once) emitter; 6 stage records, shared run id, provenance block | `benchmark_throughput.py` RUNRECORD pattern (`build_run_record`, provenance `{is_reference_host, environment, canonical_verdict}`), `write_manifest.py` | **stdlib only** |
| `prereg.py` | DC-24 | immutable, commit-anchored, hash-chained pre-registration | `write_manifest.py` hashing; commit-on-remote oracle `git branch -r --contains <sha>` (subprocess) | **stdlib only** |
| `verdicts.py` | DC-18/28 | pure power-class / convergence / honesty-flag derivation (enums) | `stats/power.py::PowerClass`/`PowerMatrix.verdict()` | **stdlib only** |
| `report.py` | DC-26/27/28 | projection: audited CIs + paired tests + Holm + tie-gated leaderboard/figures; self-verifying header | `stats/intervals.py` (Wilson/CP), `stats/paired.py` (McNemar/bootstrap), **new** `stats` Holm primitive (SP-S4), `DesignProvenance` | stdlib core; **lazy** numpy/matplotlib in figure code only (SP-S5) |

**audited `stats/` (EXISTING — extend, do not relocate):** add **Holm–Bonferroni** (SP-S4, verified absent) next to `intervals.py`/`paired.py`/`power.py`/`lattice.py`. All pure-stdlib, integer-guarded.

**pii-rate-elo (CONSUMES — thin adapter; do NOT rebuild engine/metrics/convergence):**

| Artifact | DC(s) | Responsibility |
|---|---|---|
| `configs/assessment.yaml` | DC-20 | the assessment preset; **`analysis.run_significance_tests: false`** (P1, SP-S2) |
| `cli.py` `assessment` command | DC-20/21 | second L3 entrypoint: `pii-rate-elo assessment --sample manifest.json --config configs/assessment.yaml --out results/` |
| assessment adapter (thin) | DC-21 | load manifest → run `PIIRateEloEngine` + `ConvergenceChecker` (Glicko RD) + `compute_span_metrics` → hand per-system/per-record outcomes to `pii_anon_datasets.assessment.report` |
| `datasets/converters/pii_anon_eval.py` + `schema.py` fix | DC-16 | v2.0.0 metadata pins + 5-tuple regression contract (§4) |

### 5.2 Dependency graph (one-way; eval-data never imports pii-rate-elo)

```
                         shared venv: pii-anon-core/.venv (py 3.10.6)
  ┌───────────────────────────────────────────────────────────────────────────────┐
  │  eval-data  (pii_anon_datasets)  — OWNS sample + observability + reporting       │
  │                                                                                 │
  │   assessment.sample ─uses→ stats.power, stats.lattice, scripts.lattice_audit,   │
  │                            subsets.slices, scripts.benchmark_throughput          │
  │   assessment.manifest ─uses→ scripts.write_manifest, scoring.detection          │
  │   assessment.runrecord ─uses→ scripts.benchmark_throughput, scripts.write_manifest│
  │   assessment.prereg ─uses→ scripts.write_manifest   (+ git subprocess oracle)    │
  │   assessment.verdicts ─uses→ stats.power                                          │
  │   assessment.report ─uses→ stats.intervals, stats.paired, stats.<HOLM new>,      │
  │                            scoring.detection   [lazy: numpy/matplotlib figs only]│
  └───────────────────────────────────────────────────────────────────────────────┘
                       ▲                                   ▲
        (1) imports    │ pii_anon_datasets.assessment      │ pii_anon_datasets.stats
            ───────────┘  + .stats   (ONE-WAY; the only    │
                          Python coupling, in shared venv) │
  ┌───────────────────────────────────────────────────────────────────────────────┐
  │  pii-rate-elo  (pii_rate_elo_pipeline) — CONSUMES (extend, do NOT rebuild)       │
  │   cli.py:assessment ─→ thin adapter ─→ PIIRateEloEngine + ConvergenceChecker     │
  │                       └─→ hands outcomes to pii_anon_datasets.assessment.report  │
  │   datasets/converters/pii_anon_eval.py + schema.py  = v2.0.0 fix + 5-tuple pin   │
  │   (bundled parser STAYS standalone-installable — L4; reads the on-disk corpus    │
  │    via resolve_eval_dataset_path / PII_ANON_DATASET_ROOT — NO import of load_dataset)│
  └───────────────────────────────────────────────────────────────────────────────┘

  DATA SEAM (L1, the ONLY cross-process coupling):
     (eval-data) assessment.sample  ──writes──▶  sample-manifest.json  ──read──▶  (pii-rate-elo) adapter
     v2.0.0 corpus on disk  ◀──read by BOTH sides' own parsers (no shared import)──▶

  FORBIDDEN EDGE:  eval-data ──X──▶ pii-rate-elo   (eval-data stays standalone; OWNS reporting)
```

### 5.3 The seam contract (the load-bearing schema — L1)

The **sample-manifest** is the sole data coupling between the two repos. Its contract (written by `assessment.manifest`, read by the pii-rate-elo adapter), grounded in D1 DC-19 + D2 SP-W5 + the cited NFRs:

| Field group | Contents | Serves |
|---|---|---|
| `record_ids` | the exact corpus record ids the run scores (the adapter scores **only** these) | L1 seam; FR-034 |
| `per_cell_draw` | per-(entity-type × language) cell: realized positive count, draw provenance, `power_class ∈ {WELL_POWERED, UNDER_SAMPLED, CORPUS_LIMITED, EMPTY, NOT_ASSESSED}`, integer `realized_positive_shortfall` | NFR-035/036/037 |
| `design_point` | per-tier `(p_ref, half_width, α)` triple + coverage envelope (which of 63 types × langs × domains committed) | NFR-039 |
| `power_verdict` | `PowerMatrix.verdict()` ∈ {SMALL, ADEQUATE, LARGE} | NFR-035 |
| `repro` | `seed`, RNG fingerprint (algorithm + seed-derivation), `lattice_version` (730@`47c3a8f`), sampler commit (`subsets/slices.py` + `stats/power.py` hash) | NFR-030/021/038 |
| `run_type` / `preset` | the upfront selector (`smoke`/`dev`/`leaderboard-submission`/`filing-grade`; preset `powered-representative`/`full`/`smoke`) | NFR-033/034 |
| `caveat` | non-strippable synthetic-only / anti-anonymity caveat (`DesignProvenance` `__post_init__` raises on empty) | NFR-044 |
| `provenance` | producing `{run_id, stage, code_commit, content_hash}` | NFR-042/043 |

**Canonical-form equality (NFR-030):** sorted keys + fixed float repr; re-running the sampler from the recorded `repro` block reproduces the manifest under canonical-form equality and every seeded artifact byte-identically. **Standalone invariant:** the manifest is the only thing pii-rate-elo needs from eval-data's *data* side; its bundled parser independently reads the on-disk v2.0.0 corpus.

---

## 6. NFR adherence (system-level projection)

| NFR | Threshold (abbrev.) | Achievability | Rationale |
|---|---|:---:|---|
| **NFR-019/020/021/022** (P1) | `SignificanceTester` unreachable; `run_significance_tests==false`; no approximated stats; LOCAL-RNG; integer-guarded | **high** | thin adapter is the single import surface; static import-graph gate + config assertion (SP-S2); report calls audited `stats/*` only |
| **NFR-030** | canonical-form manifest + byte-identical seeded artifacts | **high** | in-process modules, single seeded `random.Random`, no concurrency nondeterminism; manifest `repro` block carries seed + RNG fingerprint + sampler commit |
| **NFR-038** | single streaming pass; working set ≤ 730 keys; O(1)/annotation | **high** | direct reuse of `lattice_audit.audit_positives` (structural O-bound, not RSS) + `reservoir_sample` |
| **NFR-040/041** (P2) | v2.0.0 conjunction + 5-tuple red-on-drift | **high** | metadata-provenance pins only; normalizer already reads `annotations`; regression contract mutates each pin → RED (§4) |
| **NFR-042/043** | 6 stage records, shared run id, code_commit + toolchain; file-level provenance | **high** | reuse `benchmark_throughput` RUNRECORD pattern; write-once discipline (SP-S3) |
| **NFR-050** | stdlib-only cores; heavy dep lazy-guarded | **high** | `report.py` is the sole lazy-numpy/matplotlib module (SP-S5); cores import math/random only |
| **NFR-051** | pii-rate-elo `pytest`+`ruff`+`mypy` green | **medium** | small edit surface (metadata pins + thin adapter) but cross-venv; mitigated by the manifest seam keeping coupling to one import surface |
| **NFR-052/053/054/055** | lattice 730@`47c3a8f`; power gate ON; doc-drift 0; four families never merged | **high** | no corpus regeneration; reused gates unchanged; CAP-02-added modules carry the static no-merge check |
| **NFR-010b** (inherited) | ≥5000 rec/sec lightweight detection, 8-core ref host | **low / INSUFFICIENT_EVIDENCE** | inherited unchanged; needs a reference-host run (out of scope; `real_user_needed: true`) |

---

## 7. Constraints on D5 (Architecture)

- **Dependency direction (hard):** pii-rate-elo → `pii_anon_datasets.{assessment, stats}` only; **eval-data NEVER imports pii-rate-elo**. The manifest is the sole data seam.
- **Deployment grain:** in-process modules in one shared venv (two pip-installable packages); **no** services, **no** event bus, **no** broker (SP-S1).
- **Module boundaries:** pure-stdlib cores (`sample`/`manifest`/`runrecord`/`prereg`/`verdicts` + reused `stats/*`); `report.py` the **only** module permitted lazy numpy/matplotlib (figure code) (SP-S5).
- **L4 (resolved):** FIX the bundled parser to v2.0.0 + 5-tuple regression contract; reserve `load_dataset` for the eval-data sampler side; bundled parser stays standalone-installable (§4).
- **P1 mechanism:** two CI predicates — static import-graph unreachability of `SignificanceTester` **and** `run_significance_tests == False` (SP-S2); "green requires no human."
- **Holm–Bonferroni:** new primitive in audited `stats/` (verified absent), **never** in `significance.py` (SP-S4).
- **Persistence:** write-once content-hashed JSON artifacts (manifest, 6 run-records, pre-reg, results, figures) with append-only discipline — **not** an event-sourcing store (SP-S3).
- **Seam schema:** the §5.3 manifest contract is the load-bearing inter-process schema D5 must specify in full (field types, canonical-form serialization rule).

---

## 8. What feeds the next diamond (D5 Architecture)

D5 inherits a **Modular, in-process, two-package system** with a one-way dependency (pii-rate-elo → eval-data), the **manifest as the sole data seam**, pure-stdlib cores + a single lazy-heavy-dep module, and a **resolved L4** (fix-bundled-parser + 5-tuple contract). The load-bearing artifacts D5 must detail: (1) the **sample-manifest schema** (§5.3) including canonical-form serialization; (2) the **run-record schema** (6 stages, shared run id, provenance block) reusing the `benchmark_throughput` pattern; (3) the **pre-reg hash-chain** + commit-on-remote oracle; (4) the **new Holm primitive** signature in `stats/`; (5) the **P1 static-import-gate** spec (the exact import-graph predicate). The two named system switch-points carried forward are **SP-S2** (P1 = static gate + config flag) and **SP-S3** (write-once artifacts, not event sourcing); the simplicity win (A's in-process grain, SP-S1) is absorbed into the Modular shape rather than carried as an open fork.

---

## 9. Decision record (machine-readable)

```yaml
d4_system_converge:
  chosen_frame: B
  chosen_archetype: modular            # cycle-1 precedent confirmed; in-process modules, one shared venv
  datum: B
  weighted_totals: { A_monolith: -0.12, B_modular: 0.00, C_event_sourced: -0.34 }
  primary_data_shape: hybrid           # streaming sample -> json manifest/run-records -> relational metric rows
  replay_capability: partial           # byte-reproducible-from-manifest (NFR-030), not event-sourced
  operational_complexity: medium       # two pip packages, shared venv, two chained CLIs; no service infra
  loader_decision: fix-bundled-parser  # L4 RESOLVED; reserve load_dataset for eval-data sampler side
  dependency_direction: "pii-rate-elo -> pii_anon_datasets.{assessment,stats}; eval-data NEVER imports pii-rate-elo"
  sole_data_seam: sample-manifest.json
  switch_points:
    - id: SP-S1
      decision: "in-process modules in one shared venv (B with A's monolith grain); no bus/broker/services"
    - id: SP-S2
      decision: "P1 = static import-graph unreachability of SignificanceTester AND run_significance_tests==false"
    - id: SP-S3
      decision: "write-once content-hashed JSON artifacts with append-only discipline; NOT event sourcing (C absorbed as discipline)"
    - id: SP-S4
      decision: "Holm-Bonferroni = net-new primitive in audited stats/ (verified absent); never in significance.py"
    - id: SP-S5
      decision: "report.py is the sole lazy-heavy-dep module (numpy/matplotlib in figure code only)"
    - id: SP-S6
      decision: "L4 -> fix bundled parser (see loader_decision)"
  modules_eval_data:
    package: "src/pii_anon_datasets/assessment/"
    new: [__init__.py, sample.py, manifest.py, runrecord.py, prereg.py, report.py, verdicts.py]
    stats_extension: "Holm-Bonferroni added to existing audited stats/ (pure-stdlib)"
  modules_pii_rate_elo:
    - "configs/assessment.yaml (run_significance_tests: false)"
    - "cli.py assessment command (2nd L3 entrypoint)"
    - "thin assessment adapter (load manifest -> engine+convergence -> report)"
    - "datasets/converters/pii_anon_eval.py + schema.py v2.0.0 fix + 5-tuple regression contract"
  nfr_adherence:
    - { nfr: NFR-019, projected_achievability: high }
    - { nfr: NFR-030, projected_achievability: high }
    - { nfr: NFR-038, projected_achievability: high }
    - { nfr: NFR-040, projected_achievability: high }
    - { nfr: NFR-042, projected_achievability: high }
    - { nfr: NFR-050, projected_achievability: high }
    - { nfr: NFR-051, projected_achievability: medium }
    - { nfr: NFR-010b, projected_achievability: low }   # inherited; INSUFFICIENT_EVIDENCE; out of scope
  no_regression_respected: true        # lattice 730@47c3a8f; NFR-018 power gate ON; doc-drift 0; four families separate; no corpus regen
  context_bounds_respected: true
  provisional_status: AGENT_SIMULATED
```

---

✅ **D4 CONVERGE complete (2026-06-01).** Pugh-compared 3 system archetypes (A Monolith / B Modular / C Event-Sourced) against the brief's five criteria; **Frame B (Modular) preferred (datum; 0.00; A −0.12, C −0.34)** — confirming the cycle-1 precedent — enriched with **A's in-process grain + static-import-gate insight** (SP-S1/SP-S2) and **C's immutability discipline** (SP-S3, absorbed without an event-sourcing engine). **L4 RESOLVED: FIX the pii-rate-elo bundled parser to v2.0.0 + 5-tuple regression contract; reserve `load_dataset` for the eval-data sampler side** — grounded in the verified fact that `load_dataset` has no version arg and the drift is metadata-provenance only. Six switch-points named + resolved (SP-S1…S6). Module list + one-way dependency graph + the L1 seam contract written. No-regression rails honored. `provisional_status: AGENT_SIMULATED`. Ready for D5 (Architecture).
