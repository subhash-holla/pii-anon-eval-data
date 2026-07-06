#!/usr/bin/env python3
"""v2.0.0 → v2.1.0 corpus migration CLI (additive honesty layer).

Deterministic, streaming. Applies the additive honesty transform and re-stamps the version; writes to a
``.tmp`` then atomically replaces the input only after a count check. v2.0.0 is pinned by the ``v2.0.0``
git tag. Run AFTER bumping pyproject to 2.1.0.

By default migrates EVERY canonical jsonl.gz source that ``load_dataset`` can read — the full corpus
(``data/pii_anon.jsonl.gz``), every split (``splits/*.jsonl.gz``), and every subset
(``subsets/**/*.jsonl.gz``) — so the honesty layer is consistent across all access patterns. The transform
is value-idempotent, so re-running over an already-migrated file is safe.

Usage:
  PYTHONPATH=src python scripts/v2_0_0_to_v2_1_0.py                 # migrate ALL canonical sources in place
  PYTHONPATH=src python scripts/v2_0_0_to_v2_1_0.py --in PATH       # migrate one file
  PYTHONPATH=src python scripts/v2_0_0_to_v2_1_0.py --in PATH --limit 200 --no-replace   # sample (smoke test)
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pii_anon_datasets.honesty import TARGET_VERSION, apply_honesty  # noqa: E402

_PKG = os.path.join(os.path.dirname(__file__), "..", "src", "pii_anon_datasets")
DEFAULT_IN = os.path.join(_PKG, "data", "pii_anon.jsonl.gz")


def canonical_sources() -> list[str]:
    """Every jsonl.gz source ``load_dataset`` reads: the full corpus + splits + subsets."""
    patterns = [
        os.path.join(_PKG, "data", "pii_anon.jsonl.gz"),
        os.path.join(_PKG, "splits", "*.jsonl.gz"),
        os.path.join(_PKG, "subsets", "**", "*.jsonl.gz"),
    ]
    out: list[str] = []
    for pat in patterns:
        out.extend(sorted(glob.glob(pat, recursive=True)))
    # de-dup while preserving order
    seen: set[str] = set()
    return [p for p in out if not (p in seen or seen.add(p))]


def migrate_file(inp: str, *, limit: int = 0, no_replace: bool = False) -> int:
    """Migrate one jsonl.gz file in place (or to a `.v21.jsonl.gz` sample). Returns 0 on success, 1 on abort."""
    out_path = inp if not (limit or no_replace) else inp.replace(".jsonl.gz", ".v21.jsonl.gz")
    tmp_path = out_path + ".tmp"

    n_in = n_out = 0
    with gzip.open(inp, "rt", encoding="utf-8") as fin, gzip.open(tmp_path, "wt", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            n_in += 1
            if limit and n_in > limit:
                n_in -= 1
                break
            rec = json.loads(line)
            mig = apply_honesty(rec)
            mig["schema_version"] = TARGET_VERSION
            mig["version"] = TARGET_VERSION
            fout.write(json.dumps(mig, ensure_ascii=False, sort_keys=True) + "\n")
            n_out += 1

    if n_out != n_in:
        print(f"ABORT: count mismatch in={n_in} out={n_out} for {inp}", file=sys.stderr)
        os.remove(tmp_path)
        return 1
    os.replace(tmp_path, out_path)
    print(f"migrated {n_out:>7,} records → {os.path.relpath(out_path)} (v{TARGET_VERSION}, additive honesty)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=None, help="migrate one file (default: ALL canonical sources)")
    ap.add_argument("--limit", type=int, default=0, help="migrate only first N records (sample mode; implies one file)")
    ap.add_argument("--no-replace", action="store_true", help="write .v21.jsonl.gz, do not replace input")
    args = ap.parse_args()

    if args.inp or args.limit or args.no_replace:
        return migrate_file(args.inp or DEFAULT_IN, limit=args.limit, no_replace=args.no_replace)

    sources = canonical_sources()
    print(f"migrating {len(sources)} canonical jsonl.gz sources (full corpus + splits + subsets)...")
    for path in sources:
        if migrate_file(path) != 0:
            return 1
    print(f"DONE: {len(sources)} sources migrated to v{TARGET_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
