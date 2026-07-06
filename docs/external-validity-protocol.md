# PII-Anon External-Validity Protocol (FR-027)

> **Status: DEFERRED — Pass-2 pending real-data acquisition.**
> The correlation harness is shipped and `RealDataAbsent`-guarded; no real i2b2/TAB score has been
> computed yet. The run described here is the **only path** to an external-validity claim on this
> benchmark. Until it completes, every metric on PII-Anon is precision on the synthetic distribution
> only (AX-001).

---

## 1. The synthetic-only ceiling (AX-001)

PII-Anon is a **fully synthetic** benchmark corpus. Every record contains synthetic PII generated
under a controlled lattice process; no real personal data appears in the corpus. This design enables
public, CC0-licensed sharing without privacy risk, but it imposes a hard epistemic ceiling:

> **A score on PII-Anon is statistical precision on the SYNTHETIC distribution — not external
> validity, and not a standalone real-world recall claim.**

Specifically:
- `79.2%` of records carry `provenance.source_type = "synthetic_lattice_enrichment"` (S-PWR),
  which raises within-distribution statistical power but does not establish real-world generalisation.
- `semantic_similarity_*` fields are token-overlap Jaccard, not embedding similarity.
- `re_identification_resistance_score` / `tier3_risk_level` are heuristic priors, not measured
  adversarial attacks.
- No record is demonstrated anonymised under GDPR Recital 26.

**This ceiling is permanent until the FR-027 real-data correlation run is executed.** The benchmark
is not repositioned unless the run completes; it is honest about what it is.

---

## 2. The FR-027 correlation harness

**Module:** `pii_anon_datasets.validation.correlation`

The shipped harness implements the pre-registered statistical protocol for the synthetic→real
transfer study. It **never fabricates** a result: calling it without real data returns the
`RealDataAbsent` sentinel immediately, leaving the synthetic-only caveat intact.

### Methods implemented

| Method | Description |
|---|---|
| `kendall_tau` | Kendall τ-b rank correlation (primary test) |
| `spearman_rho` | Spearman ρ (secondary, reported alongside τ-b) |
| `_bootstrap_ci(seed, n_boot)` | Seeded bootstrap CI — results reproduce byte-identically (AX-002) |
| `bland_altman` | Bland-Altman mean difference ± 1.96·SD limits |
| `correlate(synthetic, real_scores)` | Orchestrator — returns `RealDataAbsent` if `real_scores is None` |

### The `RealDataAbsent` guard

```python
from pii_anon_datasets.validation.correlation import correlate, RealDataAbsent

result = correlate(synthetic_scores, real_scores=None)
# result is RealDataAbsent — no correlation is fabricated
assert isinstance(result, RealDataAbsent)
```

Passing `real_scores=None` (the default when no real data has been acquired) returns the sentinel
and attaches the non-strippable `CORRELATION_CAVEAT`. This is the shipped state as of v2.1.0.

---

## 3. Activation flow (how to run when real data is available)

Running the correlation requires a licensed real-data collaborator (see §5 of the binding protocol).
The activation path, once real aggregate score matrices exist:

```bash
# Set the path to the derived aggregate score matrix (no note text — see §4 data constraints)
export PII_ANON_REAL_DEID_PATH=/path/to/aggregate_scores.json

# Run the correlation (imports real_data_ingest, which reads from the env-var path)
PYTHONPATH=src python -c "
from pii_anon_datasets.validation.real_data_ingest import correlate_from_path
result = correlate_from_path('$PII_ANON_REAL_DEID_PATH')
print(result)
"
```

`correlate_from_path` reads only the **derived aggregate score matrix** (K-system × entity-type
cells, no note text or spans) exported from the DUA-controlled host. Real PHI never enters this
repository (AX-pii-anon-001).

**Pre-registered parameters (frozen in `preregistration.md` before any real score is computed):**
- Seed: `20260603`
- Bootstrap resamples: `n_boot = 1000`
- τ\* floor: `0.60`
- Bland-Altman acceptance band: |Δ̄| ≤ 0.10, limits within ±0.20
- Primary corpus for verdict: **pooled** (i2b2 + TAB concatenated)
- Primary analysis: raw recall (reweighted secondary)

---

## 4. Verdict mapping

The outcome of the correlation run maps to one of five verdicts. The threshold is applied to the
**pooled** vector (i2b2 + TAB concatenated); per-corpus results are secondary.

| Condition | Verdict | Consequence |
|---|---|---|
| Pooled τ-b ≥ 0.60, bootstrap CI lower bound ≥ 0.60, both i2b2 and TAB individually ≥ 0.60, Bland-Altman within band | **REAL_USER_VALIDATED** | Synthetic-only citation ceiling lifted for the correlated entity types and domains; per-cell caveat may cite the correlation. |
| Pooled τ-b ≥ 0.60 but exactly one of i2b2 / TAB is < 0.60 per-corpus | **PERSONA-STRATIFIED** | Validated for the matching domain; caveated for the other. |
| τ-b < 0.60 on both, but a clear monotone signal after reweighting | **TIGHTENED** | Transfer holds only under the real type-mix; mandatory reweighting + tightened claim language. |
| τ-b < 0.60 on both and Bland-Altman shows systematic bias (|Δ̄| > 0.10 or limits outside ±0.20) | **PIVOT** | Synthetic distribution does not rank systems like real data; headline-recall framing withdrawn; benchmark repositioned as stress-test / pre-screen only. |
| Real data not acquired (no DUA / no collaborator) within the window | **INSUFFICIENT_EVIDENCE** | `RealDataAbsent` stays the shipped truth; SHIP-WITH-CAVEATS. |

**Current status:** `INSUFFICIENT_EVIDENCE` / `PERSONA-CONDITIONAL` — the run has not been
executed. `RealDataAbsent` is the shipped truth.

---

## 5. Data constraints (what may and may not leave the DUA host)

The correlation study uses two real corpora:

| Corpus | Role | Access |
|---|---|---|
| **i2b2-2014 / n2c2** (1,304 clinical notes) | Real clinical leg | DBMI Data Portal DUA; IRB or IRB-exempt determination required |
| **TAB — Text Anonymization Benchmark** (1,268 ECHR legal cases) | Real legal leg | Openly licensed (research use); confirm derived-artifact publication compatibility |

**Only the derived aggregate score matrix** (K × entity-type cells, no note text, no spans) leaves
the DUA-controlled host. Real PHI never enters this repository. This preserves AX-pii-anon-001.

---

## 6. Binding artifacts

The full binding protocol and frozen pre-registration are in the repository:

- **Protocol (binding):** [`dev-assist-artifacts/05-testing/05-pass2/FR-027/protocol.md`](../dev-assist-artifacts/05-testing/05-pass2/FR-027/protocol.md)
  — defines the research question, data acquisition requirements, run structure, recruitment channel,
  and outcome capture procedure.

- **Pre-registration (frozen):** [`dev-assist-artifacts/05-testing/05-pass2/FR-027/preregistration.md`](../dev-assist-artifacts/05-testing/05-pass2/FR-027/preregistration.md)
  — commits the K-list (11 detectors), metric (recall@entity-type), domain-match map
  (i2b2-2014 PHI categories → PII-Anon canonical types; TAB entity categories → PII-Anon canonical
  types), statistical plan (Kendall τ-b primary, Spearman ρ secondary, seed 20260603, n_boot=1000,
  τ\*=0.60, Bland-Altman band), and primary/secondary analysis (raw/reweighted) **before any real
  score is computed**. Any edit after the first real score is seen invalidates the pre-registration
  and must be disclosed.

- **Co-publication terms:** [`dev-assist-artifacts/05-testing/05-pass2/FR-027/copublication-terms.md`](../dev-assist-artifacts/05-testing/05-pass2/FR-027/copublication-terms.md)

- **Recruiting checklist:** [`dev-assist-artifacts/05-testing/05-pass2/FR-027/recruiting-checklist.md`](../dev-assist-artifacts/05-testing/05-pass2/FR-027/recruiting-checklist.md)

---

## 7. Non-strippable caveat

The following caveat travels with every published figure derived from this correlation study (it is
non-strippable; the harness self-attaches it to every `CorrelationResult`):

> **AX-001 + FR-027 CAVEAT:** PII-Anon is a synthetic benchmark. The correlation reported here
> measures whether synthetic-distribution detector rankings track i2b2-2014/TAB rankings on the
> domain-matched English slice. A REAL_USER_VALIDATED verdict lifts the synthetic-only citation
> ceiling for the correlated entity types and domains only — it does **not** make PII-Anon records
> real data, does not constitute a GDPR/HIPAA certification, and does not generalise to languages
> or domains outside the paired vector.

---

## 8. Honesty summary

| Claim | Supported? |
|---|---|
| Detector rankings on the PII-Anon synthetic distribution | Yes — this is what the leaderboard measures |
| Real-world recall on clinical/legal text | No — requires the FR-027 run (deferred) |
| GDPR/HIPAA compliance certification | No — not the purpose of this benchmark |
| External validity (synthetic proxy for real PII) | Pending — `RealDataAbsent` until the run executes |

The only path to an external-validity claim is the FR-027 real-data correlation run described in the
binding protocol above. No synthetic stand-in, no agent-simulated cohort, and no proxy is accepted
in its place. Substituting a fabricated "real" score vector is a catastrophic methodology violation
(see `protocol.md §1`).
