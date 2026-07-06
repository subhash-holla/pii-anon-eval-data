# Story Gate Synthesis — S3-04 (Measured-attack RRS scorer)

**Gate:** story · **Scope:** S3-04 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-29

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 4 OBSERVATION (2 = pre-existing S1 nits, out of scope) |
| traceability | ✅ APPROVE | 1 OBSERVATION |
| requirements-coverage | ✅ APPROVE | 1 MINOR (cross-module regression → sprint gate) + 1 OBS |
| security-sast `[AUDIT]` | ✅ APPROVE | 0 |
| axiom-compliance | ✅ APPROVE | 0 |

**Aggregate: APPROVE** (zero MAJOR+).

## Joint signals (high confidence)

- **FR-009 caveat non-strippable — proven at 4 layers** (security-sast): single serializer unconditionally nests `rrs.as_dict()`; `RRSResult.as_dict()` always emits `caveat`; field mandatory+non-defaulted+frozen; the `[AUDIT]` test asserts the caveat *content* (`"MUST NOT be cited"`) survives nesting.
- **FR-007 genuinely MEASURED, not precomputed** (requirements-coverage + axiom): `score_reidentification` runs `adversary.attack()` live; `correct` from `guessed_persona_id == target_id`; no precomputed RRS field read.
- **S1 frozen `RRSResult` byte-intact** (axiom, by diff: 1836==1836 chars; `__all__` grew with zero drops); AX-003 (Wilson CIs, named method, integer counts, reidx-02 guard incl. bool-rejection), AX-004/NFR-005 (re-id-family-only, no de-id merge) upheld.

## Findings waived / forwarded

- code-quality OBS (2): `reidentification.py:58` UP037 + `:69` bare-dict are **pre-existing S1** inside the frozen `RRSResult` — left untouched per the frozen-contract rule. **Route as a separate S1-lint-hardening change** if desired.
- requirements-coverage MINOR: full-suite 0-regression (executor ran 133 passed) is re-verified at the **sprint gate** Tier snapshot.

## Outcome

S3-04 → **DONE**. The M6-closing headline metric (measured RRS with Wilson CIs, |C|, version-pinned adversary, non-strippable caveat) ships. Unblocks S3-05 (exposure correlation), S3-06 (anon residual-risk axis), S3-08 (ReidProvenance). Evidence: RED `f33b3e5` → GREEN `bfa5cf9` → REFACTOR `379f086`; 133 tests pass (0 regressions); ruff+mypy clean on added lines; pure-stdlib; frozen lattice/corpus/tags untouched.
