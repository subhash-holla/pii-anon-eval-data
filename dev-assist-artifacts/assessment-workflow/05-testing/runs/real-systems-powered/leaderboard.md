# PII-Anon v2.0.0 — Assessment Leaderboard (asmt-7-94b92c4c)

> **Synthetic-only (AX-001): every scored record contains ONLY synthetic PII. Per-cell power is statistical precision on the SYNTHETIC distribution, conditional on THIS sample — NOT external validity and NOT a standalone recall claim absent the real-data correlation slice (cycle-1 UC-13). AX-003.**

- Power verdict: **SMALL** · conditional-on-this-sample · synthetic-only
- Inferential target: super-population · preset: powered-representative · rigor bar: **full-AX005** · gold positives scored: 15569
- Pre-registration: `4c5609c3a67a359d…` (verified)
- Convergence: RD-NOT-CONVERGED (ranking provisional)

- **Governance (FR-052)** — corpus_owner: PII-Anon maintainers (CC0 synthetic corpus) · label_holder: PII-Anon maintainers (held-out gold labels) · evaluator: pii-rate-elo assessment harness (neutral; no system entrant)
  - _Governance block is a NEUTRALITY / PROVENANCE statement (who controls the corpus, who holds the held-out labels, who runs the eval) — NOT an endorsement. A vendor self-benchmark without it is inadmissible (FR-052)._

| rank | system | recall | 95% CI (method) | Elo | RD | tie-group | contamination |
|---|---|---|---|---|---|---|---|
| 1 | presidio | 0.616 | [0.608, 0.624] (wilson) | 1586 | 157 | 0 | synthetic-bundled |
| 2 | gliner | 0.558 | [0.550, 0.566] (wilson) | 1543 | 157 | 1 | synthetic-bundled |
| 3 | piiranha | 0.285 | [0.278, 0.292] (wilson) | 1373 | 157 | 2 | synthetic-bundled |

## System-vs-system (paired, Holm-corrected)

| A | B | Δrecall | Δ 95% CI | McNemar p | Holm p | significant |
|---|---|---|---|---|---|---|
| presidio | gliner | +0.058 | [+0.050, +0.067] | 0.0000 | 0.0000 | yes |
| gliner | piiranha | +0.273 | [+0.265, +0.281] | 0.0000 | 0.0000 | yes |

## Operating point (recall-priority; FR-048)

| system | precision | recall | Fβ(β=2) | AUPRC | precision@recall_target |
|---|---|---|---|---|---|
| presidio | 0.431 | 0.616 | 0.567 | 0.265† | 0.431 (target not reached) |
| gliner | 0.683 | 0.558 | 0.579 | 0.381† | 0.683 (target not reached) |
| piiranha | 0.435 | 0.285 | 0.306 | 0.124† | 0.435 (target not reached) |

_† AUPRC is DEGENERATE — a single hit-only operating point (AUPRC = recall × precision), NOT a swept precision-recall curve. A score-emitting detector yields a real multi-point AUPRC._

## Honest verdicts (non-strippable)

- Synthetic-only (AX-001): every scored record contains ONLY synthetic PII. Per-cell power is statistical precision on the SYNTHETIC distribution, conditional on THIS sample — NOT external validity and NOT a standalone recall claim absent the real-data correlation slice (cycle-1 UC-13). AX-003.
- RD-NOT-CONVERGED: achieved max-RD 156.5 > threshold 100.0 (tournament-rating convergence only; blocks ranking, NOT recall-CI validity)
- WORST-LANGUAGE recall floor: ko at 0.429 (the per-language minimum; NFR-047 honesty-set)
- rank-volatility UNMEASURED: 0 seed(s) < 3 required — single/under-replicated run makes NO rank-stability claim (NFR-047)
