# Story Gate Synthesis — S4-01 (Clopper-Pearson exact interval)

**Gate:** story · **Scope:** S4-01 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-29

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 2 OBS (pre-existing S1 nits) |
| traceability | ✅ APPROVE | 0 |
| requirements-coverage | ✅ APPROVE | 2 MINOR (intervals.py 83%<85%; coverage-mode unnamed) |
| security-sast | ✅ APPROVE | 1 OBS (no confidence-range guard, symmetric w/ Wilson) |
| axiom-compliance | ✅ APPROVE | 0 |

**Aggregate: APPROVE** (zero MAJOR+).

## Joint signals

- **Math honesty verified** (axiom + requirements-coverage, independently recomputed): textbook 95% values match to 4 d.p. (max Δ 2.9e-5); axiom-compliance cross-checked against `scipy.stats.beta.ppf` (a non-repo oracle in shell) → agree <1e-5; **CP ⊇ Wilson** conservatism holds on every cell. Not curve-fit.
- **Deterministic + DoS-free** (security-sast + axiom): pure `math`, fixed iteration bounds (`_betacf` ≤200, `_inv_betainc` 60 bisection, no `while`); byte-identical cross-process under varying PYTHONHASHSEED; no `log(0)` at edges.
- **Wilson preserved + reidx-02 strengthened**: guard factored into `_require_int_counts`, now rejects bool `n` too (closes a latent Wilson hole); Wilson tests 6/6 byte-identical.

## Findings forwarded (non-blocking)

- **requirements-coverage MINOR (tracked):** `intervals.py` 83% line < 85% per-module bar. Deficit = pre-existing S1 lines (`_z` Winitzki branch, wilson n=0 sentinel) + unreachable inverse-beta defensive guards; the S4-01 CP behavior is fully exercised. **→ S4 sprint-gate coverage-hardening micro-commit** (add wilson-n=0 + `_z`-uncommon-confidence + inverse-beta-symmetry-branch micro-tests).
- security-sast OBS: no `confidence`-range guard (symmetric with Wilson; non-security) → robustness item.
- code-quality OBS: pre-existing `as_dict -> dict` + `type: ignore` unused (project-wide, no `py.typed`).

## Outcome

S4-01 → **DONE**. Clopper-Pearson exact CI ships (FR-004 second method; NFR-002 named). Evidence: RED `8939c46` → GREEN `acac5a8` → REFACTOR `c4dc62c` → docs `4b8d0e3`; 176 passed / 1 skipped (0 regressions); pure-stdlib; deterministic; frozen lattice/corpus/tags untouched.
