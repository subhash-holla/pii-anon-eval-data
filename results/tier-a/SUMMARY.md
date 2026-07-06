# Tier-A free bundle — synthesis

Source: `results/baselines/tier1-en-all/baseline_results.json` (n_records=31,048, n_gold=201,880, split=test/en). Zero detector re-runs.

## Load-bearing numbers
- **Coverage ceiling is real:** Pearson r(reachable/66, micro-recall) = **0.80**, r(reachable, macro-F2) = **0.86** across 11 detectors — recall tracks the label-map ceiling, not just model quality.
- **Strict leaderboard top-2:** aws (F2 0.7360) ≳ gliner (F2 0.7337).
- **Partial-overlap flips the top:** gliner (partial_f1 0.7787) > aws (0.7663).
- **Macro collapse:** aws 0.736→0.273; gliner 0.734→0.242; gcp 0.704→0.146 (micro→macro F2).
- **Power cliff:** 17 powered languages (≥1000 recs); 43 in the coverage tail.

## Files
- `coverage_ceiling.md` / `.png`
- `per_entity_type.md`
- `strict_vs_partial.md`
- `power_cliff.md`
- `macro_vs_micro.png`
