# Discovery §3 — Market Research (JTBD + Kano + Pugh)

**Stage**: 01-Discovery · Section 3
**Date**: 2026-05-28
**Method**: 3 parallel agents — `jtbd-analyst`, `kano-analyst`, `pugh-comparator` — triangulating jobs, feature value-shape, and competitive position with live web verification.

> **Brownfield Mode — Source Signal vs Gaps**
> - **From assessment (cited):** market context rated STRONG (`COMPARISON.md`, `docs/PUGH_CHART_ANALYSIS.md`) — extracted AND **corrected** here (finding o1 + 4 newly-found false claims).
> - **Confirmed (not just inferred):** the 2026 competitors flagged "unverified" in §0/§2 are **VERIFIED real** (see Part C). The §0 CATASTROPHIC finding stands — the refined POV was the correct call.
> - **Gaps the user must fill:** real-user JTBD/Kano validation (Pass-2).
> - **Does NOT cover:** pricing/WTP (≈$0 across personas; CC0).

---

## A. Jobs-To-Be-Done (6 jobs; top 3 to optimize)

| Job | Statement (abbrev.) | Incumbent coverage | Verdict |
|---|---|---|---|
| **J1 Re-id resistance** | "prove my system resists LLM re-identification" | TAB (real, EN, clinical/legal) + **RAT-Bench** (synthetic, 2026) | underserved but **now contested** |
| **J2 Pseudonymization integrity** | "prove my reversible pseudonymizer is sound" | **none** | **uncontested greenfield — the moat** |
| **J3 Defensible numbers** | "get a statistically defensible, peer-acceptable number" | i2b2/TAB (peer-accepted but underpowered) | underserved, **gated by synthetic ceiling** |
| **J4 Shareable breadth** | "stress-test on shareable data w/o IRB/DUA" | **AI4Privacy** (Schelling point) | well-served — don't compete on breadth alone |
| **J5 Regression/bypass CI** | "catch regressions & adversarial bypasses pre-release" | Presidio eval, PIIBench; AgentDojo (agentic) | adequately served — table-stakes |
| **J6 Legal end-state** | "reach a defensible anon-vs-pseudo end-state w/ residual-risk" | PrivaCI-Bench (reasoning, not end-state separation) | underserved — distinctive |

**Top 3 to optimize:** **J2** (uncontested; differentiation-per-effort moat) → **J1** (citable hook + 2026 tailwind, but differentiate on what RAT-Bench lacks: paired personas + multilingual + integration with pseudo scoring) → **J3** (credibility multiplier, whose value is **capped until the real-data validation slice lands**). Deliberately deferred: J4 (out-incumbenting AI4Privacy on breadth is a losing game) and J5's live-agentic dimension (AgentDojo/AgentLeak own it).

## B. Kano feature value-shape → v1 sequencing

**Must-haves (v1 floor — absence = non-adoption by the 3 HIGH personas):** span P/R/F1/F2 · reproducible/deterministic **CI-verified** harness · **neutral governance + leaderboard + held-out provenance** · clean HF/Parquet/Croissant exports · regulatory crosswalk (must-have for DPO).

**Performance dimensions to push (the body of the value prop):** per-slice statistical power + CIs · multilingual breadth (60 langs — still leading post-MultiGraSCCo's 10) · adversarial robustness · anonymization residual-risk + utility (Pareto).

**Delighters (2, deliberately — the word-of-mouth surface):**
1. **Pseudonymization-integrity scoring** — the *safe, uncontested flagship*; empty quadrant across all 9 competitors; maps 1:1 to the GDPR anon-vs-pseudo distinction. **Lead marketing here.**
2. **LLM RRS + paired personas + anonymization Pareto** — the *contested-but-leading* magnet; differentiate as **multilingual + paired-persona + integrated**, not as a standalone RAT-Bench competitor.

**Must-have currently deferred (the #1 fast-follow):** **real-data validation slice** (correlation vs i2b2-2014/TAB). Tolerated as absent only because v1 is explicitly pre-validation; it is the single highest-leverage credibility unlock. → v1.1, co-publish with a recognized de-id group.

**Reverse-feature guardrails (things that ACTIVELY dissatisfy):**
- **Do NOT** position the 1,000 static AI-era records as an *agent-leakage benchmark* — AgentLeak shows 41.7% of leaks are internal-channel; static records can't score that. Rescope to "PII-recognition oracle + injection-payload seed library"; live-harness adapter = v2 roadmap.
- **Never** collapse anon + pseudo into one "redaction-quality" score (DPO: "legally meaningless"). The separation *is* the thesis (axiom AX-pii-anon-004).
- **No** RRS leaderboard without held-out labels + submission provenance (tool-builders bounce on gamed leaderboards).

## C. Pugh competitive position

### C.1 Citation verification (all VERIFIED; 4 existing-doc claims are FALSE)
All 2026 papers flagged "unverified" in §0/§2 resolve to **real arXiv preprints** (retrieved 2026-05-28): RAT-Bench (2602.12806, Imperial — scores tools by re-id risk), PIIBench (2604.15776 — 2.37M seqs, 8 systems <0.14 F1), AgentLeak (2602.11510 — 41.7%-missed figure exact), From-Weak-Cues (2603.18382 — 79.2% re-id), GLiNER Guard (2605.05277). **⇒ the §0 CATASTROPHIC finding is confirmed: the original "no public benchmark measures all three" claim was falsifiable. Refined POV validated.**

**`COMPARISON.md` corrections required (carry to Development — finding M1):**
| Claim in COMPARISON.md | Reality |
|---|---|
| SPY — "Mökander et al. 2023, real clinical, restricted access" | **FALSE** → SPY, NAACL-SRW 2025, **synthetic**, ~8.7K medical+legal, **open** |
| PIILO — "Pikkanen et al." | **invented author** → Learning Agency Lab / Vanderbilt (CRAPII), 2024 |
| AI4Privacy — "580K / 8 languages / 20-54 types" | **stale** → 1.4M / 23 languages / 19 classes (CC BY 4.0) |
| Nemotron-PII — "200K" | **inflated** → 100K |
| (missing) | add **RAT-Bench, PIIBench, AgentLeak** as primary 2026 competitors |
| name collision | disambiguate **PIIBench (2604.15776)** vs **PII-Bench (2502.18545)** vs GLiNER-Guard's internal "PII-Bench" with explicit arXiv IDs everywhere |

### C.2 Weighted matrix (PII-Anon = datum; verified competitors only)
PII-Anon ranks **#2 behind RAT-Bench (+0.27)**. RAT-Bench wins *today* only because re-id-resistance scoring is its running contribution while **PII-Anon's Tiers 2/3 are precomputed annotations, not a running scorer (finding M6)**.

- **Defensible empty quadrant (where PII-Anon uniquely wins):** *multilingual + re-id-resistance (C1) + pseudonymization-integrity (C2) + anonymization risk+utility (C3) in one CC0 artifact.* **C2 (pseudonymization-integrity) is unoccupied by all 9 competitors.**
- **Where PII-Anon loses:** **C5 real-data validity** (synthetic ceiling; TAB/i2b2/PIIBench beat it) · **C10 adoption** (years behind AI4Privacy) · **C8 agentic realism** (AgentLeak's live per-channel harness is categorically ahead).
- **Must improve, priority order:** (1) **ship real scorers** for C1–C3 (close M6 — *the* reason RAT-Bench out-ranks us today); (2) **real-data correlation study** vs i2b2/TAB (break the C5 ceiling); (3) **powered slices + calibration** (C6); (4) **arms-length governance + leaderboard hygiene** (C7).

---

## Decisive market-research conclusions (→ Requirements)

1. **The moat is J2 (pseudonymization-integrity) + the J1×J2×J3 combination in one multilingual artifact** — not re-id scoring alone (RAT-Bench contests that).
2. **Closing M6 (build running scorers) is the top engineering priority** — it's literally why PII-Anon ranks #2 not #1.
3. **The real-data validation slice is the top credibility fast-follow** (v1.1, co-published) — the universal synthetic-ceiling objection.
4. **Honestly bound the agentic track**; **never collapse anon/pseudo**; **leaderboard hygiene is a must-have**.
5. **Fix the 4 false COMPARISON.md claims + the name-collision** before any external publication.

## Methodology & Epistemic Honesty
- JTBD/Kano are **agent-conducted extrapolations** from §2 personas — real-user job/Kano validation is a Pass-2 follow-up.
- Pugh **verification is live-sourced and conservative** (zero unverifiable papers; 4 existing-doc claims found false). Weights/scores are agent-judgment; a real SME panel reviews the use cases in §4.
- WTP ≈ $0 (CC0); priority is strategic, not revenue.

✅ **Section 3 VALIDATED (2026-05-28)** — proceeding to §4 Use Cases.
