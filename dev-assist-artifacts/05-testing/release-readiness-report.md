# Release-Readiness Report — pii-anon-datasets v2.0.0

**Stage 5 · Wave T6 (FINAL synthesis)** · 2026-05-31 · Produced by `dev-assist-testing-release-readiness`
**Scope:** the PII-Anon CC0 synthetic-PII benchmark + pure-stdlib evaluation harness (`src/pii_anon_datasets/`).
**Policy:** `developer-assistant.yaml testing.pass2_required: false` (4B default) — a PERSONA-CONDITIONAL / DIVERGED row lacking real-data/real-user Pass-2 evidence downgrades **SHIP → SHIP-WITH-CAVEATS**; it does **not** DEFER. **DEFER is reserved for a MUST-track FAILURE** (a failing MUST NFR, a carrying-forward SHOWSTOPPER, or a Pass-2 invalidation requiring pivot). None of those obtain.
**Provisional status:** `AGENT_SIMULATED` — every Stage-4 verdict is agent-self-assessed; a real-CI Pass-2 is owed (carried as Caveat 4).

> **Discipline note.** This report *synthesizes and rules*; it audits nothing new. Every load-bearing claim cites a `file:section` or a git fact. No finding is generated here; where a prior wave flagged a limitation it is carried verbatim, never invented and never stripped.

> **Brownfield — Source Signal vs Gaps.** PII-Anon entered the PDLC with a brownfield assessment that rated Testing WEAK→PARTIAL and filed **C1 (CATASTROPHIC): zero automated tests; the scoring harness itself is unverified** (`05-testing/02-architecture/test-architecture.md §0`). Stage 4 closed C1 by growing the suite 0 → 346 tests under strict TDD; Stage 5 measured the result. This first-release verdict therefore carries the methodology-evidence debt typical of a brownfield project: the evidence base is real and green, but it is `AGENT_SIMULATED` until a real CI + real-data Pass-2 runs.

---

## 1. Verdict

# **SHIP-WITH-CAVEATS**

**Rationale (one sentence):** All four privacy directions (detection / anonymization / pseudonymization / measured-RRS) are runnable and statistically grounded with M6 closed (`_signoffs/SO-02-s3.yaml:scope`); every quantified NFR PASSES except **NFR-010** throughput, which is honestly **PROVISIONAL** pending a real-host Pass-2 (`05-testing/03-nfr-verification/nfr-verification-matrix.md#aggregate` — 12 PASS / 1 PROVISIONAL / 0 FAIL); there is **no MUST-track failure, no showstopper, and no Pass-2 invalidation**, so the binding limitations are documented caveats — not blockers — for a CC0 synthetic eval.

**Decision-tree trace** (per the T6 verdict tree):

| Gate | Result | Evidence |
|---|---|---|
| Any MUST NFR FAIL? | **No** (0 FAIL) | `nfr-verification-matrix.md#aggregate`, `#fail-details` ("None.") |
| Any SHOWSTOPPER carrying forward? | **No** (every story + sprint gate APPROVE, 0 MAJOR+ open) | `_reviews/sprint/{S3,S4,S5,S6,S7}/synthesis.md` (all "Aggregate: APPROVE"); `SO-0{1..6}-*.yaml` |
| Any Pass-2 invalidation requiring pivot? | **No** (Pass-2 is protocols-only; nothing run, nothing invalidated) | `05-testing/05-pass2/*/protocol.md` (all 5 are protocols; `INSUFFICIENT_EVIDENCE → SHIP-WITH-CAVEATS`, never PIVOT, because un-run) |
| Any UI-surface a11y HOLD? | **No** (N/A — no UI) | `05-testing/04-accessibility/accessibility-audit-results.md` ("NOT APPLICABLE") |
| All MUST NFRs PASS **and** all DIVERGED REAL_USER_VALIDATED **and** all surfaces a11y PASS **and** ≤3 MAJOR open? | **NFRs: NFR-010 PROVISIONAL (not all PASS); DIVERGED rows: not yet real-user-validated** → the SHIP precondition is not met | `nfr-verification-matrix.md#provisional-details`; `SO-06-s7.yaml:findings_waived_to_pass2` |
| **⇒ Outcome** | **SHIP-WITH-CAVEATS** (with the explicit caveat list in §5) | this report |

---

## 2. Evidence summary

| Evidence area | Result | Citation |
|---|---|---|
| **NFR coverage** | **12 PASS / 1 PROVISIONAL / 0 FAIL** over the 13 quantified/auditable NFRs routed to T3. PASS: NFR-001/002/003/004/005/006/008/012/013/014/016/018. PROVISIONAL: NFR-010 (throughput b/c, `real_user_needed`). | `nfr-verification-matrix.md#aggregate` |
| `validate.py` power gate | **0 errors**, exit 0, over **575,604 records / 575,604 unique IDs**; NFR-018 committed-cell power gate PASS (all committed cells meet tiered target). | `nfr-verification-matrix.md#nfr-001` & `#nfr-018`; re-measured this dispatch |
| Committed lattice | **730 cells**; `eval_lattice.json` round-trips `build_committed_lattice()` (anti-drift, 0 drift). | `nfr-verification-matrix.md#nfr-018`; **git-verified**: `eval_lattice.json` last touched `47c3a8f` (2026-05-29), **zero** commits touch it through HEAD `1423167` |
| **A11y** | **N/A — no UI surface** (CC0 dataset + pure-stdlib library + thin console CLI). Recorded as an explicit "not applicable" finding, not a skipped obligation. De-scoped throughout the PDLC. | `accessibility-audit-results.md` (Determination + Outcome) |
| **Pass-2** | **5 protocols authored; 0 run** (Wave T5). Each refuses agent-simulated substitution and maps `INSUFFICIENT_EVIDENCE → SHIP-WITH-CAVEATS` (never DEFER, never PIVOT while un-run). | `05-pass2/{FR-027,NFR-010,design-real-user-trial,formulaic-distribution-shift,FR-015-016}/protocol.md §8` |
| **Findings carried forward** | All work-streams **APPROVE with 0 MAJOR+ open**; remaining items are OBSERVATION-level (lint baseline, hosted-leaderboard hardening, recursive gold-key screen, O(n²) seams at seam-scale). No showstopper, no unresolved MAJOR. | `_reviews/sprint/{S3..S7}/synthesis.md` (reviewer tables); `SO-0{1..6}-*.yaml:findings_waived_to_pass2` |
| **Test suite** | **346 passed / 1 skipped / 0 failed** (the 1 skip = `anthropic`-absent live-LLM contract test, by design — the deterministic offline adversary is the RRS headline). | `nfr-verification-matrix.md#nfr-016`; `SO-06-s7.yaml:evidence`; `examples-and-tests-catalog.md §6.3` |

---

## 3. Test-architecture summary

**Pyramid shape: CLASSIC PYRAMID with a PROPERTY-TEST mantle** — broad unit base, thin integration band, small named system cap; measured from inline test-type markers, not asserted (`test-architecture.md §1`).

| Marker | Count | Band |
|---|---|---|
| `[UNIT-TEST]` | 108 | base |
| `[PROPERTY-TEST]` | 45 | base mantle (determinism / invariants) |
| `[CONTRACT-TEST]` | 15 | port boundaries (Hexagonal) |
| `[AUDIT]` | 15 | cross-cutting structural guards |
| `[INTEGRATION-TEST]` | 14 | export↔load round-trips, store↔policy, CLI dispatch |

Unit + property dominate (~153 of ~197 marked assertions; ~7.7:1 unit+property : integration). **Anti-pattern check:** ice-cream-cone NOT present; no hidden integration weight in "unit" files (heavy deps gated behind `pytest.importorskip`). Justified by project profile, not "best practice": correctness lives in pure stdlib functions; the architecture is Hexagonal (scoring core) + Clean (DC-09 stats), making the integration band small by construction; there is no UI/service runtime to drive an e2e tier (`test-architecture.md §1` justification + anti-pattern check).

**Coverage (NFR-016, hard gate — CLEARED with margin on both axes):**

- **Aggregate: 96.4% line (2364/2452), 88.7% branch (605/682)** over 11 covered packages (`test-architecture.md §5`).
- **scoring + stats (the credibility-bearing surface): 95.18% line (1,421/1,493), 84.52% branch (355/420)** — line **+10.18pp** over the ≥85% bar, branch **+14.52pp** over the ≥70% bar (`nfr-verification-matrix.md#nfr-016`).
- Lowest scorer/stats module `signals.py` at 86% line — still above the 85% floor (`test-architecture.md §5`).

---

## 4. Cross-cutting discipline summary

| Discipline | Status | Evidence |
|---|---|---|
| **TDD discipline** | Strict RED→GREEN→REFACTOR per Build Task across S-PWR+S3+S4+S5+S6+S7; a Build Task is not GREEN until its FR/NFR has ≥1 named test. | `SO-0{1..6}-*.yaml:scope` ("strict TDD"); recent git log shows `[RED]`/`[GREEN]`/`[REFACTOR]` triplets |
| **Traceability** | **0 orphans**: all 29 FR + 18 NFR accounted; **221** test fns carry an `fr_/nfr_` token (of 335); explicit-to-inferred ≈ 85/15. The token convention is the traceability join (closes brownfield M3). | `examples-and-tests-catalog.md §6.1/§6.2` (29/29, 18/18, zero orphans); `test-architecture.md §3.1` |
| **CI health** | Full suite **346 passed / 1 skipped / 0 failed**; lint (ruff) + type (mypy --strict) clean; **flakiness budget ZERO** (count-based power gate, equality-not-tolerance determinism, local explicit seeds). One copy-paste CI invocation defined (DX-03). | `nfr-verification-matrix.md#nfr-016`; `test-architecture.md §3.6, §4` |
| **Determinism (AX-002)** | Seeded/offline paths byte-reproducible (frozen-dataclass equality, not a seed-fakeable hash); LLM paths flagged `deterministic=False`, version-stamped; offline adversary proven nondeterminism-free by AST import audit (no `random`/`time`/`datetime`). | `test-architecture.md §3.4, §3.5, §2.4` |
| **Non-strippable caveats** | Privacy figures cannot be emitted without their caveat — caveat is a mandatory non-defaulted value-object field (TypeError on omit, rejected on empty, survives `as_dict()`). Replicated for RRS anti-anonymity, exposure "NOT RRS", EDPB Art 4(5), DPIA disclaimer, CoI no-pre-pub attestation, slice low-power, correlation `RealDataAbsent`. | `test-architecture.md §3.3`; `SO-06-s7.yaml:evidence` ("5/5 scope-honesty disclaimers non-strippable") |
| **NFR-005 / AX-004 separation** | Zero code paths merge anon + pseudo into one headline; mutation-tested against 4 fusion vectors; no `__float__`/combined/deid field in the scoring public API. | `nfr-verification-matrix.md#nfr-005`; `_reviews/sprint/S3/synthesis.md` (4 fusion vectors rejected) |
| **Mutation / perf gates** | No full mutation score and no perf gate in v1 (targeted no-merge/no-fusion audits exist); flagged, not silently omitted. Consistent with NFR-010a no-throughput-floor. | `test-architecture.md §5` (mutation), `§2.6` (perf) |

---

## 5. Caveats (non-strippable — carried, NEVER fabricated)

These five bind the SHIP-WITH-CAVEATS verdict. Each is a pre-existing, documented limitation; none is a MUST failure. Mitigations are the authored Pass-2 protocols (`05-pass2/`). Owner / deadline reflect that Pass-2 is **OPTIONAL** under `pass2_required: false` — these are release-honesty obligations and v1.1 unlocks, not v1 ship-blockers.

| # | Caveat | Why it is a caveat, not a blocker | Mitigation (protocol) | Owner | Deadline |
|---|---|---|---|---|---|
| **1** | **Synthetic-only external-validity gap.** FR-027 synthetic→real transfer is unmeasured; `correlate(real=None)` returns the `RealDataAbsent` sentinel and never fabricates a correlation. Every committed-cell metric carries the non-strippable "not citable as a standalone recall claim absent the real-data correlation slice" caveat. | FR-027 is SHOULD / v1.1; the v1 seam ships and is honest. `pass2_required: false` ⇒ un-Pass-2'd PERSONA-CONDITIONAL row downgrades, does not DEFER. | Real i2b2-2014 + TAB correlation (Kendall τ-b + Bland-Altman) on the domain-matched English slice; pre-registered; real PHI never enters repo (derived score matrix only). `05-pass2/FR-027/protocol.md` | De-id collaborator + maintainer (needs i2b2/n2c2 DUA) | v1.1 / when a DUA-holding collaborator is secured |
| **2** | **Design was never real-user-trialed.** R10 was a SIMULATED panel (6-persona 2026-05-28 + 10-persona 2026-05-29 NFR-018 amendment); the concept-value study was 15 simulated agents, explicitly "NOT a substitute for real users." | The locked thresholds (1,522/753/200) were ACCEPTED-WITH-CAVEATS by the simulated panel with 0 REVISE; design credibility rests on simulation until real consumers confirm. Downgrades, does not DEFER. | n=12–18 real consumers, 2–3 per persona; semi-structured interview + artifact walkthrough; mirrors the R10 10-sub-archetype split for comparability. `05-pass2/design-real-user-trial/protocol.md` | Maintainer + recruited panel (de-id/privacy-ML community; paid role-screened backfill) | v1.1 / first real-consumer study window |
| **3** | **~72% formulaic-template synthetic monoculture.** ~72% of the 575,604-record corpus carries `provenance.source_type="synthetic_lattice_enrichment"` (filterable). Power is **precision on the synthetic distribution, not external validity** — a tight committed-cell CI is not generalization. | DATASHEET/README state this plainly; the caveat is non-strippable on every per-cell metric. The enrichment raised statistical power legitimately (NFR-018 PASS); the open question is distribution-shift magnitude, which is a measurement, not a defect. Downgrades, does not DEFER. | Real-data distribution-shift study vs i2b2/TAB feature histograms (derived only); quantify the power discount + name the most-monocultured types/languages. `05-pass2/formulaic-distribution-shift/protocol.md` | Maintainer + de-id collaborator (co-located i2b2/TAB acquisition with #1) | v1.1 / same DUA window as #1 |
| **4** | **All evidence is AGENT_SIMULATED; real-CI Pass-2 owed.** Every story + sprint gate is an agent self-assessment; the suite has not run in a clean, provisioned external CI image. The two environment-conditional guarantees — Parquet→HF-`datasets` load and full `mlcroissant` spec-conformance (NFR-012) — degrade to `importorskip` skips when the `distribution`/`croissant` extras are absent. | No FAIL was observed; the local run is **346 passed / 1 skipped**; NFR-012's HF `datasets` round-trip *did* run in-env. The gap is provenance (self-assessed vs CI-attested), not a known break. Downgrades, does not DEFER. | Real CI run on a clean checkout with `.[dev,baselines,llm,distribution,croissant,viz]`; the one copy-paste DX-03 invocation. `test-architecture.md §4, §7.1` | Maintainer / CI of record | Before any MUST counts RELEASE-verified (v1.0 release-CI) |
| **5** | **NFR-010 runtime throughput unmeasured on real hardware.** NFR-010b (lightweight path ≥5,000 rec/sec on 8-core + p50/p95/p99) and NFR-010c (batch wall-clock) are `real_user_needed: true`. No throughput harness or rec/sec emitter exists in the codebase (a forward seam by Stage-2/3 design); **no number was fabricated**. | NFR-010 is the sole PROVISIONAL row; NFR-010a has no floor; transformer/LLM detectors are exempt. This is a real-hardware measurement gap, not a missing Stage-4 deliverable. Per policy and the protocol, this is **explicitly SHIP-WITH-CAVEATS, not DEFER**. | Real 8-core reference-host benchmark (declared spec); ship `scripts/benchmark_throughput.py`; record rec/sec per detector-class + p50/p95/p99 + streaming/chunked. `05-pass2/NFR-010/protocol.md` | Runtime privacy engineer + maintainer (8-core CI/cloud host) | v1.1 / first reference-host provisioning |

---

## 6. Known scope gaps (acceptable for v1)

Distinct from the caveats above — these are **bounded feature gaps**, all SHOULD/COULD priority, each documented and honestly framed (not silent omissions). None affects a MUST verdict.

| Item | Priority | v1 status | Evidence |
|---|---|---|---|
| **FR-014** — query-aware masking scorer | SHOULD | **Genuine gap** — no `fr_014` token, no test. Acceptable for v1; recommend a seam test for the query-aware records slice. | `examples-and-tests-catalog.md` FR-014 ("GAP (SHOULD)"); §6.1 |
| **FR-028** — frictionless citation (BibTeX/CITATION.cff) | SHOULD | **Genuine gap** — no `fr_028` token; citation presence implied by dataset-card tests but not explicitly traced. Recommend a `CITATION.cff` presence check. | `examples-and-tests-catalog.md` FR-028 ("GAP (SHOULD)"); §6.1 |
| **FR-015 / FR-016** — coreference-chain & quasi-id-combination scoring | SHOULD | **v1 seam ships, full feature deferred to v1.1.** Slice loaders (`coreference_slice`, `quasi_identifier_slice`) with non-strippable ~72%-formulaic low-power caveat; chain-as-a-unit / qid-combination *scoring* is v1.1/Pass-2. | `examples-and-tests-catalog.md` FR-015/FR-016 ("Pass-2 deferred"); `SO-06-s7.yaml:decisions_acknowledged` |
| **FR-027** — real-data correlation harness | SHOULD | **v1 seam ships, full real-data run deferred.** (Also Caveat 1.) Harness seam-tested (`RealDataAbsent` sentinel, non-strippable caveat, deterministic bootstrap CI); real i2b2-2014/TAB correlation is v1.1 Pass-2. | `examples-and-tests-catalog.md` FR-027 ("Pass-2 deferred") |
| **FR-018 / FR-019 / FR-020** — cross-turn fragmented leakage / transcript residual-leakage / live-harness adapter | COULD | **Roadmap-only.** Documented in ROADMAP.md, pinned by `test_roadmap.py` property tests as future-not-shipped; no feature implementation in v1. | `examples-and-tests-catalog.md` FR-018/019/020 ("doc-pinned"); `SO-06-s7.yaml` |

---

## 7. Guardrails held (frozen-asset integrity)

The release does not silently mutate any frozen evaluation asset. Verified independently against git, not merely asserted by the signoffs:

| Guardrail | State | Evidence |
|---|---|---|
| `eval_lattice.json` frozen (**730 cells @ `47c3a8f`**) | **HELD** — last touched `47c3a8f` (2026-05-29); **zero** commits touch it through HEAD `1423167`; round-trips its deterministic generator (0 drift). | **git-verified** (`git log 47c3a8f..HEAD -- eval_lattice.json` empty); `nfr-verification-matrix.md#nfr-018`; `SO-04..06:evidence` |
| Tags `v1.3.0` + `pre-lattice-enrichment` intact | **HELD** — both tags present locally. | **git-verified** (`git tag` lists both); `SO-0{1..6}:evidence` |
| Corpus **575,604 records** unchanged | **HELD** — `pii_anon.jsonl.gz` untouched since baseline (`git log 47c3a8f..HEAD` empty for that path); `validate.py` confirms 575,604 records / 575,604 unique IDs / 0 errors; `metadata.json` version `2.0.0`, entity_types `63`. | **git-verified**; `nfr-verification-matrix.md#nfr-001`; `metadata.json` |
| **NFR-018 power gate PASS** | **HELD** — all committed cells meet tiered target (≥1,522/≥753/≥200, NIST-derived), exit 0, 0 shortfalls. | `nfr-verification-matrix.md#nfr-018` |
| **NFR-013 doc-drift = 0** | **HELD** — canonical 575,604 / 2,486,438 / 63 / v2.0.0 pinned across 7 docs; `test_doc_drift.py` 6/6 green; doc-drift still 0 through S6/S7. | `nfr-verification-matrix.md#nfr-013`; `SO-05-s6.yaml` / `SO-06-s7.yaml:evidence` ("NFR-013 doc-drift still 0") |

---

## 8. What would change the verdict to SHIP

SHIP requires retiring the open caveats via the Pass-2 roster — i.e. moving every PROVISIONAL/PERSONA-CONDITIONAL row to a real-data/real-user/real-host VALIDATED outcome, with no PIVOT:

1. **NFR-010 → MEASURED (real host).** `05-pass2/NFR-010/protocol.md §8`: lightweight path **≥5,000 rec/sec on a declared 8-core host** with p50/p95/p99 recorded and streaming/chunked demonstrated → NFR-010 PROVISIONAL becomes the 13th PASS. (A LOOSENED outcome — e.g. 3,000–4,999 rec/sec — substitutes the measured floor and still clears the row; only a wide miss / pathological tail is a PIVOT that would hold SHIP.)
2. **FR-027 → REAL_USER_VALIDATED.** `05-pass2/FR-027/protocol.md §8`: τ-b ≥ τ\* on **both** i2b2 and TAB with the bootstrap-CI lower bound above the pre-registered floor and Bland-Altman within band → lifts the synthetic-only citation ceiling (retires Caveat 1).
3. **Design real-user trial → REAL_USER_VALIDATED.** `05-pass2/design-real-user-trial/protocol.md §8`: real consumers confirm the design elements + locked thresholds (≈R10's ACCEPTED-WITH-CAVEATS, no DIVERGED) → retires Caveat 2.
4. **Distribution-shift study → REAL-DATA-VALIDATED (or TIGHTENED with a stated power discount).** `05-pass2/formulaic-distribution-shift/protocol.md §8`: bounds Caveat 3 to a measured, named discount.
5. **Real-CI Pass-2 green on a clean checkout** with the full optional surface → drops `AGENT_SIMULATED` (retires Caveat 4) and converts the NFR-012 `importorskip` skips to executed passes.

Until those outcomes exist **as real artifacts** (`05-pass2/*/outcome.md`), the honest verdict is SHIP-WITH-CAVEATS. **No agent-simulated cohort, synthetic reference, or sandbox throughput number may substitute** — each protocol marks substitution a CATASTROPHIC methodology violation and REFUSES it (`05-pass2/*/protocol.md` preamble).

---

## 9. Recommended next action

**Ship v1.0 of pii-anon-datasets as SHIP-WITH-CAVEATS**, publishing the five §5 caveats verbatim in the release notes / dataset card (they are already non-strippable in-artifact). Concurrently, **execute the §8 Pass-2 roster** — prioritizing (a) the **real-CI clean-checkout run** (cheapest, retires Caveat 4 and the NFR-012 skips with no external dependency) and (b) securing the **i2b2/n2c2 DUA + de-id collaborator** that co-unlocks Caveats 1 and 3 and FR-015/016. Record each outcome to `05-pass2/<item>/outcome.md` and write the corresponding Status Change Log row into `02-requirements/traceability-matrix.md`; re-run T6 to re-rule toward SHIP once the roster lands.

---

## 10. Handoff signal — PDLC closure for this release

**Stage 5 Testing is COMPLETE for pii-anon-datasets v2.0.0.** This report is the canonical release-readiness verdict and closes the developer-assistant PDLC for this release cycle:

- **Development COMPLETE** (S1 + S2 + S-PWR + S3 + S4 + S5 + S6 + S7 all DONE; `SO-06-s7.yaml:scope`).
- **Testing COMPLETE** (T2 architecture, T3 NFR-verification, T4 a11y N/A, T5 Pass-2 protocols, T6 catalog + this synthesis).
- **Release verdict: SHIP-WITH-CAVEATS** — actionable, evidence-backed, caveats non-strippable, Pass-2 roster authored and routed.

The PDLC reopens for v1.1 upon the first Pass-2 `outcome.md` landing (re-run T6), or for any new scope (FR-014/028 feature work; FR-015/016/018/019/020 promotion from seam/roadmap).

---

*Conforms to the developer-assistant release-readiness-report section contract (verdict · evidence summary · test-architecture summary · cross-cutting discipline · caveats · recommended next action · handoff signal). Brownfield "Source Signal vs Gaps" header carried. Every load-bearing claim cites an artifact section or a git-verified fact; no new finding generated; no caveat fabricated or stripped.*
