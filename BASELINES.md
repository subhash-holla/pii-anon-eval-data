# Baseline Detector Performance on PII-Anon v2.0.0

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
PII-Anon **2.0.0** · `test` split · language `en` · **30,995 records / 201,701 gold spans** · **11 detectors** (8 local + 3 cloud DLP), ranked by **F2** (β=2, recall-weighted). Cloud DLP numbers are a **single run** of non-deterministic managed services (a variance re-run is a separate decision); the local detectors are deterministic.

### Overall (micro-averaged, F2-ranked)

| Rank | Detector | Precision | Recall | F1 | F2 | Recall 95% CI | Coverage |
|---|---|---:|---:|---:|---:|---|---:|
| 1 | aws | 0.769 | 0.729 | 0.748 | 0.737 | [0.727, 0.731] | 24/63 |
| 2 | gliner | 0.812 | 0.718 | 0.762 | 0.735 | [0.717, 0.720] | 23/63 |
| 3 | gcp | 0.722 | 0.701 | 0.712 | 0.705 | [0.699, 0.703] | 18/63 |
| 4 | azure | 0.730 | 0.688 | 0.709 | 0.696 | [0.686, 0.690] | 17/63 |
| 5 | presidio | 0.419 | 0.563 | 0.480 | 0.527 | [0.561, 0.565] | 20/63 |
| 6 | regex | 0.856 | 0.348 | 0.495 | 0.395 | [0.346, 0.350] | 9/63 |
| 7 | piiranha | 0.444 | 0.329 | 0.378 | 0.347 | [0.327, 0.331] | 16/63 |
| 8 | stanza | 0.581 | 0.308 | 0.403 | 0.340 | [0.306, 0.310] | 3/63 |
| 9 | flair | 0.566 | 0.296 | 0.389 | 0.327 | [0.294, 0.298] | 3/63 |
| 10 | spacy | 0.463 | 0.294 | 0.360 | 0.317 | [0.292, 0.296] | 3/63 |
| 11 | scrubadub | 0.817 | 0.168 | 0.278 | 0.199 | [0.166, 0.169] | 12/63 |

### F2 by domain

| Detector | clinical | financial | general | legal | technology |
|---|---:|---:|---:|---:|---:|
| aws | 0.579 | 0.780 | 0.797 | 0.665 | 0.655 |
| gliner | 0.584 | 0.720 | 0.796 | 0.792 | 0.620 |
| gcp | 0.589 | 0.672 | 0.763 | 0.692 | 0.672 |
| azure | 0.551 | 0.660 | 0.759 | 0.751 | 0.635 |
| presidio | 0.418 | 0.484 | 0.591 | 0.488 | 0.539 |
| regex | 0.327 | 0.393 | 0.426 | 0.272 | 0.560 |
| piiranha | 0.273 | 0.410 | 0.385 | 0.180 | 0.273 |
| stanza | 0.316 | 0.295 | 0.339 | 0.489 | 0.297 |
| flair | 0.293 | 0.225 | 0.343 | 0.543 | 0.238 |
| spacy | 0.283 | 0.249 | 0.331 | 0.463 | 0.278 |
| scrubadub | 0.117 | 0.160 | 0.270 | 0.078 | 0.191 |

**Headline:** GLiNER (`gliner_multi_pii-v1`, a free local model) is statistically tied with AWS Comprehend for the top spot (F2 0.735 vs 0.737; GLiNER leads on F1 at 0.762 via its 0.812 precision) and outscores both GCP DLP and Azure AI Language. The Coverage column (reachable / 63) caps the general-NER detectors (spaCy / Stanza / Flair at 3/63) regardless of model quality.
<!-- END-LEADERBOARD -->

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

Each detector emits its own native label set, which we project onto PII-Anon's **63-type taxonomy**. That
projection is lossy: a detector can only ever score a true positive on a type its label map can *reach*.
The **Coverage** column (`reachable / 63`) is that projection ceiling — independent of model quality. For
example, a general-purpose 4-class NER model (PER / LOC / ORG / MISC) reaches at most 3 of the 63 types, so
its recall is structurally bounded however good the model is. Per-detector reachable / dropped / unreachable
type lists are in `baseline_results.json` under each detector's `coverage` block.

The label maps for Presidio / GLiNER / Piiranha mirror the audited maps used in the companion Elo pipeline
(re-implemented here — this dataset package never imports that pipeline). The spaCy / scrubadub / Stanza /
Flair maps are designed here, deliberately **dropping** coarse labels (e.g. spaCy's generic `DATE`, which is
not the corpus's specific `DATE_OF_BIRTH` / `TIMESTAMP`, and `NORP`, which conflates
nationality / religion / politics) rather than inflating false positives.

## Honesty checklist

1. **Synthetic-only (AX-001)** — every number; real detectors on synthetic data ≠ external validity.
2. **Span-matching policy disclosed** — strict-v1 headline + relaxed partial-overlap point estimate.
3. **Label-map lossiness disclosed** — per-detector coverage (reachable / 63) and dropped native labels.
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
