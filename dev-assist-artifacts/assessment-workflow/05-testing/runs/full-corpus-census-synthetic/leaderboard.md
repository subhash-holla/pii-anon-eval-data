# PII-Anon v2.0.0 — Assessment Leaderboard (asmt-7-9827a54e)

> **Synthetic-only (AX-001): every scored record contains ONLY synthetic PII. Per-cell power is statistical precision on the SYNTHETIC distribution, conditional on THIS sample — NOT external validity and NOT a standalone recall claim absent the real-data correlation slice (cycle-1 UC-13). AX-003.**

- Power verdict: **LARGE** · conditional-on-this-sample · synthetic-only
- Inferential target: descriptive-census · preset: full-corpus · rigor bar: **full-AX005** · gold positives scored: 2486438
- Pre-registration: `dc1af4c40e67c13b…` (verified)
- Convergence: RD-NOT-CONVERGED (ranking provisional)

- **Governance (FR-052)** — corpus_owner: PII-Anon maintainers (CC0 synthetic corpus) · label_holder: PII-Anon maintainers (held-out gold labels) · evaluator: pii-rate-elo assessment harness (neutral; no system entrant)
  - _Governance block is a NEUTRALITY / PROVENANCE statement (who controls the corpus, who holds the held-out labels, who runs the eval) — NOT an endorsement. A vendor self-benchmark without it is inadmissible (FR-052)._

## Leaderboard (DESCRIPTIVE — inference suppressed)

> CI + pairwise p-values are SUPPRESSED for this run-type / inferential-target (NFR-025/033/034): point-estimate recall + power verdict only; NO inferential claim.

| rank | system | recall | Elo | RD | contamination |
|---|---|---|---|---|---|
| 1 | regex-strong | 0.920 | 1625 | 157 | synthetic-bundled |
| 2 | regex-mid | 0.699 | 1502 | 157 | synthetic-bundled |
| 3 | regex-weak | 0.450 | 1369 | 157 | synthetic-bundled |

## Operating point (recall-priority; FR-048)

| system | precision | recall | Fβ(β=2) | AUPRC | precision@recall_target |
|---|---|---|---|---|---|
| regex-strong | 1.000 | 0.920 | 0.935 | 0.920† | 1.000 |
| regex-mid | 1.000 | 0.699 | 0.744 | 0.699† | 1.000 (target not reached) |
| regex-weak | 1.000 | 0.450 | 0.505 | 0.450† | 1.000 (target not reached) |

_† AUPRC is DEGENERATE — a single hit-only operating point (AUPRC = recall × precision), NOT a swept precision-recall curve. A score-emitting detector yields a real multi-point AUPRC._

## Honest verdicts (non-strippable)

- Synthetic-only (AX-001): every scored record contains ONLY synthetic PII. Per-cell power is statistical precision on the SYNTHETIC distribution, conditional on THIS sample — NOT external validity and NOT a standalone recall claim absent the real-data correlation slice (cycle-1 UC-13). AX-003.
- RD-NOT-CONVERGED: achieved max-RD 156.5 > threshold 100.0 (tournament-rating convergence only; blocks ranking, NOT recall-CI validity)
- CI/p-values SUPPRESSED under rigor_bar='full-AX005' / inferential_target='descriptive-census' (NFR-025/033/034): point-estimate recall + power verdict only — NO confidence intervals, NO pairwise significance, NO tie-gating; this run makes NO inferential claim (descriptive-census / smoke-inert).
- WORST-LANGUAGE recall floor: ha at 0.903 (the per-language minimum; NFR-047 honesty-set)
- rank-volatility UNMEASURED: 0 seed(s) < 3 required — single/under-replicated run makes NO rank-stability claim (NFR-047)
