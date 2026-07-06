# Discovery §2 — Workflow Maps (Persona / Goal / Outcome)

**Stage**: 01-Discovery · Section 2 (companion to `personas.md`)
**Date**: 2026-05-28

These **P/G/O triples** are the bridge to Stage 2: each becomes the seed for one or more Functional Capabilities (FRs) and Quality Attributes (NFRs) via the R0 UC↔PGO bridge. 18 triples across 6 personas.

---

## P-mlnlp-researcher (HIGH)
| ID | Goal | Outcome |
|---|---|---|
| PGO-researcher-01 | Benchmark a new anon/pseudo method against re-id AND utility on a shared reproducible corpus | Paper reports RRS + pseudonymization-integrity + utility on PII-Anon splits; reviewers accept as standard; method lands on the neutral leaderboard |
| PGO-researcher-02 | Evaluate LLM semantic re-identification (Staab/Lermen-style) via paired pseudonymous/real profiles without IRB-blocked real data | Attack-resistance results on 2,500 paired personas + ESRC slices; safely shareable, reviewer-reproducible; no real-PII exposure |
| PGO-researcher-03 | Report statistically credible per-slice (language/entity/domain) performance with power + calibration | Per-slice CIs + ECE/Brier on powered, stratified splits; subgroup recall gaps defensible in review |

## P-tool-builder (HIGH)
| ID | Goal | Outcome |
|---|---|---|
| PGO-builder-01 | Gate every PR against an external multilingual/adversarial PII corpus | CI fails on F2 regression or a homoglyph/BiDi bypass before release |
| PGO-builder-02 | Publish a credible, reproducible detection + anonymization score | A citable neutral-leaderboard entry with held-out test provenance, used in the model card/README |
| PGO-builder-03 | Prove a pseudonymizer resists LLM re-identification while preserving utility | An RRS + utility score (Tier 2/3) demonstrating the privacy/utility tradeoff — unavailable in any current benchmark |

## P-acad-deid (HIGH)
| ID | Goal | Outcome |
|---|---|---|
| PGO-acaddeid-01 | Benchmark a de-id model with adequate statistical power per language/domain slice | Publishable per-slice F1/F2 with CIs (infeasible on n≈1.3K real corpora) |
| PGO-acaddeid-02 | Measure whether "anonymized" text resists LLM re-identification | An RRS / ESRC-attack-recall figure citable in a privacy paper |
| PGO-acaddeid-03 | Share corpora and run ablations without DUA/IRB delay | CC0 dataset reused in teaching, robustness studies, and reproductions |

## P-agentic-redteam (MEDIUM)
| ID | Goal | Outcome |
|---|---|---|
| PGO-redteam-01 | Detect whether PII crossed any agent channel during a live attack | Per-channel (C1–C7) leakage verdict using PII-Anon labeled entities as the recognition oracle |
| PGO-redteam-02 | Seed reproducible exfiltration payloads into a running harness | Adversarial/multilingual PII payload set injected into AgentDojo/AgentLeak-style runs with known ground truth |
| PGO-redteam-03 | Verify sanitized agent output resists re-identification | RRS / behavioral-signal-residual score on agent transcripts confirming low re-id risk |

## P-priv-eng (MEDIUM, downstream)
| ID | Goal | Outcome |
|---|---|---|
| PGO-priveng-01 | Narrow a vendor/tool shortlist to 1–2 finalists before spending POC budget | Tools failing on breadth (multilingual, entity coverage) eliminated via the public leaderboard; only finalists proceed to internal-data POC |
| PGO-priveng-02 | Stand up a credible internal eval harness without building scoring from scratch | Adopts PII-Anon's per-slice power + calibration + Tier-2/3 scoring design to evaluate finalists on their own corpus |
| PGO-priveng-03 | Enumerate entity types + adversarial patterns to cover before writing detection policy | Uses the 65-type taxonomy + regulatory crosswalk as a coverage checklist, closing blind spots earlier |

## P-dpo (MEDIUM)
| ID | Goal | Outcome |
|---|---|---|
| PGO-dpo-01 | Certify whether a release is lawfully *anonymized* vs merely *pseudonymized* | Documented end-state classification with cited residual-re-id evidence that survives regulator review |
| PGO-dpo-02 | Justify a motivated-intruder / "very small risk" determination with quantitative backing | DPIA artifact citing per-record RRS / residual-risk + quasi-identifier handling, not bare span-F1 |
| PGO-dpo-03 | Map a transformation's technical output to GDPR/HIPAA/CCPA obligations | Class-by-class regulatory crosswalk showing which sensitivity classes were handled under which framework's standard |

---

## Outcome → benchmark-capability themes (preview of Requirements)

| Theme (recurring across PGOs) | Personas | Becomes (Stage 2) |
|---|---|---|
| **Re-identification-resistance scoring** (RRS, ESRC, paired personas) | researcher, builder, acad-deid, redteam, dpo | FR family + the headline novelty |
| **Pseudonymization-integrity scoring** (reversal/collision/referential-integrity) | researcher, builder, dpo | FR family — least-served quadrant (closes M6) |
| **Anonymization residual-risk + utility (Pareto)** | researcher, builder, acad-deid, dpo | FR family (closes M6) |
| **Per-slice statistical power + calibration** (CIs, ECE/Brier) | researcher, acad-deid, priv-eng | NFR family (closes M2/M3) |
| **Neutral leaderboard + held-out provenance + submission pipeline** | builder, researcher, priv-eng, dpo | FR + governance NFR |
| **Multilingual / adversarial breadth as one CC0 artifact** | all | dataset-property FRs |
| **Regulatory crosswalk + anon/pseudo end-state separation** | dpo, priv-eng | FR + axiom AX-pii-anon-004 |
| **Real-data validation slice** (correlation vs i2b2/TAB) | researcher, acad-deid, builder | top open item → Requirements + Testing Pass-2 |
| **Agentic PII-recognition oracle + RRS-on-transcripts** (live-harness adapter = roadmap) | redteam | scoped FR, honestly bounded |

✅ **Section 2 VALIDATED (2026-05-28).**
