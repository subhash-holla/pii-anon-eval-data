# Baseline Detector Performance on PII-Anon v2.2.0

How do the most-used PII detection pipelines perform on PII-Anon? This page reports **traditional
detection metrics** — precision, recall, F1, and **F2** — for a roster of off-the-shelf detectors, with
per-entity-type / per-domain / per-language breakdowns and Wilson 95% confidence intervals.

> **Synthetic-only caveat (AX-001) — rides every number on this page.** These are *real detectors* run on
> *synthetic* data. The scores measure behavior on PII-Anon's synthetic distribution; they are **not**
> external-validity claims about production text. A real-data correlation slice (FR-027) is required before
> any number here is cited as a standalone recall claim. Power on PII-Anon is statistical precision on the
> synthetic distribution, not external validity.

## Why F2 (recall-weighted)?

A *missed* PII span is the costly error in de-identification — a leaked identifier is a breach, while a
false positive merely over-redacts. We therefore rank by **F2** (Fβ with β=2), which weights recall 4× more
than precision. Precision is reported **beside** recall in every table so the false-positive tax of
recall-weighted ranking stays visible — a detector cannot top the board by flagging everything.

## Leaderboard

<!-- BEGIN-LEADERBOARD (generated from results/baselines/tier1-en-all/baseline_results.json via `render_baseline_leaderboard`; do not hand-edit) -->
## Baseline Detector Performance

How widely-used PII detectors score on PII-Anon **2.2.0** (`test` split, language `en`; 31,048 records / 201,880 gold spans). Ranked by **F2** (β=2 — recall-weighted, because a missed PII is the costly error).

> Power on a committed cell is statistical precision on the SYNTHETIC distribution, NOT external validity; not citable as a standalone recall claim absent the real-data correlation slice (FR-027). Synthetic-only (AX-001).

### Overall (micro-averaged, F2-ranked)

| Rank | Detector | Precision | Recall | F1 | F2 | Recall 95% CI | Coverage |
|---|---|---:|---:|---:|---:|---|---:|
| 1 | aws | 0.769 | 0.728 | 0.748 | 0.736 | [0.726, 0.730] | 24/66 |
| 2 | gliner | 0.813 | 0.716 | 0.762 | 0.734 | [0.714, 0.718] | 23/66 |
| 3 | gcp | 0.722 | 0.700 | 0.711 | 0.704 | [0.698, 0.702] | 18/66 |
| 4 | azure | 0.730 | 0.688 | 0.709 | 0.696 | [0.686, 0.690] | 17/66 |
| 5 | presidio | 0.419 | 0.562 | 0.480 | 0.526 | [0.560, 0.564] | 20/66 |
| 6 | regex | 0.857 | 0.349 | 0.496 | 0.396 | [0.347, 0.351] | 9/66 |
| 7 | piiranha | 0.441 | 0.327 | 0.376 | 0.345 | [0.325, 0.329] | 16/66 |
| 8 | stanza | 0.583 | 0.308 | 0.403 | 0.340 | [0.306, 0.310] | 3/66 |
| 9 | flair | 0.565 | 0.295 | 0.388 | 0.326 | [0.293, 0.297] | 3/66 |
| 10 | spacy | 0.464 | 0.294 | 0.360 | 0.317 | [0.292, 0.296] | 3/66 |
| 11 | scrubadub | 0.818 | 0.169 | 0.280 | 0.201 | [0.167, 0.170] | 12/66 |

### F2 by domain

| Detector | clinical | financial | general | legal | technology |
|---|---:|---:|---:|---:|---:|
| aws | 0.578 | 0.780 | 0.796 | 0.667 | 0.651 |
| gliner | 0.584 | 0.717 | 0.794 | 0.794 | 0.619 |
| gcp | 0.588 | 0.672 | 0.761 | 0.692 | 0.670 |
| azure | 0.556 | 0.656 | 0.758 | 0.756 | 0.635 |
| presidio | 0.420 | 0.484 | 0.590 | 0.486 | 0.535 |
| regex | 0.326 | 0.391 | 0.426 | 0.276 | 0.557 |
| piiranha | 0.272 | 0.405 | 0.384 | 0.186 | 0.267 |
| stanza | 0.318 | 0.295 | 0.338 | 0.488 | 0.299 |
| flair | 0.293 | 0.225 | 0.342 | 0.542 | 0.240 |
| spacy | 0.285 | 0.248 | 0.330 | 0.460 | 0.278 |
| scrubadub | 0.119 | 0.160 | 0.271 | 0.081 | 0.190 |

> Headline metrics use strict-v1 exact (start, end, entity_type) span matching; the relaxed partial-overlap variant is reported separately as partial_f1 (0.5 overlap credit) and is EXCLUDED from all confidence intervals (reidx-02). Predicted spans are whitespace-trimmed to their entity boundary before matching (gold is authoritative and untrimmed).

Coverage = the count of canonical PII types reachable through a detector's native→66-type label map (its projection ceiling). Matching policy: `strict-v1`. Precision is shown beside recall so the false-positive tax of recall-weighted (F2) ranking stays visible.
<!-- END-LEADERBOARD -->

## Full multilingual test

The headline above is the English `test` split. PII-Anon also ships a **60-language** `test` split
(115,618 records). The table below extends the roster to the **entire multilingual split** — the 8 local
detectors over all 60 languages, and each cloud DLP provider over the languages it officially supports for
PII (AWS Comprehend is English-only; Azure and GCP cover the major-language subset; `—` = a language a
provider does not support, never faked). Regenerate it from a completed run with
`scripts/run_full_leaderboard.sh` → `scripts/sync_cards.py matrix` (see [EVAL_RUNBOOK.md](EVAL_RUNBOOK.md)).

<!-- BEGIN-LEADERBOARD-MULTILINGUAL (generated from results/baselines/fulltest-local + fulltest-cloud via `scripts/sync_cards.py matrix`; do not hand-edit) -->
Full multilingual `test` split — **F2 by language** (β=2, recall-weighted). Local detectors run over all 60 languages; each cloud provider runs only the languages it officially supports for PII (— = unsupported by that provider, never faked). Columns are the 12 major languages (each >6k records); the full 60-language breakdown is in `results/baselines/fulltest-local/baseline_results.json`.

| Detector | en | nl | hi | ko | pt | it | es | ar | zh | fr | ja | de |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gliner | 0.734 | 0.849 | 0.835 | 0.834 | 0.838 | 0.839 | 0.832 | 0.833 | 0.820 | 0.814 | 0.815 | 0.812 |
| presidio | 0.526 | 0.614 | 0.613 | 0.390 | 0.612 | 0.611 | 0.567 | 0.415 | 0.377 | 0.551 | 0.382 | 0.567 |
| piiranha | 0.345 | 0.422 | 0.397 | 0.668 | 0.423 | 0.401 | 0.404 | 0.410 | 0.681 | 0.372 | 0.492 | 0.364 |
| regex | 0.396 | 0.441 | 0.439 | 0.107 | 0.399 | 0.441 | 0.294 | 0.120 | 0.125 | 0.418 | 0.127 | 0.394 |
| spacy | 0.317 | 0.345 | 0.360 | 0.033 | 0.349 | 0.357 | 0.309 | 0.082 | 0.041 | 0.309 | 0.049 | 0.326 |
| stanza | 0.340 | 0.373 | 0.375 | 0.039 | 0.363 | 0.365 | 0.352 | 0.046 | 0.044 | 0.349 | 0.050 | 0.356 |
| flair | 0.326 | 0.358 | 0.334 | 0.036 | 0.298 | 0.354 | 0.349 | 0.046 | 0.042 | 0.343 | 0.048 | 0.328 |
| scrubadub | 0.201 | 0.378 | 0.372 | 0.028 | 0.333 | 0.374 | 0.159 | 0.030 | 0.034 | 0.288 | 0.039 | 0.281 |
| gcp | 0.704 | 0.731 | 0.761 | 0.564 | 0.726 | 0.737 | 0.729 | 0.711 | 0.580 | 0.733 | 0.436 | 0.741 |
| azure | 0.696 | 0.738 | — | 0.349 | 0.695 | 0.739 | 0.555 | — | 0.331 | 0.685 | 0.340 | 0.672 |
<!-- END-LEADERBOARD-MULTILINGUAL -->

## Cost-normalized companion

<!-- BEGIN-COST -->

### Cost-normalized (companion lens)

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
<!-- END-COST -->

## Harness validity bounds (sanity checks — NOT ranked)

These rows verify the **scoring harness**, not detector quality, and are deliberately excluded from the
11-detector leaderboard above. Computed on a 2,000-record English-test subsample (deterministic). A null
detector floors at F2≈0, a perfect oracle (reads gold) reaches F2=1.0, and `always_person_name` (tags every
whitespace token `PERSON_NAME`) shows the precision floor of blanket tagging — and scores near-0 under
strict span matching because per-token spans do not match multi-token gold spans.

<!-- BEGIN-SANITY -->
| Rank | Detector | Precision | Recall | F1 | F2 | Recall 95% CI | Coverage |
|---|---|---:|---:|---:|---:|---|---:|
| 1 | oracle | 1.000 | 1.000 | 1.000 | 1.000 | [1.000, 1.000] | 66/66 |
| 2 | always_person_name | 0.002 | 0.012 | 0.004 | 0.006 | [0.012, 0.013] | 1/66 |
| 3 | null | 0.000 | 0.000 | 0.000 | 0.000 | [0.000, 0.000] | 0/66 |
<!-- END-SANITY -->

## Methodology

- **Detectors.** Local: `regex` (a pattern lower bound), Microsoft **Presidio**, **spaCy** NER
  (`en_core_web_lg`), **GLiNER** (`urchade/gliner_multi_pii-v1`), **Piiranha**
  (`iiiorg/piiranha-v1-detect-personal-information`), **scrubadub**, **Stanza**, **Flair**. Cloud DLP
  adapters (AWS Comprehend, GCP DLP, Azure AI Language) are **run behind credentials** on the full English
  test and included in the leaderboard above (budget-gated behind `--cloud`; reported as a **single run** of
  non-deterministic managed services — a variance re-run is a separate decision). An LLM detector
  (GPT/Claude) runs behind an API key (`--detectors llm`).
- **Scoring.** Every published number is routed through the audited scorer
  (`pii_anon_datasets.scoring.detection.score_detection`): integer strict-match counts → precision / recall /
  F1 / F2, each headline rate carrying a **Wilson 95% CI** (Bernoulli counts only).
- **Micro vs. macro.** *Micro* pools counts across all spans (frequency-weighted); *macro* is the unweighted
  mean over entity types present in gold (every PII type counts equally, so a missed rare-but-critical type
  — e.g. SSN — cannot hide behind frequent ones). The leaderboard ranks by **micro F2**; macro F2 is shown
  alongside.

## Span-matching policy (disclosed)

- **strict-v1 (headline).** A predicted span is a true positive iff its `(start, end, entity_type)` exactly
  matches a gold span. Deterministic, order-independent multiset matching.
- **Relaxed / partial-overlap.** A same-type overlapping span earns 0.5 credit and is reported separately as
  `partial_f1`. It is a **point estimate** and is **excluded from all confidence intervals** (a partial
  match is not a Bernoulli success).
- **Whitespace trimming.** Predicted spans are trimmed to their non-whitespace entity boundary before
  matching (tokenizer-based detectors often emit a leading sub-word space). Gold is authoritative and never
  trimmed.

## Label-map coverage (lossiness)

Each detector emits its own native label set, which we project onto the dataset's canonical taxonomy. That
projection is lossy: a detector can only ever score a true positive on a type its label map can *reach*.
The **Coverage** column (`reachable / 66`) is that projection ceiling — independent of model quality. For
example, a general-purpose 4-class NER model (PER / LOC / ORG / MISC) reaches at most 3 of the 66 types, so
its recall is structurally bounded however good the model is. The 3 GDPR **Art-9 special-category** types
added in the 63→66 taxonomy expansion sit in the unreachable set of *every* off-the-shelf detector (recall 0
by construction — the coverage-ceiling finding extended to special-category PII; see
[art9_coverage_v22dev.md](results/tier-a/art9_coverage_v22dev.md)). Per-detector reachable / dropped /
unreachable type lists are in `baseline_results.json` under each detector's `coverage` block.

The label maps for Presidio / GLiNER / Piiranha mirror the audited maps used in the companion Elo pipeline
(re-implemented here — this dataset package never imports that pipeline). The spaCy / scrubadub / Stanza /
Flair maps are designed here, deliberately **dropping** coarse labels (e.g. spaCy's generic `DATE`, which is
not the corpus's specific `DATE_OF_BIRTH` / `TIMESTAMP`, and `NORP`, which conflates
nationality / religion / politics) rather than inflating false positives.

## Honesty checklist

1. **Synthetic-only (AX-001)** — every number; real detectors on synthetic data ≠ external validity.
2. **Span-matching policy disclosed** — strict-v1 headline + relaxed partial-overlap point estimate.
3. **Label-map lossiness disclosed** — per-detector coverage (reachable / 66) and dropped native labels.
4. **Precision shown beside recall** — the false-positive tax of F2 ranking is never hidden.

## Reproduce

```bash
pip install -e ".[baselines,engines]"          # detector libraries (heavy; lazy-loaded)
python -m spacy download en_core_web_lg          # Presidio + spaCy
# Tier 1 — English test split (headline). Drop --languages for all languages; raise the sample for a census.
pii-anon baselines \
  --detectors regex,scrubadub,spacy,stanza,gliner,presidio,flair,piiranha \
  --split test --languages en --out results/baselines/tier1-en
```

Emits, into `--out`:

- `baseline_results.json` — the canonical sorted-key leaderboard (overall + per-type / per-domain /
  per-language, micro + macro, Wilson CIs, the relaxed `partial_f1`, and the AX-001 caveat);
- `baseline_run_record.jsonl` — seed / dataset version / code commit / content hash (verdict: `INDICATIVE`);
- `baseline_provenance.json` — a sha256 index over the artifacts above.

Cloud DLP detectors require explicit opt-in (`--cloud`) **and** a confirmed budget; see
**[CLOUD_DLP_COST.md](CLOUD_DLP_COST.md)** for the grounded ×2 estimate (≈ $88 for the English test across
all three providers; ≈ $1,450 for the full 60-language corpus, Azure-dominated) before enabling them.
