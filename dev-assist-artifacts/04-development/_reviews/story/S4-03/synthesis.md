# Story Gate Synthesis — S4-03 (Calibration: ECE + Brier + reliability bins)

**Gate:** story · **Scope:** S4-03 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-29

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 0 |
| traceability | ✅ APPROVE | 1 OBS (FR-005 abstention-curve facet not claimed) |
| requirements-coverage | ✅ APPROVE | 2 OBS (calibration.py 97.8%; abstention facet + Pass-2) |
| security-sast | ✅ APPROVE | 0 |
| axiom-compliance | ✅ APPROVE | 0 |

**Aggregate: APPROVE** (zero MAJOR+).

## Joint signals

- **Math recomputed independently** (requirements-coverage + axiom, from scratch): ECE 0.29375, Brier 0.2171875, perfect→0.0, per-class PERSON 0.0/EMAIL 0.9 — exact to 1e-12; equal-width binning convention pinned + reproducible; reliability bins partition [0,1], sum to n.
- **NFR-008 honesty verified** (axiom + traceability + requirements-coverage): `meets_reference` is a reported `@property`; the ONLY raise is length-mismatch `ValueError`; a high-ECE input (0.29375) and a badly-calibrated EMAIL class (0.9) both return normally → the benchmark cannot covertly gate submitters on calibration (NFR-008 "reported, not pass/fail").
- **Pure-stdlib** (`statistics` only — not even `math`); no RNG/clock/IO; `cast()` typing changes are runtime no-ops (verified).

## Findings forwarded (non-blocking)

- **traceability + requirements-coverage OBS (tracked):** FR-005 also names an **"abstention coverage-risk curve"** — S4-03 honestly scopes only ECE+Brier+reliability (a legitimate partial). **→ fold the abstention/selective-prediction curve into S4-05 (viz)** so FR-005 is fully covered; flag at the S4 sprint gate.
- requirements-coverage OBS: Pass-2 real-CI before NFR-008 counts release-verified.
- axiom note: `n_bins<=0` raises an unrelated error not `ValueError` — minor robustness, non-blocking.

## Outcome

S4-03 → **DONE**. Calibration (ECE/Brier/reliability, per entity class) ships (FR-005 partial; NFR-008 reference reported). Evidence: RED `6f13d97` → GREEN `483af11` → REFACTOR `a6c1cf6` → docs `147d210`; 192 passed / 1 skipped (0 regressions); pure-stdlib; deterministic; frozen lattice/corpus/tags untouched.
