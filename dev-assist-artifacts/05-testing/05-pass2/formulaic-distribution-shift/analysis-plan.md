# Analysis Plan STUB — Formulaic-Template Distribution-Shift Study

**Stage 5 · Wave T5 (Pass-2) · analysis-plan TEMPLATE** · 2026-05-31
**Status: STUB.** Per protocol §6, freeze this **before** computing any real-reference divergence. No
human cohort — this is a derived-histogram analysis. The reference distribution **must be real** PII/PHI
(measuring synthetic-against-synthetic is circular and REFUSED).

---

## 1. Divergence metric(s) (pre-register)
- Per-feature distributional distance: `<Jensen-Shannon | total-variation>` over format-feature histograms.
- Value-diversity / entropy ratio definition: `<…>`.
- **Effective-diversity** definition (distinct realistic exemplars after collapsing template-duplicate
  structure): `<…>`.

## 2. Feature set (pre-register)
- Entity-type mix; value-format classes; length bins; co-occurrence pairs: `<enumerate>`.
- Entity-type / language / domain alignment map (synthetic ↔ real): `<…>`.

## 3. Corpus partition (in-repo, available now)
- Enrichment mass (~72%, `provenance.source_type == "synthetic_lattice_enrichment"`) vs non-enrichment
  (V1-migrated). Compute the same histograms on **whole / enrichment-only / non-enrichment-only**.
- Inputs: `src/pii_anon_datasets/data/pii_anon.jsonl.gz`, `data/lattice_freq_snapshot.json`,
  `data/enrichment-report.json`.

## 4. Real reference (derived histograms only — no real-PHI egress)
- i2b2/n2c2 clinical type-mix + value formats; TAB legal indirect/quasi-id mix + co-occurrence; published
  distribution statistics as a prior where raw data is gated. Acquisition = shared i2b2/TAB track.

## 5. Research questions (pre-register; protocol §3)
- **RQ-1 (shift magnitude):** per shared entity type, synthetic-vs-real divergence; is the enrichment
  mass *more* divergent than the non-enrichment mass?
- **RQ-2 (power-claim impact):** holding the 1,522/753/200 counts fixed, the **effective** distinct-exemplar
  count per cell → the implied **power discount**.
- **RQ-3 (caveat sizing):** which types/languages/domains are most monocultured (name them).

## 6. Outcome → verdict (protocol §8, pre-committed)
- small shift + effective≈nominal → **REAL-DATA-VALIDATED** (caveat bounded);
- mixed → **PERSONA-STRATIFIED/TIGHTENED** (name high-shift types);
- broad count-inflation → **TIGHTENED** (publish a power-discount factor);
- far-from-real on claim cells → **PIVOT** (reposition power as "synthetic-distribution precision only").
