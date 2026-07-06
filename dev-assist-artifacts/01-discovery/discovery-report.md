# Discovery Report — PII-Anon Benchmark (canonical)

**Stage 1 — Discovery · CANONICAL OUTPUT** · 2026-05-28
**Inputs:** 2 user research briefs + own web research + existing project docs + 32 agent dispatches (3 POV critics · 6 persona researchers · 3 market analysts · 5 SME reviewers · 15 concept-value interviewers).
**Ready for:** Stage 2 Requirements (`/dev-assist-requirements`).

> **Benchmark-dataset framing:** PII-Anon is a synthetic benchmark + Python eval harness, not an app. "Personas" = benchmark consumers; FR/NFR = benchmark capabilities/quality attributes. See `MANIFEST.md` Methodology Notes.

---

## 1. Point of View (refined & validated — §0)
> For **ML/NLP privacy researchers and privacy-tool builders** who need a *safely-shareable, reproducible* way to stress-test PII systems before exposing real data, **PII-Anon** is an open (CC0), **independently-governed** benchmark whose distinguishing contributions are **(1) LLM re-identification-resistance scoring** (measured-attack RRS + paired pseudonymous/real personas) and **(2) pseudonymization-integrity scoring** (authorized-reversal, collision, referential-integrity, key/state separation) — alongside detection and anonymization-utility tracks — unified into **one multilingual (60-language) artifact** with per-slice confidence intervals. Existing benchmarks cover these tracks **in fragments and mostly in English**; none scores re-identification resistance *and* pseudonymization integrity across languages as one reproducible, leaderboard-backed suite. Enterprise privacy engineers use it to **shortlist** before validating on their own corpus — a pre-screen and research instrument, not a substitute for own-data POCs.

**Governance (locked):** arms-length neutral — neutral leaderboard + methodology paper + open submissions; funded via grants / as a credibility loss-leader for `pii-anon-core`; **no certification/paid-eval monetization** (it would re-introduce the neutrality conflict).

## 2. Motivation (§1)
PII protection is now a system-level control across training/prompt/retrieval/tool/memory/output/log channels. Detection is fragmented and brittle (cross-source baselines collapse); anonymization ≠ pseudonymization is a regulatory + product fork (EDPB 2025: pseudonymized data remains personal data); vendor single-score claims are untrustworthy. The benchmark targets four measurement gaps — calibration/uncertainty, query-aware masking, end-to-end agentic privacy, and **separate anon-vs-pseudo evaluation** — plus the cross-cutting methodological gap of **stated statistical power** (per-slice n + CIs).

## 3. Personas (priority-classified — §2)
| Priority | Persona | Core job |
|---|---|---|
| **HIGH** | ML/NLP privacy researcher (+ citation-giver/adversary-pluggability sub-traits) | shared reproducible anon/pseudo+re-id benchmark with powered, calibrated, citable numbers |
| **HIGH** | Privacy-tool builder / OSS maintainer (Presidio/GLiNER/commercial-SDK sub-types) | CI regression gate + credible neutral leaderboard score + pseudonymizer integrity proof |
| **HIGH** | Academic de-id researcher (clinical + legal/education; +HIPAA-ED context) | per-slice-powered, IRB-free, citable de-id eval + re-id resistance + **coreference/quasi-id** |
| MEDIUM | Agentic-security red-teamer (frontier-lab + enterprise sub-types) | a recognition oracle + payload library their **live** harness calls (not an agent-leakage benchmark) |
| MEDIUM | Enterprise privacy engineer (runtime-gateway · batch-scaffold · dpo-bridge sub-types) | shortlist/pre-screen + a calibration/coverage scaffold for own-data validation |
| MEDIUM | Compliance / DPO (EU-GDPR + US-HIPAA/CCPA sub-types) | DPIA *input*: anon-vs-pseudo separation + regulatory crosswalk + residual-risk evidence |

Universal bounce risk: **synthetic-only citation ceiling**. Universal trust gate: **neutral governance**.

## 4. Workflow Maps (P/G/O — §2)
18 P/G/O triples → see `workflow-maps.md`. They cluster into the capability themes in §6.

## 5. Market Position (§3 — competitors VERIFIED live)
- 2026 competitors confirmed real (RAT-Bench 2602.12806, PIIBench 2604.15776, AgentLeak 2602.11510, From-Weak-Cues 2603.18382, GLiNER Guard 2605.05277). **The original "no benchmark does all three" claim was correctly retired.**
- **PII-Anon ranks #2 (behind RAT-Bench) on the weighted Pugh matrix — because Tiers 2/3 are precomputed annotations, not a running scorer (finding M6).** Closing M6 is the top engineering priority.
- **Defensible empty quadrant:** multilingual + re-id-resistance + **pseudonymization-integrity** (unoccupied by all 9 competitors) + anon-risk+utility in **one CC0 artifact**.
- **Weakest:** real-data validity (synthetic ceiling), adoption/citations (AI4Privacy incumbent), agentic realism (AgentLeak owns live).
- **`COMPARISON.md` has 4 false/stale claims** (SPY, PIILO, AI4Privacy, Nemotron) + a PIIBench/PII-Bench name-collision → fix before external publication.

## 6. Use Cases (§4, v2 — 15 UCs, SME-reviewed)
See `04-use-cases.md`. Capability themes (the spine of Requirements):
- **Re-identification-resistance scoring** (UC-05, de-circularized: measured-attack RRS + exposure-index pre-screen) — headline.
- **Pseudonymization-integrity scoring** (UC-06, threat-model + collision-type-separation + key/state separation) — moat.
- **Anonymization residual-risk + utility Pareto** (UC-04).
- **Detection: powered per-slice CIs + calibration** (UC-02, UC-03; Wilson/paired stats).
- **Query-aware masking** (UC-07).
- **Agentic recognition-oracle + payloads** (UC-08, bounded; UC-09 transcript residual).
- **Anon-vs-pseudo end-state evidence + regulatory crosswalk** (UC-10, "inform not determine").
- **Neutral leaderboard + held-out provenance + opt-in** (UC-11); **CC0 + contribution pipeline** (UC-12); **real-data correlation** (UC-13, v1.1 unlock); **shortlist** (UC-14); **governance & contribution lifecycle** (UC-15).
- **Cross-cutting:** scorer I/O contract (schema adapter + span-matching + adversary version-pinning).

## 7. Concept Value Findings (§5 — 15-member cohort, validated)
Concept **validated** (value 6–8, capped by synthetic ceiling; UC-13 lifts to ~9). Pseudonymization-integrity is the strongest, most uncontested signal. **9 NEW forward-deferred items (N1–N9)** for Requirements — notably **coreference/quasi-identifier-combination scoring (N1)**, cost-aware/pluggable adversary (N2/N3), runtime latency dimension (N4), financial-PII coverage (N5), cross-turn fragmented leakage (N6), per-language power table (N7), frictionless citation (N8), display-layer regime distinctness + PCI-DSS (N9).

## 8. Open Items for Requirements
1. **Close M6**: turn precomputed annotations into running scorers (anon/pseudo/re-id) with a documented I/O contract + Presidio reference adapter — the top priority.
2. **De-circularize RRS** (measured attack + Wilson CIs + |C| param + version-pinned, pluggable, distractor-augmented adversary) and make the **anti-anonymity caveat non-strippable**.
3. **Statistical power** (Wilson/Clopper-Pearson + paired stats + per-slice n + per-language table; axiom AX-003).
4. **Pseudonymization-integrity** threat model + collision-type separation + key/state separation (axiom AX-004; EDPB Art. 4(5)).
5. **Governance/neutrality** (UC-15): GOVERNANCE.md, advisory body, CoI policy, leaderboard hygiene.
6. **Real-data validation slice (UC-13)** — the credibility unlock; v1.1, co-published; Pass-2.
7. **Incorporate N1–N9** (esp. coreference/quasi-id N1; runtime latency N4; financial PII N5).
8. **Fix COMPARISON.md** false/stale claims + name-collisions; reconcile **v2.0.0 version narrative** (stale prior v2.0.0 commit) + doc/data drift (M1).
9. **Honestly bound the agentic track** (oracle, not agent-leakage benchmark).

## 9. Methodology & Epistemic Honesty
- 32 agent dispatches; **all simulated** (critics, personas, SMEs, cohort). Web-grounded research (competitor verification, persona/market evidence) cites live sources w/ 2026-05-28 retrieval; **the 2026 competitor papers were independently verified** in §3.
- **Real-user validation of personas, use cases, and concept value is a Pass-2 follow-up** — agent-simulated cohorts are NOT a substitute (the dev-assist-testing pass2-coordinator will refuse substitution).
- WTP ≈ $0 (CC0); priority is strategic, not revenue.

---
### Handoff signal to Requirements (post-Discovery)
> Discovery complete (2026-05-28). 15 use cases (→ Requirements R0 bridge), 6 personas (priority: 3 high / 3 medium), arms-length-neutral governance, refined POV (re-id-resistance + pseudonymization-integrity + multilingual, one CC0 artifact). Methodology: 3 POV critics + 6 persona researchers + 3 market analysts (competitors verified) + 5-SME UC panel + 15-member concept-value cohort. Top Requirements priority: close M6 (running scorers). Ready for Requirements. Run: `/dev-assist-requirements`
