# Story Gate Synthesis — S3-07 (Pseudonymization-integrity scorer, the moat / DC-08)

**Gate:** story · **Scope:** S3-07 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-29

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 1 MINOR + 2 OBS |
| traceability | ✅ APPROVE | 2 OBS |
| requirements-coverage | ✅ APPROVE | 2 OBS |
| security-sast `[AUDIT]` | ✅ APPROVE | 0 |
| axiom-compliance | ✅ APPROVE | 0 |

**Aggregate: APPROVE** (zero MAJOR+). The moat ships clean.

## Joint signals (high confidence — the moat's correctness)

- **FR-012 collision separation is structural** (security-sast + requirements-coverage + axiom): two independent `int` fields, never summed; no `total_collisions`/`combined` field or `as_dict` key; a correct deterministic pseudonymizer → `unintended_crypto_collisions==0` (never penalized).
- **FR-013 EDPB Art 4(5) finding is FAITHFUL, not flattering** (axiom + security-sast): `_keyless_rejoinable` flags the bare-md5 no-secret artifact as self-rejoinable (`True` = fails separation), expresses it in a non-empty note citing Art 4(5), and the cited offender is **real** — axiom-compliance confirmed `scripts/enrich_context_preservation.py::PseudonymGenerator._hash_to_index:91` is literally `int(md5(value).hexdigest(),16) % max_idx` (keyless, secret-less) = exactly the `_BareMd5` shape.
- **md5 disambiguation** (security-sast): md5 is the auditor's *detection probe* over a closed candidate set, never a defense protecting a secret — correctly not flagged as weak-crypto.
- **NFR-005/AX-004**: pseudonymization is its own module; no anon-utility/residual-risk/combined/deid field, and it doesn't import the anon machinery — structural separation.

## Findings waived

- code-quality MINOR (`ThreatModel.has` missing docstring): cosmetic, non-blocking. **Waived.**
- traceability OBS: NFR-004 tested but not listed in §3; matrix is UC-level by design. **Noted** for sprint gate.
- requirements-coverage OBS: unauthorized-reversal is closed-world (documented Deviation #3); broader auxiliary-data attack is a post-MVP extension. **Accepted.**

## Outcome

S3-07 → **DONE**. The pseudonymization-integrity moat (DC-08, FR-011/012/013) ships — the distinctive capability no competitor benchmark has. Unblocks S3-08 (NFR-005 cross-module separation test pairs this with anonymization.py). Evidence: RED `49fbfba` → GREEN `0ffedd8` → REFACTOR `0e92642`; 143 tests pass (0 regressions); ruff+mypy clean on the new file; pure-stdlib (hashlib); frozen lattice/corpus/tags untouched.
