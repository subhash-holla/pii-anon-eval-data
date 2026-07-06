# Combined Story Gate Synthesis — S7-03 (correlation harness) + S7-04 (corpus slices)

**Gate:** story (combined — two independent v1.1 seam stories executed in parallel) · **Scope:** S7-03 +
S7-04 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-31

> **Why combined:** S7-03 (`validation/correlation.py`, FR-027) and S7-04 (`subsets/slices.py`,
> FR-015/016) are independent extension seams on disjoint dirs; their executors ran concurrently
> (interleaved RED/GREEN/REFACTOR commits, no file conflict). Reviewed in one 5-reviewer gate; per-story FR
> mapping + commit evidence preserved.

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 2 OBS (no docstring examples; absolute-import style — both valid) |
| axiom-compliance | ✅ APPROVE | 0 (load-bearing — never-fabricate sentinel + low-power caveat verified) |
| requirements-coverage | ✅ APPROVE | 2 OBS (pyproject coverage-source deferred → sprint close; seam-vs-feature framing) |
| traceability | ✅ APPROVE | 1 MINOR + 1 OBS (deferred coverage edit; matrix annotation) |
| security-sast | ✅ APPROVE | 0 (pure-stdlib; no egress/secrets; never-fabricate is non-bypassable) |

**Aggregate: APPROVE** (zero SHOWSTOPPER / CATASTROPHIC / MAJOR).

## Joint signals

- **FR-027 NEVER FABRICATE (the S7-03 crux)** — axiom-compliance + security-sast verified `correlate(...,
  None)` AND `correlate(..., [])` both return `RealDataAbsent` (available=False), never a
  `CorrelationResult`; the short-circuit precedes any result construction (non-bypassable); a lone present
  score refuses via the `>=2` ValueError rather than fabricating. The note + caveat are non-strippable
  (`__post_init__` ValueError on empty) and name "NOT external validity" + FR-027. The bootstrap is
  seed-deterministic via a LOCAL `random.Random(seed)` (AST-guarded — no module-global RNG; bans
  {time,uuid,datetime,secrets}; mirrors `stats/paired.py`); concordant→+1, discordant→-1.
- **FR-015/016 low-power caveat (the S7-04 crux)** — `SLICE_CAVEAT` is non-strippable (empty → ValueError)
  and states "72%" + v1.1 + LIMITED + external-validity, honest about the formulaic synthetic monoculture;
  the filters are correct (coreference = non-empty chains; quasi-id = ≥ min_qids, configurable),
  order-preserving, pure-stdlib.
- **Quality** — both modules ruff + mypy --strict clean; 9/9 targeted tests pass; full suite 344 passed /
  1 skipped (0 regressions); each diff scoped to its §8 owned files (neither touched the other's dir; the
  optional pyproject coverage-source edit correctly DEFERRED).

## Findings forwarded (S7 sprint-close actions)

- **requirements-coverage + traceability (the actionable one)**: the OPTIONAL `[tool.coverage.run] source`
  += `pii_anon_datasets.validation` + `pii_anon_datasets.subsets` was deferred from both stories (to avoid
  a concurrent-edit conflict) — **land it at the S7 sprint-close coverage step** so the two new packages
  are measured.
- **requirements-coverage (framing)**: FR-027 / FR-015 / FR-016 are SHOULD / v1.1 / PERSONA-CONDITIONAL —
  S7-03/04 deliver the v1 SEAM (harness/loaders + honesty guards); the real-data correlation + the actual
  coreference/qid SCORING are v1.1/Pass-2, carried on the Stage-5 release-gate Pass-2 roster. Seam-level
  verified, not full-feature closed.

## Outcome

S7-03 + S7-04 → **DONE**. The real-data validation correlation harness ships with a non-bypassable
never-fabricate `RealDataAbsent` sentinel (FR-027), seed-deterministic Kendall-τ/Spearman bootstrap +
Bland-Altman, and a "synthetic ≠ external validity" caveat; the coreference + quasi-identifier slice
loaders ship with the non-strippable ~72%-formulaic v1.1 low-power caveat (FR-015/016). Evidence: S7-03 RED
`3525a5d` → GREEN `a17726d` → REFACTOR `4d8611f`; S7-04 RED `bbcf838` → GREEN `cc496b0` → REFACTOR
`7200ee0`; **344 passed / 1 skipped** (335 prior + 5 + 4, 0 regressions); ruff + mypy --strict clean;
corpus / lattice / tags untouched; pyproject coverage-source edit deferred to the S7 close.
