#!/usr/bin/env python3
"""
NFR-010 scorer-throughput + runtime benchmark harness (Pass-2 deliverable).

Measures the **lightweight detection path** throughput the runtime-gateway privacy-engineer
persona named as N4 ("inference latency/throughput + streaming/chunked input"). Reports, per
detector class, sustained **rec/sec** + per-record **p50/p95/p99** latency, plus the eval
**scorer** hot path this repo owns (``score_detection``), an end-to-end leg, and an NFR-010c
warehouse full-scan extrapolation.

WHAT THIS HARNESS IS (and is NOT) — NFR-010 protocol §2, LOAD-BEARING honesty:
  * It is a reproducible benchmark any consumer can run on THEIR OWN 8-core reference host.
  * The number it produces *here* (agent execution sandbox) is INDICATIVE ONLY. The agent host
    is NOT the declared 8-core reference host; its CPU/topology/contention are unrepresentative.
    Therefore the canonical NFR-010b verdict this harness stamps on its own run is
    ``INSUFFICIENT_EVIDENCE`` — never a pass — until a real reference-host run lands out-of-band.
    Publishing a sandbox rec/sec as the threshold result would be a fabricated performance claim.

Measured classes (NFR-010a):
  * ``regex``       — the in-repo lightweight detector (``baselines/regex_baseline.py``); pure-stdlib
                      ``re``; this is the class the ≥5,000 rec/sec floor (NFR-010b) applies to.
  * ``spacy_ner``   — Presidio + spaCy (the ``[baselines]`` extra); measured IF installed, else honestly
                      SKIPPED. Behind a lazy guard so importing this module never needs spaCy (NFR-004).
  * ``transformer`` / ``llm`` — reported but EXEMPT from the throughput floor (NFR-010a).

Determinism (AX-002): slice selection, span conversion, and percentile math are byte-reproducible
under ``SEED_BENCHMARK``; only the wall-clock timings vary run-to-run (they are the measurement).

Usage:
    python scripts/benchmark_throughput.py                       # head slice, JSON to stdout
    python scripts/benchmark_throughput.py -n 5000 --runs 5      # 5 runs over first 5k English recs
    python scripts/benchmark_throughput.py --sample random --seed 20260531 -o run.json
"""
from __future__ import annotations

import argparse
import gzip
import itertools
import json
import math
import os
import platform
import random
import sys
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Repo root (for the `baselines` namespace package) + src (for `pii_anon_datasets`).
_REPO_ROOT = Path(__file__).resolve().parent.parent
for _p in (str(_REPO_ROOT), str(_REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Pure-stdlib in-repo lightweight detector (regex class) + the eval scorer hot path.
from baselines.regex_baseline import detect_pii_regex  # noqa: E402
from pii_anon_datasets.scoring.core import Span as CoreSpan  # noqa: E402
from pii_anon_datasets.scoring.detection import score_detection  # noqa: E402

# Distinct from the corpus-generation seeds core(42)/v120(162)/v130(172)/coverage(4242)/lattice(91237).
SEED_BENCHMARK = 20260531

RUNRECORD_SCHEMA = "pii-anon-nfr010-runrecord/v1"
HARNESS_VERSION = "1.0.0"
NFR_010B_FLOOR = 5000          # rec/sec, lightweight detection path on an 8-core reference host
CANONICAL_RECORDS = 782677     # full corpus (v2.2.0), for the NFR-010c full-scan extrapolation

DEFAULT_CORPUS = _REPO_ROOT / "src" / "pii_anon_datasets" / "data" / "pii_anon.jsonl.gz"


# ----------------------------------------------------------------------------- streaming I/O
def iter_corpus(path: Path | str, language: str | None = None) -> Iterator[dict]:
    """Stream records from a (gzipped or plain) JSONL corpus, optionally filtering by language.

    Generator — never materializes the whole corpus (the streaming-input requirement).
    """
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if language and rec.get("language") != language:
                continue
            yield rec


def reservoir_sample(iterable: Iterator[Any], k: int, rng: random.Random) -> list:
    """Algorithm-R reservoir sample of size ``k`` — single streaming pass, fully seeded (AX-002)."""
    res: list = []
    for i, item in enumerate(iterable):
        if i < k:
            res.append(item)
        else:
            j = rng.randint(0, i)
            if j < k:
                res[j] = item
    return res


def select_slice(path: Path | str, n: int, language: str | None = "en",
                 sample: str = "head", seed: int = SEED_BENCHMARK) -> list[dict]:
    """Pre-registered corpus slice. ``head`` = deterministic first-N (default);
    ``random`` = seeded reservoir sample (reproducible under the same seed)."""
    if sample == "head":
        return list(itertools.islice(iter_corpus(path, language), n))
    if sample == "random":
        return reservoir_sample(iter_corpus(path, language), n, random.Random(seed))
    raise ValueError(f"unknown sample mode: {sample!r} (use 'head' or 'random')")


# ----------------------------------------------------------------------------- span conversion
def gold_core_spans(record: Mapping[str, Any]) -> list[CoreSpan]:
    """Gold annotations (dicts) -> canonical 3-field ``scoring.core.Span``; skip malformed offsets."""
    out: list[CoreSpan] = []
    anns = record.get("annotations") or []
    for a in anns:
        if not isinstance(a, Mapping):
            continue
        if "start" not in a or "end" not in a or "entity_type" not in a:
            continue
        try:
            out.append(CoreSpan(int(a["start"]), int(a["end"]), str(a["entity_type"])))
        except (ValueError, TypeError):
            continue  # core.Span rejects end<start / negative — skip rather than fabricate
    return out


def pred_core_spans(spans: Sequence[Any]) -> list[CoreSpan]:
    """Detector spans (``baselines.evaluate.Span``, 4-field) -> canonical 3-field core.Span."""
    out: list[CoreSpan] = []
    for s in spans:
        try:
            out.append(CoreSpan(int(s.start), int(s.end), str(s.entity_type)))
        except (ValueError, TypeError, AttributeError):
            continue
    return out


def detect_regex(text: str) -> list:
    """The in-repo lightweight regex detector (single source of truth: regex_baseline)."""
    return detect_pii_regex(text)


# ----------------------------------------------------------------------------- math helpers
def percentiles(samples: Sequence[float], ps: Sequence[int] = (50, 95, 99)) -> dict:
    """Nearest-rank percentiles (ceil; no interpolation) — deterministic, method pre-registered."""
    if not samples:
        return {p: 0.0 for p in ps}
    s = sorted(samples)
    n = len(s)
    out = {}
    for p in ps:
        rank = max(1, min(math.ceil(p / 100.0 * n), n))
        out[p] = s[rank - 1]
    return out


def _median(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    m = len(s) // 2
    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2.0


def _chunks(seq: Sequence[Any], size: int) -> Iterator[Sequence[Any]]:
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def _human_time(seconds: float) -> str:
    if seconds == float("inf"):
        return "inf"
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m{sec:02d}s"
    if m:
        return f"{m}m{sec:02d}s"
    return f"{seconds:.3f}s"


# ----------------------------------------------------------------------------- timing core
def time_stage(items: Sequence[Any], fn: Callable[[Any], Any], *,
               warmup: int, chunk_size: int) -> dict:
    """Warm up (discard ``warmup`` items), then time the rest one-by-one, iterated in chunks.

    rec/sec is computed from the summed per-record compute time (decompression/IO excluded — it is
    setup, not the detection path). Latency percentiles come from the same per-record measurements.
    """
    items = list(items)
    n_total = len(items)
    warmup = max(0, min(warmup, n_total))
    for it in items[:warmup]:
        fn(it)
    timed = items[warmup:]
    latencies_us: list[float] = []
    for chunk in _chunks(timed, max(1, chunk_size)):
        for it in chunk:
            t0 = time.perf_counter_ns()
            fn(it)
            t1 = time.perf_counter_ns()
            latencies_us.append((t1 - t0) / 1000.0)
    n_timed = len(latencies_us)
    total_seconds = sum(latencies_us) / 1e6
    rec_per_sec = n_timed / total_seconds if total_seconds > 0 else 0.0
    pct = percentiles(latencies_us, (50, 95, 99))
    return {
        "n_total": n_total,
        "n_timed": n_timed,
        "warmup": warmup,
        "chunk_size": chunk_size,
        "total_seconds": total_seconds,
        "rec_per_sec": rec_per_sec,
        "latency_us": {
            "p50": pct[50], "p95": pct[95], "p99": pct[99],
            "mean": (sum(latencies_us) / n_timed) if n_timed else 0.0,
        },
    }


def _aggregate_runs(name: str, runs_out: list[dict], *, floored: bool) -> dict:
    rps = sorted(s["rec_per_sec"] for s in runs_out)
    median_rps = _median(rps)
    rep = min(runs_out, key=lambda s: abs(s["rec_per_sec"] - median_rps))
    return {
        "class": name,
        "status": "measured",
        "floored": floored,
        "runs": len(runs_out),
        "rec_per_sec": {"median": median_rps, "min": rps[0], "max": rps[-1]},
        "latency_us": rep["latency_us"],
        "n_timed": rep["n_timed"],
    }


def run_detector_class(name: str, records: Sequence[dict], detect_fn: Callable[[str], Any], *,
                       warmup: int, chunk_size: int, runs: int, floored: bool) -> dict:
    runs_out = [time_stage(records, lambda r: detect_fn(r["text"]),
                           warmup=warmup, chunk_size=chunk_size) for _ in range(runs)]
    return _aggregate_runs(name, runs_out, floored=floored)


def _spacy_ner_detector() -> Callable[[str], Any]:
    """Lazily build a Presidio (spaCy-NER) detector, or raise a clear ``[baselines]`` install error.

    Behind a function so importing this module never imports presidio/spaCy (NFR-004 / NFR-009 pattern).
    """
    try:
        from presidio_analyzer import AnalyzerEngine  # type: ignore[import-not-found]
    except ImportError as e:
        raise RuntimeError(
            "spaCy-NER class needs the 'baselines' extra: pip install pii-anon-datasets[baselines] "
            "&& python -m spacy download en_core_web_lg"
        ) from e
    from baselines.presidio_baseline import detect_pii_presidio
    analyzer = AnalyzerEngine()
    return lambda text: detect_pii_presidio(text, analyzer)


def run_spacy_ner_class(records: Sequence[dict], *, warmup: int, chunk_size: int, runs: int) -> dict:
    try:
        detect = _spacy_ner_detector()
    except Exception as e:  # ImportError->RuntimeError, or model-missing at AnalyzerEngine()
        return {"class": "spacy_ner", "status": "skipped", "floored": False, "reason": str(e)}
    return run_detector_class("spacy_ner", records, detect,
                              warmup=warmup, chunk_size=chunk_size, runs=runs, floored=False)


def _exempt_class(name: str) -> dict:
    return {
        "class": name, "status": "exempt", "floored": False,
        "reason": "NFR-010a exempts transformer/LLM detectors from the throughput floor "
                  "(reported for completeness, not measured here).",
    }


def run_score_leg(records: Sequence[dict], *, warmup: int, chunk_size: int, runs: int) -> dict:
    """Throughput of ``score_detection`` (the eval hot path THIS repo owns). Gold + regex predictions
    are pre-extracted (setup, not timed); only the scorer call is timed."""
    prepped = [(gold_core_spans(r), pred_core_spans(detect_regex(r["text"]))) for r in records]

    def _score(item):
        gold, pred = item
        return score_detection(gold, pred)

    runs_out = [time_stage(prepped, _score, warmup=warmup, chunk_size=chunk_size) for _ in range(runs)]
    agg = _aggregate_runs("score_detection", runs_out, floored=False)
    agg["status"] = "measured"
    return agg


def run_end_to_end_leg(records: Sequence[dict], *, warmup: int, chunk_size: int, runs: int) -> dict:
    """Full consumer pipeline per record: detect (regex) -> convert -> score_detection."""
    def _pipe(r):
        return score_detection(gold_core_spans(r), pred_core_spans(detect_regex(r["text"])))

    runs_out = [time_stage(records, _pipe, warmup=warmup, chunk_size=chunk_size) for _ in range(runs)]
    agg = _aggregate_runs("end_to_end", runs_out, floored=False)
    agg["status"] = "measured"
    return agg


# ----------------------------------------------------------------------------- host + extrapolation
def host_spec() -> dict:
    """Best-effort host description (stdlib only). ALWAYS flags is_reference_host=False (protocol §2)."""
    ram_bytes = None
    try:
        ram_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")  # POSIX (macOS/Linux)
    except (ValueError, AttributeError, OSError):
        ram_bytes = None
    return {
        "cpu": platform.processor() or platform.machine() or "unknown",
        "machine": platform.machine(),
        "cores_logical": os.cpu_count(),
        "ram_bytes": ram_bytes,
        "os": platform.system(),
        "os_release": platform.release(),
        "python_version": platform.python_version(),
        "is_reference_host": False,
        "note": "Agent execution sandbox — NOT the declared 8-core reference host required by "
                "NFR-010b. Figures are INDICATIVE only; not a canonical threshold result (protocol §2).",
    }


def full_scan_estimate(rec_per_sec: float, total_records: int = CANONICAL_RECORDS,
                       budget_seconds: float = 60.0) -> dict:
    """NFR-010c: warehouse-scale full-scan wall-clock + a 'sample above N rows' recommendation."""
    wall = (total_records / rec_per_sec) if rec_per_sec > 0 else float("inf")
    rows_in_budget = int(rec_per_sec * budget_seconds)
    return {
        "total_records": total_records,
        "rec_per_sec": rec_per_sec,
        "wall_clock_seconds": wall,
        "wall_clock_human": _human_time(wall),
        "budget_seconds": budget_seconds,
        "recommended_sampling_rows": min(rows_in_budget, total_records),
        "note": f"At {rec_per_sec:.0f} rec/sec a full {total_records:,}-row scan ≈ {_human_time(wall)}; "
                f"above ~{min(rows_in_budget, total_records):,} rows, sample to stay within "
                f"{budget_seconds:.0f}s.",
    }


def _record_size_chars(records: Sequence[dict]) -> dict:
    sizes = [len(r.get("text", "") or "") for r in records]
    if not sizes:
        return {"min": 0, "max": 0, "mean": 0.0, "p50": 0}
    return {"min": min(sizes), "max": max(sizes),
            "mean": sum(sizes) / len(sizes), "p50": percentiles(sizes, (50,))[50]}


# ----------------------------------------------------------------------------- canonical verdict
def _canonical_verdict(reference_host: str | None, regex_rps: float, floor: int = NFR_010B_FLOOR) -> dict:
    """The canonical NFR-010b verdict block. Without an OPERATOR-declared 8-core reference host (the agent
    sandbox / any unverified machine), the verdict is INSUFFICIENT_EVIDENCE — NEVER a pass, regardless of the
    measured rec/sec (NFR-010 protocol §2/§8). Only an explicit ``--reference-host`` declaration on the real
    host lets the floor verdict (PASS iff ``regex_rps >= floor`` else FAIL) stand. This is the never-fabricate
    seam: an agent-env run cannot publish a pass."""
    if not reference_host or not str(reference_host).strip():
        return {
            "is_reference_host": False,
            "environment": "agent-execution-sandbox",
            "canonical_verdict": "INSUFFICIENT_EVIDENCE",
            "reason": "The host is not a declared 8-core reference host (NFR-010 protocol §2/§8). The measured "
                      "rec/sec is INDICATIVE; the canonical NFR-010b verdict stays INSUFFICIENT_EVIDENCE until a "
                      "real reference-host run lands (pass --reference-host on the declared host). Release stays "
                      "SHIP-WITH-CAVEATS.",
        }
    spec = str(reference_host).strip()
    meets = regex_rps >= floor
    return {
        "is_reference_host": True,
        "environment": spec,
        "canonical_verdict": "PASS" if meets else "FAIL",
        "reason": f"Operator-declared reference host: {spec!r}. Lightweight regex path measured "
                  f"{regex_rps:,.0f} rec/sec vs the NFR-010b floor {floor:,}/sec → {'PASS' if meets else 'FAIL'}.",
    }


# ----------------------------------------------------------------------------- run-record assembly
def build_run_record(*, corpus_path: Path | str, n: int, language: str | None, sample: str,
                     seed: int, warmup: int, chunk_size: int, runs: int,
                     spacy_records: int = 500, timestamp: str | None = None,
                     reference_host: str | None = None) -> dict:
    """Run the full benchmark and assemble the JSON run-record. ``timestamp`` is injected for
    test reproducibility; defaults to now (UTC). The floored regex path uses the full slice; the
    heavy spaCy-NER class times only the first ``spacy_records`` records (kept tractable on any host)."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records = select_slice(corpus_path, n, language=language, sample=sample, seed=seed)

    regex_cls = run_detector_class("regex", records, detect_regex,
                                   warmup=warmup, chunk_size=chunk_size, runs=runs, floored=True)
    spacy_cls = run_spacy_ner_class(records[:spacy_records],
                                    warmup=min(warmup, max(0, spacy_records // 4)),
                                    chunk_size=chunk_size, runs=runs)
    detector_classes = [regex_cls, spacy_cls, _exempt_class("transformer"), _exempt_class("llm")]

    score_leg = run_score_leg(records, warmup=warmup, chunk_size=chunk_size, runs=runs)
    e2e_leg = run_end_to_end_leg(records, warmup=warmup, chunk_size=chunk_size, runs=runs)

    regex_rps = regex_cls["rec_per_sec"]["median"]
    nfr_010c = full_scan_estimate(regex_rps)

    nfr_010a = {
        c["class"]: (
            {"status": c["status"], "rec_per_sec_median": c["rec_per_sec"]["median"]}
            if c["status"] == "measured" else {"status": c["status"]}
        )
        for c in detector_classes
    }

    return {
        "schema": RUNRECORD_SCHEMA,
        "harness_version": HARNESS_VERSION,
        "timestamp": timestamp,
        "seed": seed,
        "host": host_spec(),
        "corpus": {
            "path": str(corpus_path),
            "n_requested": n,
            "n_selected": len(records),
            "language": language,
            "sample": sample,
            "record_size_chars": _record_size_chars(records),
        },
        "params": {"warmup": warmup, "chunk_size": chunk_size, "runs": runs,
                   "percentile_method": "nearest-rank(ceil), no interpolation"},
        "detector_classes": detector_classes,
        "score_leg": score_leg,
        "end_to_end_leg": e2e_leg,
        "nfr_010a": nfr_010a,
        "nfr_010b": {
            "target_rec_per_sec": NFR_010B_FLOOR,
            "detector_class": "regex",
            "measured_rec_per_sec": regex_rps,
            "meets_target": regex_rps >= NFR_010B_FLOOR,
            "note": "Indicative only — see provenance.canonical_verdict.",
        },
        "nfr_010c": nfr_010c,
        "provenance": _canonical_verdict(reference_host, regex_rps),
    }


# ----------------------------------------------------------------------------- CLI
def _fmt_class(c: dict) -> str:
    if c["status"] == "measured":
        r = c["rec_per_sec"]
        lat = c["latency_us"]
        return (f"  {c['class']:<12} {r['median']:>12,.0f} rec/s  "
                f"(min {r['min']:,.0f} / max {r['max']:,.0f})  "
                f"p50={lat['p50']:.1f}µs p95={lat['p95']:.1f}µs p99={lat['p99']:.1f}µs"
                f"{'   [≥5000 floor]' if c['floored'] else ''}")
    return f"  {c['class']:<12} {c['status'].upper():>12}  ({c.get('reason', '')[:60]})"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="NFR-010 throughput + runtime benchmark (Pass-2).")
    ap.add_argument("--input", type=Path, default=DEFAULT_CORPUS, help="Corpus JSONL(.gz).")
    ap.add_argument("-n", "--records", type=int, default=5000, help="Slice size (default 5000).")
    ap.add_argument("--language", default="en", help="Language filter (default en; '' for all).")
    ap.add_argument("--sample", choices=("head", "random"), default="head",
                    help="head=first-N (deterministic); random=seeded reservoir.")
    ap.add_argument("--seed", type=int, default=SEED_BENCHMARK, help="Seed for --sample random.")
    ap.add_argument("--warmup", type=int, default=200, help="Warm-up records to discard.")
    ap.add_argument("--chunk-size", type=int, default=256, help="Chunk size (streaming/chunked input).")
    ap.add_argument("--runs", type=int, default=3, help="Timed runs; median reported.")
    ap.add_argument("--spacy-records", type=int, default=500,
                    help="Bound the (heavy) spaCy-NER sub-slice (default 500); regex uses the full slice.")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Write JSON run-record here.")
    ap.add_argument("--reference-host", default=None,
                    help="OPERATOR ONLY: declare THIS machine is the 8-core reference host (pass the exact "
                         "spec). Omit on the agent sandbox / any unverified host -> verdict stays "
                         "INSUFFICIENT_EVIDENCE (never a fabricated pass).")
    args = ap.parse_args(argv)

    rr = build_run_record(
        corpus_path=args.input, n=args.records, language=(args.language or None),
        sample=args.sample, seed=args.seed, warmup=args.warmup,
        chunk_size=args.chunk_size, runs=args.runs, spacy_records=args.spacy_records,
        reference_host=args.reference_host,
    )

    text = json.dumps(rr, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")

    # Human summary (stderr-style banner first so it's never confused with the JSON payload).
    h = rr["host"]
    b = rr["nfr_010b"]
    print("=" * 78)
    print("NFR-010 throughput benchmark — INDICATIVE (agent sandbox, NOT the 8-core ref host)")
    print(f"  host: {h['cpu']} | {h['cores_logical']} logical cores | "
          f"{h['os']} {h['os_release']} | py{h['python_version']}")
    print(f"  slice: {rr['corpus']['n_selected']:,} {rr['corpus']['language']} records "
          f"(sample={rr['corpus']['sample']}, runs={rr['params']['runs']}, "
          f"warmup={rr['params']['warmup']}, chunk={rr['params']['chunk_size']})")
    print("-" * 78)
    print("Detector classes (NFR-010a; ≥5000 rec/s floor applies to regex only — NFR-010b):")
    for c in rr["detector_classes"]:
        print(_fmt_class(c))
    print(f"  {'score_detection':<12} {rr['score_leg']['rec_per_sec']['median']:>12,.0f} rec/s  "
          f"(eval scorer hot path)")
    print(f"  {'end_to_end':<12} {rr['end_to_end_leg']['rec_per_sec']['median']:>12,.0f} rec/s  "
          f"(detect+convert+score)")
    print("-" * 78)
    print(f"NFR-010b: regex {b['measured_rec_per_sec']:,.0f} rec/s vs ≥{b['target_rec_per_sec']:,} "
          f"target → meets_target={b['meets_target']} (INDICATIVE)")
    print(f"NFR-010c: {rr['nfr_010c']['note']}")
    print(f"CANONICAL VERDICT: {rr['provenance']['canonical_verdict']} — {rr['provenance']['reason']}")
    print("=" * 78)
    if args.output:
        print(f"run-record → {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
