# Pass-2 Outcome — NFR-010 · Scorer Throughput + Runtime

**Stage 5 · Wave T5 (Pass-2) · OUTCOME** · 2026-05-31
**Verdict: `INSUFFICIENT_EVIDENCE`** (canonical NFR-010b) — **agent-env INDICATIVE run only.**
**Release impact: NONE — stays SHIP-WITH-CAVEATS.** No T6 re-rule (no *real* reference-host evidence).

> **Why this is INSUFFICIENT_EVIDENCE, not a pass — the honest read.** The harness ran on the **agent
> execution sandbox** (a 10-logical-core Apple-Silicon laptop), which is **not** the declared 8-core
> reference host NFR-010b requires, and not a pinned/isolated CI runner. Per the protocol §2/§8, a
> rec/sec from this host is **INDICATIVE only** and must **not** be published as the threshold result.
> The number below is recorded for information and to prove the harness works — it does **not** flip
> NFR-010 PROVISIONAL → PASS. The real reference-host run is still owed (release-readiness Caveat 5).

What **did** land as real progress: the named deliverable — a seeded, fixture-driven, reproducible
benchmark harness — **now exists in-repo** (`scripts/benchmark_throughput.py`, 17 passing tests). The
release-readiness report flagged that "no throughput harness or rec/sec emitter exists in the codebase";
that gap is now closed. Any consumer can run it on their own 8-core host to produce the canonical number.

---

## 1. What was run (matches the frozen [`benchmark-plan.md`](benchmark-plan.md))

```
python scripts/benchmark_throughput.py -n 5000 --language en --sample head \
    --warmup 200 --chunk-size 256 --runs 3 --spacy-records 500 \
    -o .../05-pass2/NFR-010/run-record-agent-env.json
```

Full machine-readable result: [`run-record-agent-env.json`](run-record-agent-env.json) (schema
`pii-anon-nfr010-runrecord/v1`).

## 2. Host (recorded — NOT the canonical reference host)

| Field | Value |
|---|---|
| CPU / arch | `arm` / `arm64` (Apple Silicon) |
| Logical cores | **10** (the NFR-010b floor is specified "on **8-core**" — core count differs; arch differs) |
| RAM | 32 GiB (34,359,738,368 bytes) |
| OS | Darwin 25.5.0 |
| Python | 3.10.6 |
| `is_reference_host` | **false** (agent sandbox; single-process; not pinned/isolated; shared-tenant jitter possible) |

## 3. Per-run results (protocol §7 — capture)

**Corpus slice:** 5,000 English `head` records; record size 38–1,426 chars (mean 294, p50 200).
**Timing:** warm-up 200; T = 4,800 timed/run; R = 3 runs; chunk 256; nearest-rank(ceil) percentiles.

| Detector class | Floored? | rec/sec (median; min–max) | p50 | p95 | p99 | n_timed |
|---|---|---|---|---|---|---|
| **`regex`** (lightweight path — NFR-010b) | **YES** | **17,507** (17,490–17,539) | 39.8 µs | 147.7 µs | 191.1 µs | 4,800 |
| `spacy_ner` (Presidio+spaCy — NFR-010a) | no | 108 (104–109) | 6.59 ms | 23.72 ms | 35.34 ms | 375 |
| `transformer` | no | **EXEMPT** (NFR-010a — reported, not measured) | — | — | — | — |
| `llm` | no | **EXEMPT** (NFR-010a — reported, not measured) | — | — | — | — |

**Context legs (unfloored):** `score_detection` (eval scorer hot path this repo owns) = **50,317 rec/s**;
`end_to_end` (detect → convert → score) = **11,622 rec/s**.

## 4. Roll-up (protocol §7)

- **Does the lightweight path clear ≥5,000 rec/sec?** On this *non-canonical* host, **yes — ~3.5× the
  floor** (17,507 vs 5,000), with very tight run-to-run variance (±0.3%). This is **encouraging and
  de-risks** the eventual real-host run, but is **not** the canonical measurement.
- **Tail latency:** regex p99 = 191 µs/record — comfortably inside a sub-300 ms runtime-fit budget on
  this host. spaCy-NER p99 = 35 ms/record — two orders of magnitude slower, which is exactly **why
  transformer/LLM detectors are NFR-010a-exempt** and regex is the floored lightweight path.
- **NFR-010c (full-scan):** at 17,507 rec/s a full 575,604-row scan ≈ **32.9 s** single-process; at this
  throughput the whole corpus fits inside a 60 s budget, so no sampling is required *at this rate*. (On a
  slower real host the recommended-sampling row count drops proportionally — the harness recomputes it.)
- **NFR-010a per-class table:** regex measured; spaCy-NER measured (the `[baselines]` extra happened to be
  present in this env); transformer + LLM exempt.

## 5. Honest caveats on the indicative number (do NOT over-read)

1. **Wrong host class.** Apple-Silicon 10-core laptop ≠ declared **8-core** reference host ≠ x86 CI
   runner. Throughput and tail latency are hardware/topology/contention-bound; this figure does not
   transfer.
2. **Minimal regex set.** The measured `regex` class is the in-repo **9-pattern** baseline
   (`regex_baseline.py`: EMAIL/PHONE/SSN/IP/CC/DOB/IBAN/MAC/TIMESTAMP). A production-grade lightweight
   detector carries **far more** patterns; per-record cost grows roughly linearly with pattern count, so
   a fuller detector would post a **lower** rec/sec. 17,507 is an **optimistic** read for "the regex
   class," not a ceiling.
3. **Decompression excluded.** rec/sec is detector *compute* (gzip decompression is setup, not timed);
   an end-to-end streaming pipeline that includes IO will be lower.
4. **Single-process, warm, steady-state.** No concurrency sweep; warm-cache; not the cold-start or
   contended profile.

## 6. Verdict mapping (protocol §8)

| Protocol §8 row | This run |
|---|---|
| "No reference host provisioned in-window → **INSUFFICIENT_EVIDENCE**; the ≥5,000 figure is carried as an **un-validated target**; **T6 → SHIP-WITH-CAVEATS**." | **THIS ROW.** No declared 8-core reference host was provisioned. The agent-env figure is an indicative datapoint, not the canonical measurement. |

**Status:** NFR-010b (+010c) `AGENT_SIMULATED (real_user_needed)` → **INSUFFICIENT_EVIDENCE
(agent-env indicative; real 8-core reference-host run owed).** The ≥5,000 target remains **un-validated**
on canonical hardware; the release-readiness verdict is unchanged at **SHIP-WITH-CAVEATS** (Caveat 5).

## 7. What lands the canonical pass (the still-owed work)

Run the **same frozen protocol** on a declared **8-core reference host** (CI runner of record or a pinned
8-core cloud instance), out-of-band:

```
python scripts/benchmark_throughput.py -n <N> --language en --sample head \
    --warmup 200 --chunk-size 256 --runs 5 -o run-record-ref-host.json
```

Then, per protocol §8: ≥5,000 → **REAL-HOST-VALIDATED** (NFR-010b becomes the 13th PASS); 3,000–4,999 →
**LOOSENED** (republish the floor at the measured number); wide miss / pathological tail → **PIVOT**
(batch-only positioning). Only that run writes the canonical outcome and triggers a T6 re-rule toward
SHIP. **No agent-sandbox number substitutes** (protocol §2 — refused).

---

*Reproducible: `scripts/benchmark_throughput.py` (seeded `SEED_BENCHMARK=20260531`; deterministic
slice/conversion/percentile math, AX-002). Run-record: `run-record-agent-env.json`. Pre-registration:
`benchmark-plan.md`. No number fabricated; no canonical claim made on non-canonical hardware.*
