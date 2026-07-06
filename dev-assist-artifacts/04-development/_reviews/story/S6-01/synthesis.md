# Story Gate Synthesis — S6-01 (Append-only event-sourced held-out leaderboard store; FR-023 / NFR-014)

**Gate:** story · **Scope:** S6-01 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-31

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 0 |
| security-sast | ✅ APPROVE | 1 OBS (forbidden-key reject is top-level-only — nested gold defense-in-depth) |
| requirements-coverage | ✅ APPROVE | 1 OBS (author S6-02/S6-03 + record the FR-023 deferral delta before S6 closes) |
| traceability | ✅ APPROVE | 2 OBS (matrix board refresh at sprint gate; FR-023 partition watch) |
| axiom-compliance | ✅ APPROVE | 0 |

**Aggregate: APPROVE** (zero SHOWSTOPPER / CATASTROPHIC / MAJOR; OBSERVATIONs only).

## Joint signals

- **No held-out gold leak (FR-023, the crux)** — security-sast + requirements-coverage verified
  `append` raises `ValueError` on the 6 forbidden keys (`gold`/`gold_labels`/`held_out`/
  `held_out_labels`/`answers`/`ground_truth`) STRICTLY before any file write — a rejected append leaves
  no file. The store records scores + config_version + attestation (provenance), never gold.
- **Tamper-evidence (NFR-014)** — sha256 content-hash chain (`prev_hash` links; first == `GENESIS_HASH`
  = 64 zeros); `verify_chain()` recomputes and returns `False` on any line mutation; the CLI
  `leaderboard.main(["verify", log])` returns 0 intact / non-zero tampered. Framing is honest: tamper-
  EVIDENT (integrity), not tamper-PROOF against the log owner.
- **Append-only** — public surface is exactly `{append, events, verify_chain}`; zero mutate/delete
  methods; sole writer is `open("a")`.
- **AX-002 determinism / NFR-004 pure-stdlib** — NO `time`/`datetime` (order by monotonic `seq`; any
  wall-clock ts is an optional caller payload field, never generated); AST guard green (only json+hashlib
  +stdlib); two fresh logs from the same events → byte-identical hashes; `import leaderboard` pulls in no
  heavy dep.
- **CLI wired** — S5-05's `pii-anon leaderboard` verb (the `_until_s6` placeholder) is now functional;
  the executor retired the obsolete placeholder test by succession (no production cli.py change).

## Findings forwarded (non-blocking)

- **security-sast (OBS)**: the forbidden-key screen is top-level-only — a nested `{"scores":{"gold":…}}`
  is accepted. Within the documented flat-payload contract, but a recursive screen is a cheap
  defense-in-depth upgrade for a future hardening.
- **requirements-coverage + traceability (OBS → S6 sprint close)**: FR-023 is NOT closed by S6-01 alone —
  the anti-gaming control (rate-limit/rotation/contamination) + opt-in publish are the named successor
  **S6-02**; the CoI is **S6-03**. Author those + record the FR-023 deferral delta + the S6-01 Status
  Change Log advancement at the S6 sprint gate.

## Outcome

S6-01 → **DONE**. The append-only, content-hash-chained held-out leaderboard store ships: held-out gold
never stored (FR-023 forbidden-key reject), tamper-evident (NFR-014 hash chain + `verify_chain`),
append-only (no mutate API), deterministic (seq-ordered, no clock/RNG), pure-stdlib; the S5-05 CLI
`leaderboard` verb is wired. Evidence: RED `7ffbe06` → GREEN `4bd0c2f` → REFACTOR `65153d7` → docs
`9d3dc74`; **302 passed / 1 skipped** (290 prior + 12 new, 0 regressions); ruff + mypy --strict clean;
corpus / lattice / tags untouched. FR-023 store-half closed (policy=S6-02, CoI=S6-03 to follow).
