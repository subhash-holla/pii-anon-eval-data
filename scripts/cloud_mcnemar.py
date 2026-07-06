#!/usr/bin/env python3
"""GLiNER-vs-AWS paired McNemar — the marquee test behind 'a free local model ties the best cloud DLP'.

Replaces CI-overlap eyeballing of the near-tie (GLiNER micro-F2 0.7337 vs AWS 0.7360) with a PAIRED test
over the same 201,880 English gold spans: McNemar (harness `stats.paired.mcnemar`) on the discordant pairs
+ a seeded bootstrap CI on the recall difference. Reads the per-record hit dump (gliner from the local run,
aws from the authorized cloud re-score) — both aligned to the same gold.

Caveat carried into the output: AWS Comprehend is a non-deterministic managed service scored in a SINGLE
run; the p-value reflects that run. Synthetic-only (AX-001).

Usage: python scripts/cloud_mcnemar.py --dump results/per-record/en-test-v22 --out results/tier-a
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from pii_anon_datasets.stats.paired import mcnemar


def _load_hits(dump: Path, det: str, gold_rid):
    ht = pq.read_table(dump / f"hits_{det}.parquet").to_pydict()
    assert ht["record_id"] == gold_rid, f"{det}: hits not aligned to gold (record_id mismatch)"
    return np.array(ht["hit"], dtype=bool)


def main() -> int:
    ap = argparse.ArgumentParser()
    # The gliner-vs-aws McNemar needs BOTH detectors' per-record hits; only the en-test-v22 dump carries aws
    # (the local en-test dump is 8-local, no aws). Defaulting here keeps the committed McNemar reproducible.
    ap.add_argument("--dump", default="results/per-record/en-test-v22")
    ap.add_argument("--a", default="gliner")
    ap.add_argument("--b", default="aws")
    ap.add_argument("--out", default="results/tier-a")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260616)
    args = ap.parse_args()
    dump, out = Path(args.dump), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    g = pq.read_table(dump / "gold.parquet").to_pydict()
    gold_rid = g["record_id"]
    n_gold = len(gold_rid)
    A = _load_hits(dump, args.a, gold_rid)   # gliner
    B = _load_hits(dump, args.b, gold_rid)   # aws

    def _meta(det):
        p = dump / f"meta_{det}.json"
        return json.loads(p.read_text()) if p.exists() else {}
    ma, mb = _meta(args.a), _meta(args.b)

    b = int((A & ~B).sum())   # A hit, B miss
    c = int((~A & B).sum())   # A miss, B hit
    res = mcnemar(b, c)
    recall_a, recall_b = float(A.mean()), float(B.mean())
    delta = recall_a - recall_b

    # seeded numpy bootstrap CI on the recall difference (paired: same resampled gold indices for both)
    rng = np.random.default_rng(args.seed)
    Ai, Bi = A.astype(np.int8), B.astype(np.int8)
    deltas = np.empty(args.n_boot)
    for i in range(args.n_boot):
        idx = rng.integers(0, n_gold, n_gold)
        deltas[i] = Ai[idx].mean() - Bi[idx].mean()
    lo, hi = float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))

    sig = res.p_value < 0.05
    if not sig:
        verdict = (f"**Statistically indistinguishable.** GLiNER ({args.a}) and AWS ({args.b}) detect the "
                   f"same gold spans at a rate that is NOT significantly different (McNemar p={res.p_value:.3g}). "
                   f"A free local model is on par with the best cloud DLP on this synthetic English benchmark.")
    else:
        better = args.a if delta > 0 else args.b
        verdict = (f"**Significant difference** (McNemar p={res.p_value:.3g}): {better} has higher recall "
                   f"(Δrecall={delta:+.4f}). The near-tie in micro-F2 masks a paired-significant recall gap.")

    res_json = {"a": args.a, "b": args.b, "n_gold": n_gold,
                "recall_a": recall_a, "recall_b": recall_b, "delta_recall": delta,
                "delta_recall_ci95": [lo, hi], "mcnemar": res.as_dict(),
                "f2_a": ma.get("f2"), "f2_b": mb.get("f2"),
                "b_count_a_hit_b_miss": b, "c_count_a_miss_b_hit": c, "significant": bool(sig)}
    (out / "cloud_mcnemar.json").write_text(json.dumps(res_json, indent=2, default=float), encoding="utf-8")

    md = [
        f"# {args.a.upper()} vs {args.b.upper()} — paired McNemar (the 'free local ties best cloud' test)\n",
        f"Over **{n_gold:,}** English gold spans. {args.a} micro-F2 {ma.get('f2', float('nan')):.4f} "
        f"(recall {recall_a:.4f}) vs {args.b} micro-F2 {mb.get('f2', float('nan')):.4f} (recall {recall_b:.4f}).\n",
        "| Quantity | Value |", "|---|---|",
        f"| Discordant: {args.a}✓ {args.b}✗ (b) | {b:,} |",
        f"| Discordant: {args.a}✗ {args.b}✓ (c) | {c:,} |",
        f"| Δrecall ({args.a} − {args.b}) | **{delta:+.4f}** [95% CI {lo:+.4f}, {hi:+.4f}] |",
        f"| McNemar | {res.method}, statistic={res.statistic:.4g}, **p={res.p_value:.3g}** |",
        f"\n## Verdict\n{verdict}\n",
        "_Caveat: AWS Comprehend is a non-deterministic managed service scored in a SINGLE run; the p-value "
        "reflects that run. AX-001: synthetic-distribution precision, not external validity._",
    ]
    (out / "cloud_mcnemar.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{args.a} recall {recall_a:.4f} vs {args.b} recall {recall_b:.4f}  Δ={delta:+.4f} "
          f"[{lo:+.4f},{hi:+.4f}]  McNemar {res.method} p={res.p_value:.3g}  → {'sig' if sig else 'NS'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
