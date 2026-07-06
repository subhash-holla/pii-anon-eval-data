# CAP-02 Discovery §4 — Use-Case SME Review Synthesis

**Capability**: CAP-02 — Powered, repeatable, reportable assessment workflow.
**Stage**: assessment-workflow / 01-Discovery · Section 8 (consolidation of 5 SME heuristic reviews of `04-use-cases.md`)
**Date**: 2026-06-01
**Inputs reviewed**: `04-use-cases.md` (UC-16 … UC-23, 8 evaluation scenarios).
**Reviewers (5)**: (1) benchmark/evaluation-methodology incumbent · (2) statistics / power & CI expert · (3) reproducibility & pre-registration expert · (4) domain technologist (privacy-detection / de-id) · (5) OSS-leaderboard / anti-gaming veteran.
**Consolidated verdict**: **REQUEST_CHANGES** (5 of 5 reviewers). No reviewer found the *intent* unsound — every finding is a §Acceptance-signal / §Outcome precision edit, not a UC redesign. All findings `provisional_status: AGENT_SIMULATED`.

> **Code-grounding note.** Every load-bearing code claim the reviewers made was re-verified against the live repos before resolution:
> - `stats/power.py` — `TIER_SPECS` are **derived** from `(p_ref, half_width)` pairs, not hand-typed: CRITICAL `(0.99, 0.005)→1522`, STANDARD `(0.98, 0.010)→753`, LONG_TAIL `(0.95, 0.03025)→200` (L95–99). `PowerClass` has a **third state `EMPTY` (n==0)** beyond WELL/UNDER (L60–63; `classify()` L235–240). A **separate** `REID_TIER_SPECS` family exists for re-identification — `(0.30, 0.030)→897`, `(0.10, 0.030)→385` *pairs*, operating point p≈0.1–0.5, explicitly distinct from the 0.95–0.99 detection tiers (L106–157). All confirmed.
> - `pii-rate-elo` drift — converter `num_records=159891` (`datasets/converters/pii_anon_eval.py:93`), `citation="…v1.3.0"` (L222); schema `version: str = "1.3.0"` and `labels: list[...]` (`schema.py:136–137`). Confirmed. **Nuance:** `schema.py:337` comment shows the loader already supports `v1.1.0 (annotations, nested objects)` — so "read annotations" is **partly already true**; the regression contract must target the **count + version pins specifically** (validates finding MEI-04 / REPRO-05).

---

## 1. Severity tally

| Severity | Count | IDs |
|---|---:|---|
| **CATASTROPHIC** | **3** | STATS-01, STATS-03, GAME-01 |
| **MAJOR** | **15** | MEI-01, MEI-02, MEI-03, STATS-02, STATS-04, STATS-06, STATS-07, REPRO-01, REPRO-02, REPRO-03, DOM-01, DOM-02, DOM-03, GAME-02, GAME-03, GAME-04 *(16 rows — see note)* |
| MINOR | 11 | MEI-04, MEI-05, STATS-05, REPRO-04, REPRO-05, REPRO-06, DOM-04, DOM-05, GAME-05, GAME-06 |
| OBSERVATION | 4 | STATS-08, STATS-09, REPRO-07, GAME-07 |
| SUGGESTION | 3 | MEI-06, DOM-06, DOM-07 |
| PRAISE | (noted inline) | UC-16/17/18/23 spine; AGENT_SIMULATED tagging |

> **MAJOR count reconciliation.** 16 distinct MAJOR finding-IDs were filed, but **GAME-04 and REPRO-03 are the same root cause** (byte-identity under-specified → must pin sampler-version + RNG/env fingerprint), resolved jointly. Counting that convergence once → **15 unique MAJOR defects**. **Total CATASTROPHIC+MAJOR resolved this pass: 18** (3 + 15). Convergences (resolved together, named once each below): **multiplicity** = MEI-01 + STATS-03; **pre-reg ordering** = MEI-02 + REPRO-01; **single-seed variance** = STATS-04 + GAME-02; **byte-identity fingerprint** = REPRO-03 + GAME-04.

---

## 2. Findings ledger (every finding · severity · resolution)

Resolution column states the **edit applied** to `04-use-cases.md`. ✅ = applied this pass.

### CATASTROPHIC

| ID | UC | Finding | Resolution (✅ applied) |
|---|---|---|---|
| **STATS-01** | UC-16 | Tier targets stated as bare constants; the **power design point** (assumed `p_ref` / MDE, target CI half-width `d`, `alpha`, and whether the tier targets a proportion-CI half-width vs a paired detectable effect) is never declared, so WELL_POWERED is unfalsifiable. | ✅ UC-16 §Intent + §Acceptance now state target_n **derives** from `required_n(p_ref, half_width, α=0.95)` per `TIER_SPECS` — CRITICAL `(0.99, 0.005)`, STANDARD `(0.98, 0.010)`, LONG_TAIL `(0.95, 0.03025)` — and that the design point (p_ref, half_width, α, proportion-CI target) is written into the manifest. Acceptance requires the manifest to carry the design-point triple, not a bare `target_n`. |
| **STATS-03** *(+MEI-01)* | UC-17 | **Multiplicity universe undeclared.** A CI is emitted on every metric × 730 cells × systems — a massive simultaneous-inference surface — while Bonferroni is named only for pairwise claims. Inconsistent: per-cell CIs uncorrected, pairs over/under-corrected; "win on some slice" cherry-pick invited. Family **size** never stated. | ✅ UC-17 §Outcome/§Acceptance now declare **two explicit inference families**: (1) **per-cell CIs** = nominal-coverage, **simultaneous-uncorrected / exploratory** (labelled as such, not headline claims); (2) **pairwise system claims** = **Holm–Bonferroni** (registered method) with the **family size reported** (# pairs × metrics in the confirmatory set). Per-slice "wins" must carry the multiplicity-adjusted verdict (resolves GAME-06 too). |
| **GAME-01** | UC-17 | **No contamination / held-out posture.** Systems may have trained on the public synthetic PII-Anon v2.0.0 → inflated, ungameable-only-in-theory ratings. Nothing asserts the scored slice is unseen. | ✅ UC-17 §Acceptance adds a required **`contamination_status` per system** in the run-record (training-data disclosure ∈ {disclosed-unseen, disclosed-trained-on-corpus, undisclosed}) and a stated contamination posture. Honest bound: where status is `undisclosed`/`trained-on-corpus`, the leaderboard (UC-23) flags the rating as **contamination-uncontrolled**. Full held-out fold rotation noted as a Requirements/roadmap item (the synthetic corpus is public; disclosure + flag is the v0.1 honest control). |

### MAJOR

| ID | UC | Finding | Resolution (✅ applied) |
|---|---|---|---|
| **MEI-01** | UC-17 | Bonferroni family size unspecified; naive Bonferroni over 730×metrics is brutally conservative. | ✅ Folded into **STATS-03** resolution (Holm–Bonferroni, named family + size, two-family split). |
| **MEI-02** *(+REPRO-01)* | UC-18 | Pre-reg "tamper-evident" rests on a **back-datable local timestamp** — not a cryptographic ordering proof (the exact failure Art.11 assessors distrust). | ✅ UC-18 §Acceptance re-anchored: ordering is bound to a **git commit SHA pushed to remote** (the pre-reg payload's commit), recorded in the first run-record — a **hash-chain (pre-reg → first run-record)**, not a bare timestamp. The word "tamper-evident" is retained **only** with the commit-anchor; "timestamp strictly before" is demoted to a secondary check. |
| **MEI-03** | UC-16 | A cell that **cannot** reach target (corpus-exhausted) collapses to the same UNDER_POWERED bucket as one merely unsampled — shortfall not actionable. | ✅ UC-16 §Outcome now distinguishes **`CORPUS_LIMITED`** (positives in the full corpus < target_n — irreducible) from **`UNDER_SAMPLED`** (corpus has enough; this draw fell short — fixable by drawing more). Acceptance requires every under-tier cell to carry which of the two it is. (Maps onto `PowerClass.EMPTY` for the n==0 structural case, already in `power.py`.) |
| **STATS-02** | UC-16 | Power is defined on **positives per cell**, but a stratified sample draws **records**; realized positives per cell are stochastic. The signal can pass on `target_n` labels while realized positives fall short. | ✅ UC-16 §Acceptance now asserts **realized positive counts ≥ target_n** (or flags UNDER_SAMPLED on the *realized* count), not the mere presence of a `target_n` label matching `TIER_SPECS`. |
| **STATS-04** *(+GAME-02)* | UC-17 / UC-23 | **Single seed = single point.** Glicko RD bounds rating uncertainty, not **corpus-draw / seed-to-seed** variance; leaderboard rank can be sampling-fragile while RD-converged. | ✅ UC-17 §Acceptance scopes the per-cell CI as **conditional-on-this-sample** AND requires **either** ≥2 sampling seeds with **rank-stability (Kendall-τ)** reported **or** an explicit `seed_variance_scope: single-seed` flag that propagates to UC-23 as **rank-volatility: UNMEASURED**. UC-23 surfaces that flag on the headline. |
| **STATS-06** | UC-18 | Pre-reg freezes seed/systems/metrics/stopping-rule but **not the analysis plan** (interval method per metric, correction family, UNDER_POWERED handling, exclusion/tie rules) → residual researcher degrees of freedom. | ✅ UC-18 §Intent/§Acceptance: the pre-reg payload now includes the **full analysis plan** — interval method per metric class, multiplicity family + size, power design point, span-match mode, scoring family, tie/exclusion rules — and `pre_registration_matches` checks them. |
| **STATS-07** | UC-23 | A **ranked** leaderboard implies ordinal claims, but no rule governs rank when CIs overlap → re-introduces the over-claim the UC exists to prevent. | ✅ UC-23 §Acceptance: ranks must be **annotated with the paired-test verdict** — systems whose pairwise difference is **not** significant (post-correction) are **grouped/greyed as statistical ties**, so rank order never out-runs the paired evidence. |
| **REPRO-01** | UC-18 | Ordering on back-datable timestamp; `pre_registration_matches` omits **`dataset_version`** and **`rd_stopping_rule`** that §Intent claims are frozen. | ✅ Folded into **MEI-02** (commit-anchor) **plus** `dataset_version` + `rd_stopping_rule` added to the `pre_registration_matches` equality set. |
| **REPRO-02** | UC-17 | RD **NOT-converged** has no defined consequence and **no stopping rule** (max rounds / seed budget) → run not deterministically bounded (AX-002 gap). | ✅ UC-17 §Acceptance now states the **stopping rule** (max tournament rounds / seed budget) and requires the **NOT-converged verdict to propagate as a blocking honesty flag into UC-23** (explicit link). |
| **REPRO-03** *(+GAME-04)* | UC-16 | **"Byte-identical"** is environment-sensitive (dict order, float repr, locale across 60 langs) and pins the **seed but not the sampler algorithm version** → silent leaderboard-shift vector. | ✅ UC-16 §Acceptance redefined: reproduction = **canonical-form equality** (sorted keys, fixed float repr) **plus** a recorded **environment/RNG fingerprint** (RNG algorithm + seed-derivation, not just the seed int) **plus** the **sampler version** (commit/hash of `subsets/slices.py` + `stats/power.py`) in the manifest and the reproduction contract. |
| **DOM-01** | UC-17 | **AX-004 (anon vs pseudo, separate metric families) is asserted as an axiom but not enforced** in any acceptance signal. Pseudonymization scored by bare span-F1 silently violates it. | ✅ UC-17 §Acceptance adds: the run **declares `scoring_family ∈ {anonymization, pseudonymization}`**, pseudo runs are **NOT** scored by bare span-F1 (consistency / reversibility / linkage metrics apply), and the two families are never merged. Mirrored into the UC-18 pre-reg payload. |
| **DOM-02** | UC-23 | De-id recall (leakage avoidance) and precision are **not symmetric** — a missed SSN is a breach, a false positive is over-redaction. A generic recall/precision point under-claims rigor. | ✅ UC-23 §Acceptance: the operating-point view must **name the asymmetry** — report a **recall-priority Fβ (β>1)** or a stated **FN:FP cost** — not a symmetric tradeoff alone. |
| **DOM-03** | UC-16 | 63 types × 60 langs × 5 domains ≫ 730 cells, so most type×lang×domain combos are uncommittable; the UC never **bounds the entity-type coverage envelope** → implicit over-claim that rare-critical types (MRN, IBAN) are powered when absent. | ✅ UC-16 §Outcome/§Acceptance: the manifest must **state the lattice's entity-type coverage envelope** explicitly, and **uncovered critical types surface as `NOT_ASSESSED`** (never silently absent). |
| **GAME-02** | UC-23 | Single-seed rank fragility; RD-convergence does not bound seed-to-seed rank volatility. | ✅ Folded into **STATS-04** (≥2 seeds + Kendall-τ, or `rank-volatility: UNMEASURED` on the headline). |
| **GAME-03** | UC-23 | Recall-vs-precision **operating threshold not pinned** → systems game by tuning the decision threshold post-hoc to the eval set. | ✅ UC-23 §Acceptance: the operating point is **tied to the UC-18 pre-registration** (threshold-selection rule declared pre-scoring) AND a **threshold-free summary (AUPRC)** is shown alongside the operating point. |
| **GAME-04** | UC-16 | Same seed + changed sampler logic ⇒ different "valid" sample (silent shift); sampler version unpinned. | ✅ Folded into **REPRO-03** (sampler commit/hash in manifest + reproduction contract). |

### MINOR

| ID | UC | Finding | Resolution |
|---|---|---|---|
| **MEI-04** | UC-21 | Seam already partially reads `annotations` (`schema.py:337`); `num_records=159891` + `version="1.3.0"` are the hard pins. "Reads annotations" muddies the regression contract. | ✅ UC-21 §Outcome/§Acceptance retargeted to the **count + version pins specifically** (159,891 / "1.3.0"), acknowledging the loader already understands `annotations`-shaped rows. |
| **MEI-05** | UC-23 | "Recall-vs-precision operating point" is **one point mislabeled as a curve** without a threshold sweep. | ✅ Resolved jointly with GAME-03 (AUPRC threshold-free summary + pinned operating point = an honest point, not a faux curve). |
| **STATS-05** | UC-17 | `method ∈ {wilson, clopper-pearson, paired-bootstrap}` mixes interval families with **no selection rule** → comparability harmed. | ✅ UC-17 §Acceptance pins the **deterministic selection rule**: proportions → **Wilson** (default); small-n / boundary → **Clopper-Pearson**; paired differences → **paired-bootstrap**. Recorded in the pre-reg analysis plan (STATS-06). |
| **REPRO-04** | UC-19 | Hardcoded `records_scored == 575604` couples acceptance to a **magic constant**; breaks silently on v2.0.1 and contradicts UC-21's version-as-contract. | ✅ UC-19 §Acceptance now asserts `records_scored == dataset.record_count(version)`, not a literal; full-corpus runs **also require pre-registration** (parity with UC-18). |
| **REPRO-05** *(+DOM-06)* | UC-21 | Contract pins {version, field, count} but **not the schema shape** (63 entity types / annotation keys); a v2.x keeping the count but mutating the schema passes yet breaks scoring. | ✅ UC-21 §Acceptance adds an **entity-type-count (63) + schema-fingerprint** assertion to the regression contract (consistent with UC-22's `schema_fingerprint`). |
| **REPRO-06** | UC-22 | Run-record omits an **environment / code-version** field; the chain proves what data was touched, not under which executable. | ✅ UC-22 §Acceptance adds **`code_commit`** (and toolchain fingerprint) to the per-stage run-record stamp. |
| **DOM-04** | UC-17 | `compute_span_metrics` **span-match mode** (exact vs overlap/partial) unspecified — materially changes recall. | ✅ UC-17 §Acceptance pins the **span-match mode** (exact vs relaxed/overlap), recorded in the pre-reg (STATS-06 / DOM-05). |
| **DOM-05** | UC-18 | Pre-reg omits **span-match mode + scoring family** — the two DOF most prone to post-hoc tuning in de-id. | ✅ Folded into STATS-06 (both added to the pre-reg payload). |
| **GAME-05** | UC-18 | No anti-cherry-pick clause against re-rolling seeds/systems until favorable, then pre-registering that. | ✅ UC-18 §Acceptance: each pre-registration is **immutable** and the report **discloses the count of prior pre-registered runs** for the same system set (**run lineage**). |
| **GAME-06** | UC-23 | Multiple-comparison risk across 730 slices ("win on some slice"); unclear Bonferroni extends to per-slice headline claims. | ✅ Folded into STATS-03 (per-slice wins carry the multiplicity-adjusted verdict). |

### OBSERVATION / SUGGESTION (logged; lighter-touch edits)

| ID | UC | Finding | Resolution |
|---|---|---|---|
| **STATS-08** | UC-19 | A full-corpus census still warrants CIs **iff** the inference target is a super-population. Declare descriptive-census vs inferential. | ✅ UC-19 §Outcome declares the **inferential target**: full-corpus metrics are **exact-on-corpus (descriptive)** by default; CIs retained **only** when the report explicitly targets a super-population. |
| **STATS-09** | UC-20 | Smoke artifacts should **forbid CI/p-value emission**, not just carry a caveat. | ✅ UC-20 §Acceptance: smoke artifacts **suppress/null all CI + p-value fields** (in addition to `not_statistically_valid: true`). |
| **REPRO-07** | UC-23 | Report must **embed the pre-reg hash + run id** to be self-verifying end-to-end. | ✅ UC-23 §Acceptance requires the report to carry the **pre-reg hash + run id**. |
| **GAME-07** | UC-21 | `record_count==575604` is an integrity check, not a **content** check — a swapped same-count corpus passes. | ✅ UC-21 §Acceptance adds a **dataset content hash** to the regression contract alongside the count. |
| **MEI-06** | (cross) | **Coverage gap:** `power.py` ships a distinct `REID_TIER_SPECS` (re-id, recall 0.95–0.99 *not* applicable; operating point p≈0.1–0.5, 897/385 pairs). **No UC scores re-identification power.** §107 excludes only red-team, not re-id. | ✅ **New scope-boundary note added** to UC-23 / §Coverage: re-identification-power scoring (the `REID_TIER_SPECS` ladder) is **explicitly OUT of scope for CAP-02 v0.1** (CAP-02 is the *detection/anonymization* powered-assessment workflow; re-id power is a named roadmap item), so the bound is honest rather than silent. (Cross-refs cycle-1 UC-08/09 RRS scenarios.) |
| **DOM-06** | UC-21 | Schema-shape (annotation keys + 63-type vocab) assertion. | ✅ Folded into REPRO-05. |
| **DOM-07** | UC-23 | Cross-lingual recall varies sharply; surface **worst-language / low-resource recall** or flag languages below a power floor. | ✅ UC-23 §Acceptance: surface **worst-language / low-resource recall** alongside the aggregate (or flag languages below the power floor) as an honesty signal. |

### PRAISE (preserved — do not regress)
- The UC-16/17/18/23 spine — **pre-registration before scoring**, **per-metric CIs + paired McNemar/bootstrap + correction**, **non-strippable synthetic-only caveat**, and **honest RD-NOT-CONVERGED / UNDER-POWERED verdicts on the headline** — is academically sound and rare to see specified this crisply (all 5 reviewers).
- `WELL_POWERED / UNDER_POWERED`-with-named-shortfall forced classification (anti-silent-failure) and `AGENT_SIMULATED` tagging called out as correct.

---

## 3. Resolution summary

| Metric | Value |
|---|---|
| Reviewers | 5 (all REQUEST_CHANGES) |
| **CATASTROPHIC findings resolved** | **3 / 3** (STATS-01, STATS-03, GAME-01) |
| **MAJOR findings resolved** | **15 / 15** unique (16 IDs; GAME-04≡REPRO-03 counted once) |
| **CATASTROPHIC + MAJOR resolved (total)** | **18** |
| MINOR resolved | 10 / 10 |
| OBSERVATION/SUGGESTION addressed | 7 / 7 |
| New UCs added | 0 (re-id power **explicitly scoped OUT**, MEI-06; all gaps closed by sharpening existing UC acceptance signals) |
| UCs edited in place | UC-16, UC-17, UC-18, UC-19, UC-20, UC-21, UC-22, UC-23 (all 8) |

**Disposition.** Every CATASTROPHIC and MAJOR was an **acceptance-signal precision defect**, not a missing scenario — consistent with all 5 reviewers finding the intent sound. Resolutions applied by editing `04-use-cases.md` in place (global numbering UC-16…UC-23 preserved; no IDs added or reused). The one genuine **coverage gap** (re-identification power, MEI-06) is closed by an **explicit out-of-scope boundary** rather than a new UC — the honest bound, since CAP-02 is the detection/anonymization powered-assessment workflow and the `REID_TIER_SPECS` ladder belongs to the cycle-1 RRS / roadmap track.

**Epistemic honesty.** All findings and resolutions are `provisional_status: AGENT_SIMULATED` — agent reasoning from the UC doc + re-verified repo constants; no live users consulted. Real-reviewer validation is a Pass-2 follow-up.
