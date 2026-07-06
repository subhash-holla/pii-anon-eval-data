# Discovery §5 — Concept Value Study Synthesis

**Stage**: 01-Discovery · Section 5
**Date**: 2026-05-28
**Method**: 15 simulated `concept-value-interviewer` agents (full-rigor cohort), each a distinct cohort member across the 6 persona archetypes + sub-variations, running the 30-question protocol. **Agent-simulated — NOT a substitute for real users; a real concept-value study is a Pass-2 follow-up.**

> Cohort: 3 researchers (junior PhD, senior industry, re-id specialist), 3 tool-builders (Presidio-OSS, HF model author, commercial SDK), 2 acad-de-id (clinical, legal/education), 2 red-teamers (frontier-lab, enterprise), 3 priv-engs (runtime-gateway, batch-platform, fintech/healthtech), 2 DPOs (EU GDPR, US HIPAA/CCPA).

## Value scores (1-10)
Range 6–8; median ~6–7. Enthusiasm medium→high. **The score is almost entirely gated by ONE factor**: the synthetic-only citation ceiling caps most personas at 6–7; nearly every persona says the **real-data validation slice (UC-13) lifts them to 8.5–9**.

## Convergent confirmations (validate the locked direction)
1. **Pseudonymization-integrity (UC-06) = the universal delighter / moat.** Every persona that touches it calls it an empty quadrant with no competitor; the clinical de-id researcher and DPOs would adopt it **with no caveats and no real-data slice required**. Strongest, most uncontested signal in the study.
2. **Synthetic-only ceiling is the universal cap.** Researchers/academics won't headline-cite; DPOs can't use synthetic RRS as primary DPIA evidence; commercial vendor "will integrate internally in 60 days but won't stake a marketing claim" until UC-13. → **UC-13 is the #1 fast-follow.**
3. **Neutral governance (UC-15) is a hard gate, not a nicety.** "If GOVERNANCE.md reads like MLPerf/NeurIPS-D&B, I'm in; if it reads like a company's responsible-AI page, I'm out" (senior researcher). DPOs: a vendor-captured benchmark is **un-citable in a DPIA**.
4. **The anti-anonymity caveat must be NON-STRIPPABLE from every emitted artifact** (DPOs + academics, emphatic): "an engineer will strip it and hand me 'PII-Anon certified: anonymized' — that is not hypothetical, it will happen." → strengthen beyond UC-05/10: caveat embedded in the output format itself.
5. **Adversary version-pinning + candidate-set-size |C| disclosure** for RRS is a hard reproducibility requirement (researchers, re-id specialist, academics).
6. **Scorer I/O contract + Presidio reference adapter must SHIP in v1** (tool-builders, priv-engs): without it the oracle/CI integration is "a documentation promise, not a drop-in" → deprioritized.
7. **Agentic oracle framing is honest + useful, NOT a fig leaf** — IF it ships a callable API + reference stub and the live-harness adapter hits all 7 AgentLeak channels. Red-teamer: "if the README ever says 'agent-leakage benchmark', I'm out and the red-team community follows."

## NEW signals — forward-deferred to Requirements (per the §5 backward-iteration vs forward-deferral rule, these are additive; they don't invalidate §4, so they enter Stage-2's input queue)
| # | New signal | Source persona(s) | Becomes (Requirements) |
|---|---|---|---|
| N1 | **Coreference-chain + quasi-identifier-COMBINATION scoring** — atomic-span scoring misses contextual/indirect identification ("the student who transferred from Lincoln High in 2019"), the dominant hard-case class in legal/education/IRB de-id | legal/education de-id (strong) | candidate **new UC + FR**; likely a v1.1 quasi-identifier-combination slice + coreference-as-a-unit scoring |
| N2 | **Cost-aware / cheap-adversary mode** — full paired-persona LLM-adversary run may cost \$50–200/eval; solo authors need a cost estimate + a deterministic/rule-based adversary option | HF model author, gateway eng | NFR (cost budget) + FR (pluggable cheap adversary) |
| N3 | **Adversary-pluggability** (not just version-pinning) — researchers must name a specific frontier model in their threat model | senior researcher | FR refinement to UC-05 |
| N4 | **Inference latency/throughput dimension + streaming/chunked input** — accuracy-only is "half the picture" for sub-300ms runtime fit | runtime-gateway eng | NFR + a runtime-perf reporting FR |
| N5 | **Financial-sector PII coverage** confirm/expand (IBAN/SWIFT/instrument IDs + account+routing co-occurrence) | fintech/healthtech engs | coverage FR / taxonomy check |
| N6 | **Cross-turn fragmented-leakage payload type** (partial name turn 1 + partial DOB turn 4, reassembled turn 7) | enterprise red-teamer | agentic payload FR (v1.x) |
| N7 | **Per-language sample-size table** — "60 languages means nothing if 50 have <200 positives" | senior researcher | NFR (per-slice power transparency) |
| N8 | **"Make correct citation frictionless"** — ready BibTeX + citation template + a claims-policy on what synthetic-only supports; PhD students are the citation-gravity engine | junior PhD | docs/distribution FR (UC-12) |
| N9 | **PCI-DSS column + legally-distinct regime columns at the DISPLAY layer** (not just schema) | fintech, US counsel | FR refinement to UC-10 |

## Persona refinements (no backward iteration needed — all are sub-archetypes of existing personas)
- **P-priv-eng splits into 3 sub-types**: runtime-gateway (latency/calibration/query-aware), batch-scaffold (coverage/regression/pseudo), dpo-bridge (regulatory crosswalk/translation — one floated **\$15–40K/yr for managed services / certified reports**, NOT the CC0 benchmark — noted but constrained by the no-certification governance decision).
- **P-dpo sub-variant P-dpo-hipaa-ed** (US Expert Determination path).
- **P-mlnlp-researcher**: add adversary-pluggability + the "citation-giver / citation-gravity" framing.

## Decision
No T1 persona or value-prop change forces **backward iteration** of §0–§4. All §5 findings **forward-defer** to Requirements (N1–N9 above). The concept is **validated** with a clear, consistent value proposition and a single dominant unlock (UC-13 real-data slice).

✅ **Section 5 VALIDATED (2026-05-28)** — proceeding to §6 Final Discovery Report.
