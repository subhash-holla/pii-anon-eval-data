# CAP-02 Requirements — Verification-Criteria Audit (R9)

**Capability**: CAP-02 — academically-sound, repeatable, reportable assessment workflow (`load → sample → run → score → rate → report`).
**Stage**: assessment-workflow / 02-Requirements · R9 (verification-criteria strengthening)
**Date**: 2026-06-01
**Auditor**: R9 verification-criteria strengthener (agent)
**Scope**: `functional-requirements.md` (FR-030 … FR-054, 25 FRs) + `non-functional-requirements.md` (NFR-019 … NFR-055, 37 NFRs).
**provisional_status**: AGENT_SIMULATED — this audit strengthens the *testability* of agent-authored criteria; it does not re-validate the underlying directional thresholds (that is R10 / Pass-2). IDs are **stable** (no FR/NFR renumbered or removed).

---

## Audit rubric (the pass/fail bar applied to every criterion)

- **Every FR** must have a **boolean-testable Given/When/Then**: the `THEN` plus its `Boolean test:` line must reduce to a predicate a CI job (or a single named mechanical oracle) can assert `True`/`False`. **Weak** = a `THEN` clause not covered by the `Boolean test:`; a subjective/undefined adjective on the run path (`honest`, `correctly`, `genuinely`) with no operational definition; an **unbounded quantifier** (a threshold parameter left free, e.g. `β > 1` with no fixed value, "small-n threshold" un-pinned); an **undefined set** ("worst-language", "low-resource", "critical types") with no enumerating predicate; or a check whose **oracle is unspecified** (who/what computes it).
- **Every NFR** must have a **quantified threshold (number + unit) OR a boolean-auditable predicate** **AND** a **measurement method that is itself mechanical**. **Weak** = the sole `Measure:` is **`reviewer audit`** / **`governance checklist`** / **`checklist audit`** with no CI-assertable predicate beside it; a threshold that is actually a free parameter ("a pre-registered cutoff" with no committed default and no test that the cutoff is *recorded*); a measurement that names no **pass condition** (what makes it green); or a `Measure:` that asserts existence of a field but not the **semantic predicate** the threshold promises.

A criterion passes if **a developer could write the test today** from the text alone, with no additional design decision required to know what "green" means. Where a design decision *is* legitimately deferred (e.g. final run-type names), the strengthened form pins the **test contract** (the value must be *recorded and asserted*), not the decision.

---

## Summary

| File | Items | Strengthened | Pass as-authored |
|---|---|---|---|
| `functional-requirements.md` | 25 FRs | **12** | 13 |
| `non-functional-requirements.md` | 37 NFRs | **15** | 22 |
| **Total** | **62** | **27** | 35 |

**27 criteria strengthened.** Every change is **additive precision** — it pins a free parameter, enumerates an undefined set, names a missing oracle, or extends the boolean-test to cover an orphaned `THEN` clause. **No threshold direction was changed, no ID renumbered, no requirement removed.** The directional/`real_user_needed` thresholds remain R10/Pass-2's to validate; this pass only makes them *testable as written*.

The two dominant weakness classes:
1. **Free parameters presented as thresholds** (`β > 1`, "small-n threshold", "the operating point", "tiny slice", "<10 min") — strengthened by pinning a committed default **and/or** converting the contract to "the value is *recorded in the manifest/pre-reg and asserted equal*" so the test is green/red without a hidden decision.
2. **`reviewer audit` / `checklist` as the sole measurement oracle** (NFR-019, NFR-020, NFR-033, NFR-049, NFR-055) — strengthened by promoting the mechanical predicate already implied to the **primary** oracle and demoting the human review to a *secondary* corroboration, so CI is the gate.

---

## Part A — Functional Requirements (FR-030 … FR-054)

### FR-030 — PASS
GWT + boolean-test are fully mechanical (string/int equalities against a version-pinned loader). No change.

### FR-031 — PASS
Boolean-test enumerates all five pinned values + the content-swap injection and asserts RED-on-mutation / green-on-truth. Fully covered. No change.

### FR-032 — STRENGTHENED (oracle for "never head-truncation")
- **Weak criterion:** `THEN … the draw never uses naive file-order head-truncation` and boolean-test `no head-truncation code path is taken`. "No code path is taken" has **no named oracle** — at runtime you cannot observe a path *not* taken without an assertion hook; the test as written is not mechanically decidable.
- **Strengthened:** the boolean-test now binds a concrete oracle — **(i)** a static/import-graph assertion that the assessment sampler entrypoint does **not** reference the `max_samples` head-truncation symbol (`converter L82-84` / `loader L73`), **AND (ii)** a behavioral assertion that for a fixture corpus whose positives are deliberately back-loaded (positives placed after record N), the seeded draw still reaches each cell's `target_n` (head-truncation would fail this). Either failure ⇒ `False`.

### FR-033 — PASS
Four-state `power_class` enumerated, shortfall typed as integer-on-realized-positives, verdict ∈ a closed 3-set with numeric cuts (0.80/0.999) cited from code, `NOT_ASSESSED` defined. Fully decidable. No change.

### FR-034 — PASS
"Canonical-form equality (sorted keys + fixed float repr)" is a defined oracle; every enumerated field is named; non-empty-caveat is construction-enforced. No change.

### FR-035 — STRENGTHENED (undefined "results-bearing" predicate)
- **Weak criterion:** boolean-test `no fourth results-bearing preset exists`. "Results-bearing" is **undefined** — a CI job cannot enumerate presets and decide which are "results-bearing" without a predicate.
- **Strengthened:** pin the closed set — the CLI preset enumeration **equals exactly `{powered-representative, full-corpus, smoke}`** (set equality, not "no fourth"); any preset that emits a metrics/CI/leaderboard artifact and is not in that set ⇒ `False`. This makes "results-bearing" operational (emits a scored artifact) and the count a set-equality assertion.

### FR-036 — PASS
`preset == "full"`, `records_scored == dataset.record_count(version)` (explicitly *not* a literal), pre-reg existence, and the inferential-target label (descriptive→no-CI / super-population→CI) are all mechanical. No change.

### FR-037 — PASS
`not_statistically_valid == true` + "no CI field and no p-value field is non-null anywhere" + spine-completed is a fully decidable triple. No change.

### FR-038 — STRENGTHENED (deferred names left the test undecidable)
- **Weak criterion:** run-type names `(smoke / dev / leaderboard-submission / filing-grade, names finalizable in Design)`; the boolean-test asserts each run-type "resolves to its declared profile" but the **profile table is not pinned in the requirement**, so "its declared profile" has no referent a test can read.
- **Strengthened:** the boolean-test now binds to a **committed run-type→profile table** (a fixture/enum the requirement *references*, even if names change in Design): the test asserts (a) the enum is non-empty and each member maps to a **fully-specified** `{rigor_bar ∈ {full-AX005, suppressed}, prereg ∈ {enforced, opt-in, off}, sample_mode ∈ {full, sample}}` triple with **no field unset**, and (b) the four behavioral invariants hold regardless of the chosen names: a `full-AX005` member omitting any AX-005 element ⇒ `False`; a `suppressed` member emitting any non-null CI/p-value ⇒ `False`. The *names* are deferrable; the *table being total and the invariants holding* is the test.

### FR-039 — STRENGTHENED (span-match mode value-space unpinned)
- **Weak criterion:** `a declared span-match mode (exact vs relaxed/overlap)` — "declared" is asserted but the **legal value-set is not closed**, so a run could stamp an arbitrary string and pass "a mode is declared".
- **Strengthened:** boolean-test asserts `span_match_mode ∈ {exact, relaxed-overlap}` (closed set) AND that the *same* declared mode is the one consumed by `compute_span_metrics` (the declared value equals the value the metric bridge was called with) — a declared-but-unused or out-of-set value ⇒ `False`.

### FR-040 — STRENGTHENED (un-pinned small-n threshold)
- **Weak criterion:** `small-n / boundary (k∈{0,n} or n below a stated threshold) → Clopper-Pearson` — "a stated threshold" is a **free parameter**; without a committed value (or a recorded-and-asserted contract) the selection rule is not reproducible and the test cannot decide which method *should* have been chosen.
- **Strengthened:** the rule is made deterministic by contract — the **n-cutoff is a single value recorded in the manifest + pre-registration** (`small_n_cutoff`, default proposed **n < 30**, R10 to confirm the number), and the boolean-test asserts: every metric's `method` **equals the method the recorded cutoff dictates for that metric's `(k, n)`** (Wilson for proportions with `n ≥ cutoff` and `k ∉ {0,n}`; Clopper-Pearson for `k ∈ {0,n}` or `n < cutoff`; paired-bootstrap for differences). A method inconsistent with the recorded cutoff ⇒ `False`. (Pinning the *contract* — cutoff recorded + obeyed — is testable today even while the number stays directional.)

### FR-041 — STRENGTHENED (prose-only "stated in report text" has no oracle)
- **Weak criterion:** `the two-family split … is stated in the report text, not only in code`. "Stated in the report text" is **not mechanically assertable** without a target the linter can match.
- **Strengthened:** boolean-test now requires a **machine-checkable token contract** — the report carries a structured `inference_families` block listing exactly the two labels `{exploratory, confirmatory}` with `confirmatory.family_size` an integer `== #pairs × #metrics in the confirmatory set` (computed, not free-typed), and the prose section is detected by the **presence of that structured block** (the linter asserts the block; the prose renders from it). A missing block, a family_size ≠ the computed product, or only-one-family ⇒ `False`.

### FR-042 — PASS
The two-direction CI assertion (fabricated symbol unreachable from run/score/rate entrypoints AND audited symbols invoked) is a concrete static + call-graph oracle. No change.

### FR-043 — STRENGTHENED (multi-seed minimum unpinned; "never `unknown` unflagged")
- **Weak criterion (a):** `seed_variance_scope — either ≥2 sampling seeds … (INT-02 names a 3-seed minimum) or single-seed flag`. The text names **both** "≥2" and "3-seed minimum" without pinning which the test enforces — an ambiguous threshold.
- **Weak criterion (b):** `contamination_status … (never unknown unflagged)` — "unflagged" has no oracle.
- **Strengthened:** (a) the boolean-test enforces a **single committed minimum**: `seed_variance_scope == multi-seed ⇒ len(seeds) ≥ MIN_SEEDS` with **`MIN_SEEDS = 3`** committed (INT-02's named floor; R10 may relax to 2 with rationale) **and** a Kendall-τ value present; else `seed_variance_scope == single-seed` AND the run carries `rank-volatility: UNMEASURED`. (b) "unflagged" is operationalized: `contamination_status == unknown ⇒ a `contamination-uncontrolled` boolean is set True on every downstream metric of that system`; an `unknown` status with that flag absent on any of the system's metrics ⇒ `False`.

### FR-044 — STRENGTHENED ("pushed to remote" needs an oracle)
- **Weak criterion:** `the record is committed and the commit pushed to remote` and boolean-test `bound to a pushed-to-remote commit SHA`. "Pushed to remote" is **not locally decidable** by a CI job without a named check.
- **Strengthened:** boolean-test binds the oracle — the pre-reg commit SHA is **reachable on the named remote ref** (`git branch -r --contains <sha>` is non-empty against the configured origin, OR an equivalent remote-existence API check), asserted in CI; an SHA that exists only locally (not on any remote ref) ⇒ `False`. The hash-chain (`first run-record references the pre-reg commit`) and full-payload-field-set checks are already mechanical and retained.

### FR-045 — PASS
"Exactly one record per spine stage (6) sharing one run id, each with the full key set incl. `code_commit` + toolchain fingerprint" + the regression-contract fields present is a closed, countable predicate. No change.

### FR-046 — PASS
`{content_hash, code_commit, run_id, stage}` embedded on every artifact is a flat field-presence predicate. No change.

### FR-047 — STRENGTHENED (subjective "honest"; product-string ban needs a list)
- **Weak criterion:** the title/THEN lean on "honest"; the boolean-test clause `no product-verdict strings` does not say **which** strings — an open-ended "product-verdict language" is not enumerable.
- **Strengthened:** "honest leaderboard" is fully operationalized by the existing sub-predicates (CI on every number; ties greyed by Holm verdict; families not merged; registers emit) — those are kept as the definition. The product-string ban is pinned to a **committed forbidden-token list** (`{"SHIP-WITH-CAVEATS", "SHIP", "DEFER", "GO/NO-GO"}`, extensible) asserted absent from the LaTeX/CSV registers; a register containing any listed token ⇒ `False`. (Defines "honest" by its sub-tests and makes the negative check a literal set-membership scan.)

### FR-048 — STRENGTHENED (unbounded β; "available" precision-at-recall; un-pinned recall point)
- **Weak criterion:** `recall-priority Fβ (β>1)` — **β is a free parameter**; `a precision-at-fixed-recall readout is available` — "available" is not a hard presence assertion; `INT-04 operates at recall ≈ 0.90–0.93` — the fixed recall point is a **range, not a value**.
- **Strengthened:** boolean-test pins testable contracts: (i) the report emits an Fβ with **β recorded in the manifest/pre-reg** and **β ≥ 2** (committed default **β = 2**, R10 to confirm) **OR** a stated integer FN:FP cost ratio; (ii) **precision-at-fixed-recall is present (non-null)** at a **recall target recorded in the pre-reg** (committed default **recall = 0.90**, within INT-04's 0.90–0.93 band, R10 to confirm); (iii) AUPRC present; (iv) the operating point equals the pre-registered threshold rule (FR-044). A lone F1, a free/undeclared β, an absent precision-at-recall, or a post-hoc operating point ⇒ `False`.

### FR-049 — STRENGTHENED (undefined "worst-language / low-resource"; subjective "honesty signal")
- **Weak criterion:** `the worst-language / low-resource recall` — **"worst-language" and "low-resource" are undefined sets**; a linter cannot compute "the worst-language recall" without (a) the population of languages in scope and (b) the selection rule.
- **Strengthened:** operationalized — **worst-language recall** = `min over the languages present in the run's coverage envelope of per-language recall`, reported with the **language label** that realizes the min (an `argmin`, fully computable); **low-resource** is pinned to an **enumerable predicate**: the set of languages whose realized positive count is below the LONG_TAIL tier target (`< 200`), so "low-resource recall" = recall restricted to that committed set. The boolean-test asserts both the `min`+label and the low-resource-set recall are present and non-null; the "stripping any honesty signal invalidates" clause is retained but each "honesty signal" is now one of the **enumerated** structured flags (caveat / convergence-block / per-cell power_class / contamination flag / rank-volatility scope / worst-language argmin / low-resource recall / named-and-pending), so "any signal" ranges over a closed list.

### FR-050 — PASS
`{pre-reg hash, commit SHA, run id}` embedded; every metric cell carries inline `{CI, provenance hash, synthetic-only caveat}`; Art-11 label present; reproduces-from-manifest — all flat presence/equality predicates. No change.

### FR-051 — STRENGTHENED ("genuinely held out" + "signed attestation" need oracles)
- **Weak criterion:** `held-out labels genuinely held out` and `a signed attestation` — "genuinely" is subjective; "signed" has no verification oracle (what makes a signature valid?).
- **Strengthened:** (i) "genuinely held out" → the **scoring API surface test** (already in NFR-049) is the oracle: a call sequence to the scoring endpoint **never returns held-out label values** (response schema asserted to exclude the label field); (ii) "signed attestation" → a **structured attestation record is present and well-formed** (required fields `{submitter_id, statement, signature, signed_at}` all non-empty) and, where a signing scheme is configured, the signature **verifies against the configured public key**; an entry missing the attestation record or failing signature verification (when a key is configured) ⇒ `False`; (iii) `contamination_status == unknown ⇒ entry rejected` is retained as a hard reject predicate.

### FR-052 — STRENGTHENED (sole oracle is structural-presence, but "on every report page" + recusal needs a predicate)
- **Weak criterion:** `appears … on every report page` and `a managed conflict … is recorded with an explicit disclosure + recusal record`. "Every report page" needs a per-page assertion; "a managed conflict" has no trigger predicate (when is a recusal *required*?).
- **Strengthened:** boolean-test pins: (i) the governance block `{corpus_owner, label_holder, evaluator}` (all non-empty) is a **structured run-record field** AND is rendered on **each emitted report page/section** (per-page presence asserted by the report linter, not a single front-matter check); (ii) a **conflict trigger predicate** — *if* any `evaluator` identity appears in the submitting-system ownership metadata of any leaderboard entry, *then* a `recusal_record` for that identity must be present; the trigger-without-record case ⇒ `False`. (Makes recusal a conditional with a computable antecedent, not a judgment call.)

### FR-053 — PASS
"Every one of the 63 types has a regulatory-regime mapping kept legally distinct per regime; the artifact is versioned/updateable with provenance" is a per-type completeness + per-regime-distinctness predicate (count == 63; no cross-regime equivalence field). No change.

### FR-054 — PASS
"Persistent DOI (not only a SHA) AND BibTeX + citation template AND a synthetic-only claims policy" is a flat presence triple. No change.

**FR result: 12 strengthened (FR-032, 035, 038, 039, 040, 041, 043, 044, 047, 048, 049, 051, 052) — correction: 13 IDs listed; see count note below.**

> **Count note:** the FR strengthenings are **FR-032, FR-035, FR-038, FR-039, FR-040, FR-041, FR-043, FR-044, FR-047, FR-048, FR-049, FR-051, FR-052 = 13 FRs**. (The summary table groups FR-051+FR-052 governance pair under one finding theme; the applied edits touch all 13 IDs. Authoritative per-ID list is this line.)

---

## Part B — Non-Functional Requirements (NFR-019 … NFR-055)

### NFR-019 — STRENGTHENED (sole-oracle drift: "+ reviewer audit")
- **Weak criterion:** `Measure: import-graph / call-graph static check … + config assertion … + reviewer audit`. The static + config checks are mechanical and sufficient; appending `reviewer audit` is fine as corroboration but the requirement does not state that the **CI checks alone are the gate** — leaving ambiguity about whether green requires a human.
- **Strengthened:** `Measure:` reordered to make the **CI-blocking predicate the gate** ("**CI gate (blocking):** import-graph assertion `SignificanceTester` unreachable from the assessment entrypoint AND `run_significance_tests == False`; reviewer audit is a *secondary, non-gating* corroboration"). Threshold unchanged.

### NFR-020 — STRENGTHENED (sole-oracle drift on the human diff)
- **Weak criterion:** `Measure: grep-based forbidden-pattern lint … (CI-blocking) + reviewer diff of the two implementations`. Same pattern — but the **forbidden-pattern set is not enumerated as a committed list**, so the grep is under-specified (which patterns?).
- **Strengthened:** the forbidden-pattern set is pinned to a **committed regex list** (the three verified fabrication signatures: `*(1-*)/100`, `np.random.normal`, `n_approx`/`pooled_sd = 0.1`/`sqrt(n_approx)/0.05`), and `Measure:` states the grep over the **declared run-path module set** is the **CI gate**; reviewer diff is secondary. Threshold (zero occurrences) unchanged.

### NFR-021 — PASS
"Local `random.Random(seed)`; byte-identical same-seed re-run regardless of ambient `random.seed`; static check for `np.random.`/bare `random.` global calls on the run path" — a mechanical byte-equality test + a static scan. No change.

### NFR-022 — PASS
Integer-guarded `(k,n)`, `0≤k≤n`, `TypeError/ValueError` on fractional/bool, the reidx-02 guard tests + run-path int-assertion. Fully mechanical. No change.

### NFR-023 — STRENGTHENED (un-pinned "pre-registered cutoff")
- **Weak criterion:** `small-n / boundary (… or n below a pre-registered cutoff)`. The cutoff is a **free parameter**; the linter cannot decide the *correct* method without the cutoff value, and "recorded in the manifest and pre-registration" is asserted for the *rule* but not as a **value-equality contract**.
- **Strengthened (mirrors FR-040):** the `small_n_cutoff` is a **single recorded integer** (default **n < 30**, R10 to confirm) and the linter's pass condition is: every metric's `method` **matches the method the recorded cutoff prescribes** for its `(k, n)` class. The threshold "100% of metrics carry `{n, ci_low, ci_high, method}`; zero bare estimates" is unchanged; the addition is the *deterministic resolvability* of `method`.

### NFR-024 — STRENGTHENED (multi-seed minimum unpinned)
- **Weak criterion:** `corpus-draw … variance is either measured (≥ 2 sampling seeds, with Kendall-τ) or flagged single-seed`. `≥ 2` here vs FR-043's "3-seed minimum (INT-02)" is an **internal inconsistency** — the same quantity has two thresholds across the doc.
- **Strengthened:** pinned to the **single committed minimum `MIN_SEEDS = 3`** (consistent with FR-043; R10 may relax to 2 with recorded rationale), with the Kendall-τ block present when multi-seed and `rank-volatility: UNMEASURED` present when single-seed. `Measure:` predicate (presence of `scope` + the ≥`MIN_SEEDS`/Kendall-τ block or the single-seed flag) unchanged in form, now with a concrete bound.

### NFR-025 — PASS
`inferential_target ∈ {exact-on-corpus, super-population}` + linter rule (census + no super-pop declaration ⇒ CI fields absent) is a closed, decidable predicate. No change.

### NFR-026 — PASS
"Every confirmatory pairwise row has a McNemar p-value + a paired-bootstrap delta CI; a directional claim with no paired test is rejected" — flat per-row presence + a hard-reject predicate. No change.

### NFR-027 — STRENGTHENED (prose-location oracle; family-size computability)
- **Weak criterion:** `family declaration appears in the report text and the pre-registration, not only in code`. Same prose-location problem as FR-041 — "appears in the report text" needs a matchable target.
- **Strengthened (mirrors FR-041):** the linter asserts a **structured `inference_families` block** (exactly two labels; `confirmatory.family_size` integer **== #pairs × #metrics**, computed) present in **both** the report payload and the pre-reg payload (parity check); prose renders from the block. A missing block in either, or a family_size ≠ the product ⇒ fail. Threshold (two families, Holm, size printed) unchanged.

### NFR-028 — PASS
"For every adjacent rank pair, a significant Holm decision exists OR the pair is rendered as a tie" — a per-adjacent-pair decidable predicate. No change.

### NFR-029 — PASS
Four named fields + the ±2RD interval + the stopping rule + NOT-converged-on-headline; the linter asserts the block completeness. Mechanical. No change. (G4 "never an extrapolated round count" is enforced by *reporting max-RD±2RD*, which is the positive contract — decidable.)

### NFR-030 — PASS
Canonical-form manifest diff empty + byte-diff empty under `{seed, RNG fingerprint, sampler version}`. Fully mechanical. No change.

### NFR-031 — STRENGTHENED ("pushed to remote" oracle; mirrors FR-044)
- **Weak criterion:** `bound to a git commit SHA pushed to remote` — not locally decidable without a named remote check (same gap as FR-044).
- **Strengthened:** `Measure:` binds the remote-existence oracle (`git branch -r --contains <sha>` non-empty against the configured origin, or remote-API equivalent) as the CI predicate for the "pushed" clause; local-only SHA ⇒ fail. The field-completeness + hash-chain + report-embeds-hash + lineage-count predicates are already mechanical and retained.

### NFR-032 — PASS
"A pre-reg exists for the full-corpus run and passes NFR-031's equality set" — delegates to NFR-031's (now-strengthened) mechanical check. No change needed beyond NFR-031's fix, which it inherits.

### NFR-033 — STRENGTHENED (sole-oracle drift "+ reviewer audit"; table not pinned)
- **Weak criterion:** `Measure: table-driven test asserting each run-type maps to its exact (bar, sample-mode, pre-reg) tuple; reviewer audit of the preset table`. The table-driven test is mechanical, but "its exact tuple" needs the **table to be a committed fixture** the test reads, and `reviewer audit` should not be co-equal to the gate.
- **Strengthened (mirrors FR-038):** the run-type→profile table is a **committed enum/fixture**; the **table-driven test is the CI gate** asserting every member maps to a **total** `{rigor_bar, sample_mode, prereg}` triple with no unset field **and** the four behavioral invariants; `reviewer audit` demoted to secondary. Threshold (fixed/auditable mapping; pre-reg never a global on/off) unchanged.

### NFR-034 — PASS
`preset == "smoke"` + non-strippable `not_statistically_valid: true` + zero non-null CI/p-value fields — a closed decidable triple. No change.

### NFR-035 — PASS
Four-state classification on realized positives, each `target_n` reproduced from its `(p_ref, half_width, α)` triple via `required_n` (cited 1522/753/200), `PowerMatrix.verdict()` with numeric cuts (0.999/0.80) cited from `power.py:L351-361`, "never silently LARGE". Fully grounded and decidable. No change.

### NFR-036 — PASS
"Each under-tier cell has an integer `realized_positive_shortfall` + the non-strippable binding; reuses `lattice_audit.deficits` (observed+deficit per cell)". Mechanical integer-presence + construction-binding. No change.

### NFR-037 — PASS
Three-way distinction (UNDER_SAMPLED vs CORPUS_LIMITED vs EMPTY) computed by comparing cell realized positives to the sample draw AND the full-corpus positive total via `audit_positives`. A decidable comparison. No change.

### NFR-038 — STRENGTHENED (memory bound stated as O()-notation, not an asserted number)
- **Weak criterion:** `working-set memory bounded by … O(#committed-cells) ≈ O(730) keys … independent of the 575,604 record count` with `Measure: peak-RSS bound test that holds constant as the record count scales`. "Holds constant" is the right idea but **no numeric tolerance/oracle** is given — "constant" under measurement noise needs a bound (peak-RSS is also noisy and includes interpreter baseline, so a raw "constant" assertion is flaky/undecidable).
- **Strengthened:** the bound is made a **testable inequality on the data-structure size, not raw RSS**: the test asserts the sampler's candidate-key working set has **`len(keys) ≤ 730`** (the committed-cell count, the true O-bound) across corpus sizes — a deterministic integer assertion immune to RSS noise — **and** (optionally, as a secondary signal) peak-RSS growth between a 10k-record and a 100k-record run stays **within a stated tolerance (≤ 1.10×)** rather than "constant". Primary gate = the `≤ 730` key-set assertion (`real_user_needed: false` retained).

### NFR-039 — PASS
"Design-point triple per tier + coverage envelope (which of 63×60×5 committed) + every uncovered critical type listed `NOT_ASSESSED`" — a manifest field-completeness + per-uncovered-type enumeration. Decidable. No change.

### NFR-040 — STRENGTHENED (subjective "correctly")
- **Weak criterion:** `pii-rate-elo loads PII-Anon v2.0.0 correctly`. "Correctly" is subjective; the operational meaning must be the four metadata equalities + the crosswalk test.
- **Strengthened:** "correctly" is **replaced by its operational definition** — `version == "2.0.0"` AND `license ∈ {CC0-1.0, CC0}` AND `record_count == dataset.record_count("2.0.0")` (== 575,604 for full) AND citation references v2.0.0 AND the crosswalk lossless/explicit-lossy test green. (The pieces already exist in the text; the strengthening removes the bare adjective and makes the conjunction the threshold.)

### NFR-041 — PASS
Five-tuple pinned to canonical values from `test_doc_drift.py` (575,604 / 2,486,438 / 2.0.0 / 63-derived) + schema fingerprint + content hash; "mutate each pin → assert red". Fully mechanical. No change.

### NFR-042 — PASS
"Exactly 6 stage records, each field-complete with the full key set + toolchain fingerprint, sharing one run id". Closed countable predicate. No change.

### NFR-043 — PASS
"`{run id, stage, code_commit, content hash}` on every emitted artifact + a `MANIFEST.sha256` content-hash index". Flat presence + index existence. No change.

### NFR-044 — PASS
Round-trip serialize/deserialize asserts the caveat survives on every artifact; attempt-to-empty raises (construction-enforced via `DesignProvenance.__post_init__`). Mechanical. No change.

### NFR-045 — PASS
`scoring_family` declared; zero merge paths (static check); pseudo carries no bare-F1 headline. Decidable static + field check. No change.

### NFR-046 — STRENGTHENED (unbounded β; un-pinned operating point; mirrors FR-048)
- **Weak criterion:** `recall-priority Fβ with β > 1` (free β) + `operating point matches the pre-reg threshold rule` (the rule's recall point not pinned). Same unbounded-parameter gap as FR-048.
- **Strengthened (mirrors FR-048):** the linter asserts an Fβ with **β recorded and β ≥ 2** (default 2, R10) OR a stated integer FN:FP cost; AUPRC present; the operating point's **recall target is recorded in the pre-reg** (default 0.90, R10) and the emitted point equals it. Threshold form ("instead of a lone F1") unchanged; the parameters are now pinned/recorded-and-asserted.

### NFR-047 — STRENGTHENED (undefined "worst-language / low-resource"; mirrors FR-049)
- **Weak criterion:** `worst-language / low-resource recall` — undefined sets (same as FR-049).
- **Strengthened (mirrors FR-049):** worst-language recall = `argmin over languages in the coverage envelope of per-language recall` (computable, reported with the language label); low-resource = the committed set of languages with realized positives `< 200` (LONG_TAIL target). The linter asserts both present + that **removing any enumerated honesty flag fails validation**, where "honesty flag" ranges over the closed enumerated list (caveat / convergence / per-cell power_class / contamination / rank-volatility / worst-language argmin / low-resource recall). The pre-reg/run-id binding predicate is unchanged.

### NFR-048 — PASS
`contamination_status ∈` a closed 3-set; `unknown` ⇒ rejected (hard predicate); attestation-presence check for leaderboard run-types; downstream flag propagation asserted. Decidable. No change. (The attestation *validity* oracle is strengthened under FR-051; NFR-048's presence check is sufficient at the NFR layer.)

### NFR-049 — STRENGTHENED (sole oracle is "governance checklist audit")
- **Weak criterion:** `Measure: governance checklist audit + API-surface test (held-out labels never returned) + submission-provenance log present`. The **API-surface test** and **log-present** check are mechanical, but a `governance checklist audit` listed first reads as the primary oracle, and a "checklist" is not itself CI-assertable.
- **Strengthened:** `Measure:` promotes the **two mechanical predicates to the CI gate** — (i) API-surface test: a call sequence to the scoring endpoint returns a response whose schema **excludes the held-out label field** (asserted), (ii) the submission-provenance log record is present and well-formed; the `governance checklist` is demoted to a *secondary human corroboration*. Threshold (held-out protected + provenance-stamped/blind) unchanged.

### NFR-050 — PASS
"The four cores import only stdlib (no numpy/scipy on the CI/paired/power path); heavy deps behind a lazy guard; import-graph test + 'module import triggers no heavy import' test (CI-blocking)". The `etc.` in `math, random, etc.` is illustrative inside a **negative** assertion (no third-party numeric lib), so it does not weaken the test — the predicate is "imports ∩ {third-party numeric libs} == ∅", which is decidable. No change.

### NFR-051 — PASS
"`pytest`, `ruff`, `mypy` all pass in the `pii-rate-elo-pipeline` venv". Three named gates, mechanical. No change.

### NFR-052 — PASS
"`lattice --check` reports exactly 730 cells @ `47c3a8f`; exits non-zero on drift". A numeric + exit-code oracle. No change.

### NFR-053 — PASS
"`validate.py --lattice` audits per committed cell in one streaming pass, exits non-zero on any shortfall; a test re-enables it if disabled". Mechanical exit-code + meta-test. No change.

### NFR-054 — PASS
"record count / annotation count / entity-type count / version identical across all canonical docs (zero drift); `pytest -k nfr_013` green; tags intact". A numeric zero-drift + suite-green oracle. No change.

### NFR-055 — STRENGTHENED (sole-oracle drift "+ reviewer audit")
- **Weak criterion:** `Measure: static check + reviewer audit over CAP-02-added code`. The static check ("zero merge paths") is mechanical; `reviewer audit` should not be co-gate.
- **Strengthened:** `Measure:` states the **static check is the CI gate** (zero code paths merge the four families — asserted over the CAP-02-added module set), `reviewer audit` demoted to secondary. Threshold (zero merge paths; NFR-005 invariant holds) unchanged.

**NFR result: 15 strengthened — NFR-019, NFR-020, NFR-023, NFR-024, NFR-027, NFR-031, NFR-033, NFR-038, NFR-040, NFR-046, NFR-047, NFR-049, NFR-055** *(13 IDs)* **+ the two cross-doc threshold-consistency pins (the `MIN_SEEDS=3` reconciliation in NFR-024↔FR-043 and the `small_n_cutoff` pin in NFR-023↔FR-040 also touch the contract NFR-032 inherits).** Authoritative per-ID applied-edit list: **NFR-019, NFR-020, NFR-023, NFR-024, NFR-027, NFR-031, NFR-033, NFR-038, NFR-040, NFR-046, NFR-047, NFR-049, NFR-055 = 13 NFRs** plus **NFR-021 left as-is** (already strong). See count reconciliation below.

---

## Count reconciliation (authoritative)

The summary table's "15" for NFRs counted two cross-document consistency pins as separate findings. The **applied per-ID edits** are:

- **FRs edited in place (13):** FR-032, FR-035, FR-038, FR-039, FR-040, FR-041, FR-043, FR-044, FR-047, FR-048, FR-049, FR-051, FR-052.
- **NFRs edited in place (13):** NFR-019, NFR-020, NFR-023, NFR-024, NFR-027, NFR-031, NFR-033, NFR-038, NFR-040, NFR-046, NFR-047, NFR-049, NFR-055.
- **Total criteria strengthened (applied edits): 26.**

The "27" in the headline counts the **internal-inconsistency reconciliation** (the `≥2`-vs-`3-seed` threshold clash between NFR-024 and FR-043) as a distinct *finding* even though it is fixed by edits already listed under both IDs. The **authoritative applied-edit count is 26 requirements** (13 FR + 13 NFR); the **distinct findings count is 27** (26 per-ID + 1 cross-doc consistency finding). Both numbers are reported for transparency; the load-bearing figure for "requirements edited" is **26**.

---

## Cross-cutting findings (applied across multiple IDs)

1. **Free distributional/statistical parameters left unbound** (β, small-n cutoff, fixed-recall point, multi-seed minimum). Fixed by pinning a **committed default** AND converting the contract to **"value recorded in manifest/pre-reg and asserted obeyed"**, so the test is green/red today while R10 keeps the right to re-tune the number. (FR-040/043/048, NFR-023/024/046.)
2. **`reviewer audit` / `governance checklist` co-listed with the mechanical oracle.** Demoted to *secondary corroboration* everywhere; the **CI-assertable predicate is made the gate**. (NFR-019/020/033/049/055.)
3. **Subjective adjectives on the run path** (`correctly`, `honest`, `genuinely`, "results-bearing"). Replaced by their operational conjunctions / closed sets. (FR-035/047/051, NFR-040.)
4. **Undefined sets** ("worst-language", "low-resource"). Operationalized as `argmin` over the coverage-envelope languages + the `< 200`-realized-positive committed set. (FR-049, NFR-047.)
5. **"Pushed to remote" not locally decidable.** Bound to `git branch -r --contains <sha>` (or remote-API) as the CI oracle. (FR-044, NFR-031.)
6. **Prose-only "stated in the report text".** Bound to a **structured `inference_families` block** the linter asserts; prose renders from it. (FR-041, NFR-027.)
7. **One internal-inconsistency** (`≥2` vs `3-seed`) reconciled to a single committed `MIN_SEEDS = 3` across both docs.

All directional numbers introduced (β=2, small_n_cutoff, recall=0.90, MIN_SEEDS=3) are flagged **R10-to-confirm** and are pinned as *defaults that are recorded-and-asserted*, never as silent constants — consistent with the brief's "thresholds are directional; R9 strengthens testability, R10 validates the number" split and with AX-002 (recorded provenance) / AX-pii-anon-005 (pre-registered analysis plan). **R10 update (2026-06-01):** `small_n_cutoff` was **lowered 30 → 15** as the resolution of a DIVERGED threshold-validation outcome (NFR-023; see `_threshold-validation/findings-summary.md`) — both personas + the cited binomial-CI literature agree the n-based Clopper-Pearson switch is over-conservative and that no canonical integer exists; the boundary clause (`k∈{0,n}`→Clopper-Pearson) and the determinism/manifest-recording contract are firm, only the n-switch integer remains `real_user_needed: true` for Pass-2. Pin kept reconciled across NFR-023 ↔ FR-040.

---

## Methodology & Epistemic Honesty
- This audit changes **only verification criteria** (boolean-tests, `Measure:` oracles, and the bound parameters those tests read). No FR/NFR **intent**, priority, trace, or ID was altered. The directional thresholds remain `provisional_status: AGENT_SIMULATED` and are R10/Pass-2's to validate.
- Every strengthening is **conservative**: where a number had to be introduced to make a test decidable, it is introduced as a **recorded-and-asserted default** (the *contract* "the value is recorded and obeyed" is what the test checks), so the requirement is testable today and the number stays re-tunable.
- The audit is grounded in the canonical Discovery artifacts (`discovery-report.md` §8 Open Items 1–13, G1–G7 rails, C1–C10; `04-use-cases.md` UC-16…23 acceptance signals; `personas.md`) and the R3 `interview-synthesis.md` threshold signals; the code/line evidence the criteria bind to is the FRs'/NFRs' own firsthand file-reads at HEAD 2026-06-01.
