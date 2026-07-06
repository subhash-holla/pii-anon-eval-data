## Baseline Detector Performance

How widely-used PII detectors score on PII-Anon **2.0.0** (`test` split, language `en`; 31,048 records / 201,880 gold spans). Ranked by **F2** (β=2 — recall-weighted, because a missed PII is the costly error).

> Power on a committed cell is statistical precision on the SYNTHETIC distribution, NOT external validity; not citable as a standalone recall claim absent the real-data correlation slice (FR-027). Synthetic-only (AX-001).

### Overall (micro-averaged, F2-ranked)

| Rank | Detector | Precision | Recall | F1 | F2 | Recall 95% CI | Coverage |
|---|---|---:|---:|---:|---:|---|---:|
| 1 | spacy | 0.464 | 0.294 | 0.360 | 0.317 | [0.292, 0.296] | 3/66 |

### F2 by domain

| Detector | clinical | financial | general | legal | technology |
|---|---:|---:|---:|---:|---:|
| spacy | 0.285 | 0.248 | 0.330 | 0.460 | 0.278 |

> Headline metrics use strict-v1 exact (start, end, entity_type) span matching; the relaxed partial-overlap variant is reported separately as partial_f1 (0.5 overlap credit) and is EXCLUDED from all confidence intervals (reidx-02). Predicted spans are whitespace-trimmed to their entity boundary before matching (gold is authoritative and untrimmed).

Coverage = the count of canonical PII types reachable through a detector's native→63-type label map (its projection ceiling). Matching policy: `strict-v1`. Precision is shown beside recall so the false-positive tax of recall-weighted (F2) ranking stays visible.

pii-anon baselines: merged 1 runs -> results/baselines/en-local/spacy/baseline_results.json
