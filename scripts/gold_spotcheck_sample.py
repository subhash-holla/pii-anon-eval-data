#!/usr/bin/env python3
"""2F gold spot-check sampler — deterministic stratified ~500-span sample → a human review CSV.

Streams the corpus once (per-stratum reservoirs cap memory), allocates across (script, entity_type) strata
satisfying floors (>=2 per type, >=24 per priority script), records each span's inclusion probability p_incl
(for the aggregator's Horvitz-Thompson weighting), a seeded ~25% blind-to-type subset, and a tranche tag.
Output: results/tier-a/gold_spotcheck_review.csv (the PI fills type_correct/realistic/recovered_type/note).
"""
from __future__ import annotations

import argparse
import csv
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pii_anon_datasets import load_dataset  # noqa: E402

SEED = 20260619
PRIORITY_SCRIPTS = ("Cyrl", "Thai", "Grek", "Beng", "Hebr", "Latn")
PER_TYPE_FLOOR = 2
PRIORITY_SCRIPT_FLOOR = 24
BLIND_FRACTION = 0.25  # blind rows = entity_type withheld -> type-recovery + anchoring-resistant realism
RES_CAP = 60  # reservoir cap per (script, type) stratum
CONTEXT_PAD = 60
_HERE = os.path.dirname(__file__)
DEFAULT_OUT = os.path.join(_HERE, "..", "results", "tier-a", "gold_spotcheck_review.csv")
DEFAULT_KEY = os.path.join(_HERE, "..", "results", "tier-a", "gold_spotcheck_key.csv")
REALISM_RUBRIC = ("Realism rubric (mark realistic=1 if the value is a plausible instance of its type IN THIS "
                  "CONTEXT): 1=plausible (e.g. a well-formed email, a native-script name in its language); "
                  "0=implausible (e.g. an English/US value in a non-English carrier, malformed format). "
                  "Examples: 'pedro@x.com' as EMAIL=1; 'James Smith' as PERSON_NAME in a Greek record=0.")


def _iter_spans(corpus):
    for rec in corpus:
        for i, a in enumerate(rec.get("annotations", [])):
            yield {"record_id": rec["record_id"], "ann_idx": i, "language": rec.get("language", ""),
                   "script": rec.get("script", ""), "entity_type": a["entity_type"],
                   "span_text": a.get("text", ""), "rec_text": rec.get("text", ""),
                   "start": a.get("start", 0), "end": a.get("end", 0)}


def _stream_strata(corpus, rng):
    """One pass: per (script, entity_type) stratum -> population count + a seeded reservoir of <=RES_CAP spans."""
    pop: dict[tuple, int] = {}
    res: dict[tuple, list] = {}
    seen = 0
    for sp in _iter_spans(corpus):
        key = (sp["script"], sp["entity_type"])
        pop[key] = pop.get(key, 0) + 1
        bucket = res.setdefault(key, [])
        n = pop[key]
        if len(bucket) < RES_CAP:
            bucket.append(sp)
        else:  # reservoir replacement (Algorithm R), seeded
            j = rng.randrange(n)
            if j < RES_CAP:
                bucket[j] = sp
        seen += 1
    return pop, res, seen


def sample(corpus, *, total: int = 500, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed)
    pop, res, _ = _stream_strata(corpus, rng)
    keys = sorted(pop)  # deterministic order
    draw: dict[tuple, int] = {k: 0 for k in keys}

    def _take(key, k):
        draw[key] = min(pop[key], draw[key] + k)

    # 1) per-type floor: ensure >=PER_TYPE_FLOOR per entity_type (from its largest (script,type) cell)
    types = sorted({t for (_s, t) in keys})
    for t in types:
        cells = sorted((k for k in keys if k[1] == t), key=lambda k: -pop[k])
        have = sum(draw[k] for k in cells)
        for k in cells:
            if have >= PER_TYPE_FLOOR:
                break
            add = min(PER_TYPE_FLOOR - have, pop[k] - draw[k])
            _take(k, add)
            have += add
    # 2) priority-script floor: ensure >=PRIORITY_SCRIPT_FLOOR per priority script (round-robin its types)
    for sc in PRIORITY_SCRIPTS:
        cells = sorted((k for k in keys if k[0] == sc), key=lambda k: -pop[k])
        if not cells:
            continue
        idx = 0
        while sum(draw[k] for k in cells) < PRIORITY_SCRIPT_FLOOR and any(draw[k] < pop[k] for k in cells):
            k = cells[idx % len(cells)]
            if draw[k] < pop[k]:
                _take(k, 1)
            idx += 1
    # 3) proportional fill to `total` (HT weighting corrects any residual imbalance)
    current = sum(draw.values())
    remaining = max(0, total - current)
    total_pop = sum(pop.values())
    if remaining and total_pop:
        # largest-remainder proportional over headroom
        room = {k: pop[k] - draw[k] for k in keys}
        weights = {k: pop[k] / total_pop for k in keys}
        alloc = {k: min(room[k], int(remaining * weights[k])) for k in keys}
        for k in keys:
            _take(k, alloc[k])
        # top up any rounding shortfall deterministically by population
        for k in sorted(keys, key=lambda k: -pop[k]):
            if sum(draw.values()) >= total:
                break
            if draw[k] < pop[k]:
                _take(k, 1)

    # materialize: draw the allocated count from each stratum's reservoir (seeded), set p_incl + tranche
    out: list[dict] = []
    for k in keys:
        n = draw[k]
        if not n:
            continue
        bucket = res[k]
        picks = rng.sample(bucket, min(n, len(bucket)))
        p_incl = min(1.0, len(picks) / pop[k])
        for sp in picks:
            s, e = sp["start"], sp["end"]
            ctx = sp["rec_text"][max(0, s - CONTEXT_PAD): e + CONTEXT_PAD]
            out.append({
                "span_id": f"{sp['record_id']}#{sp['ann_idx']}", "record_id": sp["record_id"],
                "language": sp["language"], "script": sp["script"], "entity_type": sp["entity_type"],
                "span_text": sp["span_text"], "context": ctx.replace("\n", " "),
                "p_incl": round(p_incl, 8), "tranche": "stratified",
            })
    out.sort(key=lambda r: r["span_id"])
    # seeded ~25% blind subset (stratified by script so blinding isn't concentrated)
    brng = random.Random(seed ^ 0x9E3779B9)
    for sc in sorted({r["script"] for r in out}):
        rows = [r for r in out if r["script"] == sc]
        k = round(len(rows) * BLIND_FRACTION)
        for r in brng.sample(rows, k):
            r["blind"] = 1
    for r in out:
        r.setdefault("blind", 0)
    return out


# blind rows (entity_type withheld) do DOUBLE duty: type-recovery (recovered_type) AND the anchoring-resistant
# realism anchor (realistic rated without the type label visible) — see gold_spotcheck_aggregate.blind_realism_rate.
FIELDS = ["span_id", "record_id", "language", "script", "entity_type", "span_text", "context",
          "p_incl", "blind", "tranche", "type_correct", "realistic", "recovered_type", "note"]


def write_review_csv(rows: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("# 2F gold spot-check review — NON-blind rows: fill type_correct(1/0) + realistic(1/0). "
                "BLIND rows (blind=1, entity_type WITHHELD): fill recovered_type + realistic, leave type_correct blank.\n")
        f.write(f"# {REALISM_RUBRIC}\n")
        f.write("# BLIND rows give BOTH anchoring-resistant signals: type-recovery (recovered_type, named BEFORE you "
                "reveal the type) AND blind realism (realistic, judged without the type label visible).\n")
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            row = dict(r)
            if r.get("blind"):
                row["entity_type"] = ""  # withhold the type -> recovered_type + anchoring-resistant realism
            row.setdefault("type_correct", "")
            row.setdefault("realistic", "")
            row.setdefault("recovered_type", "")
            row.setdefault("note", "")
            w.writerow(row)


KEY_FIELDS = ["span_id", "entity_type", "script", "language"]


def write_key(rows: list[dict], path: str) -> None:
    """Answer key span_id -> true entity_type (so the aggregator can score blind type-recovery + group
    blind rows by their true type). Separate file: do NOT open it while adjudicating the blind rows."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("# 2F answer key — span_id -> true entity_type. DO NOT open while adjudicating blind rows.\n")
        w = csv.DictWriter(f, fieldnames=KEY_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="2F gold spot-check sampler.")
    ap.add_argument("--total", type=int, default=500)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--split", default=None, help="dataset split (default: full corpus)")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--key", default=DEFAULT_KEY)
    ap.add_argument("--key-only", action="store_true", help="write only the answer key (don't touch the review CSV)")
    args = ap.parse_args(argv)
    corpus = load_dataset(split=args.split) if args.split else load_dataset()
    rows = sample(corpus, total=args.total, seed=args.seed)
    write_key(rows, args.key)
    if args.key_only:
        print(f"wrote {os.path.relpath(args.key)} — {len(rows)} key rows (review CSV untouched)")
        return 0
    write_review_csv(rows, args.out)
    print(f"wrote {os.path.relpath(args.out)} (+ key {os.path.relpath(args.key)}) — {len(rows)} spans "
          f"({sum(r['blind'] for r in rows)} blind); fill the review CSV, then run gold_spotcheck_aggregate.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
