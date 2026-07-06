#!/usr/bin/env python3
"""Per-script F2 + Wilson recall lower-bound from a MULTILINGUAL aggregate baseline_results.json
(Path-B: sum by_language counts into ISO-15924 script buckets — no per-record parquet needed).
The 5 new 2C scripts get local-detector LBs; cloud providers (which don't support them) show '—'."""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(__file__)
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "..", "src"))

from multilingual_analysis import ASIAN, LANG_SCRIPT  # noqa: E402
from pii_anon_datasets.stats.intervals import wilson_interval  # noqa: E402


def _f2(tp, n_pred, n_gold):
    p = tp / n_pred if n_pred else 0.0
    r = tp / n_gold if n_gold else 0.0
    f2 = (5 * p * r / (4 * p + r)) if (4 * p + r) else 0.0
    return p, r, f2


def build_by_language(results_path: str, detectors: list) -> dict:
    """Return {lang: {"script": name, "n_gold": N, "f2": {det: f2}}} from the multilingual aggregate's
    by_language cells — the full per-language F2 (same source as the BASELINES matrix; supersedes the
    retired per-record Path-A). n_gold is identical across detectors for a language (the gold count)."""
    data = json.loads(open(results_path, encoding="utf-8").read())
    dets_blk = data.get("detectors", {})
    langs: dict = {}
    for det in detectors:
        for lang, cell in ((dets_blk.get(det) or {}).get("by_language") or {}).items():
            c = cell.get("counts") or {}
            rec = langs.setdefault(lang, {"script": LANG_SCRIPT.get(lang, lang), "n_gold": 0, "f2": {}})
            rec["n_gold"] = c.get("tp", 0) + c.get("fn", 0)
            rec["f2"][det] = cell.get("f2", 0.0)
    return langs


def render_leaderboard_md(table: dict, detectors: list) -> str:
    total = sum(r["n_gold"] for r in table.values())
    head = "| Lang | Script | n_gold | " + " | ".join(detectors) + " |"
    sep = "|---|---|---:|" + "---:|" * len(detectors)
    lines = [
        "# Multilingual leaderboard — per-language F2 (all detectors)",
        "",
        f"{total:,} gold spans across **{len(table)} languages** (full per-language `test` split). F2, "
        "strict-v1. ⚠ = Asian language. Regenerated from `results/baselines/fulltest-local` (the same "
        "aggregate as the BASELINES.md matrix); languages with low n_gold are underpowered (wide CIs).",
        "",
        head, sep,
    ]
    for lang in sorted(table, key=lambda k: -table[k]["n_gold"]):
        r = table[lang]
        flag = " ⚠" if lang in ASIAN else ""
        cells = " | ".join(f"{r['f2'].get(d, 0.0):.3f}" for d in detectors)
        lines.append(f"| {lang} | {r['script']}{flag} | {r['n_gold']:,} | {cells} |")
    return "\n".join(lines) + "\n"


def build_by_script(results_path: str) -> dict:
    """Return {script: {detector: {recall, f2, recall_lb, n_gold}}} from a multilingual aggregate."""
    data = json.loads(open(results_path, encoding="utf-8").read())
    out: dict = {}
    for det, blk in data.get("detectors", {}).items():
        for lang, cell in (blk.get("by_language") or {}).items():
            c = cell.get("counts")
            if not c:
                continue
            sc = LANG_SCRIPT.get(lang)
            if not sc:
                continue
            agg = out.setdefault(sc, {}).setdefault(det, {"tp": 0, "fp": 0, "fn": 0})
            agg["tp"] += c["tp"]
            agg["fp"] += c["fp"]
            agg["fn"] += c["fn"]
    table: dict = {}
    for sc, dets in out.items():
        table[sc] = {}
        for det, c in dets.items():
            tp, fp, fn = c["tp"], c["fp"], c["fn"]
            n_gold, n_pred = tp + fn, tp + fp
            _, r, f2 = _f2(tp, n_pred, n_gold)
            lb = wilson_interval(tp, n_gold).low if n_gold else 0.0
            table[sc][det] = {"recall": r, "f2": f2, "recall_lb": lb, "n_gold": n_gold}
    return table


def render_md(table: dict, detectors: list[str]) -> str:
    head = "| Script | " + " | ".join(f"{d} F2 / R-LB95" for d in detectors) + " |"
    sep = "|---|" + "---:|" * len(detectors)
    lines = [
        "# Multilingual performance by script — F2 with Wilson recall lower-bound (95%)",
        "",
        "Local detectors pooled per ISO-15924 script from the multilingual `by_language` counts (strict-v1). "
        "`R-LB95` = Wilson lower bound on recall. Cloud DLP per-language performance is in the BASELINES.md "
        "multilingual matrix (no provider supports the 5 new scripts ru/th/el/bn/he — the honesty guard).",
        "",
        head,
        sep,
    ]
    for sc in sorted(table, key=lambda s: -max((table[s][d]["n_gold"] for d in table[s]), default=0)):
        cells = []
        for d in detectors:
            v = table[sc].get(d)
            cells.append(f"{v['f2']:.3f} / {v['recall_lb']:.3f}" if v else "—")
        lines.append(f"| {sc} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="multilingual aggregate baseline_results.json")
    ap.add_argument("--detectors", default="gliner,piiranha,presidio,regex,spacy,stanza,scrubadub,flair")
    ap.add_argument("--out", default=os.path.join(_HERE, "..", "results", "tier-a", "multilingual_by_script.md"))
    args = ap.parse_args(argv)
    table = build_by_script(args.results)
    dets = [d.strip() for d in args.detectors.split(",") if d.strip()]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(render_md(table, dets))
    print(f"wrote {os.path.relpath(args.out)} — {len(table)} scripts")
    # Also (re)generate the per-language leaderboard from the SAME aggregate (supersedes the retired
    # per-record Path-A multilingual_analysis.py, which read a stale per-record dump + collided on the
    # by_script filename).
    lb_table = build_by_language(args.results, dets)
    lb_out = os.path.join(os.path.dirname(args.out), "multilingual_leaderboard.md")
    with open(lb_out, "w", encoding="utf-8") as f:
        f.write(render_leaderboard_md(lb_table, dets))
    print(f"wrote {os.path.relpath(lb_out)} — {len(lb_table)} languages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
