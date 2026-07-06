# Test Architecture — pii-anon-eval-data

**Stage 5 · Wave T2 (Test Architecture)** · 2026-05-31 · `language_profile: python`
**Scope:** the `pii-anon-datasets` v2.0.0 benchmark + evaluation harness (`src/pii_anon_datasets/`).
**Provisional status:** `AGENT_SIMULATED` — every Stage-4 verdict is agent-simulated; a real-CI Pass-2 is owed (see §7).

> **Brownfield mode — Source Signal vs Gaps.** This project entered the PDLC with a brownfield assessment
> (`00-brownfield-assessment/assessment-2026-05-28.md`) that rated **Testing WEAK→PARTIAL** and filed
> **C1 (CATASTROPHIC): zero automated tests; the scoring harness itself is unverified.** This architecture
> documents the test suite Stage 4 *built* against that gap (0 → 346 tests), and reads the existing signal
> honestly: the only pre-existing "test" assets were `scripts/validate.py` (8 schema checks) and
> `baselines/evaluate.py` (an unrun, partial-credit-double-counting eval harness). Both were **wrapped /
> superseded, not preserved** — `evaluate.py`'s reidx-02 double-count bug was fixed-not-inherited. There is
> **no STRONG-rated prior test pattern to protect**; the canonical developer-assistant shape below is the
> shape this suite was grown into. This document **describes and calibrates** the realized architecture; it
> does not prescribe a framework migration (the suite is pytest, and stays pytest).

---

## 0. Inputs read (read-only)

| Input | Path | Used for |
|---|---|---|
| Design synthesis (D6) | `03-design/06-synthesis/D-implementation-ready-design.md` | DC-15 test+CI mandate; Hexagonal/Clean module map; reidx-/gov-/DX- design constraints |
| NFR document | `02-requirements/non-functional-requirements.md` | NFR-016 coverage bar; what needs verification (NFR-001..018) |
| Development log | `04-development/development-log.md` | 8-sprint roll-up; per-sprint coverage + green counts |
| Brownfield assessment | `00-brownfield-assessment/assessment-2026-05-28.md` | C1 + Testing rating; "wrap don't rebuild" |
| Test suite (sample) | `tests/` (48 files) | pyramid-shape calibration; inline test-type tags; token convention |
| Language profile | `python` (from `developer-assistant.yaml`) + `pyproject.toml` | build/test/lint/coverage commands |

**Calibration note:** the suite already carries **inline test-type markers** in test docstrings
(`[UNIT-TEST]`, `[INTEGRATION-TEST]`, `[PROPERTY-TEST]`, `[CONTRACT-TEST]`, `[AUDIT]`). The pyramid shape
declared in §1 is **measured from those markers**, not asserted as a default.

---

## 1. Pyramid shape declaration

### Shape: **CLASSIC PYRAMID with a PROPERTY-TEST mantle** (broad unit base · thin integration band · system cap)

**Measured marker census** (`grep` over `tests/` docstrings, 2026-05-31):

| Marker | Count | Band |
|---|---|---|
| `[UNIT-TEST]` | 108 | base |
| `[PROPERTY-TEST]` | 45 | base mantle (determinism / invariants / order-independence) |
| `[CONTRACT-TEST]` | 15 | port boundaries (adapter / adversary / serializer) |
| `[AUDIT]` | 15 | cross-cutting structural guards (purity / separation / no-merge) |
| `[INTEGRATION-TEST]` | 14 | export→load round-trips, store↔policy, CLI dispatch |
| (system / gate) | small named set | `validate.py --lattice` gate, determinism re-run hash |

Unit + property dominate (~153 of ~197 marked assertions). Integration is a **deliberately thin band**, and
the system tier is a **small named set** of end-to-end gates. This is a **classic pyramid**, not an
inverted trophy and not a honeycomb.

### Justification (from project profile — NOT "best practice")

1. **The value of this artifact is measurement correctness, and correctness lives in pure functions.** The
   thesis (brownfield C1, design M6) is that a benchmark's credibility *is* the math: Clopper-Pearson vs.
   table, McNemar vs. binomial, ECE/Brier on fixed inputs, the crosswalk N-column invariant, integer-count
   guards. These are **stdlib, deterministic, side-effect-free** primitives — the ideal unit surface. A broad
   unit base is the correct shape because the risk is concentrated there.
2. **The architecture is Hexagonal (scoring core) + Clean (DC-09 stats).** Ports & adapters make the
   integration band *small by construction*: there are a bounded number of port boundaries
   (adapter inbound, adversary outbound, export/leaderboard outbound), each covered by a focused
   **CONTRACT** test rather than a wide integration web.
3. **Determinism (AX-002) is a first-class axiom**, so the natural test is a **PROPERTY** test (identical
   inputs → byte-equal output; shuffle inputs → identical result). The 45-strong property mantle is a
   direct consequence of the determinism mandate, not a stylistic choice.
4. **There is no UI and no service runtime** (CLI + library + files). There is nothing to drive an
   e2e/browser tier, so the system tier is correctly limited to **two gates**: the corpus-power gate
   (`validate.py --lattice`) and the determinism re-run hash. An e2e-heavy shape here would be an
   **anti-pattern** for a batch benchmark.

### Anti-pattern check (part of the job)

- **Ice-cream cone (e2e-heavy / unit-light): NOT PRESENT.** Ratio is ~7.7:1 unit+property : integration.
  No finding.
- **Hidden integration weight in "unit" files: checked.** Heavy deps (pyarrow / datasets / mlcroissant /
  spacy / matplotlib / anthropic) are gated behind `pytest.importorskip` — they do **not** silently
  inflate the base. The one structural risk is that **integration round-trips skip when optional deps are
  absent** (see §3 CI-isolation and §7) — this is the load-bearing Pass-2 item, not a shape defect.
- **Flag (MINOR, carried to Pass-2):** the system-tier "real round-trip" guarantees (Parquet→`datasets`
  load, Croissant spec-conformance) are **environment-conditional**. In a dep-bare runner they degrade to
  skips. The architecture is sound; the **proof is owed in a provisioned CI image** (NFR-012).

---

## 2. Per-test-type strategy (the 5 realized tags)

The canonical 9-tag set collapses to the **5 tags this suite actually uses**; the unused four
(E2E, SNAPSHOT, SMOKE, PERFORMANCE) are addressed honestly below rather than silently filled.

### 2.1 UNIT-TEST (108) — the base
- **When it applies:** any pure function in `scoring/`, `stats/`, `compliance/`, `subsets/` whose output is a
  function of its arguments. The statistical & scoring primitives.
- **Canonical members:** Clopper-Pearson vs. a hand-checked table (`test_intervals` / `test_clopper_pearson`);
  Wilson integer-count guard (rejects fractional k/n — reidx-02); McNemar exact/χ² vs. binomial
  (`test_paired`); ECE/Brier on fixed inputs (`test_calibration`); NIST `required_n` derivation
  (`test_power`); crosswalk → exactly-5-typed-columns (`test_crosswalk::test_fr_022_five_legally_distinct_columns`).
- **Fixture convention:** **inline literals only** — tiny hand-constructed inputs whose expected output is
  computed independently (table, closed form, or by hand). **Never the corpus.**
- **Lifecycle:** stateless; no setup/teardown; no `tmp_path`.
- **Ownership:** the module author (TDD RED→GREEN per Build Task). One test file mirrors one module.

### 2.2 PROPERTY-TEST (45) — the determinism/invariant mantle
- **When it applies:** AX-002 determinism, order-independence, and algebraic invariants that must hold across
  *all* inputs of a shape, not one example.
- **Canonical members:** `test_offline_adversary::test_fr_007_attack_is_deterministic` (identical inputs →
  byte-equal `Guess` list via frozen-dataclass equality); `test_fr_007_ranking_is_order_independent` (shuffle
  → identical); strict-match multiset order-independence (reidx-03); crosswalk N-column invariant under
  regime reordering; lattice spec round-trips against its deterministic generator (anti-drift).
- **Fixture convention:** small generated families (shuffles, permutations, seeded `random.Random(seed)` —
  never global RNG). Determinism is asserted via **frozen-dataclass `==`**, not a recomputed hash that a
  shared seed could fake.
- **Lifecycle:** stateless; the seed is local and explicit.
- **Ownership:** module author; these are the tests that encode AX-002 at the unit level.

### 2.3 CONTRACT-TEST (15) — the port boundaries (Hexagonal)
- **When it applies:** at every port in the ports-&-adapters core — the inbound `SpanAdapter`, the outbound
  adversary port, and every **serializer** that must carry a value object's mandatory fields.
- **Canonical members:** `test_adversary_port::*_satisfies_port` (offline + LLM adapters honor the
  `deterministic` + `adversary_id` contract); the **non-strippable caveat** contract
  (`test_rrs_caveat`: caveat is a mandatory non-defaulted field → omitting it is `TypeError`; empty →
  rejected; survives `as_dict()` — gov-01); the CoI **non-strippable attestation** contract
  (`test_coi::test_fr_026_attestation_is_non_strippable` — empty/whitespace → `ValueError`; gov-03).
- **Fixture convention:** the minimal object that satisfies / violates the contract; assertions target the
  *boundary shape* (field presence, type, exception), not numeric values.
- **Lifecycle:** stateless.
- **Ownership:** the port owner + any adapter author (a new adapter must add a contract test before merge).

### 2.4 AUDIT (15) — cross-cutting structural guards
- **When it applies:** invariants that must hold **across the source tree**, enforced by reading the code
  itself (AST) or by source-grep — the guards that make a class of bug *structurally impossible*.
- **Canonical members:**
  - **AST import-purity guards** — pure-stdlib core / lazy heavy deps. `test_nfr005_separation` parses module
    source with `ast.walk`; `test_offline_adversary::test_fr_007_nfr004_offline_adversary_imports_no_nondeterminism`
    asserts the offline adversary imports **no** nondeterministic modules (no `random`/`time`/`datetime`) —
    "offline deterministic" proven by *absence of capability*, not by idempotence a seed could fake.
  - **NFR-005 separation (AX-004)** — no module merges anon + pseudo into one headline; no combined `de-id`
    callable in the scoring public API; mutation-tested against 4 fusion vectors.
  - **gov-02 no-merged-verdict** — `test_crosswalk::test_fr_022_no_merged_or_equivalence_column` greps the
    module source: no merged/equivalence/flattened regime field anywhere.
  - **Heavy-dep laziness** — force-block `pyarrow`/`mlcroissant`/`spacy`/`datasets` at import and assert
    `distribution`/`cli`/`compliance` still import (NFR-004 purity), each lazy guard raising its
    correctly-named extra `RuntimeError`.
- **Fixture convention:** the **module source** (`inspect.getsource` / `ast.parse`) or an import-blocking
  shim. These are the most valuable tests in the suite per unit of code.
- **Lifecycle:** stateless; operate on source/import, not runtime data.
- **Ownership:** the architecture owner (this discipline is cross-module; an audit failing is an
  architecture regression, not a local bug).

### 2.5 INTEGRATION-TEST (14) — the thin band
- **When it applies:** when two real subsystems must agree across a serialized boundary.
- **Canonical members:** export→Croissant→`datasets` load round-trip (`test_croissant`, `test_parquet_export`
  — the 5 `reg_*` columns survive HF `datasets` load); Parquet / spaCy DocBin / CoNLL BIO-BILOU round-trips;
  leaderboard **store ↔ policy** (append-only hash-chain feeds the anti-gaming policy); `validate.py --lattice`
  wiring; **CLI dispatch** (`test_cli`: 5 thin verbs route to the owning subsystem;
  `export --format parquet` → `distribution`; `validate` **never** injects `--no-power-gate`).
- **Fixture convention:** `tmp_path` for any filesystem artifact; `monkeypatch`/`subprocess.run` patched to
  assert **dispatch**, not to re-run heavy logic; optional deps via `pytest.importorskip` (skip-clean when
  absent).
- **Lifecycle:** `tmp_path`-scoped; no shared mutable state between tests; no network.
- **Ownership:** the two subsystem owners jointly; the boundary is the contract.

### 2.6 Tags NOT used (honest non-fill)
- **E2E / browser:** N/A by design — no UI, no service (brownfield: accessibility N/A).
- **SMOKE:** subsumed by the CLI dispatch integration tests + the `import pii_anon_datasets` purity audits.
- **SNAPSHOT:** deliberately avoided — determinism is asserted via frozen-dataclass equality and explicit
  expected values, which are more legible than golden-file snapshots for math.
- **PERFORMANCE:** **no perf gate** (consistent with NFR-010a's "no throughput floor" and the advisory-only
  perf findings in S3/S6). Two O(n²) seams (pseudonymization referential-integrity — already lifted to O(n);
  leaderboard store re-read) are documented as v1.x hardening, **not** gated. NFR-010b's 5,000 rec/sec floor
  is explicitly `real_user_needed: true` → Pass-2.

---

## 3. Cross-cutting discipline

### 3.1 The `fr_NNN` / `nfr_NNN` token convention (every capability → ≥1 named test)
- **Mechanism:** every test function name carries a requirement token, e.g. `test_fr_024_*`, `test_nfr004_*`,
  `test_fr_022_five_legally_distinct_columns`. The token is the traceability join key (closes brownfield M3).
- **Realized census (2026-05-31):** **221** test functions carry an `fr_/nfr_` token (of **335** total test
  functions); **34 distinct FR/NFR tokens** are exercised by name (FR-002/004/005/006/007/008/009/010/
  011/012/013/015/016/017/018/019/020/021/022/023/024/025/026/027/029 + NFR-002/003/004/005/008/012/013/014/018).
- **Discipline:** a Build Task is not GREEN until its FR/NFR has ≥1 named test. Non-tokened tests are allowed
  for internal helpers, but every shipped capability and every quantified NFR has a named guardian.

### 3.2 AST import-purity guards (pure-stdlib core, lazy heavy deps)
- **Invariant:** the scoring/stats **core is pure stdlib** (NFR-004) so `import pii_anon_datasets` never pulls
  a runtime dep; all heavy deps (pyarrow / datasets / mlcroissant / spacy / matplotlib / anthropic) are
  **lazy** behind their optional-extra and a named `RuntimeError`.
- **Enforcement:** per-module AST/import-block audits (§2.4). This is what lets the published wheel stay
  dependency-free while the exporters remain optional.

### 3.3 Non-strippable-caveat tests (FR-009 / gov-01 / gov-03 / EDPB Art 4(5))
- **Invariant:** a privacy figure can never be emitted without its caveat. The caveat is a **mandatory
  non-defaulted field on the value object**, not renderer state — so it travels with the number through any
  serializer.
- **Enforcement:** construct-without-caveat → `TypeError`; empty caveat → rejected; `as_dict()` still
  contains it. Replicated for the RRS anti-anonymity caveat, the exposure-"NOT RRS" disclaimer, the EDPB
  Art 4(5) key/state-separation caveat, the Pareto separation, the DPIA disclaimer, and the CoI
  no-pre-publication attestation.

### 3.4 Determinism (AX-002) tests
- **Invariant:** seeded/offline paths are **byte-reproducible**; LLM paths are explicitly flagged
  `deterministic=False` and version-stamped (NFR-007).
- **Enforcement:** PROPERTY tests assert identical-input → byte-equal output and shuffle-invariance;
  a **system-tier re-run hash** check (the migration + enrichment proved byte-identical across two full runs;
  `data/MANIFEST.sha256` over the 28 data files is `--check`-verified). Determinism is proven structurally,
  too, via the no-RNG/no-clock import audit on the offline adversary.

### 3.5 De-circularization (reidx-01) test
- **Invariant:** the **RRS headline is the DETERMINISTIC offline adversary + exposure index**; the LLM
  adversary is a *version-stamped secondary* figure (design revision #1). This breaks the circularity of
  "score the benchmark with the same stochastic model the benchmark is meant to grade."
- **Enforcement:** `test_offline_adversary` pins the offline attacker as deterministic
  (`OFFLINE_ADVERSARY_VERSION == "offline-deterministic-v1"`, `deterministic is True`), order-independent,
  and import-pure (no nondeterminism). `test_adversary_port` confirms the LLM adapter is the secondary,
  `deterministic=False`, lazy behind `[llm]`. The exposure index is tested as an explicit **prior, NOT RRS**.

### 3.6 Hermeticity / CI-isolation / fixture-management / flakiness budget
- **Hermeticity:** the core is network-free and clock-free; no test reaches the network. Filesystem writes
  are `tmp_path`-scoped. The **frozen corpus and `eval_lattice.json` (730 cells @ `47c3a8f`) are never
  mutated by tests** — reporters/gates take `(lattice, observed_counts)` as arguments.
- **CI-isolation:** optional deps are `pytest.importorskip`-gated; a dep-bare runner yields **clean skips**,
  not errors. The single standing skip is **`anthropic`-absent** (the live-LLM-attack contract test) — by
  design, the offline adversary is the headline.
- **Fixture-management:** fixtures are tiny inline literals or `tmp_path`; there is **no `conftest.py`
  fixture web and no shared mutable state** — each test reconstructs its inputs. This is what keeps the
  property/determinism guarantees honest.
- **Flakiness budget: ZERO.** The corpus-power gate is **count-based (non-flaky) by deliberate design**,
  held distinct from the FR-002 paired-McNemar detector-regression gate. Seeds are local and explicit.
  Determinism is asserted by equality, not tolerance (except the *stated epsilon* on the stochastic LLM
  re-run, NFR-007). Any nonzero flake is a release blocker, not a budget line.

---

## 4. Per-language commands (python profile)

Honoring `language_profile: python` and the tooling actually used in Stage 4 (per commit history +
`pyproject.toml`). **No new framework is prescribed** — pytest / ruff / mypy / pytest-cov are the realized
toolchain.

| Concern | Command | Source |
|---|---|---|
| Build / install (editable + dev) | `python3 -m pip install -e ".[dev]"` | `pyproject.toml [project.optional-dependencies] dev = pytest>=8, pytest-cov>=5` |
| Build (full optional surface) | `python3 -m pip install -e ".[dev,baselines,llm,distribution,croissant,viz]"` | optional-extras |
| Test (fast) | `python3 -m pytest -q` | `[tool.pytest.ini_options] addopts="-q"`, `pythonpath=["src"]`, `testpaths=["tests"]` |
| Test + coverage (line+branch) | `python3 -m pytest -q --cov` | `[tool.coverage.run] branch=true` over the 11 source packages |
| Lint | `ruff check src tests` | S3–S7 `[REFACTOR]` commits (ruff) |
| Format | `ruff format src tests` | S7 `[REFACTOR]` commits (ruff-format) |
| Type-check | `mypy --strict src` | S2–S7 `[REFACTOR]` commits (mypy --strict) |
| Coverage gate (per-module) | `python3 -m pytest -q --cov` → assert ≥85% line on changed scorer modules | NFR-016 |
| Power gate (corpus) | `python3 scripts/validate.py --lattice` (default-on; exits non-zero on any under-powered committed cell) | NFR-018 |
| Manifest integrity | `python3 scripts/write_manifest.py --check` (sha256 over 28 data files; asserts v1.3.0 tag intact) | NFR-004 |
| Lattice anti-drift | `python3 scripts/generate_lattice_fill.py --check` (frozen `eval_lattice.json` round-trips its deterministic generator) | NFR-018 |
| CLI smoke | `pii-anon --help` (5 verbs) / `pii-anon validate` (power gate ON) | FR-024 / DX-03 |
| Bench | **none** — no perf gate (NFR-010a no-floor; perf findings advisory) | §2.6 |

**One copy-paste CI invocation (DX-03):** `python3 -m pip install -e ".[dev]" && ruff check src tests && mypy --strict src && python3 -m pytest -q --cov && python3 scripts/validate.py --lattice`.

---

## 5. Coverage targets & posture

### Target (NFR-016, R10 ACCEPTED-WITH-CAVEATS)
- **≥85% line** on new/changed scorer modules.
- **≥70% branch** on scorer / statistical-computation modules (where reproducibility bugs hide).
- CI green (lint + type + test) and coverage recorded in a versioned, auditable artifact (NFR-017).

### Measured (this run: `python3 -m pytest -q --cov`, 2026-05-31 — **346 passed / 1 skipped**)
- **Aggregate: 96.4% line (2364/2452), 88.7% branch (605/682)** over the 11 covered packages
  (scoring, stats, compliance, distribution, reporting, integrations, cli, leaderboard, validation, subsets).
  Report headline reads "94%" (the rounded combined line figure).
- **Posture vs. NFR-016: CLEARED, with margin, on both axes.** Every scoring/stats module is **≥85% line and
  well over ≥70% branch.** Representative per-module floor check:

| Module | Line | Module | Line |
|---|---|---|---|
| `scoring/core.py` | 100% | `stats/intervals.py` | 87% |
| `scoring/detection.py` | 100% | `stats/calibration.py` | 96% |
| `scoring/anonymization.py` | 97% | `stats/paired.py` | 92% |
| `scoring/pseudonymization.py` | 93% | `stats/power.py` | 91% |
| `scoring/reidentification.py` | 92% | `stats/lattice.py` | 97% |
| `scoring/signals.py` | 86% | `compliance/crosswalk.py` | 95% |
| `scoring/adversary/offline_adversary.py` | 94% | `distribution/parquet_export.py` | 99% |
| `scoring/adversary/llm_adversary.py` | 94% | `reporting/power_table.py` | 100% |
| `cli.py` | 91% | `validation/correlation.py` | 94% |

**Lowest scorer/stats module is `signals.py` at 86% line** — still above the 85% bar; it is the largest
single module (160 stmts) and the only one near the floor. No scorer/stats module is below either threshold.

### Mutation testing
- **Not run as a gate.** Two targeted "mutation-style" audits exist where they matter most (the NFR-005
  no-merge audit rejects 4 fusion vectors; the gov-02 audit rejects a merged-verdict column), but a full
  `mutmut`/`cosmic-ray` mutation score is **not part of v1**. Recommended as a Pass-2 enhancement on the
  `stats/` + `scoring/core` hot-spots, where a high mutation score would most strengthen the credibility
  claim. **Flagged, not silently omitted.**

---

## 6. What Stage 5 adds vs. Stage 4

Stage 4 produced the **suite** (346 green) under strict TDD with self-assessed reviewer gates. Stage 5's
distinct contributions:

| Stage 5 wave | Adds over Stage 4 | Owner |
|---|---|---|
| **T2 — this doc** | The **holistic architecture view**: pyramid-shape *measurement* (not per-story green), cross-cutting discipline as one document, coverage posture confirmed against live `--cov`, the anti-pattern check, mutation-testing gap call. | test-architecture (this agent) |
| **NFR-verification execution** (`05-testing/03-nfr-verification/`) | **Execution** of the quantified NFRs as a matrix — NFR-001/018 power gate run to completion on the frozen lattice, NFR-008 ECE on the dev split, NFR-012 Croissant validate-AND-load in a **provisioned** image, NFR-013 doc-drift = 0, NFR-016 the numbers above. Stage 4 asserted these per-module; Stage 5 runs them as a labelled NFR ledger. | nfr-verification |
| **WCAG / accessibility audit** (`05-testing/04-accessibility/`) | **N/A by design** (no UI; brownfield Testing→accessibility N/A). Stage 5 records the explicit N/A determination + the doc-clarity-only posture (markdown/static reports) rather than leaving the section blank. | accessibility |
| **Examples-catalog roll-up** | 1:1 **example↔test** pairing (closes brownfield "examples+tests WEAK"): every README/Quick-Start example mapped to its guarding test via the `fr_/nfr_` token. The token convention (§3.1) is the join. | examples-catalog |
| **Pass-2 protocol hand-off** (`05-testing/05-pass2/`) | **Not authored here** (out of this agent's bounded context). The honest-limitations ledger in §7 is the *input* the Pass-2 coordinator consumes. | pass2-coordinator |

---

## 7. Honest limitations (non-strippable)

Carried forward from the Stage-4 handoff and confirmed against the live suite — these are **release caveats,
not defects to hide**, and are the binding Pass-2 agenda:

1. **All `AGENT_SIMULATED`; real-CI Pass-2 is owed.** Every story + sprint gate is an agent self-assessment.
   The suite has **not been run in a clean, provisioned external CI image**. The two
   environment-conditional guarantees — Parquet→HF-`datasets` load and full `mlcroissant` spec-conformance
   (NFR-012) — currently **degrade to `importorskip` skips** when the `distribution`/`croissant` extras are
   absent. The numbers in §5 are from the local environment. **A real CI run is the load-bearing Pass-2
   item.**
2. **~72% formulaic synthetic corpus.** The S-PWR enrichment that powered all 710 committed cells used a
   single carrier template (`provenance.source_type="synthetic_lattice_enrichment"`, filterable). Power is
   **precision on the synthetic distribution, not external validity.** Every published per-cell metric carries
   the non-strippable synthetic-provenance / external-validity caveat (FR-009/FR-027). Template-diversity is
   a follow-on; the **synthetic→real transfer delta (FR-027)** is the binding Pass-2 study — `correlate()`
   returns a `RealDataAbsent` sentinel rather than fabricate it.
3. **The `anthropic`-absent skip (the 1 skipped).** The live-LLM-attack contract test
   (`test_llm_adversary`) skips cleanly via `pytest.importorskip("anthropic")`. This is **by design** — the
   deterministic offline adversary is the RRS headline (reidx-01) and the LLM path is a version-stamped
   secondary — but it means the LLM adversary's *live* behavior is unexercised in the default run. Likewise,
   `pyarrow`/`datasets`/`mlcroissant`/`spacy`/`matplotlib` skips reduce realized integration coverage in a
   dep-bare runner.
4. **Design was never real-user/real-SME trialed.** D6 was critiqued by a representative SME *heuristic*
   panel; R10 threshold validation was a *simulated* 10-persona panel. Real benchmark-consumer interviews,
   real external leaderboard submissions, and a real privacy-eval SME review of the anon/pseudo scoring
   semantics are Pass-2 (cannot be agent-simulated).
5. **No mutation gate; no perf gate.** (§5, §2.6.) Targeted no-merge/no-fusion audits exist; a full mutation
   score and the NFR-010b 5,000 rec/sec throughput number are Pass-2.
6. **Reserved seams (intentionally v1-deferred):** effective near-duplicate-collapsed positive counts
   (reidx-04 — v1 uses raw counts); FR-015/016 full coreference/quasi-id *scoring* (loaders ship; scoring is
   v1.1); FR-018/019/020 agentic facets (ROADMAP, not shipped). Each ships behind a non-strippable
   scope-honesty caveat.

**Expected Stage-5 release verdict on this evidence: SHIP-WITH-CAVEATS.**

---

*Conforms to the developer-assistant `templates/testing/test-architecture.md.tmpl` section contract
(pyramid · per-type strategy · cross-cutting discipline · per-language commands · coverage targets ·
Stage-5-vs-Stage-4). Brownfield "Source Signal vs Gaps" header carried. No test framework prescribed beyond
the python profile's realized pytest/ruff/mypy toolchain.*
