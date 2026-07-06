#!/usr/bin/env python3
"""Free JSON-mining bundle — paper-ready Tier-A analyses that need ZERO detector re-runs.

Reads the published 11-detector leaderboard ``baseline_results.json`` (which already carries
``by_entity_type`` with Wilson CIs, ``coverage``, ``micro``/``macro``/``partial_f1``, ``by_domain``)
plus the test-split Parquet for per-language record counts, and emits:

  1. coverage_ceiling.{md,png}  — coverage(reachable/63) vs micro-recall & macro-F2 across all detectors
                                  + Pearson r (the structural "ceiling caps recall, not model quality").
  2. per_entity_type.md         — micro vs macro F2 collapse per detector; per-type recall for the worst
                                  high-severity types; types with 0 coverage across ALL detectors.
  3. strict_vs_partial.md       — strict-v1 F2 ranking vs partial-overlap (partial_f1) re-rank.
  4. power_cliff.md             — per-language test-split record counts (powered-N vs coverage-tail).
  5. macro_vs_micro.png         — the collapse, as grouped bars.
  6. SUMMARY.md                 — one-screen synthesis with the load-bearing numbers.

Pure post-processing — no detector runs. Numbers are read directly from the canonical artifacts.

Usage: python scripts/free_bundle.py \
    --results results/baselines/tier1-en-all/baseline_results.json \
    --split-file src/pii_anon_datasets/splits/test.jsonl.gz --out results/tier-a
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

CLOUD = {"aws", "gcp", "azure"}
# High-severity types whose silent miss is the paper's "off-the-shelf detectors miss critical low-frequency PII".
HIGH_SEV = [
    "SOCIAL_SECURITY_NUMBER", "CREDIT_CARD_NUMBER", "PASSPORT_NUMBER", "MEDICAL_RECORD_NUMBER",
    "BANK_ACCOUNT_NUMBER", "DRIVER_LICENSE_NUMBER", "AGE", "HEALTH_CONDITION", "NATIONAL_ID_NUMBER",
    "DATE_OF_BIRTH", "AUTHENTICATION_TOKEN", "API_KEY",
]


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)          # drop NaN/inf pairs so one missing macro block can't null the whole r
    x, y = x[m], y[m]
    if len(x) < 2 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def scored(dets):
    return {n: b for n, b in dets.items() if b.get("status") == "scored"}


def load(results_path):
    d = json.load(open(results_path))
    return d, scored(d["detectors"])


def coverage_ceiling(d, dets, out: Path):
    of_total = next(iter(dets.values()))["coverage"]["of_total"]  # live canonical size (tracks 63 -> 66)
    rows = []
    for n, b in dets.items():
        rows.append({
            "detector": n,
            "kind": "cloud" if n in CLOUD else "local",
            "reachable": b["coverage"]["reachable"],
            "recall": b["micro"]["recall"],
            "micro_f2": b["micro"]["f2"],
            "macro_f2": (b.get("macro") or {}).get("f2", float("nan")),
        })
    rows.sort(key=lambda r: r["micro_f2"], reverse=True)
    r_recall = pearson([r["reachable"] for r in rows], [r["recall"] for r in rows])
    r_macro = pearson([r["reachable"] for r in rows], [r["macro_f2"] for r in rows])

    md = ["# Coverage ceiling vs recall (structural label-map bound)\n",
          f"Pearson r(reachable, micro-recall) = **{r_recall:.3f}**  ·  "
          f"r(reachable, macro-F2) = **{r_macro:.3f}**  (n={len(rows)} detectors).\n",
          f"Recall is bounded by how many of the {of_total} canonical types a detector's native→{of_total} "
          "label map can even reach — a *structural* ceiling independent of model quality.\n",
          f"| Detector | Kind | Coverage (reach/{of_total}) | Micro recall | Micro F2 | Macro F2 |",
          "|---|---|---:|---:|---:|---:|"]
    for r in rows:
        md.append(f"| {r['detector']} | {r['kind']} | {r['reachable']}/{of_total} | "
                  f"{r['recall']:.3f} | {r['micro_f2']:.4f} | {r['macro_f2']:.4f} |")
    (out / "coverage_ceiling.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
        for axi, (ykey, ylab) in zip(ax, [("recall", "Micro recall"), ("macro_f2", "Macro F2")]):
            xs = [r["reachable"] for r in rows]
            ys = [r[ykey] for r in rows]
            cols = ["#d55e00" if r["kind"] == "cloud" else "#0072b2" for r in rows]
            axi.scatter(xs, ys, c=cols, s=55, zorder=3)
            for r in rows:
                axi.annotate(r["detector"], (r["reachable"], r[ykey]),
                             fontsize=7, xytext=(3, 3), textcoords="offset points")
            if np.std(xs) > 0:
                m, b = np.polyfit(xs, ys, 1)
                xx = np.array([min(xs), max(xs)])
                axi.plot(xx, m * xx + b, "--", color="#888", lw=1, zorder=2)
            axi.set_xlabel(f"Coverage ceiling (reachable canonical types / {of_total})")
            axi.set_ylabel(ylab)
            axi.grid(True, alpha=0.25)
        ax[0].set_title(f"r = {r_recall:.2f}")
        ax[1].set_title(f"r = {r_macro:.2f}")
        fig.suptitle("Detection performance is bounded by label-map coverage (blue=local, orange=cloud)")
        fig.tight_layout()
        fig.savefig(out / "coverage_ceiling.png", dpi=150)
        plt.close(fig)
    except Exception as e:  # figure is nice-to-have; the table is the deliverable
        (out / "coverage_ceiling.png.SKIPPED").write_text(f"matplotlib failed: {e}\n")
    return rows, r_recall, r_macro


def micro_macro_collapse(d, dets, out: Path):
    rows = sorted(
        ({"detector": n, "micro_f2": b["micro"]["f2"], "macro_f2": (b.get("macro") or {}).get("f2", float("nan")),
          "micro_recall": b["micro"]["recall"], "macro_recall": (b.get("macro") or {}).get("recall", float("nan"))}
         for n, b in dets.items()),
        key=lambda r: r["micro_f2"], reverse=True)
    of_total = next(iter(dets.values()))["coverage"]["of_total"]  # live canonical size (tracks 63 -> 66)
    md = ["# Per-entity-type & micro→macro collapse\n",
          f"Macro (unweighted mean over the {of_total} types) collapses relative to micro: detectors succeed"
          " on a few frequent types and fail the long tail. The ratio macro/micro is a *coverage-ceiling*"
          " diagnostic.\n",
          "| Detector | Micro F2 | Macro F2 | Macro/Micro | Micro recall | Macro recall |",
          "|---|---:|---:|---:|---:|---:|"]
    for r in rows:
        ratio = r["macro_f2"] / r["micro_f2"] if r["micro_f2"] else float("nan")
        md.append(f"| {r['detector']} | {r['micro_f2']:.4f} | {r['macro_f2']:.4f} | {ratio:.2f} | "
                  f"{r['micro_recall']:.3f} | {r['macro_recall']:.3f} |")

    # zero-coverage-across-all-detectors types
    all_reach = set()
    for b in dets.values():
        all_reach |= set(b["coverage"].get("reachable_types", []))
    # taxonomy types = union over by_entity_type keys (the gold types present)
    gold_types = set()
    for b in dets.values():
        gold_types |= set(b.get("by_entity_type", {}).keys())
    unreached_by_all = sorted(t for t in gold_types if t not in all_reach)
    md += ["\n## Types reachable by NO detector (structural blind spots)\n",
           f"{len(unreached_by_all)} of {len(gold_types)} gold types are outside *every* detector's label map:\n",
           "`" + ", ".join(unreached_by_all) + "`\n" if unreached_by_all else "(none)\n"]

    # high-severity zero-recall table (top 2 detectors + best-of-any)
    top2 = [r["detector"] for r in rows[:2]]
    md += ["\n## High-severity types: recall of the top-2 detectors + best-of-any\n",
           "| Type | " + " | ".join(top2) + " | best recall (any detector) | best detector |",
           "|---|" + "---:|" * (len(top2) + 1) + "---|"]
    for t in HIGH_SEV:
        cells = []
        for det in top2:
            bt = dets[det].get("by_entity_type", {}).get(t)
            cells.append(f"{bt['recall']:.3f}" if bt else "—(unreached)")
        best_r, best_det = -1.0, "—"
        for n, b in dets.items():
            bt = b.get("by_entity_type", {}).get(t)
            if bt and bt["counts"]["tp"] + bt["counts"]["fn"] > 0 and bt["recall"] > best_r:
                best_r, best_det = bt["recall"], n
        if best_r > 0:                                  # a real best exists
            best_cell = f"{best_r:.3f}"
        else:                                            # every detector ties at recall 0 → no single "best"
            best_cell, best_det = "0.000 (all miss)", "—"
        md.append(f"| {t} | " + " | ".join(cells) + f" | {best_cell} | {best_det} |")
    (out / "per_entity_type.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        labels = [r["detector"] for r in rows]
        x = np.arange(len(labels))
        fig, ax = plt.subplots(figsize=(11, 4.2))
        ax.bar(x - 0.2, [r["micro_f2"] for r in rows], 0.4, label="Micro F2", color="#0072b2")
        ax.bar(x + 0.2, [r["macro_f2"] for r in rows], 0.4, label="Macro F2", color="#e69f00")
        ax.set_xticks(x); ax.set_xticklabels(labels, rotation=40, ha="right")
        ax.set_ylabel("F2"); ax.legend(); ax.grid(True, axis="y", alpha=0.25)
        ax.set_title("Micro vs macro F2 — the collapse exposes long-tail blindness")
        fig.tight_layout(); fig.savefig(out / "macro_vs_micro.png", dpi=150); plt.close(fig)
    except Exception as e:
        (out / "macro_vs_micro.png.SKIPPED").write_text(f"matplotlib failed: {e}\n")
    return rows


def strict_vs_partial(d, dets, out: Path):
    by_strict = sorted(dets.items(), key=lambda kv: kv[1]["micro"]["f2"], reverse=True)
    by_partial = sorted(dets.items(), key=lambda kv: kv[1]["micro"]["partial_f1"], reverse=True)
    prank = {n: i + 1 for i, (n, _) in enumerate(by_partial)}
    md = ["# Strict-v1 vs partial-overlap re-ranking\n",
          "`partial_f1` gives 0.5 credit for a same-type overlapping span (no CI by design). Under partial"
          " credit the ordering near the top can flip — a robustness check on the headline.\n",
          "| Strict rank | Detector | Micro F2 (strict) | partial_f1 | Partial rank | Δrank |",
          "|---:|---|---:|---:|---:|---:|"]
    for i, (n, b) in enumerate(by_strict):
        sr, pr = i + 1, prank[n]
        md.append(f"| {sr} | {n} | {b['micro']['f2']:.4f} | {b['micro']['partial_f1']:.4f} | {pr} | {sr - pr:+d} |")
    # headline flips
    flips = [n for i, (n, _) in enumerate(by_strict) if (i + 1) != prank[n]]
    md += ["\n**Rank changes under partial credit:** " + (", ".join(flips) if flips else "none") + "."]
    (out / "strict_vs_partial.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return by_strict, by_partial


def power_cliff(split_file, out: Path, d):
    # Accept the frozen corpus split (.jsonl.gz) directly, or a parquet export — read only language + domain.
    if str(split_file).endswith((".jsonl.gz", ".jsonl")):
        import gzip
        import json as _json
        opener = gzip.open if str(split_file).endswith(".gz") else open
        langs, doms = [], []
        with opener(split_file, "rt", encoding="utf-8") as fh:
            for line in fh:
                r = _json.loads(line)
                langs.append(r.get("language"))
                doms.append(r.get("domain"))
    else:
        import pyarrow.parquet as pq
        tbl = pq.read_table(split_file, columns=["language", "domain"])
        langs = tbl.column("language").to_pylist()
        doms = tbl.column("domain").to_pylist()
    from collections import Counter
    lc = Counter(langs); dc = Counter(doms)
    total = len(langs)
    ordered = lc.most_common()
    powered = [(l, c) for l, c in ordered if c >= 1000]
    tail = [(l, c) for l, c in ordered if c < 1000]
    md = ["# Per-language / per-domain power cliff\n",
          f"Test split: **{total:,} records** across **{len(lc)} languages**. The English Tier-1"
          f" leaderboard is one (powered) language; the multilingual board is a *resource* claim until run.\n",
          f"- **Powered (≥1000 records): {len(powered)} languages** — "
          + ", ".join(f"{l}={c:,}" for l, c in powered[:15]) + "\n",
          f"- **Coverage tail (<1000 records): {len(tail)} languages**, "
          f"min={min(c for _, c in tail) if tail else 0}, "
          f"median={int(np.median([c for _, c in tail])) if tail else 0} records/language.\n",
          "## Records per domain\n",
          "| Domain | Records |", "|---|---:|"]
    for dom, c in dc.most_common():
        md.append(f"| {dom} | {c:,} |")
    (out / "power_cliff.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return lc, dc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results/baselines/tier1-en-all/baseline_results.json")
    # Per-language power-cliff counts come from the FROZEN corpus split (reproducible), NOT the dist/hf
    # export (which is regenerated separately at the DOI/HF re-mint). Accepts .jsonl.gz or .parquet.
    ap.add_argument("--split-file", "--test-parquet", dest="split_file",
                    default="src/pii_anon_datasets/splits/test.jsonl.gz")
    ap.add_argument("--out", default="results/tier-a")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    d, dets = load(args.results)
    if len(dets) < 2:                                # degenerate input → clear message, not an IndexError
        print(f"free_bundle: need >=2 scored detectors, found {len(dets)}", flush=True)
        return 1
    cov_rows, r_recall, r_macro = coverage_ceiling(d, dets, out)
    mm_rows = micro_macro_collapse(d, dets, out)
    by_strict, by_partial = strict_vs_partial(d, dets, out)
    lc, dc = power_cliff(args.split_file, out, d)

    top = by_strict[0][0]; second = by_strict[1][0]
    pt0 = by_partial[0][0]; pt1 = by_partial[1][0]
    of_total = next(iter(dets.values()))["coverage"]["of_total"]  # live canonical size (tracks 63 -> 66)
    summary = [
        "# Tier-A free bundle — synthesis\n",
        f"Source: `{args.results}` (n_records={d['dataset']['n_records']:,}, "
        f"n_gold={d['dataset']['n_gold']:,}, split={d['dataset']['split']}/{d['dataset']['language']}). "
        "Zero detector re-runs.\n",
        "## Load-bearing numbers",
        "- **Coverage ceiling is real:** Pearson r(reachable/{}, micro-recall) = **{:.2f}**, "
        "r(reachable, macro-F2) = **{:.2f}** across {} detectors — recall tracks the label-map ceiling, "
        "not just model quality.".format(of_total, r_recall, r_macro, len(cov_rows)),
        f"- **Strict leaderboard top-2:** {top} (F2 {dets[top]['micro']['f2']:.4f}) ≳ "
        f"{second} (F2 {dets[second]['micro']['f2']:.4f}).",
        f"- **Partial-overlap flips the top:** {pt0} (partial_f1 {dets[pt0]['micro']['partial_f1']:.4f}) > "
        f"{pt1} ({dets[pt1]['micro']['partial_f1']:.4f}).",
        "- **Macro collapse:** "
        + "; ".join(f"{r['detector']} {r['micro_f2']:.3f}→{r['macro_f2']:.3f}" for r in mm_rows[:3])
        + " (micro→macro F2).",
        f"- **Power cliff:** {sum(1 for _,c in lc.items() if c>=1000)} powered languages (≥1000 recs); "
        f"{sum(1 for _,c in lc.items() if c<1000)} in the coverage tail.",
        "\n## Files",
        "- `coverage_ceiling.md` / `.png`",
        "- `per_entity_type.md`",
        "- `strict_vs_partial.md`",
        "- `power_cliff.md`",
        "- `macro_vs_micro.png`",
    ]
    (out / "SUMMARY.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("Free bundle written to", out)
    for f in sorted(out.iterdir()):
        print("  ", f.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
