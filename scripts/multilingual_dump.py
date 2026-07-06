#!/usr/bin/env python3
"""Multilingual per-record dump — extends the English leaderboard to ALL languages in the test split.

Reuses the VALIDATED scoring from `per_record_dump.py` (same adapters, same strict-v1 matcher) but:
  * stratifies by language with a per-language cap (balance + tractable compute);
  * records `script` + `language_family` in the gold table so the analysis can slice by writing system.

flair is excluded (slow, English-only); the multilingual-relevant detectors are gliner / piiranha
(multilingual models) + regex (language-agnostic patterns), with the English-tuned NER detectors
(spacy / stanza / presidio / scrubadub) included to MEASURE their cross-lingual collapse.

Resumable per-detector. Output: results/per-record/multilingual/{gold,hits_*,predcounts_*,meta_*}.

Usage: python scripts/multilingual_dump.py --per-lang-cap 600 --out results/per-record/multilingual
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

# Reuse the validated scoring core (sys.path[0] == scripts/ when run as `python scripts/multilingual_dump.py`).
from per_record_dump import _write_parquet, score_detector

from pii_anon_datasets import load_dataset
from pii_anon_datasets.baselines import registry

DETECTORS = ["regex", "scrubadub", "spacy", "presidio", "gliner", "piiranha", "stanza"]


def build_gold_multi(records) -> list[dict]:
    rows: list[dict] = []
    for rec in records:
        rid = str(rec["record_id"])
        lang = str(rec.get("language") or "unknown")
        script = str(rec.get("script") or "unknown")
        fam = str(rec.get("language_family") or "unknown")
        anns = rec.get("annotations") or []
        if isinstance(anns, str):
            anns = json.loads(anns)
        for gi, a in enumerate(anns):
            rows.append({
                "record_id": rid, "gold_idx": gi, "entity_type": str(a["entity_type"]),
                "language": lang, "script": script, "language_family": fam,
                "sensitivity_class": str(a.get("sensitivity_class") or "unknown"),
            })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    ap.add_argument("--per-lang-cap", type=int, default=600, help="max records per language (balance)")
    ap.add_argument("--detectors", default=",".join(DETECTORS))
    ap.add_argument("--out", default="results/per-record/multilingual")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    recs = load_dataset(split=args.split, language=None)
    per: Counter = Counter()
    capped = []
    for r in recs:
        lang = str(r.get("language") or "unknown")
        if per[lang] < args.per_lang_cap:
            capped.append(r)
            per[lang] += 1
    print(f"Capped to {len(capped)} records across {len(per)} languages (cap {args.per_lang_cap}/lang)", flush=True)

    # alignment guard: a resume against the same --out with a different cap/record set would misalign hits↔gold
    content_hash = hashlib.sha256("\x1e".join(str(r.get("record_id", "")) for r in capped).encode()).hexdigest()
    manifest_path = out / "run_manifest.json"
    if manifest_path.exists():
        prev = json.loads(manifest_path.read_text())
        if (prev.get("content_hash"), prev.get("per_lang_cap")) != (content_hash, args.per_lang_cap):
            raise SystemExit(f"[abort] {out} built with a different cap/record set "
                             f"(prev cap={prev.get('per_lang_cap')} n={prev.get('n_records')}); use a fresh --out dir.")
    else:
        manifest_path.write_text(json.dumps(
            {"split": args.split, "per_lang_cap": args.per_lang_cap, "n_records": len(capped),
             "content_hash": content_hash}, indent=2), encoding="utf-8")

    gold_path = out / "gold.parquet"
    if not gold_path.exists():
        gold = build_gold_multi(capped)
        _write_parquet(gold, gold_path)
        print(f"gold.parquet: {len(gold)} gold spans", flush=True)

    names = [n.strip() for n in args.detectors.split(",") if n.strip()]
    adapters = {a.name: a for a in registry.resolve(names)}
    for name in names:
        meta_path = out / f"meta_{name}.json"
        if meta_path.exists():
            print(f"[{name}] already done — skipping", flush=True)
            continue
        ad = adapters.get(name)
        if ad is None or not ad.available():
            meta_path.write_text(json.dumps({"status": "unavailable"}), encoding="utf-8")
            continue
        print(f"[{name}] scoring {len(capped)} records…", flush=True)
        hits, pred_rows, micro = score_detector(ad, capped)
        gi_rows = []
        h = 0
        for rec in capped:
            rid = str(rec["record_id"])
            anns = rec.get("annotations") or []
            if isinstance(anns, str):
                anns = json.loads(anns)
            for gi in range(len(anns)):
                gi_rows.append({"record_id": rid, "gold_idx": gi, "hit": hits[h]})
                h += 1
        _write_parquet(gi_rows, out / f"hits_{name}.parquet")
        _write_parquet(pred_rows, out / f"predcounts_{name}.parquet")
        meta_path.write_text(json.dumps({"status": "scored", **micro}, indent=2), encoding="utf-8")
        print(f"[{name}] f2={micro['f2']:.4f} recall={micro['recall']:.4f} ({micro['wall_seconds']:.0f}s)", flush=True)

    print(f"Multilingual dump complete → {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
