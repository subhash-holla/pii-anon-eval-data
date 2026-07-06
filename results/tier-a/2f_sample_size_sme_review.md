# SME Panel Review — 2F Gold Spot-Check Sample-Size Adequacy

**Date:** 2026-06-19 · Branch `paper1-tier-a-experiments` · Independent 5-lens SME panel (AGENT_SIMULATED decision-support, NOT real peer review).
**Question:** Is n=400 single-rater, 2-axis gold spot-check paper-quality for NeurIPS 2026 Evaluations & Datasets?
**Verdict:** ADEQUATE-WITH-CHANGES (5/5 unanimous; MAJOR if unaddressed). PI adopted **Option C** (n≈500 + 25% blind subset + ≤6 powered per-script cells + weighted estimator + claim-scoping + AMEND framing).

---

Both load-bearing numbers check out (English split = 30,995 records; the per-type floor math and span universe are as the panel states). Here is the synthesized decision brief.

---

# DECISION BRIEF — 2F Gold Spot-Check Paper-Quality Ruling

**To:** PI (Subhash Holla) · **Re:** Is n=400 single-rater, 2-axis gold spot-check paper-quality for NeurIPS 2026 E&D? · **Panel:** 5 SME lenses, unanimous verdict, one genuine split (resolved below).

---

## 1. Headline verdict

**ADEQUATE-WITH-CHANGES** (5/5 lenses, unanimous; all rate severity-if-unaddressed = MAJOR).

**Why, in one sentence:** n=400 single-pass is the right-sized, field-normal instrument for the **one** number it can honestly carry — a single overall gold-validity corroboration rate *per axis* with a tight Wilson CI — but the spec as written also promises per-entity-type and per-script *breakdowns* out of the same budget, and those n≈3–10 cells corroborate nothing, re-importing the exact "underpowered cells" objection the paper already absorbed once at SC-09.

The defect is **not the headcount** — it is a **granularity/estimand mismatch** plus three integrity hygiene items. All are cheap to fix; none requires more sampling or a second human.

---

## 2. The crux — adequacy hinges on claim GRANULARITY, not N

Every lens converged here independently. The N you need is entirely a function of what you *claim*:

| Granularity | N needed | Verdict at n=400 | Source |
|---|---|---|---|
| **ONE overall rate per axis** (the defensible headline) | n≈280–400 (Wilson half-width ±0.017 @0.97, ±0.022 @0.95, ±0.030 @0.90) | **POWERED — keep 400** | Statistician; E&D AC; methodologist (recomputed n=400@0.97→[0.948,0.983]); domain expert |
| **Powered per-SCRIPT cells** (if wanted) | ~24/script → all 19 = infeasible; ≤6 priority scripts ≈ 144 dedicated spans → fold into a 500–550 total | descriptive-only at n=400 | Statistician |
| **Powered per-TYPE cells** (66 types) | ~24/cell→~1,584; ±0.05→~4,600; "usable" ±0.10→1,980 (66×30) | **HOPELESS at any feasible single-rater N — REJECT** | all 5 lenses |

The arithmetic that settles it: the per-type floor (3 × 66 = **198 spans, ~half the 400-span budget**) plus the proportional fill and per-script guarantees force ~170 cells at n=3–10. **3/3 → Wilson [0.44, 1.00]; 6/6 → [0.61, 1.00]; 10/10 → [0.72, 1.00].** These are coverage demonstrations ("we looked"), not powered claims. The paper's own bar for a reportable per-stratum cell is ~270 gold (SC-07, claims-document.md:72) — 3–10 is two orders of magnitude short.

**Reconciled answer to "what N?":** **keep ~400** for an overall-only claim. The lone upgrade path worth considering is **~500** (domain expert + statistician), which (a) lands squarely inside the reviewer-named n≈300–500 band, (b) absorbs partial-fill attrition, and (c) optionally funds ≤6 *powered* per-script cells. Do **not** go past ~550 — 800 only buys ±0.017→±0.012, invisible to a reviewer, on an artifact the venue does not gate on.

---

## 3. The independence problem — single-rater self-adjudication

**Is it a paper-quality blocker?** No — unanimous. The author confirming the generator's own labels is the **one genuine credibility red flag** (anchoring/confirmation confound), but it triggers a *discoverable, disclosable limitation*, not a desk-reject or major revision — **provided it is disclosed first, in the author's voice, and bounded.** Field precedent backs this: AI4Privacy's pii-masking-300k (the closest published analog) validated gold via a **single QA pass of n=216 at ~98.3% token accuracy, no IAA** — 2F at n≈400 *exceeds* the field norm. PIIBench (2.37M sequences) reports **no human gold audit at all**.

**Where the panel split — and my reconciliation:**

- **Disclosure-only** (research-integrity critic; partially the domain expert): disclose self-adjudication as a named first-class threat + pre-commit the rubric into the CSV header before adjudication. Treat the rate as an upper bound.
- **Disclosure + cheap independence hedge = BLINDING** (E&D AC, methodologist, domain expert): for a random subset (~25%), withhold `entity_type` so the author must *name* the type from `span_text`+`context` before the label is revealed, then score the match. Converts "do I agree with a label I can see" (confirmation-prone) into "do I independently recover the label" (stronger evidence) at **zero extra rater cost**.
- **Second human rater:** explicitly **rejected by all five** — the venue does not require it, it would re-open the AX-002 κ/IAA door it is forbidden to walk through, and it is over-engineering for a non-gating defense move.
- **LLM cross-check:** already PI-deferred (no API key; "another model agrees" is weaker than a human pass *for this specific objection*) — panel does not reopen it.

**My reconciled recommendation: blinding wins.** The strongest argument is the methodologist's — blinding is "the single biggest rigor upgrade available without a second rater," costs nothing, and directly converts the worst reviewer red flag into a documented, *bounded* limitation rather than merely a confessed one. Disclosure alone leaves the type-correctness rate as a pure upper bound a methods reviewer will discount; blinding a subset gives you a defensible lower-anchor on the same axis. So: **blind a ~25% seeded subset on the type axis, AND disclose self-adjudication as a named threat, AND pre-commit the rubric.** Do all three; they are complementary, not alternatives.

---

## 4. Concrete recommendation + options

**Recommended (Option B):**

| Dimension | Setting |
|---|---|
| **N** | ~400 (or 500 if you want ≤6 powered per-script cells + attrition headroom) |
| **Raters** | 1 (the author), with a **~25% blind-to-type subset** |
| **Granularity** | ONE overall rate **per axis** (type-correctness, realism), each with Wilson 95% CI = the *only* powered/reportable claim |
| **Breakdowns** | per-type/per-script → relabeled "audit coverage across the type/script space (descriptive; per-cell UNDERPOWERED)", appendix, every 100% cell prints its wide CI inline — reusing the SC-09 precedent verbatim |
| **Framing** | disclosed post-hoc AMEND row; "single-pass author corroboration, NOT κ/IAA, NOT external validity"; never the phrase "human-validated" unqualified |

| Option | What | Cost/effort | Tradeoff |
|---|---|---|---|
| **A — Minimum viable** | Keep 400, scope to overall-only per axis, demote breakdowns to flagged coverage, disclose self-adjudication, log AMEND | ~0 extra (framing + aggregator estimator fix only) | Clears every MAJOR; type-rate is an *upper bound* (anchoring undefended) |
| **B — RECOMMENDED** | Option A **+ 25% blind-to-type subset + pre-committed rubric** | +0 sampling, ~1 extra script branch + slightly slower adjudication | Best rigor-per-dollar; converts the lone red flag into a *bounded* limitation; moves 2F from "at the AI4Privacy bar" to "above it" |
| **C — Powered per-script (optional add-on)** | Option B **+ raise N to ~500** with ≤6 priority scripts at ~24/cell | +100 spans of author labor | Buys a *small* set of genuinely powered per-script cells; per-type stays descriptive at any N. Only worth it if a reviewer specifically presses per-script gold quality |

**Do NOT:** chase powered per-type cells (1,980–4,600 spans), add a second human, or report κ. All three are wasted or forbidden.

---

## 5. Severity + dissent

**Worst-case severity if shipped as-spec'd: MAJOR** (unanimous). Not a desk-reject — the venue hard-gates only Croissant/RAI metadata, and synthetic data gets "no special mention or heightened scrutiny" — but a methods reviewer would ding two things: (1) per-type/per-script numbers presented as results re-invite the underpowered-cells objection; (2) undisclosed/under-bounded self-adjudication reads as "author confirms own labels." Both are reviewer-perception hits on a credibility *buttress*, so they dent rather than sink — but they squander 2F's entire purpose (defusing MAJOR-3) if left raw.

**Genuine dissent / divergence worth the PI seeing:**
- **The statistician's estimator bug (most consequential non-consensus point).** Only the sampling statistician flags it sharply: spec §3 computes the overall rate as naive `(#correct)/(#adjudicated)`. With the per-type floor **massively over-sampling the long tail** (rare/Art-9 types), a naive pooled mean is a **biased** estimate of the corpus-wide gold-validity rate — it over-weights long-tail types. **Fix:** report the overall rate as a frequency-weighted / Horvitz–Thompson estimate using each span's true selection probability (or run a clean *proportional* headline sample + a *separate* small long-tail coverage tranche that is never pooled into the headline). I rate this **correct and load-bearing**: without it, the one number 2F can defend does not estimate the quantity the claim states. This is the single most important technical edit beyond claim-scoping, and the other lenses simply did not surface it — heed it.
- **Floor size:** methodologist/critic suggest dropping the per-type floor from 3 to 2 (132 spans) to free budget for the headline; statistician suggests decoupling the floor into a separate coverage pass entirely. Both serve the same goal (stop spending half the budget on uninterpretable cells). Either is fine; the cleanest is the statistician's decoupling.
- **What 2F does NOT discharge (all five flag this):** the contribution-value-study §2.7 flip-lever the reviewers named wanted *real-text* validation (FR-027/Paper-3 scope). 2F is synthetic-plausibility — a deliberately weaker in-scope substitute. State plainly that 2F corroborates gold-*label-validity on the synthetic distribution* and does **not** answer external validity. Do not let it be cited as having closed the real-text objection.

---

## 6. Spec edits (if adopted — exact changes to `docs/superpowers/specs/2026-06-19-2f-gold-spotcheck-design.md`)

1. **§1 Done-when #1:** keep ~400; add "(or ~500 to sit inside the reviewer-named n≈300–500 band and absorb partial-fill attrition)".
2. **§1 Done-when #3 + §3 — the load-bearing edit.** Change the deliverable from "two rates + per-type/per-script breakdowns" to: *"**ONE overall single-pass corroboration rate per axis** (type-correctness, realism), each with a Wilson 95% CI = the only powered/reportable claim. Per-entity-type and per-script tables are emitted as **'audit coverage across the type/script space (descriptive; per-cell UNDERPOWERED — flagged)'**, to an appendix, with an explicit `n; CI; UNDERPOWERED` column and the wide CI printed inline next to every 100% cell — reusing the SC-09 treatment (claims-document.md:81-82)."*
3. **§3 — fix the estimator (statistician).** Replace naive `(#1)/(#adjudicated)` with a **frequency-weighted / Horvitz–Thompson** overall rate using each span's stratum selection probability (or split into a proportional headline sample + a non-pooled long-tail coverage tranche). Add: state the estimand explicitly ("overall rate over the corpus marginal via inverse-probability weighting", *not* the raw stratified pooled mean); optionally also print the unweighted pooled rate labeled "sample-level, not corpus-projecting"; note the FPC (≈0.99993 at 400/~3M) once and dismiss it; report both axis CIs **with widths inline** (H-4 house rule).
4. **§2 — floor.** Either lower `min_per_type` from 3 to 2, or (cleaner) run the floor as a **separate coverage pass** explicitly decoupled from the headline-estimation sample, reframed as "coverage breadth assurance," never pooled into the headline rate.
5. **§4 + §2 — add blinding.** New protocol step: for a seeded ~25% subset, the sampler **withholds `entity_type`**; the author names the type from `span_text`+`context` before the label is revealed, then scores the match. Disclose the split. Pre-commit a 1–2-sentence **realism rubric** (with 2–3 worked examples) into the CSV header *before* adjudication.
6. **§5 / §7 — promote self-adjudication.** Move "Author-rater bias" out of the §7 risk table into a **first-class named limitation** in §5 (and the paper's Limitations/datasheet), in the author's voice, treating the type rate as bounded. Rename the headline noun from "single-pass agreement rate" to **"gold-validity corroboration rate (author single-pass review against the programmatic gold)"**. Add a manuscript-lint rule banning unqualified "human-validated"/"human validation" anywhere (mirror the existing "never discover" / "never rounded 0.80" lints).
7. **§0 / §8 + preregistration.md — integrity.** Add: 2F is **net-new after the PI-signed prereg (2026-06-18, hash 6d7b621a)** and absent from the 12 frozen experiments and from claims/falsifiability. Log it as a dated **AMEND-03-style deviations-log row** and narrate it in the paper's "Deviations from preregistration" section as **disclosed post-hoc corroboration commissioned by MAJOR-3** — never pre-planned validation (consistent with the AX-G1/G2 posture; must not contradict the prereg's own "no human annotators (AX-002)" attestation).
8. **New §10 — scope honesty.** State explicitly that 2F corroborates gold-label-validity on the synthetic distribution and does **NOT** discharge the contribution-value-study §2.7 real-text flip-lever (FR-027/Paper-3 scope).

---

**Bottom line for the PI:** Green-light 2F — but ship **Option B** (n≈400, single rater + 25% blind subset, **claim exactly one weighted overall rate per axis**, breakdowns demoted to flagged coverage, self-adjudication owned as a named threat, logged as a disclosed post-hoc AMEND). The two edits that are non-negotiable are spec edit **#2** (claim-scoping) and spec edit **#3** (the weighted-estimator fix the statistician alone caught). With those, n=400 single-pass is honest, field-above-norm, and paper-quality; it converts MAJOR-3 from an objection into a differentiator. Without them, it is fine for the headline but the promised per-type/per-script claims are a credibility trap.

**Lenses:** sampling statistician · NeurIPS E&D AC/reviewer · annotation/NLP-eval methodologist · research-integrity critic · PII/privacy-benchmark domain expert (all ADEQUATE-WITH-CHANGES, MAJOR).
**Key artifacts:** spec §0–§9 · novelty-stress-test.md MAJOR-3:44 · claims-document.md SC-09:81-82 & SC-07:72 · preregistration.md §56-63 (AMEND policy) · contribution-value-study.md §2.7 · field-positioning.md §2/§5 · census.out:34372 (EN split 30,995 rec) · AI4Privacy pii-masking-300k (n=216 QA analog) · NeurIPS 2026 E&D Reviewer Guidelines.
