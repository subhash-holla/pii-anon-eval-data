# NFR-010 throughput — reference-host runbook (HUMAN-ONLY step)

**Status:** `INSUFFICIENT_EVIDENCE` (permanent until a real 8-core reference host runs this).
**Why human-only:** the agent sandbox is NOT the declared reference host; its CPU/topology/contention are
unrepresentative, so the protocol fixes its verdict at `INSUFFICIENT_EVIDENCE` and the harness refuses to
publish a sandbox number as a pass (NFR-010 protocol §2/§8). This session shipped the *gate* that makes that
refusal structural; it cannot supply the host.

## What shipped this session (closes the code side)
- `scripts/benchmark_throughput.py` gained a `--reference-host "<spec>"` declaration flag and a
  `_canonical_verdict()` gate: **without** the flag the canonical NFR-010b verdict is `INSUFFICIENT_EVIDENCE`
  regardless of measured rec/sec; **with** an operator declaration it becomes `PASS` iff the lightweight regex
  path measures `>= 5000 rec/sec`, else `FAIL`. (test: `tests/test_benchmark_reference_host.py`.)
- `scripts/run_throughput_benchmark.sh` — the one-command runner.

## Exact command for the operator (on the REAL 8-core host)
```bash
# from the eval-data repo root, on the declared reference host:
./scripts/run_throughput_benchmark.sh nfr010-refhost.json \
  --reference-host "8-core x86_64 @ ≥3.0GHz, 32GB RAM, isolated (no co-tenant load), Python 3.10, single NUMA node"
# -> writes nfr010-refhost.json and prints canonical_verdict = PASS | FAIL
```
The agent NEVER passes `--reference-host`; only a human on the declared machine does.

## Declared reference-host spec (pin before running)
| Attribute | Required |
|---|---|
| Cores | 8 physical (not 8 vCPU on a shared host) |
| Clock | ≥ 3.0 GHz base |
| RAM | ≥ 32 GB |
| Isolation | no co-tenant CPU load during the run; pin to one NUMA node |
| Corpus | the committed `pii_anon.jsonl.gz` (575,604 records), English slice, `--sample head` (deterministic) |
| Params | `-n 5000`, `--warmup 200`, `--runs 5` (median) — the frozen `benchmark-plan.md` parameters |
| Floor | NFR-010b: regex lightweight path `≥ 5000 rec/sec`; transformer/LLM detectors exempt |

## What to do with the result
1. Commit the `nfr010-refhost.json` run-record to `05-pass2/NFR-010/`.
2. Copy its `provenance.canonical_verdict` (PASS/FAIL) into `05-pass2/NFR-010/outcome.md`.
3. Re-run `/dev-assist-testing` T6 — a PASS moves NFR-010 from PROVISIONAL → the 13th PASS and removes Caveat 5.

**Do NOT** fabricate this from an agent-env number — `run-record-agent-env.json` stays `INSUFFICIENT_EVIDENCE`.
