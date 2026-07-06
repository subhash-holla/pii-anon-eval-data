# Label-map fairness audit

Pre-empts the conflict-of-interest objection to an author-built leaderboard. Every independent detector's predictions are projected through a published native→66-canonical `label_map` (`baselines/*.py`); the canonical set has **66 types**. The author's own `pii_anon`/`pii_anon_swarm` is **excluded from the leaderboard** and uses the **same** crosswalk machinery (`tests/test_coi.py`, `tests/test_crosswalk.py`).

## Per-detector projection

| Detector | native labels | mapped→canonical | dropped (native) | reachable/66 | unreachable | unfair drop? |
|---|---:|---:|---:|---:|---:|:--:|
| regex | 9 | 9 | 0 | 9/66 | 57 | none |
| scrubadub | 12 | 12 | 0 | 12/66 | 54 | none |
| spacy | 18 | 5 | 13 | 3/66 | 63 | none |
| presidio | 28 | 27 | 1 | 20/66 | 46 | none |
| gliner | 33 | 33 | 0 | 23/66 | 43 | none |
| piiranha | 20 | 19 | 1 | 16/66 | 50 | none |
| stanza | 18 | 5 | 13 | 3/66 | 63 | none |
| flair | 5 | 4 | 1 | 3/66 | 63 | none |

## Dropped native labels (per detector) — are any a PII type being discarded?

- **regex**: drops nothing — every native label reaches a canonical type.
- **scrubadub**: drops nothing — every native label reaches a canonical type.
- **spacy**: drops `CARDINAL, DATE, EVENT, LANGUAGE, LAW, MONEY, NORP, ORDINAL, PERCENT, PRODUCT, QUANTITY, TIME, WORK_OF_ART` — all non-PII or multi-category native labels (no clean canonical home).
- **presidio**: drops `NRP` — all non-PII or multi-category native labels (no clean canonical home).
- **gliner**: drops nothing — every native label reaches a canonical type.
- **piiranha**: drops `TITLE` — all non-PII or multi-category native labels (no clean canonical home).
- **stanza**: drops `CARDINAL, DATE, EVENT, LANGUAGE, LAW, MONEY, NORP, ORDINAL, PERCENT, PRODUCT, QUANTITY, TIME, WORK_OF_ART` — all non-PII or multi-category native labels (no clean canonical home).
- **flair**: drops `MISC` — all non-PII or multi-category native labels (no clean canonical home).

## Why the coverage ceiling is structural, not a handicap

- A detector can only be projected to canonical types its **own model emits**. spaCy/Stanza/Flair emit a 3–4-class scheme (PER/LOC/ORG/MISC), so they are *structurally* capped at ~3 reachable types — no label map could lift that without inventing predictions the model never made.

- The maps are **maximal**: every native label with a clean canonical home is mapped (the only drops are genuinely non-PII labels like CARDINAL/ORDINAL/MONEY or multi-category labels like spaCy's NORP, which spans nationality/religion/politics and has no single canonical target).

- **NORP note (the one defensible borderline):** spaCy's NORP could partially map to NATIONALITY / ETHNICITY / RELIGIOUS_BELIEF / POLITICAL_OPINION. It is dropped because a 1→4 ambiguous projection would manufacture false positives; a reviewer who prefers the opposite can re-run with NORP mapped (the maps are public and editable). This is disclosed, not hidden.

- Every per-detector `reachable_types` / `dropped_native` is published in `baseline_results.json`; the maps are in `baselines/*.py`. The projection is **reproducible and inspectable** by anyone.


## Verdict

**FAIR.** No independent detector has a PII canonical type unfairly dropped from its label map. Coverage differences reflect each model's native label inventory, the maps are maximal and published, the same crosswalk applies to the (excluded) author system, and the projection is fully reproducible. The author-built leaderboard does not handicap competitors.
