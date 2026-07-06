# Coverage ceiling vs recall (structural label-map bound)

Pearson r(reachable, micro-recall) = **0.797**  ·  r(reachable, macro-F2) = **0.863**  (n=11 detectors).

Recall is bounded by how many of the 66 canonical types a detector's native→66 label map can even reach — a *structural* ceiling independent of model quality.

| Detector | Kind | Coverage (reach/66) | Micro recall | Micro F2 | Macro F2 |
|---|---|---:|---:|---:|---:|
| aws | cloud | 24/66 | 0.728 | 0.7360 | 0.2726 |
| gliner | local | 23/66 | 0.716 | 0.7337 | 0.2424 |
| gcp | cloud | 18/66 | 0.700 | 0.7040 | 0.1456 |
| azure | cloud | 17/66 | 0.688 | 0.6962 | 0.1334 |
| presidio | local | 20/66 | 0.562 | 0.5262 | 0.0914 |
| regex | local | 9/66 | 0.349 | 0.3956 | 0.1214 |
| piiranha | local | 16/66 | 0.327 | 0.3452 | 0.1084 |
| stanza | local | 3/66 | 0.308 | 0.3402 | 0.0211 |
| flair | local | 3/66 | 0.295 | 0.3264 | 0.0207 |
| spacy | local | 3/66 | 0.294 | 0.3170 | 0.0181 |
| scrubadub | local | 12/66 | 0.169 | 0.2006 | 0.0406 |
