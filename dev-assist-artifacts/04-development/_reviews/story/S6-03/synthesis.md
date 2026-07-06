# Story Gate Synthesis — S6-03 (Conflict-of-interest record + recusal; gov-03 / FR-026 / NFR-014)

**Gate:** story · **Scope:** S6-03 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-31

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 0 |
| axiom-compliance | ✅ APPROVE | 0 (load-bearing — non-strippable attestation + recusal evasion-resistance verified) |
| requirements-coverage | ✅ APPROVE | 2 OBS (don't mark FR-026 verified on S6-03 alone — S6-04/05 owed; FR-023 now sprint-gate-verifiable) |
| traceability | ✅ APPROVE | 3 OBS (matrix refresh; FR-026 partition watch; FR-023 CoI transitive coverage) |
| security-sast | ✅ APPROVE | 1 OBS (hyphen-drop / unicode-look-alike recusal evasion — monitoring) |

**Aggregate: APPROVE** (zero SHOWSTOPPER / CATASTROPHIC / MAJOR; OBSERVATIONs only).

## Joint signals

- **Non-strippable attestation (gov-03 / FR-026)** — `NO_PREPUB_ATTESTATION` constant +
  non-defaulted-validated field + `__post_init__` ValueError on empty/whitespace/NBSP; the text carries
  "pre-publication"+"access"+"held-out"+"train"/"tune". Follows the `crosswalk.py` non-strippable pattern.
- **Recusal control resists evasion (the governance-neutrality invariant)** — `requires_recusal` lowercases
  + strips + substring-matches `pii-anon-core`: `MAINTAINER`, `"  pii-anon-core  "`, `"PII-Anon-Core,
  Inc."`, `"Pii-Anon-Core Labs"` all → True; tight substring keeps externals (`"Acme University"`,
  `"pii anon core"`) False.
- **Embeddable provenance (NFR-014)** — `as_dict()` keys (submitter/affiliation/attestation/
  requires_recusal) are disjoint from the S6-01 store's `_FORBIDDEN_PAYLOAD_KEYS`; the store accepts the
  payload and the recusal flag is logged into the chained log (not stripped).
- **Pure-stdlib + deterministic (NFR-004 / AX-002)** — AST guard green (imports only `{__future__,
  dataclasses}`); `requires_recusal`/`as_dict` pure (stable across runs). No real PII.

## Findings forwarded (non-blocking)

- **requirements-coverage + traceability (OBS → S6 sprint close)**: with S6-01+S6-02+S6-03 landed,
  **FR-023 (leaderboard) is now collectively covered** — mark verified at the S6 sprint gate. **FR-026 is
  NOT closed by S6-03 alone** — its GOVERNANCE.md / roster / bus-factor charter is owed by **S6-04**, and
  the contribution pipeline (FR-025) by **S6-05**. Refresh the traceability-matrix Status Change Log at
  the sprint close.
- **security-sast (OBS)**: hyphen-drop (`piianoncore`) / unicode-look-alike (`pｉｉ-anon-core`) recusal
  evasions — a future identity-normalization hardening (monitoring, non-blocking).

## Outcome

S6-03 → **DONE**. The gov-03 `CoIRecord` ships: a mandatory non-strippable no-pre-publication-access
attestation (empty rejected), `requires_recusal` True for maintainer / pii-anon-core-affiliated submitters
(evasion-resistant via lower+strip+substring), and an `as_dict()` provenance payload embeddable in the
S6-01 store. Evidence: RED `0dfe825` → GREEN `d4e310f` → REFACTOR `2b88750` → docs `a99870b`; **319 passed
/ 1 skipped** (308 prior + 11 parametrized cases, 0 regressions); ruff + mypy --strict clean; store.py /
policy.py / corpus / lattice / tags untouched. FR-023 leaderboard fully covered (S6-01/02/03); FR-026 CoI
data-structure half closed (GOVERNANCE.md = S6-04, CONTRIBUTING.md = S6-05 to follow).
