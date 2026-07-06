# CAP-02 Discovery §2 — Workflow Maps (Current vs Desired Assessment Workflow)

**Capability**: CAP-02 — Powered, repeatable, reportable assessment workflow.
**Stage**: assessment-workflow / 01-Discovery · Section 2 (companion to `personas.md`)
**Date**: 2026-06-01
**Scope**: current-vs-desired assessment workflow for the **top (HIGH) personas** (P-acad-deid, P-mlnlp-researcher, P-tool-builder), plus the desired-state for the MEDIUM personas where their job differs materially. P/G/O triples are the bridge to Requirements (R0 UC↔PGO bridge); cycle-1 PGO IDs are reused where the job is unchanged, refreshed to the CAP-02 *workflow* framing.

> **The CAP-02 workflow spine (locked architecture).**
> `load → sample → run systems → score → rate → report`
> eval-data OWNS sampling + observability + reporting; `pii-rate-elo` CONSUMES (extend, do not rebuild engine/metrics/significance).
> The **desired** state below is this spine with academic-soundness controls bound at every stage; the **current** state is each persona's hand-rolled status quo.

---

## 1. P-acad-deid — Academic De-identification Researcher (HIGH, credibility)

### Current workflow (status quo)
1. **Hunt for a corpus** — mostly tiny/gated (i2b2-2014 ≈ 1,304 notes, TAB ≈ 1,268, OpenDeID ≈ 2,100); fight IRB/DUA friction.
2. **Reconcile schema** — wrangle fragmentation across datasets by hand.
3. **Run detectors** (Presidio / fine-tuned NER / GLiNER / LLM prompting) through a bespoke harness.
4. **Score** — hand-roll `nervaluate`-style exact match; usually no CIs.
5. **Eyeball significance** — a couple of seeds, no paired test.
6. **Write the limitations section** defending external validity; per-slice under-powering is unavoidable on n≈1.3K.
- **Pain surface:** data access · schema reconciliation · per-slice under-power · synthetic citation ceiling · no resistance benchmark for post-removal LLM re-id.

### Desired workflow (CAP-02)
1. **load** — point at PII-Anon **v2.0.0** (575,604 records, "annotations", 63 types, 60 languages, 5 domains); no IRB/DUA. *(Observability: load manifest records source version + record count + schema fingerprint.)*
2. **sample** — choose **powered representative** (default) sized to the committed lattice / NIST power tiers; sample is seeded + byte-reproducible. *(If a slice misses its tier it is flagged **UNDER-POWERED** with the named shortfall, not silently shipped.)*
3. **run systems** — run de-id methods through the existing `pii-rate-elo` tournament.
4. **score** — span metrics via the mature metrics bridge; **every metric carries a CI** (Wilson / Clopper-Pearson). Anon vs pseudo kept in **separate metric families**.
5. **rate** — Elo/Glicko ratings with **RD-convergence reported**; **system-vs-system claims use a paired test** (McNemar / paired bootstrap, Bonferroni-corrected).
6. **report** — a pre-registered, **reproducible-from-manifest** report carrying per-slice power, CIs, paired-test verdicts, and the **non-strippable synthetic-only caveat** (DesignProvenance, AX-001/003). Correlation-study hook for the real-data validation slice.
- **PGO-acaddeid-01** · Benchmark a de-id model with adequate statistical power per language/domain slice → publishable per-slice F1/F2 **with CIs**, powered to lattice tiers (infeasible on n≈1.3K real corpora).
- **PGO-acaddeid-02** · Measure whether "anonymized" text resists LLM re-identification → an RRS / ESRC-attack-recall figure citable in a privacy paper.
- **PGO-acaddeid-03** · Share corpora + run ablations without DUA/IRB delay → CC0 dataset reused in teaching, robustness studies, reproductions — re-run byte-for-byte from the manifest.

---

## 2. P-mlnlp-researcher — ML/NLP Privacy Researcher (HIGH, gates v1)

### Current workflow (status quo)
1. **Pull detectors** (Presidio, GLiNER-PII, Piiranha) + a borrowed HF slice (discovery harder since Papers-with-Code shut Jul 2025 → HF leaderboards canonical).
2. **Hand-roll a harness**; re-implement span-F1.
3. **Run on the borrowed slice**; eyeball 1–2 seeds.
4. **Hand-compute significance** with bespoke code (or skip it).
5. **Paste a single-seed table into the paper** — reviewers reject under-powered, non-reproducible numbers; synthetic-only external-validity attack in review.
- **Pain surface:** re-implementing scoring + significance · defending sample choice · chasing non-reproducible numbers · single-LLM dependence.

### Desired workflow (CAP-02)
1. **load** — PII-Anon v2.0.0 via the reconciled dataset seam (drift fixed: v2.0.0 / 575,604 / "annotations", *not* the stale v1.3.0 / 159,891 / "labels" pin).
2. **sample** — pick a **preset**: powered-representative (default) / full-corpus (opt-in) / **smoke** (fast iteration); all seeded + manifest-stamped.
3. **run systems** — the existing `PIIRateEloEngine` tournament; no engine rebuild.
4. **score** — `compute_span_metrics`; **CI on every metric**; four metric families never merged.
5. **rate** — ratings + **Glicko RD convergence** reported; **paired test** (bootstrap + McNemar + Bonferroni) on every system-vs-system claim.
6. **report** — pre-registered + reproducible from the manifest; a citable neutral-leaderboard-ready artifact; the synthetic-only caveat rides the headline.
- **PGO-researcher-01** · Benchmark a new anon/pseudo method against re-id AND utility on a shared reproducible corpus → paper reports RRS + pseudonymization-integrity + utility on PII-Anon splits; reviewers accept as standard; method lands on the neutral leaderboard.
- **PGO-researcher-02** · Evaluate LLM semantic re-identification via paired pseudonymous/real profiles without IRB-blocked real data → attack-resistance results on paired-persona + ESRC slices; safely shareable, reviewer-reproducible.
- **PGO-researcher-03** · Report statistically credible per-slice performance with power + calibration → per-slice CIs + ECE/Brier on powered, stratified splits; subgroup recall gaps defensible in review.

---

## 3. P-tool-builder — Privacy-Tool Builder / OSS Maintainer (HIGH, gates v1)

### Current workflow (status quo)
1. **Build/change a recognizer**; want to know it improved nothing-regressed.
2. **Test on thin Faker-based home-grown data** (Presidio maintainer: "no formal results… somewhat intentional").
3. **Run a one-off eval**; no held-out provenance; numbers not citable.
4. **Publish a self-favorable blog number** (the vendor anti-pattern) or nothing.
- **Pain surface:** no standard yardstick · home-grown thin data · leaderboards get gamed (held-out leakage, train-on-test) · no CI regression gate.

### Desired workflow (CAP-02)
1. **load** — PII-Anon v2.0.0 as the external corpus; CC0 + stratified splits + held-out labels.
2. **sample** — **smoke** preset in CI for speed; powered-representative for a release/publication run; seeded.
3. **run systems** — tool under test through the tournament harness.
4. **score** — span metrics with CIs; multilingual/adversarial slices (homoglyph/BiDi) exercised.
5. **rate** — paired test detects a **regression** vs the prior version (not just a point drop); RD reported.
6. **report** — CI gate verdict (PASS/FAIL on F2 drop or a homoglyph/BiDi bypass) for the PR; a **permalinked, provenance-stamped** leaderboard entry for the model card — **blind/held-out submission** so the set isn't leaked and weights aren't exposed (anti-gaming, justified by the `P-tool-vendor` threat-model sub-archetype).
- **PGO-builder-01** · Gate every PR against an external multilingual/adversarial PII corpus → CI fails on an F2 regression or a homoglyph/BiDi bypass before release.
- **PGO-builder-02** · Publish a credible, reproducible detection + anonymization score → a citable neutral-leaderboard entry with held-out test provenance, used in the model card/README.
- **PGO-builder-03** · Prove a pseudonymizer resists LLM re-identification while preserving utility → an RRS + utility score (Tier 2/3) demonstrating the privacy/utility tradeoff.
- **PGO-tool-vendor-01** *(sub-archetype)* · Earn a citable third-party rank vs named competitors → permalinked entry with manifest + CI usable in sales/whitepapers.
- **PGO-tool-vendor-02** *(sub-archetype)* · Submit without exposing weights or leaking the held-out set → blind/provenance-stamped submission accepted, anti-gaming controls satisfied.

---

## 4. Desired-state deltas for the MEDIUM personas

*(Current state = their cycle-1 status quo; only the CAP-02 desired-state delta is captured here — these personas do not gate v1.)*

### P-agentic-redteam (MEDIUM)
Desired: CAP-02 is a **PII-recognition oracle** their channel-sniffer calls during a live harness run (decide "did PII cross C1–C7?"), a **payload seed library**, and an **RRS-on-transcripts** scorer — explicitly NOT the agent-leakage benchmark (that stays the live harness; a live-harness adapter is roadmap).
- **PGO-redteam-01** · Per-channel (C1–C7) leakage verdict using PII-Anon labeled entities as the recognition oracle.
- **PGO-redteam-02** · Seed reproducible exfiltration payloads (adversarial/multilingual, known ground truth) into AgentDojo/AgentLeak-style runs.
- **PGO-redteam-03** · RRS / behavioral-signal-residual score on agent transcripts confirming low re-id risk.

### P-priv-eng (MEDIUM, downstream)
Desired: consume the **report → leaderboard** output as a **pre-screen** (drop tools failing on breadth before POC), then **borrow the harness design** (Wilson/CP intervals, McNemar, NIST power tiers, seeded manifest) for an own-data POC — with a **recall-vs-precision operating-point** view, not a single F1 (the false-positive tax). Finalists always re-tested on internal data.
- **PGO-priveng-01** · Narrow a vendor/tool shortlist to 1–2 finalists before spending POC budget.
- **PGO-priveng-02** · Stand up a credible internal eval harness without building scoring from scratch.
- **PGO-priveng-03** · Enumerate entity types + adversarial patterns to cover before writing detection policy (63-type taxonomy + crosswalk as a coverage checklist).

### P-dpo (MEDIUM)
Desired: receive, from technical teams, a CAP-02 **evidence artifact** — manifest + version pin + per-slice CIs + anon/pseudo-separated metric families + DesignProvenance non-strippable caveat — that survives audit and is **Article-11-fileable** (EU AI Act Art. 10/11, Aug-2026, via the `P-complreviewer` assurance lens). No over-claim (pseudonymized never marketed as anonymized).
- **PGO-dpo-01** · Certify whether a release is lawfully *anonymized* vs merely *pseudonymized* → documented end-state classification with cited residual-re-id evidence.
- **PGO-dpo-02** · Justify a motivated-intruder / "very small risk" determination with quantitative backing → DPIA artifact citing per-record RRS / residual-risk, not bare span-F1.
- **PGO-dpo-03** · Map a transformation's technical output to GDPR/HIPAA/CCPA obligations → class-by-class regulatory crosswalk.
- **PGO-complreviewer-01** *(sub-archetype)* · Produce audit-ready, reproducible-from-manifest evidence a PII control was soundly evaluated → an Article-11-fileable artifact an external assessor accepts without rework.
- **PGO-complreviewer-02** *(sub-archetype)* · Ensure no over-claim survives into the compliance record → every metric carries a CI + the non-strippable synthetic-only caveat (AX-001/003); anon-vs-pseudo never collapsed.

---

## Outcome → benchmark-capability themes (preview of CAP-02 Requirements)

| Theme (recurring across PGOs) | Personas | Becomes (Requirements, CAP-02 IDs start UC-16 / FR-030 / NFR-019) |
|---|---|---|
| **Powered sampling with tiered presets** (representative-default / full / smoke; flag UNDER-POWERED) | researcher, acad-deid, builder, priv-eng | FR family (eval-data OWNS sampling) + NFR (power gate, AX-003) |
| **CI on every metric** (Wilson / Clopper-Pearson) | all HIGH + acad-deid + priv-eng | NFR family (AX-003) |
| **Paired system-vs-system test + RD-convergence** (McNemar / paired bootstrap / Bonferroni) | researcher, acad-deid, builder | FR + NFR (extend pii-rate-elo significance, do not rebuild) |
| **Dataset-seam reconciliation** (v1.3.0/labels → v2.0.0/annotations) | researcher, builder, acad-deid | FR (the drift fix is in-scope for the capability) |
| **Observability + reporting at every stage** (manifest, run-record, recall-vs-precision operating point) | all | FR family (eval-data OWNS reporting) + NFR |
| **Reproducible-from-manifest / pre-registered run** (seeded, byte-reproducible) | all | NFR (AX-002) |
| **Leaderboard hygiene + blind/provenance submission** (anti-gaming) | builder, vendor-subtype, researcher, dpo | FR + governance NFR (justified by P-tool-vendor) |
| **Anon-vs-pseudo separation + regulatory crosswalk** (Art.11-fileable evidence) | dpo, complreviewer-subtype, priv-eng | FR + AX-004 |
| **Non-strippable synthetic-only caveat** (DesignProvenance) | all | NFR (AX-001/003, non-strippable) |
| **Real-data validation slice** (correlation vs i2b2/TAB) | acad-deid, researcher, builder | top open item → Requirements + Testing Pass-2 |
| **Agentic recognition oracle + RRS-on-transcripts** (live-harness adapter = roadmap) | redteam | scoped FR, honestly bounded |

---

## Methodology & Epistemic Honesty
- Workflow maps are **agent-synthesized** from cycle-1 PGO triples + the CAP-02 locked architecture + live 2025/2026 persona research. Cycle-1 PGO IDs reused where the job is unchanged; sub-archetype PGOs (`*-vendor-*`, `*-complreviewer-*`) carried as governance/assurance drivers, not new gating scenarios.
- Adoption/WTP signals are **agent-inferred**; real-user validation of every workflow is a **Pass-2 follow-up** (tag `provisional_status: AGENT_SIMULATED`). Agent-simulated research is NOT a substitute for real users.
