---
license: cc0-1.0
pretty_name: PII-Anon
size_categories:
  - 100K<n<1M
task_categories:
  - token-classification
tags:
  - pii
  - privacy
  - anonymization
  - multilingual
language:
  - en
  - bn
  - he
  - el
  - th
  - ru
  - nl
  - hi
  - ko
  - pt
  - it
  - es
  - ar
  - zh
  - fr
  - ja
  - de
  - tr
  - vi
  - id
  - sv
  - ro
  - hu
  - uk
  - da
  - pl
  - fi
  - cs
  - bg
  - no
  - te
  - af
  - sw
  - ur
  - ta
  - fa
  - xh
  - ha
  - ne
  - so
  - km
  - ms
  - cy
  - az
  - zu
  - yo
  - my
  - ca
  - sr
  - et
  - lo
  - ka
  - mg
  - am
  - fil
  - ps
  - si
  - ig
  - sq
  - lv
---

# PII-Anon

A CC0 multilingual PII benchmark corpus of **782,677** records carrying **3,107,240** entity annotations across **66** entity types and **60** languages, spanning 7 evaluation dimensions. Each record exposes the five legally-distinct regulatory regime signals (gov-02 / FR-022) as separate `reg_*` columns — no merged compliance verdict.

## Train vs. evaluation substrate

The 159,891 tier3_evaluation records are the EVALUATION substrate of the 782,677-record corpus (behavioral-signal / RRS scoring runs on this substrate), NOT the whole corpus.

## Synthetic-enrichment disclosure

79.2% of records carry provenance.source_type='synthetic_lattice_enrichment' (the S-PWR power fill); synthetic power is not external validity.

## Statistical power

PII-Anon v2 is powered for all single-factor marginal recall claims (95% Wilson CIs; credential/financial-critical types to ±0.5pp at recall 0.99, standard to ±1pp at 0.98) and for three pre-registered 2-way interactions (language×entity-type on a committed rectangle, domain×track, adversarial-type×entity-type). The corpus carries a committed evaluation lattice powering 17 languages across 11 writing systems (Latin, Han, Japanese, Hangul, Arabic, Devanagari, Cyrillic, Thai, Greek, Bengali, Hebrew) to statistically-calibrated positive-count targets (critical n≥1522, standard n≥753). It is not powered for the full multilingual×entity-type grid or any ≥3-way interaction; those are reported as exploratory. Synthetic-distribution power is not external validity — see the real-data correlation slice.

## Baseline Detector Performance

How widely-used PII detectors score on this corpus (`test` split, language `en`; 31,048 records), ranked by **F2** (recall-weighted — a missed PII is the costly error). Full per-type / per-domain / per-language tables, Wilson CIs, and provenance: `baseline_results.json` and `BASELINES.md`.

> Power on a committed cell is statistical precision on the SYNTHETIC distribution, NOT external validity; not citable as a standalone recall claim absent the real-data correlation slice (FR-027). Synthetic-only (AX-001).

| Rank | Detector | Precision | Recall | F2 | Recall 95% CI | Coverage |
|---|---|---:|---:|---:|---|---:|
| 1 | aws | 0.769 | 0.728 | 0.736 | [0.726, 0.730] | 24/66 |
| 2 | gliner | 0.813 | 0.716 | 0.734 | [0.714, 0.718] | 23/66 |
| 3 | gcp | 0.722 | 0.700 | 0.704 | [0.698, 0.702] | 18/66 |
| 4 | azure | 0.730 | 0.688 | 0.696 | [0.686, 0.690] | 17/66 |
| 5 | presidio | 0.419 | 0.562 | 0.526 | [0.560, 0.564] | 20/66 |
| 6 | regex | 0.857 | 0.349 | 0.396 | [0.347, 0.351] | 9/66 |
| 7 | piiranha | 0.441 | 0.327 | 0.345 | [0.325, 0.329] | 16/66 |
| 8 | stanza | 0.583 | 0.308 | 0.340 | [0.306, 0.310] | 3/66 |
| 9 | flair | 0.565 | 0.295 | 0.326 | [0.293, 0.297] | 3/66 |
| 10 | spacy | 0.464 | 0.294 | 0.317 | [0.292, 0.296] | 3/66 |
| 11 | scrubadub | 0.818 | 0.169 | 0.201 | [0.167, 0.170] | 12/66 |

## License

The **data** is released under **CC0-1.0** (public-domain dedication); the accompanying **code** (loaders, scorers, exporters) is licensed **Apache-2.0**. The two licenses are distinct — using the data does not subject you to the code license, and vice versa.
