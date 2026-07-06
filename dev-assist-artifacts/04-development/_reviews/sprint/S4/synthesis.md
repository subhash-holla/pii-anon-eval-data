# Sprint Gate Synthesis — S4 (Stats/reporting completion, DC-09)

**Gate:** sprint · **Scope:** S4 (5 stories) · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-29

| Reviewer | Verdict | Findings |
|---|---|---|
| requirements-coverage | ✅ APPROVE | 0 (all MUSTs verified; every module ≥85% line) |
| performance-benchmark | ✅ APPROVE | 2 OBS (n_boot unbounded; coverage_risk_curve O(n log n)) |
| axiom-compliance | ✅ APPROVE | 0 (NFR-004 purity boundary verified empirically) |
| code-quality · traceability · security-sast | ✅ carried forward | APPROVE on all 5 story gates (15 unanimous) |

**Aggregate: APPROVE** (zero MAJOR+). The proactive coverage-hardening (`243ba63`, power_table 74%→100%) **preempted** the per-module coverage MAJOR.

## Story roster (5/5 DONE, every story gate APPROVE)

| Story | Module | Closes | Notes |
|---|---|---|---|
| S4-01 | `stats/intervals.py` (+CP) | FR-004, NFR-002 | Clopper-Pearson via stdlib inverse-beta; CP⊇Wilson; textbook-verified |
| S4-02 | `stats/paired.py` | FR-002 (measure), NFR-002 | McNemar exact/χ² + seeded paired bootstrap (local random.Random) |
| S4-03 | `stats/calibration.py` | FR-005, NFR-008 | ECE/Brier/reliability per entity class; ECE≤0.05 reported-not-gated |
| S4-04 | `reporting/language_power.py` | NFR-003 | per-language + language×type power transparency (recovered from a long-run interruption) |
| S4-05 | `reporting/viz.py` | FR-005, NFR-003, FR-006 | reliability/Pareto/heatmap/Sankey/coverage-risk; `[viz]` extra; FR-005 abstention facet CLOSED |

## MUST-coverage snapshot (sprint)

All S4 requirements VERIFIED with named tests: **FR-004** (Clopper-Pearson), **FR-002** (paired McNemar measurement), **NFR-002** (every CI method-named: Wilson/Clopper-Pearson/paired-bootstrap/McNemar — zero bare estimates), **NFR-003** (per-language + language×type table + slice heatmap), **FR-005** (calibration + reliability diagram + abstention curve — **COMPLETE** across S4-03+S4-05, no successor owed), **NFR-008** (ECE reference reported-not-gated). **0 orphans.**

## Cross-cutting verification

- **AX-003** every CI named-method on integer counts; reid seam composes (one z-table). **NFR-004** purity boundary HELD (matplotlib lazy behind `[viz]`; `import reporting` leaves it out of `sys.modules`). **AX-004/NFR-005** no reporter fuses families (`pareto_plot` two-axis). **AX-002** deterministic (seeded bootstrap, fixed-iter CP, sorted reporters; viz correctly avoids PNG byte-equality). **AX-001** no real PII.
- **Epistemic honesty:** NFR-008 reported-not-gated (no covert submitter fail); the FR-027 synthetic-not-external-validity caveat is in `power_report`'s *rendered* markdown.
- **S-PWR guardrail HELD:** frozen `eval_lattice.json` (730 cells) untouched; tags intact; no corpus regeneration; reporters take `(lattice, observed_counts)` as args (no corpus read).

## Coverage / quality

- 211 passed, 1 skipped (the `anthropic`-absent contract skip); 92% aggregate; **every stats+reporting module ≥85% line** (power_table 100%, intervals 87%, calibration 96%, paired 92%, viz 96%, language_power 97%, power 91%, lattice 97%).

## Outcome

**Sprint S4 → DONE.** DC-09 stats/reporting complete. `provisional_status: AGENT_SIMULATED` (no DIVERGED DC; real-CI Pass-2 owed at Stage 5). Ready for S5 (exports/CLI + compliance + doc-drift).
