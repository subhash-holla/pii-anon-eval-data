# R7 — Prioritization Analysis + Decisions

**Stage 2 · R7** · 2026-05-28 · Input: 12 R6 survey responses (`survey-analysis.md`) + R3 synthesis. `provisional_status: AGENT_SIMULATED`.

> **Scale note:** R6 ran at representative n=12 (2 per persona × 6) rather than literal n=60 (single-session execution limit). Signal was highly consistent across respondents (low variance on B5/B6/B7/B12), so the prioritization is well-supported; **real-user Pass-2 still recommended** for load-bearing MUSTs. Documented in `methodology.md`.

## Aggregate MoSCoW (12 respondents)
| Bundle | M | S | C | W | Verdict |
|---|---|---|---|---|---|
| B5 anon-Pareto | 11 | 1 | | | **MUST** |
| B6 measured-RRS | 12 | | | | **MUST (headline)** |
| B7 non-strippable caveat | 11 | | | 1 | **MUST** |
| B12 end-state + crosswalk | 10 | 1 | | 1 | **MUST** |
| B8 pseudonymization-integrity | 8 | 4 | | | **MUST (moat; persona-stratified)** |
| B3 per-slice CIs + power | 7 | 3 | 2 | | **MUST** |
| B1 detection + CI gate | 6 | 6 | | | **MUST** |
| B2 scorer I/O + Presidio adapter | 5 | 4 | 3 | | **MUST** |
| B13 neutral leaderboard + governance | 4 | 6 | 2 | | **MUST** (boundary — see D1) |
| B14 CC0 exports + contribution | 3 | 6 | 3 | | **split: exports MUST, contribution SHOULD** (D2) |
| B10 coreference + quasi-id | 3 | 8 | 1 | | **SHOULD (v1.1)** (D3) |
| B4 calibration + abstain | 1 | 7 | 3 | 1 | **SHOULD** |
| B9 query-aware masking | 2 | 10 | | | **SHOULD** |
| B15 real-data slice | 3 | 4 | 4 | 1 | **SHOULD (v1.1 — the unlock)** (D4) |
| B16 frictionless citation | 1 | 7 | 1 | 3 | **SHOULD** (leaning COULD) |
| B11 agentic oracle | | | 10 | 2 | **COULD** (D5) |

## Forced trade-off outcomes
- **T1 (RRS vs pseudo-integrity):** 7–5 RRS — but the split confirms **both are MUST**; if only one in a hypothetical cut, RRS edges. Ship both.
- **T2 (real-data slice vs RRS/caveat polish):** 6–6 — adjudicated: **polish RRS/caveat in v1; real-data slice → v1.1** (it's the credibility unlock but explicitly post-v1, and commercial persona actively prefers synthetic-first).
- **T3 (Presidio adapter vs coreference depth):** ~6–6 — adjudicated: **adapter v1 (adoption gate), coreference/quasi-id v1.1 (depth)**.
- **T4 (governance vs faster ship):** 7–5 governance — **B13 MUST** (reinforces §0 locked decision; DPOs can't cite without it).
- **T5 (statistical power vs agentic breadth):** 10–2 power — **B3 MUST, B11 COULD**.

## Boundary-item adjudications (rationale)
- **D1 — B13 governance = MUST** (not SHOULD despite only 4 direct M): T4 result + §0 locked arms-length decision + DPOs/researchers treat it as a hard trust gate ("un-citable without CoI/advisory body"). Locked MUST.
- **D2 — B14 split:** Croissant-validates-and-loads + standard exports (FR-024, NFR-012) = **MUST** (distribution precondition, §5 universal); inbound contribution pipeline (FR-025) = **SHOULD** (broadens past v1).
- **D3 — B10 coreference/quasi-id = SHOULD/v1.1:** strong from legal-de-id + re-id specialist ("the crux"; "where synthetic benchmarks fail"), but T3 deferred depth behind adoption. **Flag: this is the most important SHOULD — N1 is a genuine differentiator; promote to MUST if v1.1 slips.**
- **D4 — B15 real-data slice = SHOULD/v1.1:** the dominant credibility unlock (academics/re-id would make it MUST-for-headline-citation) but explicitly post-v1, Pass-2, co-published. **PERSONA-CONDITIONAL.**
- **D5 — B11 agentic = COULD:** only red-teamers value it; honestly-bounded oracle (FR-017) kept as SHOULD-for-redteam/COULD-overall; FR-018/019/020 = COULD/roadmap.

## Resulting FR/NFR priority assignment
- **MUST (16 FRs + core NFRs):** FR-001, 002, 003, 004, 006, 007, 008, 009, 011, 012, 013, 021, 022, 023, 024, 026 · NFR-001, 002, 005, 006, 007, 011, 012, 013, 014, 015, 016, 017.
- **SHOULD (8 FRs + NFRs):** FR-005, 010, 014, 015, 016, 025, 027, 028 · NFR-003, 008, 009, 010.
- **COULD (4 FRs):** FR-017, 018, 019, 020.
- **Distribution:** ~30% MUST / ~55% SHOULD / ~15% COULD — natural shape. No OUT items (the 15 UCs were already SME-filtered; nothing scored majority-W).

## Persona-stratification note
Pseudonymization-integrity (B8/FR-011-013): **MUST** overall, but value is persona-stratified — load-bearing for tool-builders, DPOs, batch-priv-eng; **irrelevant** to clinical-de-id (irreversible removal) and red-teamers. Documented so it's not mistaken for universal demand.
