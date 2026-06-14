#!/usr/bin/env bash
# NFR-010 throughput benchmark — one-command runner (Pass-2 reference-host seam).
#
#   AGENT / UNVERIFIED host:  ./scripts/run_throughput_benchmark.sh out.json
#       -> canonical_verdict = INSUFFICIENT_EVIDENCE (never a fabricated pass).
#
#   REAL 8-core reference host (OPERATOR, out-of-band):
#       ./scripts/run_throughput_benchmark.sh out.json --reference-host "8-core x86_64, 32GB, isolated, no-contention"
#       -> canonical_verdict = PASS iff the lightweight regex path measures >= 5000 rec/sec, else FAIL.
#
# The agent NEVER passes --reference-host; only a human on the declared host does. See
# dev-assist-artifacts/05-testing/05-pass2/NFR-010/ for the host spec + protocol.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PII_ANON_PYTHON:-python}"
OUT="${1:-throughput-run.json}"
shift || true
PYTHONPATH="$HERE/src" "$PY" "$HERE/scripts/benchmark_throughput.py" \
  --input "$HERE/src/pii_anon_datasets/data/pii_anon.jsonl.gz" \
  -n 5000 --language en --sample head --runs 5 -o "$OUT" "$@"
VERDICT="$("$PY" -c "import json; print(json.load(open('$OUT'))['provenance']['canonical_verdict'])")"
echo "NFR-010 run-record -> $OUT"
echo "canonical_verdict   -> $VERDICT"
