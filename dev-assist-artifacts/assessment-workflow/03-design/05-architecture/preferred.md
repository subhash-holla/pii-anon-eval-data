# CAP-02 — D5 CONVERGE: Preferred Architecture

**Capability**: CAP-02 — academically-sound, repeatable, reportable assessment **workflow** that runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 / CC0 / `annotations`** over a **powered-representative sample (CLI default)** / **full corpus (opt-in, citable)** / **smoke (fast CI)**, with statistical/epistemic observability + reporting at every spine stage `load → sample → run → score → rate → report`.
**Stage**: assessment-workflow / 03-Design · **Diamond 5 (Architecture) — CONVERGE**
**Date**: 2026-06-01
**provisional_status**: AGENT_SIMULATED — the pattern is selected by agent-simulated Pugh scoring against the requirements + the **verified code seams** (direct file-read at HEAD 2026-06-01; paths + line numbers cited inline). Refactor/onboarding costs are pattern-extrapolated, validated only by Stage 4 execution. No new high-stakes user-validation commitment is introduced here.

> **Vocabulary remap.** DC = **Benchmark Component**; FR = Assessment Capability; UC = Evaluation Scenario; NFR = Quality Attribute; AX = binding axiom.

> **What D4 LOCKED (this diamond inherits, does NOT re-open).** A **Modular, in-process, two-package system** in one shared venv (`pii-anon-core/.venv`); one-way dependency (`pii-rate-elo → pii_anon_datasets.{assessment,stats}`, **eval-data NEVER imports pii-rate-elo**); the **sample-manifest is the sole cross-process data seam** (L1); pure-stdlib cores + `report.py` the only lazy-heavy-dep module (SP-S5); **L4 RESOLVED = fix the bundled parser** + 5-tuple regression contract (SP-S6); P1 = **static import-graph unreachability of `SignificanceTester` AND `run_significance_tests==false`** (SP-S2); write-once content-hashed artifacts, not event sourcing (SP-S3); Holm–Bonferroni = net-new audited `stats/` primitive (SP-S4). **D5 picks the in-process software-architecture pattern that turns the D4 invariant — "audited stats are the domain core; the pii-rate-elo engine + loader + figures are replaceable infrastructure" — into a STRUCTURAL property, and specifies the exact import-boundary rule that makes `significance.py` unreachable.**

---

## 1. The three architecture proposals (DIVERGE recap)

| Frame | Pattern | Core idea | P1 enforcement style | Signature move |
|---|---|---|---|---|
| **A** | **Hexagonal (Ports & Adapters)** | audited `stats` + `assessment` logic = the domain hexagon; engine/loader/figures = adapters behind Protocol ports the domain never names | adapter is the **single import surface** the static gate scans; `significance` is an adapter the domain cannot reach | in-memory port fakes = mock-free domain tests; new detector = new `TournamentRunner` adapter |
| **B** | **Clean (Layered, 4 concentric rings)** | Entities (`stats`/power/lattice) → Use Cases (`assessment`) → Interface Adapters (engine/loader/figures + `significance`) → Frameworks (CLIs/venv) | the **dependency rule** ("inner never imports outer") puts `significance` in an outer ring on a disjoint sub-graph | rings are familiar; the one rule is lint-enforceable; 8 named seams |
| **C** | **Capability-based** | audited core is the only **minter** of unforgeable `InferenceCap` tokens; every inference fn refuses to compute without one | `significance`/the engine adapter **never hold an `InferenceCap`** → cannot emit an inference number even if reached | latent multi-tenant/sandbox-plugin power; trust line = the cap mint-surface |

All three share the D4-locked substrate: two pip packages, one-way import, the manifest seam, pure-stdlib cores + one lazy-heavy-dep module, write-once artifacts, the 5-tuple dataset contract, Holm as a new audited primitive, and **two CI predicates** for P1 (static import-graph + config flag).

---

## 2. Pugh comparison (the brief's five named criteria)

**Datum = Frame A (Hexagonal).** The brief names the **cycle-1 precedent = "Hexagonal scoring core (Clean inside `stats`)"**, and D4 framed its invariant in literal ports-and-adapters terms ("audited stats are the domain core; engine/loader/figures are replaceable infrastructure"). Scores: **+1** better than datum / **0** equal / **−1** worse.

Weights are the brief's five named criteria, normalized to sum 1.00. **Enforce-audited-stats-only as a structural invariant** carries the highest weight — it is P1, the SHOWSTOPPER precondition, and the entire reason this diamond exists. **Testability** is next (the whole stack is `pytest`/`ruff`/`mypy`-gated on both sides, NFR-051, and the P1 quarantine is itself a *testable* import-graph predicate, NFR-019). **Reuse** and **extension seams for new detector systems** are real and weighted together in the middle (D4 maximized reuse via the verified-API map; AX/FR ask for new-system extensibility). **Simplicity** is the brief's named tie-breaker, weighted last.

| Criterion | Weight | A (Hexagonal) = datum | B (Clean) | C (Capability) |
|---|---:|:---:|:---:|:---:|
| **Enforce-audited-stats-only as a structural invariant** (P1: `significance.py` unreachable by construction, not by config discipline) | 0.34 | **0 (datum)** | 0 | **+1** |
| **Testability** (domain testable mock-free; P1 an isolatable predicate; gates green) | 0.24 | **0 (datum)** | 0 | −1 |
| **Reuse of eval-data modules** (DC titles map 1:1 to verified reuse APIs) | 0.14 | **0 (datum)** | 0 | 0 |
| **Extension seams for new detector systems** (drop in a new rater/loader without touching the core) | 0.16 | **0 (datum)** | 0 | 0 |
| **Simplicity** (fewest concepts; cycle-1 consistency; no machinery the reqs don't demand) | 0.12 | **0 (datum)** | 0 | −1 |
| **Weighted total** | 1.00 | **0.00** | **0.00** | **−0.02** |

### Score rationale (per criterion)

- **Enforce-audited-stats-only — A 0 (datum); B 0; C +1.** This is the load-bearing axis. **A (Hexagonal)** makes the invariant structural via the *dependency-direction rule*: the domain (`stats` + `assessment`) defines ports (Protocols) and imports **nothing** from adapters; the `EloEngineAdapter` is the single import surface that touches `pii-rate-elo`, so a static walk of one file proves `significance` unreachable. **B (Clean)** achieves the identical structural guarantee through the same mechanism dressed as four rings — `significance` sits in Ring 3 (Interface Adapters), Ring 1/2 never import Ring 3, so it is on a disjoint sub-graph; *equal to A* (both rely on import-direction, both verified by the same import-graph predicate). **C (Capability) genuinely wins (+1):** it enforces P1 at a *deeper* layer — even if a future refactor accidentally let the engine adapter reach an inference function, that function **refuses to compute without an `InferenceCap`**, and the cap can only be minted by the audited core. C converts "unreachable" (a graph property A/B must keep true) into "powerless even if reached" (an authority property). For the SHOWSTOPPER precondition, that defence-in-depth is the strongest honest score. **This is the only axis where any frame beats the datum, and it is the heaviest — so the choice hinges on whether C's structural win survives the other four axes.**

- **Testability — A 0 (datum); B 0; C −1.** **A's headline payoff:** the domain is tested against **in-memory port fakes** (`InMemoryCorpusReader`, `FakeTournamentRunner`) — fully deterministic, zero I/O, zero mocking frameworks; "where does my mock go" has a crisp answer (implement the port). **B is equal:** Clean's inner rings are pure functions tested without mocks, and use-case rings mock the engine-outcome DTOs at the inner-facing port — the same testability A has, organized by ring. **C is −1:** the cap idiom adds a test obligation everywhere — every inference test must mint-and-thread a test cap, and the *negative* tests (assert the adapter call-graph holds no cap; assert a mis-minted/stale-version cap is rejected) are net-new surface. The cap machinery replaces DI seams with a token-threading discipline that, for a single-trust linear spine, enlarges the test matrix without a requirement asking for it. The thing that actually matters — audited-stats correctness — is identical work in all three; C just adds cap-plumbing tests around it.

- **Reuse of eval-data modules — all three 0 (equal).** Reuse is fixed by `_engineering-findings-verified.md §3` and the D4 L6 map: every frame composes the **same** verified APIs — `stats/intervals.py` (`wilson_interval`:65 / `clopper_pearson_interval`:170, integer-guarded), `stats/paired.py` (`mcnemar_exact`:62 / `mcnemar_chi2`:82 / `paired_bootstrap_recall_delta`:112, LOCAL `random.Random(seed)`:140), `stats/power.py` (`TIER_SPECS`/`PowerMatrix.verdict()`), `scripts/lattice_audit.py` (`audit_positives`/`deficits`), `scripts/benchmark_throughput.py` (RUNRECORD + `reservoir_sample`), `scoring/detection.py::DesignProvenance`. The pattern changes *how the wiring is arranged*, never *which* modules are reused — so this axis does not separate the frames.

- **Extension seams for new detector systems — all three 0 (equal).** All three give the same extension story for the brief's explicit goal ("runs against new detector systems"): a new rater/detector is a new adapter behind a stable interface (A's `TournamentRunner` Protocol; B's Ring-3 adapter port; C's holder-cap adapter), and the domain core is untouched. The count of *named* seams differs cosmetically (A enumerates 5 ports, B enumerates 8, C enumerates 6) but the load-bearing seam — **swap the rating engine without touching audited stats** — is present and equally clean in all three. No frame lets a new detector reach into the stats core. Honest score: equal.

- **Simplicity — A 0 (datum); B 0; C −1.** **A and B are equally simple in practice:** A's "domain + ports + adapters" and B's "four rings + dependency rule" are two vocabularies for the same small structure (a pure core with import-direction discipline), and for a 6-stage linear spine both are minimal. **C is −1:** capabilities add a genuinely new concept (unforgeable tokens, a mint-surface, every inference fn growing a leading `cap` param) that the **current** requirements do not demand — there is one tenant, one trust domain, one linear flow. C's own DIVERGE frame conceded this ("the cap machinery is overhead the requirements do not yet demand; its value is latent"). For the brief's named tie-breaker, latent value loses to present simplicity.

**Pugh verdict: Frame A (Hexagonal) is preferred (datum; 0.00).** It ties Clean (B, 0.00) and edges out Capability (C, −0.02). The result is **near-degenerate by design** — A and B are structurally the same import-direction discipline, and the brief's cycle-1 precedent ("Hexagonal scoring core (Clean inside `stats`)") *names both at once*. The tie is broken in A's favour, and **B is absorbed, not discarded**: the audited `stats/` core is implemented as a **Clean inner ring** (zero outward deps, pure functions, no port indirection) *inside* the Hexagonal domain. C is **not** chosen for v0.1 but its strongest idea is **carried as a lightweight switch-point** (SP-A2): the audited inference functions are reached **only** through the `report` domain module, and the engine adapter is structurally denied any import path to `stats/*` — a capability-*flavoured* boundary (authority-by-placement) without the full token machinery, preserving an upgrade path to real caps if multi-tenant/sandboxed-plugin requirements ever land.

---

## 3. Switch-points (named, per the brief)

| # | Switch-point | Frames in tension | Resolution (locked for D6 synthesis) |
|---|---|---|---|
| **SP-A1** | **Stats-core shape inside the hexagon**: full ports/adapters everywhere (A) vs a pure Clean ring with no port indirection (B) | A vs B | **CLEAN RING INSIDE THE HEXAGON (adopt B's inner ring; this IS the cycle-1 "Clean inside `stats`").** `stats/{intervals,paired,power,lattice,multitest(new Holm)}` are **pure functions with zero outward imports** — no Protocol port wraps them; the `report` domain module calls them directly. Ports/adapters apply only at the **infrastructure boundary** (corpus, engine, sinks, figures). Rationale: a port in front of `wilson_interval` would be ceremony with no swap requirement; the audited stats are the one thing we never want swappable. |
| **SP-A2** | **Inference authority placement**: plain domain call (A/B) vs capability token (C) | A/B vs C | **AUTHORITY-BY-PLACEMENT (A/B), with C's instinct as a structural rule, NOT a token.** The audited inference functions (`stats/*` + Holm) are imported **only** by the `report` domain module. The `EloEngineAdapter` (and `significance.py`) have **no import path** to `stats/*` — enforced by the same import-graph test that proves P1. This buys C's "fabricated code cannot emit an inference number" guarantee via the dependency graph, **without** threading `cap` params through every signature. Upgrade path preserved: if multi-tenant/sandbox arrives, the `report`→`stats` call becomes a cap-gated call (C) behind the unchanged port surface. |
| **SP-A3** | **P1 gate granularity**: assert symbol `SignificanceTester` unused vs assert **module `analysis.significance` unreachable** | (refinement of SP-S2) | **ASSERT THE MODULE IS UNREACHABLE (strictly stronger than D4's symbol framing).** Verified at HEAD: `significance.py:409` does `_tester_instance = SignificanceTester()` at **module scope** — so *any* import of `analysis.significance` eagerly instantiates the fabricated tester. The gate therefore asserts the **module node** `pii_rate_elo_pipeline.analysis.significance` is absent from the import-closure of the assessment entrypoints (sampler CLI + `assessment` adapter), not merely that the class symbol is unreferenced. (D4 SP-S2 said "SignificanceTester unreachable"; D5 sharpens "the class" → "its module," because of the eager `:409` instantiation.) |
| **SP-A4** | **Port catalog scope**: which infrastructure boundaries become Protocol ports | A | **FIVE PORTS (the infrastructure boundaries only).** `CorpusReader` (stream v2.0.0 records), `TournamentRunner` (manifest → per-system/per-record outcome DTOs), `RunRecordSink` + `PreregSink` (write-once emitters), `FigureRenderer` (CI/leaderboard plots, sole lazy heavy-dep). The **manifest DTO** is the cross-process data contract (not a Protocol — it is serialized JSON). Sampling/verdicts/manifest read-write stay pure domain logic (no port — they are not swappable infrastructure). |
| **SP-A5** | **Dependency-injection mechanism**: framework DI container vs constructor wiring at the CLI edge | A | **CONSTRUCTOR WIRING AT THE CLI EDGE (no DI framework).** The two CLIs (Frameworks layer) are the *composition root*: they instantiate concrete adapters and pass them to the domain. No DI container, no service locator — keeps the stdlib-only-core invariant (NFR-050) and matches D4's "no service infra" grain (SP-S1). Tests substitute in-memory fakes at the same constructor seam. |

---

## 4. The preferred architecture — Hexagonal (Ports & Adapters), Clean inside `stats` (LOCKED)

### 4.1 The hexagon (domain core — eval-data owns; pure stdlib; imports NOTHING from adapters)

**Clean inner ring (pure functions, zero outward deps) — audited `stats/`:**
`intervals` (Wilson/CP), `paired` (McNemar exact/chi2 + paired bootstrap, LOCAL RNG), `power` (`TIER_SPECS`/`PowerMatrix.verdict()`), `lattice` (730 @ `47c3a8f`), **new `multitest`** (Holm–Bonferroni, SP-S4/A1). No port wraps these; `report` calls them directly (SP-A1).

**Domain application logic — `pii_anon_datasets/assessment/`:**
`sample` (DC-17/18 seeded lattice sampler → manifest), `manifest` (DC-19 read/write the L1 seam, canonical-form), `verdicts` (DC-18/28 power-class/convergence/honesty enums), `prereg` (DC-24 hash-chained pre-reg logic), `runrecord` (DC-25 stage-record assembly), `report` (DC-26/27/28 orchestrates ports + calls the Clean stats ring for audited CIs + paired tests + Holm + tie-gated leaderboard). The domain defines the **ports** in `assessment/ports.py` and imports adapters **never**.

### 4.2 Ports (Protocols — `assessment/ports.py`, SP-A4)

| Port (Protocol) | Method contract (shape) | Implemented by (adapter) | Serves |
|---|---|---|---|
| `CorpusReader` | `stream(record_ids) -> Iterable[Record]` | `JsonlCorpusAdapter` (bundled v2.0.0 parser via `resolve_eval_dataset_path` / `PII_ANON_DATASET_ROOT`) | DC-16; FR-034 (score only manifest ids) |
| `TournamentRunner` | `run(manifest, corpus) -> PerSystemOutcomes, PerRecordOutcomes` | `EloEngineAdapter` (wraps `PIIRateEloEngine` + `ConvergenceChecker` + `compute_span_metrics`) | DC-21 |
| `RunRecordSink` | `emit(stage, run_id, record) -> Path` (write-once) | `JsonRunRecordAdapter` (reuses `benchmark_throughput` RUNRECORD) | DC-25; NFR-042/043 |
| `PreregSink` | `commit(prereg) -> Path` (immutable, hash-chained) | `PreregAdapter` (+ `git branch -r --contains <sha>` oracle) | DC-24; NFR-031 |
| `FigureRenderer` | `render(figure_spec) -> Path` | `MatplotlibFigureAdapter` (**sole** lazy numpy/matplotlib, SP-S5) | DC-27 |

The **manifest DTO** is the only data crossing the process seam (serialized JSON, §5.3 of D4); adapters cannot inject stats into the core — they hand the core *outcome DTOs*, and the core computes every inference number itself.

### 4.3 Adapters (infrastructure — replaceable; the only code that names `pii-rate-elo` or heavy deps)

- **`EloEngineAdapter`** (pii-rate-elo side): the **single import surface** between the repos. Wires the engine; **must not import `analysis.significance`** (the P1 gate scans exactly this module's closure).
- **`JsonlCorpusAdapter`** (pii-rate-elo side): the bundled parser, fixed to v2.0.0 (SP-S6 / L4); stays standalone-installable; reads the same on-disk corpus the eval-data sampler reads (no shared import).
- **`JsonRunRecordAdapter` / `PreregAdapter`** (eval-data side): write-once JSON sinks (SP-S3).
- **`MatplotlibFigureAdapter`** (eval-data side, inside `report`): lazy numpy/matplotlib in figure functions only (SP-S5).

### 4.4 Composition root (Frameworks layer — SP-A5)

Two CLIs wire concrete adapters into the domain by constructor injection (no DI framework):
- eval-data: `python -m pii_anon_datasets.assessment.sample --preset … --seed … --out sample-manifest.json` (L3a).
- pii-rate-elo: `pii-rate-elo assessment --sample sample-manifest.json --config configs/assessment.yaml --out results/` (L3b) → instantiates `EloEngineAdapter` + `JsonlCorpusAdapter`, hands outcome DTOs to `pii_anon_datasets.assessment.report`, which constructs `JsonRunRecordAdapter` + `MatplotlibFigureAdapter` and computes the audited stats.

### 4.5 Dependency-direction rule (the architectural invariant)

```
        DOMAIN HEXAGON (eval-data: pii_anon_datasets.{stats, assessment})
        ─ imports ONLY stdlib + its own ports; NEVER an adapter, NEVER pii-rate-elo ─
                 │ defines ports (Protocols)                ▲ calls Clean stats ring directly
                 ▼                                          │ (no port — SP-A1)
   ┌──────────────────────────────────────────────────────────────────────┐
   │ ADAPTERS (infrastructure) — implement ports; the ONLY code that names: │
   │   • pii-rate-elo engine  → EloEngineAdapter   (single cross-repo surface)│
   │   • bundled v2.0.0 parser → JsonlCorpusAdapter                          │
   │   • numpy/matplotlib      → MatplotlibFigureAdapter (lazy, figures only) │
   │   • analysis.significance → NOT an adapter here; on a DISJOINT sub-graph │
   └──────────────────────────────────────────────────────────────────────┘
                 ▲ wired by                                  
   ┌──────────────────────────────────────────────────────────────────────┐
   │ COMPOSITION ROOT (Frameworks): the two CLIs (constructor injection)     │
   └──────────────────────────────────────────────────────────────────────┘

   DATA SEAM (L1, sole cross-process coupling): sample-manifest.json (DTO)
   FORBIDDEN EDGES:  domain ──X──▶ adapters/pii-rate-elo ;  any assessment node ──X──▶ analysis.significance
```

---

## 5. THE IMPORT-BOUNDARY RULE that makes `significance.py` unreachable (P1 — the canonical NFR-019 mechanism)

This is the load-bearing deliverable of D5. P1 is enforced as a **conjunction of two CI predicates**, "green requires no human":

**Predicate (a) — static import-graph unreachability of the FABRICATED MODULE (SP-A3, strictly stronger than D4):**
Build the import closure (transitive `import`/`from … import`) starting from **both** assessment entrypoints —
1. the eval-data sampler CLI `pii_anon_datasets.assessment.sample`, and
2. the pii-rate-elo `assessment` command + its thin adapter (`EloEngineAdapter`).
**Assert the module node `pii_rate_elo_pipeline.analysis.significance` is NOT in either closure.** Module-level, not symbol-level, because — verified at HEAD 2026-06-01 — `significance.py:409` runs `_tester_instance = SignificanceTester()` at import time (class at `:90`); thus *importing the module at all* eagerly constructs the fabricated tester. The Hexagonal payoff: the `EloEngineAdapter` is the **single import surface** touching pii-rate-elo, so the predicate scans one well-known node's closure. The pre-existing eager import lives only at the standalone `cli.py:33` (`from .analysis.significance import SignificanceTester`) → `cli.py:240` flag → `cli.py:242` instantiation; the `assessment` command must **not** route through that module-level import — i.e., the assessment entrypoint imports the engine/convergence/metrics symbols **without** importing the `cli` module's `significance` line (the adapter imports `tournament.engine` / `tournament.convergence` / `evaluation.metrics_bridge` directly, never `analysis.significance`).

**Predicate (b) — runtime config assertion:**
`configs/assessment.yaml` sets `analysis.run_significance_tests: false`, and a test asserts the loaded `PipelineConfig.analysis.run_significance_tests == False` for the assessment preset. Belt-and-suspenders with (a): even on the standalone `run` path, the flag gates the `cli.py:242` instantiation; on the `assessment` path, (a) guarantees the module is never imported in the first place.

**Why the dependency-direction rule makes this true by construction (not by discipline):**
The audited inference functions (`stats/*` + Holm) are imported **only** by the `report` domain module (SP-A2). The `report` core imports **nothing** from `pii-rate-elo` — it consumes `TournamentRunner` *outcome DTOs*. The `EloEngineAdapter` wires the engine but has **no import edge** to `stats/*` *or* to `analysis.significance`. Therefore `SignificanceTester` is on a sub-graph **disjoint** from the assessment call path, and the fabricated stats can neither be reached nor (SP-A2) emit an inference number even if a future edit reached them. The single import-graph test enforces all three forbidden edges at once: `domain ↛ adapter`, `assessment ↛ analysis.significance`, and `EloEngineAdapter ↛ stats/*`.

**Test placement:** the P1 predicate lives in **eval-data** (the OWNS side) as a contract test over both entrypoints; a mirror `mypy`/import-lint runs in pii-rate-elo CI (NFR-051). Mutating either predicate (add the import edge; flip the flag to `true`) must turn the gate **RED**.

---

## 6. Test architecture (the Hexagonal payoff)

- **Unit (domain):** the hexagon against **in-memory port fakes** — `InMemoryCorpusReader`, `FakeTournamentRunner`, `RecordingSink` — fully deterministic, zero I/O, no mocking framework. The Clean `stats/` ring needs **no** fakes (pure, seeded, integer-guarded). This is the reason Hexagonal wins testability.
- **Contract:** each adapter ⊨ its Protocol (substitutability); the **dataset 5-tuple** test (`{version==2.0.0, record_count==575,604, entity-type count==63, schema fingerprint, content hash}` — mutate each pin → RED, SP-S6); the **manifest canonical-form** test (NFR-030, sorted keys + fixed float repr, byte-repro from the `repro` block).
- **P1 gate (NFR-019):** the two predicates of §5 (module-unreachability + config-false), each independently RED-on-violation.
- **Integration:** real adapters end-to-end on the **smoke** preset (CI-fast; inferential fields suppressed); byte-repro from the manifest `repro` block.
- **E2E:** the chained two-CLI one-command example; both repos' gates (`pytest`/`ruff`/`mypy`) green (NFR-051).

---

## 7. Refactor & onboarding cost (AGENT_SIMULATED — pattern-extrapolated)

- **Add a new DC:** **low** — a new domain function (sampling/verdict/report logic) or a new adapter behind an existing port.
- **Swap D4's loader / data store:** **low** — replace the `CorpusReader` adapter; the core is untouched (the headline Hexagonal win, matching D4's L4 "loader is replaceable behind the seam").
- **Add a new detector/rating engine:** **low** — a new `TournamentRunner` adapter; audited stats untouched (the brief's explicit extensibility goal).
- **Add multi-tenant / sandboxed plugins:** **medium** — Hexagonal threads a context param through ports; **this is the one axis where Frame C would have been first-class.** Out of v0.1 scope; SP-A2 preserves the upgrade path (port surface unchanged; `report→stats` becomes cap-gated). Flagged honestly, not hidden.
- **Onboarding time-to-first-PR:** **medium** — contributors learn the port/adapter indirection + the dependency-direction rule ("the domain never imports an adapter; the engine adapter never imports `stats` or `significance`") before the first change; both are lint/import-graph-enforced, so violations fail fast. Docs needed: the 5-port catalog + the adapter-authoring guide + the §5 P1 predicate.

---

## 8. NFR / axiom adherence (architecture-level)

| NFR / AX | Threshold (abbrev.) | Achievability | Rationale |
|---|---|:---:|---|
| **NFR-019** (P1) | `analysis.significance` unreachable from assessment entrypoints; `run_significance_tests==false` | **high** | §5 two predicates; module-level gate (SP-A3); single adapter import surface (Hexagonal) |
| **NFR-020/021/022** | no approximated stats on the run path; LOCAL-RNG; integer-guarded | **high** | `report` calls only the audited Clean `stats/` ring (SP-A1); `EloEngineAdapter ↛ stats/*` |
| **NFR-027** | Holm–Bonferroni multiplicity control | **high** | new audited `stats/multitest` primitive (SP-S4); deterministic; unit-tested |
| **NFR-030** | canonical-form manifest + byte-repro | **high** | manifest DTO + `repro` block; constructor-wired single seeded RNG; no concurrency nondeterminism |
| **NFR-040/041** (P2) | v2.0.0 conjunction; 5-tuple red-on-drift | **high** | `JsonlCorpusAdapter` v2.0.0 fix + contract test (SP-S6); normalizer already reads `annotations` |
| **NFR-042/043** | 6 stage records, shared run id; file-level provenance | **high** | `RunRecordSink` reusing `benchmark_throughput` RUNRECORD; write-once (SP-S3) |
| **NFR-050** | stdlib-only cores; heavy dep lazy-guarded | **high** | hexagon + ports are stdlib; `MatplotlibFigureAdapter` is the sole lazy numpy/matplotlib (SP-S5); no DI framework (SP-A5) |
| **NFR-051** | pii-rate-elo `pytest`+`ruff`+`mypy` green | **medium** | small adapter surface; mirror import-lint asserts the forbidden edges; cross-venv risk mitigated by the single import surface |
| **NFR-052/053/054/055** | lattice 730@`47c3a8f`; power gate ON; doc-drift 0; four families never merged | **high** | no corpus regeneration; reused gates unchanged; `report` carries the static no-merge check (AX-004) |
| **AX-001..005** | audited-stats-only, honesty, provenance, four-families-separate, non-strippable caveat | **high** | AX-001/002/003/004 structurally supported by the dependency rule + write-once provenance; AX-005 caveat via `DesignProvenance` `__post_init__` empty-guard |

---

## 9. What feeds the next diamond (D6 Synthesis)

D6 inherits an **implementation-ready Hexagonal architecture with a Clean `stats/` inner ring**: a pure-stdlib domain hexagon (`pii_anon_datasets.{stats, assessment}`) that defines **5 ports** + the **manifest DTO**, four replaceable adapters (engine, loader, sinks, figures), a two-CLI composition root with constructor injection, and — the load-bearing deliverable — **the §5 import-boundary rule** that makes the fabricated `analysis.significance` **module** unreachable from both assessment entrypoints (the canonical NFR-019 gate, sharpened to module-level because of the eager `:409` instantiation). The named switch-points carried forward: **SP-A1** (Clean ring, no port over stats), **SP-A2** (authority-by-placement; C's upgrade path reserved), **SP-A3** (module-level P1 gate), **SP-A4** (5-port catalog), **SP-A5** (no DI framework). D6 must reconcile this with the D1–D3 cascade (design cases / workflow / UI) and run the synthesis-stage user research + SME heuristic evaluations.

---

## 10. Decision record (machine-readable)

```yaml
d5_architecture_converge:
  chosen_frame: A
  chosen_pattern: hexagonal_ports_and_adapters   # cycle-1 precedent: "Hexagonal scoring core (Clean inside stats)"
  datum: A
  inner_core_style: clean_layered                # B absorbed: audited stats/ = a pure Clean inner ring (no port)
  weighted_totals: { A_hexagonal: 0.00, B_clean: 0.00, C_capability: -0.02 }
  testability_rating: high
  port_count: 5                                  # CorpusReader, TournamentRunner, RunRecordSink, PreregSink, FigureRenderer
  data_seam: sample-manifest.json                # DTO, not a Protocol; sole cross-process coupling
  dependency_rule: "domain imports stdlib + own ports only; NEVER an adapter; NEVER pii-rate-elo. EloEngineAdapter is the single cross-repo import surface and imports neither stats/* nor analysis.significance."
  p1_enforcement:
    mechanism: two_ci_predicates
    predicate_a: "static import-graph: module 'pii_rate_elo_pipeline.analysis.significance' NOT in closure of {assessment.sample CLI, assessment adapter}"
    predicate_a_granularity: module_level        # SP-A3: sharper than D4 symbol-level (eager _tester_instance at significance.py:409)
    predicate_b: "config assertion analysis.run_significance_tests == False"
    verified_targets:
      class_def: "analysis/significance.py:90"
      eager_module_instantiation: "analysis/significance.py:409 (_tester_instance = SignificanceTester())"
      standalone_import: "cli.py:33"
      flag_gate: "cli.py:240"
      standalone_instantiation: "cli.py:242"
    test_owner: eval-data                         # mirror import-lint in pii-rate-elo CI (NFR-051)
  switch_points:
    - id: SP-A1
      decision: "Clean inner ring inside the hexagon: stats/{intervals,paired,power,lattice,multitest} are pure fns, NO port wraps them; report calls them directly"
    - id: SP-A2
      decision: "authority-by-placement: audited inference imported ONLY by report; EloEngineAdapter has no import path to stats/*; C's cap upgrade-path reserved (not built in v0.1)"
    - id: SP-A3
      decision: "P1 gate asserts MODULE analysis.significance unreachable (not just the class symbol) due to eager :409 instantiation"
    - id: SP-A4
      decision: "5 ports (CorpusReader, TournamentRunner, RunRecordSink, PreregSink, FigureRenderer); manifest is a JSON DTO; sampling/verdicts/manifest stay pure domain (no port)"
    - id: SP-A5
      decision: "constructor injection at the two-CLI composition root; NO DI framework/container (keeps stdlib-only core, NFR-050)"
  ports:
    - { name: CorpusReader, adapter: JsonlCorpusAdapter, side: pii-rate-elo, dc: DC-16 }
    - { name: TournamentRunner, adapter: EloEngineAdapter, side: pii-rate-elo, dc: DC-21 }
    - { name: RunRecordSink, adapter: JsonRunRecordAdapter, side: eval-data, dc: DC-25 }
    - { name: PreregSink, adapter: PreregAdapter, side: eval-data, dc: DC-24 }
    - { name: FigureRenderer, adapter: MatplotlibFigureAdapter, side: eval-data, dc: DC-27 }
  refactor_cost_6mo: low                           # new DC / swap loader / new detector = low; multi-tenant = medium (Frame C's edge, out of scope)
  onboarding_cost: medium
  axioms_supported: [AX-001, AX-002, AX-003, AX-004, AX-005]
  no_regression_respected: true                    # lattice 730@47c3a8f; NFR-018 power gate ON; doc-drift 0; four families separate; no corpus regen
  context_bounds_respected: true
  provisional_status: AGENT_SIMULATED
```

---

✅ **D5 CONVERGE complete (2026-06-01).** Pugh-compared 3 architecture patterns (A Hexagonal / B Clean / C Capability) against the brief's five criteria; **Frame A (Hexagonal, Ports & Adapters) preferred (datum; 0.00)** — confirming the cycle-1 precedent "Hexagonal scoring core (Clean inside `stats`)" — **tying Clean (B, 0.00, absorbed as the pure `stats/` inner ring)** and edging out **Capability (C, −0.02, whose authority-by-placement instinct is carried as SP-A2 with the cap upgrade-path reserved)**. Five switch-points named + resolved (SP-A1…A5). The load-bearing deliverable — **the import-boundary rule (§5)** — makes the fabricated `analysis.significance` **module** unreachable from both assessment entrypoints via a two-predicate CI gate, sharpened to module-level granularity because `significance.py:409` eagerly instantiates `SignificanceTester` at import time. Ports/adapters catalog, dependency-direction rule, test architecture, and NFR/axiom adherence written. No-regression rails honored. `provisional_status: AGENT_SIMULATED`. Ready for D6 (Synthesis).
