# Discovery §4 — SME Use-Case Review Synthesis

**Stage**: 01-Discovery · Section 4 (panel)
**Date**: 2026-05-28
**Panel**: 5 independent simulated `sme-reviewer` agents (focused panel within the documented 5–9 range; config default 9 — ran 5 distinct high-distinctiveness framings for whole-pipeline cost pacing, flagged at CHECKPOINT 2). Framings: (1) industry incumbent / PII-tool vendor, (2) academic benchmark methodologist, (3) privacy-law / DPO, (4) agentic-security expert, (5) OSS-governance veteran.

**Panel verdict:** all 5 = **REQUEST_CHANGES** → after v2 revisions (folded into `04-use-cases.md`), the blocking findings are resolved → **APPROVE**.

> Epistemic honesty: reviewers are agent-simulated, grounded in live sources (EDPB 2025, ICO, HHS, Staab ICLR-2024, AgentLeak/AgentDojo/InjecAgent, MLPerf/NeurIPS-D&B norms, Presidio eval docs). Not a substitute for a real SME panel (Pass-2).

## Findings & resolutions

| # | Sev | UC | Finding | Resolution in v2 |
|---|---|---|---|---|
| 1 | **CATASTROPHIC** | UC-05 | RRS as implemented is **circular** — a deterministic heuristic over the benchmark's own behavioral-signal labels, not a measured attack; V13 doc carries 2 incompatible RRS defs | Split: **exposure index** (heuristic, relabeled pre-screen) + **measured RRS** (run LLM adversary → empirical recall/precision, Wilson CIs, RRS=1−recall×precision); report index↔RRS correlation |
| 2 | **CATASTROPHIC** | UC-06 | Pseudonymization metrics **not implementable/falsifiable** — no threat model; collision conflates feature vs fault; key-rotation undefined | Added threat model; separated deterministic-linkage vs cryptographic collisions; defined key-rotation pass/fail; **added key/state separation signal** (EDPB Art. 4(5)) |
| 3 | **CATASTROPHIC** | (set) | **No governance/contribution/maintenance UC** — §0 neutrality decision has nothing to trace to | **Added UC-15** (governance & contribution lifecycle); promoted P-host to UC actor |
| 4 | MAJOR | UC-01/04/05/06 | No **scorer I/O contract** (schema adapter, span-matching, adversary version-pinning) | Added cross-cutting v2 requirement + per-UC acceptance (reference Presidio adapter; "vs model@version") |
| 5 | MAJOR | UC-04 | "utility" non-comparable across vendors | Pinned utility probe (fixed task + frozen model); residual-risk declares threat model |
| 6 | MAJOR | UC-02 | Wald CIs at p≈0.98 invalid; 753 bar applied p-independently; no paired statistic | Wilson/Clopper-Pearson; 753 framed as high-recall-regime; McNemar/paired bootstrap; dedup/leakage control |
| 7 | MAJOR | UC-05 | Closed-world matcher over fixed 2,500 candidates under/over-states risk | |C|=N a first-class param; web-like-distractor variant; RRS = relative ranking instrument |
| 8 | MAJOR | UC-10 | Crosswalk implies it can certify a lawful end-state | "**Inform** not back a determination"; anti-case added; GDPR/HIPAA/CCPA columns kept legally distinct |
| 9 | MAJOR | UC-05/09 | Over-claimable RRS figure travels without caveat | **Anti-anonymity caveat attached to the scorer** (every emitted figure carries it) |
| 10 | MAJOR | UC-06 | Misses EDPB "additional information kept separately" | Added key/state separation acceptance signal |
| 11 | MAJOR | UC-08 | "C1–C7 verdicts" Outcome reintroduces the agent-leakage overclaim | Rewrote: harness produces verdicts **by calling** the oracle; PII-Anon owns recognition only |
| 12 | MAJOR | UC-09 | Reusing prose RRS on transcripts → output-only blind spot | Per-channel/per-turn + transcript-distribution caveat; out-of-scope: confident final-output-only "low risk" |
| 13 | MAJOR | UC-11 | Governance "arms-length" asserted, not testable; submission reluctance underestimated | Submission policy + anti-gaming + opt-in publish/private pre-score + config attestation + named arbiter + DOI host |
| 14 | MAJOR | UC-12 | Reuse-only; no contribution pipeline | Added inbound contribution workflow + erratum policy + dated versions + Croissant validates+loads |
| 15 | MAJOR | UC-13 | Rank-correlation under-powered/confounded as sole test | Estimator+MDE+bootstrap CI; domain-matched English slice; Bland-Altman; co-pub governance terms |
| 16 | MINOR | UC-08/09/04/02 | payload shape; OWASP LLM06; reproducible≠valid; co-pub≠validity | Folded into v2 acceptance lines |

## Cross-cutting themes carried to Requirements
1. **Close M6 with a real scorer that has a documented I/O contract + version-pinned LLM-in-the-loop** — the top engineering theme (and why PII-Anon ranks #2 not #1 in §3).
2. **De-circularize RRS** (measured attack, not label heuristic) — protects the headline from peer-review rejection.
3. **Make pseudonymization-integrity falsifiable** (threat model + collision-type separation + key/state separation) — protects the moat.
4. **Operationalize governance (UC-15)** — protects the §0 neutrality decision.
5. **Attach legal/anonymity caveats to scorers, not just the DPO UC** — protects against downstream over-claiming.

✅ **Panel closed; §4 v2 APPROVED (2026-05-28).**
