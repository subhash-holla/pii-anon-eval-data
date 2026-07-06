# Paired significance + complementarity (local detectors)

Over **201,880** gold spans, 7 local detectors. Paired McNemar (harness `stats.paired.mcnemar`, exact ≤1000 discordant else continuity-χ²), Holm–Bonferroni corrected (`stats.multitest`). RRS-style CI-overlap eyeballing is replaced by a paired test.

> The GLiNER-vs-AWS marquee comparison needs AWS per-record hits — a budget-gated cloud dump (not run here). This pins the **local** ranking.

## Adjacent-rank pairwise significance
| Pair (A>B) | recall A | recall B | Δrecall | b (A✓B✗) | c (A✗B✓) | p (Holm) | method | significant |
|---|---:|---:|---:|---:|---:|---:|---|:--:|
| gliner>presidio | 0.716 | 0.562 | +0.154 | 47,103 | 15,976 | 0.00e+00 | mcnemar-chi2-continuity | ✅ |
| presidio>regex | 0.562 | 0.349 | +0.213 | 58,840 | 15,746 | 0.00e+00 | mcnemar-chi2-continuity | ✅ |
| regex>piiranha | 0.349 | 0.327 | +0.021 | 16,752 | 12,460 | 8.55e-139 | mcnemar-chi2-continuity | ✅ |
| piiranha>stanza | 0.327 | 0.308 | +0.019 | 62,524 | 58,636 | 5.92e-29 | mcnemar-chi2-continuity | ✅ |
| stanza>spacy | 0.308 | 0.294 | +0.014 | 5,823 | 2,928 | 1.16e-209 | mcnemar-chi2-continuity | ✅ |
| spacy>scrubadub | 0.294 | 0.169 | +0.125 | 59,308 | 34,066 | 0.00e+00 | mcnemar-chi2-continuity | ✅ |

**6/6 adjacent pairs are significant after Holm correction.**

## Complementarity (oracle union recall)

Top local detector **gliner** recall = 0.716. Union recall when paired:

| + detector | union recall | gain over top |
|---|---:|---:|
| presidio | 0.795 | +0.079 |
| stanza | 0.769 | +0.053 |
| spacy | 0.766 | +0.050 |
| regex | 0.765 | +0.048 |
| piiranha | 0.742 | +0.026 |
| scrubadub | 0.721 | +0.005 |

**Full 7-detector oracle-union recall ceiling = 0.834** (vs best single 0.716) — +0.118 of recall is recoverable by an ensemble: detectors miss *different* spans (a novel complementarity finding).

