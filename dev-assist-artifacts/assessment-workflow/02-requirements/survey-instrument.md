# CAP-02 R5 — Prioritization Survey Instrument

**Capability**: CAP-02 — academically-sound, repeatable, reportable assessment **workflow** that runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 / CC0 / `annotations`** over a **powered, lattice-stratified sample (default)** / **full corpus (opt-in, citable)** / **smoke (fast)** — with statistical/epistemic observability + reporting at every spine stage (`load → sample → run → score → rate → report`).
**Stage**: assessment-workflow / 02-Requirements · R5 (Prioritization survey instrument)
**Date**: 2026-06-01
**Vocabulary remap**: FR = Benchmark/Assessment Capability; NFR = Quality Attribute; UC = Evaluation Scenario; DC = Benchmark Component; Persona = **assessment consumer**.
**provisional_status**: AGENT_SIMULATED — this instrument prioritizes an agent-authored FR/NFR set; it is administered (R6) to **agent-simulated** respondents stratified by the 6 personas. Agent-simulated research is **NOT** a substitute for real users; real-respondent administration is a Pass-2 follow-up. The thresholds the trade-off items reference are **directional** (R9 threshold-validator pressure-tests them), not committed.

> **What this instrument prioritizes.** The full CAP-02 requirement set authored in R4: **25 FRs (FR-030 … FR-054)** in `functional-requirements.md` and **37 NFRs (NFR-019 … NFR-055)** in `non-functional-requirements.md` — **62 requirements total**. To keep the respondent task tractable (the cycle-1 lesson — rank bundles, not raw IDs), the 62 requirements are grouped into **18 rankable capability bundles** (B1 … B18). Every FR and NFR maps to exactly one bundle; the mapping is exhaustive and non-overlapping (coverage table at the end). Each bundle is scored on Tier A, MoSCoW-classed in Tier B, and the bundles in genuine tension are forced against each other in Tier C.

> **Design lineage.** Mirrors the cycle-1 R5 instrument (`02-requirements/survey-instrument.md`): **Tier A** = 3-axis 1–5 scoring; **Tier B** = MoSCoW from the respondent's persona seat; **Tier C** = forced trade-off pairs. CAP-02 changes: (1) the "impact" axis is reframed as **credibility-impact** (does this bundle move the academic-soundness / admissibility bar), because that is CAP-02's reason to exist; (2) the trade-off pairs are drawn **directly from the live R3 decision-forks and disagreements** (DF-1 default mode; the AX-005 universality tension; the DOI persona-split; the throughput-SLA pre-gate; the AUTHOR-vs-defer crosswalk fork) — every Tier-C item is a real adjudication R6/R7 must close, not a synthetic dilemma.

---

## 0. How to read a bundle (precondition / axiom tags)

Each bundle is tagged so the respondent sees what is *load-bearing* before scoring:

- **[P1] / [P2] / [P3]** — touches a **hard precondition** (P1 audited-stats-only + `significance.py` quarantine · P2 dataset-seam→v2.0.0 + regression contract · P3 powered lattice-stratified sampler + PowerMatrix verdict). Preconditions are not "features"; a respondent ranking them low is a signal to probe, not to de-scope.
- **[AX5-n]** — implements element *n* of the proposed **AX-pii-anon-005** (1 CI · 2 paired-test+multiplicity · 3 convergence · 4 provenance · 5 non-strippable synthetic-only caveat · 6 contamination disclosure + held-out attestation). Confirming AX-005 is itself a survey output (see §4 closing item).
- **[NR]** — a **no-regression guardrail** (cycle-1 invariants encoded as CAP-02 NFRs). Scored for awareness; **not** de-scopable (a low rank flags a respondent who under-weights regression risk).
- **[GATE]** — engineering/consumer gates treated as a **baseline** (scored Tier A, excluded from the Tier-C forced trade-offs — you do not trade a green gate against a feature).

---

## Rankable bundles (B1 … B18) — every FR + NFR mapped, exhaustive & non-overlapping

### Precondition spine (P1 / P2 / P3)

1. **B1 — Audited-stats-only run path + `significance.py` quarantine** **[P1]** **[AX5-1][AX5-2]**
   FR-042 · NFR-019, NFR-020, NFR-021, NFR-022
   *Route every CI + paired test through the audited `stats/intervals.py` + `stats/paired.py`; assert the fabricated `significance.py` (se=metric·(1−metric)/100 + Gaussian noise; n_approx=100 / pooled_sd=0.1) is unreachable from the run surface; zero approximated stats; seeded LOCAL-RNG; integer-guarded interval inputs. The unanimous walk-away trigger (C-1).*

2. **B2 — Dataset-seam reconciliation to v2.0.0 + versioned crosswalk + regression contract** **[P2]**
   FR-030, FR-031 · NFR-040, NFR-041
   *Fix the stale pins (num_records=159891, CC-BY-4.0, v1.3.0 citation, schema 1.3.0) → v2.0.0 / 575,604 / CC0 via a versioned lossless-or-explicit-lossy crosswalk; a 5-tuple regression contract {version, record-count, 63-type count, schema fingerprint, content hash} goes RED on any drift (incl. same-count content swap). Two confirmed multi-week/multi-month silent-drift burns (C-2).*

3. **B3 — Powered, lattice-stratified, seeded sampler (single streaming pass)** **[P3]** **[AX5-1]**
   FR-032 · NFR-038, NFR-039
   *Seeded, deterministic, lattice-stratified draw against each committed cell's tier target_n (derived via `required_n`, never hand-typed) on realized positives; one streaming pass, memory bounded by #committed-cells (730 @ 47c3a8f), not the corpus; design-point triple + coverage envelope written to the manifest. The capability's net-new reason to exist vs naive max_samples head-truncation.*

4. **B4 — PowerMatrix verdict + per-cell named shortfall (realized positives)** **[P3]** **[AX5-1]**
   FR-033 · NFR-035, NFR-036, NFR-037
   *Every committed cell classified WELL_POWERED / UNDER_SAMPLED / CORPUS_LIMITED / EMPTY (+ NOT_ASSESSED) against realized positives; corpus verdict SMALL/ADEQUATE/LARGE (never silently LARGE); shortfall named in realized positive counts ("short by N vs ADEQUATE"); UNDER_SAMPLED (fixable) vs CORPUS_LIMITED (irreducible) distinguished. The study's strongest delight, DF-3 resolved zero-dissent (C-5).*

### Run-type spine + presets (the highest-leverage net-new mechanism)

5. **B5 — Run-type designation scoping pre-reg + AX-005 bar + backing sample mode** **[AX5-enforcement]**
   FR-038 · NFR-033, NFR-034
   *A declared run-type (`smoke`/`dev`/`leaderboard-submission`/`filing-grade`) as a CLI flag/preset that deterministically selects the enforced rigor bar, the pre-registration gate, and the backing sample mode; smoke/dev SUPPRESS CI+p-value emission (no un-rigorous number) while leaderboard/filing bind the full AX-005 bar. N-01: the single highest-leverage new item R3 surfaced; resolves DF-2 + the AX-005 universality tension + the DF-1 citable-vs-pre-screen distinction.*

6. **B6 — Preset trio: powered-representative (default) / full-corpus (opt-in citable) / smoke (CI)**
   FR-035, FR-036, FR-037 · NFR-025
   *Exactly three presets with locked defaults: powered-representative is DEFAULT (always labelled with its power verdict, never silently full / never silently LARGE); full-corpus is explicit-opt-in + the citable leaderboard mode + descriptive-census (no CI unless a super-population target is declared); smoke is fast CI with suppressed inferential outputs. Resolves DF-1 (locked default holds; citable-vs-pre-screen made first-class).*

### Run path — engine reuse + the statistics that ride it

7. **B7 — Run wired to the existing engine + convergence + span-metric bridge (no rebuild)**
   FR-039 · NFR-051
   *Rate systems through the existing `PIIRateEloEngine`, converge via the existing `ConvergenceChecker` (Glicko RD), score spans via the existing `compute_span_metrics` at a declared span-match mode; consumed, not rebuilt; `pii-rate-elo`'s own gates (pytest/ruff/mypy) stay green. The OWNS/CONSUMES boundary made testable.*

8. **B8 — CI on 100% of metrics under a deterministic interval-selection rule** **[AX5-1]**
   FR-040 · NFR-023, NFR-024
   *Every published metric carries {n, ci_low, ci_high, method}; Wilson default / Clopper-Pearson small-n-boundary / paired-bootstrap differences, rule disclosed; CI scope labelled conditional-on-this-sample with corpus-draw variance either measured (≥2 seeds + Kendall-τ) or flagged single-seed → rank-volatility:UNMEASURED. The cheapest credibility the benchmark can buy (C-3).*

9. **B9 — Paired system-vs-system test + Holm-Bonferroni + two declared inference families** **[AX5-2]**
   FR-041 · NFR-026, NFR-027, NFR-028
   *McNemar (exact / Edwards χ²) + paired-bootstrap recall-delta CI on every pairwise claim; confirmatory set carries Holm-Bonferroni + printed family size; two families (exploratory uncorrected vs confirmatory Holm) declared in report text not only code; ranks gated by the paired verdict (non-significant pairs greyed as ties). Closes the "delta within noise" rejection vector (C-4); Holm is the one net-new statistical primitive (added to audited `stats/`, NOT `significance.py`).*

10. **B10 — Scoring-family separation (anon vs pseudo) + contamination status + seed-variance scope** **[AX5-6]** **[NR]**
    FR-043 · NFR-045, NFR-055
    *Declare scoring_family ∈ {anonymization, pseudonymization} (AX-004); pseudo never scored by bare span-F1; the four metric families never merged (inherits NFR-005); per-system contamination_status with `unknown` rejected; seed_variance_scope recorded (≥2-seed Kendall-τ or single-seed flag); AX-004 rationale written in prose. Legally load-bearing for the assurance lens (C-10).*

### Pre-registration + observability

11. **B11 — Pre-register before scoring: commit-anchored + hash-chained + immutable** **[AX5-4]**
    FR-044 · NFR-031, NFR-032
    *On an enforcing run-type, freeze the full design+analysis plan (dataset version + manifest hash + seed + systems + metrics + RD stopping rule + interval rule + multiplicity family+size + power design point + span-match mode + scoring family + tie/exclusion rules) bound to a pushed-to-remote commit SHA chained into the first run-record; immutable; report discloses run-lineage count (re-roll-until-favorable visible); census runs get parity. Opt-in rigor (DF-2), mechanism is MUST.*

12. **B12 — Per-stage observability run-record + file-level provenance** **[AX5-4]**
    FR-045, FR-046 · NFR-042, NFR-043
    *One provenance-complete run-record per spine stage (6 records: load/sample/run/score/rate/report) stamped {dataset_version, record_count, schema_fingerprint, seed, stage, code_commit} + toolchain, sharing one run id; every emitted artifact carries file-level {content_hash, code_commit, run_id, stage}. Statistical/epistemic instrumentation (G5), not generic logging; INT-05's first-six send-back floor + Art-11 provenance (C-9).*

### Reporting — the deliverable

13. **B13 — Honest leaderboard: paired-test-gated ranks + anon/pseudo separate + artifact-first register**
    FR-047
    *Every ranked number with its CI; non-significant pairs greyed/grouped as statistical ties (no rank out-runs its paired evidence); anon and pseudo reported as separate metric families (never one "redaction quality" number); academic-vocabulary LaTeX tabular + CSV, no product-verdict strings ("SHIP-WITH-CAVEATS") verbatim. The report is the deliverable (C7).*

14. **B14 — Operating-point view: recall-priority Fβ / FN:FP cost + AUPRC at the pre-registered operating point**
    FR-048 · NFR-046
    *Instead of a lone F1: a recall-priority Fβ (β>1) or stated FN:FP cost naming the de-id asymmetry + a threshold-free AUPRC + the pre-registered operating point + precision-at-fixed-recall. The false-positive tax is a confirmed real burn (F1=0.91 → precision 0.71 @ recall 0.93 → 34k FPs/10k entities → 3× license cost). N-03, the most valuable MEDIUM-persona contribution.*

15. **B15 — RD-convergence reporting + non-strippable honesty-flag bundle on every figure** **[AX5-3][AX5-5]**
    FR-049 · NFR-029, NFR-044, NFR-047
    *RD-convergence as achieved max-RD ± 2RD with rounds stated (never extrapolated, G4; NOT-CONVERGED is a blocking flag); non-strippable synthetic-only/anti-anonymity caveat inline per-metric (`DesignProvenance`, survives export to Confluence/Excel/regulatory systems); per-cell under-power flags + contamination-uncontrolled + rank-volatility scope + worst-language recall + correlation-study named-and-pending all ride the artifact. Stripping any honesty signal invalidates it (C-6).*

16. **B16 — Reproducible sample manifest + self-verifying report (embeds pre-reg hash + run id + Art-11 label)** **[AX5-4]**
    FR-034, FR-050 · NFR-030
    *The sample manifest records drawn record ids + per-cell draw provenance (design-point triple, target_n, realized positives, power_class, named shortfall) + seed + RNG/environment fingerprint + lattice_version + sampler version + PowerMatrix verdict + coverage envelope + a non-strippable caveat, and re-runs to canonical-form equality; the filing-grade report then embeds {pre-reg hash, commit SHA, run id} + a pre_registration_matches check; every metric cell carries inline {CI, provenance hash, synthetic-only caveat}; a named Art-11 alignment label; byte-reproducible sample+run from the manifest given {seed, RNG fingerprint, sampler version}. The universal reproducibility commitment (AX-002, REPRO-07).*

### Governance / anti-gaming / compliance crosswalk / citation

17. **B17 — Leaderboard hygiene + neutrality/governance + regulatory crosswalk** **[AX5-6]**
    FR-051, FR-052, FR-053 · NFR-048, NFR-049
    *Held-out labels protected + blind/provenance-stamped submission; contamination_status with `unknown` rejected + signed held-out-non-exposure attestation; named neutrality/governance statement (corpus owner / label holder / evaluator) as a structured run-record + per-report field + recusal record for managed conflicts; an auditable/updateable 63-type → GDPR(Art-9)/HIPAA/CCPA/GLBA crosswalk kept legally distinct per regime. DF-5 resolved; arms-length governance is inadmissibility-grade; crosswalk AUTHOR-not-defer (Open Item 10).*

18. **B18 — Citable / DOI-able release with frictionless citation + claims policy**
    FR-054
    *A persistent identifier (Zenodo DOI or equivalent), not only a git SHA (which link-rots); ready BibTeX + recommended-citation template; a synthetic-only claims policy stating what the result does/does not support (the ceiling caveat). C2; a hard citation gate for the academic cohort, SHOULD elsewhere.*

### Baseline gates (scored Tier A, excluded from Tier-C trade-offs)

- **G-eng — Pure-stdlib statistical cores + lazy heavy-dep guards** **[GATE][NR]** — NFR-050
- **G-norg — Cycle-1 no-regression guardrails** **[GATE][NR]** — NFR-052 (lattice 730 @ 47c3a8f), NFR-053 (NFR-018 power gate ON), NFR-054 (doc-drift = 0)
  *(NFR-051 `pii-rate-elo` gates-green is carried inside B7, where the rewiring risk lives; NFR-055 four-families-never-merged is carried inside B10, where the merge risk lives.)*

---

## Tier A — 3-axis scoring (score each of B1 … B18 + the two baseline gates; 1–5 per axis)

Rate each bundle on three independent axes. **1 = lowest, 5 = highest.**

- **Axis 1 · Credibility-impact** — *How much does shipping this bundle move CAP-02's academic-soundness / admissibility bar for your seat?* (1 = cosmetic; 5 = without it the workflow is not credible / not citable / not admissible for you).
- **Axis 2 · Effort-to-ship** — *Your estimate of build + verification cost, given the LOCKED architecture (eval-data OWNS sampling/observability/reporting; `pii-rate-elo` is CONSUMED, extend not rebuild; reuse the named seams).* (1 = trivial wiring of an existing seam; 5 = substantial net-new work). *Effort is scored so the prioritizer can compute impact-per-effort; it is **not** a vote to drop high-effort preconditions.*
- **Axis 3 · Persona-affinity** — *How central is this bundle to **your** persona's job-to-be-done (not the project's)?* (1 = irrelevant to my seat; 5 = my core need). *This axis is expected to be **stratified**, not uniform — e.g. B14 operating-point is core for P-priv-eng, peripheral for P-acad-deid; B18 DOI is core for P-acad-deid, peripheral elsewhere. Divergence here is signal, not noise.*

**Reading rule (R6 analyst):** rank by **credibility-impact × persona-affinity**, then sanity-check against effort for the impact-per-effort frontier. **A precondition bundle (B1–B4) or a baseline gate that scores low on credibility-impact is a respondent-comprehension flag** (probe in follow-up) — preconditions and no-regression gates are not de-scopable regardless of score.

---

## Tier B — MoSCoW (classify each of B1 … B18 from your persona seat)

For each bundle, assign exactly one: **Must** / **Should** / **Could** / **Won't (this cycle)**.

- Answer **from your persona's seat**, not the project's — divergence across personas is the point (it is how persona-stratified priority, e.g. DOI MUST-for-academics-SHOULD-elsewhere, is detected).
- **Preconditions (B1–B4)** and **baseline gates** may be classed, but a **Won't** on a precondition requires a one-line written rationale (it contradicts the locked brief and must be surfaced for adjudication).
- The R4 provisional split is **19 MUST · 6 SHOULD · 0 COULD** across the 25 FRs; this tier pressure-tests that split per-persona and against the bundle grouping (R7 finalizes).

---

## Tier C — Forced trade-off pairs (pick ONE per pair; one-line rationale)

Each pair is a **live adjudication** drawn from the R3 decision-forks / §4 disagreements. Assume only one can land first / fully in v0.1. **Baseline gates and preconditions are excluded** (you do not trade a precondition or a green gate against a feature). One line of rationale per choice; "both" is not permitted (the forcing is the instrument).

- **T1 — Default-mode labelling vs filing-grade full-corpus first.** **B6 preset trio with powered-representative-default-always-power-labelled** OR **a filing-grade run-type that backs the citable number with full-corpus by default (B5)** — which is the v0.1 priority for the *citable* path? *(DF-1, the study's one genuine fork — split-by-use; carries INT-05's filing-grade-full-corpus pushback to R6/R7.)*
- **T2 — AX-005 universality vs run-type scoping.** **Enforce the full AX-005 bar on every results-bearing run (B8+B9+B15 unconditional)** OR **scope enforcement by run-type and SUPPRESS inferential outputs on smoke/dev (B5)** — which enforcement model ships first? *(§4 #2: INT-02 universal-enforcement vs INT-05 avoidance-risk; the run-type mechanism is the proposed reconciliation.)*
- **T3 — Audited-stats quarantine vs powered sampler, if only one precondition lands first.** **B1 (P1 audited-stats-only + `significance.py` quarantine)** OR **B3+B4 (P3 powered sampler + PowerMatrix verdict)** — which precondition is the v0.1 must-land-first? *(Both are MUST; this surfaces which walk-away trigger the persona weights highest under sequencing pressure — fabricated stats vs missing power verdict.)*
- **T4 — Paired-test rigor (depth) vs operating-point view (decision-utility).** **B9 (paired test + Holm + two families + tie-gating)** OR **B14 (recall-priority Fβ/FN:FP + AUPRC at the pre-registered operating point)** — which lands first if only one? *(Methods-credibility depth (HIGH cohort) vs the false-positive-tax decision view (MEDIUM personas) — tests whether the academic-soundness depth or the operational-utility view is the binding need for the respondent.)*
- **T5 — DOI / persistent identifier vs leaderboard hygiene + governance.** **B18 (Zenodo DOI + BibTeX + claims policy)** OR **B17 (leaderboard hygiene + neutrality statement + regulatory crosswalk)** — which is the higher v0.1 priority? *(§4 #5 + DF-5: DOI is a HARD gate for the academic-citation cohort and silent for others; governance/neutrality is inadmissibility-grade for the assurance/procurement cohort — the choice should split cleanly by persona, confirming both are persona-stratified rather than universal.)*
- **T6 — Provenance reproducibility vs throughput-SLA pre-gate.** **B12+B16 (per-stage run-records + file-level provenance + self-verifying reproducible-from-manifest report)** OR **route effort to the oracle throughput SLA (≤50 ms p95 / ≥500 rps, machine-readable) deferred to the oracle track** — where does v0.1 effort go? *(§4 #6: throughput is a HARD pre-gate for INT-06 (red-team) and absent for everyone else; this confirms whether reproducibility-provenance is the binding need vs the oracle-latency gate, and whether the throughput SLA is correctly routed off the CAP-02-v0.1 critical path.)*
- **T7 — Regulatory crosswalk: author now vs defer.** **Author the 63-type → GDPR/HIPAA/CCPA/GLBA crosswalk in v0.1 (inside B17)** OR **defer it to a later cycle and ship the results path first** — which? *(Open Item 10's author-vs-defer fork, resolved AUTHOR in R3 by INT-04/05 — this re-tests that resolution per-persona under forced sequencing: INT-04 called it "more load-bearing than the pre-registration question.")*

---

## Survey-closing confirmation items (single question each)

- **AX-005 confirmation (the candidate axiom).** *Should **AX-pii-anon-005** — "no published metric without (1) a CI [method disclosed], (2) a paired test for system-vs-system claims [multiplicity family + size declared], (3) a convergence statement [max-RD ± 2RD + rounds], (4) reproduce-from-manifest provenance, (5) a non-strippable synthetic-only caveat, (6) for leaderboard entries, contamination disclosure + signed held-out-non-exposure attestation], enforcement scope run-type-bound; manifest-reproducibility universal" — be **CONFIRMED** as a binding CAP-02 axiom?* (Yes / Yes-with-change / No — one line.)
- **Run-type names.** *Are `smoke` / `dev` / `leaderboard-submission` / `filing-grade` the right run-type labels, or do you propose different names?* (free text — names are finalizable in Design.)
- **Missing capability.** *Is there a capability this instrument does not cover that would block your acceptance?* (free text — catches a bundle the FR/NFR set missed.)

---

## Respondent plan (administered in R6)

- **Stratified by persona + sub-archetype; ≥2 respondents per persona** (cycle-1 cadence), with the **two folded sub-archetypes explicitly seated** so their distinct lenses are not averaged away: `P-tool-vendor` (the gaming/threat-model lens that justifies B17 hygiene) under **P-tool-builder**, and `P-complreviewer` (the external-assessor / Art-11 lens that owns B12/B16/B17) under **P-dpo**.
- **Cohort weighting:** the **3 HIGH personas** (P-acad-deid, P-mlnlp-researcher, P-tool-builder) are the acceptance + credibility cohort — where all three converge on a bundle's MoSCoW class, the signal is **gating**; the **3 MEDIUM personas** (P-priv-eng, P-dpo, P-agentic-redteam) are downstream but **each owns a net-new bundle the HIGH cohort under-weights** (B14 operating-point · B12/B16/B17 filing-grade+governance · the throughput-SLA route in T6) — those signals must **not** be averaged out.
- **Confirmation-bias control (carried from R2/R3):** every section includes the disconfirming framing — Tier B permits **Won't**, Tier C **forces** a drop, and the closing items permit **No** on the axiom and a free-text "missing capability." The instrument is built to elicit rejection signal, not just assent.
- **provisional_status: AGENT_SIMULATED** — respondents are agent-simulated single-session personas; real-respondent administration + the **first-contact P-dpo lens** re-confirmation are Pass-2 musts. The trade-off thresholds are directional (R9 validates).

---

## Coverage — every FR + NFR maps to exactly one bundle (exhaustive, non-overlapping)

| Bundle | FRs | NFRs |
|---|---|---|
| B1 audited-stats + quarantine [P1] | FR-042 | NFR-019, NFR-020, NFR-021, NFR-022 |
| B2 seam→v2.0.0 + regression contract [P2] | FR-030, FR-031 | NFR-040, NFR-041 |
| B3 powered seeded sampler [P3] | FR-032 | NFR-038, NFR-039 |
| B4 PowerMatrix verdict + shortfall [P3] | FR-033 | NFR-035, NFR-036, NFR-037 |
| B5 run-type designation | FR-038 | NFR-033, NFR-034 |
| B6 preset trio | FR-035, FR-036, FR-037 | NFR-025 |
| B7 engine/convergence/bridge reuse | FR-039 | NFR-051 |
| B8 CI on every metric | FR-040 | NFR-023, NFR-024 |
| B9 paired test + Holm + 2 families | FR-041 | NFR-026, NFR-027, NFR-028 |
| B10 anon/pseudo + contamination + seed-variance | FR-043 | NFR-045, NFR-055 |
| B11 pre-registration | FR-044 | NFR-031, NFR-032 |
| B12 observability run-records + file provenance | FR-045, FR-046 | NFR-042, NFR-043 |
| B13 honest leaderboard | FR-047 | — |
| B14 operating-point view | FR-048 | NFR-046 |
| B15 convergence + honesty-flag bundle | FR-049 | NFR-029, NFR-044, NFR-047 |
| B16 reproducible manifest + self-verifying report | FR-034, FR-050 | NFR-030 |
| B17 hygiene + governance + crosswalk | FR-051, FR-052, FR-053 | NFR-048, NFR-049 |
| B18 DOI release | FR-054 | — |
| G-eng baseline gate [GATE] | — | NFR-050 |
| G-norg baseline gate [GATE] | — | NFR-052, NFR-053, NFR-054 |

**FR coverage:** FR-030 … FR-054 = **25/25**, each in exactly one bundle (0 orphan, 0 double-counted).
**NFR coverage:** NFR-019 … NFR-055 = **37/37**, each in exactly one bundle or baseline gate (0 orphan, 0 double-counted).
**Total requirements prioritized: 62** (25 FR + 37 NFR), grouped into **18 rankable bundles + 2 baseline gates**.

---

## Methodology & Epistemic Honesty
- **Instrument authored from** the R4 `functional-requirements.md` (FR-030 … FR-054) + `non-functional-requirements.md` (NFR-019 … NFR-055), the R3 `interview-synthesis.md` (DF-1 … DF-5 resolutions, §4 disagreements, §2 threshold signals, N-01 … N-15), `01-discovery/personas.md` (6 personas + 2 folded sub-archetypes, 3 HIGH / 3 MEDIUM), and the cycle-1 `02-requirements/survey-instrument.md` (3-tier format reference).
- **Bundling rationale:** 62 raw IDs are not a tractable ranking task (cycle-1 lesson). The 18 bundles + 2 baseline gates follow the FR family groups (A–I) and the NFR sections, keeping each **hard precondition (P1/P2/P3)** and the **run-type/AX-005 spine** individually visible (B1–B5) rather than buried, so the precondition signal is not diluted by aggregation. Coverage is exhaustive and non-overlapping (table above).
- **Tier-C provenance:** every forced pair is a **real, still-open adjudication** (DF-1 default mode; the AX-005 universality tension §4#2; the DOI persona-split §4#5; the throughput-SLA route §4#6; the AUTHOR-vs-defer crosswalk Open Item 10; the two-precondition sequencing question). No synthetic dilemmas.
- **provisional_status: AGENT_SIMULATED.** This instrument is administered (R6) to agent-simulated respondents; agent-simulated research is **not** a substitute for real users. The referenced thresholds (e.g. <10 min smoke, ≤50 ms/≥500 rps, 34k-FP tax, Kendall-τ, 0.80/0.999 verdict cuts) are **directional** — the R9 threshold-validator pressure-tests them; they are not committed values. Real-respondent administration + the first-contact P-dpo/assurance lens re-confirmation are Pass-2.
- **ID discipline:** no FR/NFR IDs minted or renumbered here; the instrument prioritizes the existing FR-030 … FR-054 / NFR-019 … NFR-055 set verbatim. AX-pii-anon-005 is carried as a candidate placed for confirmation (closing item), not asserted as binding.

✅ **R5 prioritization survey instrument complete (2026-06-01).** 3-tier instrument (Tier A 3-axis 1–5 · Tier B MoSCoW · Tier C 7 forced trade-off pairs) over **18 rankable bundles + 2 baseline gates** covering all **62 requirements (25 FR + 37 NFR)** exhaustively and non-overlappingly; preconditions P1/P2/P3 + the run-type/AX-005 spine individually visible; every Tier-C pair a live R6/R7 adjudication; AX-005 confirmation + run-type-naming + missing-capability closing items; respondent plan stratified by persona + the 2 folded sub-archetypes (≥2/persona). `provisional_status: AGENT_SIMULATED`.
