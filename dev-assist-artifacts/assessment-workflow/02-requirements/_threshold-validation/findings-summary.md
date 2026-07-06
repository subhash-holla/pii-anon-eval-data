# CAP-02 R10 Threshold-Validation — Findings Summary

**Capability**: CAP-02 — academically-sound, repeatable, reportable assessment **workflow** (PII-Anon v2.0.0 / 575,604 / CC0 / `annotations`) over a powered lattice-stratified sample (default) / full corpus (opt-in) / smoke.
**Stage**: assessment-workflow / 02-Requirements · **R10 (threshold validation)**
**Date**: 2026-06-01
**Scope of this pass**: **3 NFR thresholds × 2 HIGH-tier personas = 6 per-persona verdicts**, aggregated to one outcome per threshold, with any warranted tightening/loosening applied in place to `non-functional-requirements.md` (and mirrored to `functional-requirements.md` / `audit-report.md` where the pin is cross-doc).
**Personas exercised** (HIGH tier): **P-acad-deid** (clinical/PHI de-id researcher; credibility/citation-gating) · **P-mlnlp-researcher** (ML/NLP PII-detection researcher; ACL/EMNLP/PETS publication-rigor).
**provisional_status**: **AGENT_SIMULATED** — persona reactions are agent-simulated and are NOT a substitute for real users. Code/version/line evidence and the cited external literature are firsthand; the contested integer in NFR-023 carries `real_user_needed: true` for Pass-2.

> **Method.** Each (NFR × persona) verdict stress-tests the *quantified threshold itself* (is the number too strict / too lax / wrong-shaped for what this persona is held to?), grounded in (a) firsthand reads of the cited eval-data code and (b) external standards/literature where the number claims external warrant. Per-threshold aggregate outcome ∈ **{ACCEPTED, REVISE, PERSONA-STRATIFIED, DIVERGED}**. An edit is applied **only** where the convergent technical substance of the two verdicts warrants it.

---

## Aggregate outcomes (the headline table)

| NFR threshold | P-acad-deid | P-mlnlp-researcher | **Aggregate outcome** | Edit applied? |
|---|---|---|---|---|
| **NFR-038** — sampler: single streaming pass, O(#committed-cells)≈O(730)-bounded memory, byte-reproducible (structural; `real_user_needed:false`) | ACCEPTED | ACCEPTED | **ACCEPTED** | No |
| **NFR-035** — powered-tier compliance OR explicit UNDER-POWERED + named realized-positive shortfall; never silently LARGE (CRITICAL 1,522 / STANDARD 753 / LONG_TAIL 200) | ACCEPTED | ACCEPTED | **ACCEPTED** | No |
| **NFR-023** — CI on 100% of metrics + deterministic interval-selection rule (`small_n_cutoff` default) | **PERSONA_CONDITIONAL** | ACCEPTED | **DIVERGED** | **Yes — `small_n_cutoff` 30 → 15** (NFR-023 + FR-040 + audit-report reconciliation note) |

**Net result:** 2 thresholds **ACCEPTED unchanged**; 1 threshold **DIVERGED → tightened** (one applied edit, cross-doc-reconciled). Confidence on all three: **medium** (personas agent-simulated); the two ACCEPTED structural/power thresholds are additionally code-grounded + (for NFR-035) NIST-derived + venue-rigor-corroborated.

---

## NFR-038 — Sampler performance (single streaming pass, bounded memory, deterministic) → **ACCEPTED**

**Threshold (unchanged).** Counts committed-cell positives in **exactly ONE streaming pass** (generator-based, never materializing the corpus); working set **O(#committed-cells) ≈ O(730) keys** (per `47c3a8f`), O(1) per-annotation lookups, **independent of the 575,604 record count**; byte-reproducible under a fixed seed (Algorithm-R reservoir). **Primary gate:** `len(keys) ≤ 730` + corpus opened exactly once (integer assertion, RSS-noise-immune). **Secondary (non-gating):** peak-RSS growth 10k→100k ≤ 1.10×. Self-scoped `real_user_needed: false`.

**Both verdicts: ACCEPTED.** Convergent reasoning — neither persona's binding constraint is the count-streaming pass:
- **P-acad-deid**'s load-bearing demand is **byte-reproducibility-from-manifest (AX-002)** + **powered per-slice CIs** over a corpus the tiny real sets (i2b2 ~1,304 / TAB ~1,268) cannot reach — not sampler wall-clock. An integer `len(keys) ≤ 730` assertion is **more** reproducible than a wall-clock floor; a flaky timing gate would *threaten* this persona's reproducibility bar. The structural form is exactly grounded in the cited code (`lattice_audit.audit_positives` single pass with a committed-cell-keyed Counter; `benchmark_throughput.reservoir_sample` Algorithm-R, seeded under `SEED_BENCHMARK=20260531`).
- **P-mlnlp-researcher**'s compute binds on the **LLM tournament's GPU/API cost**, not the count-streaming pass; what they need from the sampler is exactly **determinism + scale-invariance over 575,604 records**, which the O(#committed-cells)=O(730) data-structure bound (verified firsthand in `lattice_audit.py::audit_positives` via `committed_index` + `_candidate_keys`, and `benchmark_throughput.py::reservoir_sample` + generator-based `iter_corpus`) delivers. A host-dependent rec/sec floor would add the unreproducible kind of number their review culture rejects (cf. NFR-010b, which stays INSUFFICIENT_EVIDENCE off a reference host).

**Verdict basis:** the bound is **internal-architecture-defined**, not a comparison against external tools' SLAs — no web evidence required. `real_user_needed: false` concurred by both.

**Non-blocking OBSERVATION (both personas, no edit):** the threshold is silent on a **published wall-clock for the sample stage**. Neither needs it as a *gate*, but emitting the **sample-pass elapsed seconds (descriptive, ungated) into the run-record** would close the "how long until I get my sample?" expectation without compromising the structural bound. → Carry to **Design** as a reporting nicety on the `sample`-stage run-record (NFR-042 already emits a per-stage record; this is one more descriptive field, not a new gate). **Not** a threshold change.

---

## NFR-035 — Powered-tier compliance OR explicit UNDER-POWERED + named shortfall → **ACCEPTED**

**Threshold (unchanged).** Every committed cell classified **against REALIZED positive counts** (not `target_n` labels) into `WELL_POWERED / UNDER_SAMPLED / CORPUS_LIMITED / EMPTY` (+ `NOT_ASSESSED`); each `target_n` **derived** from its design-point triple via `required_n` per `stats/power.py::TIER_SPECS` — **CRITICAL 1,522** `(0.99, 0.005)`, **STANDARD 753** `(0.98, 0.010)`, **LONG_TAIL 200** `(0.95, 0.03025)`; run labelled `PowerMatrix.verdict()` **SMALL (<0.80) / ADEQUATE (≥0.80) / LARGE (≥0.999 well-powered fraction)** (verified L351-361); representative default **never silently LARGE**; under-tier cells carry a **named realized-positive shortfall** (NFR-036).

**Both verdicts: ACCEPTED.** This threshold **is** each persona's acceptance bar made testable:
- **P-acad-deid** (citation-gating): the per-cell targets are the **genuine differentiator, not a burden** — real de-id corpora cannot reach per-slice power at all (i2b2-2014 = **1,304 records total**, PMC4989908 confirmed; TAB ~1,268; OpenDeID ~2,100), whereas these NIST/SEMATECH §7.2.4.2-derived targets over a **~440× larger** 575,604-record corpus let many `(entity-type × language)` cells actually clear them. The risk-tiered half-widths (CRITICAL ±0.5%, STANDARD ±1%, LONG_TAIL ±3% on recall) map onto a PHI-breach risk model; measuring against **realized positives + UNDER_SAMPLED-vs-CORPUS_LIMITED-vs-EMPTY** is exactly what defends subgroup gaps in review (cross-critic consensus point 5) rather than silently over-claiming LARGE — the exact failure mode that desk-rejects de-id papers.
- **P-mlnlp-researcher** (ACL/EMNLP/PETS): reviewers reject under-powered single-seed tables; the **ARR Responsible-NLP checklist + Eval4NLP** explicitly demand CIs (Clopper-Pearson named for small-n), significance tests, multi-seed error bars, and a declared single-run-vs-N-seed status — so a per-cell floor classified against **realized positives with a named shortfall** is precisely what lets their per-slice numbers survive review. The named-shortfall escape valve means under-powered cells are **honestly flagged, never blocking the run** (not too strict); the tiers are tied to the de-id breach asymmetry (not too lax). For their dominant **confirmatory paired McNemar A/B on shared gold**, the binding quantity is **discordant pairs**, and sampling-design §3.3 / `required_discordant_pairs` shows cells sized for the harder marginal recall are **already over-powered** for the paired comparison → the marginal-n floor is conservative-correct.

**Verdict basis:** **doubly-grounded** — NIST/SEMATECH §7.2.4.2 sizing + firsthand `stats/power.py::TIER_SPECS` (1522/753/200) + `PowerMatrix.verdict` (L351-361) + cited venue rigor (ARR/Eval4NLP) — plus a prior 10-persona R10 ACCEPTED-WITH-CAVEATS on the same sampling design. Confidence **medium** only because the personas remain AGENT_SIMULATED; `real_user_needed: true` (P-acad-deid) / `false` (P-mlnlp) on the *persona reaction*, not on the number's external warrant.

**Load-bearing-pair OBSERVATION (no edit, but a Design guard):** for **both** personas the defensibility of NFR-035 **depends on NFR-037 (CORPUS_LIMITED) actually firing** — i.e. the workflow must compute **full-corpus** positive totals per cell (`lattice_audit.audit_positives` over the full corpus) so an irreducible long-tail cell is never mislabelled "just under-sampled, draw more." **NFR-035 and NFR-037 are an inseparable pair for these personas, not independent.** If the full-corpus audit is dropped at Design, the review-defense value collapses even with NFR-035's targets met. → Flag for **Design**: keep the full-corpus per-cell positive audit on the critical path of the sampler stage.

---

## NFR-023 — CI on 100% of metrics + deterministic interval-selection rule → **DIVERGED → tightened (edit applied)**

**Threshold (BEFORE).** 100% of published metrics carry `{n, ci_low, ci_high, method}`; zero bare estimates. `method` by deterministic pre-registered rule: proportions → **Wilson** (default); small-n / boundary (point est at 0 or 1, **or `n < small_n_cutoff`**, committed default **`small_n_cutoff = 30`**, recorded in manifest + pre-reg) → **Clopper-Pearson**; paired differences → **paired-bootstrap**.

**The two verdicts DIVERGED on the action, while CONVERGING on the technical substance:**

| | **P-acad-deid** | **P-mlnlp-researcher** |
|---|---|---|
| Verdict | **PERSONA_CONDITIONAL** | **ACCEPTED** |
| On the 100%-CI rule | endorsed (it is their acceptance bar) | endorsed (load-bearing: a CI on every metric) |
| On the **boundary clause** (`k∈{0,n}`→Clopper-Pearson) | endorsed — correct & defensible | endorsed — fixes Wilson's degenerate zero-width at `p̂=0|1` (Brown/Cai/DasGupta 2001); **carries most of the value** |
| On the **n-based CP switch at n<30** | **contested** — Wilson robust to n≈10, Clopper-Pearson over-conservative ⇒ n<30 yields **wider-than-necessary** CIs on LONG_TAIL cells (target n=200, realized positives often <30); "30" is an **arbitrary reviewer-scrutiny point** the literature does not endorse | conceded soft — Wilson stays accurate at small n, CP over-conservative, "30 vs 40 changes little"; but **defensible because recorded + deterministic** (the actual acceptance bar) |
| Recommended action | **lower to n<15**, or **drop the n-switch entirely** (Wilson + CP-at-boundary only) — whichever stands must be the single pre-reg-recorded integer | **keep 30** (no change); determinism + manifest-recording is what survives review |
| `real_user_needed` | **true** | **true** |
| Confidence | medium | medium |

**Convergent technical core (what both agree on, firsthand-grounded):**
1. The **boundary clause is statistically mandated** and stays (both endorse). Verified present: `stats/intervals.py::clopper_pearson_interval` (L170, `_require_int_counts` L42, integer-guarded) + `wilson_interval` (L65); `small_n_cutoff` is a **config/manifest parameter, not hardcoded** in the interval fns.
2. **Wilson is robust at small n** and **Clopper-Pearson is over-conservative** (coverage > nominal) — per Wikipedia binomial-CI synthesis, Brown/Cai/DasGupta (2001), TDS/Dennis Robert, StatsKingdom, AFIT STAT COE. The n-based CP switch therefore **over-widens** intervals.
3. **No canonical numeric cutoff exists in the literature** — so any specific integer's defensibility comes from **determinism + manifest-recording**, not external warrant. (This is the precise point on which P-mlnlp rests "keep 30" and P-acad-deid rests "then the number is arbitrary, lower it.")

**Aggregate outcome: DIVERGED.** The disagreement is **not** about the rule's shape (agreed) — it is about whether to **act now** on the shared finding that 30 is over-conservative (P-acad-deid) vs **defer the integer to Pass-2** while keeping it recorded (P-mlnlp). Because the *technical substance is convergent* (both: n-switch over-conservative; no canonical integer; boundary clause is the real value), an R10 edit is warranted — but the **minimal** one that honors both.

### Applied resolution (edit landed in place)

**`small_n_cutoff` lowered 30 → 15**, with the contested-element rationale recorded inline; the boundary clause and the determinism/manifest-recording contract preserved; `real_user_needed: true` retained on the integer.

Why **15**, and why this satisfies both personas:
- **Honors P-acad-deid's primary actionable recommendation** (their first choice was "lower or drop"; 15 lowers toward the **Wilson-robust-to-n≈10 zone** both cite, materially shrinking the over-wide-CI exposure on LONG_TAIL cells).
- **Does NOT adopt P-acad-deid's more aggressive "drop the n-switch entirely" option** — that is a larger design change P-mlnlp did **not** endorse, and removing the small-n branch would forfeit a conservative safety margin for genuinely tiny n (n<5, where even the literature still prefers exact CP). Keeping a *small* exact-CP floor is the conservative middle.
- **Preserves everything P-mlnlp requires** — the cutoff stays a **single deterministic integer recorded in the manifest + pre-registration**, the linter still asserts `method` equals what the recorded cutoff prescribes, and the contract (recorded + obeyed) is unchanged. The only thing that moved is the directional default *value*, which was always flagged R10-DIRECTIONAL.
- **Keeps `real_user_needed: true`** — both verdicts flagged it; a real ACL/PETS/de-id reviewer in Pass-2 may push toward "drop entirely" (P-acad-deid's stretch) or "n<40 heuristic" (P-mlnlp's alternative). 15 is the defensible interim, not a closed decision.

**Files edited (cross-doc reconciled — the pin is shared NFR-023 ↔ FR-040, per the audit report):**
- `non-functional-requirements.md` — **NFR-023** threshold: `small_n_cutoff 30 → 15`; boundary clause split out and labelled the load-bearing branch; `real_user_needed: true` annotation added on the integer.
- `functional-requirements.md` — **FR-040** mirror: same `30 → 15`, same boundary-clause split (keeps the NFR↔FR pin reconciled).
- `audit-report.md` — directional-numbers reconciliation note updated (`small_n_cutoff` 30→15 recorded as a DIVERGED-resolution edit, pin kept reconciled).

---

## Cross-cutting notes

- **Edit discipline.** Only the **one** DIVERGED threshold was changed. The two ACCEPTED thresholds (NFR-038, NFR-035) were left **byte-unchanged**; their two non-blocking OBSERVATIONS (sample-stage elapsed-seconds in the run-record; the NFR-035↔NFR-037 load-bearing pair) are **Design-stage carries, not threshold edits**, and are recorded here only.
- **Provenance of evidence.** Code thresholds (`TIER_SPECS` 1522/753/200, `PowerMatrix.verdict` L351-361, `_require_int_counts` L42, `wilson_interval`/`clopper_pearson_interval`, `lattice_audit.audit_positives`, `benchmark_throughput.reservoir_sample`) are **firsthand file reads at HEAD (2026-06-01)**. External warrants are cited: i2b2-2014 (PMC4989908), NIST/SEMATECH §7.2.4.2, ARR Responsible-NLP / Eval4NLP, Brown/Cai/DasGupta (2001) / Wikipedia binomial-CI, PII-Bench (arXiv 2502.18545).
- **`real_user_needed` ledger after this pass.** NFR-038 → **false** (structural). NFR-035 → number externally warranted (NIST + venue), persona reaction agent-simulated. NFR-023 `small_n_cutoff` integer → **true** (Pass-2: real ACL/PETS/de-id reviewer to confirm 15, push to "drop the n-switch", or to n<40). The **boundary clause + determinism contract** in NFR-023 are firm and need no real-user confirmation.
- **No-regression.** No corpus regeneration; no lattice change (730 @ `47c3a8f` untouched); no metric-family merge; the edit is confined to a directional CI-method-selection integer and its documentation. AX-002 (recorded provenance) and AX-pii-anon-005 (pre-registered analysis plan) are preserved — the cutoff remains recorded-and-asserted.

---

## Source ledger

**In-repo (firsthand, HEAD 2026-06-01):**
- `/Users/subhashholla/Development/pii_anonymize_pseudonymize/pii-anon-core/pii-anon-eval-data/src/pii_anon_datasets/stats/power.py` — `TIER_SPECS` (1522/753/200), `required_n`, `classify`, `PowerMatrix.verdict` (L351-361)
- `/Users/subhashholla/Development/pii_anonymize_pseudonymize/pii-anon-core/pii-anon-eval-data/src/pii_anon_datasets/stats/intervals.py` — `wilson_interval` (L65), `clopper_pearson_interval` (L170), `_require_int_counts` (L42)
- `/Users/subhashholla/Development/pii_anonymize_pseudonymize/pii-anon-core/pii-anon-eval-data/scripts/lattice_audit.py` — `audit_positives`, `committed_index`, `_candidate_keys`, `deficits`
- `/Users/subhashholla/Development/pii_anonymize_pseudonymize/pii-anon-core/pii-anon-eval-data/scripts/benchmark_throughput.py` — `reservoir_sample` (Algorithm-R), `iter_corpus`, `SEED_BENCHMARK=20260531`

**External (cited in verdicts):**
- i2b2/UTHealth 2014 de-id shared task — 1,304 records — https://pmc.ncbi.nlm.nih.gov/articles/PMC4989908/
- NIST/SEMATECH e-Handbook §7.2.4.2 (proportion sample sizing) — https://www.itl.nist.gov/div898/handbook/prc/section2/prc242.htm
- ACL Rolling Review Responsible-NLP checklist / Eval4NLP — http://aclrollingreview.org/responsibleNLPresearch/
- Binomial proportion confidence interval (Wilson robust small-n; Clopper-Pearson conservative; both special-case p-hat=0|1) — https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval
- AFIT STAT COE — Recommended CIs for a Binomial Proportion — https://www.afit.edu/STAT/statcoe_files/12_Binomial%20proportion%20intervals%20DRAFT%20-%20PA%20copy(1).pdf
- PII-Bench (2,842 total samples; no per-cell power floor) — https://arxiv.org/html/2502.18545v1

---

✅ **R10 threshold-validation complete (2026-06-01).** 6 per-persona verdicts (3 NFR thresholds × 2 HIGH-tier personas) aggregated: **NFR-038 ACCEPTED**, **NFR-035 ACCEPTED**, **NFR-023 DIVERGED → tightened** (`small_n_cutoff` 30 → 15, applied in place + cross-doc reconciled NFR-023 ↔ FR-040 ↔ audit-report). Two non-blocking Design-stage OBSERVATIONS recorded. `provisional_status: AGENT_SIMULATED`; NFR-023 `small_n_cutoff` integer carries `real_user_needed: true` for Pass-2.
