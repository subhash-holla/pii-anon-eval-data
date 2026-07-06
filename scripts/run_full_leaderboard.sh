#!/usr/bin/env bash
# run_full_leaderboard.sh — ONE command to score all 11 detectors over the full multilingual `test` split
# and regenerate the multilingual card section.
#   * Local lane: the 8 local detectors over all 60 languages (CPU + GPU lanes, restart-safe).
#   * Cloud lane: aws / gcp / azure, each over the languages it officially supports — Azure capped to a USD
#     budget so it never blows the free credit. Restart-safe per (provider, language) shard.
#   * Report: assembles the by-language F2 matrix into BASELINES.md (BEGIN/END-LEADERBOARD-MULTILINGUAL).
# Portable (macOS/MPS + Linux/CUDA). BUDGET-GATED: no cloud money is spent without an explicit confirmation.
#
# Usage:
#   scripts/run_full_leaderboard.sh --dry-run                 # preflight only — prints cost plan, spends $0
#   LIMIT=50 scripts/run_full_leaderboard.sh --no-cloud       # local smoke (first 50 records), no cloud
#   scripts/run_full_leaderboard.sh --max-azure-usd 90        # full run; Azure capped at $90; confirm to spend
#   scripts/run_full_leaderboard.sh --cloud-only --yes        # cloud shards only, skip the confirm prompt
#
# Env overrides: SPLIT, OUT_LOCAL, OUT_CLOUD, THREADS, LIMIT, PII_ANON_BIN, PYTHON_BIN, LOCAL_CPU, LOCAL_GPU.
# NOTE: no `set -u` — macOS ships bash 3.2 where expanding an empty array under nounset wrongly errors.
set -o pipefail

# ---- locate repo + the project's pii-anon / python (no PATH ambiguity) ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT" || exit 1

PII_ANON="${PII_ANON_BIN:-}"
[ -z "$PII_ANON" ] && for c in "$REPO_ROOT/../../.venv/bin/pii-anon" "$REPO_ROOT/.venv/bin/pii-anon" "$(command -v pii-anon 2>/dev/null)"; do
  [ -n "$c" ] && [ -x "$c" ] && PII_ANON="$c" && break
done
PYTHON="${PYTHON_BIN:-}"
[ -z "$PYTHON" ] && for c in "$REPO_ROOT/../../.venv/bin/python" "$REPO_ROOT/.venv/bin/python" "$(command -v python3 2>/dev/null)"; do
  [ -n "$c" ] && [ -x "$c" ] && PYTHON="$c" && break
done
[ -x "$PII_ANON" ] || { echo "ERROR: pii-anon not found — set PII_ANON_BIN or pip install -e \".[baselines,engines,cloud]\"" >&2; exit 1; }
[ -x "$PYTHON" ]   || { echo "ERROR: python not found — set PYTHON_BIN" >&2; exit 1; }

# ---- config + flags ----
SPLIT="${SPLIT:-test}"
OUT_LOCAL="${OUT_LOCAL:-results/baselines/fulltest-local}"
OUT_CLOUD="${OUT_CLOUD:-results/baselines/fulltest-cloud}"
MAX_AZURE_USD="${MAX_AZURE_USD:-90}"
DO_LOCAL=1; DO_CLOUD=1; DRY_RUN=0; ASSUME_YES=0; DO_REPORT=1
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --no-cloud) DO_CLOUD=0 ;;
    --cloud-only) DO_LOCAL=0 ;;
    --no-report) DO_REPORT=0 ;;
    --yes|-y) ASSUME_YES=1 ;;
    --max-azure-usd) shift; MAX_AZURE_USD="$1" ;;
    --max-azure-usd=*) MAX_AZURE_USD="${1#*=}" ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "unknown flag: $1 (try --help)" >&2; exit 2 ;;
  esac
  shift
done

# ---- OS-aware runtime env (MPS on macOS, CUDA on Linux) ----
THREADS="${THREADS:-4}"
export OMP_NUM_THREADS="$THREADS" MKL_NUM_THREADS="$THREADS" OPENBLAS_NUM_THREADS="$THREADS" \
       NUMEXPR_NUM_THREADS="$THREADS" TOKENIZERS_PARALLELISM=false
if [ "$(uname -s)" = "Darwin" ]; then
  export PYTORCH_ENABLE_MPS_FALLBACK=1
  command -v caffeinate >/dev/null 2>&1 && caffeinate -i -w $$ &   # keep the Mac awake while we run
fi
LIMIT="${LIMIT:-}"
LIMIT_ARG=(); [ -n "$LIMIT" ] && LIMIT_ARG=(--limit "$LIMIT")

LOCAL_CPU="${LOCAL_CPU:-regex scrubadub spacy stanza presidio}"
LOCAL_GPU="${LOCAL_GPU:-gliner piiranha flair}"
# languages for the local lane (split per-language for checkpointing). Derived from the split; override with LOCAL_LANGS=...
LOCAL_LANGS="${LOCAL_LANGS:-$("$PYTHON" - "$SPLIT" <<'PY' 2>/dev/null
import sys, gzip, json, collections
split = sys.argv[1]
c = collections.Counter()
with gzip.open(f"src/pii_anon_datasets/splits/{split}.jsonl.gz", "rt", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            c[json.loads(line).get("language", "?")] += 1
print(" ".join(sorted(k for k in c if k != "?")))
PY
)}"
[ -n "$LOCAL_LANGS" ] || LOCAL_LANGS="en de fr es it pt nl sv ru uk ja zh ko ar hi th el bn he tr"

# ---- detector lanes (restart-safe: a finished (detector,language) shard is skipped on re-run) ----
run_one_local() {
  local det="$1"
  local det_dir="$OUT_LOCAL/$det"   # MUST be a separate `local` line: `local a=$1 b=$a` expands $a from the outer scope (empty) — bash gotcha
  mkdir -p "$det_dir"
  if [ -f "$det_dir/baseline_results.json" ]; then echo "  local $det: done (skip)"; return 0; fi
  for lang in $LOCAL_LANGS; do
    local lang_dir="$det_dir/$lang"
    if [ -f "$lang_dir/baseline_results.json" ]; then echo "  local $det/$lang: done (skip)"; continue; fi
    mkdir -p "$lang_dir"; echo "  local $det/$lang: START $(date +%H:%M:%S)"
    if "$PII_ANON" baselines --detectors "$det" --split "$SPLIT" --languages "$lang" "${LIMIT_ARG[@]}" \
         --out "$lang_dir" > "$lang_dir/leaderboard.txt" 2> "$lang_dir/run.log"; then
      echo "  local $det/$lang: DONE $(date +%H:%M:%S)"
    else
      echo "  local $det/$lang: FAILED rc=$? — see $lang_dir/run.log (skipped; run continues)"
    fi
  done
}
run_local() {
  mkdir -p "$OUT_LOCAL"
  ( for d in $LOCAL_CPU; do run_one_local "$d"; done ) & local cpu=$!
  ( for d in $LOCAL_GPU; do run_one_local "$d"; done ) & local gpu=$!     # one transformer at a time per lane
  wait "$cpu" "$gpu" 2>/dev/null
  shopt -s nullglob 2>/dev/null
  # LANGUAGE-combine the per-(detector,language) shards into ONE multilingual leaderboard. The `baselines
  # --merge` path is a SAME-DATASET detector-merger (orchestrator.merge_results) and rejects cross-language
  # shards, so the language union lives in combine_lang_shards.py (pooled micro + by_language per detector).
  local shards=("$OUT_LOCAL"/*/*/baseline_results.json)
  if [ "${#shards[@]}" -gt 0 ]; then
    "$PYTHON" "$SCRIPT_DIR/combine_lang_shards.py" --root "$OUT_LOCAL" --out "$OUT_LOCAL/baseline_results.json"
    echo "  local combined -> $OUT_LOCAL/baseline_results.json (+ leaderboard.md)"
  else
    echo "  WARNING: no local results produced — check $OUT_LOCAL/*/*/run.log" >&2
  fi
}

prov_langs() {  # echo the planned languages for one provider out of $PLAN_JSON
  "$PYTHON" -c 'import json,sys; print(" ".join(json.loads(sys.argv[1]).get(sys.argv[2], [])))' "$PLAN_JSON" "$1"
}
run_one_cloud() {
  local prov="$1" lang="$2" dir="$OUT_CLOUD/$1/$2"
  if [ -f "$dir/baseline_results.json" ]; then echo "  cloud $prov/$lang: done (skip)"; return 0; fi
  mkdir -p "$dir"; echo "  cloud $prov/$lang: START $(date +%H:%M:%S)"
  if "$PII_ANON" baselines --cloud --detectors "$prov" --split "$SPLIT" --languages "$lang" "${LIMIT_ARG[@]}" \
       --out "$dir" > "$dir/leaderboard.txt" 2> "$dir/run.log"; then
    echo "  cloud $prov/$lang: DONE $(date +%H:%M:%S)"
  else
    echo "  cloud $prov/$lang: FAILED rc=$? — see $dir/run.log (other shards preserved)"
  fi
}
run_cloud() {
  mkdir -p "$OUT_CLOUD"
  local pids=""
  for prov in aws gcp azure; do                       # one background loop per provider (separate accounts)
    ( for lang in $(prov_langs "$prov"); do run_one_cloud "$prov" "$lang"; done ) &
    pids="$pids $!"
  done
  [ -n "$pids" ] && wait $pids
}

# ---- PREFLIGHT (always; spends nothing) ----
echo "================================================================================"
echo " run_full_leaderboard — split=$SPLIT  local=$DO_LOCAL  cloud=$DO_CLOUD  Azure cap=\$$MAX_AZURE_USD"
echo "================================================================================"
"$PYTHON" scripts/cloud_cost_preflight.py --split "$SPLIT" --max-azure-usd "$MAX_AZURE_USD"
PLAN_JSON="$("$PYTHON" scripts/cloud_cost_preflight.py --split "$SPLIT" --max-azure-usd "$MAX_AZURE_USD" --format plan)"

if [ "$DRY_RUN" = "1" ]; then
  echo ""
  echo "[dry-run] local -> $OUT_LOCAL ; cloud plan -> $PLAN_JSON ; nothing run, \$0 spent."
  exit 0
fi

# ---- LOCAL LANE ----
if [ "$DO_LOCAL" = "1" ]; then
  echo ""; echo "===== LOCAL LANE: 8 detectors over $SPLIT / $(echo $LOCAL_LANGS | wc -w | tr -d ' ') languages -> $OUT_LOCAL ====="
  run_local
fi

# ---- CLOUD LANE (budget-confirmed) ----
if [ "$DO_CLOUD" = "1" ] && [ "$ASSUME_YES" != "1" ]; then
  printf "\nProceed with the CLOUD run above? It spends REAL money (Azure capped ~\$%s). [y/N] " "$MAX_AZURE_USD"
  read -r reply
  case "$reply" in y|Y|yes|YES) ;; *) echo "cloud run skipped."; DO_CLOUD=0 ;; esac
fi
if [ "$DO_CLOUD" = "1" ]; then
  [ -f "$HOME/.pii-anon-cloud.env" ] && . "$HOME/.pii-anon-cloud.env"   # provider creds (never committed)
  echo ""; echo "===== CLOUD LANE: per (provider, language) shard -> $OUT_CLOUD ====="
  run_cloud
fi

# ---- REPORT: assemble the by-language matrix into the card ----
if [ "$DO_REPORT" != "1" ]; then
  echo ""; echo "===== REPORT skipped (--no-report) — results are in $OUT_LOCAL / $OUT_CLOUD ====="
elif [ -f "$OUT_LOCAL/baseline_results.json" ]; then
  echo ""; echo "===== REPORT: by-language F2 matrix -> BASELINES.md ====="
  "$PYTHON" scripts/sync_cards.py matrix \
    --local "$OUT_LOCAL/baseline_results.json" \
    --cloud-glob "$OUT_CLOUD/*/*/baseline_results.json" \
    --file BASELINES.md --marker LEADERBOARD-MULTILINGUAL
else
  echo "  local merge missing — run the local lane first; skipping card sync."
fi

echo ""
echo "================================================================================"
echo " DONE."
echo "   Local:  $OUT_LOCAL/baseline_results.json   (+ leaderboard.md)"
echo "   Cloud:  $OUT_CLOUD/<provider>/<language>/baseline_results.json"
echo "   Card:   BASELINES.md  (BEGIN/END-LEADERBOARD-MULTILINGUAL block)"
echo "================================================================================"
