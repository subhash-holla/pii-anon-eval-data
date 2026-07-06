# Discovery §4 — Use Cases (Evaluation Scenarios) — v2 (panel-revised)

**Stage**: 01-Discovery · Section 4
**Date**: 2026-05-28
**Method**: UCs authored from the 18 §2 P/G/O triples + §3 market signal, then revised per a 5-SME review panel (`08-use-case-review-synthesis.md`). Each UC = situation / intent / outcome + acceptance + trace. UCs are the unit carried into Requirements (R0 bridge).

> **Brownfield Mode — Source Signal vs Gaps**
> - **From assessment:** capabilities described as prose "uses" (finding m2) — now formalized as UC-NN.
> - **Gaps the user must fill:** real-user UC validation (Pass-2).
> - **Does NOT cover:** non-consumer governance was missing in v1 — added as **UC-15** in v2.

Legend — Track: **DET** detection · **ANON** anonymization · **PSEUDO** pseudonymization · **AGENT** agentic-leakage · **X** cross-cutting/governance.

> **v2 cross-cutting requirement (from panel; carry to R0 bridge): the SCORER I/O CONTRACT.** Every "running scorer" UC (01, 04, 05, 06, 07) depends on two contracts that are now first-class requirements: **(a) a documented input schema-adapter** (entity-type crosswalk + offset convention + span-matching policy: exact / partial / type-relaxed) with a **reference adapter for ≥1 real detector (Presidio)**; and **(b) version-pinning of any LLM-in-the-loop** (adversary/judge model id + prompt + decoding + seed, reported as "vs model@version"). Without these, scores are neither reproducible nor comparable.

---

### UC-01 — Multilingual/adversarial detection regression gate · DET
- **Personas:** P-tool-builder (P), P-priv-eng
- **Situation:** a detector maintainer merges a change; home-grown Faker fixtures miss multilingual + obfuscation edges.
- **Intent:** run the detector against PII-Anon's multilingual + 17-attack-type slices in CI.
- **Outcome:** CI **fails** on an F2 regression or a homoglyph/ZWSP/BiDi/encoded bypass before release; per-slice deltas shown.
- **Acceptance:** deterministic scoring on a fixed split; a known-injected bypass is caught; F2 per language/attack slice; **ships a reference detector adapter (Presidio) + documented entity-type crosswalk + span-matching policy** *(v2: scorer I/O contract)*.
- **Trace:** PGO-builder-01, priveng-03.

### UC-02 — Per-slice powered detection scoring with CIs · DET / X
- **Personas:** P-mlnlp-researcher (P), P-acad-deid
- **Situation:** tiny real corpora (i2b2 1,304 / TAB 1,268) can't power per-language/entity/domain claims.
- **Intent:** score a system per slice with confidence intervals on adequately powered splits.
- **Outcome:** publishable per-slice P/R/F1/F2 **with CIs**; subgroup recall gaps defensible.
- **Acceptance (v2):** intervals use **Wilson or Clopper-Pearson** (not Wald); the ≥753-positive bar is framed as the **high-recall-regime** target (n recomputed vs the observed operating recall — power is p-dependent); **train/test de-duplication / leakage control** stated so CIs aren't inflated by templated near-duplicates; subgroup gaps use a **paired statistic (McNemar / paired bootstrap)** on shared positives, not overlapping marginal CIs; **"reproducibility claimed; external validity deferred to UC-13."**
- **Trace:** PGO-researcher-03, acaddeid-01 · closes M2/M3 · axiom AX-pii-anon-003.

### UC-03 — Calibration + abstain-to-review · DET / X
- **Personas:** P-priv-eng (P), P-mlnlp-researcher
- **Situation:** confidence scores aren't calibrated, so human-review thresholds are fragile.
- **Intent:** measure calibration (ECE/Brier) + reliability per entity type; evaluate abstain/route-to-review.
- **Outcome:** reliability diagram + ECE/Brier per slice; a coverage-risk curve justifying a review threshold.
- **Acceptance:** ECE/Brier per entity class; abstention coverage-risk curve emitted.
- **Trace:** §3 calibration theme.

### UC-04 — Anonymization residual-re-identification-risk + utility (Pareto) · ANON
- **Personas:** P-mlnlp-researcher (P), P-tool-builder, P-dpo
- **Situation:** a span-F1 score says nothing about whether anonymized text is still re-identifiable or still useful.
- **Intent:** score an anonymizer's **output** for residual re-id risk **and** downstream utility on the same text.
- **Outcome:** a privacy-utility **Pareto** point per strategy; never a single "redaction quality" number.
- **Acceptance (v2):** harness ingests a *system's anonymized text* (closes M6); residual-risk axis **declares its adversary/threat model** (auxiliary data assumed; motivated-intruder vs public-release framing); **utility probe is pinned** (named task set + frozen scoring model/version) so submissions are comparable.
- **Trace:** PGO-builder-03, dpo-02.

### UC-05 — LLM re-identification-resistance scoring via paired personas · ANON *(HEADLINE — v2 de-circularized)*
- **Personas:** P-mlnlp-researcher (P), P-acad-deid, P-dpo
- **Situation:** LLMs re-identify "anonymized" text from behavioral cues (Staab ICLR-2024; Lermen); no public benchmark scores resistance, and real data is IRB-gated.
- **Intent:** evaluate re-identification resistance using 2,500 paired pseudonymous↔real personas + ESRC slices.
- **Outcome (v2):** **two distinct quantities** — (1) **behavioral-signal-exposure index** = the existing deterministic density heuristic, explicitly relabeled a *prior / pre-screen* (NOT "resistance"); (2) **measured RRS** = actually run the LLM-adversary matching task over the paired personas, report **empirical re-id recall AND precision with Wilson CIs**, and define **RRS = 1 − recall×precision** on *that*. Report the **correlation between the cheap index and the measured RRS** so the heuristic's validity is evidenced, not assumed.
- **Acceptance (v2):** adversary **model id + prompt + decoding + seed are version-pinned and published** ("vs adversary@version"); **candidate-set size |C|=N is a first-class parameter of every RRS figure** (closed-world recall ≠ open-world); ≥1 adversary variant run with **web-like distractors**; RRS framed as a **relative ranking instrument**, not an absolute re-id probability. **Anti-anonymity caveat is attached to the scorer itself** (travels with every emitted figure): *"RRS is a relative resistance metric under a specific synthetic adversary; it is NOT an anonymity threshold and MUST NOT be cited as evidence that output is 'anonymized' under GDPR/HIPAA."* External validity deferred to UC-13.
- **Trace:** PGO-researcher-02, acaddeid-02 · J1 · resolves panel CATASTROPHIC (RRS circularity).

### UC-06 — Pseudonymization-integrity scoring · PSEUDO *(MOAT — v2 made falsifiable)*
- **Personas:** P-tool-builder (P), P-mlnlp-researcher, P-dpo
- **Situation:** reversible tokenizers/alias systems have **no public yardstick**; silent collisions break case continuity; over-shared tokens enable unauthorized joins.
- **Intent:** score a pseudonymizer on a **stated threat model** for reversal, collision, referential integrity, key-rotation, and **key/state separation**.
- **Outcome:** a pseudonymization-integrity scorecard distinct from anonymization metrics (axiom AX-pii-anon-004).
- **Acceptance (v2):**
  - **Threat model enumerated** (attacker capabilities: has token corpus? frequency side-channel? partial key?) — "unauthorized-reversal rate" is measured *against that model*, not trivially zero.
  - **Collision metric separates** *intended deterministic-linkage collisions* (same input → same token; a referential-integrity **feature**) from *unintended cryptographic collisions* (a **fault**) — never penalize correct deterministic pseudonymizers.
  - **Key-rotation pass/fail defined**: post-rotation, authorized reversal succeeds for pre-rotation tokens; unauthorized linkage across epochs fails.
  - **Key/state separation signal** (EDPB 2025 / GDPR Art. 4(5)): can records be re-joined from the artifact **alone** without the external secret? (separation-attestable Y/N + linkability test). Reversal-resistance alone is necessary but not sufficient for the legal definition.
- **Trace:** PGO-builder-03, dpo-01 · J2 · closes M6 · **the defensible moat** · resolves panel CATASTROPHIC (implementability).

### UC-07 — Query-aware masking scoring · X / DET
- **Personas:** P-priv-eng (P), P-mlnlp-researcher
- **Situation:** "mask everything" breaks RAG/summarization utility; over- vs under-redaction is unmeasured.
- **Intent:** score whether query-irrelevant PII is masked while query-relevant context survives.
- **Outcome:** PII-relevance precision/recall + answer-quality delta + over-redaction rate.
- **Acceptance:** uses the 8K+ query-aware records; reports false-retention + false-removal rates.
- **Trace:** §3 query-aware theme.

### UC-08 — PII-recognition oracle + injection-payload seeds for live agent harnesses · AGENT *(bounded — v2)*
- **Personas:** P-agentic-redteam (P)
- **Situation:** red-teamers run live harnesses (AgentDojo/InjecAgent/AgentLeak); they need a labeled PII oracle + payloads, NOT a static "agent-leakage benchmark."
- **Intent:** supply PII-Anon's labeled entities + adversarial obfuscations as a recognition oracle the harness calls, and as injection-payload seeds.
- **Outcome (v2):** the red-teamer's **harness produces per-channel verdicts BY CALLING PII-Anon's oracle at each channel boundary — PII-Anon owns recognition, the harness owns channel capture** (AgentLeak's 7-channel taxonomy; 68.8% of leakage is inter-agent, invisible to a static set).
- **Acceptance (v2):** entities exported as an oracle API; payloads as **(obfuscated PII span + injection-carrier template + intent tag)** tuples consumable by InjecAgent/AgentDojo; differentiator stated = **multilingual + obfuscation coverage** absent from those harnesses' English payloads; **explicitly NOT marketed as live agent-leakage scoring** (guardrail kept in acceptance — testable). **Roadmap:** v1.x AgentDojo + InjecAgent callback adapter invoking the oracle at each of AgentLeak's 7 channel boundaries; v2 native multi-agent capture.
- **Trace:** PGO-redteam-01, redteam-02 · OWASP LLM02 + LLM06.

### UC-09 — Behavioral-signal residual on sanitized agent transcripts · AGENT / ANON *(v2 hardened)*
- **Personas:** P-agentic-redteam (P), P-mlnlp-researcher
- **Situation:** an agent sanitizes output but behavioral signals may still leak identity across turns/channels.
- **Intent:** **estimate residual behavioral-signal leakage** on transcripts under the synthetic adversary.
- **Outcome (v2):** a residual-leakage estimate applied **per-channel / per-turn** (NOT final-output-only — that reproduces the output-only blind spot AgentLeak quantifies).
- **Acceptance (v2):** reuses the UC-05 *measured* RRS scorer with a **transcript-distribution caveat** ("scaffolding, not a leakage verdict; un-calibrated for transcripts until validated"); confident "low risk" on final-output-only is **out of scope**. *(If the transcript path doesn't ship in v1, fold into UC-05 as a transcript-input variant.)*
- **Trace:** PGO-redteam-03.

### UC-10 — Anon-vs-pseudo end-state **evidence bundle** + regulatory crosswalk · X / ANON / PSEUDO *(v2)*
- **Personas:** P-dpo (P), P-priv-eng
- **Situation:** technical teams surface span-F1, which is "legally meaningless" for an anonymized-vs-pseudonymized end-state.
- **Intent:** surface residual-risk + reversal evidence + a per-record GDPR/HIPAA/CCPA crosswalk to **inform** (not make) a determination.
- **Outcome (v2):** a DPIA **input** bundle separating the two end-states with cited residual-risk; **renamed from "back a determination" → "inform a determination."**
- **Acceptance (v2):** the **entire bundle (crosswalk + residual-risk) is labeled DPIA INPUT, not a determination**; explicit **anti-case**: *"Does NOT certify a lawful end-state; the controller's release context + motivated-intruder assessment are out of scope."* Crosswalk keeps **GDPR / HIPAA / CCPA columns legally distinct** (Safe Harbor ≠ Expert Determination ≠ GDPR anonymisation ≠ CCPA "deidentified") — never imply cross-regime equivalence.
- **Trace:** PGO-dpo-01, dpo-03 · axiom AX-pii-anon-004.

### UC-11 — Neutral public leaderboard submission · X *(governance — v2)*
- **Personas:** P-tool-builder (P), P-mlnlp-researcher, + **P-host (UC-15 actor)**
- **Situation:** vendors won't submit to a vendor-captured or gameable board.
- **Intent:** submit a system to a neutral, arms-length leaderboard with held-out labels + provenance.
- **Outcome:** a citable, reproducible leaderboard entry usable in a model card / paper.
- **Acceptance (v2):** held-out labels not distributed **+** (a) **published submission policy** (who may submit, mandatory provenance/metadata, **reproducibility artifact: config + seed + version, independently re-runnable**); (b) **anti-gaming control** (submission-rate limit and/or held-out rotation + contamination/leakage check); (c) **opt-in publish + private "dry-run" pre-score + config/version attestation** (vendors won't submit without asymmetric-upside opt-in; rank on *attested* config, not a misconfigured default); (d) **per-slice strengths surfaced** (not just an overall rank); (e) **named neutral arbiter / advisory body distinct from `pii-anon-core`** + published CoI policy; (f) hosted on a **durable repo (HF/OpenML/Dataverse) with a versioned DOI**.
- **Trace:** PGO-builder-02, researcher-01 · governance must-have.

### UC-12 — Shareable CC0 corpus + contribution pipeline · X *(v2)*
- **Personas:** P-acad-deid (P), P-mlnlp-researcher, P-tool-builder
- **Situation:** real PHI/PII is IRB/DUA-gated; and a reuse-only commons calcifies at v1 under a solo maintainer.
- **Intent:** reuse a CC0 superset for ablations/teaching **and** contribute slices/recognizers/corrections back.
- **Outcome:** reproducible reuse + a live inbound contribution path that broadens coverage past the maintainer.
- **Acceptance (v2):** CC0 intact; deterministic load; **Croissant validates against the spec AND loads via the HF `datasets` loader** (not mere presence); **inbound contribution workflow** (PR template + provenance + CC0 license-compatibility check); **deprecation/erratum policy** for bad labels; **semantic-versioned + dated releases** so reuse is reproducible across versions.
- **Trace:** PGO-acaddeid-03 · J4.

### UC-13 — Real-data validation correlation (vs i2b2/TAB) · X *(v1.1 fast-follow — v2)*
- **Personas:** P-acad-deid (P), P-mlnlp-researcher, P-tool-builder
- **Situation:** the synthetic-only citation ceiling caps first-class adoption (4/6 personas).
- **Intent:** show PII-Anon model rankings **correlate** with rankings on i2b2-2014/TAB.
- **Outcome:** a correlation study that converts pre-screen → citable.
- **Acceptance (v2):** **estimator named (Kendall τ / Spearman) + expected n + pre-registered MDE** (n≈6–8 systems is under-powered — say so); report a **bootstrap CI on τ**, not a point value; **restrict correlation to the English clinical/legal slice overlapping i2b2/TAB** (hold domain constant so breadth isn't penalized as invalidity); add a **Bland-Altman-style agreement view**. Governance terms a **named deliverable**: co-publication MOU/authorship + data-stewardship + **rankings adjudicated by the external de-id group** + **CoI disclosure of the `pii-anon-core` relationship**. Flagged **real-data Pass-2, not agent-simulable**.
- **Trace:** §3 real-data slice (the #1 credibility unlock; v1.1).

### UC-14 — Shortlist/pre-screen tools before own-data POC · X *(downstream)*
- **Personas:** P-priv-eng (P)
- **Situation:** running full POCs on all candidate tools wastes budget.
- **Intent:** use the public leaderboard + 65-type taxonomy/coverage map to drop tools that fail on breadth.
- **Outcome:** a 1–2-finalist shortlist; finalists validated on the engineer's **own** corpus (never the benchmark as procurement oracle).
- **Acceptance:** leaderboard filterable by language/domain/track; explicit "pre-screen, not procurement oracle" framing.
- **Trace:** PGO-priveng-01.

### UC-15 — Benchmark governance & contribution lifecycle · X *(NEW in v2 — keystone for the §0 neutrality decision)*
- **Personas:** **P-host / maintainer-stakeholder** (promoted from non-persona), serving P-tool-builder + P-mlnlp-researcher + P-dpo.
- **Situation:** §0 made arms-length governance the load-bearing precondition, but neutrality was asserted, not operationalized; the repo today has 0 tests / 0 CI / no governance docs (bus-factor of one).
- **Intent:** operationalize neutral governance + a maintained contribution/release lifecycle.
- **Outcome:** a benchmark a vendor will submit to and a DPO will cite because neutrality is *demonstrable*.
- **Acceptance:** `CONTRIBUTING.md` + `GOVERNANCE.md` exist; **advisory/steering body roster published, arms-length from `pii-anon-core`**; **conflict-of-interest statement** re: the commercial product; **semantic-versioned + dated releases** with a refresh/saturation cadence; **public submission policy** (links UC-11); a **bus-factor/succession note**; CI-verified harness (links assessment C1).
- **Trace:** §0 governance decision · panel CATASTROPHIC (missing governance UC) · MLPerf/NeurIPS-D&B norms.

---

## Coverage check (v2)
- **Tracks:** DET (01,02,03,07) · ANON (04,05,09) · PSEUDO (06) · AGENT (08,09) · X/governance/credibility (10,11,12,13,14,15). All covered.
- **Personas:** all 6 consumer personas + the promoted **P-host** (UC-15) have ≥2 UCs. No orphans.
- **Closes assessment findings:** M6 (UC-04,05,06), M2/M3 (UC-02,03), M1 (UC-11/12 provenance + COMPARISON fixes), AX-004 (UC-06,10), C1 (UC-15).
- **Resolves panel CATASTROPHICs:** RRS circularity (UC-05), pseudonymization implementability (UC-06), missing governance (UC-15).

✅ **Section 4 VALIDATED (2026-05-28, v2 post-panel)** — see `08-use-case-review-synthesis.md`.
