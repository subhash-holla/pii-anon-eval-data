# Pre-Registration — FR-027 Synthetic→Real Correlation

**Stage 5 · Wave T5 (Pass-2) · pre-registration** · 2026-05-31 · filled 2026-06-17
**Status: FROZEN PLAN — no real i2b2/TAB score has been computed yet.**  The run is deferred (Pass-2
pending real-data acquisition and DUA execution; see `protocol.md §4`).  Per protocol §3, this document
must be **committed (content hash recorded) BEFORE any real i2b2/TAB score is computed**.  Any edit after
the first real score invalidates the pre-registration and must be disclosed.

> **Freeze discipline.** The v1 harness refuses fabrication: `correlate(synthetic, real=None)` returns the
> `RealDataAbsent` sentinel (`src/pii_anon_datasets/validation/correlation.py`).  This file freezes the
> plan; it does not contain any result.  Record the git content hash of this file in `outcome.md` at the
> time of freeze (before any real score is computed).

---

## 1. Systems under comparison (the K-list)

**K = 11** — the complete PII-Anon leaderboard as of v2.1.0 (the same 11 detectors that produced the
`results/baselines/tier1-en-all/baseline_results.json` headline).

> **Deviation from `protocol.md` (disclosed):** `protocol.md §3` framed the RQ over a *target* of "K≥12
> detectors/anonymizers" — a lower-bound aspiration written before the leaderboard was finalized. This
> pre-registration **locks the actual count at K=11**, the detectors that genuinely ran in v2.1.0 (the
> author's own `pii_anon`/swarm is excluded for COI, deferred to Paper 3). Adding a 12th (e.g. the
> `llm_baseline` LLM-as-detector, which exists but needs an API key + budget) is a future-run extension,
> not part of this frozen plan. The ≥12 target is hereby superseded by the locked K=11.

| # | Detector | Type | Model / implementation |
|---|---|---|---|
| 1 | `aws` | Cloud DLP | AWS Comprehend entity/PII detection (managed service, June-2026) |
| 2 | `gliner` | Local NER | `urchade/gliner_multi_pii-v1` (GLiNER) |
| 3 | `gcp` | Cloud DLP | Google Cloud DLP (managed service, June-2026) |
| 4 | `azure` | Cloud DLP | Azure AI Language PII detection (managed service, June-2026) |
| 5 | `presidio` | Local | Microsoft Presidio (default English configuration) |
| 6 | `regex` | Local pattern | PII-Anon regex pattern baseline |
| 7 | `piiranha` | Local NER | `iiiorg/piiranha-v1-detect-personal-information` |
| 8 | `stanza` | Local NER | Stanford Stanza (`en_core_web_lg` NER) |
| 9 | `flair` | Local NER | Flair NER (English model) |
| 10 | `spacy` | Local NER | spaCy `en_core_web_lg` NER |
| 11 | `scrubadub` | Local | scrubadub (default English detectors) |

**Selection rule (pre-committed):** all detectors registered in
`src/pii_anon_datasets/baselines/registry.py` that are NOT in the `SANITY_DETECTORS` partition
(null / always_person_name / oracle), as of the v2.1.0 tag.  No external systems are added to the
K-list after freeze.

---

## 2. Metric

- **Primary metric:** per-system **recall@entity-type** on the domain-matched English clinical/legal
  slice.  Concretely: for each system k and each entity type t in the pre-registered paired vector
  (§3), compute `recall(k, t) = TP(k,t) / (TP(k,t) + FN(k,t))` on the relevant corpus slice.
- **Aggregation for the correlation vector:** per-entity-type micro-recall (one recall value per
  (system, entity-type) pair).  The **per-system summary** used in Kendall τ-b / Spearman ρ is the
  **mean recall across entity types in the paired vector** (i.e. a macro-average over the pre-registered
  entity-type set, not over all 63 PII-Anon types).  This is the **primary** aggregation.
- **Micro-averaged overall recall** (collapsed across entity types) is reported as a **secondary**
  aggregation alongside the primary.

---

## 3. Domain-match map (PII-Anon 63-type taxonomy → real corpus types)

Only entity types present in both the real corpus and the PII-Anon taxonomy enter the paired vector.
Types present on only one side are **excluded** from the correlation vector and reported separately
as "no real anchor".

### i2b2-2014 (clinical English, 1,304 notes)

| i2b2-2014 PHI category | PII-Anon canonical type(s) |
|---|---|
| NAME (patient/doctor names) | `PERSON_NAME` |
| DATE | `TIMESTAMP` (date/time occurrences); `DATE_OF_BIRTH` excluded if not distinguishable |
| AGE | `AGE` |
| ID (patient ID / medical record number) | `MEDICAL_RECORD_NUMBER`; `NATIONAL_ID_NUMBER` (when the i2b2 annotation covers SSN-as-ID) |
| LOCATION (city, state, country, zip, street) | `LOCATION_NAME`; `STREET_ADDRESS`; `POSTAL_CODE` |

Types present in i2b2-2014 but **absent from PII-Anon**: PROFESSION (no equivalent in the
63-type taxonomy) → excluded.  Types present in PII-Anon but not in i2b2-2014 (e.g. financial,
digital_online categories) → excluded from the clinical paired vector and reported as "no real anchor".

### TAB — Text Anonymization Benchmark (legal English, 1,268 ECHR cases)

| TAB entity category | PII-Anon canonical type(s) |
|---|---|
| PERSON | `PERSON_NAME` |
| LOCATION | `LOCATION_NAME`; `STREET_ADDRESS` |
| ORG (organization / institution) | `ORGANIZATION_NAME` |
| QUANTITY (numerical amounts, ages, dates as quantities) | `AGE`; `TIMESTAMP` (date sub-type) |
| DATETIME (explicit date/time expressions) | `TIMESTAMP` |

Types present in TAB but not represented in PII-Anon at the granularity needed → excluded and
reported as "no real anchor".

### Exclusion rule (pre-committed)

Any PII-Anon entity type that is not in the above tables for a given corpus is excluded from that
corpus's paired recall vector.  The exclusion list is computed deterministically from the tables
above and is not adjusted after the first real score is seen.

---

## 4. Statistical plan

### Primary test
- **Kendall τ-b** (rank correlation, primary).  Transfer "holds" iff τ-b ≥ τ\* **and** the
  bootstrap CI lower bound (5th percentile) exceeds τ\*.

### Secondary test
- **Spearman ρ** (secondary).  Reported alongside τ-b; not used for the primary verdict.

### Threshold
- **τ\* floor = 0.60**.  The pre-registered acceptance threshold.  If the seeded bootstrap
  CI lower bound is ≥ 0.60 and the point estimate τ-b ≥ 0.60, the verdict is REAL_USER_VALIDATED
  (subject to Bland-Altman check).

### Bootstrap
- **Seed = 20260603** (integer).  Fixed before any real score is seen.
- **n_boot = 1 000** bootstrap resamples.
- Implementation: `src/pii_anon_datasets/validation/correlation.py → _bootstrap_ci(seed=20260603,
  n_boot=1000)`.  Results must reproduce byte-identically (AX-002).

### Bland-Altman
- Mean difference and ±1.96·SD limits are computed on the (synthetic recall, real recall) pairs
  for each entity type in the paired vector.
- **Acceptance band (pre-registered):** mean difference |Δ̄| ≤ 0.10 (10 pp) and both
  limits of the ±1.96·SD band within ±0.20.  If the band is exceeded, the verdict is downgraded
  (see §5).  Values are computed after the run; the band itself is pre-registered here.

### Run structure (pre-committed)
- i2b2 and TAB as **two separate** paired recall vectors; **pooled** (concatenated across the two
  matched entity-type sets) as a third vector.
- **Primary corpus for the verdict:** the **pooled** vector.  Per-corpus results (i2b2 / TAB
  separately) are reported as secondary analyses.

### Enrichment handling (pre-committed)
- **Primary analysis: raw** recall scores on the PII-Anon synthetic domain-matched English slice
  (no reweighting).
- **Secondary analysis: reweighted** — down-weight synthetic rows whose entity-type distribution
  inflates a type beyond the real corpus's type mix (per protocol §4), then recompute recall.
- Both are reported; raw is primary.

---

## 5. Outcome → verdict (protocol §8, pre-committed)

| Condition | Verdict |
|---|---|
| **Pooled** τ-b ≥ 0.60 with bootstrap CI lower bound ≥ 0.60 **and** both i2b2 and TAB individually ≥ 0.60, Bland-Altman within acceptance band | **REAL_USER_VALIDATED** — lift the synthetic-only citation ceiling; per-cell caveat may cite the correlation |
| **Pooled** τ-b ≥ 0.60 but exactly one of i2b2 / TAB is < 0.60 per-corpus | **PERSONA-STRATIFIED** — validated for the matching domain, caveated for the other |
| τ-b < 0.60 on both but a clear monotone signal after reweighting | **TIGHTENED** — transfer holds only under the real type-mix |
| τ-b < 0.60 on both **and** Bland-Altman shows systematic bias (|Δ̄| > 0.10 or limits outside ±0.20) | **PIVOT** — synthetic distribution does not rank systems like real data; headline-recall framing withdrawn |
| Real data not acquired (no DUA / no collaborator) | **INSUFFICIENT_EVIDENCE** — `RealDataAbsent` stays the shipped truth; SHIP-WITH-CAVEATS |

> **Verdict gate (disambiguation):** the τ-b threshold is applied to the **pooled** vector (the §4 primary);
> the per-corpus i2b2 / TAB results are secondary and only select between REAL_USER_VALIDATED and
> PERSONA-STRATIFIED once the pooled gate passes.

---

## 6. Provenance to record in `outcome.md`

At freeze time, record:
- **Content hash of this file:** `sha256sum dev-assist-artifacts/05-testing/05-pass2/FR-027/preregistration.md` — committed to git BEFORE any real score is computed.
- DUA references: i2b2/n2c2 DUA ID (assigned by Harvard DBMI); IRB determination reference.
- TAB license reference (TAB public release; confirm research-use compatibility with derived artifact publication).
- De-id collaborator identity and `copublication-terms.md` version hash.
- Confirmation that **only the derived aggregate score matrix** (K × entity-type cells, no note text or spans) left the DUA-host.

---

## Non-strippable caveat (travels with every published figure)

> **AX-001 + FR-027 CAVEAT:** PII-Anon is a synthetic benchmark.  The correlation reported here measures
> whether synthetic-distribution detector rankings track i2b2-2014/TAB rankings on the domain-matched
> English slice.  A REAL_USER_VALIDATED verdict lifts the synthetic-only citation ceiling for the
> correlated entity types and domains only — it does **not** make PII-Anon records real data, does not
> constitute a GDPR/HIPAA certification, and does not generalize to languages or domains outside the
> paired vector.
