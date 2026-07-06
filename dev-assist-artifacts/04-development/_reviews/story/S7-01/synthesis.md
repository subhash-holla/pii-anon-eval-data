# Story Gate Synthesis — S7-01 (PII-recognition oracle; FR-017 / DC-10 bounded)

**Gate:** story · **Scope:** S7-01 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-31

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 0 |
| axiom-compliance | ✅ APPROVE | 0 (load-bearing — non-strippable scope guard + recognition-only verified) |
| requirements-coverage | ✅ APPROVE | 1 OBS (FR-017 stays PARTIAL — payload library = S7-02) |
| traceability | ✅ APPROVE | 2 (1 MINOR matrix-row-pending, 1 OBS S7-02 not yet authored) |
| security-sast | ✅ APPROVE | 0 (pure-stdlib value object; scope-honesty guard non-strippable) |

**Aggregate: APPROVE** (zero SHOWSTOPPER / CATASTROPHIC / MAJOR; OBSERVATIONs + 1 MINOR matrix-row nit).

## Joint signals

- **Non-strippable "NEVER agent-leakage scoring" scope guard (FR-017, the crux)** — axiom-compliance +
  security-sast verified via stress tests that `ORACLE_DISCLAIMER` cannot be silently dropped (empty /
  whitespace / None all raise; frozen dataclass blocks mutation; `as_dict()` always serializes it; the
  module carries NO scoring/leak/cross-turn/residual measurement logic — recognition-only). This holds the
  DC-10-bounded scope at the type level.
- **Recognition correctness** — `recognize(record)` → one `RecognizedEntity` per gold annotation;
  `.labels()` matches; `recognize_span` returns the matching entity or `None`.
- **Pure-stdlib + deterministic + AX-001** — imports only `{__future__, collections, dataclasses}`; AST
  guard green; byte-identical re-runs; synthetic gold only (no real PII, no I/O, no egress/secrets).

## Findings forwarded (non-blocking)

- **requirements-coverage + traceability (OBS → S7 sprint close)**: FR-017 is bipartite (oracle API **AND**
  injection payloads). S7-01 delivers the **oracle-API half** + the scope guard; the **injection-payload
  library is the named successor S7-02**. Keep FR-017 PARTIAL until S7-02 lands; author S7-02 + record the
  matrix row at the S7 sprint gate.

## Outcome

S7-01 → **DONE**. The PII-recognition oracle ships: `recognize` / `recognize_span` return labeled-entity
verdicts carrying the non-strippable "never marketed as agent-leakage scoring" disclaimer (FR-017 scope
guard); recognition-only; pure-stdlib; deterministic; synthetic gold. Evidence: RED `132f760` → GREEN
`9269943` → REFACTOR `19a4dfc` → docs `8a1bb56`; **329 passed / 1 skipped** (325 prior + 4 new, 0
regressions); ruff + mypy --strict clean; base/offline/llm adversary + corpus / lattice / tags untouched.
FR-017 oracle-half closed (payload library = S7-02).
