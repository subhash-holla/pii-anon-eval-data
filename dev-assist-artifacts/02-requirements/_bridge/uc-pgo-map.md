# R0 — UC↔PGO Bridge

**Stage 2 · Phase R0** · 2026-05-28 · Input: `01-discovery/{discovery-report,personas,workflow-maps,04-use-cases}.md`

> **Brownfield Mode — Source Signal vs Gaps**
> - **From assessment/Discovery (cited):** 15 UCs (v2, SME-reviewed) + 18 P/G/O triples + 6 priority-classified personas.
> - **Inferred but unconfirmed:** priority hints below (finalized in R7 after survey).
> - **Gaps the user must fill:** real-user validation (Pass-2).
> - **Does NOT cover:** the 9 forward-deferred items N1–N9 yet (enter at R1/R4 as net-new candidate requirements).

## Forward map: UC → PGO → persona → priority hint → acceptance signal

| UC | Track | PGO triple(s) | Lead persona(s) | Priority hint | Acceptance signal (→ FR/NFR seed) |
|---|---|---|---|---|---|
| UC-01 | DET | PGO-builder-01, priveng-03 | tool-builder, priv-eng | MUST | deterministic CI scoring; injected bypass caught; F2 per language/attack slice; **Presidio reference adapter + scorer I/O contract** |
| UC-02 | DET/X | PGO-researcher-03, acaddeid-01 | researcher, acad-deid | MUST | per-slice P/R/F1/F2 with **Wilson/Clopper-Pearson CIs**; ≥753-positive high-recall bar; **paired stat** for subgroup gaps |
| UC-03 | DET/X | (calibration theme) | priv-eng, researcher | SHOULD | ECE/Brier + reliability diagram per entity class; abstention coverage-risk curve |
| UC-04 | ANON | PGO-builder-03, dpo-02 | researcher, tool-builder, dpo | MUST | scorer ingests system's anonymized text (M6); residual-risk **declares threat model**; **pinned utility probe** |
| UC-05 | ANON | PGO-researcher-02, acaddeid-02 | researcher, acad-deid, dpo | MUST (headline) | measured-attack RRS (recall/precision + Wilson CI); **\|C\| param**; **version-pinned, pluggable, distractor-augmented adversary**; non-strippable anti-anonymity caveat; + exposure-index pre-screen |
| UC-06 | PSEUDO | PGO-builder-03, dpo-01 | tool-builder, researcher, dpo | MUST (moat) | threat model enumerated; **deterministic-linkage vs cryptographic collision separated**; key-rotation pass/fail; **key/state separation** (EDPB Art. 4(5)) |
| UC-07 | X/DET | (query-aware theme) | priv-eng, researcher | SHOULD | PII-relevance P/R + answer-quality delta + over-redaction rate on 8K+ query-aware records |
| UC-08 | AGENT | PGO-redteam-01, redteam-02 | agentic-redteam | SHOULD | callable oracle API + payload tuples (span+carrier+intent); multilingual/obfuscation; **NOT marketed as agent-leakage scoring**; live-harness adapter = roadmap |
| UC-09 | AGENT/ANON | PGO-redteam-03 | agentic-redteam, researcher | COULD | per-channel/per-turn residual-leakage estimate w/ transcript-distribution caveat |
| UC-10 | X | PGO-dpo-01, dpo-03 | dpo, priv-eng | MUST | DPIA **input** bundle; anon-vs-pseudo separation; **legally-distinct** GDPR/HIPAA/CCPA(+PCI-DSS) columns; anti-case |
| UC-11 | X (gov) | PGO-builder-02, researcher-01 | tool-builder, researcher, host | MUST | held-out labels; submission policy; **anti-gaming**; opt-in publish + private pre-score + config attestation; named arbiter + CoI; DOI host |
| UC-12 | X | PGO-acaddeid-03 | acad-deid, researcher, tool-builder | MUST | CC0; deterministic load; **Croissant validates + loads via HF**; contribution pipeline + erratum policy; dated versions |
| UC-13 | X | (real-data-slice theme) | acad-deid, researcher, tool-builder | SHOULD (v1.1) | estimator+MDE+bootstrap-CI on τ; domain-matched English slice; Bland-Altman; co-pub governance terms; **Pass-2 (not agent-simulable)** |
| UC-14 | X | PGO-priveng-01 | priv-eng | COULD | leaderboard filterable by language/domain/track; "pre-screen not procurement oracle" |
| UC-15 | X (gov) | (§0 governance decision) | host/maintainer | MUST | GOVERNANCE.md + advisory roster + CoI; semantic-versioned dated releases; submission policy; bus-factor note; CI-verified harness |

## Reverse map: PGO → UC (no orphan PGOs)
All 18 P/G/O triples map forward to ≥1 UC (researcher-01→UC-11; researcher-02→UC-05; researcher-03→UC-02; builder-01→UC-01; builder-02→UC-11; builder-03→UC-04,06; acaddeid-01→UC-02; acaddeid-02→UC-05; acaddeid-03→UC-12; redteam-01,02→UC-08; redteam-03→UC-09; priveng-01→UC-14; priveng-02→UC-02/03 scaffold; priveng-03→UC-01; dpo-01→UC-06,10; dpo-02→UC-04; dpo-03→UC-10). ✔

## Orphan scan
- **UCs without a PGO source:** 0 (UC-03, UC-07, UC-13 trace to Discovery §-themes rather than a single PGO; flagged as theme-derived, not orphan — acceptable).
- **PGOs without a UC consumer:** 0.
- **Personas without a UC:** 0 (all 6 + host have ≥2).
- **Orphan rate:** 0% (< 20% gate). ✅ **R0 PASSES — proceed to R1.**

## Carry-in: N1–N9 (forward-deferred from §5) become candidate net-new requirements at R1/R4
N1 coreference/quasi-id-combination scoring · N2 cost-aware/cheap adversary · N3 adversary-pluggability (→UC-05) · N4 runtime latency/throughput + streaming · N5 financial-PII coverage · N6 cross-turn fragmented-leakage payloads · N7 per-language sample-size table · N8 frictionless citation (BibTeX/template/claims-policy) · N9 display-layer regime distinctness + PCI-DSS (→UC-10).
