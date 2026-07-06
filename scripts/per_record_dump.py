#!/usr/bin/env python3
"""Per-record hit-vector dump — the keystone for paired significance, the enrichment ablation,
detector complementarity, and the per-adversarial-attack table.

The canonical ``pii-anon baselines`` run computes per-record predictions in memory and discards them
(only aggregate ``baseline_results.json`` survives). Paired tests (McNemar/bootstrap), the
enriched-vs-core ablation, and detector-complementarity all need the per-GOLD-SPAN hit/miss of each
detector, aligned across detectors. This tool re-runs the 8 local detectors ONCE over the SAME
canonical slice (``load_dataset(split, language)``) and persists, per detector:

  * ``hits_<det>.parquet``      — one row per gold span: (record_id, gold_idx, hit)  [aligned to gold.parquet]
  * ``predcounts_<det>.parquet``— one row per record:    (record_id, n_pred)         [for slice precision]
  * ``meta_<det>.json``         — recomputed micro P/R/F1/F2 + model_id/deterministic/build_seconds

plus a single shared ``gold.parquet`` (record_id, gold_idx, entity_type, domain, language,
source_type, adversarial_type, sensitivity_class) — one row per gold span, the join key for everything
downstream.

Correctness: matching is strict-v1 — ``(start, end, entity_type)`` equality, with PREDICTED spans
trimmed via the orchestrator's own ``_trim_spans`` (gold is authoritative, never trimmed). Hits are
assigned by greedy multiset consumption within each record, which reproduces the audited scorer's
micro TP exactly (cross-record matches are impossible by construction, so per-record TP sums to the
pooled multiset TP). ``--validate`` recomputes micro F2 from the dump and diffs it against a published
``baseline_results.json`` so a wrong dump cannot pass silently.

Resumable: each detector writes its own files and is skipped if already present, so a multi-hour run
survives interruption (the repo's restart-safe census pattern). Local detectors are deterministic;
``--seed`` is recorded for provenance only.

Usage:
  python scripts/per_record_dump.py --split test --language en \
      --detectors regex,scrubadub,spacy,presidio,gliner,piiranha,stanza,flair \
      --out results/per-record/en-test
  python scripts/per_record_dump.py --split test_adversarial --language all \
      --out results/per-record/adversarial
  python scripts/per_record_dump.py --out results/per-record/en-test --validate results/baselines/tier1-en-all/baseline_results.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from pii_anon_datasets import load_dataset
from pii_anon_datasets.baselines import registry
from pii_anon_datasets.baselines.orchestrator import _trim_spans

# The 8 INDEPENDENT local detectors that make up the Paper-1 leaderboard. The author's own
# pii_anon / pii_anon_swarm are deliberately excluded here (conflict-of-interest; Paper 3).
LOCAL_8 = ["regex", "scrubadub", "spacy", "presidio", "gliner", "piiranha", "stanza", "flair"]


def _f2(tp: int, n_pred: int, n_gold: int) -> tuple[float, float, float, float]:
    precision = tp / n_pred if n_pred else 0.0
    recall = tp / n_gold if n_gold else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    f2 = (5 * precision * recall / (4 * precision + recall)) if (4 * precision + recall) else 0.0
    return precision, recall, f1, f2


def _source_type(rec) -> str:
    p = rec.get("provenance")
    if isinstance(p, str):
        try:
            p = json.loads(p)
        except Exception:
            p = {}
    return str((p or {}).get("source_type") or "unknown")


def _adversarial_type(rec) -> str:
    a = rec.get("adversarial")
    if isinstance(a, str):
        try:
            a = json.loads(a)
        except Exception:
            a = {}
    return str((a or {}).get("type") or "clean")


def build_gold_table(records) -> list[dict]:
    """One row per gold span, in stable (record, annotation) order — the alignment key for hits."""
    rows: list[dict] = []
    for rec in records:
        rid = str(rec["record_id"])
        dom = str(rec.get("domain", "unknown") or "unknown")
        lang = str(rec.get("language", "unknown") or "unknown")
        st = _source_type(rec)
        adv = _adversarial_type(rec)
        anns = rec.get("annotations") or []
        if isinstance(anns, str):
            anns = json.loads(anns)
        for gi, a in enumerate(anns):
            rows.append(
                {
                    "record_id": rid,
                    "gold_idx": gi,
                    "entity_type": str(a["entity_type"]),
                    "domain": dom,
                    "language": lang,
                    "source_type": st,
                    "adversarial_type": adv,
                    "sensitivity_class": str(a.get("sensitivity_class") or "unknown"),
                }
            )
    return rows


def score_detector(adapter, records, *, progress_every: int = 2000, checkpoint_path=None) -> tuple[list[int], list[dict], dict]:
    """Run one adapter over every record; return (hits aligned to gold rows, per-record pred counts, micro).

    With ``checkpoint_path`` set, each record's result is flushed to a JSONL checkpoint as it is computed and
    reloaded on resume — so a kill mid-detector (e.g. a ~40-minute cloud run) never loses scored records and a
    re-run continues where it stopped. The per-record hit computation (greedy multiset strict-v1 match) is
    UNCHANGED; the checkpoint changes only WHEN results are persisted, never how they are computed (so the
    assembled output is bit-identical to the non-checkpointed path).
    """
    name = adapter.name
    t0 = time.monotonic()
    model = adapter.build()
    build_s = time.monotonic() - t0
    total = len(records)
    record_errors = 0

    done: dict = {}   # record_id -> (per-gold-span hits list, n_pred)
    if checkpoint_path is not None and Path(checkpoint_path).exists():
        for line in Path(checkpoint_path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:                                   # a torn final line from a kill is simply skipped + re-scored
                o = json.loads(line)
                done[str(o["record_id"])] = (list(o["hits"]), int(o["n_pred"]))
            except Exception:
                pass
        if done:
            print(f"  [{name}] resumed {len(done)} records from checkpoint", flush=True)

    ckpt = open(checkpoint_path, "a", encoding="utf-8") if checkpoint_path is not None else None
    try:
        for i, rec in enumerate(records):
            rid = str(rec["record_id"])
            if rid in done:
                continue                           # already scored in a prior (killed) run
            text = str(rec.get("text", "") or "")
            try:
                preds = _trim_spans(adapter.detect(text, model), text)
            except Exception:  # one pathological record must not zero out the detector
                preds = []
                record_errors += 1
            pred_keys = Counter((s.start, s.end, s.entity_type) for s in preds)
            anns = rec.get("annotations") or []
            if isinstance(anns, str):
                anns = json.loads(anns)
            rec_hits: list[int] = []
            for a in anns:
                key = (int(a["start"]), int(a["end"]), str(a["entity_type"]))
                if pred_keys.get(key, 0) > 0:
                    pred_keys[key] -= 1
                    rec_hits.append(1)
                else:
                    rec_hits.append(0)
            done[rid] = (rec_hits, len(preds))
            if ckpt is not None:
                ckpt.write(json.dumps({"record_id": rid, "hits": rec_hits, "n_pred": len(preds)}) + "\n")
                ckpt.flush()
            if (i + 1) % progress_every == 0:
                el = time.monotonic() - t0
                rate = (i + 1) / el if el else 0.0
                eta = (total - i - 1) / rate / 60 if rate else 0.0
                print(f"  [{name}] {i+1}/{total} ({100*(i+1)/total:.0f}%)  {rate:.1f} rec/s  ETA {eta:.0f}m", flush=True)
    finally:
        if ckpt is not None:
            ckpt.close()

    # assemble aligned output from `done` in the canonical records order (bit-identical to the inline path)
    hits: list[int] = []
    pred_rows: list[dict] = []
    tp_total = npred_total = ngold_total = 0
    for rec in records:
        rec_hits, npred = done[str(rec["record_id"])]
        hits.extend(rec_hits)
        pred_rows.append({"record_id": str(rec["record_id"]), "n_pred": npred})
        tp_total += sum(rec_hits)
        npred_total += npred
        ngold_total += len(rec_hits)
    precision, recall, f1, f2 = _f2(tp_total, npred_total, ngold_total)
    micro = {
        "model_id": getattr(adapter, "model_id", ""),
        "deterministic": bool(getattr(adapter, "deterministic", True)),
        "build_seconds": round(build_s, 1),
        "wall_seconds": round(time.monotonic() - t0, 1),
        "record_errors": record_errors,
        "n_records": total,
        "n_gold": ngold_total,
        "n_pred": npred_total,
        "n_tp": tp_total,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "f2": f2,
    }
    return hits, pred_rows, micro


def _write_parquet(rows: list[dict], path: Path) -> None:
    # Atomic: write a .tmp sibling then os.replace — so a kill mid-write never leaves a corrupt-but-trusted
    # file that the existence-based resume gates would silently accept.
    tmp = path.with_suffix(path.suffix + ".tmp")
    pq.write_table(pa.Table.from_pylist(rows), tmp)
    os.replace(tmp, path)


def _atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def validate(out: Path, published_path: Path) -> int:
    pub = json.loads(published_path.read_text(encoding="utf-8"))
    det_block = pub.get("detectors", pub)
    print(f"Validating {out} against {published_path.name}")
    worst = 0.0
    for meta_file in sorted(out.glob("meta_*.json")):
        name = meta_file.stem[len("meta_"):]
        mine = json.loads(meta_file.read_text(encoding="utf-8"))
        if mine.get("status") != "scored":          # partial dump (unavailable detector) — skip, don't crash
            print(f"  {name:10s}  (status={mine.get('status')}; skipped)")
            continue
        theirs = (det_block.get(name) or {}).get("micro") or {}
        if not theirs:
            print(f"  {name:10s}  (no published micro to compare)")
            continue
        df2 = abs(mine["f2"] - theirs.get("f2", 0.0))
        dr = abs(mine["recall"] - theirs.get("recall", 0.0))
        worst = max(worst, df2, dr)
        flag = "OK " if max(df2, dr) < 5e-3 else "!! "
        print(
            f"  {flag}{name:10s}  mine f2={mine['f2']:.4f} r={mine['recall']:.4f}  "
            f"pub f2={theirs.get('f2',0):.4f} r={theirs.get('recall',0):.4f}  Δf2={df2:.4f} Δr={dr:.4f}"
        )
    print(f"worst |Δ| = {worst:.4f}  ({'PASS' if worst < 5e-3 else 'CHECK'})")
    return 0 if worst < 5e-3 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", default="test")
    ap.add_argument("--language", default="en", help="BCP-47 code or 'all'")
    ap.add_argument("--detectors", default=",".join(LOCAL_8))
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--seed", type=int, default=20260603, help="recorded for provenance only (local detectors are deterministic)")
    ap.add_argument("--validate", default=None, help="published baseline_results.json to diff micro F2/recall against, then exit")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.validate:
        return validate(out, Path(args.validate))

    language = None if args.language in ("", "all") else args.language
    records = load_dataset(split=args.split, language=language)
    if args.limit:
        records = records[: args.limit]
    print(f"Loaded {len(records)} records (split={args.split} language={args.language})", flush=True)

    # Run manifest: stamp this slice's identity so a resume against the same --out can NEVER silently mix
    # hits from a different record set (cross-run --split/--language/--limit drift → positional misalignment).
    content_hash = hashlib.sha256("\x1e".join(str(r.get("record_id", "")) for r in records).encode()).hexdigest()
    manifest_path = out / "run_manifest.json"
    if manifest_path.exists():
        prev = json.loads(manifest_path.read_text())
        if (prev.get("content_hash"), prev.get("split"), prev.get("language")) != (content_hash, args.split, args.language):
            raise SystemExit(
                f"[abort] {out} was built with a different record set/args "
                f"(prev {prev.get('split')}/{prev.get('language')} n={prev.get('n_records')} vs now "
                f"{args.split}/{args.language} n={len(records)}). Use a fresh --out dir to avoid misaligned hits.")
    else:
        _atomic_write_text(manifest_path, json.dumps(
            {"split": args.split, "language": args.language, "limit": args.limit,
             "n_records": len(records), "content_hash": content_hash}, indent=2))

    gold_path = out / "gold.parquet"
    if not gold_path.exists():
        gold_rows = build_gold_table(records)
        _write_parquet(gold_rows, gold_path)
        print(f"Wrote gold.parquet ({len(gold_rows)} gold spans)", flush=True)

    names = [n.strip() for n in args.detectors.split(",") if n.strip()]
    adapters = {a.name: a for a in registry.resolve(names)}
    for name in names:
        meta_path = out / f"meta_{name}.json"
        # Resume only past a *scored* detector. An 'unavailable' sentinel is re-attempted (the library may
        # have been installed since), so a resume can never permanently lock out a now-available detector.
        if meta_path.exists() and json.loads(meta_path.read_text()).get("status") == "scored":
            print(f"[{name}] already scored — skipping (resumable)", flush=True)
            continue
        adapter = adapters.get(name)
        if adapter is None or not adapter.available():
            print(f"[{name}] unavailable — skipping", flush=True)
            (out / f"meta_{name}.json").write_text(json.dumps({"status": "unavailable"}), encoding="utf-8")
            continue
        ckpt_path = out / f"ckpt_{name}.jsonl"
        print(f"[{name}] scoring {len(records)} records…", flush=True)
        hits, pred_rows, micro = score_detector(adapter, records, checkpoint_path=ckpt_path)
        # align hits to gold rows by writing them in the same (record, gold_idx) order build_gold_table used
        gi_rows = []
        h = 0
        for rec in records:
            rid = str(rec["record_id"])
            anns = rec.get("annotations") or []
            if isinstance(anns, str):
                anns = json.loads(anns)
            for gi in range(len(anns)):
                gi_rows.append({"record_id": rid, "gold_idx": gi, "hit": hits[h]})
                h += 1
        _write_parquet(gi_rows, out / f"hits_{name}.parquet")
        _write_parquet(pred_rows, out / f"predcounts_{name}.parquet")
        _atomic_write_text(meta_path, json.dumps({"status": "scored", **micro}, indent=2))
        ckpt_path.unlink(missing_ok=True)          # detector complete → drop its checkpoint
        print(
            f"[{name}] done: f2={micro['f2']:.4f} recall={micro['recall']:.4f} "
            f"precision={micro['precision']:.4f}  ({micro['wall_seconds']:.0f}s, {micro['record_errors']} errs)",
            flush=True,
        )

    print(f"Dump complete → {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
