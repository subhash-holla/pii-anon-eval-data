#!/usr/bin/env python3
"""Combine per-(detector,language) local shards into ONE multilingual baseline_results.json.

The local lane is checkpointed per (detector,language) — one single-language run per shard. Those shards
differ on (language, n_records), so orchestrator.merge_results (a same-dataset DETECTOR-merger) refuses to
combine them. This LANGUAGE-combine instead unions each detector's per-language shards: pooled micro
(sum tp/fp/fn across languages), by_language = {lang: that shard's score}, by_entity_type pooled per type.

Downstream (sync_cards matrix, multilingual_by_script_lb) reads detectors[].by_language[lang].counts / .f2,
which this preserves. Deterministic + idempotent.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pii_anon_datasets.baselines.orchestrator import _macro  # noqa: E402
from pii_anon_datasets.baselines.results import BaselineResults  # noqa: E402
from pii_anon_datasets.scoring.detection import aggregate_detection_score  # noqa: E402


def combine(root: str) -> BaselineResults:
    detectors: dict = {}
    per_det_records: list[int] = []
    per_det_gold: list[int] = []
    split = "test"
    ds_version = "2.0.0"  # provisional; overwritten from the shards (they all scored the same corpus)
    for det_dir in sorted(glob.glob(os.path.join(root, "*"))):
        if not os.path.isdir(det_dir):
            continue
        det = os.path.basename(det_dir)
        shards = sorted(glob.glob(os.path.join(det_dir, "*", "baseline_results.json")))
        if not shards:
            continue
        by_language: dict = {}
        tp = fp = fn = 0
        n_rec = 0
        coverage = None
        model_id = ""
        bt: dict = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
        for s in shards:
            data = json.loads(open(s, encoding="utf-8").read())
            lang = data["dataset"]["language"]
            split = data["dataset"].get("split", split)
            ds_version = data["dataset"].get("dataset_version", ds_version)
            blk = data["detectors"].get(det)
            if not blk:
                continue
            c = blk["micro"]["counts"]
            tp += c["tp"]
            fp += c["fp"]
            fn += c["fn"]
            n_rec += int(blk.get("n_records", 0))
            coverage = blk.get("coverage", coverage)
            model_id = blk.get("model_id", model_id)
            by_language[lang] = (blk.get("by_language") or {}).get(lang) or blk["micro"]
            for t, cell in (blk.get("by_entity_type") or {}).items():
                cc = cell.get("counts") or {}
                bt[t]["tp"] += cc.get("tp", 0)
                bt[t]["fp"] += cc.get("fp", 0)   # pool per-type fp so macro-F2 is real, not a micro copy
                bt[t]["fn"] += cc.get("fn", 0)
        micro = aggregate_detection_score(tp, fp, fn)
        by_type_scores = {t: aggregate_detection_score(v["tp"], v["fp"], v["fn"]) for t, v in bt.items()}
        by_type = {t: sc.as_dict() for t, sc in by_type_scores.items()}
        # Real macro = unweighted mean over types present in gold (n_gold>0), matching orchestrator._macro.
        macro = _macro([sc for sc in by_type_scores.values() if sc.counts.n_gold > 0]) or {
            "precision": 0.0, "recall": 0.0, "f1": 0.0, "f2": 0.0, "n_types": 0,
        }
        detectors[det] = {
            "status": "scored", "model_id": model_id, "deterministic": True, "record_errors": 0,
            "n_records": n_rec, "n_gold": tp + fn, "n_pred": tp + fp, "coverage": coverage,
            "micro": micro.as_dict(),
            "macro": macro,
            "by_entity_type": by_type, "by_domain": {}, "by_language": by_language,
        }
        per_det_records.append(n_rec)
        per_det_gold.append(tp + fn)
    ranking = sorted(
        ({"detector": d, "f2_micro": detectors[d]["micro"]["f2"],
          "f2_macro": (detectors[d].get("macro") or {}).get("f2", 0.0)}
         for d in detectors), key=lambda r: -r["f2_micro"])
    for i, r in enumerate(ranking, 1):
        r["rank"] = i
    # detectors all scored the same corpus, so per-detector totals agree; use the max as the split total.
    # split + dataset_version are read from the shards (uniform) so the combined file tracks its inputs.
    dataset = {"split": split, "language": "all", "dataset_version": ds_version,
               "n_records": max(per_det_records, default=0), "n_gold": max(per_det_gold, default=0)}
    return BaselineResults(dataset=dataset, confidence=0.95, ranking=ranking, detectors=detectors)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="results/baselines/fulltest-local",
                    help="dir holding <detector>/<language>/baseline_results.json shards")
    ap.add_argument("--out", default=None, help="output path (default: <root>/baseline_results.json)")
    args = ap.parse_args(argv)
    res = combine(args.root)
    out = args.out or os.path.join(args.root, "baseline_results.json")
    if not res.detectors:
        print(f"combine_lang_shards: no detector shards under {args.root}", file=sys.stderr)
        return 2
    with open(out, "w", encoding="utf-8") as f:
        f.write(res.to_json())
    # Render the F2-ranked leaderboard beside the json so a fresh runner call reproduces both artifacts
    # (parity with `pii-anon baselines --merge`, which also emits leaderboard.md).
    from pii_anon_datasets.reporting.baselines import render_baseline_leaderboard  # noqa: PLC0415
    md_path = os.path.join(os.path.dirname(out) or ".", "leaderboard.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_baseline_leaderboard(res) + "\n")
    print(f"combined {len(res.detectors)} detectors × {len(next(iter(res.detectors.values()))['by_language'])} "
          f"languages -> {out} (+ {os.path.basename(md_path)})")
    for r in res.ranking:
        print(f"  {r['rank']:2d} {r['detector']:12s} F2={r['f2_micro']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
