# Pass-2 Protocol — NFR-010 · Scorer Throughput + Runtime (real-host measurement)

**Stage 5 · Wave T5 (Pass-2 coordination)** · 2026-05-31 · `pass2_required: false` (OPTIONAL; T6 → **SHIP-WITH-CAVEATS** for the NFR-010b throughput row if un-Pass-2'd, not DEFER).

**Pass-2 working files:** [`benchmark-plan.md`](benchmark-plan.md) · [`outcome.md`](outcome.md) · [`run-record-agent-env.json`](run-record-agent-env.json) — harness shipped (`scripts/benchmark_throughput.py`) + agent-env **INDICATIVE** run (canonical verdict **INSUFFICIENT_EVIDENCE**; real 8-core reference-host run still owed; release stays SHIP-WITH-CAVEATS).

> **NO agent-simulated measurement substitutes for this protocol.** NFR-010b is flagged `real_user_needed: true` — *"Pass-2 the number."* The agent execution environment is **not** the CI/reference host: any rec/sec or p50/p95/p99 figure produced inside the agent sandbox is unrepresentative hardware and would be a fabricated performance claim if published as the threshold result. This protocol specifies a **real-hardware** benchmark on a declared 8-core host; the numbers land out-of-band. Substituting a sandbox/agent-estimated throughput for the real-host run is REFUSED.

---

## 1. Item under validation

| Field | Value |
|---|---|
| **Item** | NFR-010 — Scorer throughput + runtime dimension (R10 → PERSONA-STRATIFIED; split a/b/c) |
| **Source stage** | Requirements `non-functional-requirements.md` (N4; concept-value study) |
| **Binding sub-row** | **NFR-010b (runtime path):** lightweight detection path **≥5,000 rec/sec on 8-core** AND report **p50/p95/p99** per-record latency + streaming/chunked input. (`real_user_needed: true` — Pass-2 the number.) |
| **Also Pass-2** | **NFR-010c (batch):** document warehouse-scale full-scan wall-clock + record-size; recommend sampling above a stated row count. |
| **Not gated** | NFR-010a (no gate): per-detector-class rec/sec reporting; transformer/LLM detectors **exempt from any throughput floor**. |
| **Hot path under test** | the lightweight detection path — `src/pii_anon_datasets/scoring/detection.py` (+ `scoring/core.py`, `scoring/signals.py`); regex / spaCy-NER class only (NFR-010a exempts transformer/LLM). |
| **Threshold under question** | Does the regex / lightweight-NER detection path actually sustain **≥5,000 rec/sec on a real 8-core host**, and what are the real p50/p95/p99 latencies under streaming/chunked input? |
| **Downstream impact** | The runtime-gateway privacy-engineer persona (P-priv-eng, runtime sub-type) named "inference latency/throughput + streaming/chunked input" as N4 — "accuracy-only is half the picture for sub-300ms runtime fit." Without a real-host number, the ≥5,000 rec/sec claim is unverified and the runtime-fit value prop is a documentation promise. This is a pure real-hardware-measurement gap, not a user-preference question. |

## 2. Why a real HOST is needed (no agent-sandbox substitute)

- Throughput and tail latency are **hardware- and contention-bound**. The agent sandbox has unknown/variable CPU, no pinned 8-core topology, and shared-tenant jitter — a rec/sec figure there is not the NFR-010b threshold and must not be reported as one.
- NFR-010b is explicitly tagged `real_user_needed: true` / "Pass-2 the number" in the requirement; the methodology already reserves this measurement for a real host.
- This is a **measurement protocol on a declared reference host**, not a human cohort. The "sample" is records pushed through the detector on real hardware; the "recruitment" is provisioning the reference host.

## 3. Measurement question (pre-registered)

> **MQ:** On a declared **8-core reference host** (CPU model, core count, clock, RAM, OS, Python version all recorded), running the lightweight detection path (regex / spaCy-NER class) over a fixed corpus sample with streaming/chunked input, what is the sustained **rec/sec** (≥5,000 floor?) and the **p50 / p95 / p99** per-record latency — warm, steady-state, single-process and at the documented concurrency?

Pre-register the host spec, the corpus sample, the warm-up discard, the number of timed records, and the percentile method **before** the run. Freeze as `pass2/NFR-010/benchmark-plan.md`.

## 4. Data source + host (the "sample")

- **Corpus sample (real, in-repo):** stream from `src/pii_anon_datasets/data/pii_anon.jsonl.gz` (the frozen 575,604-record corpus). Use a fixed, pre-registered slice (e.g. the first N records of the English detection substrate) so the run is reproducible and the record-size distribution is the real one. Record the byte/char size distribution (NFR-010c needs record-size).
- **Reference host (declared 8-core):** a real CI host or a provisioned 8-core cloud instance. **Record the full spec** (the threshold is "on 8-core" — the host spec is part of the result). The agent env explicitly does NOT qualify.
- **Detector under test:** the lightweight class only (regex + spaCy-NER). Per NFR-010a, transformer/LLM detectors are run for **reporting** (per-class rec/sec) but are **exempt** from the ≥5,000 floor — do not let an LLM detector's rec/sec contaminate the NFR-010b verdict.

## 5. Acquisition / provisioning channel

- Provision the declared 8-core reference host (CI runner of record, or a pinned cloud instance type). No human recruitment.
- Ship the benchmark harness with the repo so the run is **reproducible by any consumer on their own host** (the persona wants to re-run on their hardware): a `scripts/benchmark_throughput.py` (or pytest-benchmark target) that (a) streams the pre-registered corpus slice through `detection.py`, (b) discards warm-up, (c) times steady-state, (d) emits rec/sec per detector-class + p50/p95/p99 + host spec into a run-record. (Harness authoring is part of this Pass-2 deliverable — no such harness exists in-repo yet; only sprint-review `performance-benchmark.yaml` reviewer outputs.)

## 6. Run structure (steady-state benchmark sequence)

1. **Pin host**, record spec; **warm up** (discard first W records / JIT/cache warm).
2. **Stream** the pre-registered corpus slice through the lightweight detector, **chunked** (the streaming/chunked-input requirement), single-process baseline.
3. **Time** T steady-state records; compute sustained rec/sec and per-record p50/p95/p99.
4. **Repeat** R runs; report median rec/sec + the tail percentiles + run-to-run variance.
5. **NFR-010c:** extrapolate / measure a warehouse-scale full-scan wall-clock at the real record-size; derive the "recommend sampling above N rows" threshold.
6. **NFR-010a:** emit per-detector-class rec/sec for every class (regex / spaCy-NER / transformer / LLM) into the run-record (transformer/LLM reported, not floored).

## 7. Outcome capture

**Per-run:** host spec (CPU/cores/clock/RAM/OS/Python); detector class; sustained rec/sec; p50/p95/p99 (µs/ms per record); chunk size; warm-up discard; T timed; R runs + variance; record-size distribution.

**Roll-up:** does the lightweight path clear **≥5,000 rec/sec on 8-core**? the real tail-latency profile; the NFR-010c full-scan wall-clock + recommended sampling row count; per-class rec/sec table (NFR-010a).

## 8. Verdict mapping

| Outcome | Verdict | Status transition |
|---|---|---|
| Lightweight path ≥5,000 rec/sec on the declared 8-core host; p50/p95/p99 recorded; streaming/chunked demonstrated | **REAL-HOST-VALIDATED** (real-data-validated) | NFR-010b: AGENT_SIMULATED → **MEASURED (real host)**; the ≥5,000 claim is substantiated with the host spec. |
| ≥5,000 on a *higher*-core host but not 8-core | **PERSONA-STRATIFIED / TIGHTENED** | restate the floor against the host where it holds; document the 8-core gap honestly. |
| Sustains, say, 3,000–4,999 rec/sec on 8-core | **LOOSENED** | revise the published floor to the measured real number (e.g. "≥N rec/sec on 8-core") — never keep an unmet 5,000 claim. |
| Misses the floor by a wide margin / pathological tail latency | **PIVOT** | the runtime-fit value prop is withdrawn or rescoped (batch-only positioning per NFR-010c); the gateway persona's runtime claim is not made. |
| No reference host provisioned in-window | **INSUFFICIENT_EVIDENCE** | NFR-010b stays unmeasured; the ≥5,000 figure is carried as an **un-validated target**; **T6 → SHIP-WITH-CAVEATS**. |

**Status Change Log entry to write on outcome:**
`| <date> | NFR-010b (+010c) | AGENT_SIMULATED (real_user_needed) | <verdict> | Pass-2 real-host benchmark: <rec/sec> rec/sec on <host spec>, p50/p95/p99=<...>; evidence .../05-pass2/NFR-010/outcome.md |`
