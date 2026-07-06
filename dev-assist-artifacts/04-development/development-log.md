# Stage 4 — Development Log & Sprint Plan

**Date**: 2026-05-28 · Target: `src/pii_anon_datasets/` (DX-01: nested under the existing package — no wheel-breaking rename) + v2.0.0 schema. TDD; reviewer-gate self-assessment per slice.

> **Safety:** `git tag v1.3.0` applied to HEAD (`19ce769`) **before** any v2.0.0 work — the corpus state is pinned/restorable (plan guardrail + AX-002).

## Sprint plan (from design build sequence)
| Sprint | Scope (DCs) | Status |
|---|---|---|
| **S1 Foundations** | DC-15 pytest+CI baseline · DC-04 Hexagonal scoring core + I/O contract · DC-05 detection scorer · DC-09(partial) Wilson CI · DC-07(value-object) RRS caveat | ✅ **DONE (this session)** |
| S2 Schema | DC-02 v2.0.0 unified schema + `v1_3_0_to_v2_0_0.py` migration (tag-first, archive, deterministic) | ✅ **DONE** |
| **S-PWR Power & Sampling** | DC-01/DC-09 committed-lattice statistical-power work-stream: power audit + DOE lattice + targeted stratified enrichment + CI power-gate + per-cell design provenance (FR-029, NFR-018) — inserted before S3 per the 2026-05-29 amendment | ✅ **DONE (this session)** — corpus 159,891→575,604; all 710 committed cells powered; 103 tests green |
| S3 Scorers | DC-06 anonymization (residual-risk+utility Pareto) · DC-08 pseudonymization-integrity (moat) · DC-07 measured-attack RRS (offline+LLM adversary ports) | ✅ **DONE (2026-05-29)** — 8 stories S3-01..08, all story gates + sprint gate APPROVE; 169 tests green; M6 closed (all 4 privacy directions runnable) |
| S4 Stats/reporting | DC-09 Clopper-Pearson + paired (McNemar/bootstrap) + ECE/Brier + per-language power table + viz (reliability/Pareto/heatmap) | ✅ **DONE (2026-05-29)** — 5 stories S4-01..05, all story gates + sprint gate APPROVE; 211 tests green; DC-09 complete; FR-005 fully closed |
| S5 Compliance+dist | DC-11 end-state bundle + legally-distinct crosswalk · DC-12 Parquet/Croissant/spaCy exports (fix regime-flattening) + HF card + CLI entry · **NFR-013 doc-drift fix** | ⏳ TODO |
| S6 Governance | DC-13 leaderboard (held-out, opt-in, anti-gaming, CoI recusal) + GOVERNANCE.md + contribution pipeline | ⏳ TODO |
| S7 Seams | DC-10 agentic oracle (bounded) · DC-14 real-data correlation (v1.1) · DC-01 coreference/quasi-id slices (v1.1) | ⏳ TODO |

## S1 — what shipped (real, tested code)
| Module | Closes | Notes |
|---|---|---|
| `stats/intervals.py` | FR-004, NFR-002 | **Wilson CI**, pure-stdlib, deterministic; **integer-count guard** (reidx-02 — rejects fractional k/n) |
| `scoring/core.py` | FR-003, DC-04 | Hexagonal core: `Span`, `SpanAdapter` port, **deterministic order-independent strict matching → integer counts** (reidx-02/03), `MATCHING_POLICY_VERSION` |
| `scoring/detection.py` | FR-001/004, **M6** | scores a *system's* spans; P/R/F1/F2 + Wilson CIs on integer counts; **partial-F1 reported separately, excluded from CIs** |
| `scoring/reidentification.py` | FR-007/008/009, **gov-01** | `RRSResult` value object with **mandatory non-defaulted `caveat` field** → FR-009 made structural (caveat travels with the number through any serializer); `|C|` first-class; deterministic-headline flag (reidx-01) |
| `tests/` (4 files, 23 tests) | NFR-016, **C1** | all green |
| `pyproject.toml` | M5, DX-05, NFR-016 | declared `dev`/`baselines`/`llm`/`distribution` extras; pytest pythonpath; **branch coverage**; classifier Production→**Beta** (honest) |

**Verification (this session):** `python3 -m pytest` → **23 passed**. `--cov` → **95% line, branch on** (core 100% · detection 100% · RRS 92% · intervals 86%) — clears NFR-016. Determinism confirmed (frozen dataclasses, stdlib-only core).

### SME-panel bugs fixed as code (not inherited from v1.3.0)
- **reidx-02** — the v1.3.0 `baselines/evaluate.py` adds partial matches to *both* CI denominators + fractional success counts. The new `match_strict` produces clean integer (k,n); `wilson_interval` **rejects** non-integer counts. ✅
- **reidx-03** — `evaluate.py` greedy order-dependent matching → non-reproducible. `match_strict` is a multiset operation, **order-independent** (tested by shuffling). ✅
- **gov-01** — FR-009 caveat was renderer-bound (strippable). Now a **mandatory value-object field**. ✅

## S1 — story-gate self-review (reviewer-set: code-quality · traceability · security-sast · axiom-compliance)
- **code-quality:** PASS — typed, frozen dataclasses, pure-stdlib core, docstrings cite FR/finding IDs, lint-clean (no unused), TDD evidence (tests written alongside). 
- **traceability:** PASS — every module docstring cites its FR + design finding; maps to DC-04/05/07/09/15.
- **security-sast (AX-001):** PASS — no real PII, no secrets, no network egress in core/stats (pure-stdlib); `_count_partial`/matching operate on synthetic spans only.
- **axiom-compliance:** PASS — AX-002 (determinism: stdlib, frozen, tested) · AX-003 (CIs with named method + integer counts) · AX-004 (anon vs pseudo will be separate modules; RRS value object is re-id, distinct). 
- **Verdict: APPROVE** for S1 slice.

## Honest status (epistemic)
S1 delivered the M6 scoring spine, the statistical-rigor fix, and the structural FR-009 caveat as real tested code. **S2 is now also DONE** (see below). **Sprints S3–S7 remain** (anonymization/pseudonymization/measured-RRS scorers, stats/reporting completion, exports/CLI, leaderboard/governance, remaining doc-drift) + Stage 5 Testing — each best continued in focused follow-on sessions, TDD + reviewer-gated, on this branch.

## S2 — what shipped (DONE 2026-05-28)
True-v2.0.0 clean restructure of all 159,891 records, committed on `feat/v2-scoring-harness`:
- `tier3_evaluation` wrapper consolidating the scattered RRS/behavioral/tier3-risk signal (7,003 paired-profile wrappers merged, not clobbered).
- Deterministic content-addressed `record_id`; lineage in `provenance.v1_3_0_record_id`.
- Canonical entity registry `src/pii_anon_datasets/taxonomy.py` (**63 types / 9 categories** — fixes the 48/65/80 drift); `validate.py` derives from it; +schema_version checks.
- `scripts/v1_3_0_to_v2_0_0.py` (deterministic streaming) + `migration.py` + back-compat `compat.to_v1_record()`; `load_dataset()` unchanged (DX-01).
- **Verified:** migration byte-identical across 2 full runs; `validate.py` PASSED 0 errors / 159,891 records; splits+subsets regenerated, counts preserved; pytest **33 green**; loader + back-compat smoke-pass. Doc bump (README/CHANGELOG/TAXONOMY → v2.0.0 / 63).
- **S2 story-gate:** code-quality / traceability / security-sast(AX-001) / axiom-compliance(AX-002 determinism proven, AX-004 separation) → **APPROVE**.

### Git (branch `feat/v2-scoring-harness`)
`8efbf57` spec · `75e9eed` S1 scoring foundation · `1cc8d87` v2.0.0 migration · `bf2d990` doc bump. (v1.3.0 pinned at tag `v1.3.0`.)

### Remaining doc-drift (tracked): DATASHEET counts + train-vs-eval; MIGRATION v1.3.0→v2.0.0 section; COMPARISON competitor-claim fixes + name disambiguation; TAXONOMY body pruning to exactly 63.

---

## S-PWR — Statistical Power & Sampling Design (IN_PROGRESS, 2026-05-29)

**Why:** the v2.0.0 corpus is adequate for marginal claims but under-powered for crossed dimensions — of 60×63 = 3,780 language×entity-type cells, **73% are EMPTY** and only **3.3% reach ≥753 positives**. The benchmark cannot honestly make per-(language×type×domain×difficulty×adversarial) claims. This sprint adds **hard guarantees that every COMMITTED evaluation cell meets a stated power bar**, exploiting the synthetic-data advantage (generate exactly enough seeded records to power each committed cell).

**Requirements + Design amendment (DONE, validated APPROVE):**
- NFR-001 extended to committed crossed cells; NFR-003 → per-language×type transparency; **NFR-018** (committed-lattice per-cell power, hard CI gate) added; **FR-029** (power audit + enforcement + per-cell provenance); AX-003 extended to crossed-cell granularity; NFR-011 entity-count 65→63.
- **R10 threshold validation:** literal 10-persona panel → **ACCEPTED-WITH-CAVEATS** (tier numbers 1,522/753/200 LOCKED, 0 REVISE; 6 mechanism/framing refinements bound). `_threshold-validation/findings-nfr-018-2026-05-29.md`.
- Design note `03-design/sampling-design.md`: DOE = forced estimability skeleton + balanced D-optimal fraction; estimand = main effects + 3 named 2-ways (language×entity-type, domain×track[both readings], adversarial-type×entity-type); tiered NIST targets; McNemar paired efficiency; two-gate distinction; track-specific power seam; SMALL/ADEQUATE/LARGE claim ladder.
- Cross-artifact validation: `00-validation/validation-report-2026-05-29-1200.md` → **APPROVE**.

**Stories (TDD RED→GREEN→REFACTOR; story-gate reviewer self-assessment per slice) — ALL DONE:**
| Story | Scope | Closes | Status |
|---|---|---|---|
| **P1** | `stats/power.py` — NIST `required_n`, design-time `projected_wilson_halfwidth`/`projected_interval` (method `wilson-projected`, NOT integer-guarded), `Tier`/`TierSpec`/`PowerClass`, `classify`, `audit_crossing`→`PowerMatrix` (md/csv/heatmap), McNemar `required_discordant_pairs`/`paired_vs_independent_ratio`; `taxonomy.risk_tier` (22 critical / 31 standard / 10 long_tail, derived) | FR-029, NFR-018, AX-003 | ✅ DONE |
| **P2** | `stats/lattice.py` — `build_committed_lattice(...)` (deterministic, reads PINNED `data/lattice_freq_snapshot.json` so the frozen spec survives enrichment) → frozen `data/eval_lattice.json` (730 cells) | FR-029, NFR-018 | ✅ DONE |
| **P3** | 28 missing `PIIFactory` emitters (centralized in `scripts/lattice_targeting.py` — all 63 covered, fail-loud) + `gen_targeted_record` (guaranteed 1-positive-per-record; 3 faithful value-level adversarial transforms; non-PII nonce for uniqueness) | NFR-018, AX-001 | ✅ DONE |
| **P4** | `scripts/lattice_audit.py` (shared O(1)/annotation audit + deficit) + `scripts/generate_lattice_fill.py` (SEED 91237, per-cell sub-seed, greedy running-counter w/ incidental fills, `migrate_record` normalize, exact `--dry-run` estimate) | NFR-018, AX-002 | ✅ DONE |
| **P5** | `merge_and_rebuild.py` migrate-normalize + stable-sort by content-addressed id; `scripts/write_manifest.py` (`data/MANIFEST.sha256` over 28 files + v1.3.0-tag-intact assertion) — closes M2 | NFR-004, AX-002 | ✅ DONE |
| **P6** | `validate.py` committed-cell power gate (`--lattice` default-on, `--no-power-gate`) — exits non-zero on any under-powered committed cell | NFR-018, FR-029 | ✅ DONE |
| **P7** | `scoring/detection.py::DesignProvenance` (non-strippable external-validity caveat) on `DetectionScore` + `reporting/power_table.py` (per-cell n + Wilson CI + provenance; `power_report` matrix) | FR-029, AX-003 | ✅ DONE |

### S-PWR — what shipped + verification
- **Enrichment run (Full Broad, user-approved at the dry-run checkpoint):** `pre-lattice-enrichment` tag set → before-matrix → `generate_lattice_fill.py` (415,713 records, deterministic) → `merge_and_rebuild.py` → `generate_subsets.py` → `write_manifest.py` → `validate.py` → after-matrix.
- **Corpus: 159,891 → 575,604 records · 1,239,637 → 2,486,438 annotations** (+415,713 / +1,246,801).
- **Power: BEFORE 251 well / 200 under / 259 empty (shortfall 424,144, verdict SMALL) → AFTER 710/0/0 (shortfall 0, verdict LARGE).** `03-design/_power/power-matrix-{before,after}.{md,csv}`.
- **Verification:** `pytest` **103 green**; coverage 95% line (scoring+stats; lattice 97%, power 90%, detection 100%) — clears NFR-016. `validate.py` → **0 errors, NFR-018 gate PASS** (all 710 committed cells ≥ target). Lattice anti-drift (`--check`) OK; `MANIFEST.sha256 --check` OK; **v1.3.0 tag intact** (19ce769). Re-fill record_id determinism verified (AX-002). `data/enrichment-report.json` archives before/after + provenance.
- **S-PWR story-gate self-review (code-quality · traceability · axiom-compliance · security-sast · performance):** PASS — pure-stdlib power core; targets DERIVED from NIST (no hand-typed bars, asserted); AX-001 synthetic-only (fail-loud emitter coverage; faithful adversarial obfuscation); AX-002 determinism (seeded + content-addressed + stable-sort, re-run identical); AX-003 per-cell provenance non-strippable; gate is count-based (non-flaky), distinct from the FR-002 McNemar regression gate. **Verdict: APPROVE.**
- **Honest limitations (documented, Pass-2 / follow-on):** (1) targeted records are formulaic (one carrier template) → ~72% of the corpus is enrichment; tagged `provenance.source_type="synthetic_lattice_enrichment"` (filterable); template-diversity is a follow-on. (2) Domain distribution skews to `general` (cells not pinning a domain default to general); committed domain marginals + domain×adv_track cells are each individually powered, but overall balance is general-heavy. (3) Power = precision on the SYNTHETIC distribution, **not external validity** (non-strippable caveat + FR-027 real-data slice). (4) adv×type committed to 3 reliably-faithful transforms (base64/ocr/zero-width); letter-only transforms (homoglyph/leetspeak/mixed-case) no-op on digit IDs and are NOT committed. (5) effective (near-dup-collapsed) counts are a reserved seam (reidx-04); v1 uses raw counts.

---

## S3 — Scorers (DONE 2026-05-29)

Closes the M6 centerpiece: all four privacy directions now have **running scorers** (not precomputed signals). 8 stories, strict TDD, every story gate + the sprint gate APPROVE. Story contracts in `02-stories/sprint-3/`; gate evidence in `_reviews/story/S3-*/` + `_reviews/sprint/S3/`.

| Story | Module(s) | Closes |
|---|---|---|
| S3-01 | `scoring/adversary/{base,__init__}.py`, `scoring/signals.py` (ported pure) | FR-010 port; `assemble_paired_set` (the 2,500 paired personas are ASSEMBLED from the tier3 substrate — no paired file existed) |
| S3-02 | `scoring/adversary/offline_adversary.py` | FR-007/010 — the deterministic OFFLINE adversary (RRS headline, reidx-01) + distractor variant |
| S3-03 | `scoring/adversary/llm_adversary.py` | FR-010 — LLM secondary, `deterministic=False`, behind `[llm]` extra (lazy import; pkg imports without anthropic) |
| S3-04 | `scoring/reidentification.py` (+`MeasuredRRS`) | FR-007/009 — measured RRS = 1−recall×precision, Wilson CIs on integer counts, non-strippable caveat |
| S3-05 | `scoring/reidentification.py` (+exposure index) | FR-008 — deterministic exposure-index PRIOR (explicitly NOT RRS) + index↔RRS Pearson/Spearman correlation |
| S3-06 | `scoring/anonymization.py` | FR-006/NFR-005 — privacy-utility `ParetoPoint`, structurally unmergeable (no `__float__`/combined field) |
| S3-07 | `scoring/pseudonymization.py` | FR-011/012/013 — **the moat**: enumerated threat model, intended-vs-crypto collision separation (never summed), referential integrity, key rotation, EDPB Art 4(5) key/state separation |
| S3-08 | `stats/power.py` (+reid ladder) | NFR-018/NFR-005 — reid-operating-point power seam (`reid_required_n` 897/385, `ReidProvenance`) + the 4-way cross-module no-merge audit |

### S3 — verification + guardrails
- **Tests:** 159,891-record corpus untouched; `python3 -m pytest` → **169 passed, 1 skipped** (the `anthropic`-absent contract skip), **0 regressions** from the S-PWR baseline. Coverage **93% aggregate** line on scoring+stats; every new scorer module ≥85% (NFR-016).
- **S-PWR guardrail HELD:** `eval_lattice.json` (730 cells) untouched (last touched at `47c3a8f`); tags `v1.3.0` + `pre-lattice-enrichment` intact; **no corpus regeneration**; the reid ladder is a parallel CODE seam, not a lattice rebuild.
- **Axioms:** AX-001 synthetic-only · AX-002 determinism (offline headline byte-reproducible; LLM flagged non-deterministic) · AX-003 named-method CIs on integer counts · AX-004/NFR-005 anon/pseudo/RRS/detection never merged (mutation-tested, 4 fusion vectors rejected). Non-strippable caveats structural: RRS anti-anonymity, exposure-"NOT RRS", EDPB Art 4(5), Pareto separation.
- **Sprint-gate amendment `bea79ba`:** lifted `anonymization.py` 72%→97% (NFR-016 per-module) + fixed 2 advisory perf findings (pseudonymization `_referential_integrity` O(n²)→O(n); offline-adversary target-signal hoist out of the |C| loop) — behavior-preserving.
- **Honest status:** `provisional_status: AGENT_SIMULATED` (no DIVERGED DC). The execution-environment **real-CI Pass-2** is owed before any S3 MUST counts RELEASE-verified.
- **Deferred:** the pre-existing lint baseline (power.py UP035/E702/type-arg; reidentification.py UP037/type-arg; scoring/__init__ I001) → a Stage-5 lint-hardening pass.

### Git (branch `feat/v2-scoring-harness`)
S3 commits interleave `[RED]/[GREEN]/[REFACTOR]` per story (SHAs in each story's §12 + `_reviews/`) with `docs(pdlc)` bookkeeping commits; `bea79ba` sprint-gate amendment.

---

## S4 — Stats/reporting completion (DONE 2026-05-29)

DC-09 completed. 5 stories, strict TDD, every story gate + the S4 sprint gate APPROVE. Pure-stdlib stats/reporting core; matplotlib behind a new `[viz]` extra (lazy). Signoff `SO-03-s4`.

| Story | Module | Closes |
|---|---|---|
| S4-01 | `stats/intervals.py` (+`clopper_pearson_interval` + stdlib inverse-beta) | FR-004, NFR-002 |
| S4-02 | `stats/paired.py` (McNemar exact/χ² + seeded paired bootstrap) | FR-002 (measure), NFR-002 |
| S4-03 | `stats/calibration.py` (ECE/Brier/reliability per entity class) | FR-005, NFR-008 |
| S4-04 | `reporting/language_power.py` (per-language + language×type power table) | NFR-003 |
| S4-05 | `reporting/viz.py` (reliability/Pareto/heatmap/Sankey/coverage-risk) + `[viz]` extra | FR-005, NFR-003, FR-006 |

### S4 — verification + notes
- **Tests:** `pytest` → **211 passed, 1 skipped** (the `anthropic`-absent contract skip), 0 regressions. **Every stats+reporting module ≥85% line** (power_table 100%, intervals 87%, calibration 96%, paired 92%, viz 96%, language_power 97%); sprint coverage-hardening `243ba63` lifted power_table.py 74%→100% (DC-09 reporting completion) + fixed the `fr_005` token.
- **FR-005 COMPLETE** across S4-03 (ECE/Brier/reliability) + S4-05 (reliability diagram + abstention coverage-risk curve — the facet flagged open at the S4-03 gate).
- **NFR-008 honesty:** ECE≤0.05 is a REFERENCE reported via `meets_reference`, NEVER a submitter gate (a high-ECE input returns normally). **NFR-002:** every CI carries a named method (Wilson/Clopper-Pearson/paired-bootstrap/McNemar). **NFR-004:** matplotlib lazy behind `[viz]`; `import reporting` succeeds without it.
- **S4-04 recovery:** the executor was interrupted at a long-run boundary mid-cycle (RED+GREEN committed, tests passing); the orchestrator finished the REFACTOR (`b4e0335`, annotation-only mypy fix) + the REVIEW transition. No work lost.
- **S-PWR guardrail HELD:** `eval_lattice.json` (730 cells) untouched; tags intact; reporters read NO corpus (take `(lattice, observed_counts)` as args).
- **Honest status:** `provisional_status: AGENT_SIMULATED` — real-CI Pass-2 owed at Stage 5.

## S5 — Exports/CLI (DC-12) + Compliance end-state bundle (DC-11) + Doc-drift (NFR-013) (DONE 2026-05-30)

7 stories, strict TDD, every story gate + the S5 sprint gate APPROVE. Signoff `SO-04-s5`. **FR-024 fully closed**; **NFR-012**, **FR-021**, **FR-022/gov-02**, **NFR-013** closed.

| Story | Module(s) | Closes |
|---|---|---|
| S5-01 | `compliance/crosswalk.py` (5 legally-distinct regime columns; HIPAA SH/ED) | FR-022 / gov-02 |
| S5-02 | `distribution/parquet_export.py` (streaming; N `reg_*` cols; fixes v1.3.0 blob-flatten) | FR-024, NFR-012 |
| S5-03 | `distribution/{croissant,dataset_card}.py` (Croissant 1.0 validate-AND-load; counts from metadata.json) | FR-024, **NFR-012** |
| S5-04 | `distribution/{conll_export,spacy_export}.py` + `integrations/conll_format.py` (CoNLL BIO/BILOU thin-wrap; spaCy DocBin lazy) | FR-024 |
| S5-05 | `cli.py` + `[project.scripts] pii-anon` (5 thin verbs; power gate ON; no business logic) | FR-024 (DX-03) — **FR-024 fully closed** |
| S5-06 | `compliance/end_state_bundle.py` (DPIA-input; anon/pseudo SEPARATE; non-strippable disclaimer) | **FR-021**, NFR-005 |
| S5-07 | README/DATASHEET/COMPARISON/TAXONOMY/MIGRATION/CHANGELOG/`__init__` + `tests/test_doc_drift.py` | **NFR-013** |

### S5 — verification + notes
- **Tests:** `pytest` → **290 passed, 1 skipped** (the `anthropic`-absent contract skip), 0 regressions. Proactive sprint coverage-hardening `35faf3a` lifted the 4 sub-85% modules (cli 71→93%, integrations/conll_format 78→98%, croissant 79→99%, parquet_export 81→99%) — **every new S5 module ≥85% line**; coverage source extended to compliance/distribution/reporting/integrations/cli. Also fixed the pre-existing `__init__.py` `list[dict]` type-arg.
- **NFR-012 (the literal threshold):** `validate_croissant()` is an always-on pure-stdlib schema-shape check; the described Parquet loads via HF `datasets` with the five `reg_*` columns intact (genuinely RAN — pyarrow + datasets present). Full `mlcroissant` spec-conformance is skip-if-absent → Pass-2 CI image.
- **gov-02 end-to-end:** crosswalk emits N legally-distinct typed regime columns (HIPAA split SH/ED) → Parquet writes them as N `reg_*` columns (no flattened blob) → Croissant recordSet declares them. No merged verdict.
- **FR-021 separation (NFR-005/AX-004):** `EndStateBundle` keeps anon (DC-06 Pareto) + pseudo (DC-08 integrity) evidence in SEPARATE keys — no merged field, no `__float__`, import-time structural assert; FR-009 + EDPB Art 4(5) caveats travel unstripped; non-strippable DPIA disclaimer.
- **CLI:** 5 thin dispatch verbs; `export`→distribution (lazy), `validate`/`generate`/`score`→trusted repo scripts via subprocess (fixed paths, no `shell=True`), `leaderboard`→graceful-until-S6. The `validate` verb NEVER injects `--no-power-gate` (NFR-018 gate stays ON, test-asserted); `generate` never targets the frozen corpus.
- **NFR-013 (doc-drift):** 7 docs at canonical 575,604 / 2,486,438 / 63 / 9 / 60 / 7 / v2.0.0; the `159,891 (100%)` reframed to the 27.8% Tier-3 eval substrate; the ~72%-enrichment + synthetic≠external-validity (§7 sentence) + train-vs-eval caveats surfaced; MIGRATION v1.3.0→v2.0.0 section; CHANGELOG S-PWR entry; TAXONOMY body = the 63 `ENTITY_REGISTRY` types. `tests/test_doc_drift.py` pins zero current-state drift; competitor figures only the two authorized deltas + a sourcing note; history preserved.
- **NFR-004 purity:** force-blocking pyarrow + mlcroissant + spacy + datasets at import → `distribution` + `cli` + `compliance` import OK; each lazy guard raises the correctly-named extra `RuntimeError`; per-module AST purity guards green for all 7 modules.
- **Guardrail HELD:** `eval_lattice.json` (730 cells) frozen at `47c3a8f` (`lattice --check` OK); corpus `.jsonl.gz` + `metadata.json` untouched; tags `v1.3.0` + `pre-lattice-enrichment` intact.
- **Honest status:** `provisional_status: AGENT_SIMULATED` — real-CI Pass-2 owed at Stage 5.

## S6 — Leaderboard & governance (DC-13) (DONE 2026-05-31)

5 stories, every story gate + the S6 sprint gate APPROVE. Signoff `SO-05-s6`. All pure-stdlib (json + hashlib; no hosted service in v1 — the governance seam). **FR-023/025/026 + NFR-014 verified.**

| Story | Module / doc | Closes |
|---|---|---|
| S6-01 | `leaderboard/store.py` (append-only hash-chained held-out store; gold never stored; `verify_chain`) | FR-023, NFR-014 |
| S6-02 | `leaderboard/policy.py` (opt-in publish + anti-gaming: rate-limit / rotation epoch / contamination) | FR-023, NFR-014 |
| S6-03 | `leaderboard/coi.py` (gov-03 CoIRecord: non-strippable no-pre-pub attestation + recusal) | FR-026, NFR-014 |
| S6-04 | `GOVERNANCE.md` (charter + aspirational/AGENT_SIMULATED roster + CoI naming pii-anon-core + bus-factor=1) | FR-026, NFR-014 |
| S6-05 | `CONTRIBUTING.md` (PR template + CC0 checklist + synthetic-only provenance + deprecation/erratum + semver) | FR-025 |

### S6 — verification + notes
- **Tests:** `pytest` → **325 passed, 1 skipped** (the `anthropic`-absent contract skip), 0 regressions. The leaderboard package was 99% line out of the gate (store 97%, policy/coi/__init__ 100%) — **no coverage-hardening needed**; coverage source extended to add `pii_anon_datasets.leaderboard`.
- **Held-out store (FR-023):** append-only, event-sourced (submitted/scored/published), sha256 content-hash chained (`prev_hash` links, `GENESIS_HASH` first); `verify_chain()` detects any line mutation (tamper-EVIDENT, honestly framed). Held-out GOLD is NEVER stored — `append` rejects {gold,gold_labels,held_out,held_out_labels,answers,ground_truth} before any write. Deterministic: seq-ordered, NO clock/RNG (no time/datetime).
- **Anti-gaming policy (NFR-014):** opt-in publish (a disallowed submission is never published) + rate-limit (per submitter per epoch) + held-out rotation epoch (stale-epoch rejected) + contamination/duplicate — each a distinct reason; read-only over the store.
- **gov-03 recusal (FR-026):** `CoIRecord` carries a non-strippable `NO_PREPUB_ATTESTATION` (empty rejected) + `requires_recusal` True for maintainer / any pii-anon-core affiliation (lower+strip+substring, evasion-resistant); `as_dict()` rides in a `submitted` event.
- **Epistemic honesty (S6-04):** GOVERNANCE.md flags the advisory roster ASPIRATIONAL / AGENT_SIMULATED (no fabricated members) + states bus-factor=1 plainly; every CoI/neutrality claim maps to real code. The two governance docs (S6-04/05) were authored directly (orchestrator RED→GREEN, a property test pins each) + reviewed jointly in one combined 5-reviewer gate (`_reviews/story/S6-04-05/`).
- **Performance (advisory):** the store's O(N²)-over-appends + policy's O(N)-per-eval are single-digit-ms at the intended tens/hundreds-submission seam scale; an indexed/append-without-reread hosted leaderboard is a v1.x hardening.
- **Guardrail HELD:** `eval_lattice.json` (730 cells) frozen at `47c3a8f`; corpus `.jsonl.gz` + `metadata.json` + `MANIFEST.sha256` untouched; tags `v1.3.0` + `pre-lattice-enrichment` intact; NFR-013 doc-drift still 0.
- **Honest status:** `provisional_status: AGENT_SIMULATED` — real-CI Pass-2 owed at Stage 5.

## S7 — Extension seams (DC-10/14/01, v1.1) (DONE 2026-05-31) — closes Development

5 stories, every story gate + the S7 sprint gate APPROVE. Signoff `SO-06-s7`. All pure-stdlib v1.1 seams with non-strippable scope-honesty guards. **FR-017 fully covered**; FR-027 + FR-015/016 v1 SEAMS verified (real-data correlation + full coref/qid scoring = Pass-2); FR-018/019/020 ROADMAP.

| Story | Module / doc | Closes |
|---|---|---|
| S7-01 | `scoring/adversary/oracle.py` (PII-recognition oracle; "never agent-leakage scoring") | FR-017 |
| S7-02 | `scoring/adversary/payloads.py` (INERT injection payloads; base64/ocr/zero-width faithful transforms) | FR-017 |
| S7-03 | `validation/correlation.py` (Kendall/Spearman bootstrap + Bland-Altman; `RealDataAbsent` never-fabricate sentinel) | FR-027 (SEAM) |
| S7-04 | `subsets/slices.py` (coreference + quasi-id loaders; ~72%-formulaic v1.1 low-power caveat) | FR-015/016 (SEAM) |
| S7-05 | `ROADMAP.md` (FR-018/019/020 documented as v1.x, NOT shipped) | FR-018/019/020 roadmap |

### S7 — verification + notes
- **Tests:** `pytest` → **346 passed, 1 skipped**, 0 regressions. Every new S7 module ≥85% line (oracle 94%, payloads 98%, slices 97%, correlation 94%) out of the gate — **no coverage-hardening needed**; coverage source extended (`+validation`, `+subsets`); overall TOTAL 94%.
- **FR-017 FULLY covered** (oracle + payloads). The "never marketed as agent-leakage scoring" scope guard is type-enforced + stress-verified non-droppable; the payloads are INERT synthetic fixtures (3 committed FAITHFUL transforms base64/ocr/zero-width; benign carriers; no weaponized content).
- **FR-027 never-fabricate (S7-03):** `correlate()` returns a `RealDataAbsent` sentinel when real i2b2/TAB data is absent — the short-circuit precedes any result construction (non-bypassable); the synthetic→real transfer delta is the binding Stage-5 Pass-2 item. Bootstrap is seed-deterministic via a LOCAL `random.Random(seed)` (mirrors `stats/paired.py`).
- **FR-015/016 (S7-04):** coreference + quasi-id slice loaders ship with a non-strippable ~72%-formulaic v1.1 low-power caveat; the full scoring is v1.1/Pass-2.
- **Parallel execution:** S7-03 + S7-04 executors ran concurrently on disjoint dirs (validation/ vs subsets/) — interleaved commits, no conflict; both deferred the pyproject coverage-source edit to this close (landed).
- **Guardrail HELD:** the full S7 diff is NEW/additive only; corpus / `eval_lattice.json` (frozen at `47c3a8f`) / tags untouched; NFR-013 doc-drift still 0.
- **Honest status:** `provisional_status: AGENT_SIMULATED` — real-CI + real-data Pass-2 owed at Stage 5.

---

## Development stage COMPLETE (2026-05-31)

All 8 development sprints DONE (S1 foundations · S2 v2.0.0 migration · S-PWR statistical power · S3 scorer trio (M6 closed) · S4 stats/reporting · S5 exports/CLI + compliance + doc-drift · S6 leaderboard + governance · S7 extension seams). **346 tests / 1 skip**; every scoring+stats+reporting+compliance+distribution+leaderboard+validation+subsets module ≥85% line. All story + sprint gates APPROVE; signoffs SO-01-spwr … SO-06-s7. Frozen-corpus guardrails held throughout (`eval_lattice.json` 730 cells @ `47c3a8f`; tags `v1.3.0` + `pre-lattice-enrichment`). **Handoff to Stage 5 Testing:** all work `AGENT_SIMULATED`; the Pass-2 roster (FR-027 synthetic→real transfer; FR-015/016 full scoring; design never real-user-trialed [R10 10-persona simulated]; ~72% formulaic-template monoculture) carries forward as non-strippable caveats. Expected release verdict: **SHIP-WITH-CAVEATS**.
