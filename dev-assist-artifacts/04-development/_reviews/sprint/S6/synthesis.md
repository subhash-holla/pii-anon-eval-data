# Sprint Gate Synthesis — S6 (Leaderboard & governance; DC-13)

**Gate:** sprint · **Scope:** S6 (5 stories) · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-31

| Reviewer | Verdict | Findings |
|---|---|---|
| requirements-coverage | ✅ APPROVE | 1 OBS (real-CI Pass-2 owed before dropping AGENT_SIMULATED) |
| performance-benchmark | ✅ APPROVE | 2 OBS (store append-without-full-reread; indexed submitter/epoch — v1.x hosted-leaderboard hardening) |
| axiom-compliance | ✅ APPROVE | 1 OBS (axiom-ID alias hygiene AX-001 ↔ AX-pii-anon-001) |
| code-quality · traceability · security-sast | ✅ carried forward | APPROVE on all S6 story gates (S6-01/02/03 + combined S6-04-05) — unanimous |

**Aggregate: APPROVE** (zero MAJOR+). The new leaderboard package needed **no coverage-hardening**
(store 97%, policy/coi/__init__ 100% out of the gate); coverage source extended to add
`pii_anon_datasets.leaderboard`.

## Story roster (5/5 DONE, every story gate APPROVE)

| Story | Module / doc | Closes | Notes |
|---|---|---|---|
| S6-01 | `leaderboard/store.py` | FR-023, NFR-014 | append-only hash-chained held-out store; gold never stored; `verify_chain`; CLI verb wired |
| S6-02 | `leaderboard/policy.py` | FR-023, NFR-014 | opt-in publish + anti-gaming (rate-limit / rotation epoch / contamination), distinct reasons; read-only |
| S6-03 | `leaderboard/coi.py` | FR-026/gov-03, NFR-014 | non-strippable no-pre-pub attestation + recusal (maintainer / pii-anon-core, evasion-resistant) |
| S6-04 | `GOVERNANCE.md` | FR-026, NFR-014 | charter + aspirational/AGENT_SIMULATED roster + CoI naming pii-anon-core + honest bus-factor=1 |
| S6-05 | `CONTRIBUTING.md` | FR-025 | PR template + CC0 checklist + synthetic-only provenance + deprecation/erratum + semver |

## MUST-coverage snapshot (sprint)

All S6 requirements VERIFIED with named tests, 0 orphans: **FR-023** (neutral leaderboard — store +
anti-gaming policy + CoI recusal), **FR-025** (contribution pipeline), **FR-026** (governance charter —
CoIRecord + GOVERNANCE.md), **NFR-014** (governance neutrality auditable — its three sub-claims fully
evidenced end-to-end: GOVERNANCE.md+roster+CoI from S6-04; anti-gaming from S6-02; provenance logged from
S6-01 `verify_chain` + S6-03 attestation/recusal). Traceability-matrix Status Change Log records all four
closures (AGENT_SIMULATED — real-CI Pass-2 owed). Full suite **325 passed / 1 skipped**; leaderboard
package 99% (store 97%, rest 100%).

## Cross-cutting verification

- **Governance-integrity controls** (axiom-compliance, behaviorally verified): held-out gold NEVER stored
  (forbidden-key reject fires on all 6 keys); `verify_chain` clean-True / tamper-False on a 1-byte
  mutation; opt-in publish never publishes a disallowed submission; all 3 anti-gaming controls fire as
  distinct reasons; `CoIRecord` rejects an empty attestation; recusal True for maintainer / any
  pii-anon-core affiliation, False for external.
- **Epistemic honesty (S6-04)**: advisory roster flagged ASPIRATIONAL/AGENT_SIMULATED with zero fabricated
  members; bus-factor=1 plainly stated; every CoI/neutrality doc claim maps to a real symbol
  (`verify_chain`, `leaderboard.policy`, `requires_recusal`, `NO_PREPUB_ATTESTATION`) — no over-claiming.
- **NFR-004 pure-stdlib**: AST scan of all 4 leaderboard modules — zero forbidden imports; `import
  leaderboard` pulls no heavy dep. **AX-002 determinism**: seq-not-clock ordering, canonical-JSON hashing,
  pure policy/coi → byte-identical hashes. **AX-001**: CONTRIBUTING.md synthetic-only gate; real-PII scan
  over all S6 surfaces clean.
- **Performance (advisory)**: the store's O(N²)-over-N-appends + the policy's O(N)-per-evaluation are
  empirically single-digit-ms at the intended tens/hundreds-of-submissions seam scale; no corpus hot-path
  leakage. Append-without-full-reread + an indexed submitter/epoch count are v1.x hosted-leaderboard
  hardening (OBSERVATIONs).
- **Guardrails**: corpus / `eval_lattice.json` / `metadata.json` / `MANIFEST.sha256` / tags (`v1.3.0`,
  `pre-lattice-enrichment`) UNTOUCHED across S6 (`git diff --name-only` empty for those paths).

## Forwarded to Stage 5 / v1.x

- Real-CI Pass-2 re-run is the only owed item to drop AGENT_SIMULATED on the S6 MUSTs.
- A hosted leaderboard (append-without-full-reread, indexed counts, identity normalization for the
  submitter-id / recusal evasion) is a documented v1.x hardening — out of the v1 governance-seam scope.

## Outcome

Sprint S6 → **APPROVE / DONE**. The leaderboard + governance seam (DC-13) ships: FR-023, FR-025, FR-026,
NFR-014 all verified. Proceed to `/dev-assist-signoff SO-05-s6`.
