# Discovery §1 — Motivation & Background

**Stage**: 01-Discovery · Section 1
**Date**: 2026-05-28
**Method**: synthesis of the two user-supplied research briefs (primary evidence base) + §0 critic web findings. External claims trace to the briefs' cited primary sources; agent-synthesized framing is marked as such.

> **Brownfield Mode — Source Signal vs Gaps**
> - **From assessment (cited):** README/DATASHEET motivation (`DATASHEET.md:7-8` — "existing benchmarks are predominantly English-only, limited in entity coverage, lack structured evaluation").
> - **Inferred but unconfirmed:** the "why now" timing argument below (synthesized).
> - **Gaps the user must fill:** none blocking; competitor specifics verified in §3.
> - **Does NOT cover:** primary-source re-verification of every brief citation (the briefs are taken as the evidence base; §3 re-verifies competitor claims).

---

## 1. Why this project exists

PII protection has shifted from a **preprocessing step** to a **system-level control** that must hold across model training, prompt assembly, retrieval, tool calls, agent memory, logs/observability, and completions. Both briefs converge that the hard problem is no longer finding a phone number — it is (a) deciding whether a span is *query-relevant* and should survive, (b) choosing the right **end-state** (anonymize vs pseudonymize) for the use case, and (c) bounding residual re-identification risk under LLM-assisted inference. A benchmark that measures only span-F1 cannot speak to any of these. (Source: `pii_eval_may26.md` Exec Summary + "Evaluation gaps"; `pii_enterprise_landscape_may26.md` Exec Summary.)

## 2. Why now — the macro trends

1. **GenAI + agentic systems widened the privacy boundary.** A single detection miss now leaks into a prompt, a tool call, a memory store, a browser action, or a completion — not just a static dataset. Official guidance (EDPB on LLM privacy; OpenAI/Anthropic/Google SAIF; OWASP) treats prompt injection, sensitive-data disclosure, and over-broad agent permissions as first-class runtime risks. Trace/observability pipelines have become a *new PII datastore* (OpenAI Agents SDK `trace_include_sensitive_data=True` by default; LangSmith recommends Presidio/Comprehend anonymizers). (Source: both briefs, "LLMs and agentic workflows".)
2. **Detection is fragmented and brittle.** When ten public datasets were unified into a cross-source benchmark, published baselines collapsed (the eval brief reports best baselines <0.14 span-F1 with zero recall on most entity types) — today's "leaders" reflect *narrow-domain or synthetic proficiency*, not enterprise robustness. (Source: `pii_eval_may26.md` "Detection landscape".)
3. **Anonymization ≠ pseudonymization is now a regulatory and product fork.** Under GDPR/EDPB, pseudonymized data remains personal data; effective anonymization is an *effectiveness/residual-risk* problem, not "remove direct identifiers." HIPAA (Safe Harbor / Expert Determination + audit controls), FERPA (re-identification codes allowed), CCPA/CPRA (must not be reasonably linkable), and DICOM all push toward **three simultaneous requirements: high-recall detection, risk-appropriate transformation, and accountability artifacts.** (Source: both briefs' regulatory sections — EDPB 2025 pseudonymisation guidance, ICO, HHS, US Dept. of Education, DICOM Part 15.)
4. **Vendor single-score claims are not trustworthy for GenAI privacy controls.** Both briefs (and §0's live findings — e.g., an Apr-2026 vendor benchmark subtitled "where PII detection still needs real data") argue procurement should combine vendor docs with neutral benchmarking and cross-domain suites. This is the wedge for an **independently-governed** benchmark (per the §0 governance decision).

## 3. The evaluation gaps this benchmark targets

The eval brief names four measurement gaps; these become the spine of the project's value proposition (and Stage-2 requirements):

| Gap | What's missing today | This benchmark's response |
|---|---|---|
| **Calibration & uncertainty** | Scores reported, but not calibrated; no per-entity reliability | ECE/Brier + reliability diagrams + abstain-to-review (net-new) |
| **Contextual / query-aware masking** | Most datasets can't tell necessary from unnecessary PII | query-aware scoring (partial data exists; needs scorer) |
| **End-to-end agentic privacy** | Output-only audits miss internal channels (memory, tool args, inter-agent) | scoped agentic-leakage track, honestly bounded |
| **Separate anon vs pseudo evaluation** | Collapsed into generic "redaction quality" | **two distinct metric families** (residual re-id + utility; reversal/collision/referential-integrity) — the project's core thesis |

Plus the cross-cutting methodological gap both briefs stress: **stated statistical power** — per-slice sample sizes and confidence intervals (NIST proportion guidance: ≈753 positives → recall≈0.98 ±1pp), with **stratified enrichment** for rare classes. (Source: `pii_eval_may26.md` "Recommended research program".)

## 4. Why *this* artifact is positioned to fill them

The existing v1.3.0 corpus already has the raw material few others combine in one place: 60 languages, 65 entity types, sensitivity classes, regulatory crosswalk, 4 anonymized variants, paired pseudonymous↔real personas, and behavioral-signal/RRS annotations. The opportunity (and the work) is to turn that **corpus of annotations** into a **reproducible, neutrally-governed scoring suite** with stated confidence — closing assessment findings M6 (build the scorer), M2 (statistical power), and C1 (verified harness). That is the gap between "a big dataset" and "a credible benchmark."

## 5. Honest "why now" risks (carry to §3 / Requirements)

- The synthetic-only nature is a **citation ceiling** until a real-data validation slice exists (TAB's authority came from real ECHR documents).
- Adjacent 2026 benchmarks may already occupy parts of this space (RAT-Bench, PIIBench, PrivaCI-Bench, AgentLeak — **agent-retrieved, to be verified in §3**).
- The incumbent Schelling point (AI4Privacy: 15M+ downloads, 64+ citations) raises switching costs; canonical status requires neutral governance + a paper + a live leaderboard, not just better features.

## Methodology & Epistemic Honesty

- This section's evidence base is the **two user-supplied research briefs**, which themselves cite primary sources (EDPB, NIST, ICO, HHS, OpenAI/Anthropic/Google, and the named benchmark papers). They are treated as the motivation evidence base; competitor specifics are **re-verified in §3** before any external-facing claim.
- "Why now" timing and the "positioned to fill" argument are **agent-synthesized** interpretation, not independent market measurement.
- No live re-crawl was performed in this section beyond §0's findings; retrieval timestamps for competitor claims live in §0 and (forthcoming) §3.

✅ **Section 1 VALIDATED (2026-05-28)** — proceeding to §2 Personas & Workflows.
