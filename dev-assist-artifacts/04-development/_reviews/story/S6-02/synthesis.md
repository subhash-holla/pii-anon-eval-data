# Story Gate Synthesis — S6-02 (Leaderboard submission policy: opt-in publish + anti-gaming; FR-023 / NFR-014)

**Gate:** story · **Scope:** S6-02 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-31

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 0 (verbatim §8b; mypy --strict clean on production + tests) |
| security-sast | ✅ APPROVE | 1 OBS (submitter-id case-variation resets rate count — identity-normalization hardening) |
| requirements-coverage | ✅ APPROVE | 1 OBS (author S6-03 + record FR-023 deferral delta before S6 closes) |
| traceability | ✅ APPROVE | 2 OBS (matrix board refresh; FR-023 CoI partition watch) |
| axiom-compliance | ✅ APPROVE | 0 |

**Aggregate: APPROVE** (zero SHOWSTOPPER / CATASTROPHIC / MAJOR; OBSERVATIONs only).

## Joint signals

- **Opt-in publish (FR-023)** — security-sast verified exhaustively + behaviorally that `published =
  allowed and publish_opt_in` makes a disallowed submission unpublishable even with `publish_opt_in=True`;
  no path yields `published=True` while `allowed=False`.
- **Anti-gaming active (NFR-014)** — rate-limit keyed on `(submitter, current_epoch)` (the `declared_epoch`
  spoof is defeated by the exact-equality `stale_epoch` block); held-out rotation rejects stale epochs;
  contamination flags a re-used `submission_hash`. Each control adds a distinct order-stable `reason`.
- **Read-only over the store** — `evaluate_submission` never writes (the only `.append` is to a local
  `reasons` list); axiom-compliance + security-sast confirmed the JSONL log is SHA-256 byte-identical +
  event-count unchanged before/after blocked/dup/clean evaluations.
- **Pure-stdlib + deterministic (NFR-004 / AX-002)** — AST guard green; 5 identical runs → byte-identical
  `PolicyDecision`; the decision is a pure function of (store events, submission, config). No real PII.

## Findings forwarded (non-blocking)

- **security-sast (OBS)**: submitter-id case-variation resets the rate count (consistent with the §8b
  spec which treats the id as opaque) — a future identity-normalization hardening.
- **requirements-coverage + traceability (OBS → S6 sprint close)**: with S6-01 (store) + S6-02 (policy)
  landed, FR-023's leaderboard + anti-gaming + opt-in are covered; the **CoI sub-part is the named
  successor S6-03**, so FR-023 is NOT yet fully closed. Author S6-03 + record the FR-023 deferral delta +
  the per-story Status Change Log advancement at the S6 sprint gate.

## Outcome

S6-02 → **DONE**. The submission policy ships: opt-in publish + the three FR-023 anti-gaming controls
(rate-limit, held-out rotation epoch, contamination/duplicate), each with a distinct reason; read-only
over the store; deterministic; pure-stdlib. Evidence: RED `3f5fbe2` → GREEN `5b6e19c` → REFACTOR
`14d9f8d` → docs `3eafda4`; **308 passed / 1 skipped** (302 prior + 6 new, 0 regressions); ruff + mypy
--strict clean (production + tests); store.py / corpus / lattice / tags untouched. FR-023 policy-half
closed (CoI = S6-03 to follow).
