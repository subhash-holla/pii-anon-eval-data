# Strict-v1 vs partial-overlap re-ranking

`partial_f1` gives 0.5 credit for a same-type overlapping span (no CI by design). Under partial credit the ordering near the top can flip — a robustness check on the headline.

| Strict rank | Detector | Micro F2 (strict) | partial_f1 | Partial rank | Δrank |
|---:|---|---:|---:|---:|---:|
| 1 | aws | 0.7360 | 0.7663 | 2 | -1 |
| 2 | gliner | 0.7337 | 0.7787 | 1 | +1 |
| 3 | gcp | 0.7040 | 0.7238 | 4 | -1 |
| 4 | azure | 0.6962 | 0.7337 | 3 | +1 |
| 5 | presidio | 0.5262 | 0.5173 | 5 | +0 |
| 6 | regex | 0.3956 | 0.4958 | 6 | +0 |
| 7 | piiranha | 0.3452 | 0.4796 | 7 | +0 |
| 8 | stanza | 0.3402 | 0.4297 | 8 | +0 |
| 9 | flair | 0.3264 | 0.4062 | 9 | +0 |
| 10 | spacy | 0.3170 | 0.3944 | 10 | +0 |
| 11 | scrubadub | 0.2006 | 0.2944 | 11 | +0 |

**Rank changes under partial credit:** aws, gliner, gcp, azure.
