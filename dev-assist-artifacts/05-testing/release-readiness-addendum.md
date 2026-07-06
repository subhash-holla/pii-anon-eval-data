# Cycle-1 (v2.0.0 dataset) — Release-Readiness RE-RULE addendum

**Date:** 2026-06-01 (v2-scoring-harness close-out). **Verdict: UNCHANGED — SHIP-WITH-CAVEATS.** This addendum
records what the close-out session changed for cycle-1; the canonical report is `release-readiness-report.md`.

## Verdict is unchanged — and here is why (the honesty boundary)
Cycle-1's five caveats are **permanent-by-design or genuinely external**, so closing code could not move the
verdict to unconditional SHIP — only minimize/close the *code sides*:
- **Caveat 1 (synthetic-only, AX-001)** — 🔒 PERMANENT. Unchanged.
- **Caveat 2 (design never real-user-trialed)** — ⏳ pending-external (real consumers). Instrument unchanged.
- **Caveat 3 (formulaic monoculture)** — ⏳ pending-external (distribution-shift vs real data). Unchanged.
- **Caveat 4 (AGENT_SIMULATED, real-CI owed)** — ⏳ pending-external (clean CI image). Unchanged.
- **Caveat 5 (NFR-010 throughput on real hardware)** — ⏳ pending-external; **code side hardened this session**
  (see below) but the verdict stays `INSUFFICIENT_EVIDENCE` until a real 8-core host runs it.

## Cycle-1 code closures this session (strict TDD, committed)
| Item | First-rule status | Re-rule | Evidence |
|---|---|---|---|
| **FR-015 / FR-016** coreference-chain + quasi-id-combination | v1 SEAM (slice loaders), scoring deferred | **SCORING SHIPPED** | `scoring/coreference.py` (chain-as-a-unit: any-mention → chain leaked) + `scoring/quasi_identifier.py` (k-of-n joint re-id); non-strippable low-power caveat; 12 tests |
| **FR-027** real-data correlation | seam-only (`RealDataAbsent`) | **path-activated ingest SHIPPED** | `validation/real_data_ingest.py` `correlate_from_path()` activates on `PII_ANON_REAL_DEID_PATH`; still `RealDataAbsent` until real data dropped; 4 tests + handoff |
| **NFR-010** throughput harness | harness shipped; agent-env INSUFFICIENT_EVIDENCE | **reference-host gate + one-command runner SHIPPED** | `_canonical_verdict` (agent never reaches PASS) + `scripts/run_throughput_benchmark.sh`; verdict still INSUFFICIENT_EVIDENCE (real host owed); 6 tests |
| **FR-028** frictionless citation | genuine gap | **CLOSED** (via CAP-02 C6) | `CITATION.cff` + `CITATION.bib` + `release/citation.py`; DOI = pending sentinel |
| **NFR-051** mypy (pii-rate-elo, consumer) | — | **mypy clean on full src** (61 files, 0 issues) | C13 |

These shrink the cycle-1 "known scope gaps" (FR-014/015/016/028 § of the canonical report): FR-015/016 move
from seam → scoring; FR-028 closed; FR-027's code seam is now path-activated. The remaining FR-014 (query-aware
masking) stays a documented v1.1 gap.

## Guardrails (held — git-verified)
lattice 730@`47c3a8f` · NFR-018 power gate PASS on 575,604 / 0 errors · doc-drift 0 · tags + corpus + lattice
untouched · four metric families never merged · pure-stdlib cores · eval-data suite **502 passed / 7 skipped**.

## Net
Cycle-1 verdict **SHIP-WITH-CAVEATS** (unchanged); the caveat set is the same five, now with their code-sides
closed/hardened where code could. The path to unconditional SHIP is the external items in
`assessment-workflow/05-testing/HUMAN-ONLY-TODO.md` (shared across both cycles).
