# Pre-Registration — NFR-010 Throughput Benchmark

**Stage 5 · Wave T5 (Pass-2) · pre-registration (protocol §3)** · 2026-05-31
**Frozen BEFORE the timed run.** This document fixes the host-spec capture, corpus slice, warm-up
discard, timed-record count, run count, and percentile method so the result cannot be retrofitted to a
target. The harness is [`scripts/benchmark_throughput.py`](../../../../scripts/benchmark_throughput.py)
(shipped this Pass-2; it did not exist in-repo before).

> **Honesty pre-commitment (protocol §2).** The run that accompanies this pre-registration executes on
> the **agent execution sandbox**, which is **NOT** the declared 8-core reference host NFR-010b requires.
> Therefore the canonical NFR-010b verdict for this run is fixed, in advance, at **INSUFFICIENT_EVIDENCE**
> regardless of the number observed. The measured rec/sec is **INDICATIVE only** — it demonstrates the
> harness works and gives an order-of-magnitude read; it is **not** a threshold result and does **not**
> flip NFR-010 PROVISIONAL → PASS. A real reference-host run lands out-of-band; only then is `outcome.md`
> upgraded past INSUFFICIENT_EVIDENCE.

---

## 1. Measurement question (restated from protocol §3)

On the run host, streaming the lightweight detection path over a fixed English corpus slice with
chunked input, what is the sustained **rec/sec** (vs the ≥5,000 NFR-010b floor) and the **p50/p95/p99**
per-record latency — warm, steady-state, single-process — for each detector class?

## 2. Host (recorded, not chosen)

The harness records the host spec at runtime via stdlib (`platform`, `os.cpu_count()`,
`os.sysconf`): CPU, logical cores, RAM, OS + release, Python version. The host record **always** carries
`is_reference_host: false` and a note that it is the agent sandbox, not the canonical 8-core host. The
spec is part of the result; it is reported, never asserted to be 8-core.

## 3. Corpus slice (frozen)

| Parameter | Frozen value |
|---|---|
| Source | `src/pii_anon_datasets/data/pii_anon.jsonl.gz` (frozen 575,604-record corpus; untouched) |
| Language filter | `en` (English detection substrate; ~26% of corpus, abundant in the head) |
| Sample mode | `head` — the **first N** English records (deterministic; no RNG) |
| N (slice size) | **5,000** English records |
| Seed | `SEED_BENCHMARK = 20260531` (governs `--sample random` only; unused in `head` mode) |

Record-size (char) distribution of the slice is captured in the run-record (NFR-010c needs record-size).

## 4. Timing protocol (frozen)

| Parameter | Frozen value |
|---|---|
| Warm-up discard (W) | **200** records (JIT/cache warm; discarded) |
| Timed records per run (T) | **N − W = 4,800** |
| Runs (R) | **3** — median rec/sec reported; min/max also recorded (run-to-run variance) |
| Chunk size | **256** records (the streaming/chunked-input requirement) |
| Per-record timer | `time.perf_counter_ns()` around each detect/score call |
| Throughput | `rec/sec = n_timed / Σ(per-record compute seconds)` (decompression/IO excluded — setup, not the path) |
| **Percentile method** | **nearest-rank (ceil), NO interpolation** — `rank = ⌈p/100 · n⌉`, value = `sorted[rank−1]` |

## 5. Detector classes (frozen scope — protocol §4, NFR-010a)

| Class | Detector | Floored (≥5,000)? | Notes |
|---|---|---|---|
| `regex` | `baselines/regex_baseline.py:detect_pii_regex` (pure-stdlib `re`) | **YES (NFR-010b)** | the lightweight detection path; full 5,000-record slice |
| `spacy_ner` | Presidio + spaCy (`[baselines]` extra), lazy-guarded | no (NFR-010a) | timed on a **bounded 500-record** sub-slice; honestly `skipped` if the extra/model is absent |
| `transformer` | — | no (NFR-010a) | **exempt**; reported, not measured |
| `llm` | — | no (NFR-010a) | **exempt**; reported, not measured |

Two additional legs are timed for context (both unfloored): **`score_detection`** (the eval scorer hot
path this repo owns) and **`end_to_end`** (detect → convert → score, the full consumer pipeline).

## 6. NFR-010c (frozen)

Full-scan wall-clock is extrapolated from the regex median rec/sec over the canonical 575,604-record
corpus, with a "recommend sampling above N rows" figure derived against a 60-second budget. Reported as
an estimate, labelled as such.

## 7. Exact invocation (frozen)

```
python scripts/benchmark_throughput.py \
    -n 5000 --language en --sample head \
    --warmup 200 --chunk-size 256 --runs 3 --spacy-records 500 \
    -o dev-assist-artifacts/05-testing/05-pass2/NFR-010/run-record-agent-env.json
```

## 8. Verdict pre-commitment (protocol §8)

- **This (agent-sandbox) run → INSUFFICIENT_EVIDENCE** for canonical NFR-010b — fixed in advance. The
  indicative number is recorded and compared to the ≥5,000 target for information only; **T6 stays
  SHIP-WITH-CAVEATS**; no T6 re-rule is triggered (no *real* evidence landed).
- A future run on a declared 8-core reference host, using this same frozen protocol, maps per protocol
  §8 (≥5,000 → REAL-HOST-VALIDATED; 3,000–4,999 → LOOSENED; wide miss → PIVOT). Only that run writes the
  canonical outcome.
