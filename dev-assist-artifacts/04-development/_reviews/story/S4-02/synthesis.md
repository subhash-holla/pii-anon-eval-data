# Story Gate Synthesis — S4-02 (Paired stats: McNemar + paired bootstrap)

**Gate:** story · **Scope:** S4-02 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-29

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 0 |
| traceability | ✅ APPROVE | 2 OBS |
| requirements-coverage | ✅ APPROVE | 2 OBS (paired.py 92%, clears bar) |
| security-sast | ✅ APPROVE | 1 OBS (n_boot unbounded; non-DoS at trust scope) |
| axiom-compliance | ✅ APPROVE | 0 |

**Aggregate: APPROVE** (zero MAJOR+).

## Joint signals

- **Math honesty recomputed** (requirements-coverage + axiom, from first principles): `mcnemar_exact(10,0)` p=0.001953125, `mcnemar_chi2(20,10)` χ²=2.7 p=0.10034824…(=erfc(√1.35)), `mcnemar_exact(5,5)`=1.0, b+c==0→(0,1), odds_ratio=b/c|None. Exact.
- **AX-002 determinism proven 3 ways** (axiom + code-quality + security-sast): local `random.Random(seed)` (only `rng.randrange`); AST guard (no global-random, no time/uuid/datetime/secrets); runtime invariance under caller `random.seed(0/999999)` → global RNG provably never consulted. McNemar RNG-free.
- **Two-gate distinction respected**: this is the FR-002 detector-regression measurement gate, decoupled from the NFR-018 corpus-power gate (no lattice/wilson/clopper coupling).
- **Executor fixture-widening (8→50 pairs)** independently confirmed a test-robustness fix (8-pair percentile aliased across seeds), not a production patch.

## Findings forwarded (non-blocking)

- traceability OBS: FR-002 canonical title is "Deterministic CI regression gate"; the design's two-gate split (`sampling-design.md` §3.2) assigns the paired-McNemar A/B gate to FR-002 — not a misclaim, recorded for readers.
- requirements-coverage OBS: empty-pairs branch (`paired.py:134`) spec'd but untested (non-acceptance defensive line) — fold into the S4 sprint coverage-hardening micro-commit.
- security-sast OBS: `n_boot`/`len(pairs)` unbounded — non-DoS (no `while`, sane default, trusted in-process caller); add an input-size guard only if exposed behind a public/remote surface.

## Outcome

S4-02 → **DONE**. Paired McNemar + bootstrap ship (FR-002 measurement; NFR-002 named). Evidence: RED `5568608` → GREEN `1e34f7b` → REFACTOR `d5cafe7` → docs `33b1886`; 184 passed / 1 skipped (0 regressions); pure-stdlib; deterministic; frozen lattice/corpus/tags untouched.
