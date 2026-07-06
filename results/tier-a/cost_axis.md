# Cost-normalized leaderboard (companion)

English test split: 31,048 docs. Cloud = June-2026 list price ×2 safety (CLOUD_DLP_COST.md); local detectors are free (on-host).

| Rank | Detector | F2 | $/1k records | Cost per F2-point |
|---|---|---:|---:|---:|
| 1 | aws | 0.736 | $0.8250 | $1.1210 |
| 2 | gliner | 0.734 | free | free |
| 3 | gcp | 0.704 | free-tier* | free-tier* |
| 4 | azure | 0.696 | $2.0276 | $2.9122 |
| 5 | presidio | 0.526 | free | free |
| 6 | regex | 0.396 | free | free |
| 7 | piiranha | 0.345 | free | free |
| 8 | stanza | 0.340 | free | free |
| 9 | flair | 0.326 | free | free |
| 10 | spacy | 0.317 | free | free |
| 11 | scrubadub | 0.201 | free | free |

_`free` = on-host local model (no API cost). `free-tier*` = a **paid cloud DLP** service whose cost is $0 only because this 31,048-doc English slice is under the provider's free tier (e.g. GCP's 1 GB/month); it is NOT free at production scale._
