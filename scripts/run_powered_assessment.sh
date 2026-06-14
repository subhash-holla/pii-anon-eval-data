#!/usr/bin/env bash
# CAP-02 — one-command academically-sound pii-rate-elo assessment over a POWERED PII-Anon v2.0.0 sample.
#
# eval-data OWNS sampling + observability + reporting; pii-rate-elo CONSUMES the existing Elo tournament.
# Emits: results/leaderboard.{md,json} + prereg.json + run-records.jsonl with audited CIs + paired tests + RD
# + a non-strippable synthetic-only caveat.
#
# Usage: run_powered_assessment.sh [CORPUS] [OUT_DIR] [SEED] [PRESET]
#   CORPUS   default: the full v2.0.0 corpus (slow); pass a split (e.g. splits/test_technology.jsonl.gz) for a fast run
#   PRESET   powered-representative (default) | full-corpus | smoke
set -euo pipefail

EVAL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ELO="$EVAL/../pii-anon-research-paper/pii-rate-elo-pipeline"
CORPUS="${1:-$EVAL/src/pii_anon_datasets/data/pii_anon.jsonl.gz}"
OUT="${2:-/tmp/cap02}"
SEED="${3:-42}"
PRESET="${4:-powered-representative}"
EVAL_PY="${EVAL_PY:-$EVAL/../../.venv/bin/python}"
ELO_PY="${ELO_PY:-$ELO/.venv/bin/python}"

mkdir -p "$OUT"
echo "[1/2] powered sample ($PRESET, seed $SEED) → $OUT/manifest.json"
PYTHONPATH="$EVAL/src" "$EVAL_PY" -m pii_anon_datasets.assessment.sample \
    --preset "$PRESET" --seed "$SEED" --corpus "$CORPUS" --out "$OUT/manifest.json"

echo "[2/2] assessment → $OUT/results/leaderboard.md"
"$ELO_PY" -m pii_rate_elo_pipeline.cli assessment \
    --sample "$OUT/manifest.json" --corpus "$CORPUS" --out "$OUT/results" --seed "$SEED"

echo "Done. Leaderboard: $OUT/results/leaderboard.md"
