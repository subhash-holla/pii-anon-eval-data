## Baseline Detector Performance

How widely-used PII detectors score on PII-Anon **2.0.0** (`test` split, language `en`; 31,048 records / 201,880 gold spans). Ranked by **F2** (β=2 — recall-weighted, because a missed PII is the costly error).

> Power on a committed cell is statistical precision on the SYNTHETIC distribution, NOT external validity; not citable as a standalone recall claim absent the real-data correlation slice (FR-027). Synthetic-only (AX-001).

### Overall (micro-averaged, F2-ranked)

| Rank | Detector | Precision | Recall | F1 | F2 | Recall 95% CI | Coverage |
|---|---|---:|---:|---:|---:|---|---:|
| 1 | gliner | 0.813 | 0.716 | 0.762 | 0.734 | [0.714, 0.718] | 23/66 |
| 2 | presidio | 0.419 | 0.562 | 0.480 | 0.526 | [0.560, 0.564] | 20/66 |
| 3 | regex | 0.857 | 0.349 | 0.496 | 0.396 | [0.347, 0.351] | 9/66 |
| 4 | piiranha | 0.441 | 0.327 | 0.376 | 0.345 | [0.325, 0.329] | 16/66 |
| 5 | stanza | 0.583 | 0.308 | 0.403 | 0.340 | [0.306, 0.310] | 3/66 |
| 6 | flair | 0.565 | 0.295 | 0.388 | 0.326 | [0.293, 0.297] | 3/66 |
| 7 | spacy | 0.464 | 0.294 | 0.360 | 0.317 | [0.292, 0.296] | 3/66 |
| 8 | scrubadub | 0.818 | 0.169 | 0.280 | 0.201 | [0.167, 0.170] | 12/66 |

### F2 by domain

| Detector | clinical | financial | general | legal | technology |
|---|---:|---:|---:|---:|---:|
| gliner | 0.584 | 0.717 | 0.794 | 0.794 | 0.619 |
| presidio | 0.420 | 0.484 | 0.590 | 0.486 | 0.535 |
| regex | 0.326 | 0.391 | 0.426 | 0.276 | 0.557 |
| piiranha | 0.272 | 0.405 | 0.384 | 0.186 | 0.267 |
| stanza | 0.318 | 0.295 | 0.338 | 0.488 | 0.299 |
| flair | 0.293 | 0.225 | 0.342 | 0.542 | 0.240 |
| spacy | 0.285 | 0.248 | 0.330 | 0.460 | 0.278 |
| scrubadub | 0.119 | 0.160 | 0.271 | 0.081 | 0.190 |

> Headline metrics use strict-v1 exact (start, end, entity_type) span matching; the relaxed partial-overlap variant is reported separately as partial_f1 (0.5 overlap credit) and is EXCLUDED from all confidence intervals (reidx-02). Predicted spans are whitespace-trimmed to their entity boundary before matching (gold is authoritative and untrimmed).

Coverage = the count of canonical PII types reachable through a detector's native→63-type label map (its projection ceiling). Matching policy: `strict-v1`. Precision is shown beside recall so the false-positive tax of recall-weighted (F2) ranking stays visible.

pii-anon baselines: merged 8 runs -> results/baselines/en-local/baseline_results.json
