#!/usr/bin/env bash
# One-off: full English-test cloud baseline (aws + azure + gcp), run in PARALLEL, one process per
# detector so each provider's spend is protected once it writes its result (restart-safe per detector).
# Auto-merges the three into one F2 leaderboard at the end. The launcher wraps this in
# `nohup caffeinate -i …` so it survives the terminal/session closing and keeps the Mac awake.
# Local helper for the cloud baseline run — not intended for commit.
set +u   # bash 3.2 + empty arrays + nounset don't mix (see commit c123ff7)

ROOT="/Users/subhashholla/Development/pii_anonymize_pseudonymize/pii-anon-core/pii-anon-eval-data"
cd "$ROOT" || exit 1
# shellcheck disable=SC1090
source ~/.pii-anon-cloud.env
mkdir -p results/baselines/cloud-en logs

pids=""
for d in aws azure gcp; do
  if [ -f "results/baselines/cloud-en/$d/baseline_results.json" ]; then
    echo "$(date '+%F %T') $d: result already present — skipping (restart-safe)"
    continue
  fi
  pii-anon baselines --cloud --detectors "$d" --split test --languages en \
    --out "results/baselines/cloud-en/$d" > "logs/cloud-$d.log" 2>&1 &
  pids="$pids $!"
  echo "$(date '+%F %T') launched $d (pid $!) -> logs/cloud-$d.log"
done

if [ -n "$pids" ]; then
  wait $pids
fi
echo "$(date '+%F %T') all detectors finished"

pii-anon baselines --merge results/baselines/cloud-en/*/baseline_results.json \
  --out results/baselines/tier1-en-cloud > logs/cloud-merge.log 2>&1
echo "$(date '+%F %T') merged -> results/baselines/tier1-en-cloud (log: logs/cloud-merge.log)"
