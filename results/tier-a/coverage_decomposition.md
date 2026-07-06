# Within-reach decomposition of the coverage ceiling (CL-02b headline)

> **Honesty (AX-001 synthetic-only; n=11 → structural *bound*, not a law).** Mechanism: unreachable types → recall exactly 0 → overall recall is upper-bounded by coverage. The contribution is the coverage-*independent* within-reach skill factor + the structural framing, NOT the correlation. Denominator pinned to the frozen 63 (`label_maps_63.json`).

**Headline reproduced: True** — the overall coverage↔recall correlation collapses once we condition on reach, and the collapse holds under all three crosswalks.

**SC-02b(a) test.** The contrast is a PAIRED bootstrap of the drop Δr = overall r − within-reach r (resample detectors, recompute both correlations on the same resample); the headline holds iff this CI excludes 0. At n=11 the *marginal* Fisher-z CIs are wide and overlap — reported below for transparency but NOT the gate (the paired drop CI + leave-one-out stability carry the contrast).

| Crosswalk | overall r | within-reach r | drop | drop 95% bootstrap CI | mean skill |
|---|---:|---:|---:|---|---:|
| XW-EXACT | 0.797 | 0.050 | 0.748 | [0.325, 1.114] | 0.751 |
| XW-BROAD | 0.805 | 0.143 | 0.663 | [0.253, 1.007] | 0.738 |
| XW-BROAD-PRIME | 0.804 | 0.143 | 0.661 | [0.257, 0.991] | 0.738 |

_Marginal Fisher-z CIs (context, n=11, wide/overlapping — not the gate):_ XW-EXACT: overall [0.379, 0.945] vs within [-0.567, 0.631]; XW-BROAD: overall [0.397, 0.947] vs within [-0.500, 0.684]; XW-BROAD-PRIME: overall [0.393, 0.947] vs within [-0.500, 0.684].

## Per-detector (XW-EXACT)

| Detector | coverage (reach/63) | micro recall | within-reach skill |
|---|---:|---:|---:|
| regex | 9/63 | 0.349 | 0.936 |
| aws | 24/63 | 0.728 | 0.923 |
| gcp | 18/63 | 0.700 | 0.879 |
| azure | 17/63 | 0.688 | 0.857 |
| gliner | 23/63 | 0.716 | 0.852 |
| stanza | 3/63 | 0.308 | 0.825 |
| flair | 3/63 | 0.295 | 0.791 |
| spacy | 3/63 | 0.294 | 0.787 |
| presidio | 20/63 | 0.562 | 0.690 |
| piiranha | 16/63 | 0.327 | 0.436 |
| scrubadub | 12/63 | 0.169 | 0.284 |
