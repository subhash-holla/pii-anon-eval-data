# Pass-2 Protocol — Formulaic-Template Monoculture · Real-Data Distribution-Shift Study

**Stage 5 · Wave T5 (Pass-2 coordination)** · 2026-05-31 · `pass2_required: false` (OPTIONAL; T6 → **SHIP-WITH-CAVEATS** for the corpus external-validity caveat if un-Pass-2'd, not DEFER).

**Pass-2 working files:** [`analysis-plan.md`](analysis-plan.md) (stub) · [`acquisition-checklist.md`](acquisition-checklist.md) · shared [real-data acquisition](../_shared/real-data-acquisition-checklist.md). **No `outcome.md` until real reference distributions land out-of-band.**

> **NO agent-simulated cohort and NO synthetic reference distribution substitutes for this protocol.** The whole question is *how far the formulaic synthetic distribution diverges from REAL PII distributions* — measuring synthetic-against-synthetic (or against an agent-generated "real" reference) is circular and answers nothing. The reference distribution MUST be real PII/PHI. Substituting a simulated reference is a **CATASTROPHIC methodology violation** and is REFUSED.

---

## 1. Item under validation

| Field | Value |
|---|---|
| **Item** | The **~72% formulaic-template monoculture** — roughly 72% of the 575,604-record corpus carries `provenance.source_type="synthetic_lattice_enrichment"` (the S-PWR enrichment that raises statistical power). DATASHEET: *"not, by itself, evidence of real-world generalization."* |
| **Source stage** | Corpus / DATASHEET.md + README.md power statement; Design `sampling-design.md §6` (non-strippable external-validity caveat); generation via `PIIFactory` template-based expansion. |
| **Current status** | AGENT_SIMULATED corpus; the external-validity caveat is non-strippable and carried on every published per-cell metric. |
| **Threshold under question** | (a) **How much** does the formulaic `synthetic_lattice_enrichment` distribution diverge from real PII distributions (per entity type, per language, per format/co-occurrence)? (b) **What is the impact on the published power claims** — does the enrichment-driven count (the 1,522/753/200 tiers that the enrichment fills) translate into *effective* power against the real distribution, or is it precision on a monoculture? |
| **Downstream impact** | This is the **corpus external-validity caveat** itself. The README states the enrichment *"raises statistical power but does NOT establish real-world generalization,"* and `sampling-design.md §6` warns *"a tight committed-cell CI is precision on a synthetic distribution, not external validity."* Every per-slice power claim inherits this. Quantifying the divergence (a) sizes how big the caveat really is, and (b) tells consumers how much to discount the published power. It is distinct from — and complementary to — FR-027 (which correlates *rankings*; this study characterizes the *distribution*). |

## 2. Why real DATA is needed (no simulation substitutes)

- A distribution-shift measurement compares the corpus to a **reference**. If the reference is also synthetic/agent-generated, the divergence is meaningless. The reference must be a **real** PII/PHI distribution (its entity-type mix, value formats, length/format variety, co-occurrence structure).
- The ~72% figure is itself a *known* generation artifact; the open question is whether that formulaic mass **distorts** the per-type/per-language distribution away from reality (e.g. over-regular formats, under-represented cultural variants, templated co-occurrence). Only real data can anchor "what reality looks like."
- The DATASHEET's own limitation section names the risk: *"may not directly translate … particularly for domain-specific jargon, formatting patterns, or culturally specific PII formats not covered by the templates."* This study measures exactly that.

## 3. Research questions (pre-registered)

> **RQ-1 (shift magnitude):** For each shared entity type, how far does the synthetic value/format distribution diverge from the real one (distributional distance — e.g. Jensen-Shannon / total-variation over format-feature histograms, plus value-diversity / entropy ratios)? Is the `synthetic_lattice_enrichment` mass *more* divergent than the non-enrichment (V1-migrated) mass?
> **RQ-2 (power-claim impact):** Holding the published per-cell counts fixed (the 1,522/753/200 tiers), what is the **effective** number of *distinct, realistic* exemplars per cell after collapsing template-duplicate structure — i.e. does formulaic enrichment inflate count without inflating effective coverage, and by how much should the published power be discounted?
> **RQ-3 (caveat sizing):** Which entity types / languages / domains are *most* monocultured (largest shift, lowest effective diversity) — so the non-strippable caveat can name them specifically rather than generically?

## 4. Data source (the real reference) + corpus side

**Real reference distributions (no real-PHI egress — derived feature histograms only, AX-pii-anon-001):**
| Source | Provides | Acquisition |
|---|---|---|
| **i2b2-2014 / n2c2** | real clinical PHI type-mix + value formats (NAME/DATE/AGE/ID/LOCATION) | DUA (shared with FR-027); export only **feature histograms** (format-class counts, length distributions, co-occurrence rates), never note text/values. |
| **TAB (ECHR legal)** | real legal indirect/quasi-identifier mix + co-occurrence | open research license; derived feature histograms. |
| **Published PII/PHI distribution statistics** (i2b2/n2c2/OpenDeID papers, public frequency tables) | type-frequency priors where raw data is gated | cit. |

**Corpus side (in-repo, fully available):**
- `src/pii_anon_datasets/data/pii_anon.jsonl.gz` (575,604 records) with `provenance.source_type`. Split into the **enrichment** mass (~72%, `synthetic_lattice_enrichment`) vs the **non-enrichment** mass (V1-migrated) using the provenance field; compute the same feature histograms on each.
- `data/lattice_freq_snapshot.json` + `data/enrichment-report.json` for the enrichment's own frequency structure.

## 5. Acquisition channel

- Same de-id collaborator / DUA channel as FR-027 and FR-015/016 (these three real-data items co-locate on one i2b2/TAB acquisition). Only **derived, de-identified feature histograms** leave the DUA-host — no real PII enters this repo.
- Where raw real data is fully gated, published distribution statistics serve as the reference prior (cited, with the limitation noted). A small confirmation pass against the live i2b2/TAB feature histograms strengthens the prior-based estimate.

## 6. Run structure (analysis sequence — no human cohort)

1. **Pre-register** the divergence metric(s), the feature set (entity-type mix, value-format classes, length bins, co-occurrence pairs), the entity-type/language/domain alignment map, and the effective-diversity definition. Freeze as `pass2/formulaic-distribution-shift/analysis-plan.md`.
2. **Compute** synthetic feature histograms: whole corpus, enrichment-only, non-enrichment-only.
3. **Compute** real feature histograms on the DUA-host (export histograms only).
4. **Measure** divergence per entity type / language / domain (synthetic-vs-real; and enrichment-vs-non-enrichment to isolate the formulaic effect).
5. **Estimate** effective diversity per committed cell (distinct realistic exemplars after de-duplicating template structure) and the implied power discount vs the published 1,522/753/200 counts.
6. **Rank** the most-monocultured cells for the named caveat.

## 7. Outcome capture

**Per-(type / language / domain):** synthetic-vs-real divergence; enrichment-vs-non-enrichment divergence; value-diversity/entropy ratio; effective-vs-nominal exemplar count; co-occurrence realism.

**Roll-up:** the overall shift magnitude and its spread; whether the ~72% enrichment is the dominant shift driver; the recommended **power discount** (how much to deflate the published per-cell power against reality); the **named** most-monocultured types/languages/domains for the caveat; edge cases (any type where synthetic happens to match real well).

## 8. Verdict mapping

| Outcome | Verdict | Status transition |
|---|---|---|
| Shift is small + effective diversity ≈ nominal count across most cells | **REAL-DATA-VALIDATED** | the corpus external-validity caveat is *bounded* (small, quantified); published power claims stand with a stated, modest discount; caveat softened to a measured bound. |
| Shift varies — some types/languages realistic, others heavily monocultured | **PERSONA-STRATIFIED / TIGHTENED** | the non-strippable caveat is made **specific** (names the high-shift types/languages); power claims on high-shift cells are tightened/flagged exploratory; low-shift cells keep their claim. |
| Enrichment inflates count well above effective coverage broadly | **TIGHTENED** | publish an explicit **power discount factor**; restate per-cell power as effective-exemplar-based, not raw-count-based; strengthen the README/DATASHEET caveat with the measured number. |
| Synthetic distribution is far from real on the claim-bearing cells | **PIVOT** | the per-cell *power* framing is over-claimed; reposition the published power as "synthetic-distribution precision only" and lean entirely on FR-027 for any external-validity claim; withdraw count-based power as a standalone strength. |
| Real reference distributions not acquired in-window | **INSUFFICIENT_EVIDENCE** | the generic non-strippable external-validity caveat stands unquantified; **T6 → SHIP-WITH-CAVEATS**. |

**Status Change Log entry to write on outcome:**
`| <date> | corpus external-validity (DATASHEET ~72% formulaic; NFR-001/018 power claims) | AGENT_SIMULATED | <verdict> | Pass-2 distribution-shift study: synthetic-vs-real divergence=<...>, effective/nominal=<...>, power discount=<...>, most-monocultured=<named>; evidence .../05-pass2/formulaic-distribution-shift/outcome.md |`
