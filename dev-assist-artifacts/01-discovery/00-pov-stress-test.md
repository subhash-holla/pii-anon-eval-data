# Discovery §0 — POV Stress Test

**Stage**: 01-Discovery · Section 0
**Date**: 2026-05-28
**Method**: 3 independent `pov-stress-test-critic` agents in parallel (adjacent-product skeptic · persona realist · OSS/monetization strategist), each citing live web evidence.

> **Brownfield Mode — Source Signal vs Gaps**
> - **From assessment (cited):** Discovery market-context rated STRONG (`COMPARISON.md`, `docs/PUGH_CHART_ANALYSIS.md`); finding M6 (harness doesn't yet *score* anon/pseudo); M2 (no statistical-power method); o1 (refresh competitors).
> - **Inferred but unconfirmed:** the original POV below (synthesized from README positioning + the two research briefs).
> - **Gaps the user must fill:** confirm the refined POV; decide the governance/neutrality posture (CoI finding).
> - **Does NOT cover:** real-user validation of the POV (Pass-2 follow-up).

---

## Original POV (under test)

> "For ML/NLP researchers and enterprise privacy engineers who can't trust single-score vendor claims, **PII-Anon** is an open benchmark that scores PII **detection, anonymization, and pseudonymization** as three separate, statistically-powered, agentic-aware evaluation tracks — because no public benchmark measures all three end-states with stated confidence, and collapsing 'redaction quality' into one number hides the failures that matter."

All three critics returned verdict **REFINE**. The POV's *spirit* (three separated end-states; distrust of single-score claims; confidence-aware) is sound, but several specific clauses are overclaimed or falsifiable.

---

## Critique 1 — Adjacent-Product Skeptic

**Strongest concern (CATASTROPHIC):** the load-bearing clause *"no public benchmark measures all three end-states with stated confidence"* is likely **falsifiable as of 2026-05-28**. The critic cites a Feb-2026 **RAT-Bench** (attributed to the de Montjoye / Imperial re-identification group) said to cover detection + anonymization + pseudonymization with an LLM re-identification attacker, multilingually — and, unlike PII-Anon (finding M6), to actually *score a system's output*. It also cites established incumbents that each own a track: **PIIBench** (cross-source detection at large scale), **TAB** (anonymization privacy/utility), **PrivaCI-Bench** (contextual-integrity/legal), and agentic-leakage suites (**AgentDojo**, **AgentLeak**).

> ⚠️ **Epistemic caveat:** the specific 2026 citations (RAT-Bench, PIIBench arXiv IDs, AgentLeak, MAMA) are **agent-retrieved and NOT yet independently verified**. They will be properly grounded/verified in §3 Market Research before any external-facing claim is made. The *direction* of the critique is robust regardless, because TAB / AI4Privacy / PII-Bench / PrivaCI-Bench are well-established and already cover ≥1 track each.

**Also overclaimed:** "agentic-aware" rests on 1,000 *static* AI-era records — a category-mismatch against live agent harnesses that exercise tool/memory channels. "Statistically-powered" is currently **unearned** (finding M2: no per-slice sample-size/CI methodology).

**What survives:** (a) the *single-artifact* multilingual superset (60 langs × 65 types × regulatory crosswalk × paired-profile + utility annotations, CC0) that no one ships as one download; (b) **pseudonymization-integrity scoring** (authorized-reversal / collision / referential-integrity) — the least-served quadrant even for the cited competitors.

**Severity:** CATASTROPHIC (the novelty clause must be narrowed before any external publication).

---

## Critique 2 — Persona Realist

**Strongest concern (MAJOR):** the two named personas have **opposite trust criteria**. ML/NLP researchers reward citable methodological novelty; enterprise privacy engineers reward decision validity *on their own data*. A 100%-synthetic benchmark fails the criterion each cares most about: synthetic-only is a known **citation ceiling** for researchers (TAB built its reputation on *real* ECHR court documents precisely because synthetic/de-id benchmarks "may overestimate privacy protection"; an Apr-2026 vendor benchmark is literally subtitled "where PII detection still needs real data"), and enterprise engineers change procurement via POCs on their own corpus, not public leaderboards. Compounding this, finding M6 means the promised three-track *scoring* isn't runnable yet (only the regex baseline, on 500 records).

**What lands:** the **Tier-3 re-identification-resistance** framing (behavioral signals + RRS + paired pseudonymous/real personas) is genuinely novel with no public equivalent — this is the citable hook. And synthetic + CC0 is a real asset *if reframed* as a **safely-shareable, reproducible pre-procurement / research stress harness** (run it before touching real data), not a procurement oracle.

**Severity:** MAJOR (adoption risk; reframe persona + synthetic-data positioning).

---

## Critique 3 — OSS / Monetization Strategist

**Strongest concern (CATASTROPHIC): host-neutrality conflict of interest.** The benchmark's maintainer also builds the commercial `pii-anon-core` privacy control plane, while the POV's hook is *distrust of vendor claims*. A vendor scoring competitors on a benchmark it controls is the very conflict the POV claims to fight. Canonical benchmarks earn authority through **neutral/consortium governance** (MLPerf), a peer-reviewed paper, a maintained **live leaderboard with external submissions**, and reproducibility — none of which exist yet. Today: 0 tests / 0 CI (an *unverified scorer* is disqualifying for a measurement artifact), one partial baseline, no `CONTRIBUTING.md`/governance, and AI4Privacy already holds the incumbent Schelling point (15M+ downloads, 64+ citations).

**Monetization:** certification ("PII-Anon Verified") and paid private eval runs **re-introduce the neutrality conflict** — avoid. Only grant funding and "benchmark as credibility loss-leader for the core product" are compatible with canonical neutrality.

**Severity:** CATASTROPHIC (without arms-length governance, the "trustworthy alternative to vendor claims" positioning collapses).

---

## Refined POV (synthesis)

> "For **ML/NLP privacy researchers and privacy-tool builders** who need a *safely-shareable, reproducible* way to stress-test PII systems before exposing real data, **PII-Anon** is an open (CC0), **independently-governed** benchmark whose distinguishing contributions are (1) **LLM re-identification-resistance scoring** (behavioral signals + RRS + paired pseudonymous/real personas) and (2) **pseudonymization-integrity scoring** (authorized-reversal, collision, referential-integrity) — alongside detection and anonymization-utility tracks — unified into **one multilingual (60-language) artifact** with per-slice confidence intervals. Existing benchmarks cover these tracks **in fragments and mostly in English**; none scores re-identification resistance *and* pseudonymization integrity across languages as one reproducible, leaderboard-backed suite. Enterprise privacy engineers use it to **shortlist** before validating on their own corpus — it is a pre-screen and research instrument, not a substitute for own-data POCs."

### What changed and why
| Original clause | Problem | Refinement |
|---|---|---|
| "no public benchmark measures all three end-states" | Falsifiable (RAT-Bench + incumbents) | "in fragments and mostly in English; none does re-id + pseudonymization-integrity across languages as one suite" |
| "statistically-powered" | Unearned (M2) | kept as a *commitment* ("per-slice CIs"), conditioned on building the stat-power layer |
| "agentic-aware … tracks" | Static records ≠ live agent harness | dropped from headline; agentic-leakage handled as a scoped track, honestly bounded |
| "researchers AND enterprise engineers" (co-primary) | Opposite trust criteria; synthetic fails both | researchers/tool-builders **primary**; enterprise = **downstream shortlist** user |
| (silent on credibility) | Neutrality CoI + unverified harness | "independently-governed", "reproducible", "leaderboard-backed" baked into the value prop |
| (synthetic as liability) | Citation ceiling | reframed as "safely-shareable, reproducible" feature + real-data validation slice on roadmap |

### Hard preconditions the refined POV now *commits the project to*
1. **Close M6** — build a harness that *scores a system's* anonymization/pseudonymization output (not just stores annotations).
2. **Close M2** — per-slice sample-size + CIs so "stated confidence" is real.
3. **Close C1** — CI-verified scoring harness (0→real tests) before v2.0.0.
4. **Governance/neutrality** — arms-length from `pii-anon-core`; open submission + public leaderboard; a methodology paper.
5. **Refresh competitors** (§3) — verify RAT-Bench/PIIBench/PrivaCI-Bench/AgentLeak; update `COMPARISON.md`.

---

## Methodology & Epistemic Honesty

- The three critics are **agent-simulated** (each an independent `pov-stress-test-critic` dispatch) and conducted live web search. Their competitor citations — especially the 2026 ones (RAT-Bench, PIIBench, AgentLeak, MAMA) — are **agent-retrieved and unverified**; they are treated as *signal to verify in §3*, not established fact, and must not appear in external-facing claims until confirmed.
- The critique direction is robust to citation uncertainty because it also rests on well-established artifacts (TAB, AI4Privacy, PII-Bench, PrivaCI-Bench, MLPerf governance norms).
- Real-user validation of this POV is a **Pass-2 follow-up** (assessment §6), not performed here.

**User decisions (section gate, 2026-05-28) — RESOLVED:**
- **(a) POV → ADOPT REFINED.** Lead with re-identification-resistance + pseudonymization-integrity + multilingual breadth as one artifact; researchers/tool-builders are the **primary** persona, enterprise privacy engineers are **downstream shortlist** users; synthetic = safely-shareable pre-screen with a real-data validation slice on the roadmap. This commits the project to closing M6 (build the scorer) and M2 (per-slice CIs).
- **(b) Governance → ARMS-LENGTH NEUTRAL.** PII-Anon is positioned/governed **independently** of the commercial `pii-anon-core`: neutral leaderboard + methodology paper + open external submissions; funded via grants / as a credibility loss-leader. **Certification and paid-eval monetization are explicitly off the table** (they re-introduce the neutrality conflict). This decision propagates into §2 personas (add a neutral-host/maintainer stakeholder lens), §3 positioning, and Stage-3 Design (distribution + leaderboard governance).

✅ **Section 0 VALIDATED (2026-05-28).**
