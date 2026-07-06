# Acquisition Checklist — Formulaic Distribution-Shift Study

**Stage 5 · Wave T5 (Pass-2)** · 2026-05-31 · companion to [`protocol.md`](protocol.md).
**No human cohort** — this is a derived-histogram analysis against a **real** reference distribution.
Data acquisition is the shared i2b2/TAB track —
[`../_shared/real-data-acquisition-checklist.md`](../_shared/real-data-acquisition-checklist.md).
**No `outcome.md` until the real reference histograms land.**

## Corpus side (in-repo — available now, no acquisition needed)
- ☐ Split `pii_anon.jsonl.gz` by `provenance.source_type` into enrichment (~72%) vs non-enrichment masses.
- ☐ Compute synthetic feature histograms: whole / enrichment-only / non-enrichment-only.
- ☐ Pull `data/lattice_freq_snapshot.json` + `data/enrichment-report.json` for the enrichment's own frequency structure.

## Real-reference side (shared i2b2/TAB track — derived histograms ONLY)
- ☐ On the DUA-host, compute **feature histograms** for i2b2/n2c2 (clinical) + TAB (legal): format-class
  counts, length distributions, co-occurrence rates. **Export histograms only** — no note text/values (AX-pii-anon-001).
- ☐ Where raw data is gated, cite **published distribution statistics** as the reference prior (note the limitation).

## Pre-run gate
- ☐ [`analysis-plan.md`](analysis-plan.md) frozen (divergence metric, feature set, alignment map,
  effective-diversity definition) **before** any real-vs-synthetic divergence is computed.

## Run + write-up
- ☐ Measure divergence per type/language/domain (synthetic-vs-real; enrichment-vs-non-enrichment to
  isolate the formulaic effect).
- ☐ Estimate effective diversity per committed cell + the implied power discount vs 1,522/753/200.
- ☐ Rank the most-monocultured cells for the **named** caveat.
- ☐ Write `outcome.md` (verdict per protocol §8) + Status Change Log row; re-run `/dev-assist-testing` T6.

> Until then: the generic non-strippable external-validity caveat stands **unquantified**; release stays
> **SHIP-WITH-CAVEATS** (Caveat 3). No synthetic/agent-generated reference distribution substitutes (REFUSED).
