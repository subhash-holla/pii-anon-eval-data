# CAP-02 Requirements R2 — Prioritization Interview Guide

**Capability**: CAP-02 — Powered, repeatable, reportable assessment **workflow** (runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0** over a **powered, lattice-stratified sample (default)** / **full corpus (opt-in)** / **smoke (fast)**, with epistemic instrumentation + reporting at every spine stage: `load → sample → run systems → score → rate → report`).
**Stage**: assessment-workflow / 02-Requirements · Phase R2 (prioritization interview instrument)
**Date**: 2026-06-01
**Personas covered**: 6 (3 HIGH / 3 MEDIUM) + 2 folded sub-archetypes
**Total probes**: **83** — **18 persona-agnostic core** + **65 Layer-2** (60 persona-variant: P-acad-deid 11 · P-mlnlp-researcher 11 · P-tool-builder 10 · P-agentic-redteam 9 · P-priv-eng 9 · P-dpo 10 — the P-dpo section is full-depth to close the un-sampled DPO/assurance lens; + 5 sub-archetype: P-tool-vendor 3 · P-complreviewer 2)
**provisional_status**: AGENT_SIMULATED — this is an agent-designed instrument. The interview signal collected with it in R3 is agent-simulated single-session research; real-user interviewing with this same guide is a recommended **Pass-2** activity. Agent-simulated research is **NOT** a substitute for real users.

> **Vocabulary remap (project framing — synthetic PII benchmark).** Persona = assessment/benchmark **consumer**; UC = **Evaluation Scenario**; FR = **Benchmark/Assessment Capability**; NFR = **Quality Attribute**. The "product" these probes refer to is **the CAP-02 assessment workflow**, not a generic app. Probes elicit *behavior with benchmarks and statistical evidence* (how they currently run bake-offs, defend numbers in review, gate releases) — not generic tool opinions.

---

## Methodology

This guide is the R2 prioritization instrument. It is designed (per `references/interview-design.md` + the `interview-guide-author` agent) to resolve the **Discovery Section-8 open questions** — *which* of the 13 open items and the C1–C10 concept-value signals personas actually weight, and *where the locked-but-still-soft decision forks should land*. It follows the canonical **2-layer structure** (persona-agnostic core + per-persona variants) and carries a documented self-bias-check pass.

**This guide IS**: a structured prioritization instrument for eliciting (a) which R1 capabilities/quality-attributes each consumer treats as gating vs nice-to-have, (b) how they work around the gap today (behavior, not opinion), (c) where the open decision-forks (default mode, pre-registration mandate, under-powered reporting, real-data slice, leaderboard hygiene, regulatory crosswalk) should resolve for *their* acceptance.

**This guide is NOT**: a script, a concept-pitch, or a confirmation exercise. Interviewers (R3's `simulated-interviewee` agents; in Pass-2, real interviewers) follow the probe order but let respondent stories drive depth. **Several probes are deliberately disconfirming** — they invite the respondent to reject CAP-02's locked choices.

### What this guide targets (traceability to Discovery)

Every variant probe is anchored to a specific Discovery artifact so R3 signal maps cleanly back to a decision. The five **open decision-forks** the brief named are each owned by a probe family:

| Open decision-fork (Discovery §8 / brief) | Probe family | Anchored to |
|---|---|---|
| **Default mode: powered-representative vs full** | DF-1 (Core P3 + variant probes in P-acad-deid / P-mlnlp / P-tool-builder) | Open Items 3,4 · G2/G3 · UC-16/19 |
| **Pre-registration: opt-in vs mandatory** | DF-2 (Core P3 + P-acad-deid / P-mlnlp / P-tool-builder) | Open Item 6 · UC-18 |
| **Under-powered / shortfall reporting** | DF-3 (Core P3 + P-acad-deid / P-mlnlp) | Open Items 3,5 · UC-16/17/23 |
| **Real-data validation slice priority** | DF-4 (Core P3 + P-acad-deid / P-mlnlp / P-dpo) | Open Item 11 · cycle-1 UC-13 |
| **Leaderboard hygiene / anti-gaming** | DF-5 (P-tool-builder + P-tool-vendor + P-dpo/P-complreviewer) | Open Items 8,9,10 · UC-17/23 |

Secondary forks also probed: AX-pii-anon-005 candidate axiom (Core P3 + P-acad-deid), seam-reconciliation rigor (C1, UC-21), artifact-first reporting register (C7), incremental-resample semantics (C6), file-level provenance (C5), citable/DOI release (C2), scope-statement template (C3), smoke CI-diff reference output (C4).

### Probe design discipline (applied to every probe)

1. **Behavior over opinion** — "Walk me through the last time you…" / "What did you actually do when…" beats "Do you value…". The few opinion probes (concept-engagement layer) are explicitly framed as *reactions to a described workflow*, paired with a behavioral follow-up.
2. **Disconfirmation is mandatory** — each persona variant includes ≥1 probe that invites rejection of a CAP-02 locked choice ("what would make you NOT trust / NOT use this?").
3. **Functional paired with consequence** — statistical-rigor probes are paired with a stakes probe ("what happened when a reviewer / regulator / your CI caught that?").
4. **No leading toward the locked answer** — decision-fork probes present *both* arms neutrally; the respondent picks and justifies. The interviewer never names CAP-02's pre-decided arm.

### Self-Bias Check Findings

A self-review pass walked the full guide for the five canonical bias risks plus two project-specific risks (over-claim priming and the documented sampling gap). Findings and resolutions:

| Bias risk | Probes flagged | Resolution |
|---|---|---|
| **Leading questions** | 9 flagged (early drafts of DF-1/DF-2/DF-3 + 3 acad-deid probes phrased "Wouldn't a powered sample be better than…", "Isn't pre-registration essential…") | All 9 reworded to neutral two-arm forks or open behavioral prompts. Grep confirms zero remaining "wouldn't / shouldn't / don't you think / isn't it / essential / obviously" in probe text. Decision-fork probes now present both arms in randomized order with no valence cue. |
| **Confirmation bias** | Whole guide (the concept is "locked" — risk of only surfacing assent) | Added an explicit **disconfirmation probe to every persona variant** ("What would make you walk away / not cite / not trust this?") and a core probe (#16) inviting the respondent to name the workflow's biggest validity threat. The brief's own G1–G7 anti-over-claim rails are surfaced as *probes*, not assertions (e.g., "When a tool says it 'delegates' vs 'invents' a method — does that distinction change how you cite it?"). |
| **Recency bias** | 6 flagged (probes anchored only to "your last run / this week") | Paired each with a longer-horizon prompt ("…and the most painful version of that you can remember, even years back?"). The status-quo / war-story probes (Core #2–#5) now explicitly span "most recent" AND "most extreme." |
| **Sampling bias (CRITICAL — documented Discovery gap)** | The **P-dpo / compliance-assurance lens was UN-SAMPLED** in the Discovery concept-value cohort (CM-05 refused; `06-concept-value-study-synthesis.md` §Member-refinements + §Caveats(3)). Designing the guide only around the 3 HIGH personas would re-propagate that gap into R3. | (1) Built a **full P-dpo variant section (10 probes)** + the **P-complreviewer assurance sub-archetype** so the EU-AI-Act Art. 10/11 (Aug-2026) lens is first-class in R3, explicitly closing the cohort gap. (2) Added a **sub-archetype stratification plan** so R3 dispatches an interviewee for each folded lens (P-tool-vendor gaming-incentive; P-complreviewer external-assessor). (3) Flagged in the R3 handoff that DPO/assurance signal in R3 is *first contact* for this lens, not re-confirmation — and remains a Pass-2 real-user priority regardless of R3 result. |
| **Anchoring (probe order pre-loads conclusions)** | Decision-fork probes risked anchoring on whichever arm was stated first; Layer-1 concept-engagement (P3) risked priming Layer-2. | Documented a **canonical order** (below) for reproducibility, but instruct R3 to **randomize the two arms within each decision-fork probe** and to **randomize Layer-2 probe order within a persona**. The concept-engagement block (#11–#15) is placed *after* the status-quo + forces blocks so respondents anchor on their own workflow first, not on CAP-02's framing. |
| **Over-claim priming (project-specific)** | 4 flagged (probes that stated CAP-02 capabilities as facts — "the powered sampler that hits every tier", "the non-strippable caveat") risked the interviewer making the tool's anti-over-claim *claims* for the respondent. | Reworded so the interviewer describes a *capability shape* neutrally and asks the respondent to judge sufficiency ("Suppose a benchmark reported X with a stated power class per slice — does that change whether you'd cite it, and why / why not?"). Aligns with G1 (credit consumed machinery) / G6 (integration not method novelty) / G7 ("lattice-stratified," not "representative of population") — these rails are tested, not asserted. |
| **Acquiescence / social-desirability (project-specific)** | Statistical-rigor probes risk respondents over-claiming their own rigor ("yes I always pre-register / always report CIs"). | Converted to **last-instance behavioral evidence** ("In your last published/shipped comparison, did a CI or paired test actually appear? Walk me through that table.") and added a stakes counter-probe ("Have you ever shipped/published a number you later felt was under-powered? What happened?"). |

The self-bias-check finding is part of the instrument's epistemic record; R3 carries it forward.

---

## Layer 1: Persona-Agnostic Core (18 probes)

Every interviewee answers these, regardless of persona — they enable cross-persona comparison on the open decision-forks. **Canonical order below; R3 randomizes the two arms inside each fork probe.**

### Phase 1 — Status quo & workflow context (5 probes)

1. "Walk me through the last time you needed a defensible comparison between two PII / de-identification systems. What did you do, step by step — from getting the data to the number you reported?" *(establishes the `load → … → report` spine in their own words; behavioral)*
2. "In that comparison — and in the most painful version of this you can remember, even from years back — what part did you trust least, and why?" *(push + recency-debias; surfaces the validity threat they already feel)*
3. "When the corpus you needed was too small to make a per-language or per-subgroup claim, what did you actually do? Cut the claim, caveat it, or report it anyway?" *(behavioral; sets up DF-3 under-powered fork without naming it; grounds Open Items 3,5)*
4. "Of everything in that workflow, which single step costs you the most — time, compute budget, or credibility with whoever reviews your work?" *(elicits the real cost-binding constraint — the heart of DF-1 default-mode; G2/G3)*
5. "If you could fix exactly one thing about how PII-system comparisons are run and reported in your field, what would it be?" *(pull / magic-wand; open)*

### Phase 2 — Forces: push / pull / habit / anxiety (5 probes)

6. "When you adopt an external benchmark or harness someone else built, what makes you trust its numbers enough to cite or ship against them?" *(pull toward CAP-02's credibility attributes — without naming them)*
7. "What would you have to give up — habits, in-house scripts, control over the metric — to move your comparisons onto a shared external harness?" *(habit / switching cost)*
8. "When a benchmark is built on **synthetic** data, what's your honest concern about leaning on its results?" *(anxiety; the synthetic-only ceiling — the universal objection from `personas.md` §cross-persona-synthesis #1; sets up DF-4)*
9. "Think of an evaluation tool or leaderboard you tried and then stopped trusting. What was the moment you lost confidence?" *(disconfirming; surfaces anti-gaming / hygiene triggers for DF-5)*
10. "Think of an evaluation method or harness you've relied on for a year or more. What keeps you coming back to it?" *(habit / loyalty; surfaces the real must-haves)*

### Phase 3 — Concept engagement & the open decision-forks (8 probes)

> Interviewer frames CAP-02 once, neutrally, then probes. **Neutral framing to read:** *"There's a workflow that runs an existing PII-system tournament over a public synthetic corpus. By default it scores a right-sized stratified sample rather than the whole corpus; it can attach a confidence interval to every number, run a paired statistical test before declaring one system better, report whether its rankings have stabilized, and carry a fixed 'this is synthetic' caveat on the output. Full-corpus and fast-smoke modes also exist."* Then:

11. "What's your first reaction to that — and concretely, where would it fit (or not fit) in the workflow you described earlier?" *(reaction paired with behavioral fit)*
12. **[DF-1 · default mode]** "Two ways a workflow like this could default: (A) score a powered, stratified **sample** and label its power, or (B) score the **whole corpus** every time. For the number you'd actually cite or gate on, which default do you want — and what makes the other one wrong for you?" *(both arms; R3 randomizes A/B order; Open Items 3,4 · G2/G3)*
13. **[DF-2 · pre-registration]** "Suppose the workflow could require you to commit the sample, seed, systems, and full analysis plan *before* any system is scored. Should that be **mandatory for every run**, or **opt-in rigor** you turn on when you need it? Walk me through a run where you'd want it on, and one where the requirement would just get in your way." *(both arms; Open Item 6 · UC-18)*
14. **[DF-3 · under-powered reporting]** "When a particular slice doesn't have enough data to hit its statistical target, what should the report do — **omit that slice**, **show it greyed/flagged as under-powered with the exact shortfall named**, or **show it like any other number**? Has the way a tool handled this ever helped or hurt you with a reviewer?" *(three arms; Open Items 3,5 · UC-16/23; paired with a stakes probe)*
15. **[DF-4 · real-data slice]** "If this synthetic benchmark also published a study showing its rankings track a small **real** corpus (say i2b2 / TAB), how much would that change what you'd use it for — and would you wait for that before citing the synthetic numbers, or use them now with a caveat?" *(Open Item 11 · cycle-1 UC-13; the named credibility unlock — probed as priority, not assumed)*

16. "What's the single biggest reason a skeptical reviewer, regulator, or competitor could dismiss results from a workflow like this — and what would have to be in the output to disarm that?" *(disconfirming; surfaces the over-claim rails G1–G7 as the respondent's own concerns)*
17. **[AX-pii-anon-005 candidate]** "Imagine a rule that said: *no number gets published from this workflow unless it carries a confidence interval, a paired test where a comparison is claimed, a statement of whether rankings converged, full provenance, and the synthetic-only caveat.* Is that the right bar, too strict, or not strict enough — for your use?" *(tests the candidate axiom directly; both directions invited)*
18. "Anything I should have asked about how you'd judge, trust, or reject a workflow like this — but didn't?" *(blind-spot wrap)*

---

## Layer 2: Persona-Variant Probes

> R3 randomizes probe order within each section. Each section opens with workflow/tooling detail, moves through the persona's owned UCs/PGOs and the decision-forks they gate, and closes with a mandatory disconfirmation probe.

### P-acad-deid — Academic De-identification Researcher · HIGH (11 probes)

*Owns PGO-acaddeid-01/03; primary on UC-18/19; gates citation legitimacy. Load-bearing objection: synthetic citation ceiling.*

1. "In your most recent published de-id evaluation, what corpus did you use, and what was the largest claim you *couldn't* make because the corpus was too small?" *(grounds PGO-acaddeid-01; behavioral; i2b2≈1.3K / TAB≈1.3K reality)*
2. "Pull up — in memory — the results table from that paper. Did a confidence interval or significance test actually appear next to the headline numbers? If not, why not?" *(acquiescence-debiased; behavioral evidence of current rigor)*
3. "Has a reviewer ever pushed back on an **under-powered subgroup claim** in your work? What did you change?" *(DF-3 from the citation side; stakes probe)*
4. **[DF-4]** "You've said synthetic data has a citation ceiling. Concretely: with a synthetic benchmark *alone*, what's the strongest sentence you'd write about a system in a paper? And what would a real-corpus correlation study let you upgrade that sentence to?" *(Open Item 11; quantifies the unlock as the persona sees it)*
5. **[DF-2]** "For a result you intend to *publish*, would you want pre-registration enforced by the workflow, or do you manage that yourself? Has a venue or reviewer ever required proof a comparison wasn't chosen after the fact?" *(UC-18; opt-in vs mandatory from the publishing side)*
6. "When you re-run someone else's evaluation to check it, what's the smallest thing that, if missing, makes it un-reproducible for you?" *(byte-reproducibility / manifest; PGO-acaddeid-03; AX-002)*
7. **[C2 · citable release]** "When you cite a dataset or harness, is a GitHub commit SHA enough, or do you need a DOI / formal release? Walk me through the last time citation friction stopped you from using something." *(C2; behavioral)*
8. **[C7 · reporting register]** "If this produced a results table, what format would actually drop into your paper — and is product-style 'ship / ship-with-caveats' language a help or a problem in a peer-review context?" *(C7 artifact-first register)*
9. **[C1 · seam reconciliation]** "If a benchmark quietly changed which dataset version it loaded between two of your runs, how would you even notice — and how badly would that burn you?" *(UC-21 / C1 as a *validity threat* the persona names, per CM-01/06)*
10. **[G1/G6 over-claim rail]** "If a workflow says it *reuses* an existing tournament engine and *reuses* a published power method rather than inventing new ones, does that make you more or less likely to trust and cite it?" *(tests G1/G6 as the respondent's own preference)*
11. **[DISCONFIRM]** "What would make you decide this benchmark is *not* citable in your work — even as a supplementary stress-test?" *(mandatory rejection probe)*

### P-mlnlp-researcher — ML/NLP Privacy Researcher · HIGH (11 probes)

*Primary on UC-16/17/21/22/23; gates v1. The powered+CI+paired+reproducible bar IS this persona's acceptance bar.*

1. "Walk me through the last time you ran two PII methods head-to-head for a paper or report. Where did the harness come from — yours, borrowed, or hand-rolled per project?" *(status quo; PGO-researcher-01)*
2. "In that head-to-head, how did you decide one system was actually better than the other — eyeballing the F1, a significance test, multiple seeds?" *(UC-17 paired-test gating; behavioral)*
3. **[DF-1]** "When LLM-adversary cost or runtime binds, would you rather a workflow score a powered **sample** and tell you its power, or always score the **full corpus**? Where's the line where sampling becomes unacceptable for you?" *(Open Items 3,4 · G2/G3 — the cost-bound persona)*
4. **[DF-3]** "If a per-slice number came back labeled 'UNDER-POWERED, short by N positives' — is that more useful to you than no number, or does a flagged-but-shown number create its own problems?" *(UC-16/17/23; both directions)*
5. "How do you handle the fact that a single sample draw is itself random — do you run multiple seeds, report rank stability, or treat one draw as the answer?" *(UC-17 `seed_variance_scope` / Kendall-τ; behavioral)*
6. **[DF-5]** "The corpus here is public and synthetic, so a system could be trained on it. As a *consumer* of someone else's leaderboard entry, what would you need disclosed to trust their rank — and what would make you suspect train-on-test inflation?" *(Open Items 8,9 · UC-17 `contamination_status`)*
7. "Pseudonymization and anonymization — do you currently score them with the same metrics or different ones? What breaks when they're collapsed into one 'redaction quality' number?" *(AX-004; UC-17 `scoring_family`)*
8. **[C4 · smoke CI-diff]** "When you iterate on a recognizer, what's your inner-loop check that you didn't break the pipeline — and how fast does it have to be to actually get used?" *(C4 / UC-20; behavioral)*
9. **[C8 · adversary-pluggability — scope check]** "Some of what you might want here is re-identification / attack-resistance scoring with a frontier model you name yourself. If a v0.1 explicitly says 'detection/anonymization power only, re-id is roadmap,' does that honest bound work for you, or is re-id table-stakes?" *(probes the OUT-of-scope boundary honestly; C8 routes to cycle-1 re-id track; tests MEI-06 acceptance)*
10. **[DF-2]** "For a leaderboard-grade result, should pre-registration be required or optional? Would a mandatory pre-reg step change whether you'd bother submitting at all?" *(UC-18; adoption-friction angle)*
11. **[DISCONFIRM]** "What's the failure — in the stats, the sampling, the reporting, or the provenance — that would make you tell a colleague *don't* use this?" *(mandatory rejection probe)*

### P-tool-builder — Privacy-Tool Builder / OSS Maintainer · HIGH (10 probes)

*Primary on UC-20/23; co-owner UC-17/21. Acceptance cohort for leaderboard-hygiene + reproducibility + CI-gate attributes.*

1. "How do you catch a detection regression in your tool today — a test set in CI, manual spot-checks, user bug reports?" *(status quo; PGO-builder-01)*
2. "Walk me through your CI for the recognizer. If you added an external corpus gate, what's the slowest it could be before you'd rip it out?" *(UC-20 smoke; C4 reference-diff; behavioral)*
3. **[C4]** "Would a tiny deterministic smoke run with a committed reference output you can byte-diff in CI actually fit your pipeline — or do you need the full powered run to trust a gate?" *(C4 / UC-20; both arms)*
4. **[DF-5]** "If you published a rank on a neutral leaderboard, what submission rules would make *you* trust the leaderboard — held-out labels, blind submission, provenance stamps? And which of those would annoy you as a submitter?" *(Open Items 8,9 · UC-23 hygiene — the persona whose own incentive is the forcing function)*
5. **[DF-1]** "For a number you'd put in your model card or README, do you want it from a powered sample or the full corpus? Does 'sampled but powered' read as credible to *your* users?" *(Open Item 4; publication-credibility angle)*
6. "When you publish a detection score, what makes it credible to *other maintainers* — reproducibility, the corpus, the metric, the significance test?" *(PGO-builder-02; behavioral)*
7. "The de-id world cares about the recall/precision trade — a missed SSN vs over-redaction. Do you report an operating point, a recall-priority Fβ, or just F1 today?" *(UC-23 Fβ/AUPRC; DOM-02 false-positive tax)*
8. **[C6 · incremental re-run]** "When your test corpus grows — say you add 10k examples — do you re-run everything or extend incrementally? What would you expect a powered harness to do there?" *(C6 / UC-16/21 incremental-resample semantics; open question)*
9. **[C1]** "If the harness you gate on silently loaded a different dataset version than last release, how would that surface in your CI — and how much would it cost you?" *(UC-21 regression contract from the CI-consumer side)*
10. **[DISCONFIRM]** "What would make you remove this gate from your CI after adding it — false reds, slowness, an un-credible number?" *(mandatory rejection probe)*

### P-agentic-redteam — Agentic-Security Red-Teamer · MEDIUM (9 probes)

*Honestly bounded: CAP-02 = recognition oracle + payload seed + RRS-on-transcripts, NOT a live agent-leakage benchmark. Probe the boundary, not a v1 claim.*

1. "Walk me through how you test a live agent for PII leakage today — what's your harness, and what do you measure per channel?" *(status quo; AgentDojo/AgentLeak substrate; PGO-redteam-01)*
2. "When you need to decide 'did PII actually cross this channel?', what's your detection oracle right now — regex, a model, manual?" *(probes the recognition-oracle role CAP-02 *can* fill)*
3. "If a labeled synthetic PII corpus could seed reproducible exfiltration payloads with known ground truth into your runs, would that save you work — or is payload generation not your bottleneck?" *(PGO-redteam-02; behavioral)*
4. **[scope boundary — honest]** "A static synthetic-corpus benchmark is **not** a live agent-leakage benchmark. If a tool was explicit about that boundary and positioned itself only as a recognition oracle + payload seed, would that honesty earn your trust or read as a limitation?" *(tests the §2 anti-attribute / CM-04 boundary; disconfirming-friendly)*
5. "What would make you *distrust* a PII-recognition oracle you called inside your harness — false negatives on adversarial strings, latency, multilingual gaps?" *(quality bar for the oracle role)*
6. **[C9 · oracle API]** "If you called a recognition oracle at harness volume, what latency and throughput would it need to hit, and would you need those numbers published before you'd wire it in?" *(C9 / routes to cycle-1 UC-08 oracle track; UC-23 machine-readable throughput)*
7. "Multilingual and homoglyph/BiDi adversarial inputs — does your current oracle handle those, and how would you test a new one on them?" *(adversarial breadth; behavioral)*
8. "Where's the line for you between 'useful recognition layer' and 'I need a live multi-agent harness for this' — what can a static benchmark never give you?" *(re-derives the honest bound from the persona)*
9. **[DISCONFIRM]** "What framing or claim from a benchmark like this would make you dismiss it as not built for red-teamers?" *(mandatory rejection probe — CM-04 warned any 'agent-leakage benchmark' framing loses the community)*

### P-priv-eng — Enterprise Privacy / Platform-Security Engineer · MEDIUM (9 probes)

*Downstream consumer: pre-screen finalists + borrow the harness scaffold. Primary on UC-22.*

1. "Walk me through how you shortlist PII/DLP tools before a POC today. What evidence narrows the field?" *(status quo; PGO-priveng-01)*
2. "The false-positive tax — high recall, low precision floods reviewers with over-redactions. Have you been burned by a single-F1 score that hid this? What did you need to see instead?" *(UC-23 operating-point view; DOM-02; stakes probe)*
3. "When you've stood up an internal eval on your *own* data, what did you have to build from scratch that you wish you could have borrowed?" *(PGO-priveng-02; behavioral — the harness-scaffold pull)*
4. **[reuse]** "If you could lift a scaffold — interval estimation, paired tests, power tiers, seeded manifest, per-stage run-records — into your internal eval, which piece would save you the most, and which would you still rebuild yourself?" *(PGO-priveng-02; UC-22 observability)*
5. **[UC-22]** "Per-stage receipts of what data, which version, how many records, under which code commit each step touched — is that audit trail something you need, or overhead for your use?" *(UC-22 run-record; both directions)*
6. "How hard a line is it for you that a *synthetic* leaderboard is never the procurement decision — only a pre-screen? What stops a colleague from over-trusting it?" *(persona's hard bounce; behavioral)*
7. "Do you need a coverage map — the 63 entity types, multilingual breadth — as a checklist before writing detection policy? Where do you get that today?" *(PGO-priveng-03; UC-16 coverage envelope)*
8. **[C5 · file-level provenance]** "When you hand an evaluation result to security or audit internally, does each *file* need to carry its own provenance, or is a run-level manifest enough?" *(C5 / UC-22)*
9. **[DISCONFIRM]** "What would make this useless as a pre-screen for you — un-transferable numbers, missing coverage, no operating-point view?" *(mandatory rejection probe)*

### P-dpo — Compliance / Privacy Counsel / DPO · MEDIUM (10 probes)

> **SAMPLING-GAP CLOSURE.** This lens was **un-sampled** in Discovery (CM-05 refused; `06-concept-value-study-synthesis.md`). This section is intentionally full-depth so R3 makes *first contact* with the DPO/assurance lens. R3 signal here is first-contact, **not** re-confirmation of the cycle-1 priority — flag accordingly in synthesis.

1. "When a technical team hands you an evaluation to support an 'anonymized vs pseudonymized' determination, what do they give you today — and what's missing for you to actually rely on it?" *(status quo; PGO-dpo-01; EDPB 2025 anon≠pseudo)*
2. "Have you ever had to push back on output marketed as 'anonymized' that was really pseudonymized? What evidence would have settled it?" *(AX-004; stakes probe)*
3. "Span-F1 says nothing about residual re-identification risk. For a motivated-intruder / 'very small risk' argument, what *would* you need quantified?" *(PGO-dpo-02; behavioral)*
4. **[AX-004]** "Does scoring anonymization and pseudonymization with *separate* metric families map to how you reason about legal end-states — or is that distinction not how you think about it?" *(tests AX-004 from the legal side; both directions)*
5. **[DF-5]** "Would a residual-risk figure derived from *synthetic* data be admissible as evidence scaffolding for you — and would a real-corpus correlation study change that?" *(Open Item 11 from the assurance angle — the un-sampled lens on the real-data unlock)*
6. **[DF-5 hygiene]** "For evidence you'd file or accept, does it matter who ran the benchmark — would a *vendor's own* self-benchmark be admissible, or do you need an arms-length / neutral one?" *(Open Items 9,10 · neutrality; external-assessor bounce)*
7. **[regulatory crosswalk — author-or-defer]** "Do you need a class-by-class GDPR / HIPAA / CCPA crosswalk mapping a transformation's output to obligations — or is that something your team builds separately?" *(PGO-dpo-03 · Open Item 10 — flagged weak-coverage; resolves author-vs-defer)*
8. **[C3 · scope-statement template]** "If the workflow shipped a ready-to-paste synthetic-only scope/limitations statement for a DPIA or compliance report, would you use it — or does it have to be your own words for it to be defensible?" *(C3)*
9. **[EU AI Act driver]** "The Art. 10/11 conformity-assessment bulk effect lands Aug-2026 — versioned docs, data provenance, test results as filed evidence. Is that timeline shaping what you'll need from evaluations like this, and how soon?" *(P-complreviewer driver; time-sensitivity)*
10. **[DISCONFIRM]** "What about a synthetic-data benchmark would make it inadmissible or useless in a compliance file for you?" *(mandatory rejection probe)*

---

## Sub-Archetype Variant Probes (folded lenses — governance / assurance)

> These are NOT new gating consumers; they are folded under their parent persona (`personas.md` §sub-archetypes). R3 dispatches one interviewee per sub-archetype (see stratification plan) so the **gaming-incentive** and **external-assessor** lenses are explicitly represented — directly supporting DF-5 (leaderboard hygiene) and the sampling-gap closure.

### P-tool-vendor (← P-tool-builder) — Leaderboard Submitter, commercial motive (3 probes)

*The gaming-incentive lens — the forcing function for leaderboard hygiene (Open Items 8,9).*

1. "If you submitted your commercial detector to a neutral leaderboard for a citable rank, what would you want to *avoid* disclosing — weights, training data, the held-out set?" *(PGO-tool-vendor-02; surfaces the gaming surface honestly)*
2. "What submission rule would feel *fair* to you as a vendor but still stop a competitor from gaming the rank?" *(blind/provenance submission; UC-18 lineage)*
3. **[DISCONFIRM / hard bounce]** "Would you ever present a synthetic-leaderboard rank to a customer as a procurement guarantee — and what should the leaderboard do to stop that being misread?" *(tests the hard-bounce: synthetic leaderboard ≠ procurement oracle)*

### P-complreviewer (← P-dpo) — Audit & Assurance Reader / external assessor (2 probes)

*Closes the un-sampled-assurance gap from the attestation side (Art. 11 Aug-2026).*

1. "As someone who must *attest* a PII control was soundly evaluated, what's the minimum an evaluation artifact must contain for you to accept it without sending it back for rework?" *(PGO-complreviewer-01; Article-11-fileable)*
2. **[external-assessor neutrality]** "Where's your line between an evaluation you'd accept and one you'd reject as not arms-length — and does a non-strippable synthetic-only caveat on every number help or hurt that judgment?" *(PGO-complreviewer-02; neutrality + AX-001/003)*

---

## Sub-Archetype Stratification Plan (for R3 dispatch)

The orchestrator dispatches **3 interviewees per HIGH persona and 1–2 per MEDIUM persona / sub-archetype**, stratified across sub-archetypes so distinct angles (and the documented gap) are covered. Each interviewee answers all 18 Layer-1 core probes + only their persona's Layer-2 section (+ sub-archetype probes where applicable).

| Persona | Sub-archetype 1 | Sub-archetype 2 | Sub-archetype 3 |
|---|---|---|---|
| **P-acad-deid** (HIGH) | Clinical/PHI de-id (i2b2/n2c2 lineage) | Legal/policy de-id (TAB lineage) | Replication-desk / reproductions (CM-06 lens) |
| **P-mlnlp-researcher** (HIGH) | Reproducibility-first benchmarker (CM-01 lens) | Re-identification specialist (CM-03 lens — probe scope boundary) | Methods author chasing a leaderboard entry |
| **P-tool-builder** (HIGH) | OSS maintainer (Presidio/GLiNER class) | Healthtech ML eng who ships AND screens (CM-02 overlap) | **P-tool-vendor** (commercial submitter — +3 sub-archetype probes) |
| **P-agentic-redteam** (MEDIUM) | Enterprise agentic red-teamer (CM-04 lens) | Runtime-gateway privacy eng (adjacent no-brainer) | — |
| **P-priv-eng** (MEDIUM) | Pre-screen / procurement-support | Internal-harness builder (scaffold-borrower) | — |
| **P-dpo** (MEDIUM — **gap-closure priority**) | DPO / privacy counsel (end-state determination) | **P-complreviewer** internal audit (+2 sub-archetype probes) | **P-complreviewer** external assessor (+2 sub-archetype probes) |

**Indicative R3 dispatch:** 3 (acad-deid) + 3 (mlnlp) + 3 (tool-builder, incl. vendor) + 2 (redteam) + 2 (priv-eng) + 3 (dpo, incl. both complreviewer angles) = **~16 interviewees**. Final count per `developer-assistant.yaml.cohorts` (4B default 10) is the orchestrator's call; the **minimum non-negotiable is ≥1 P-dpo and ≥1 P-complreviewer interviewee** to close the documented sampling gap.

---

## Probe Selection by Persona

For each interviewee, the R3 `simulated-interviewee` agent answers:
- **All 18 Layer-1 core probes** (mandatory — enables cross-persona comparison on the decision-forks).
- **Only their persona's Layer-2 section** (skip other personas' sections).
- **Sub-archetype probes** where their stratification cell carries them (P-tool-vendor +3; P-complreviewer +2).
- Adjust depth based on response richness; **never skip the mandatory disconfirmation probe**.

---

## Open Items for Future Iterations

| Item | When to revisit |
|---|---|
| **DPO/assurance signal is first-contact (CM-05 gap), not re-confirmation** — even a clean R3 result here does not validate the cycle-1 P-dpo priority; real-user DPO interviews remain a Pass-2 must. | After R3 synthesis + Pass-2 |
| Re-identification / RRS scope boundary (PGO-acaddeid-02 / researcher-02 / builder-03; C8) — probed for *acceptance of the bound*, not for re-id requirements. If R3 shows the bound is unacceptable to a HIGH persona, escalate to the scope decision. | After R3 synthesis |
| Regulatory-crosswalk author-vs-defer (PGO-priveng-03 / dpo-03 · Open Item 10) — probe #P-dpo-7 resolves direction; carry the verdict into FR authoring. | After R3 synthesis |
| Incremental-resample semantics (C6 · UC-16/21) — probe #P-tool-builder-8 surfaces demand; may need an FR or an explicit defer-with-rationale. | After R3 synthesis |
| Any probe that surfaces ambiguous or contradictory signal across personas on a decision-fork (esp. DF-1 default mode) — the locked default stays, but the named shortfall / labelling requirements may need sharpening. | After R3 synthesis |

---

## Methodology & Epistemic Honesty

- This is an **agent-designed instrument**; a self-bias-check pass was applied and documented (above). The interview signal collected with it in **R3 is agent-simulated** single-session research — directional, not confirmatory or saturated. **Agent-simulated research is NOT a substitute for real users**; real-user interviewing with this same guide is a recommended **Pass-2** activity, and the R3 `simulated-interviewee` agents may refuse to answer probes for which they lack a grounded basis rather than fabricate.
- **Sources read this session (canonical Discovery artifacts):** `01-discovery/discovery-report.md` (§8 Open Items 1–13, G1–G7 rails, C1–C10), `01-discovery/04-use-cases.md` (UC-16..23), `01-discovery/personas.md` (6 personas + sub-archetypes), `01-discovery/06-concept-value-study-synthesis.md` (C1–C10 + the CM-05 / un-sampled-DPO gap), `02-requirements/_bridge/uc-pgo-map.md` (R0 PGO catalogue + orphan scan), `assessment-workflow/MANIFEST-capability.md` (ID offsets + AX-pii-anon-005 candidate). Probe traceability is to these artifacts.
- **Decision-forks are presented neutrally** — the guide never names CAP-02's pre-decided arm to the respondent; the locked architecture is tested for *consumer acceptance*, not asserted. The G1–G7 anti-over-claim rails appear as probes (what would the consumer dismiss?), not as claims.
- **Numbering:** this guide introduces no UC/FR/NFR IDs; it references existing UC-16..23, PGO-*, C1–C10, Open Items 1–13, and the candidate AX-pii-anon-005 only. ID offsets (FR→030, NFR→019) are reserved for the FR/NFR authors downstream.

✅ **R2 prioritization interview guide authored (2026-06-01).** 2-layer instrument — **18 persona-agnostic core probes + 65 Layer-2 probes (60 persona-variant + 5 sub-archetype) = 83 total**; all five Discovery §8 decision-forks (default mode, pre-registration mandate, under-powered reporting, real-data slice, leaderboard hygiene) owned by named probe families; self-bias check applied (incl. the CM-05 / un-sampled-DPO sampling-gap closure via a full P-dpo + P-complreviewer section); `provisional_status: AGENT_SIMULATED`. Ready for R3 (`simulated-interviewee` dispatch).
