# CAP-02 — Example assessment output (REAL v2.0.0 data, captured 2026-06-01)

Produced by the one-command example on the real `splits/test_technology.jsonl.gz` subset (10,352 records →
1822-record powered sample, 15,569 gold positives scored). INDICATIVE (lightweight synthetic systems; real
detectors are Pass-2) — but every academic-soundness bar item is exercised on real data. Verbatim
`results/leaderboard.md`:

---

# PII-Anon v2.0.0 — Assessment Leaderboard (asmt-42-c791fcdf)

> **Synthetic-only (AX-001): every scored record contains ONLY synthetic PII. Per-cell power is statistical precision on the SYNTHETIC distribution, conditional on THIS sample — NOT external validity and NOT a standalone recall claim absent the real-data correlation slice (cycle-1 UC-13). AX-003.**

- Power verdict: **SMALL** · conditional-on-this-sample · synthetic-only
- Inferential target: super-population · preset: powered-representative · gold positives scored: 15569
- Pre-registration: `b65f007acb156c9a…` (verified)
- Convergence: RD-NOT-CONVERGED (ranking provisional)

| rank | system | recall | 95% CI (method) | Elo | RD | tie-group |
|---|---|---|---|---|---|---|
| 1 | regex-strong | 0.922 | [0.918, 0.926] (wilson) | 1625 | 157 | 0 |
| 2 | regex-mid | 0.700 | [0.692, 0.707] (wilson) | 1502 | 157 | 1 |
| 3 | regex-weak | 0.449 | [0.441, 0.457] (wilson) | 1369 | 157 | 2 |

## System-vs-system (paired, Holm-corrected)

| A | B | Δrecall | Δ 95% CI | McNemar p | Holm p | significant |
|---|---|---|---|---|---|---|
| regex-strong | regex-mid | +0.222 | [+0.216, +0.229] | 0.0000 | 0.0000 | yes |
| regex-mid | regex-weak | +0.251 | [+0.244, +0.257] | 0.0000 | 0.0000 | yes |

## Honest verdicts (non-strippable)

- Synthetic-only (AX-001) … [non-strippable caveat]
- RD-NOT-CONVERGED: achieved max-RD 156.5 > threshold 100.0 (tournament-rating convergence only; blocks ranking, NOT recall-CI validity)

---

**What this demonstrates (academic-soundness bar):** seeded/byte-reproducible · powered sample with honest
`SMALL` verdict + 122 per-cell named CORPUS_LIMITED shortfalls (sampler stderr) · a Wilson CI on every metric ·
system-vs-system paired McNemar + Holm (both significant after correction) · Glicko RD reported
(RD-NOT-CONVERGED, honest) · pre-registration plan-hash verified · non-strippable synthetic-only caveat.
Runtime: sampler 0.4s, assessment ~20s (paired bootstrap over 15,569 positives).
