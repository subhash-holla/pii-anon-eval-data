# Sprint Gate Synthesis — S5 (Exports/CLI + Compliance + Doc-drift; DC-11/DC-12 + NFR-013)

**Gate:** sprint · **Scope:** S5 (7 stories) · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-30

| Reviewer | Verdict | Findings |
|---|---|---|
| requirements-coverage | ✅ APPROVE | 2 OBS (mlcroissant full-spec conformance + real-CI Pass-2 deferred) |
| performance-benchmark | ✅ APPROVE | 3 OBS (real-runtime → Stage-5 NFR-010; spaCy DocBin serialize-at-end; `_assign_bio_tags` empirically linear) |
| axiom-compliance | ✅ APPROVE | 0 blocking (separation + lazy + no-egress + guardrails all empirically verified) |
| code-quality · traceability · security-sast | ✅ carried forward | APPROVE on all 5 S5 story gates (S5-03..07; S5-01/02 prior session) — unanimous |

**Aggregate: APPROVE** (zero MAJOR+). The proactive coverage-hardening (`35faf3a` — cli 71→93%,
conll_format 78→98%, croissant 79→99%, parquet_export 81→99%) **preempted** the per-module-coverage MAJOR
that bit S3+S4; coverage source extended to compliance/distribution/reporting/integrations/cli.

## Story roster (7/7 DONE, every story gate APPROVE 5/5)

| Story | Module(s) | Closes | Notes |
|---|---|---|---|
| S5-01 | `compliance/crosswalk.py` | FR-022 / gov-02 | 5 legally-distinct regime columns; HIPAA split SH/ED; no merged verdict (prior session) |
| S5-02 | `distribution/parquet_export.py` | FR-024, NFR-012 | streaming Parquet; N typed `reg_*` cols; fixes the v1.3.0 blob-flatten (prior session) |
| S5-03 | `distribution/{croissant,dataset_card}.py` | FR-024, **NFR-012** | Croissant 1.0 JSON-LD validate-AND-load (HF `datasets` round-trip, reg_* intact); card counts from metadata.json (cannot drift) |
| S5-04 | `distribution/{conll_export,spacy_export}.py` + `integrations/conll_format.py` | FR-024 | CoNLL BIO/BILOU thin-wrap (streaming, pure-stdlib); spaCy offsets + DocBin (lazy `[baselines]`) |
| S5-05 | `cli.py` + `[project.scripts]` | FR-024 (DX-03) | 5 thin verbs; no business logic; NFR-018 power gate kept ON; **FR-024 fully closed** |
| S5-06 | `compliance/end_state_bundle.py` | **FR-021**, NFR-005 | DPIA-input bundle; anon/pseudo kept SEPARATE; FR-009 + EDPB Art 4(5) caveats travel |
| S5-07 | 7 docs + `tests/test_doc_drift.py` | **NFR-013** | 7 docs canonical (575,604/2,486,438/63/v2.0.0); zero current-state drift; caveats surfaced |

## MUST-coverage snapshot (sprint)

All S5 requirements VERIFIED with named tests, 0 orphans: **FR-022** (gov-02 — 5 legally-distinct regime
columns, no merge), **FR-024** (**fully closed** — Parquet + Croissant + dataset card + spaCy + CoNLL +
CLI + JSONL), **NFR-012** (Croissant validate-AND-load + Parquet loadability — both genuinely RAN via HF
`datasets`), **FR-021** (DPIA-input bundle — anon/pseudo separate, non-strippable disclaimer), **NFR-013**
(documentation drift — 7 docs canonical, `tests/test_doc_drift.py` pins zero current-state drift). The
traceability-matrix Status Change Log records the verified-by-story mapping (all AGENT_SIMULATED — real-CI
Pass-2 owed). Full suite **290 passed / 1 skipped**; every new S5 module ≥85% line coverage.

## Cross-cutting verification

- **AX-004 / NFR-005 (separation)** HELD across compliance + distribution: `EndStateBundle` keeps
  anon/pseudo evidence in separate keys (no merged field, no `__float__`, import-time structural assert);
  `crosswalk` emits N legally-distinct regime columns; `parquet_export` drops the `regulatory_domains`
  blob for N typed `reg_*` columns. No fusion symbol anywhere.
- **NFR-004 (pure-stdlib core + lazy heavy deps)** HELD: `import distribution` / `import cli` /
  `import compliance` succeed with pyarrow + mlcroissant + spacy + datasets ALL force-blocked; each lazy
  guard raises the correctly-named extra `RuntimeError`; per-module AST purity guards green for all 7 modules.
- **AX-001 (synthetic-only, no egress)**: exporters/CLI write LOCAL files only; no network egress, no HF
  auto-upload; the CLI subprocess uses fixed trusted repo-script paths (no `shell=True`).
- **AX-002 (determinism)**: exporters/crosswalk/bundle/croissant/card are deterministic (sorted/ordered;
  no clock/RNG).
- **Streaming / bounded memory** (performance): every exporter is one-pass (no `list(records)`/`len`);
  the 575K Parquet stream is batched (the v1.3.0 full-materialization bug fixed).
- **Guardrails**: corpus `.jsonl.gz` / `eval_lattice.json` / `metadata.json` / tags (`v1.3.0`,
  `pre-lattice-enrichment`) UNTOUCHED across S5; the CLI `validate` verb keeps the NFR-018 power gate ON
  (test-asserted — never injects `--no-power-gate`).

## Forwarded to Stage 5 / Pass-2

- mlcroissant full-spec conformance (skip-if-absent now) → Pass-2 CI image with `[croissant]`.
- Real-runtime throughput of the 575K Parquet stream + spaCy DocBin build → Stage-5 NFR-010 (real_user_needed).
- All S5 closures are AGENT_SIMULATED → real-CI Pass-2 re-run is the source of truth.

## Outcome

Sprint S5 → **APPROVE / DONE**. Distribution (DC-12) + Compliance (DC-11) + doc-drift (NFR-013) ship:
FR-024 fully closed; NFR-012 closed; FR-021 closed; FR-022/gov-02 closed; NFR-013 closed. Proceed to
`/dev-assist-signoff SO-04-s5`.
