# CAP-02 Requirements Document — Powered Assessment Workflow (canonical)

**Capability**: CAP-02 — an academically-sound, repeatable, reportable assessment **workflow** that runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 records / CC0 / `annotations`** over a **powered, lattice-stratified sample (default)** / **full corpus (opt-in, citable)** / **smoke (fast CI)**, with statistical/epistemic observability + reporting at **every** spine stage: `load → sample → run systems → score → rate → report`.
**Stage**: assessment-workflow / 02-Requirements · **R8 (canonical consolidation)** · 2026-06-01 · Ready for Stage 3 Design.
**provisional_status**: AGENT_SIMULATED — every persona / PGO / UC / interview / survey signal these requirements trace to is agent-simulated single-session Discovery + Requirements research; the **code / version / line evidence they bind to is direct file-read at HEAD on 2026-06-01** (paths cited in the source FR/NFR docs). Agent-simulated research is **NOT** a substitute for real users; real-user validation of the requirements + thresholds is a **Pass-2** follow-up (§Methodology, `methodology.md`).
**Vocabulary remap (project framing — synthetic PII benchmark)**: FR = **Benchmark / Assessment Capability** · NFR = **Quality Attribute** · UC = **Evaluation Scenario** · DC = **Benchmark Component** · PGO = **Benchmark Goal** · Persona = **assessment consumer**.

> **Locked architecture every requirement assumes.** `load → sample → run systems → score → rate → report`. **eval-data OWNS** sampling + observability + reporting; **`pii-rate-elo` CONSUMES** — extend it, do **NOT** rebuild the engine / metrics / significance. Where a requirement says "wire", it means *call the consumer seam*, not re-implement it.

> **Source artifacts consolidated here (R0–R7, read this session):** `_bridge/uc-pgo-map.md` (R0 UC↔PGO bridge, 0% orphan), `interview-synthesis.md` (R3, INT-01…06 / DF-1…5 / N-01…15), `functional-requirements.md` (R4, FR-030…054), `non-functional-requirements.md` (R4, NFR-019…055), `survey-analysis.md` (R6 aggregate), `prioritization-decisions.md` (R7, D1–D12 + the final committed split). Grounded against the canonical Discovery artifacts (`01-discovery/discovery-report.md` §8 Open Items 1–13 / G1–G7 / C1–C10; `01-discovery/04-use-cases.md` UC-16…23; `01-discovery/personas.md`) and direct file-reads of both repos.

---

## Executive summary

CAP-02 operationalizes the refined Discovery POV: a **seeded, byte-reproducible assessment workflow** that **delegates** tournament ranking, Glicko-RD convergence, and paired-significance *machinery* to the mature `pii-rate-elo` engine, and **contributes** three net-new things — (1) a **NIST-powered, lattice-stratified sampler** over the v2.0.0 / 575,604-record corpus (the consumer's only knob is naive `max_samples` head-truncation, which has no concept of power), (2) **per-cell epistemic instrumentation** (Wilson / Clopper-Pearson CIs on every metric, a `WELL_POWERED / UNDER_SAMPLED / CORPUS_LIMITED / EMPTY` power class with the named shortfall in **realized positives**, and a non-strippable synthetic-only / anti-anonymity caveat), and (3) **reconciliation of the drifted dataset seam** (the consumer is pinned to v1.3.0 / 159,891 / `labels`; the live corpus is v2.0.0 / 575,604 / `annotations` / CC0).

All statistical claims are computed by a **single audited statistics core** (`eval-data/stats`) with **no approximated statistics on the run path** — the fabricated `pii-rate-elo/analysis/significance.py` (bootstrap `se=metric*(1-metric)/100` + Gaussian noise L205-206; McNemar `n_approx=100` / `pooled_sd=0.1` L271-281) is **quarantined and CI-enforced unreachable**. The three hard preconditions (P1 audited-stats / P2 seam reconciliation / P3 powered sampler) all land in **MUST**. The candidate axiom **AX-pii-anon-005** is **CONFIRMED** (6/6 R6 respondents, one adopted sharpening). The default-mode reconciliation is resolved explicitly: **powered-representative is the CLI default**, always labelled with its power verdict + named shortfall (never silently LARGE); **FULL = the citable leaderboard**; a **run-type designation** (`smoke` / `dev` / `leaderboard-submission` / `filing-grade`) scopes both pre-registration enforcement and the AX-005 rigor bar — manifest-reproducibility is **universal**, pre-registration is **opt-in**.

---

## Counts

- **25 Functional Requirements** (`functional-requirements.md`, FR-030 … FR-054) — **16 MUST · 8 SHOULD · 1 COULD**.
- **37 Non-Functional Requirements** (`non-functional-requirements.md`, NFR-019 … NFR-055) — **32 MUST · 4 SHOULD · 1 COULD**; each carries a quantified threshold (number + unit) **or** a boolean-auditable criterion + a measurement method + the axiom/precondition it serves.
- **Combined: 62 requirements** = **48 MUST (77.4%) · 12 SHOULD (19.4%) · 2 COULD (3.2%)** + **2 MUST-grade baseline gates** (G-eng NFR-050, G-norg NFR-052/053/054/055) held outside the feature headline.
- **8 UCs (UC-16…23) · 22 PGO triples (18 primary + 4 sub-archetype drivers) · 6 personas (3 HIGH / 3 MEDIUM)** carried from Discovery (R0 bridge, **0% orphan**).
- **ID discipline:** global numbering **continued, never renumbered/reused** — UC→16, FR→030, NFR→019, DC→16 (per `MANIFEST-capability.md`). Cycle-1 (NFR-001…018, FR-001…029, UC-01…15) remains binding; the load-bearing inherited NFRs are pinned by the no-regression guardrails (NFR-005, NFR-010, NFR-013, NFR-018).

---

## The three hard preconditions (all floor-locked to MUST — R7 §3 D1)

| Precondition | What it requires | FR(s) | NFR(s) | Status |
|---|---|---|---|---|
| **P1 (SHOWSTOPPER)** | Route the run path through the audited `eval-data/stats` core (`paired.py` + `intervals.py`); **quarantine** the statistically-fabricated `pii-rate-elo/analysis/significance.py`; **zero** approximated statistics on the run path | **FR-042** (quarantine), FR-040 (CIs), FR-041 (paired) | **NFR-019, NFR-020, NFR-021, NFR-022** | MUST (T3: must-land-**first**) |
| **P2** | Reconcile the dataset seam to v2.0.0 / 575,604 / CC0 / `annotations` via a **versioned crosswalk** (lossless-or-explicit-lossy) + a **regression contract** pinning {version, record-count, 63-type count, schema fingerprint, dataset content hash} | **FR-030, FR-031** | **NFR-040, NFR-041** | MUST |
| **P3** | Add the **powered, lattice-stratified sampler** as a first-class stage emitting the `PowerMatrix` verdict + per-cell named shortfall **against realized positive counts** (not target_n labels) | **FR-032, FR-033, FR-034** | **NFR-035, NFR-036, NFR-037, NFR-038, NFR-039** (+ NFR-053 power gate) | MUST |

All four precondition bundles (B1/B2/B3/B4) scored MUST/near-MUST with high credibility-impact and **no comprehension flag** (lowest = B4 @ 4.50); the floor-lock per the locked brief is satisfied and independently MUST-voted.

---

## Default-mode reconciliation decision (resolved explicitly — DF-1, R7 §2 T1, R3 §3 DF-1)

**Decision (locked, do NOT let it drift):**

1. **`powered-representative` is the CLI DEFAULT.** Default invocation (no preset flag) yields the powered, lattice-stratified sample — **never** silently the full corpus, **never** silently `LARGE`. The representative run is **ALWAYS** labelled with its `PowerMatrix.verdict()` (SMALL / ADEQUATE / LARGE) **and** the per-cell named shortfall in realized positives (G3). (FR-035, FR-033; NFR-035.)
2. **`full-corpus` is the citable leaderboard mode**, reachable **only via explicit opt-in**. `records_scored == dataset.record_count(version)` resolved from the version-pinned loader (never a literal `575604`). Detection is compute-cheap so a full run is reasonable; **sampling is essential only where the LLM-adversary cost binds** (G2). (FR-035, FR-036; NFR-025.)
3. **`smoke` is the fast CI/dev preset** — a fixed seeded slice that exercises the whole spine, **suppressing all CI + p-value fields** (not merely flagging) so it can never look inferential. (FR-037; NFR-034.)
4. **A `run-type` designation** (`smoke` / `dev` / `leaderboard-submission` / `filing-grade`; names finalizable in Design) — the single highest-leverage net-new mechanism (N-01) — **selects** (a) the enforced AX-005 rigor bar, (b) whether pre-registration is enforced, and (c) the backing sample mode. This one mechanism reconciles **DF-1** (citable-vs-pre-screen), **DF-2** (pre-reg scoping), and the **AX-005 universality tension**. (FR-038; NFR-033.)

**The three CLI presets are kept exactly as the locked brief specifies** (T1: 6–0 for the locked default holds). **Carried caveat (do NOT silently resolve):** INT-05 (P-dpo / assurance, **first-contact**) pushed back, wanting **full-corpus as the default for filing-grade** evidence because power-tier explanation "adds a layer of explanation that should not need to exist." This is **first-contact assurance signal, not a mandate to flip the default** — it is honored as the **`filing-grade` backing-mode profile** inside FR-038 (filing-grade may bind full-corpus) and is carried to **Pass-2** for real-user DPO verification (INT-05's own hedge: "I'd want to verify whether regulators in practice accept a well-labeled powered-sample artifact").

---

## Candidate axiom AX-pii-anon-005 — recorded for confirmation (CONFIRMED at R7; pending PO sign-off)

> **AX-pii-anon-005 (Pre-registered / reproducible assessment).** **No published metric ships without all of:** (1) a **confidence interval** with the interval-selection method named; (2) a **paired significance test** for every system-vs-system claim, under an **explicitly declared multiplicity family** — *two* inference families: **exploratory** per-cell uncorrected (labelled, never a headline) vs **confirmatory** pairwise **Holm-Bonferroni with the family size stated** (the declaration lives in the **axiom/report text, not only in code**); (3) a **convergence statement** reported as **achieved max-RD ± 2RD (95%) with the rounds / stopping rule stated**, never an extrapolated round count (G4); (4) **provenance** sufficient to reproduce the run from the manifest (`{dataset_version, record_count, schema_fingerprint, seed, stage, code_commit, toolchain}` + file-level provenance); (5) a **non-strippable synthetic-only / anti-anonymity caveat** on every metric (AX-001/003); and (6) for **leaderboard / published entries**, a **contamination disclosure** (`contamination_status` with `unknown` rejected) + a **signed attestation that held-out labels were not exposed**.
>
> **Enforcement scope is run-type-bound** (FR-038): the **full** AX-005 bar binds `leaderboard-submission` / `filing-grade`; `smoke` / `dev` **suppress CI + p-value emission entirely** — there is no un-rigorous number to mis-cite because there is *no number*. **Manifest-reproducibility is UNIVERSAL** (binds all run-types, AX-002); **pre-registration is opt-in** (high-stakes run-types only).

- **Status: CONFIRMED** at R7 (6/6 R6 respondents voted Yes; one Yes-with-change) — moves from PROPOSED (R4) to **binding, pending PO sign-off**. The NFRs in `non-functional-requirements.md` are the testable operationalization.
- **Adopted sharpening (SRV-04, the gaming / threat-model seat):** element **(6) binds `leaderboard-submission` AND `filing-grade`**, not filing-grade only. No change to the 6-element core or the run-type-bound / manifest-universal split.
- **Two sharpenings carried from R3 into the axiom text:** (a) multiplicity-family declaration is explicit in the axiom/report text (INT-01/02, "reviewers will ask"); (b) the 6th contamination element (INT-03).
- **Wiring:** (1)→NFR-023/024/025 · (2)→NFR-026/027/028 · (3)→NFR-029 · (4)→NFR-030/031/032/042/043 · (5)→NFR-044 · (6)→NFR-048/049 · enforcement-scope→NFR-033/034. The AX-005 spine bundles (B1, B5, B8, B9, B15, B16) **all land in MUST**, which is what makes the axiom enforceable rather than aspirational.
- **Inherited binding axioms unchanged:** **AX-pii-anon-001** (synthetic-only / no real PII) · **AX-pii-anon-002** (deterministic / seeded / byte-reproducible) · **AX-pii-anon-003** (stated power — every metric declares n + CI) · **AX-pii-anon-004** (anon vs pseudo scored by SEPARATE metric families).

---

## Functional Requirements register (FR-030 … FR-054)

Full Given/When/Then + boolean tests + reuse grounding live in `functional-requirements.md`. Priorities are the **final R7-committed** classes.

| FR | Title (abbrev.) | Spine stage | UC | Priority |
|---|---|---|---|---|
| **FR-030** | Reconcile `pii-rate-elo` dataset seam to v2.0.0 | LOAD | UC-21 | **MUST** (P2) |
| **FR-031** | Versioned seam crosswalk + regression contract (5-tuple) | LOAD | UC-21 | **MUST** (P2) |
| **FR-032** | Powered, lattice-stratified, seeded sampler | SAMPLE | UC-16 | **MUST** (P3) |
| **FR-033** | PowerMatrix verdict + per-cell named shortfall (realized positives) | SAMPLE | UC-16/23 | **MUST** (P3) |
| **FR-034** | Reproducible sample manifest + non-strippable caveat | SAMPLE | UC-16 | **MUST** (P3) |
| **FR-035** | Three presets (powered-representative default / full opt-in / smoke) | SAMPLE/RUN | UC-16/19/20 | **MUST** |
| **FR-036** | Full-corpus opt-in run (descriptive census; count from version-pinned loader) | SAMPLE/RUN | UC-19 | SHOULD |
| **FR-037** | Smoke run with suppressed inferential outputs | SAMPLE/RUN | UC-20 | SHOULD |
| **FR-038** | Run-type designation scoping pre-reg + AX-005 bar + backing sample mode | SAMPLE/RUN/X | UC-18/19/20 | **MUST** (D2) |
| **FR-039** | Assessment run wired to existing engine + convergence (no rebuild) | RUN/SCORE/RATE | UC-17/19 | **MUST** |
| **FR-040** | Per-metric CIs under a deterministic interval-selection rule | SCORE | UC-17/23 | **MUST** (AX5-1) |
| **FR-041** | Paired significance + Holm-Bonferroni + declared multiplicity family | RATE | UC-17/23 | **MUST** (AX5-2) |
| **FR-042** | Quarantine fabricated `significance.py` from run surface (CI-enforced) | RUN/SCORE/RATE | UC-17 | **MUST** (P1) |
| **FR-043** | Scoring-family separation (anon/pseudo) + contamination + seed-variance | SCORE/RATE | UC-17/23 | SHOULD (D6; NR-core MUST via NFR-055) |
| **FR-044** | Pre-register the run BEFORE any scoring (git-anchored + hash-chained) | X/REPORT | UC-18/19 | **MUST** (D3; enforcement opt-in) |
| **FR-045** | Per-stage observability run-record across the spine | X (all stages) | UC-22 | SHOULD (D4; assurance-MUST sub-part) |
| **FR-046** | File-level provenance on every emitted artifact | X | UC-22/23 | SHOULD |
| **FR-047** | Honest reportable leaderboard with paired-test-gated ranks | REPORT/X | UC-23 | **MUST** |
| **FR-048** | Operating-point reporting (Fβ β>1 / FN:FP cost + AUPRC @ pre-reg point) | REPORT | UC-23 | **COULD** (D5; **MUST-for-P-priv-eng**) |
| **FR-049** | Non-strippable honesty-flag bundle on every figure + RD-convergence | REPORT/X | UC-23 | **MUST** (AX5-3/5) |
| **FR-050** | Self-verifying report (embeds pre-reg hash + run id) | REPORT/X | UC-18/22/23 | **MUST** (AX5-4) |
| **FR-051** | Leaderboard hygiene: blind/provenance submission + held-out-non-exposure attestation | X | UC-17/23 | **MUST** (D8 carve-out; AX5-6) |
| **FR-052** | Neutrality / governance statement field + recusal record | X | UC-18/23 | SHOULD (D8; inadmissibility-grade) |
| **FR-053** | Regulatory taxonomy crosswalk (63 types → GDPR/HIPAA/CCPA/GLBA) | X | UC-23 | SHOULD (D8; **AUTHOR not defer**) |
| **FR-054** | Citable / DOI-able release + claims policy | X | UC-23 | SHOULD (D9; **MUST-for-P-acad-deid**) |

**FR priority split: 16 MUST · 8 SHOULD · 1 COULD.**
**MUST (16):** FR-030, FR-031, FR-032, FR-033, FR-034, FR-035, FR-038, FR-039, FR-040, FR-041, FR-042, FR-044, FR-047, FR-049, FR-050, FR-051.
**SHOULD (8):** FR-036, FR-037, FR-043, FR-045, FR-046, FR-052, FR-053, FR-054.
**COULD (1):** FR-048 (operating-point view — COULD-overall, MUST-for-P-priv-eng; D5).

> **R4→R7 FR delta (19 MUST → 16 MUST), documented + reversible at Pass-2.** Three R4-provisional MUSTs were demoted on honest persona signal driven by the **sampling gap** (the MEDIUM personas that make them MUST were unseated this round): **FR-043** (B10 new anon/pseudo sub-parts → SHOULD; the never-merge NR-core stays MUST via NFR-055/G-norg), **FR-045** (B12 per-stage run-record → SHOULD overall; assurance-MUST sub-part flagged, D4), **FR-048** (B14 operating-point → COULD-overall/persona-MUST, D5). These are demotions of *confidence in the present cohort*, not judgements that the capabilities are low-value.

---

## Non-Functional Requirements register (NFR-019 … NFR-055)

Full thresholds + measurement methods + axiom/precondition linkage live in `non-functional-requirements.md`. Grouped by the quality-attribute family; priorities are the **final R7-committed** classes.

| Group | NFRs | Priority (R7) |
|---|---|---|
| **A. Statistics-core integrity (P1)** | NFR-019 (quarantine), NFR-020 (fabrication ban), NFR-021 (seeded LOCAL-RNG), NFR-022 (integer-guarded intervals) | all **MUST** |
| **B. CIs on every metric (AX5-1)** | NFR-023 (CI on 100% + selection rule), NFR-024 (conditional-on-sample scope), NFR-025 (census = descriptive/no-CI) | all **MUST** |
| **C. Paired tests + multiplicity (AX5-2)** | NFR-026 (paired test required), NFR-027 (two families + Holm + family size), NFR-028 (ranks gated by paired verdict) | all **MUST** |
| **D. Convergence (AX5-3)** | NFR-029 (max-RD ± 2RD + stopping rule) | **MUST** |
| **E. Reproducibility + pre-reg + run-type (AX5-4 + scope)** | NFR-030 (byte-repro UNIVERSAL), NFR-031 (pre-reg completeness opt-in), NFR-032 (census pre-reg parity), NFR-033 (run-type scoping), NFR-034 (smoke statistically inert) | all **MUST** |
| **F. Powered sampling (P3)** | NFR-035 (powered-tier OR named shortfall), NFR-036 (shortfall in realized positives), NFR-037 (UNDER_SAMPLED/CORPUS_LIMITED/EMPTY), NFR-038 (single-pass bounded-memory sampler), NFR-039 (design point + coverage envelope in manifest) | all **MUST** |
| **G. Seam reconciliation (P2)** | NFR-040 (seam→v2.0.0 via versioned crosswalk), NFR-041 (regression contract 5-tuple fails red) | all **MUST** |
| **H. Observability provenance (AX5-4)** | NFR-042 (one run-record per stage, shared run id), NFR-043 (file-level provenance) | **SHOULD** (D4; assurance-MUST sub-part) |
| **I. Honest reporting (AX5-5/6)** | NFR-044 (non-strippable caveat), NFR-045 (anon/pseudo separate; pseudo never bare-F1), NFR-046 (operating-point view), NFR-047 (honesty flags + self-verifying report) | NFR-044/047 **MUST**; NFR-045 SHOULD (NR-core via NFR-055); NFR-046 **COULD** (rides FR-048; D5) |
| **J. Leaderboard hygiene (AX5-6)** | NFR-048 (contamination disclosure; `unknown` rejected; attestation), NFR-049 (held-out protected + provenance-stamped/blind) | both **MUST** |
| **K. Engineering integrity** | NFR-050 (pure-stdlib cores + lazy heavy-dep guards) [GATE], NFR-051 (`pii-rate-elo` gates green) | NFR-050 **MUST-grade gate** (D10); NFR-051 **MUST** |
| **L. Cycle-1 no-regression guardrails** | NFR-052 (lattice 730 @ `47c3a8f`), NFR-053 (NFR-018 power gate ON), NFR-054 (doc-drift = 0), NFR-055 (four families never merged) | all **MUST-grade gates** (D10/G-norg) |

**NFR priority split: 32 MUST · 4 SHOULD · 1 COULD.**
**SHOULD (4):** NFR-042, NFR-043, NFR-045, NFR-055.
**COULD (1):** NFR-046 (operating-point reporting — rides FR-048; D5).
**MUST (32):** all others (NFR-019…041, NFR-044, NFR-047, NFR-048, NFR-049, NFR-050, NFR-051, NFR-052, NFR-053, NFR-054).

> **Grounding note (verified at HEAD this session):** `stats/power.py::PowerMatrix.verdict` returns LARGE iff well-powered fraction ≥ 0.999, ADEQUATE iff ≥ 0.80, else SMALL (L357-361); `TIER_SPECS` targets 1522/753/200 are **derived** via `required_n` (CRITICAL `(0.99,0.005)`, STANDARD `(0.98,0.010)`, LONG_TAIL `(0.95,0.03025)`); `REID_TIER_SPECS` = 897/385 *pairs* (out-of-scope re-id ladder); `tests/test_doc_drift.py` pins `CANONICAL_RECORDS="575,604"` and `CANONICAL_ENTITY_COUNT = tx.ENTITY_TYPE_COUNT` (=63, derived, never hardcoded). `stats/intervals.py`, `stats/paired.py`, `stats/power.py`, `stats/lattice.py` all present where the NFRs cite them.

---

## Priority register (the v0.1 floor at a glance)

**MUST — the v0.1 floor (16 FR + 32 NFR):**
*Preconditions:* FR-030/031 (P2) · FR-032/033/034 (P3) · FR-042 (P1) · NFR-019/020/021/022 (P1) · NFR-035/036/037/038/039 (P3) · NFR-040/041 (P2).
*AX-005 spine:* FR-038/040/041/044/047/049/050/051 · NFR-023/024/025/026/027/028/029/030/031/032/033/034/044/047/048/049.
*Presets + engine:* FR-035/039.
*Engineering + no-regression gates:* NFR-050 · NFR-051 · NFR-052/053/054/055.

**SHOULD (8 FR + 4 NFR):** FR-036, FR-037, FR-043, FR-045, FR-046, FR-052, FR-053, FR-054 · NFR-042, NFR-043, NFR-045, NFR-055.

**COULD (1 FR + 1 NFR):** FR-048 + NFR-046 (operating-point view — persona-stratified-MUST-pending-its-seat).

**No bundle scored majority-WON'T → 0 OUT items** (consistent with the SME-pre-filtered UC set; nothing de-scoped to out-of-cycle).

---

## Persona-stratification register (do NOT mistake a SHOULD/COULD for "low-value universally" — R7 §7)

| FR / NFR | Universal verdict | Persona-stratified reality |
|---|---|---|
| **FR-054** DOI release | SHOULD | **MUST** for P-acad-deid citation cohort; silent for CI-gate / procurement / oracle (D9). A Zenodo DOI is a HARD citation gate (INT-01/02); a GitHub SHA link-rots. |
| **FR-048 / NFR-046** operating-point | COULD | **MUST** for P-priv-eng (the false-positive tax — INT-04: F1=0.91 → precision 0.71 @ recall 0.93 → 34k FPs/10k entities → 3× license cost); peripheral for the HIGH cohort (D5). **The bundle most distorted by the sampling gap.** |
| **FR-052 / FR-053** governance + crosswalk | SHOULD | **inadmissibility-grade** for P-dpo / P-complreviewer + P-priv-eng procurement (INT-04/05); FR-051 hygiene is MUST universally (D8). |
| **FR-045 / NFR-042** per-stage run-record | SHOULD | **audit-MUST** for P-complreviewer (Art-11 send-back floor — INT-05); methods-section-nice for the HIGH cohort (D4). |
| **FR-043 / NFR-045** anon/pseudo separation | SHOULD | **legally load-bearing** for P-dpo (AX-004); low-salience for clinical de-id (irreversible removal) — but the **NFR-055 never-merge invariant is MUST-grade universally** (D6). |
| Throughput SLA (D12) | roadmap | **HARD pre-gate** for P-agentic-redteam (≤50 ms p95 / ≥500 rps — INT-06); absent for everyone else. |

---

## Carried as deferred-with-rationale (NOT silently dropped — bridge §4, R7 D11/D12)

- **Re-id / RRS family** (PGO-acaddeid-02, PGO-researcher-02, PGO-builder-03): **out of CAP-02 v0.1** — re-id power uses the distinct `stats/power.py::REID_TIER_SPECS` ladder (897/385 *pairs*, operating point p≈0.1–0.5), RRS scenarios live in cycle-1 UC-08/09. Named roadmap (Open Item 13 / MEI-06). The anon-vs-pseudo *separation* (AX-004) IS in-scope (FR-043/047); the RRS *figure* is roadmap. **These are explicitly-scoped-OUT boundaries, not orphans.**
- **Agentic recognition-oracle / RRS-on-transcripts** (PGO-redteam-01/02/03): cycle-1 UC-08/09 + live-harness-adapter roadmap; CAP-02 is the static powered-assessment workflow, honestly bounded.
- **Oracle throughput SLA + callable surface** (N-06; INT-06: ≤50 ms p95 / ≥500 rps): routes to the oracle track (cycle-1 UC-08 / C9). Not a CAP-02-v0.1 blocker; surfaced by making `scripts/benchmark_throughput.py` output machine-readable in FR-049/050. Carried as a named MEDIUM-persona (P-agentic-redteam) roadmap quality attribute (D12).
- **Real-data correlation slice** (cycle-1 UC-13, vs i2b2-2014 / TAB): the single highest-leverage credibility unlock and the **strongest convergent missing-capability signal of R6** (4 of 6 named it). Out-of-band / gated on external DUA / **explicitly NOT v0.1-blocking** (DF-4, unanimous). Carried as a **named COULD-scope roadmap stub** + the FR-049 "named-and-pending" report flag (D11). Does **not** mint a new FR this cycle (no v0.1 acceptance path).

---

## DIVERGED / PERSONA-CONDITIONAL flags carried to Design + Pass-2

- **`filing-grade` backing-mode (DF-1 INT-05 pushback):** carried as the FR-038 filing-grade profile; real-user DPO verification of "well-labeled powered-sample vs full-corpus for filing" is a **Pass-2** must.
- **The P-dpo / assurance lens is FIRST-CONTACT** (INT-05): the compliance FRs/NFRs (FR-045/046/050/052/053; NFR-042/043) trace to a single un-re-confirmed lens. Real-user DPO interviews remain a Pass-2 must (compounded with the unseated MEDIUM cohort at R6).
- **The 3 MEDIUM personas (P-priv-eng, P-dpo/P-complreviewer, P-agentic-redteam) were UNSEATED at R6** — MEDIUM-owned bundles were adjudicated against the R3-elicited priority, never de-scoped on the absent-seat vote (D4/D5/D8/D12). A Pass-2 with a real **P-priv-eng** seat is the single highest-priority re-elicitation (FR-048).
- **Thresholds embedded in FR/NFR text are directional** (e.g. <10 min smoke, <30 min powered, ≤50 ms/≥500 rps, 3-seed Kendall-τ minimum, 0.80/0.999 verdict cuts). They are NOT committed values; R9 verification-criteria + R10 threshold-validation pressure-test them, recorded in `_threshold-validation/`.

---

## See also

`functional-requirements.md` (FR-030…054, full Given/When/Then) · `non-functional-requirements.md` (NFR-019…055, full thresholds) · `traceability-matrix.md` (UC↔FR/NFR + axiom + PGO linkage + orphan check) · `methodology.md` (representative-scale + AGENT_SIMULATED + single-session limit + Pass-2 gaps) · `_bridge/uc-pgo-map.md` (R0 bridge) · `prioritization-decisions.md` (R7 D1–D12) · `interview-synthesis.md` (R3 INT-01…06) · `survey-analysis.md` (R6 aggregate). Discovery: `01-discovery/discovery-report.md`, `01-discovery/04-use-cases.md`, `01-discovery/personas.md`.

✅ **R8 Requirements Document complete (2026-06-01).** Consolidated **25 FRs (FR-030…054; 16 MUST / 8 SHOULD / 1 COULD)** + **37 NFRs (NFR-019…055; 32 MUST / 4 SHOULD / 1 COULD)** = **62 requirements (48 MUST / 12 SHOULD / 2 COULD)** + 2 MUST-grade baseline gates. The **3 hard preconditions all land in MUST** (P1/P2/P3); **AX-pii-anon-005 recorded as CONFIRMED** (one adopted sharpening) pending PO sign-off; the **default-mode reconciliation decision recorded explicitly** (powered-representative default always power-labelled / full = citable / run-type scoping). ID offsets honored (FR→030, NFR→019, never renumbered/reused). `provisional_status: AGENT_SIMULATED`; real-user Pass-2 named. Ready for Stage 3 Design.
