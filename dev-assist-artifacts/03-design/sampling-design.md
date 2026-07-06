# Evaluation Sampling Design — Committed Lattice & Statistical Power (S-PWR)

**Stage 3 · Design note (extends DC-01 corpus/slices + DC-09 statistical-power & reporting engine)**
**Date:** 2026-05-29 · `provisional_status: AGENT_SIMULATED` (R10 10-persona ACCEPTED-WITH-CAVEATS; real-user Pass-2 noted)
**Operationalizes:** NFR-001, NFR-003, **NFR-018**, FR-029, AX-pii-anon-003 (at crossed-cell granularity).
**Grounding:** NIST/SEMATECH e-Handbook §7.2.4.2 (proportion sample sizing) + §5.5.2 (D-optimal designs); Montgomery, *Design and Analysis of Experiments* (ch. 8 fractional factorial, ch. 11 optimal designs); Box–Hunter–Hunter, *Statistics for Experimenters*; Hedayat–Sloane–Stufken, *Orthogonal Arrays* (1999); Cochran, *Sampling Techniques* (1977); Lachin (1992) McNemar power. No `pii_eval_may26.md` in repo — grounded in NFR-001/AX-003 + the assessment references + the user-restated tiered targets.

---

## 0. Problem statement

The v2.0.0 corpus (159,891 records / 1,239,637 positive annotations; 63 entity types, 60 languages, 5 domains, 4 difficulties, ~14 adversarial types, 7 dimensions) is adequate for **marginal** claims but badly under-powered for **crossed** claims. Of the 60×63 = 3,780 language×entity-type cells, **73% are EMPTY and only 3.3% reach ≥753 positives**; domain×type reaches ≥753 in only 31% of cells. Powering the full 5-way grid to 753 each would need ~2.9M positives — infeasible and wasteful.

This note specifies a **committed evaluation lattice**: a balanced, estimable, *curated* subset of cells the benchmark commits to powering, with risk-tiered per-cell targets, enforced as a CI-blocking gate. Everything outside the lattice is reported as exploratory/low-power and excluded from headline claims.

---

## 1. Estimand model (what we commit to estimating)

On the logit of recall, the committed model is **main effects + three named 2-way interactions**:

```
η = μ + Lang_i + Entity_j + Domain_d + Diff_f + Adv_a + Dim_p
      + (Lang × Entity)_ij        ← headline multilingual×type interaction
      + (Domain × Track)_d,track   ← BOTH readings: evaluation-family AND adversarial-track
      + (Adv × Entity)_a,j         ← adversarial robustness per type
```

- **"Track" = both readings** (user decision): `evaluation-family ∈ {detection, anonymization, pseudonymization, re-identification}` AND `adversarial-track ∈ {clean, adversarial}`. Domain×Track commits both layers.
- Everything **not** in this model — unnamed 2-ways (Lang×Domain, Diff×Dim, …) and **all** interactions of order ≥3 — is deliberately **pooled into the residual** (not estimable). This is the honest scope boundary.

---

## 2. DOE construction

### 2.1 Why the classic catalogs don't fit
The six factors are **highly asymmetric mixed-level** (60 / 63 / 5 / 4 / ~14 / 7) and the realizable region is **constraint-restricted** (73% of Lang×Entity is structurally empty — e.g. `DEA_NUMBER` only co-occurs with clinical text). Therefore:
- **Fractional factorial / Taguchi L-arrays** (Box–Hunter–Hunter ch. 12–13; Montgomery ch. 8) require a common small level count (2–3) — incompatible with a 60- and a 63-level factor; collapsing languages destroys the per-language main effect we must publish. **Rejected.**
- **Strength-2 mixed-level orthogonal arrays** (Hedayat–Sloane–Stufken) are the right *family*, but covering a 63- and 60-level factor at strength 2 needs N ≥ 63·60 = 3,780 runs — it degenerates to the full grid the corpus can't fill. **Rejected as primary.**
- **Latin / Graeco-Latin squares** need equal level counts. Usable only as a sub-device for the small balanced factors (domain 5 × difficulty 4). **Partial.**

### 2.2 Recommended method: **forced estimability skeleton + balanced D-optimal fraction over the non-empty candidate set**
This is the textbook tool for asymmetric, mixed-level, constraint-restricted regions (Montgomery ch. 11 "Optimal Designs"; Atkinson–Donev–Tobias 2007; NIST §5.5.2):

1. **Model first** — fix the §1 estimand (main effects + 3 named 2-ways).
2. **Candidate set** — every cell that is (a) non-empty / synthesizable and (b) can reach its tier target after enrichment. (Respects the forbidden region natively.)
3. **Forced skeleton** — force-include every cell required to make each main-effect level estimable: each of the 60 languages, 63 entity types, 5 domains, 4 difficulties, ~14 adversarial types, 7 dimensions must appear ≥1× at ≥ its marginal target. **Guarantees all main effects are powered** regardless of the interaction selection.
4. **D-optimal augmentation** — over the remaining candidates, select the balanced fraction maximizing `det(XᵀWX)` for the *named 2-way terms only* (W = per-cell information weight ∝ tier `n` at `p_ref`). Construction by coordinate-exchange / Fedorov (Montgomery §11.2). **This runs at BUILD time only**; the result is frozen to `eval_lattice.json`, so the shipped artifact carries no runtime numeric dependency (honors NFR-004). The pure-stdlib fallback is a deterministic forced-skeleton + balanced round-robin selection (no optimizer), used if a build-time numeric dep is undesirable.

> **Curated, not Cartesian (R10 refinement #4):** the committed 2-way set is an editorially-curated balanced *fraction* — e.g. the language×type commitment is the **{12 high-resource languages} × {41 frequent types} = 492-cell rectangle**, a 7.7× reduction from the 3,780 Cartesian grid — NOT the full cross-product. Cardinality + projected budget are published (§5) and confirmed at the dry-run checkpoint.

### 2.3 Estimability / aliasing / resolution statement (quote this)
- **Estimable (clear):** all 6 main effects; the 3 named 2-ways. Within the named model these are **Resolution-V quality** — no main effect or named 2-way is aliased with another.
- **Deliberately confounded (NOT estimable):** every unnamed 2-way and all ≥3-way interactions are aliased into the residual. The design is **Resolution-IV-like for unnamed effects**, **Resolution-V for the named subspace** — we state this asymmetry rather than claiming uniform resolution.
- **Empty-cell caveat:** Lang×Entity is estimable **only on the committed co-occurring rectangle**, never globally (73% structurally empty). Surfaced by the audit as `EMPTY`; excluded from claims.

---

## 3. Per-cell tiered power targets

### 3.1 NIST proportion sizing
`n = ⌈ z²·p_ref·(1−p_ref) / d² ⌉` (NIST/SEMATECH §7.2.4.2; Cochran §4.4). `z₀.₉₇₅ = 1.959963984540054` — the exact constant already in `stats/intervals.py::_Z`, reused so the design path and the measured Wilson path share one z-table.

| Tier | p_ref | half-width d | derived n | **target** | rationale |
|---|---|---|---|---|---|
| **critical** | 0.99 | 0.005 (±0.5pp) | 1,521.2 | **≥1,522** | credential/financial/strong-gov-id: one miss = breach; resolve 0.99 vs 0.985 |
| **standard** | 0.98 | 0.010 (±1pp) | 752.9 | **≥753** | default detection-quality bar |
| **long-tail** | 0.95 | ~0.030 (±~3pp) | ~183→200 | **≥200** (flagged) | rare/lower-stakes types; explicitly caveated |

Targets are **recomputed** from `(p_ref, d)` in code and asserted (a test pins 1,522/753/200); never hand-typed (NFR-018 anti-drift). 2-way cell target = **max-of-members tier** (a cell touching any critical member → 1,522).

### 3.2 Two-gate distinction (R10 refinement #1 — load-bearing)
- **Corpus-power gate (NFR-018, this design):** "does the corpus hold ≥target positives in this committed cell?" — **count-based, monotone, NOT PR-flaky** (positives only grow; no sampling jitter). Enforced by `validate.py --lattice`.
- **Detector A/B regression gate (FR-002, separate):** comparing two systems' recall on shared gold MUST use a **paired McNemar / discordant-pair test** (not CI-overlap), with a stated minimum-detectable-regression per tier, FDR-corrected or main-effects-hard / interactions-advisory, phased in via observation mode. `stats/power.py::required_discordant_pairs()` sizes it.

### 3.3 McNemar paired-comparison efficiency
The benchmark's primary use is A-vs-B on the **same** gold spans → a paired binary design (McNemar; Lachin 1992; NIST §7.3). The paired recall-difference estimator has variance ≈ `p_disc / n` (only the discordant pairs `b+c` are informative), versus ≈ `2·p(1−p)/n` for two independent arms. The efficiency ratio is `p_disc / (2·p(1−p))`, which is **< 1 (paired more efficient) exactly when `p_disc < 2·p(1−p)`** — i.e. when the two systems' errors are **positively correlated** (they miss the same hard cases), the realistic regime for two detectors on shared gold. At recall ≈0.98, `2·p(1−p) ≈ 0.039`; with correlated errors `p_disc ≈ 0.01–0.03` the paired comparison needs **≈2–4× fewer** positives. We therefore **size cells for the harder marginal target and get head-to-head A/B over-powered for free** in that regime (`stats/power.py::paired_vs_independent_ratio()` makes this computable and does not over-claim when `p_disc` is large).

### 3.4 Risk-tier assignment over the 63 types (derived from `taxonomy.py`, never a hand list)
Rule (priority order), implemented as a function over `ENTITY_REGISTRY`:
1. **CRITICAL (→1,522):** `category == "financial"` (12) ∪ credential/secret {API_KEY, PASSWORD, AUTHENTICATION_TOKEN, BIOMETRIC_ID, DEVICE_IDENTIFIER} (5) ∪ strong gov-id {SOCIAL_SECURITY_NUMBER, NATIONAL_ID_NUMBER, PASSPORT_NUMBER, DRIVER_LICENSE_NUMBER, VISA_NUMBER} (5) = **22 types**.
2. **LONG_TAIL (→200):** sensitive-attribute / soft-demographic quasi-identifiers, inherently rare & lower-stakes as a single span {POLITICAL_OPINION, RELIGIOUS_BELIEF, MARITAL_STATUS, HOUSEHOLD_SIZE, ETHNICITY, AGE, GENDER, NATIONALITY, EDUCATION_LEVEL, VEHICLE_MODEL} = **10 types**.
3. **STANDARD (→753):** the remaining **31 types**.
*(22 + 10 + 31 = 63 ✓.)* A critical type currently below 1,522 keeps the 1,522 *target* and is flagged "critical-but-underpowered" until enriched.

---

## 4. The committed lattice & budget arithmetic

### 4.1 Tier T1 — main-effect marginals (always committed + powered)
153 marginal cells (60 lang + 63 type + 5 domain + 4 difficulty + ~14 adversarial + 7 dimension). **Status from real metadata:**
- **Language marginals:** all 60 ≥210 records × ~7.75 annot/record ⇒ smallest ≈ 1,638 positives → **all ADEQUATE, most LARGE. Zero enrichment.**
- **Domain / difficulty / dimension marginals:** all far above target. **Zero enrichment.**
- **Entity-type marginals:** **total deficit = 10,905 positives** across 20 under-target types — 8 critical (e.g. VISA_NUMBER 166→1,522; DEVICE_IDENTIFIER 170; AUTHENTICATION_TOKEN 173; CRYPTOCURRENCY_ADDRESS 179; BIOMETRIC_ID 187; CREDIT_CARD_FRAGMENT 584; CVV/PIN 1,500→1,522), 6 standard (LAT_LONG/SOCIAL_MEDIA_HANDLE/VIN/PRESCRIPTION_NUMBER/URL ~174–186→753; POSTAL_CODE 556→753), 6 long-tail (VEHICLE_MODEL 163→200 … POLITICAL_OPINION 193→200).
- **Adversarial-type marginals:** confirmed by the audit (T3 below).

**T1 marginal net enrichment ≈ ~11k positives — trivial.**

### 4.2 Tier T2 — committed 2-way cells (the curated Broad fraction)
| Interaction | Committed (Broad) set | ~cells | per-cell target |
|---|---|---|---|
| **Language × Entity** | {12 high-resource langs: en,es,fr,de,zh,ja,ar,hi,it,ko,pt,nl} × {41 types with marginal ≥753} | ~492 | max-of-members (16 critical → 1,522; 25 standard → 753) |
| **Adversarial × Entity** | {~14 adversarial types} × {top ~30 critical+standard types}, balanced, all adversarial types ≥4× & all 22 critical ≥2× | ~280 | max-of-members |
| **Domain × Track** | domain(5) × eval-family(4) = 20 ∪ domain(5) × adv-track(2) = 10 | ~30 | standard 753 (critical where a critical-type slice) |

**Nominal T2 ceiling** (independent-cell upper bound): Lang×Entity ≈ 12×(16·1,522 + 25·753) ≈ **518k**; Adv×Entity ≈ **~250k**; Domain×Track ≈ **~23k** ⇒ ~0.8M nominal. **But** marginals/2-ways overlap and the 1.24M-positive corpus already covers most high-frequency cells (esp. all of `en`), so **net enrichment = the audit-reported shortfall only**, computed exactly by `power.py` over `eval_lattice.json` and **reported at the dry-run checkpoint before any generation**. Under Broad, expect a substantial corpus increase (potentially ~2–4×, concentrated in the 11 non-`en` head languages × rare-critical types and the adversarial×type cells) — the deliberate synthetic-data-advantage trade the user approved; the checkpoint confirms magnitude and allows dialing the fraction (e.g. 12×41 → 8×30) if the cost is unacceptable.

### 4.3 Tier T3 — explicitly uncommitted exploratory
Full Lang×Entity tail, unnamed 2-ways, all ≥3-way cells. Reported with actual n + CI but labeled `UNDER_POWERED`/`EMPTY` and **excluded from headline claims**. Zero committed budget.

### 4.4 Total vs the full grid
| | nominal positives |
|---|---|
| Committed lattice (T1 + T2, Broad) | ~0.8M ceiling; **net ≪** (audit-computed) |
| Full 5-way @753 (rejected) | ~2.9M |

---

## 5. Track-specific power (R10 refinement #2)

The 1,522/753/200 tiers are sized for **detection recall** (p≈0.95–0.99) and scope to the **detection track**. Anonymization / pseudonymization / RRS cells (DC-06/07/08) have a **different denominator** (paired personas / candidate set |C|) and operating point (p≈0.1–0.5), so they get a **parallel power ladder** sized at the re-id operating point:

`n_pairs = ⌈ z²·p·(1−p) / d² ⌉` at the re-id p — e.g. d=±3pp at p=0.3 → **~897 pairs/cell**; p=0.1 → **~385**.

v1 of `eval_lattice.json` enumerates the **detection-recall** committed cells (this work-stream). The **RRS/utility power ladder is a documented seam** filled when the S3/S4 scorers (DC-06/07/08, DC-09) land — its cells reference the 2,500 paired personas / ESRC-attack records already in the corpus.

---

## 6. Coverage vs depth (R10 refinement #5) & external-validity caveat (#3)

- **Coverage gate (presence):** the adversarial-type×entity-type space and the oracle/payload export (FR-017/018, DC-10) require **≥1 of every attack×type combination** + per-payload recognition accuracy — distinct from the depth (n≥target) gate, which scopes to cells backing a *published robustness claim*.
- **Non-strippable external-validity caveat:** because synthetic cells are *fillable by generation*, a tight committed-cell CI is precision **on a synthetic distribution**, not external validity. Every published per-cell metric carries a non-strippable synthetic-provenance + external-validity caveat (mirrors the RRS caveat, FR-009) and is **not citable as a standalone recall claim** absent the real-data correlation slice (FR-027). `DesignProvenance` (DC-09) embeds this.

---

## 7. Defensible-claim ladder (SMALL / ADEQUATE / LARGE)

| Granularity | Estimand | Status (committed lattice) | Allowed phrasing |
|---|---|---|---|
| Per-factor marginal | main effect | **ADEQUATE→LARGE** all standard/critical; **SMALL** for 10 long-tail types (flagged) | "Recall on X = p (95% Wilson CI [lo,hi], n)." |
| Named 2-way (Lang×Entity on committed rectangle; Domain×Track; Adv×Entity) | named interaction | **ADEQUATE** on committed cells; **EMPTY/SMALL** off-rectangle | "On the committed 17×41 rectangle the language×type interaction is estimable; off-rectangle pairs are exploratory only." |
| Unnamed 2-way / any ≥3-way / full 5-way | confounded | **NOT ESTIMABLE** | "The benchmark does not support full 5-way claims; such cells are exploratory." |

**Authoritative sentence (README/DATASHEET):**
> *"PII-Anon v2 is powered for all single-factor marginal recall claims (95% Wilson CIs; credential/financial-critical types to ±0.5pp at recall 0.99, standard to ±1pp at 0.98) and for three pre-registered 2-way interactions (language×entity-type on a committed rectangle, domain×track, adversarial-type×entity-type). The corpus carries a committed evaluation lattice powering 17 languages across 11 writing systems (Latin, Han, Japanese, Hangul, Arabic, Devanagari, Cyrillic, Thai, Greek, Bengali, Hebrew) to statistically-calibrated positive-count targets (critical n≥1522, standard n≥753). It is not powered for the full multilingual×entity-type grid or any ≥3-way interaction; those are reported as exploratory. Synthetic-distribution power is not external validity — see the real-data correlation slice."*

---

## 8. Operationalization (→ Development S-PWR)

- `src/pii_anon_datasets/stats/power.py` — `required_n`, `projected_wilson_halfwidth`/`projected_interval` (method `wilson-projected`, continuous p_ref, NOT integer-guarded), `Tier`/`TierSpec`/`PowerClass`, `classify`, `audit_crossing` → `PowerMatrix` (`to_markdown`/`to_csv`/`heatmap` behind `viz` extra), `required_discordant_pairs`/`paired_vs_independent_ratio`. Reuses `Interval`+`_z`.
- `src/pii_anon_datasets/stats/lattice.py` — `build_committed_lattice(...)` (deterministic forced-skeleton + balanced fraction) → frozen `src/pii_anon_datasets/data/eval_lattice.json` (single source of truth; header carries `lattice_version`, `seed`, `tier_specs`, `named_interactions`; per cell `{id, language, entity_type, domain, adversarial, difficulty?, tier, target_n, committed, interaction}`).
- `scripts/validate.py --lattice` — corpus-power gate (NFR-018) + round-trip anti-drift (`target_n == required_n`).
- `scoring/detection.py::DesignProvenance` + `reporting/power_table.py` — per-cell n + Wilson CI + design provenance + external-validity caveat on every published metric (FR-029, AX-003).
- Before/after power matrices → `dev-assist-artifacts/03-design/_power/power-matrix-{before,after}.{md,csv}` + slice heatmap.

---

## 9. Epistemic honesty
- DOE method, tiers, and McNemar efficiency are **standard statistical results**, applied here by an agent (no real-user trial of the *design*). The R10 panel (10 personas) returned **ACCEPTED-WITH-CAVEATS** with the tier numbers locked; all caveats are folded above. `provisional_status: AGENT_SIMULATED`.
- **Pass-2:** the committed-cell cardinality + projected growth must be confirmed feasible by an industry-lab user; the synthetic→real transfer delta (FR-027) is the binding external-validity item the power gate does **not** address.
- The exact T2 net deficit is computed by the audit at the **dry-run checkpoint** before any generation; the numbers in §4.2 are nominal ceilings, not the final corpus delta.
