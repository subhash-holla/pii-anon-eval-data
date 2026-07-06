# CAP-02 Discovery §6 — Concept Value Study Synthesis

**Capability**: CAP-02 — Powered, repeatable, reportable assessment workflow (runs the existing `pii-rate-elo` tournament against PII-Anon **v2.0.0** over a powered representative sample / full corpus / smoke).
**Stage**: assessment-workflow / 01-Discovery · Section 6
**Date**: 2026-06-01
**Method**: 6 simulated `concept-value-interviewer` agents (4B representative cohort), each a distinct cohort member mapped to the CAP-02 consumer roster, reacting to the CAP-02 concept (powered representative sampling, pre-registered manifest, seeded byte-reproducibility, Wilson/Clopper-Pearson CIs, McNemar + paired bootstrap, Glicko RD-convergence, the v1.3.0→v2.0.0 seam reconciliation, and the AX-001/003 non-strippable synthetic-only caveat).

> **REPRESENTATIVE-SCALE LIMIT + `provisional_status: AGENT_SIMULATED`.** This is a 6-member representative cohort run in a single session by simulated interviewers — NOT a saturated full-rigor study and NOT a substitute for real users. Agent-simulated research cannot stand in for ACL/PETS authors, Presidio/GLiNER maintainers, i2b2/n2c2 participants, red-teamers, privacy engineers, or DPOs. A real concept-value study (real-user interviews across the roster) is a **Pass-2 follow-up** and is NOT performed here. Treat every signal below as directional, not confirmatory.

> **Cohort (6 members → CAP-02 roster).**
> | Member | Sub-archetype | Maps to roster persona | Enthusiasm | Score |
> |---|---|---|---|---|
> | CM-01 | Reproducibility-first academic benchmarker | `P-mlnlp-researcher` (+ `P-acad-deid` overlap) | high | 8 |
> | CM-02 | Applied ML engineer, healthtech NLP | `P-tool-builder` / `P-priv-eng` overlap | medium | 7 |
> | CM-03 | Re-identification specialist | `P-mlnlp-researcher` (re-id sub-archetype) | medium-high | 7 |
> | CM-04 | Enterprise agentic-security red-teamer | `P-agentic-redteam` (enterprise sub-archetype) | medium | 7 |
> | CM-05 | — | — | **REFUSED** (incomplete parameter set) | n/a |
> | CM-06 | Replication-desk research engineer | `P-mlnlp-researcher` / `P-acad-deid` (replication lens) | medium | 7 |
>
> **5 of 6 completed; CM-05 refused** (the orchestrator did not pass the full structured parameter set; the interviewer correctly declined rather than fabricate a transcript). Completed-member score range **7–8, median 7.** Enthusiasm medium→high.

## Value scores (1-10)
Range **7–8** (n=5 completed); median **7**. The ceiling factor is **consistent with cycle-1**: the **synthetic-only citation/claim ceiling caps the academics and the re-id specialist at 7–8**, and **every academic-leaning member names the real-data correlation slice (cycle-1 UC-13) as the unlock to 8.5–9**. The new, CAP-02-specific gating factors are (a) the **schema-seam reconciliation (v1.3.0→v2.0.0, UC-21) must be auditable/validated before any number is trusted** and (b) **artifact register** — for academics a citable/DOI-able release; for the red-teamer a shipped callable oracle API with throughput specs.

## Convergent confirmations (validate the locked CAP-02 direction)
1. **Seeded, byte-reproducible, pre-registered manifest (UC-18 + UC-22) is the universal delighter for the academic cohort.** CM-01: "publishable infrastructure"; CM-06: "exactly what reviewers now require." This is the single strongest pro-signal among the completed members and directly validates CAP-02's reason to exist.
2. **Lattice power-tiers with NAMED under-powered shortfalls (UC-16 + UC-23) force honest reporting — and that is the point.** CM-01: "reviewers can't accuse you of cherry-picking strata"; CM-06: "I've had a paper bounced for under-powered subgroup claims." Confirms the `UNDER-POWERED / UNDER-SAMPLED / CORPUS-LIMITED` honesty-flag design.
3. **Paired significance (McNemar + paired bootstrap, UC-17) replaces indefensible ad-hoc F1 comparison.** Named by CM-01, CM-02, CM-03, CM-06. The "rank gated by paired-test verdict / statistical ties greyed" design (UC-23) lands.
4. **The AX-001/003 non-strippable synthetic-only caveat is honest and usable — keep it exposed, do not hide it.** CM-01: "the AGENT_SIMULATED tag is a feature if exposed — don't hide it." Validates `DesignProvenance` riding every report.
5. **The schema seam is recognized as load-bearing** — but currently a **validity threat, not a delivered feature** (CM-01, CM-02, CM-04, CM-06 all independently). This confirms UC-21 (reconcile + regression-contract) is correctly prioritized as a MUST, and sharpens its acceptance bar to *documented + tested + lossless-or-explicit-lossy*.
6. **CAP-02 is honestly bounded vs the agentic track.** CM-04 (the red-teamer) confirms the static powered-assessment workflow is NOT his live-harness leakage benchmark and explicitly warns that any "agent-leakage benchmark" framing loses the red-team community — directly validating the UC-23 scope boundary and the §2 anti-attribute for `P-agentic-redteam`.

## NEW signals — forward-deferred to Requirements (additive; do not invalidate §0–§5, so they enter Stage-2's input queue)
| # | New signal | Source member(s) | Becomes (Requirements) |
|---|---|---|---|
| C1 | **Schema reconciliation (UC-21) must be a published, VERSIONED artifact + validated transform, not just fixed in code** — auditable mapping so a six-month-old run is reproducible; tested for lossiness | CM-01, CM-02, CM-04, CM-06 (strong, convergent) | FR refinement to UC-21: emit a versioned crosswalk artifact + a lossless/explicit-lossy validation test in the regression contract |
| C2 | **Citable / DOI-able release artifact** (Zenodo or equiv) — "a GitHub SHA is not enough for most venues" | CM-01 (strong); reinforces cycle-1 N8 (frictionless citation / BibTeX) | docs/distribution FR — versioned citable release + ready citation template + claims-policy on what synthetic-only supports |
| C3 | **Pre-written synthetic-only SCOPE STATEMENT / limitations template** the consumer can paste into a paper or compliance report | CM-01, CM-04 | docs FR: ship a quotable scope/limitations block alongside the non-strippable caveat (caveat = in-artifact; scope statement = human-pasteable) |
| C4 | **CI smoke mode with reference output to diff (deterministic, <10 min, no quota burn)** — catch pipeline breaks in CI without a full run | CM-02 (strong), CM-06 (strong) | NFR + FR sharpening UC-20 (smoke): ship a reference run-record consumers can byte-diff in CI |
| C5 | **FILE-level provenance tagging, not just run-level** — every emitted file carries provenance, not only the run manifest | CM-06 | observability FR sharpening UC-22: stamp provenance per artifact file |
| C6 | **Incremental / extend-the-lattice re-run story** — "if I add 10k records, do I re-run everything or extend?" | CM-02 | FR/NFR open question for UC-16/UC-21: define incremental-resample semantics (or explicitly defer with rationale) |
| C7 | **Reporting REGISTER must be artifact-first (LaTeX-ready table / committed manifest), not product-gate language** — "SHIP-WITH-CAVEATS" is the wrong register for peer review | CM-06 (strong) | reporting FR sharpening UC-23: emit a publication-register output (academic verdict vocabulary + LaTeX/CSV table), distinct from product ship/defer language |
| C8 | **Adversary-pluggability (name your own frontier model), not just version-pinning; and |C| candidate-set size as a first-class figure on every RRS number** | CM-03 (strong) | confirms cycle-1 **N3** (adversary-pluggability) + adds **|C| disclosure**; routes to the cycle-1 UC-05/08 RRS track, NOT CAP-02 v0.1 (re-id power is explicitly out of CAP-02 scope) — carry as a cross-cycle requirement note |
| C9 | **Callable oracle API with benchmarked p95 latency + throughput at harness call volume (machine-readable run-record in the report)** | CM-04 (strong) | confirms cycle-1 **N4** (latency/throughput dimension) + the scorer-I/O-contract item; routes to the cycle-1 UC-08 oracle track; for CAP-02, make `benchmark_throughput.py` output machine-readable + surfaced in the UC-23 report |
| C10 | **Visible LONG_TAIL power derivation** — "show me the power calculation behind the 200-sample tier before I trust it" | CM-01, CM-03 | reinforces cycle-1 **N7** (per-slice power transparency); reporting FR: expose the power-tier derivation (effect size + α/β) in/alongside the report |

## Member refinements (no backward iteration needed — all sub-archetypes of existing personas)
- **`P-mlnlp-researcher`** confirmed by three completed members from distinct angles: the **reproducibility-first benchmarker** (CM-01), the **re-id specialist** (CM-03 — adds adversary-pluggability + |C|), and the **replication-desk engineer** (CM-06 — adds file-level provenance + artifact-first reporting register). Refines, does not split.
- **`P-tool-builder` / `P-priv-eng` overlap** confirmed by CM-02 (healthtech ML engineer who both ships a detector AND screens for prod) — wants the CI smoke-diff and an incremental-re-run story; reinforces both personas without creating a new one.
- **`P-agentic-redteam`** (enterprise sub-archetype, CM-04) confirmed AND its honest scope boundary independently re-derived by the persona himself: CAP-02 = recognition-oracle/payload-seed/RRS-on-transcripts, NOT a live agent-leakage benchmark. Surfaces the **runtime-gateway privacy engineer as the adjacent "no-brainer" persona** (echoes the cycle-1 `P-priv-eng` runtime-gateway sub-type).
- **`P-dpo` / `P-complreviewer`**: **not represented among the completed members** (CM-05 refused). The DPO/assurance lens is therefore **UN-SAMPLED in this representative cohort** — a named gap for Pass-2.

## Decision
No T1/HIGH persona or value-proposition change forces **backward iteration** of §0–§5. The completed members **validate the locked CAP-02 direction** (powered sample + per-metric CI + paired test + RD-convergence + pre-registered byte-reproducible manifest + non-strippable synthetic caveat + honestly-bounded agentic scope). All new findings **forward-defer** to Requirements (C1–C10 above), the strongest CAP-02-native ones being **C1 (versioned + validated schema-seam reconciliation)**, **C4 (CI smoke-diff)**, **C7 (artifact-first reporting register)**, and the carried-forward credibility unlock (cycle-1 **UC-13 real-data correlation**) plus **C2 (citable release)**.

**Caveats on this decision (epistemic honesty).** (1) Representative-scale, single-session, **AGENT_SIMULATED** — directional only. (2) **n=5 completed (CM-05 refused)** — under-sampled even for a representative cohort. (3) **`P-dpo` / assurance lens un-sampled** — the EU-AI-Act-Art.11 driver and anon-vs-pseudo separation got no concept-value reaction here; do NOT treat their cycle-1 priority as re-confirmed. (4) Scores (7–8) are agent-assigned, not elicited from real users.

⚠️ **Section 6 VALIDATED-WITH-CAVEATS (2026-06-01)** — concept validated directionally by the completed representative cohort; proceeding to §7 Final Discovery Report with C1–C10 carried to Requirements and the un-sampled DPO lens + CM-05 refusal flagged as Pass-2 gaps. `provisional_status: AGENT_SIMULATED`.
