# CAP-02 — One-command academically-sound assessment (copy-paste)

Run the **existing `pii-rate-elo` Elo tournament** against **PII-Anon v2.0.0** over a **powered, lattice-stratified,
byte-reproducible sample**, emitting an honest leaderboard with audited CIs + paired tests + RD convergence + a
non-strippable synthetic-only caveat + pre-registration + per-stage run-records.

> **Architecture:** eval-data **OWNS** sampling + observability + reporting; `pii-rate-elo` **CONSUMES** the
> mature Elo engine. The two are joined only by the **sample manifest** (the L1 seam). All inference is computed
> by the **audited `pii_anon_datasets.stats`** ring — the fabricated `pii-rate-elo/analysis/significance.py` is
> quarantined off the assessment call graph (P1, CI-enforced).

```bash
EVAL=/Users/subhashholla/Development/pii_anonymize_pseudonymize/pii-anon-core/pii-anon-eval-data
ELO=/Users/subhashholla/Development/pii_anonymize_pseudonymize/pii-anon-core/pii-anon-research-paper/pii-rate-elo-pipeline
CORPUS="$EVAL/src/pii_anon_datasets/splits/test_technology.jsonl.gz"   # fast real subset; use data/pii_anon.jsonl.gz for the FULL corpus

# 1) Draw a powered, lattice-stratified, byte-reproducible sample  →  the sample manifest (the L1 seam)
PYTHONPATH="$EVAL/src" "$EVAL/../../.venv/bin/python" -m pii_anon_datasets.assessment.sample \
    --preset powered-representative --seed 42 --corpus "$CORPUS" --out /tmp/cap02/manifest.json

# 2) Run the assessment: existing Elo tournament + AUDITED Wilson/Clopper-Pearson CIs + McNemar/Holm paired tests
#    + Glicko RD  →  results/leaderboard.{md,json} + prereg.json + run-records.jsonl
"$ELO/.venv/bin/python" -m pii_rate_elo_pipeline.cli assessment \
    --sample /tmp/cap02/manifest.json --corpus "$CORPUS" --out /tmp/cap02/results --seed 42

cat /tmp/cap02/results/leaderboard.md
```

Or use the bundled wrapper:

```bash
bash "$EVAL/scripts/run_powered_assessment.sh" "$CORPUS" /tmp/cap02 42
```

## Presets
- `--preset powered-representative` (**default**) — seeded stratified draw to the committed-lattice NIST tiers
  (CRITICAL 1522 / STANDARD 753 / LONG_TAIL 200); always labelled with its `PowerMatrix` verdict +
  per-cell named shortfall (never silently `LARGE`).
- `--preset full-corpus` — the **citable** descriptive-census run (no CI by default; opt-in).
- `--preset smoke` — fast fixed slice for CI / local dev.

## What you get (every academic-soundness bar item)
seeded/byte-reproducible (same seed → identical manifest + leaderboard) · powered sample meets the tiers OR is
flagged UNDER-SAMPLED / CORPUS-LIMITED with the named shortfall · a CI on every metric · system-vs-system claims
gated by a paired McNemar + Holm verdict · Glicko RD convergence reported (achieved max-RD) · the run
pre-registered (plan-hash, verified) + reproducible from the manifest · a non-strippable synthetic-only caveat on
every report.

## Honest scoping (INDICATIVE / Pass-2)
The bundled detector "systems" are **lightweight synthetic** placeholders — the run is **INDICATIVE**: it exercises
the full academic-soundness spine, but real detectors (Presidio / GLiNER / Piiranha) are **pluggable** and a
**Pass-2** item. Systems are injectable via `assessment_runner.run_assessment(systems={name: callable})`. The
real-data external-validity correlation slice (cycle-1 UC-13) remains the named credibility unlock (Pass-2).
See `_engineering-findings-verified.md` and `05-testing/release-readiness-report.md`.
