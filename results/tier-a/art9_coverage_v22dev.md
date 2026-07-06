# Article-9 coverage ceiling (v2.2-dev)

**Date:** 2026-06-18 · Branch `paper1-tier-a-experiments` · Sub-project 2A+2B.

The v2.2-dev corpus adds 3 GDPR **Article-9 special-category** entity types — `SEXUAL_ORIENTATION`,
`TRADE_UNION_MEMBERSHIP`, `GENETIC_DATA` (canonical taxonomy 63 → 66), each powered to ≥400 spans across
the 12 powered languages. This note reports whether off-the-shelf detectors can reach them.

## Finding: the 3 Art-9 types are structurally invisible to every off-the-shelf detector

A detector can only score a true positive on a type its native→canonical **label map** can reach. The
3 new Art-9 types are in the **unreachable set of every off-the-shelf detector** (and the author's own
system) — so their recall is **0 by construction**, independent of model quality. This is the
coverage-ceiling finding (CL-02 / AX-003) extended to special-category PII: a *label-map* gap, not a
*model-quality* gap.

| Detector | reachable / 66 | Art-9 types reachable |
|---|---:|---|
| gliner (`gliner_multi_pii-v1`) | 23/66 | none |
| presidio | 20/66 | none |
| piiranha | 16/66 | none |
| scrubadub | 12/66 | none |
| regex | 9/66 | none |
| spacy / stanza / flair | 3/66 | none |
| **pii_anon (own system, Paper 3)** | 63/66 | none |
| **LLM-as-detector** (`llm_baseline`) | 66/66 | all 3 |

**Reading:** off-the-shelf NER + the author's own first-party system all read `0/3` Art-9 special
categories. Only an open-vocabulary frontier-LLM detector reaches them. For a "comprehensive PII
benchmark" this is a load-bearing, novel result — GDPR Art-9 categories (sexual orientation, trade-union
membership, genetic data) are systematically uncovered by deployed PII tooling.

## Why no measured per-type re-score here

Measured recall on the 3 Art-9 types is **0.000 by construction** (no label → no prediction → no true
positive), so a measured run only confirms the structural fact above. The full *measured* local+cloud
leaderboard refresh over the 66-type / 782,677-record v2.2 corpus — including the marquee GLiNER-vs-AWS
rows — was completed in the **`v2.2.0` cut**: `results/baselines/tier1-en-all/` is now the measured
66-type run (coverage `/66`; aws macro-F2 0.2726; see `coverage_ceiling.md` / `BASELINES.md`), and it
confirms the **0.000-by-construction** structural fact for the 3 Art-9 types. This note is the original
v2.2-dev structural coverage refresh that predicted it.

## Honesty scope (AX-001)

Synthetic-only: the Art-9 values are English-anchored synthetic strings (per-language Art-9 localization
is deferred to sub-project 2D). The coverage figures are precision on the corpus's label-map projections,
not external-validity claims.
