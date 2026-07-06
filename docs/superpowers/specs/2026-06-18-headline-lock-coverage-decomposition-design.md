# Design Spec — Headline-Lock: Coverage-Ceiling Decomposition (B-2 → B-1)

**Date:** 2026-06-18
**Repo:** `pii-anon-eval-data` (branch `paper1-tier-a-experiments`)
**Author/PI:** Subhash Holla (with Claude)
**Status:** DRAFT — awaiting PI review before plan

---

## 0. Context

The NeurIPS Datasets & Benchmarks paper's **primary contribution** is **CL-02b** (the C1 headline):
the coverage ceiling is a *structural decomposition*, not a metric artifact —

> overall recall = coverage-fraction × within-reach skill (an identity); the within-reach skill factor
> is **coverage-independent** (orthogonal) and model-quality-driven ⇒ the coverage ceiling is a structural
> property of label-map design.

A paper-artifact extension scan (2026-06-18) of `pii-anon-research-paper/research-assist-artifacts/`
found that **the within-reach number the headline rests on is not computed anywhere in the dataset repo**.
`results/tier-a/coverage_ceiling.md` ships **only the overall** `r=0.797` (reachable/63 vs micro-recall);
the within-reach `r≈0.048`, the bootstrap/leave-one-out contrast, and the "≥2 crosswalks" robustness that
**SC-02b gates claim-lock on** exist only inside the paper's prose. This is the program's single biggest
**integrity gap**: the primary claim is asserted but not reproducible from released artifacts.

This sub-project is the **first work-stream of the current improvement iteration** and runs **before
sub-project 2C**, against the **frozen 63-type reference**, so nothing downstream contaminates it.

**Source of truth for the estimand** (read, do not paraphrase, when planning):
`02-literature/claims-document.md` CL-02b / **SC-02b**; `03-methodology/06-synthesis/preregistration.md §7`
(EX-01b + AMEND-01); `04-apparatus/00-preflight/preflight.md §A.2/§A.4.3`;
`04-apparatus/03-quality/determinism-data-validation-gates.md §2`.

**Ground truth verified against the repo (2026-06-18):**
- `results/baselines/tier1-en-all/baseline_results.json` is the committed v2.0.0 leaderboard run. It carries,
  **per detector**, `by_entity_type` (per-type counts → recall) **and** a `coverage` block
  (`of_total: 63`, `reachable_types`, `dropped_native`). Both B-2 and B-1 derive from this file —
  **no re-scoring is required.**
- The 11 leaderboard detectors are exactly: `aws, azure, flair, gcp, gliner, piiranha, presidio, regex,
  scrubadub, spacy, stanza`. The author's own `pii_anon` is **excluded** (COI) — keep it excluded.
- The canonical taxonomy is now **66** (`taxonomy.ENTITY_TYPE_COUNT == 66`); the headline denominator is
  **63** = the 66 minus the three 2A Art-9 types (`SEXUAL_ORIENTATION`, `TRADE_UNION_MEMBERSHIP`,
  `GENETIC_DATA`). The live `contract.py` lossiness reads `ENTITY_TYPE_COUNT` (66) — re-running the
  leaderboard now would yield `of_total: 66`. The headline must be pinned to a **frozen 63**, decoupled
  from the live taxonomy (AMEND-01 replay-drift hazard).

**Honesty axioms carried in** (from `00-axioms/validity-axioms.yaml`): AX-001 synthetic-only; AX-002 no
human IAA; AX-003 coverage-ceiling. n=11 forces the "law"→"structural bound" hedge (CL-02b Guard).

**Version posture:** working increments on the branch; content version stays `2.1.0`. No corpus
regeneration, no DOI/HF re-mint. This sub-project touches **analysis + a frozen reference artifact only.**

---

## 1. Goal & success criteria

**Goal:** make CL-02b reproducible from the dataset repo, pinned to a frozen 63-type reference, by (B-2)
freezing the per-detector label-map registry as a content-hashable artifact and (B-1) shipping a
deterministic `coverage_decomposition.py` that regenerates the SC-02b contrast under ≥2 monotone crosswalks.

**Done when:**

1. `results/tier-a/label_maps_63.json` exists: for each of the 11 detectors, its native→canonical(63) map,
   its **reachable set within the frozen 63**, and its dropped-native labels. `of_total` is hard-pinned to
   **63** and is **injected, not imported** from the live taxonomy. It is listed in
   `src/pii_anon_datasets/data/MANIFEST.sha256`.
2. `scripts/coverage_decomposition.py` exists and, from `label_maps_63.json` +
   `results/baselines/tier1-en-all/baseline_results.json`, computes per detector: `coverage = |reachable|/63`,
   `micro_recall` (overall), and `within_reach_recall` (recall restricted to the reachable types).
3. It computes and emits the **SC-02b contrast**: overall `r(coverage, micro_recall) ≈ 0.797` vs within-reach
   `r(coverage, within_reach_recall) ≈ 0.048`, each with a **Fisher-z CI**, a **bootstrap** distribution,
   and a **leave-one-out** sweep — testing the *drop*, not a hard cutpoint.
4. The contrast is recomputed under **≥2 independently-derived monotone crosswalks** (`XW-EXACT`,
   `XW-BROAD`); the decoupling **holds in sign and magnitude** under both (a structured assertion, not prose).
5. It reports **mean within-reach skill ≥ 0.6** with model-quality spread (e.g. regex/AWS high, scrubadub low).
6. Outputs `results/tier-a/coverage_decomposition.{json,md}`; `coverage_ceiling.md` gains a cross-link and a
   one-line "the within-reach decomposition lives in coverage_decomposition.md" pointer.
7. `tests/test_coverage_decomposition.py` pins the estimand (N=63 injected; reachable-rule fixed; the drop
   reproduces; sign holds under both crosswalks); full `pytest` green; `ruff` clean on changed files.
8. `scripts/check_version_sync.py` still OK (content stays 2.1.0). No corpus file changes.

**Explicitly OUT of scope:** the third **external-provenance** crosswalk `XW-BROAD′` (stays in the apparatus
EX-01b stage behind the prereg's content-hash-before-author firewall — authoring it here would break the
HARKing controls); any corpus regeneration; re-running the leaderboard; the v2.2.0 cut.

---

## 2. Component B-2 — Frozen 63-type label-map registry

**File:** `results/tier-a/label_maps_63.json` (new).

**What it contains** — a top-level object with a pinned header and a per-detector block:

```json
{
  "frozen_taxonomy_version": "v2.0.0-63type",
  "of_total": 63,
  "canonical_63": ["AGE", "API_KEY", "..."],
  "source_run": "results/baselines/tier1-en-all/baseline_results.json",
  "detectors": {
    "aws": {
      "native_to_canonical": {"AWS_NATIVE_LABEL": "CANONICAL_TYPE_OR_null", "...": "..."},
      "reachable_types": ["AGE", "..."],
      "dropped_native": ["CREDIT_DEBIT_EXPIRY", "..."],
      "reachable_count": 24
    }
  }
}
```

**Derivation (deterministic, no re-scoring):**
- `canonical_63` = the canonical 66 **minus** the three Art-9 types, computed and frozen here (the rule is
  documented; the *value* is serialized so the artifact is self-contained and taxonomy-independent).
- Per detector: `native_to_canonical` comes from the detector adapter's `label_map`
  (`baselines/<detector>_baseline.py`); `reachable_types` / `dropped_native` / `reachable_count` are taken
  from the existing run's `detectors.<name>.coverage` block (already computed against `of_total: 63`).
  These two sources MUST agree — the builder asserts the adapter map projects to exactly the run's
  `reachable_types`; a mismatch is a BLOCK (it would mean the registry and the scored run disagree).
- `of_total` is the literal `63`, **never** read from `taxonomy.ENTITY_TYPE_COUNT`. A test asserts the file
  says 63 even though the live taxonomy says 66.

**Why:** it is the literal content-hash object `preregistration.md §7` requires **before** EX-01b; it removes
the live-66 import hazard at the denominator source; and it is the provenance for every "reach/63" number.
It is **B-1's input.**

**Manifest:** append `label_maps_63.json` to `src/pii_anon_datasets/data/MANIFEST.sha256` via the existing
manifest-update path so it is content-hashed alongside the corpus artifacts.

---

## 3. Component B-1 — `scripts/coverage_decomposition.py`

**File:** `scripts/coverage_decomposition.py` (new). Pure-stdlib, deterministic, read-only on its inputs.

**Inputs:** `results/tier-a/label_maps_63.json` (B-2) + `results/baselines/tier1-en-all/baseline_results.json`.

**The identity (SC-02b):** for each detector, overall micro-recall = coverage-fraction × within-reach skill,
where coverage-fraction = |reachable|/63 and within-reach skill = recall computed **only over reachable types**.

**Per-detector quantities (×11):**
- `coverage = reachable_count / 63`.
- `micro_recall` = the run's overall micro recall (from `detectors.<name>.micro`).
- `within_reach_recall` = TP / (TP + FN) summed over **reachable types only**, from `by_entity_type` counts.
  (Unreachable types contribute recall exactly 0 by construction — excluding them isolates *skill*.)

**The contrast (the headline):**
- `r_overall = pearson(coverage, micro_recall)` across the 11 → expect ≈ 0.797.
- `r_within  = pearson(coverage, within_reach_recall)` across the 11 → expect ≈ 0.048.
- For each r: a marginal **Fisher-z 95% CI** + a marginal **bootstrap** (reported as context). The **SC-02b(a)
  gating test** is a **paired bootstrap of the drop** `Δr = r_overall − r_within` (resample the 11 detectors,
  recompute both correlations on the same resample): the headline holds iff this CI excludes 0 — far more
  powerful than comparing two marginal CIs, which overlap at n=11. Plus a **leave-one-out** sweep (11
  recomputations) confirming `r_within` stays near zero. No hard `|r|<0.15` cutpoint (retired by C4 as
  non-falsifiable at n=11). *(Operationalization refined during execution, PI-approved 2026-06-18 — the marginal
  Fisher-z CIs are wide/overlapping at n=11 and are reported but not the gate; faithful to SC-02b's "test the
  drop via bootstrap/leave-one-out, NOT a hard cutpoint".)*
- `mean_within_reach_skill ≥ 0.6` with the per-detector spread reported (SC-02b (c)).

**Robustness under ≥2 crosswalks (SC-02b (b), GATING):** run the entire contrast under each crosswalk and
assert the decoupling holds in **sign and magnitude** under both. See §4 for the crosswalks.

**Determinism:** a pure function of two committed files + a fixed bootstrap seed. The estimand parameters
(N=63, the reachable-type rule) are **injected as explicit constants/arguments, not imported** from the live
taxonomy, so a future taxonomy change cannot silently move the headline.

**Outputs:**
- `results/tier-a/coverage_decomposition.json` — machine-readable: per-detector rows, per-crosswalk
  `{r_overall, r_within, Δ, CIs, bootstrap summary, LOO}`, the skill summary, and a `verdict` block
  (does the drop hold under all crosswalks?).
- `results/tier-a/coverage_decomposition.md` — the human-readable headline table + the SC-02b verdict,
  honestly hedged (n=11 → "structural bound", synthetic-only).
- `results/tier-a/coverage_ceiling.md` — add a pointer to the decomposition (do not duplicate the table).

---

## 4. Crosswalks (XW-EXACT + XW-BROAD; XW-BROAD′ deferred)

The crosswalk-circularity objection (raised by four value-reviewers + the construct-validity validator) is
that the within-reach decoupling could be an artifact of *how we drew the label map*. SC-02b defuses it by
requiring the result to survive **≥2 independently-derived monotone crosswalks**.

- **XW-EXACT** — the existing per-detector maps (each adapter's `label_map`), i.e. the `reachable_types`
  already in `label_maps_63.json`. This is the default crosswalk.
- **XW-BROAD** — a deliberately **more permissive** map, derived by a **documented monotone rule**: for each
  detector, XW-BROAD's reachable set is a **superset** of XW-EXACT's — coarse native labels that XW-EXACT
  *drops* (e.g. a generic `MISC` / `DATE` / `NORP`) are mapped to their most-plausible canonical type rather
  than dropped. **Monotonicity is enforced** (a test asserts `XW-EXACT.reachable ⊆ XW-BROAD.reachable` for
  every detector). Independence is by construction (a different mapping philosophy — maximize reach vs.
  minimize false-positive risk). The per-detector XW-BROAD entries are enumerated in the implementation plan;
  the spec fixes the **rule + the monotonicity/independence constraints**, not the entries.
- **XW-BROAD′ (DEFERRED, out of scope here)** — a third, **externally-sourced** crosswalk (different
  provenance entirely). It belongs to the apparatus **EX-01b** stage and must be authored **after** the
  `label_maps_63.json` content-hash is frozen and **blind** to the within-reach result, per the prereg's
  content-hash-before-author firewall. Building it in this sub-project would break the HARKing controls.

The headline is **claim-locked** only if the drop holds under both XW-EXACT and XW-BROAD; the deferred
XW-BROAD′ later strengthens it to three independent provenances.

---

## 5. Testing & quality gates

`tests/test_coverage_decomposition.py` (new):
- **Registry pin:** `label_maps_63.json` reports `of_total == 63` and `len(canonical_63) == 63`, even though
  `taxonomy.ENTITY_TYPE_COUNT == 66` (the decoupling is the point).
- **Registry/run agreement:** each detector's adapter-map projection equals the run's `reachable_types`.
- **Estimand reproduces:** `r_overall ≈ 0.797` and `r_within ≈ 0.048` (within a tolerance), the drop is large
  (≈0.749), and the **paired bootstrap CI of the drop excludes 0** (the SC-02b(a) gate); leave-one-out keeps
  `r_within` near zero. (Marginal Fisher-z CIs are reported but not asserted-separated — they overlap at n=11.)
- **Monotone crosswalks:** for every detector `XW-EXACT.reachable ⊆ XW-BROAD.reachable`; the **sign** of the
  decoupling (drop > 0) holds under both crosswalks.
- **Skill floor:** `mean_within_reach_skill ≥ 0.6` with non-zero spread.
- **Determinism:** two runs of `coverage_decomposition.py` produce byte-identical JSON (fixed bootstrap seed).
- **Injection-not-import:** the estimand's N is passed in / constant, and changing the live taxonomy does not
  change the emitted `of_total`/denominator (guard test).

Gates: full `pytest` green; `ruff` clean on the two new files; `scripts/check_version_sync.py` OK
(content stays 2.1.0); `MANIFEST.sha256` updated and consistent.

---

## 6. Honesty

This sub-project **is** the honesty fix for two of the scan's flags:
- **Flag #1** (within-reach r not computed) → B-1 makes it reproducible from released artifacts.
- **Flag #2** (live `ENTITY_TYPE_COUNT==66` vs reach/63 drift) → B-2 freezes the 63 denominator.

All numbers stay synthetic-only (AX-001); no human IAA is claimed (AX-002). The CL-02b Guard is honored: the
`coverage_decomposition.md` states the mechanism (unreachable types → recall exactly 0 → overall recall
upper-bounded by coverage), frames the contribution as the coverage-independent within-reach factor + the
structural framing (not the correlation), and hedges "law" → "structural bound" at n=11.

---

## 7. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Adapter `label_map` and the run's `coverage.reachable_types` disagree | Builder asserts equality per detector; BLOCK + report on mismatch (do not silently prefer one). |
| Live taxonomy (66) leaks into the 63 denominator | N injected, never imported; a guard test changes the taxonomy in-test and asserts `of_total` stays 63. |
| XW-BROAD is not genuinely independent (just XW-EXACT relabelled) | Document the differing philosophy; enforce strict superset monotonicity; require the drop to hold in sign+magnitude, not identical numbers. |
| Authoring XW-BROAD′ here would break HARKing controls | Explicitly deferred to EX-01b; spec ships only XW-EXACT + XW-BROAD. |
| Bootstrap non-determinism | Fixed seed; determinism test asserts byte-identical reruns. |
| Reproduced numbers drift slightly from the paper's 0.797/0.048 | Tolerance-based assertions; the artifact becomes the source of truth and the paper prose is re-synced to it (paper-side, not this repo). |

---

## 8. Decisions locked (PI, 2026-06-18)

- This is the **first** work-stream of the iteration and runs **before 2C**, on the **frozen 63** reference.
- Ship **XW-EXACT + one internal XW-BROAD**; **XW-BROAD′** (external provenance) deferred to apparatus EX-01b.
- Estimand is **SC-02b verbatim**: test the **drop** (0.797→0.048) via Fisher-z CI + bootstrap + leave-one-out,
  not a hard cutpoint; require sign+magnitude under ≥2 monotone crosswalks; mean within-reach skill ≥ 0.6.
- Pin to **63**, injected not imported; `label_maps_63.json` is content-hashed in `MANIFEST.sha256`.
- Analysis-only: **no** corpus regeneration; content version stays **2.1.0**.

---

## 9. Deliverables

- `results/tier-a/label_maps_63.json` (frozen 63-type per-detector registry) + `MANIFEST.sha256` entry.
- `scripts/coverage_decomposition.py` + `results/tier-a/coverage_decomposition.{json,md}` + the
  `coverage_ceiling.md` cross-link.
- `tests/test_coverage_decomposition.py`; full pytest green; ruff clean; version-sync OK.
- All as working increments on `paper1-tier-a-experiments` (content version 2.1.0; no re-mint).
