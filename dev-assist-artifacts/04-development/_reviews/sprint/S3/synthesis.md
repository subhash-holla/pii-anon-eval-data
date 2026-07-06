# Sprint Gate Synthesis — S3 (Scorer trio + adversary port + reid power seam)

**Gate:** sprint · **Scope:** S3 (8 stories) · **Aggregate verdict: APPROVE** · **Iterations:** 2 · **Date:** 2026-05-29

## Reviewer verdicts (sprint gate)

| Reviewer | Verdict | Findings |
|---|---|---|
| requirements-coverage | ✅ APPROVE (iter 2) | iter-1 MAJOR (anonymization.py 72% < 85%) **RESOLVED** → 97% |
| performance-benchmark | ✅ APPROVE | 2 MINOR (O(n²) + redundant recompute) **FIXED** in `bea79ba` |
| axiom-compliance | ✅ APPROVE | 0 (4-way family separation clean) |
| code-quality · traceability · security-sast | ✅ carried forward | APPROVE on all 8 story gates (24 unanimous) |

**Aggregate: APPROVE** (zero MAJOR+ after iteration 2).

## Story roster (8/8 DONE, every story gate APPROVE)

| Story | Scope | Closes | Gate |
|---|---|---|---|
| S3-01 | adversary port + value objects + paired-set assembler + signals | FR-010 port | APPROVE (iter 2) |
| S3-02 | deterministic offline adversary + distractor variant (RRS headline) | FR-007, FR-010 | APPROVE |
| S3-03 | LLM adversary (version-stamped secondary, [llm] extra) | FR-010 | APPROVE |
| S3-04 | measured-attack RRS scorer (Wilson CIs, |C|, caveat) | FR-007, FR-009 | APPROVE |
| S3-05 | exposure index (prior-not-RRS) + index↔RRS correlation | FR-008 | APPROVE |
| S3-06 | anonymization privacy-utility Pareto (unmergeable) | FR-006, NFR-005 | APPROVE |
| S3-07 | pseudonymization-integrity moat (threat model, collision sep, EDPB Art 4(5)) | FR-011/012/013 | APPROVE |
| S3-08 | reid power-ladder seam + NFR-005 cross-module separation | NFR-018, NFR-005 | APPROVE |

## MUST-coverage snapshot (sprint)

All S3 MUSTs verified with named tests: **FR-006** (anon Pareto), **FR-007** (measured RRS), **FR-008** (exposure index), **FR-009** (non-strippable caveat, structural), **FR-011/012/013** (pseudonymization moat), **NFR-005** (anon/pseudo never merged), **NFR-018** (reid power seam). FR-010 (SHOULD) verified (offline + LLM). **0 orphans.** M6 closed in substance: all four privacy directions (detection/anon/pseudo/RRS) now have *running* scorers.

## Cross-cutting verification (high confidence)

- **AX-004/NFR-005 4-way separation** — no public path merges any two metric families into a de-id headline; mutation-tested (S3-08 security-sast injected 4 fusion vectors → audit FAILED on each).
- **AX-003 statistical rigor** — every metric carries a named-method CI on integer counts; reid ladder NIST-derived (897/385).
- **AX-002 determinism** — headline offline adversary byte-reproducible; LLM secondary flagged `deterministic=False`, opt-in.
- **AX-001 synthetic-only** — no real PII in any module/fixture.
- **S-PWR guardrail HELD** — frozen `eval_lattice.json` (730 cells) untouched; tags `v1.3.0` + `pre-lattice-enrichment` intact; no corpus regeneration.

## Coverage / quality

- 169 passed, 1 skipped (the `anthropic`-absent contract skip); **93% aggregate** line on scoring+stats; every new scorer module ≥85% line (NFR-016).
- Pre-existing lint baseline (power.py UP035/E702/type-arg; reidentification.py UP037/type-arg; __init__ I001) deferred to a Stage-5 lint-hardening pass (reviewer-recommended; out of every story's scope).

## Epistemic honesty

All S3 work `provisional_status: AGENT_SIMULATED` (no DIVERGED DC → no statistical Pass-2). The execution-environment **real-CI Pass-2** on a clean checkout is owed before any S3 MUST counts RELEASE-verified — recorded for Stage 5.

## Outcome

**Sprint S3 → DONE.** Ready for S4 (stats/reporting completion — Clopper-Pearson, paired McNemar/bootstrap, ECE/Brier, per-language power table, viz; consumes the reid power seam for per-track power reporting).
