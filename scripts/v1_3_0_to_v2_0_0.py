#!/usr/bin/env python3
"""v1.3.0 → v2.0.0 corpus migration CLI (DC-02).

Deterministic, streaming. Writes to a ``.tmp`` then atomically replaces the input
only after a count check. The v1.3.0 state is pinned by the ``v1.3.0`` git tag
(the canonical archive) — never deleted. Run AFTER bumping pyproject to 2.0.0.

Usage:
  PYTHONPATH=src python scripts/v1_3_0_to_v2_0_0.py [--limit N] [--in PATH] [--no-replace]
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pii_anon_datasets.migration import migrate_record, unknown_entity_types  # noqa: E402

DEFAULT_IN = os.path.join(
    os.path.dirname(__file__), "..", "src", "pii_anon_datasets", "data", "pii_anon.jsonl.gz"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=DEFAULT_IN)
    ap.add_argument("--limit", type=int, default=0, help="migrate only first N records (sample mode)")
    ap.add_argument("--no-replace", action="store_true", help="write .v2.jsonl.gz, do not replace input")
    args = ap.parse_args()

    out_path = args.inp if not (args.limit or args.no_replace) else args.inp.replace(".jsonl.gz", ".v2.jsonl.gz")
    tmp_path = out_path + ".tmp"

    n_in = n_out = 0
    seen_ids: set[str] = set()
    dup_ids = 0
    unknown: set[str] = set()

    with gzip.open(args.inp, "rt", encoding="utf-8") as fin, gzip.open(tmp_path, "wt", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            n_in += 1
            if args.limit and n_in > args.limit:
                n_in -= 1
                break
            rec = json.loads(line)
            unknown |= unknown_entity_types(rec)
            mig = migrate_record(rec)
            rid = mig["record_id"]
            if rid in seen_ids:
                dup_ids += 1
            seen_ids.add(rid)
            fout.write(json.dumps(mig, ensure_ascii=False, sort_keys=True) + "\n")
            n_out += 1

    if n_out != n_in:
        print(f"ABORT: count mismatch in={n_in} out={n_out}", file=sys.stderr)
        os.remove(tmp_path)
        return 1
    os.replace(tmp_path, out_path)

    print(f"migrated {n_out} records  →  {os.path.relpath(out_path)}")
    print(f"unique record_ids: {len(seen_ids)}  (content-collisions: {dup_ids})")
    print(f"unknown entity types: {sorted(unknown) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
