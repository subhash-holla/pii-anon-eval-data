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
  - ru
  - tr
  - vi
  - th
  - id
  - sv
  - ro
  - hu
  - uk
  - da
  - el
  - pl
  - he
  - bn
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

A CC0 multilingual PII benchmark corpus of **575,604** records carrying **2,486,438** entity annotations across **63** entity types and **60** languages, spanning 7 evaluation dimensions. Each record exposes the five legally-distinct regulatory regime signals (gov-02 / FR-022) as separate `reg_*` columns — no merged compliance verdict.

## Train vs. evaluation substrate

The 159,891 tier3_evaluation records are the ~27.8% EVALUATION substrate of the 575,604-record corpus (behavioral-signal / RRS scoring runs on this substrate), NOT the whole corpus.

## Synthetic-enrichment disclosure

~72% of records carry provenance.source_type='synthetic_lattice_enrichment' (the S-PWR power fill); synthetic power is not external validity.

## Statistical power

PII-Anon v2 is powered for all single-factor marginal recall claims (95% Wilson CIs; credential/financial-critical types to ±0.5pp at recall 0.99, standard to ±1pp at 0.98) and for three pre-registered 2-way interactions (language×entity-type on a 12×41 committed rectangle, domain×track, adversarial-type×entity-type). It is not powered for the full multilingual×entity-type grid or any ≥3-way interaction; those are reported as exploratory. Synthetic-distribution power is not external validity — see the real-data correlation slice.

## Baseline Detector Performance

How widely-used PII detectors score on this corpus (`test` split, language `en`; 30,995 records), ranked by **F2** (recall-weighted — a missed PII is the costly error). Full per-type / per-domain / per-language tables, Wilson CIs, and provenance: `baseline_results.json` and `BASELINES.md`.

> Power on a committed cell is statistical precision on the SYNTHETIC distribution, NOT external validity; not citable as a standalone recall claim absent the real-data correlation slice (FR-027). Synthetic-only (AX-001).

| Rank | Detector | Precision | Recall | F2 | Recall 95% CI | Coverage |
|---|---|---:|---:|---:|---|---:|
| 1 | aws | 0.769 | 0.729 | 0.737 | [0.727, 0.731] | 24/63 |
| 2 | gliner | 0.812 | 0.718 | 0.735 | [0.717, 0.720] | 23/63 |
| 3 | gcp | 0.722 | 0.701 | 0.705 | [0.699, 0.703] | 18/63 |
| 4 | azure | 0.730 | 0.688 | 0.696 | [0.686, 0.690] | 17/63 |
| 5 | presidio | 0.419 | 0.563 | 0.527 | [0.561, 0.565] | 20/63 |
| 6 | regex | 0.856 | 0.348 | 0.395 | [0.346, 0.350] | 9/63 |
| 7 | piiranha | 0.444 | 0.329 | 0.347 | [0.327, 0.331] | 16/63 |
| 8 | stanza | 0.581 | 0.308 | 0.340 | [0.306, 0.310] | 3/63 |
| 9 | flair | 0.566 | 0.296 | 0.327 | [0.294, 0.298] | 3/63 |
| 10 | spacy | 0.463 | 0.294 | 0.317 | [0.292, 0.296] | 3/63 |
| 11 | scrubadub | 0.817 | 0.168 | 0.199 | [0.166, 0.169] | 12/63 |

## License

The **data** is released under **CC0-1.0** (public-domain dedication); the accompanying **code** (loaders, scorers, exporters) is licensed **Apache-2.0**. The two licenses are distinct — using the data does not subject you to the code license, and vice versa.
