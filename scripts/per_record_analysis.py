#!/usr/bin/env python3
"""Tier-A per-record analyses over the keystone dump — paired significance + complementarity + the
enriched-vs-core ablation. Pure post-processing over results/per-record/en-test/ (no detector runs).

Uses the harness's OWN audited stats (pii_anon_datasets.stats.paired.mcnemar +
stats.multitest.holm_bonferroni) so the benchmark "invents no statistics".

  A. Per-detector recall/precision/F2 recomputed from the hit vectors (sanity vs meta_*.json).
  B. Paired significance — McNemar (exact/χ²) over discordant gold spans for every adjacent rank pair,
     Holm–Bonferroni corrected, + the observed recall delta. (Local detectors only; the GLiNER-vs-AWS
     marquee test needs a budget-gated cloud per-record dump — flagged, not run.)
  C. Complementarity — oracle union recall for the top detector paired with each other + the full
     N-detector union ceiling (a novel "how disjoint is each detector's recall" finding).
  D. Enriched-vs-core ablation — per-detector F2 partitioned by provenance.source_type
     (synthetic core vs synthetic_lattice_enrichment vs curated_public); shows whether the ranking is
     invariant to the ~lattice fill (the AX-003 desk-reject neutraliser).

Usage: python scripts/per_record_analysis.py --dump results/per-record/en-test --out results/tier-a
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from pii_anon_datasets.stats.multitest import holm_bonferroni
from pii_anon_datasets.stats.paired import mcnemar

# All local detectors the dump may produce; the loader keeps only those with hits on disk, so flair
# (excluded from the current en-test dump) is auto-included if/when its hits are present.
DETECTORS = ["gliner", "presidio", "regex", "piiranha", "stanza", "spacy", "scrubadub", "flair"]


def _f2(tp, n_pred, n_gold):
    p = tp / n_pred if n_pred else 0.0
    r = tp / n_gold if n_gold else 0.0
    f2 = (5 * p * r / (4 * p + r)) if (4 * p + r) else 0.0
    return p, r, f2


def load(dump: Path):
    g = pq.read_table(dump / "gold.parquet").to_pydict()
    n = len(g["record_id"])
    gold_rid = g["record_id"]
    source_type = np.array(g["source_type"], dtype=object)
    hits, npred = {}, {}
    for d in DETECTORS:
        hp = dump / f"hits_{d}.parquet"
        if not hp.exists():
            continue
        ht = pq.read_table(hp).to_pydict()
        assert len(ht["hit"]) == n, f"{d}: hit length {len(ht['hit'])} != gold {n}"
        assert ht["record_id"][0] == gold_rid[0] and ht["record_id"][-1] == gold_rid[-1], f"{d}: gold misalignment"
        hits[d] = np.array(ht["hit"], dtype=bool)
        pc = pq.read_table(dump / f"predcounts_{d}.parquet").to_pydict()
        npred[d] = dict(zip(pc["record_id"], pc["n_pred"]))
    # record -> source_type (first gold row per record)
    rec_src = {}
    for rid, st in zip(gold_rid, source_type):
        if rid not in rec_src:
            rec_src[rid] = st
    return n, gold_rid, source_type, hits, npred, rec_src


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", default="results/per-record/en-test")
    ap.add_argument("--out", default="results/tier-a")
    args = ap.parse_args()
    dump, out = Path(args.dump), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    n, gold_rid, source_type, hits, npred, rec_src = load(dump)
    dets = [d for d in DETECTORS if d in hits]
    n_gold = n
    print(f"Loaded {n_gold:,} gold spans × {len(dets)} detectors: {dets}", flush=True)

    # A. per-detector recall / precision / F2 from hits
    summary = {}
    for d in dets:
        tp = int(hits[d].sum())
        total_pred = int(sum(npred[d].values()))
        p, r, f2 = _f2(tp, total_pred, n_gold)
        summary[d] = {"recall": r, "precision": p, "f2": f2, "tp": tp, "n_pred": total_pred}
    order = sorted(dets, key=lambda d: summary[d]["recall"], reverse=True)

    # B. McNemar over adjacent rank pairs + Holm
    pair_rows, pvals = [], []
    for a, b in zip(order, order[1:]):
        A, B = hits[a], hits[b]
        nb = int((A & ~B).sum())   # A hit, B miss
        nc = int((~A & B).sum())   # A miss, B hit
        res = mcnemar(nb, nc)
        d_recall = summary[a]["recall"] - summary[b]["recall"]
        label = f"{a}>{b}"
        pvals.append((label, res.p_value))
        pair_rows.append({"pair": label, "recall_a": summary[a]["recall"], "recall_b": summary[b]["recall"],
                          "delta_recall": d_recall, "b": nb, "c": nc, "p_raw": res.p_value,
                          "method": res.method, "odds_ratio": res.odds_ratio})
    holm = holm_bonferroni(pvals, alpha=0.05)
    for row, padj, rej in zip(pair_rows, holm.p_adjusted, holm.rejected):
        row["p_holm"] = padj
        row["significant"] = bool(rej)

    # C. complementarity (top detector unions + full ceiling)
    top = order[0]
    comp = []
    for d in order[1:]:
        union_r = float((hits[top] | hits[d]).mean())
        comp.append({"with": d, "union_recall": union_r, "gain_over_top": union_r - summary[top]["recall"]})
    full_union = hits[order[0]].copy()
    for d in order[1:]:
        full_union |= hits[d]
    ceiling = float(full_union.mean())

    # D. enriched-vs-core ablation by source_type
    parts = sorted(set(source_type.tolist()))
    abl = {p_: {} for p_ in parts}
    # per-partition n_pred per detector
    npred_part = {p_: {d: 0 for d in dets} for p_ in parts}
    for d in dets:
        for rid, k in npred[d].items():
            st = rec_src.get(rid)          # records with zero gold spans have no source_type partition
            if st in npred_part:           # → skip their (pure-FP) predictions for per-partition precision
                npred_part[st][d] += k
    for p_ in parts:
        mask = source_type == p_
        ng = int(mask.sum())
        for d in dets:
            tp = int(hits[d][mask].sum())
            npp = int(npred_part[p_].get(d, 0))
            pr, rc, f2 = _f2(tp, npp, ng)
            abl[p_][d] = {"recall": rc, "precision": pr, "f2": f2, "n_gold": ng, "tp": tp, "n_pred": npp}
    part_rank = {p_: [d for d in sorted(dets, key=lambda x: abl[p_][x]["f2"], reverse=True)] for p_ in parts}

    # ---- write JSON ----
    (out / "per_record_analysis.json").write_text(json.dumps(
        {"summary": summary, "order": order, "pairs": pair_rows, "complementarity": comp,
         "union_ceiling": ceiling, "ablation": abl, "ablation_rank": part_rank,
         "n_gold": n_gold}, indent=2, default=float), encoding="utf-8")

    # ---- B+C markdown ----
    md = [
        "# Paired significance + complementarity (local detectors)\n",
        f"Over **{n_gold:,}** gold spans, {len(dets)} local detectors. Paired McNemar (harness "
        "`stats.paired.mcnemar`, exact ≤1000 discordant else continuity-χ²), Holm–Bonferroni corrected "
        "(`stats.multitest`). RRS-style CI-overlap eyeballing is replaced by a paired test.\n",
        "> The GLiNER-vs-AWS marquee comparison needs AWS per-record hits — a budget-gated cloud dump "
        "(not run here). This pins the **local** ranking.\n",
        "## Adjacent-rank pairwise significance",
        "| Pair (A>B) | recall A | recall B | Δrecall | b (A✓B✗) | c (A✗B✓) | p (Holm) | method | significant |",
        "|---|---:|---:|---:|---:|---:|---:|---|:--:|",
    ]
    for r in pair_rows:
        md.append(f"| {r['pair']} | {r['recall_a']:.3f} | {r['recall_b']:.3f} | {r['delta_recall']:+.3f} | "
                  f"{r['b']:,} | {r['c']:,} | {r['p_holm']:.2e} | {r['method']} | {'✅' if r['significant'] else '—'} |")
    nsig = sum(1 for r in pair_rows if r["significant"])
    md += [f"\n**{nsig}/{len(pair_rows)} adjacent pairs are significant after Holm correction.**\n",
           "## Complementarity (oracle union recall)\n",
           f"Top local detector **{top}** recall = {summary[top]['recall']:.3f}. Union recall when paired:\n",
           "| + detector | union recall | gain over top |", "|---|---:|---:|"]
    for c in sorted(comp, key=lambda x: x["union_recall"], reverse=True):
        md.append(f"| {c['with']} | {c['union_recall']:.3f} | +{c['gain_over_top']:.3f} |")
    md += [f"\n**Full {len(dets)}-detector oracle-union recall ceiling = {ceiling:.3f}** "
           f"(vs best single {summary[top]['recall']:.3f}) — {ceiling - summary[top]['recall']:+.3f} of recall is "
           "recoverable by an ensemble: detectors miss *different* spans (a novel complementarity finding).\n"]
    (out / "paired_significance.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # ---- D markdown ----
    md2 = [
        "# Enriched-vs-core ablation (provenance.source_type)\n",
        "Does the F2 ranking survive partitioning out the ~lattice enrichment fill? Per-detector F2 by "
        "`provenance.source_type` over the English test split. Neutralises the AX-003 desk-reject "
        "(\"the ranking is an artefact of the formulaic fill\").\n",
        "| Detector | " + " | ".join(f"{p_} F2 (n_gold={abl[p_][dets[0]]['n_gold']:,})" for p_ in parts) + " |",
        "|---|" + "---:|" * len(parts),
    ]
    for d in order:
        md2.append(f"| {d} | " + " | ".join(f"{abl[p_][d]['f2']:.4f}" for p_ in parts) + " |")
    md2 += ["\n## Ranking by partition (top→bottom)\n"]
    for p_ in parts:
        md2.append(f"- **{p_}**: " + " > ".join(part_rank[p_]))
    # rank stability: top-2 identical across partitions?
    tops = {p_: tuple(part_rank[p_][:2]) for p_ in parts}
    stable = len(set(tops.values())) == 1
    md2.append(f"\n**Top-2 ordering {'IS' if stable else 'is NOT'} identical across all partitions** "
               + ("→ the headline ranking is invariant to the enrichment fill." if stable else
                  "→ the enrichment fill shifts the ranking; report per-partition."))
    md2.append("\n_Precision note: per-partition precision uses n_pred only from records IN that source_type "
               "partition; predictions from zero-gold records (which carry no partition) are excluded, so the "
               "per-partition F2 is for RANK comparison — not level-comparable to the headline micro-F2._")
    (out / "enrichment_ablation.md").write_text("\n".join(md2) + "\n", encoding="utf-8")

    print("Wrote paired_significance.md, enrichment_ablation.md, per_record_analysis.json", flush=True)
    print(f"  significance: {nsig}/{len(pair_rows)} adjacent pairs significant (Holm)", flush=True)
    print(f"  complementarity: union ceiling {ceiling:.3f} vs best single {summary[top]['recall']:.3f}", flush=True)
    print(f"  ablation partitions: {parts}; top-2 stable: {stable}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
