# CAP-02 — D6 SME Heuristic Findings (consolidated)

**Stage**: assessment-workflow / 03-Design · **Diamond 6 (Synthesis) — SME heuristic evaluation panel**
**Date**: 2026-06-01
**Review target**: `03-design/06-synthesis/D-implementation-ready-design.md` (the implementation-ready design)
**provisional_status**: AGENT_SIMULATED — the 5 SME evaluations are agent-simulated single-session expert reviews against the five framings below; the **eval-data code/version/line/API evidence each reviewer leaned on is direct file-read at HEAD on 2026-06-01** (re-verified this session for the load-bearing facts behind every CATASTROPHIC/MAJOR finding); the **`pii-rate-elo` side is carried from Discovery** because that repo is not populated on this machine (UT-1).

## 0. Panel composition + verdicts

| # | Framing | Verdict | CAT | MAJOR | MINOR | SUGGEST | PRAISE |
|---|---|---|---|---|---|---|---|
| 1 | **Nielsen usability** (CLI ergonomics + error states) | REQUEST_CHANGES | 0 | 2 | 2 | 0 | 0 |
| 2 | **Statistical-methodology rigor** (CIs / paired tests / power / RD honesty) | REQUEST_CHANGES | 0 | 3 | 3 | 0 | 1 |
| 3 | **Reproducibility & provenance** | REQUEST_CHANGES | 0 | 2 | 2 | 1 | 1 |
| 4 | **Architecture & testability** | REQUEST_CHANGES | 0 | 2 | 2 | 0 | 1 |
| 5 | **Scientific-reporting integrity** | REQUEST_CHANGES | 0 | 2 | 2 | 0 | 1 |
| | **Panel total** | **REQUEST_CHANGES (5/5)** | **0** | **11** | **11** | **1** | **4** |

**Disposition rule applied (this task):** all **CATASTROPHIC + MAJOR** resolutions are APPLIED in place to `D-implementation-ready-design.md`. MINOR / SUGGESTION are RECORDED here with their resolution for Stage-4 pickup (most are "record per-cell / pin in prereg" tightenings already adjacent to applied MAJORs and are folded in where they share an edit site). PRAISE is recorded to protect the load-bearing controls from regression.

**Cross-finding convergence (3 reviewers, one root cause).** The **Holm family-size definition** was independently flagged by reviewer 2 (`stat-01`) and reviewer 5 (`integrity-MAJOR-4`); and the **descriptive-census-vs-CI** issue by reviewer 5 (`integrity-MAJOR-1`) is already *resolved in the requirements* (FR-036, NFR-027) — the design had **drifted from its own requirements**. The fixes below re-anchor the design to FR-036 / NFR-026 / NFR-027 verbatim rather than inventing new policy.

---

## 1. Findings — reviewer 1 (Nielsen usability)

### nielsen-01 — **MAJOR** — GATE-P3 / contract-fail / import-gate abort with no diagnostic message
- **Location:** §7 step 6 GATE-P3; §10 regression contract; §9 import-graph gate.
- **Framing:** Nielsen #9 (help users recognize, diagnose, recover from errors). **Confidence:** high.
- **Finding:** GATE-P3 says "exit non-zero" on shortfall but specifies **no error-message content**. A leaderboard/full run aborts with a bare exit code — no statement of WHICH cells fell short, by how many realized positives, the `power_class`, or the remedy (`UNDER_SAMPLED` → draw more vs `CORPUS_LIMITED` → irreducible). The shortfall data exists in `verdicts.py`/the manifest but the abort path doesn't surface it. Same gap for the v2.0.0 regression-contract failure (§10) and the §9 import-graph gate — all pass/fail with no diagnostic.
- **Resolution (APPLIED):** specify the fatal-exit message for all three gates: enumerate offending `cell_id`s + integer realized-positive shortfall + `power_class` + the actionable next step; for `CORPUS_LIMITED` state it is **irreducible** (do not tell the user to draw more). Regression-contract failure names the drifted tuple element + expected-vs-found; the import-gate failure names the offending edge + module node. → design §7 step 6, §9, §10.

### nielsen-02 — **MAJOR** — no manifest↔corpus precondition check at ENTRY-B ("two parsers, one corpus" can silently diverge)
- **Location:** §2.3 manifest seam; ENTRY-B (`pii-rate-elo assessment`) adapter.
- **Framing:** Nielsen #9 + #5 (error prevention). **Confidence:** high.
- **Finding:** no specified error behavior when ENTRY-B reads a manifest whose `seed` / `lattice_version` / `sampler_version` / `content_hash` no longer match the on-disk corpus the bundled parser resolves. A stale/mismatched manifest would score the **wrong records** with no guardrail message.
- **Resolution (APPLIED):** add a **fail-closed precondition check** at ENTRY-B start: verify manifest `content_hash` + `lattice_version` against the resolved corpus before any scoring; abort with a named mismatch message naming the field, the manifest value, and the resolved-corpus value. → design §2.3 (new "ENTRY-B precondition") + §9 (mirror in the consumer adapter) + §11 S10 exit gate.

### nielsen-03 — **MINOR** — no progress visibility / interruption messaging on the long `run` stage
- **Location:** §11 / D2 SP-W3 ("no sub-run resume; recovery = byte-identical re-run").
- **Framing:** Nielsen #5 + #1 (visibility of system status). **Confidence:** high.
- **Finding:** a powered/full run is potentially hours with no progress visibility or partial-failure messaging; a crash forces a full restart with no status.
- **Resolution (RECORDED; folded into §7/§11):** per-stage progress to **stderr** (records scored / cells complete) and on interruption print the `run_id` + "re-run byte-identical to resume." Machine stdout discipline (SP-U2) is preserved — progress goes to stderr only.

### nielsen-04 — **MINOR** — `--preset` × `--run-type` can be set to contradictory combos
- **Location:** §5 / DC-20 (ENTRY-A flags).
- **Framing:** Nielsen #5 + #6 (recognition over recall). **Confidence:** medium.
- **Finding:** two overlapping selectors each independently set `sample_mode`; nothing rejects e.g. `preset=smoke` + `run-type=filing-grade`. The user must recall the cross-table to avoid an incoherent run.
- **Resolution (RECORDED; folded into §5):** validate preset×run-type coherence at parse time; reject contradictions with a message (or derive one from the other). The §5 `run_types` table is the source of truth for the legal product.

### Reviewer-1 cross-framing observations (non-binding)
Discoverability: ENTRY-A `stdout = manifest path only` is terse but the two-CLI hand-piping has no discovery affordance; AI-transparency: honesty-bundle non-strippability is strong. (Out of Nielsen framing — logged only.)

---

## 2. Findings — reviewer 2 (statistical-methodology rigor)

### stat-01 — **MAJOR** — Holm family = "#pairs × #metrics printed" merges metrics AND scoring families into one correction (violates AX-004; over-corrects within a family)
- **Location:** §8 multiplicity row; §6 leaderboard `rank` row; DC-22; prereg `multiplicity.family_size: 0`.
- **Framing:** NFR-027 / multiplicity. **Confidence:** high. **(Converges with `integrity-MAJOR-4`.)**
- **Finding:** pooling 4 metrics (recall/precision/Fβ/AUPRC) AND both scoring families into one Holm family is statistically wrong: recall and precision are mechanically negatively correlated, and AX-004 requires anon/pseudo to be **separate families** — the correction merged them at the inference layer. The prereg `family_size: 0` placeholder hides that the partition was undecided. **NFR-027 already defines the answer**: confirmatory family size = `#pairs × #metrics in the confirmatory set` (a structured `inference_families` block), not "printed."
- **Resolution (APPLIED):** define the confirmatory family as the set of pairwise rank comparisons **within one (metric, scoring-family) partition** — Holm **within each partition, never across metrics or across anon/pseudo families**. Replace "#pairs × #metrics printed" with NFR-027's "#pairs × #metrics **in the confirmatory set**" computed from the structured `inference_families` block; the partition rule is stated in `prereg.design_and_analysis_plan.multiplicity` and asserted equal to the report-printed family. → design §8, §6 `rank` row, §4 prereg block, DC-22/DC-26.

### stat-02 — **MAJOR** — leaderboard shows per-system marginal CIs as if they governed ranks; no paired Δ CI per adjacent pair (the "overlapping CIs ⇏ non-significant" misread)
- **Location:** §6 honesty bundle / leaderboard `metric` + `rank` rows; DC-26; DC-22.
- **Framing:** NFR-024 / AX-005 element 2. **Confidence:** high.
- **Finding:** ranks are "gated by the paired-test verdict" but the leaderboard prints per-system **marginal** Wilson CIs while ties are decided by McNemar on discordant pairs. Marginal-CI overlap and paired significance disagree frequently; presenting both without stating which governs invites the classic misread. No **paired difference CI** is shown per compared pair, although `paired_bootstrap_recall_delta` exists and is wired. **NFR-026 already requires** a McNemar verdict **AND** a paired-bootstrap delta CI for every confirmatory pairwise claim.
- **Resolution (APPLIED):** for every **adjacent rank pair**, print the paired Δ with its bootstrap CI + the McNemar p as the **rank-governing** statistic; mark the per-system marginal CIs **descriptive-only** (they do not govern the rank). → design §6 (new adjacent-pair Δ column + marginal-CI relabel) + §8 (paired Δ CI as the rank oracle) + DC-26.

### stat-03 — **MAJOR** — WELL_POWERED label applied to metrics/operating-points it was never sized for (precision / AUPRC / pseudo re-id)
- **Location:** §7 step 4 power classification; DC-18; §6 `power` column.
- **Framing:** AX-003 / NFR-035. **Confidence:** medium.
- **Finding:** power tiers size `required_n` for **recall** at `p_ref` 0.95–0.99, but the same `target_n` is applied to cells classified by realized positive counts and then **reused** for precision/Fβ/AUPRC. AUPRC and precision-at-fixed-recall have different variance and were never powered; the REID ladder (897/385 pairs) is out-of-scope yet pseudonymization re-id rates (p≈0.1–0.5) could surface with a "WELL_POWERED" label that does not apply.
- **Resolution (APPLIED):** restrict the `WELL_POWERED` label to the **recall operating point it was sized for**; label precision/AUPRC/re-id metrics `power_class = NOT_ASSESSED` unless sized by the matching ladder; **record which operating point each power verdict covers** (`power_operating_point`). → design §7 step 4 (per-metric power scoping), DC-18, manifest `per_cell_draw[]` (+`power_operating_point`), §6 `power` column.

### stat-04 — **MINOR** — interval-method seam (Wilson↔Clopper-Pearson) not reported per-cell near the boundary
- **Location:** §5 / §4 `small_n_cutoff` branch.
- **Framing:** NFR-023 / FR-040. **Confidence:** medium.
- **Resolution (RECORDED; folded into §6/§7):** record the chosen interval method per cell (already planned inline) AND **flag cells within ±1 of the `small_n_cutoff` boundary** so a reviewer sees seam-sensitivity. `small_n_cutoff=15` remains R10-DIRECTIONAL (UT-5).

### stat-05 — **MINOR** — Glicko RD reported alongside Wilson CIs risks being read as statistical adequacy of the recall estimate
- **Location:** §6 / DC-28 RD-convergence honesty.
- **Framing:** NFR-029 / AX-005 element 3. **Confidence:** medium.
- **Resolution (RECORDED; folded into §6/DC-28):** label RD strictly as **tournament-rating convergence**, separate from the metric CIs; state that NOT-CONVERGED **blocks ranking, not interval validity**.

### stat-06 — **MINOR** — n=3 seeds reported as a point Kendall-τ risks over-reading rank stability; `n_boot` not pre-registered
- **Location:** §5 / DC-23 seed-variance.
- **Framing:** NFR-055 / rank-volatility. **Confidence:** medium.
- **Resolution (RECORDED; folded into §4/§6):** pre-register `n_boot` (=10000) and the seed count; report τ **with the seed count inline**; avoid implying rank stability is established at 3 seeds.

### stat-07 — **PRAISE** — fabricated `SignificanceTester` quarantine + routing all inference through the audited `stats/` ring
- **Location:** §8 / §9 / `_engineering-findings-verified.md`. **Framing:** NFR-019/020/021. **Confidence:** high.
- **Note:** quarantining the fabricated `SignificanceTester` (Gaussian-noise pseudo-bootstrap, hardcoded n=100, fabricated McNemar `z = diff·√100/0.05`) via module-level import-graph unreachability + config flag + fabrication-regex lint, and routing ALL inference through the integer-guarded, local-RNG audited `stats/` ring, is the single most important correctness move. **Protect from regression.**

### Reviewer-2 cross-framing observations (non-binding)
UT-1 (pii-rate-elo line numbers carried against an un-populated repo) is an implementability risk, not a stats defect; NFR-010b throughput stays INSUFFICIENT_EVIDENCE; the non-interactive no-consent batch is a UX/Nielsen concern.

---

## 3. Findings — reviewer 3 (reproducibility & provenance)

### repro-01 — **MAJOR** — determinism hole: ONE shared `random.Random(seed)` fanned across many per-cell reservoirs drawn interleaved in corpus order
- **Location:** §7 step 3; DC-17. **Framing:** AX-002 / NFR-030. **Confidence:** high. **(Verified against `benchmark_throughput.py::reservoir_sample` + `lattice_audit.record_increments` at HEAD this session.)**
- **Finding:** `reservoir_sample` (`scripts/benchmark_throughput.py:92`) is Algorithm-R — deterministic **only when ONE iterable consumes ONE RNG in a fixed order**. §7 step 3 fans one shared `rng` across many per-cell `ReservoirR` instances, drawn **interleaved in corpus order**. The RNG draw sequence per cell then depends on corpus iteration interleaving AND on the set of cells each record hits (`record_increments`) — any change to record order, lattice membership, or multi-cell records perturbs **every** cell's draw. Manifest byte-repro (NFR-030) holds only for an identical corpus+lattice, NOT the claimed "byte-reproducible from the `repro` block."
- **Resolution (APPLIED):** derive a **per-cell child RNG** `random.Random((seed, cell_id))` so each cell's reservoir is independent of interleaving and of other cells' membership; record the derivation in `repro.rng_fingerprint`. State the repro guarantee as "**byte-reproducible given pinned {corpus content_hash, lattice_version, seed}**." → design §7 step 3 + step 5 `repro`, §2.3 `repro` field, §1 ledger note, DC-17, NFR-030 wording.

### repro-02 — **MAJOR** — `sampler_version` fingerprint is incomplete (omits `lattice_audit`, `reservoir_sample`, and the UT-5 integers) → silent divergence with unchanged fingerprint
- **Location:** §2.3 `repro`; §4 prereg; UT-5. **Framing:** AX-002 / provenance. **Confidence:** high.
- **Finding:** `repro.sampler_version` pins "commit/hash of `slices.py` + `power.py`" but the draw **also** depends on `scripts/lattice_audit.py` (`record_increments` / `audit_positives`), `benchmark_throughput.reservoir_sample`, AND `{small_n_cutoff, β, recall_target, MIN_SEEDS}` (UT-5, mutable). A re-run on a patched `lattice_audit` would silently diverge with an unchanged fingerprint.
- **Resolution (APPLIED):** fingerprint the **full sampler closure** (all modules touched in §7: `subsets/slices.py`, `stats/power.py`, `scripts/lattice_audit.py`, `scripts/benchmark_throughput.py::reservoir_sample`, `assessment/sample.py`, `assessment/verdicts.py`) AND **freeze the UT-5 integers INTO the manifest + prereg hashed payload** (not adjacent to it). → design §2.3 `repro`, §4 prereg `design_and_analysis_plan` (UT-5 integers in the hashed equality set), §7 step 5, UT-5 disposition.

### repro-03 — **MINOR** — `content_hash` has no defined canonicalization (file-order / whitespace / JSONL line ordering)
- **Location:** §3 runrecord. **Framing:** AX-002. **Confidence:** high.
- **Resolution (RECORDED; folded into §3):** pin `content_hash` to `scripts/write_manifest._sha256` over a **fixed file enumeration** (sorted relative paths), state byte-vs-canonical explicitly.

### repro-04 — **MINOR** — `git branch -r --contains` oracle is non-deterministic across clones / can pass on an unrelated remote
- **Location:** §4 prereg; §9. **Framing:** AX-002. **Confidence:** medium.
- **Resolution (RECORDED; folded into §4):** assert push to a **named remote/branch** + record the **remote URL** in the hashed payload (a local-only SHA still fails, per NFR-031).

### repro-05 — **SUGGESTION** — echo `rng_fingerprint` into the run-record (only the manifest carries it today)
- **Location:** §3. **Confidence:** high.
- **Resolution (RECORDED; folded into §3):** add `repro.rng_fingerprint` to the run-record `provenance` for closure.

### repro-06 — **PRAISE** — audited LOCAL `random.Random(seed)` bootstrap, injectable timestamp, write-once content-hashed JSON, non-strippable caveat raise-on-empty
- **Location:** whole design. **Confidence:** high. **Note:** textbook reproducibility/provenance discipline; the UT-1 honesty and "structure robust to line-drift" framing are exemplary. **Protect from regression.**

### Reviewer-3 cross-framing observations (non-binding)
§9 import-graph gate correctness hinges on the unverified eager `:409` instantiation (UT-1) — a real checkout may need symbol-level fallback; the smoke preset's "statistically inert" claim is a discoverability/UX concern.

---

## 4. Findings — reviewer 4 (architecture & testability)

### arch-01 — **MAJOR** — import-closure mechanism unspecified (AST/static vs runtime `sys.modules` snapshot); the two differ materially for the P1 "unreachable" claim
- **Location:** §9 predicate (a); S8. **Framing:** import-graph testability seam. **Confidence:** high.
- **Finding:** the whole P1 guarantee rests on a static import-closure assertion over both entrypoints, but a **runtime snapshot only proves the path you exercised didn't import the module**, whereas an **AST walk proves unreachability**. The design must commit to a **static AST/import-graph** mechanism to make the claim "unreachable" rather than "not-reached-in-this-run." (The pii-rate-elo half also doesn't exist on this machine — UT-1 — so the closure nodes are unverified until S8 story-0.)
- **Resolution (APPLIED):** specify the closure mechanism explicitly — a **static AST import walk** (e.g. `grimp` / `modulefinder` over both entrypoints), NOT a runtime `sys.modules` snapshot; S8 story-0 produces a **pinned module-node list** the test asserts against, so the gate is real before the adapter exists. → design §9 predicate (a), §11 S8.

### arch-02 — **MAJOR** — the runner→report **outcome DTO** (second cross-process seam) is asserted but never schema-specified; no contract test
- **Location:** §2.4 / §8 FORBIDDEN EDGE "EloEngineAdapter ↛ stats/*". **Framing:** ports/adapters dependency direction. **Confidence:** high.
- **Finding:** `report.py` consumes "per-system/per-record outcome DTOs" from `EloEngineAdapter`, but only the manifest + run-record + report schemas are defined — the **runner→report DTO is undefined**. Without a pinned DTO schema + a contract test, the adapter and the audited-stats consumer can drift independently across repos/gate suites.
- **Resolution (APPLIED):** add the **outcome-DTO dataclass to `ports.py`** (the per-pair discordant counts `(b, c)`, per-system per-record correct/incorrect, per-cell n/k, `scoring_family`, operating-point) and a **consumer-driven contract test** (eval-data owns the schema; the adapter satisfies it), parallel to the L1 manifest seam. → design §2.1 (`ports.py` row), §2.2, §2.4 (second DTO seam), §11 S10.

### arch-03 — **MINOR** — `report.py` carries four responsibilities (projection + figure port + linters + LaTeX/CSV) → largest test surface; pure projection coupled to lazy-heavy rendering
- **Location:** §2.1 `report.py`. **Framing:** ports/adapters seam consistency. **Confidence:** medium.
- **Resolution (RECORDED; folded into §2.1):** split `report.py` into **projection** (pure, audited-stats → tables/CSV, stdlib, unit-testable without matplotlib) vs **render/lint adapters**; keep the `stats/` ring direct-called from projection only (preserves SP-A1).

### arch-04 — **MINOR** — converter/schema edits keyed to Discovery line numbers; the module-vs-symbol import-strength relaxation is decided ad hoc in an S8 record rather than designed
- **Location:** §10 / UT-1. **Framing:** TDD RED-first against unverified targets. **Confidence:** medium.
- **Resolution (RECORDED; folded into §11 S8):** author **both** the module-level and symbol-level guard tests in S8; select the active regime by the verified checkout state, **recording which regime is active** — so the relaxation is a chosen branch, not improvised.

### arch-05 — **PRAISE** — `stats` ring imported only by `report.py`; `EloEngineAdapter` has no edge to `stats` → fabricated path disjoint by construction; one import-graph test enforces all three forbidden edges at once
- **Location:** §2.4 / §9 / §8 SP-A2. **Confidence:** high. **Note:** an excellent, real, true-by-construction testability lever. **Protect from regression.**

### Reviewer-4 cross-framing observations (non-binding)
NFR-038 "single pass" — §7 step 2 (`full_counts`) + the reservoir pass read the corpus **twice** (fine for memory, not literally one pass); manifest float "fixed repr" for byte-repro is underspecified (repr vs `%.17g` vs Decimal).

---

## 5. Findings — reviewer 5 (scientific-reporting integrity)

### integrity-MAJOR-1 (≙ "MAJOR-1") — **MAJOR** — full-corpus descriptive census prints CIs anyway (FR-036 / STATS-08 violation); no `inferential_target` field
- **Location:** §4 prereg; §6 leaderboard ("each with its CI", FR-040 forcing a CI on every metric). **Framing:** FR-036 / STATS-08. **Confidence:** high.
- **Finding:** §4/§6 force a CI + `method` inline on **every** metric, but **FR-036 mandates**: full-corpus = descriptive census → **no CI by default**, CIs retained only under an explicit **super-population** label. The design has **no `inferential_target ∈ {descriptive-census, super-population}`** field in manifest/prereg/run-record and the report schema cannot suppress the CI column. As written, the citable full-corpus leaderboard over-claims a CI on an exact census — the exact over-claim FR-036/STATS-08 closed. **The requirement already exists; the design drifted from it.**
- **Resolution (APPLIED):** add `inferential_target ∈ {descriptive-census, super-population}` to the prereg + run-record + manifest; the report **suppresses CIs (or labels them descriptive-only)** when `preset == full` AND `inferential_target == descriptive-census`; CIs are retained only under an explicit `super-population` label. FR-040's "CI on every metric" is scoped to the **inferential** (sample / super-population) target, not the descriptive census. → design §3 runrecord, §4 prereg, §6 leaderboard `metric` row + smoke/census handling, DC-20, FR-036 trace.

### integrity-MAJOR-2 (≙ "MAJOR-2") — **MAJOR** — PowerMatrix verdict token (`SMALL/ADEQUATE/LARGE`) printed without the synthetic-only / sample-scope caveat bound to the token (G3 over-claim)
- **Location:** §6 honesty bundle / verdict banner; DC-18/DC-28. **Framing:** AX-001/003 / G3 anti-over-claim. **Confidence:** medium.
- **Finding:** the verdict banner can read `LARGE` on a **sample** and is printed without the "conditional-on-this-sample, synthetic-only" scope qualifier **bound to the verdict token itself**. A reader sees "LARGE" and infers population-level adequacy.
- **Resolution (APPLIED):** bind the **synthetic-only + sample-scope caveat to the verdict token** (not only per-metric): the banner always renders `<verdict> · conditional-on-this-sample · synthetic-only` as one non-strippable unit, and on a sample never renders a bare `LARGE`. → design §6 self-verifying header / verdict banner, DC-18, DC-28 honesty set, §2.3 `power_verdict` field.

### integrity-MINOR-3 (≙ "MINOR-3") — **MINOR** — `pre_registration_matches: true` is a self-asserted boolean the report computes over its own plan
- **Location:** §4 / §6. **Framing:** scientific integrity. **Confidence:** high.
- **Resolution (RECORDED; folded into §4/§6):** make `pre_registration_matches` a **recomputed hash-equality** the forbidden-token/honesty linter **independently re-derives** (prereg `prereg_hash` vs a recomputed hash of the report's realized plan), not a vanity flag.

### integrity-MINOR-4 (≙ "MINOR-4") — **MINOR/MAJOR-adjacent** — Holm family size = "#pairs × #metrics **printed**" couples the multiplicity correction to a **display** choice (researcher-degrees-of-freedom leak)
- **Location:** §8. **Framing:** scientific integrity. **Confidence:** high. **(Converges with `stat-01`; treated at MAJOR severity and applied via the `stat-01` resolution.)**
- **Finding:** adding/removing a printed metric silently changes the p-value adjustment. NFR-027 pins family size to the **confirmatory set**, not "printed."
- **Resolution (APPLIED via stat-01):** family size = `#pairs × #metrics in the confirmatory set` (from the structured `inference_families` block, computed not free-typed) AND assert **report-printed family size == prereg family size**. → design §8, §6, §4, DC-22/26.

### integrity-PRAISE — **PRAISE** — non-strippable caveat by construction, forbidden product-verdict token lint, fabricated-significance quarantine, RD-as-achieved-max-RD±2RD, named-positive shortfall, UT-6 synthetic-only ceiling surfaced as a flag
- **Confidence:** high. **Note:** textbook scientific-integrity controls. **Protect from regression.**

### Reviewer-5 cross-framing observations (non-binding)
UT-1 (pii-rate-elo line numbers unverified) is an implementability risk, not integrity — logged only.

---

## 6. Applied-resolution ledger (CATASTROPHIC + MAJOR)

11 MAJOR findings → resolutions applied to `D-implementation-ready-design.md`. (Two pairs converge: `stat-01`≙`integrity-MAJOR-4` (Holm family) and the family/CI semantics across `stat-02`. The convergent MINOR `integrity-MINOR-4` is applied under the `stat-01` MAJOR resolution.)

| # | Finding(s) | Severity | Design edit site(s) |
|---|---|---|---|
| 1 | nielsen-01 | MAJOR | §7 step 6 (GATE-P3 fatal message), §9 (import-gate message), §10 (contract-fail message) |
| 2 | nielsen-02 | MAJOR | §2.3 (ENTRY-B fail-closed precondition), §9, §11 S10 gate |
| 3 | stat-01 + integrity-MAJOR-4 (+ integrity-MINOR-4) | MAJOR | §8 (Holm within-partition + family-size from confirmatory set), §6 `rank` row, §4 prereg `multiplicity`, DC-22/DC-26 |
| 4 | stat-02 | MAJOR | §6 (adjacent-pair Δ CI column + marginal-CI relabel), §8 (paired Δ as rank oracle), DC-26 |
| 5 | stat-03 | MAJOR | §7 step 4 (per-metric power scoping), DC-18, §2.3 manifest (`power_operating_point`), §6 `power` column |
| 6 | repro-01 | MAJOR | §7 step 3 + step 5 `repro`, §2.3 `repro`, §1 ledger, DC-17, NFR-030 wording |
| 7 | repro-02 | MAJOR | §2.3 `repro` (full closure), §4 prereg (UT-5 integers in hashed payload), §7 step 5, UT-5 disposition |
| 8 | arch-01 | MAJOR | §9 predicate (a) (static AST closure), §11 S8 (pinned node list) |
| 9 | arch-02 | MAJOR | §2.1 `ports.py`, §2.2, §2.4 (outcome-DTO seam + contract test), §11 S10 |
| 10 | integrity-MAJOR-1 | MAJOR | §3, §4, §6 (`inferential_target`; census CI-suppression), DC-20, FR-036 trace |
| 11 | integrity-MAJOR-2 | MAJOR | §6 verdict banner (token-bound caveat), DC-18, DC-28, §2.3 `power_verdict` |

**MINOR / SUGGESTION recorded (folded into adjacent edit sites where they share a payload):** nielsen-03 (stderr progress), nielsen-04 (preset×run-type coherence), stat-04 (interval-method boundary flag), stat-05 (RD-vs-CI labeling), stat-06 (n_boot + seed count pre-registered), repro-03 (content_hash canonicalization), repro-04 (named-remote oracle), repro-05 (rng_fingerprint in run-record), arch-03 (report.py split), arch-04 (both import-strength guard tests), integrity-MINOR-3 (recomputed pre_registration_matches).

**PRAISE protected from regression:** stat-07 / repro-06 / arch-05 / integrity-PRAISE — the fabricated-significance quarantine (module-level disjoint import graph + flag + fabrication-regex), the audited LOCAL-RNG bootstrap + injectable timestamp + write-once content-hashed JSON, the non-strippable caveat raise-on-empty, and the single import-graph test enforcing all forbidden edges at once.

**Net effect:** the design is re-anchored to its own requirements (FR-036, NFR-026, NFR-027 were the authority the design had drifted from), the sampler reproducibility claim is made true (per-cell child RNG + full-closure fingerprint), every fatal gate now diagnoses + recovers, and the two undefined cross-process seams (import-closure mechanism, runner→report DTO) are specified with contract tests.
