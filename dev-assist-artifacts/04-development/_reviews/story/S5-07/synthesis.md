# Story Gate Synthesis — S5-07 (Documentation-drift remediation; NFR-013)

**Gate:** story · **Scope:** S5-07 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-30

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 1 OBS (pre-existing `__init__.py:61` `list[dict]` type-arg → S5 sprint-close micro-commit) |
| requirements-coverage | ✅ APPROVE | 2 (1 MINOR README:351 stale migration-range, 1 OBS README:348 benchmark count — both fixed at close) |
| traceability | ✅ APPROVE | 2 OBS (metadata path shorthand; add NFR-013-verified-by-S5-07 to traceability-matrix at sprint close) |
| axiom-compliance | ✅ APPROVE | 1 OBS (benign historical `65` in a changelog entry) |
| security-sast | ✅ APPROVE | 0 (no real PII / secrets added; doc-test is read-only/inert) |

**Aggregate: APPROVE** (zero SHOWSTOPPER / CATASTROPHIC / MAJOR). **NFR-013 closed** for the
documentation-prose arm (the Croissant arm is NFR-012, closed at S5-03).

## Joint signals

- **Zero current-state drift VERIFIED** (requirements-coverage + traceability + axiom-compliance, all
  independently re-grepped, not trusting the self-report): 575,604 / 2,486,438 / 63 / v2.0.0 are identical
  across README / DATASHEET / COMPARISON / TAXONOMY / `__init__`; ZERO residual hits for
  `117,752 / 919,000 / 150K / 160K / ~1.24M / 65-types / 57-types / 159,891 (100%)` in current-state
  contexts. The 6 `nfr_013` tests pass; full suite 263 passed / 1 skipped (+6, 0 regressions).
- **M1 single-source-of-truth**: `tests/test_doc_drift.py` derives the entity count from
  `taxonomy.ENTITY_TYPE_COUNT` (== 63 at runtime), never a hardcoded literal in an assertion.
- **Epistemic honesty surfaced** (axiom-compliance, the crux): the ~72% `synthetic_lattice_enrichment`
  disclosure, the "synthetic-distribution power is not external validity" §7 sentence (verbatim), and the
  159,891 = ~27.8% Tier-3 eval substrate (NOT "100%") all appear across README/DATASHEET/MIGRATION/CHANGELOG.
- **No fabrication / history preserved**: only the two authorized competitor deltas (Nemotron 200K→~100K,
  AI4Privacy 580K→~220K) + a sourcing note + the PII-Bench/PIIBench disambiguation; SPY/PIILO byte-identical.
  CHANGELOG diff is ADD-ONLY (all v1.x entries untouched); MIGRATION's v1.0→v1.1 guide preserved, the
  v1.3.0→v2.0.0 section ADDED. Guardrails: corpus / `eval_lattice.json` / `metadata.json` / tags untouched.

## Findings resolved at close

- **README:348** "10 competing benchmarks" → "against major competing benchmarks" (removed the brittle
  count). **README:351** "v1.0.0 to v1.1.0 migration guide" → "version migration guide (v1.0.0 → v1.1.0
  and v1.3.0 → v2.0.0)" (MIGRATION now covers v2.0.0). Doc-drift suite re-run GREEN after the edits.

## Findings forwarded (sprint-close actions)

- **code-quality (OBS)**: the pre-existing `src/pii_anon_datasets/__init__.py:61` `-> list[dict]` `[type-arg]`
  (present at baseline `703c3e3`, out of S5-07's owned scope) → fix in the **S5 sprint-close
  coverage-hardening micro-commit**.
- **traceability (OBS)**: at the sprint close, add to `traceability-matrix.md` the queued **FR-021 → S5-06**
  row AND an **NFR-013 verified-by S5-07** annotation.

## Outcome

S5-07 → **DONE**. All 7 docs are at canonical 575,604 / 2,486,438 / 63 / 9 / 60 / 7 / v2.0.0; the
`159,891 (100%)` reframed to the 27.8% Tier-3 eval substrate; the train-vs-eval + ~72%-enrichment + §7
power caveats surfaced; MIGRATION has the v1.3.0→v2.0.0 section; CHANGELOG has the S-PWR sub-entry;
TAXONOMY's body is exactly the 63 `ENTITY_REGISTRY` types (per-category 2/10/4/12/10/6/6/8/5);
`tests/test_doc_drift.py` pins it (RED→GREEN). **NFR-013 closed** (prose arm). Evidence: RED `58a4a15` →
GREEN `e8dbe77` → REFACTOR `6cdf4d0` → docs `a17a8d1` (+ close polish); **263 passed / 1 skipped** (0
regressions); corpus / lattice / metadata / `v1.3.0` + `pre-lattice-enrichment` tags untouched.
