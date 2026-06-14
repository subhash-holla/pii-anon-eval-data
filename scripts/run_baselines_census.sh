#!/usr/bin/env bash
#
# run_baselines_census.sh — run the local PII-detector roster over a full split, efficiently and
# transparently, while keeping your Mac usable.
#
# What it does, and why it stays out of your way:
#   * Two concurrent lanes — a CPU lane (regex/scrubadub/spaCy/Stanza/Presidio) and a GPU lane
#     (GLiNER/Piiranha/Flair, which use Apple MPS). Both compute units stay busy, but only ONE heavy
#     transformer runs at a time, so the GPU is never oversubscribed.
#   * Thread caps + `nice` so background ML work yields to your foreground apps.
#   * `caffeinate` so the run survives display sleep (laptop lid open).
#   * Restart-safe: each detector writes to its own dir and is SKIPPED if already finished — re-run the
#     script to resume after an interruption. A single detector failure never loses the others.
#   * Live per-detector progress (%, rec/s, ETA) in each log, plus a status dashboard every minute.
#   * Merges every per-detector result into ONE F2-ranked leaderboard at the end.
#
# Usage (from anywhere):
#   scripts/run_baselines_census.sh                 # full English test census (30,995 records)
#   SPLIT=test LANGS=en OUT=results/baselines/tier1-en-full scripts/run_baselines_census.sh
#   LIMIT=200 scripts/run_baselines_census.sh        # quick smoke (first 200 records) to test the harness
#   THREADS=6 NICE=5 scripts/run_baselines_census.sh # tune resource headroom
#   DETECTORS="gliner piiranha" scripts/run_baselines_census.sh   # restrict the roster
#
# Detached + log to a file (recommended for the multi-hour census):
#   nohup scripts/run_baselines_census.sh > census.out 2>&1 &
#   tail -f census.out
#
# NOTE: no `set -u` (nounset). macOS ships bash 3.2, where expanding an EMPTY array under nounset —
# e.g. "${LIMIT_ARG[@]}" when --limit was not given, or an empty lane — wrongly errors "unbound variable"
# (fixed only in bash 4.4+). Keeping pipefail; variables below all have explicit defaults.
set -o pipefail

# ---- locate the repo + the project venv (no PATH ambiguity: use the venv's own pii-anon) ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PII_ANON="$REPO_ROOT/../../.venv/bin/pii-anon"
cd "$REPO_ROOT"
if [ ! -x "$PII_ANON" ]; then
  echo "ERROR: project venv pii-anon not found at $PII_ANON" >&2
  echo "       create/install it:  pip install -e \".[baselines,engines]\"  into ../../.venv" >&2
  exit 1
fi

# ---- config (override via env) ----
SPLIT="${SPLIT:-test}"
LANGS="${LANGS:-en}"
OUT="${OUT:-results/baselines/tier1-${LANGS}-full}"
LIMIT="${LIMIT:-}"                                   # empty = full split; set to smoke-test
NICE="${NICE:-10}"                                   # 0..19, higher = nicer to your foreground apps
CORES="$(sysctl -n hw.ncpu 2>/dev/null || echo 8)"
THREADS="${THREADS:-$(( CORES > 3 ? CORES / 2 : 1 ))}"   # half the cores -> leaves headroom for you
GPU_DETECTORS=(${GPU_DETECTORS:-gliner piiranha flair})
CPU_DETECTORS=(${CPU_DETECTORS:-regex scrubadub spacy stanza presidio})
# DETECTORS overrides the roster entirely (space-separated); it is partitioned into the two lanes.
if [ -n "${DETECTORS:-}" ]; then
  CPU_DETECTORS=(); GPU_DETECTORS=()
  for d in $DETECTORS; do
    case "$d" in gliner|piiranha|flair) GPU_DETECTORS+=("$d");; *) CPU_DETECTORS+=("$d");; esac
  done
fi
ALL_DETECTORS=("${CPU_DETECTORS[@]}" "${GPU_DETECTORS[@]}")

# ---- resource-friendly + robust runtime env ----
export OMP_NUM_THREADS="$THREADS" MKL_NUM_THREADS="$THREADS" OPENBLAS_NUM_THREADS="$THREADS" \
       VECLIB_MAXIMUM_THREADS="$THREADS" NUMEXPR_NUM_THREADS="$THREADS" \
       TOKENIZERS_PARALLELISM=false \
       PYTORCH_ENABLE_MPS_FALLBACK=1                 # any MPS-unsupported op falls back to CPU, never errors

LIMIT_ARG=(); [ -n "$LIMIT" ] && LIMIT_ARG=(--limit "$LIMIT")

echo "=================================================================="
echo " PII-Anon baseline census"
echo "   split=$SPLIT  languages=$LANGS  out=$OUT  limit=${LIMIT:-<full>}"
echo "   cores=$CORES  threads/proc=$THREADS  nice=$NICE"
echo "   CPU lane: ${CPU_DETECTORS[*]:-<none>}"
echo "   GPU lane: ${GPU_DETECTORS[*]:-<none>}  (one transformer at a time)"
echo "   live progress per detector -> $OUT/<detector>/run.log"
echo "=================================================================="
mkdir -p "$OUT"

# keep the Mac awake (idle) while this script's process tree runs; auto-released on exit
caffeinate -i -w $$ &

run_one() {
  local det="$1" dir="$OUT/$1"
  if [ -f "$dir/baseline_results.json" ]; then
    echo "==> $det: already done — skipping ($(date +%H:%M:%S))"
    return 0
  fi
  mkdir -p "$dir"
  echo "==> $det: STARTED $(date +%H:%M:%S)"
  nice -n "$NICE" "$PII_ANON" baselines \
       --detectors "$det" --split "$SPLIT" --languages "$LANGS" "${LIMIT_ARG[@]}" \
       --out "$dir" > "$dir/leaderboard.txt" 2> "$dir/run.log"
  local rc=$?
  if [ "$rc" -eq 0 ]; then
    echo "==> $det: FINISHED $(date +%H:%M:%S)"
  else
    echo "!!> $det: FAILED rc=$rc — see $dir/run.log (the run continues; this detector is just omitted)"
  fi
}
run_lane() { for d in "$@"; do run_one "$d"; done; }

# launch the two lanes concurrently
( run_lane "${CPU_DETECTORS[@]}" ) & CPU_PID=$!
( run_lane "${GPU_DETECTORS[@]}" ) & GPU_PID=$!

# status dashboard every 60s until both lanes finish
while kill -0 "$CPU_PID" 2>/dev/null || kill -0 "$GPU_PID" 2>/dev/null; do
  sleep 60
  echo "------ status $(date +%H:%M:%S) -------------------------------------------------"
  for d in "${ALL_DETECTORS[@]}"; do
    if [ -f "$OUT/$d/baseline_results.json" ]; then
      printf '  %-10s ✓ done\n' "$d"
    elif [ -f "$OUT/$d/run.log" ]; then
      line="$(grep -aE '[0-9]+/[0-9]+ \(' "$OUT/$d/run.log" 2>/dev/null | tail -1 | sed 's/.*: //')"
      printf '  %-10s %s\n' "$d" "${line:-building model…}"
    else
      printf '  %-10s pending\n' "$d"
    fi
  done
done
wait "$CPU_PID" "$GPU_PID" 2>/dev/null

# merge every per-detector result into one F2-ranked leaderboard
echo "==> merging per-detector runs into one leaderboard…"
shopt -s nullglob
RESULT_JSONS=("$OUT"/*/baseline_results.json)
if [ "${#RESULT_JSONS[@]}" -eq 0 ]; then
  echo "ERROR: no per-detector results were produced — check the run.log files in $OUT/*/" >&2
  exit 1
fi
nice -n "$NICE" "$PII_ANON" baselines --merge "${RESULT_JSONS[@]}" --out "$OUT" --quiet | tee "$OUT/leaderboard.md"

echo "=================================================================="
echo " DONE.  Combined: $OUT/baseline_results.json"
echo "        Leaderboard: $OUT/leaderboard.md   (+ run-record + sha256 provenance in $OUT/)"
echo "        Tell Claude the path and it will wire these numbers into BASELINES.md / README / the card."
echo "=================================================================="
