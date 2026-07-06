# Design Spec — Sub-Project 2F: Gold Spot-Check Audit (human, single-pass) — v2 (post-SME-panel)

**Date:** 2026-06-19 (rev. after independent SME-panel review)
**Repo:** `pii-anon-eval-data` (branch `paper1-tier-a-experiments`)
**Author/PI:** Subhash Holla (with Claude)
**Status:** DRAFT — awaiting PI review before plan

---

## 0. Context

Fourth work-stream of the current improvement iteration (after headline-lock + 2C; B-4 deferred to the
v2.2.0 cut). 2F is the cheapest credible answer to the recurring reviewer objection *"every number is
synthetic; the gold has no human validation"* (`01-discovery/novelty-stress-test.md` MAJOR-3).

**This spec was revised after an independent 5-lens SME panel** (sampling statistician · NeurIPS E&D
AC/reviewer · annotation-methodologist · research-integrity critic · PII-benchmark domain expert; full record
`results/tier-a/2f_sample_size_sme_review.md`). Unanimous verdict: **ADEQUATE-WITH-CHANGES** — n≈400–500
single-rater is right-sized and *above* the field norm (AI4Privacy validated gold with n=216 single-pass,
no IAA; PIIBench reports no human audit), **but** the design must (i) claim only ONE weighted overall rate
per axis as powered, (ii) use a frequency-weighted estimator, (iii) add a blind subset, (iv) own
self-adjudication, (v) log 2F as a post-hoc AMEND. PI adopted **Option C** (n≈500 + the above + ≤6 *powered*
per-script cells).

**Decision (PI):** a **human, single-pass** spot-check — the author adjudicates a stratified **~500**-span
sample. (LLM judge deferred: no API key here; "another model agrees" is weaker for *this* objection than a
human pass. Second human rater rejected by the whole panel — re-opens the AX-002 κ door, venue doesn't
require it.)

**Hard honesty constraints:**
- **AX-002** (verbatim): the corpus has **NO human annotators** → **NO inter-annotator agreement / Cohen's
  kappa** may be reported. 2F is a **single-pass corroboration by ONE rater (the author)** — never IAA/κ/panel.
- **AX-001** (synthetic-only): the *realism* axis is the author's synthetic-plausibility judgment, NOT
  external validity. 2F does **NOT** discharge the real-text validation flip-lever
  (`contribution-value-study.md §2.7` → FR-027 / Paper-3 scope) — state this plainly (§10).
- **Prereg integrity:** 2F is **net-new after the PI-signed preregistration** (2026-06-18; absent from the 12
  frozen experiments + the claims/falsifiability set). It is logged as a dated **AMEND-style deviation** and
  narrated in the paper's "Deviations from preregistration" as *disclosed post-hoc corroboration commissioned
  by MAJOR-3* — never as pre-planned validation. Must not contradict the prereg's own AX-002 attestation.

**Ground truth (verified 2026-06-19):** corpus 782,677 records / 66 entity types / 60 languages / 19 scripts.
Each gold annotation carries `entity_type, start, end, text`; `text[start:end]==annotation["text"]` is
offset-validated (0 errors). The 11 powered-rectangle scripts include the 5 new 2C scripts (Cyrillic, Thai,
Greek, Bengali, Hebrew). No `anthropic`/`openai` lib or API key present.

---

## 1. Goal & success criteria

**Goal:** ship a deterministic stratified sampler + a weighted aggregator so the author adjudicates ~500 gold
spans on two axes (type-correctness + realism, with a blind type-recovery subset) and the artifact reports a
**single weighted overall corroboration rate per axis** (the only powered claim) plus a small set of **powered
per-script cells**, reframing the gold as "programmatic-by-construction, human-spot-check-corroborated."

**Done when:**
1. `scripts/gold_spotcheck_sample.py` deterministically (seeded `SEED=20260619`) emits a **stratified ~500**
   review CSV `results/tier-a/gold_spotcheck_review.csv`. Stratification (one sample, three guarantees):
   (a) a **per-script powered tranche** — ≥24 spans for each of the **6 priority scripts** (Cyrillic, Thai,
   Greek, Bengali, Hebrew, Latin) so those cells are genuinely powered; (b) a **per-type coverage floor** —
   ≥2 per entity type present (breadth assurance, NOT a powered claim); (c) **proportional fill** of the
   remainder. The sampler **records each span's inclusion probability** `p_incl` (for the weighted estimator)
   and a seeded `blind` flag on ~25% of rows.
2. Review CSV columns: `span_id, record_id, language, script, entity_type, span_text, context, p_incl, blind,
   type_correct, realistic, recovered_type, note`. For `blind=1` rows the `entity_type` is **withheld**
   (shown only after the author records `recovered_type`); for `blind=0` rows `recovered_type` is left empty.
3. The author fills `type_correct` (1/0), `realistic` (1/0), `recovered_type` (blind rows only), `note`.
   Partial completion supported. A 1–2-sentence realism **rubric** with 2–3 worked examples is pre-committed
   into the CSV header **before** adjudication.
4. `scripts/gold_spotcheck_aggregate.py` emits `results/tier-a/gold_spotcheck.md` + a DATASHEET field with:
   - **the ONE powered headline per axis** — a **frequency-weighted (Horvitz–Thompson, inverse-`p_incl`)
     overall corroboration rate** for `type_correct` and `realistic`, each with a **Wilson 95% CI** (width
     printed inline); the estimand stated explicitly ("corpus-marginal rate via inverse-probability
     weighting," NOT the raw stratified pooled mean); the unweighted pooled rate optionally shown, labeled
     "sample-level, not corpus-projecting";
   - the **blind-subset type-recovery rate** (author independently recovered the type) — the bounded,
     anchoring-resistant evidence on the type axis;
   - the **6 powered per-script cells** (≥24 each) with Wilson CIs;
   - **descriptive per-entity-type + full per-script coverage** in an appendix, each cell flagged
     `n; CI; UNDERPOWERED` with the wide CI inline next to every 100% cell (reusing the SC-09 treatment) —
     explicitly NOT powered claims;
   - the list of `0`-marked spans + notes (actionable disagreements).
5. Framing per AX-002/AX-001/prereg (§0, §5, §10). The headline noun is **"gold-validity corroboration rate
   (author single-pass review against the programmatic gold)"** — never "human-validated"/κ/IAA.
6. `tests/test_gold_spotcheck.py` green; full `pytest` green; `ruff` clean; content version stays 2.1.0.

**Explicitly OUT of scope:** any κ/IAA; a second human rater; an LLM/second-model pass (v2.2.0-cut option if
budget); **powered per-entity-type claims** (~1,980–4,600 spans needed — infeasible; types stay descriptive);
fixing gold defects the audit finds (tracked follow-ups, reported as-measured); re-scoring detectors.

---

## 2. Component A — stratified sampler (`scripts/gold_spotcheck_sample.py`)

Deterministic, seeded (`SEED=20260619`), pure-stdlib (`csv`, `json`, `random.Random`). Streams the corpus,
enumerates gold spans, computes per-stratum populations, then draws ~500 with the three guarantees in §1.1.
For each drawn span it records `p_incl` = (drawn-from-stratum / stratum-population) so the aggregator can
invert it (Horvitz–Thompson). Marks a seeded ~25% `blind` subset (stratified across scripts so blinding isn't
concentrated). Emits the review CSV with a ±60-char `context` window and the pre-committed realism rubric in
the header. Idempotent (same seed → byte-identical CSV). The per-type coverage floor is recorded as a
**separate `tranche` tag** (`headline` | `script_power` | `type_floor`) so the aggregator never pools
`type_floor` rows into the powered headline except via correct inverse-probability weighting.

---

## 3. Component B — weighted aggregator (`scripts/gold_spotcheck_aggregate.py`)

Reads the filled CSV (blank rows ignored; partial-fill safe). Per axis:
- **Headline (powered):** Horvitz–Thompson weighted rate `= Σ(w_i·x_i)/Σ(w_i)` with `w_i = 1/p_incl_i`,
  giving an unbiased estimate of the corpus-marginal corroboration rate (correcting the long-tail
  over-sampling the per-type floor induces); **Wilson 95% CI** on the effective sample (report the design
  effect / effective-n so the CI is honest under weighting); FPC (≈0.99994 at 500/~3.1M spans) noted once and
  dismissed.
- **Blind type-recovery:** `recovered_type == true entity_type` rate over `blind=1` rows + Wilson CI — the
  anchoring-resistant lower-anchor on type validity.
- **Powered per-script cells:** the 6 priority scripts (≥24 each) → per-cell rate + Wilson CI (reportable).
- **Descriptive coverage:** per-entity-type + full per-script tables, every cell flagged `n; Wilson-CI;
  UNDERPOWERED` — NOT powered claims.
- **Disagreements:** all `0`-marked spans with notes.

Emits `gold_spotcheck.md` (headline rates + CIs, blind-recovery, powered per-script, descriptive appendix,
disagreements, the AX-002/AX-001/prereg framing block) + a one-line DATASHEET summary. Pure-stdlib +
`stats.intervals.wilson_interval` (integer counts); deterministic.

---

## 4. The human adjudication step (protocol)

Between A and B the author marks, per span (given `span_text` + `context`):
- **`type_correct`** (1/0) — is `text[start:end]` genuinely an instance of `entity_type`? (gold-validity).
- **`realistic`** (1/0) — plausible synthetic instance per the pre-committed rubric? (synthetic-plausibility;
  expected lower for non-English non-name English/US-anchored values — informative, not a defect).
- **`recovered_type`** (blind rows only) — the author **names** the entity type from text+context *before*
  the true label is revealed; scored by the aggregator (independent recovery, anchoring-resistant).
- **`note`** — why, for any `0`.
The rubric + protocol are written into the CSV header and `gold_spotcheck.md` for reproducibility.

---

## 5. Honesty (load-bearing)

- **AX-002:** headline = "single-pass gold-validity corroboration by ONE rater (the author)"; explicitly NOT
  IAA / Cohen's κ / a panel. **Self-adjudication is promoted to a first-class named limitation** (here + the
  paper Limitations + datasheet), in the author's voice: the `type_correct` rate is treated as an *upper
  bound*; the **blind type-recovery rate is the bounded, anchoring-resistant complement**.
- **AX-001:** realism = author synthetic-plausibility judgment, not external validity.
- **Manuscript lint:** ban the unqualified phrase "human-validated" / "human validation" (mirror the existing
  "never discover" / "never rounded 0.80" lints).
- Disclose: adjudicator = the author (single rater); seed + sample composition + tranches; the rubric; every
  disagreement; the committed filled CSV as the audit record.

---

## 6. Testing & quality gates

- `tests/test_gold_spotcheck.py`: sampler determinism (same seed → identical span set + `p_incl` + `blind`
  flags); stratification (each of the 6 priority scripts ≥24; every present type ≥2; `blind`≈25%; `p_incl`
  recorded); aggregator math on a **mocked filled CSV** — Horvitz–Thompson weighted rate (vs a hand-computed
  expected value), Wilson CI, blind-recovery rate, powered per-script cells, descriptive-coverage flagging,
  partial-fill handling, disagreement listing.
- Full `pytest` green; `ruff` clean on the 2 new files; `check_version_sync.py` OK (content 2.1.0). No
  corpus/lattice change; headline-lock + 2C artifacts untouched.

---

## 7. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Per-type/per-script numbers read as powered claims (SC-09 trap) | Only the weighted overall rate per axis + the 6 priority per-script cells are reported as powered; all other cells flagged UNDERPOWERED with inline CIs (appendix). |
| Naive pooled mean biased by long-tail over-sampling | Horvitz–Thompson inverse-`p_incl` weighting; estimand stated; effective-n reported. |
| Self-adjudication confirmation/anchoring bias | 25% blind type-recovery subset (anchoring-resistant); promoted to a named first-class limitation; type rate treated as upper bound. |
| Misread as IAA/κ or external validity | AX-002/AX-001 framing; "corroboration rate" noun; manuscript lint bans "human-validated". |
| 2F cited as closing the real-text objection | §10 states it corroborates synthetic-distribution label-validity only; real-text = FR-027/Paper-3. |
| Prereg deviation undisclosed | Logged as a dated post-hoc AMEND; narrated in "Deviations from preregistration". |
| Sampler non-determinism | Fixed seed; determinism test. |

---

## 8. Decisions locked (PI, 2026-06-19; Option C)

- Adjudicator = **human, single-pass (author)** + a **~25% blind-to-type subset**. Sample **~500** (funds ≤6
  powered per-script cells + attrition headroom). **Two axes** (type-correctness, realism) + blind recovery.
- **Only powered claims:** one Horvitz–Thompson-weighted overall rate per axis + the 6 priority per-script
  cells. Per-entity-type stays **descriptive** (infeasible to power). Framed per AX-002/AX-001/prereg-AMEND.
- Content version stays 2.1.0. Second rater / κ / LLM-judge rejected-or-deferred.

---

## 9. Deliverables

- `scripts/gold_spotcheck_sample.py` (stratified seeded sampler, records `p_incl` + `blind` + `tranche` →
  review CSV) + `scripts/gold_spotcheck_aggregate.py` (HT-weighted overall rate per axis + Wilson CIs + blind
  type-recovery + 6 powered per-script cells + descriptive coverage → `gold_spotcheck.md` + datasheet field).
- `results/tier-a/gold_spotcheck.md` + the committed filled `gold_spotcheck_review.csv` (audit record) + a
  DATASHEET gold-validity-corroboration line + the AMEND row.
- `results/tier-a/2f_sample_size_sme_review.md` (the panel review — already committed) as the design rationale.
- `tests/test_gold_spotcheck.py`; full pytest green; ruff clean; version-sync OK. Working increment on
  `paper1-tier-a-experiments` (content 2.1.0).

---

## 10. Scope honesty (what 2F does NOT do)

2F corroborates **gold-label validity on the synthetic distribution** (is the programmatic gold correctly
typed + synthetically plausible). It does **NOT** establish external validity, does **NOT** answer the
real-text / off-template validation flip-lever (`contribution-value-study.md §2.7` → FR-027 / Paper-3), and
does **NOT** provide inter-annotator agreement. It is a single-rater, synthetic-distribution corroboration —
a deliberately bounded, in-scope substitute that defuses MAJOR-3 without overclaiming.
