# CAP-02 — Verified engineering findings (firsthand, 2026-06-01)

> Direct file reads at HEAD (not agent-simulated). These are load-bearing inputs for Design (Stage 3) and
> Development (Stage 4). Line numbers are at the time of reading; re-confirm before editing.

## 1. pii-rate-elo `analysis/significance.py` — `SignificanceTester` class is statistically FABRICATED
Path: `pii-rate-elo-pipeline/src/pii_rate_elo_pipeline/analysis/significance.py`
- `_bootstrap_samples` (L202-210): `se = metric_value*(1-metric_value)/100` (hardcoded **100**, not n) then
  `noise = np.random.normal(0, se)`, `sample = metric_value + noise`. NOT a bootstrap — Gaussian noise around the
  point estimate. Uses numpy **global** RNG (not byte-reproducible).
- `_mcnemar_test` (L265-294): `difference=abs(val1-val2)`; `n_approx=100`; `z_stat=difference*sqrt(100)/0.05`;
  `pooled_sd=0.1`. Never sees discordant pairs / confusion matrices. Fabricated.
- The run path uses this class: `cli.py:33` imports it; `cli.py:240-245`
  `if config.analysis.run_significance_tests: sig_tester = SignificanceTester()`.
- NUANCE: the module ALSO has legit module-level `compute_bootstrap_ci` (L412, real resample) + `mcnemar_test`
  (L460, real discordant-pair McNemar + continuity + chi2) — but both use numpy global RNG (`np.random.seed`),
  so still NOT the byte-reproducible / integer-guarded path the academic bar needs.

**DECISION (for Design/Dev):** the assessment preset sets `analysis.run_significance_tests: false` and computes
all CIs + paired tests in eval-data's reporting layer via the AUDITED, seeded-local-RNG, integer-guarded
`stats/intervals.py` (wilson/clopper_pearson) + `stats/paired.py` (mcnemar_exact/mcnemar_chi2/paired_bootstrap).
`SignificanceTester` is QUARANTINED off the run path. (P1 — SHOWSTOPPER precondition.)

## 2. Dataset-seam drift pins (P2 — fix in S8)
Path: `pii-rate-elo-pipeline/src/pii_rate_elo_pipeline/`
- `datasets/converters/pii_anon_eval.py`: `num_records=159891` (L93) → **575604**; `license="CC-BY-4.0"` (L221) →
  **CC0** (or CC0-1.0); `citation="…v1.3.0"` (L222) → v2.0.0; docstring "v1.3.0" (L1). Also naive `max_samples`
  head-truncation (L82) — NOT a powered sampler (that's why CAP-02 adds one).
- `schema.py`: `version: str = "1.3.0"` (L137) → **2.0.0**; docstrings v1.3.0.
- Normalizer `_normalize_eval_row` ALREADY reads annotations: `labels_raw = list(row.get("annotations",
  row.get("labels", [])))` (L349). Internal field is `labels` populated from `annotations`. **So the drift is
  metadata-provenance (count/version/license/citation pins), NOT field-reading.**

**Regression contract (S8) pins (canonical, from eval-data `tests/test_doc_drift.py`):**
`CANONICAL_RECORDS="575,604"` · `CANONICAL_ANNOTATIONS="2,486,438"` · `CANONICAL_VERSION="2.0.0"` ·
`CANONICAL_ENTITY_COUNT=63` (derived from `taxonomy.ENTITY_TYPE_COUNT`). Data license = **CC0** (README:
"Apache 2.0 (code) / CC0 (data)"; provenance `license: CC0-1.0`). Plus schema fingerprint + dataset content hash.

## 3. Reuse APIs confirmed present (compose in S9/S10/S11 — do NOT reinvent)
eval-data `src/pii_anon_datasets/`:
- `__init__.py:55` `def load_dataset(*, subset, domain, split, language, dimension)` — canonical streaming loader (v2.0.0, `annotations`).
- `scripts/lattice_audit.py`: `committed_index` (L31), `record_increments` (L68), `audit_positives` (L83), `deficits` (L103) — streaming per-cell positive counts.
- `stats/power.py`: `Tier` (L54), `PowerClass` (L60, WELL/UNDER/EMPTY), `required_n` (L67), `TIER_SPECS` (L95 → 1522/753/200), `REID_TIER_SPECS` (L152 → 897/385), `classify` (L235), `CellAudit` (L289), `PowerMatrix` (L320) `.verdict()` (L351, SMALL/ADEQUATE/LARGE), `audit_crossing` (L428).
- `stats/intervals.py`: `wilson_interval`, `clopper_pearson_interval` (integer-guarded).
- `stats/paired.py`: `mcnemar_exact`, `mcnemar_chi2`, `paired_bootstrap_recall_delta` (seeded LOCAL random.Random).
- `scripts/benchmark_throughput.py`: seeded JSON run-record pattern + `reservoir_sample` (Algorithm-R) + `SEED_BENCHMARK`.
- `scoring/detection.py`: `DesignProvenance` (non-strippable caveat, `__post_init__` empty-guard) + `DESIGN_CAVEAT`.
- `stats/lattice.py`: `build_committed_lattice`, `load_lattice`; `python -m pii_anon_datasets.stats.lattice --check` (730 cells @ 47c3a8f).

pii-rate-elo `src/pii_rate_elo_pipeline/`:
- `tournament/engine.py` `PIIRateEloEngine`; `tournament/convergence.py` `ConvergenceChecker` (Glicko RD); `tournament/organizer.py`.
- `evaluation/metrics_bridge.py` `compute_span_metrics` (precision/recall/f1/f2 + tp/fp/fn).
- `config.py` `PipelineConfig.from_yaml`; `cli.py` (Typer).

## Env + baselines (confirmed 2026-06-01, before any CAP-02 mutation)
- eval-data: shared venv at `pii_anonymize_pseudonymize/.venv` (= `../../.venv` from the eval-data dir; Python 3.10.6,
  pytest 8.3.4; NO local .venv). Run modules with `PYTHONPATH=src`.
  **Agent-env baseline (this machine): 341 passed / 6 skipped** (→ 354/6 after the multitest GREEN). The 6 skips are
  ALL optional-dep-gated (graceful, NFR-050 lazy heavy-dep): `pyarrow` (test_parquet_export, test_croissant),
  `matplotlib` (test_viz), `anthropic` (test_llm_adversary), `spacy` (test_spacy_export×2). The canonical
  **363 passed / 1 skip** assumes those extras installed (original dev machine). **No-regression bar in THIS env =
  0 failures + only these dep-gated skips.** `lattice --check` OK (730 @ 47c3a8f); doc-drift NFR-013 7 pass.
  ⚠ matplotlib absent → S11 figure tests must skip gracefully here (mirror test_viz).
- pii-rate-elo: its OWN venv `pii-rate-elo-pipeline/.venv` (Python 3.10.6); importable as `pii_rate_elo_pipeline`.
  Run: `.venv/bin/python -m pytest -o addopts="-q"` (addopts forces --cov html; override for speed).
  Baseline: **253 passed / 1 skip in 17s**. pyproject: version 1.0.0; ruff line-length 120; mypy (lenient).
- `resolve_eval_dataset_path` (schema.py:583) walks ancestors → finds `pii-anon-eval-data/src/pii_anon_datasets/data/pii_anon.jsonl.gz`
  (the v2.0.0 corpus); env override `PII_ANON_DATASET_ROOT`. `_DEFAULT_DATASET="pii_anon_eval_v1"` (name, not version).

## S8 regression-test design (the v2.0.0 contract)
No real-data contract test exists today (`tests/test_datasets.py` only exercises a `MockDatasetConverter`). S8 RED test
(`tests/test_pii_anon_eval_v2_contract.py`): assert `PiiAnonEvalConverter().info()` reports num_records **575604**,
license **CC0(-1.0)**, citation **v2.0.0**, entity_types count **63**; and a small `max_samples=N` load yields records with
`version=="2.0.0"` and non-empty `labels` populated from `annotations`. Add a schema-fingerprint + content-hash pin
(crosswalk/regression contract). Keep pii-rate-elo pytest/ruff/mypy green.

## UT-1 correction (Design D6 synthesis agent error)
The D6 implementation-ready design flags UT-1 "pii-rate-elo contains zero .py files on this machine — biggest
implementation risk." **This is WRONG** — the agent used a bad relative path. The sister repo at
`../pii-anon-research-paper/pii-rate-elo-pipeline` (absolute: `/Users/subhashholla/Development/pii_anonymize_pseudonymize/pii-anon-core/pii-anon-research-paper/pii-rate-elo-pipeline`)
IS present and verified firsthand this session: `significance.py` read in full (fabrication confirmed L205-206/L271-281),
drift pins confirmed (converter L93/L221/L222; schema.py L137), and `pytest` ran **253 passed / 1 skip**.
**Always use ABSOLUTE paths for cross-repo work.** S8 story-0 ("re-confirm before edits") is effectively DONE.
Note: there is a SECOND version pin at `schema.py:752` (per D6 §10) — re-confirm and fix both.
