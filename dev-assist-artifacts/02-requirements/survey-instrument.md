# R5 — Prioritization Survey Instrument

**Stage 2 · R5** · 2026-05-28. 3-tier instrument over **15 rankable capability bundles** (the 28 FRs grouped to keep the respondent task tractable).

## Rankable bundles
1. **B1 Detection scoring + CI regression gate** (FR-001/002)
2. **B2 Scorer I/O contract + Presidio adapter** (FR-003)
3. **B3 Per-slice CIs + statistical power** (FR-004 + NFR-001/002/003)
4. **B4 Calibration + abstain** (FR-005 + NFR-008)
5. **B5 Anonymization output scoring (Pareto)** (FR-006)
6. **B6 Measured RRS + paired personas** (FR-007/008/010 + NFR-007)
7. **B7 Non-strippable anti-anonymity caveat** (FR-009)
8. **B8 Pseudonymization-integrity scoring** (FR-011/012/013)
9. **B9 Query-aware masking** (FR-014)
10. **B10 Coreference + quasi-identifier-combination** (FR-015/016)
11. **B11 Agentic oracle + payloads** (FR-017/018/019/020)
12. **B12 End-state bundle + regulatory crosswalk** (FR-021/022)
13. **B13 Neutral leaderboard + governance** (FR-023/026 + NFR-014)
14. **B14 CC0 exports + contribution pipeline** (FR-024/025 + NFR-012)
15. **B15 Real-data validation slice** (FR-027) · **B16 frictionless citation** (FR-028)
+ engineering quality (NFR-016 test/CI) treated as a baseline gate (not ranked).

## Tier A — 3-axis scoring (1–5 each): impact · effort · persona-affinity.
## Tier B — MoSCoW: Must / Should / Could / Won't, from the respondent's persona seat.
## Tier C — forced trade-offs (pick one):
- T1: **B6 measured RRS** OR **B8 pseudonymization-integrity** (if only one ships in v1)?
- T2: **B15 real-data slice** OR **broader B6/B7 polish**?
- T3: **B2 Presidio adapter (adoption)** OR **B10 coreference/quasi-id (depth)**?
- T4: **B13 neutral governance** OR **faster v1 ship**?
- T5: **B3 statistical power** OR **B11 agentic breadth**?

Respondent plan (R6): stratified by persona + sub-archetype; ≥2 per persona.
