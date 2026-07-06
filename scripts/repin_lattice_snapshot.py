#!/usr/bin/env python3
"""Surgically re-pin the design-time lattice frequency snapshot for 2C (declare new powered head languages).

The snapshot is a DESIGN-TIME spec (build_committed_lattice reads it, never live metadata — NFR-018). 2C is a
deliberate membership re-baseline: declare ru/th/el/bn/he as head languages (by_language >= 753) so their
language_x_entity_type cells become committed targets BEFORE generation fills them. `eval_lattice.json` cells
depend on membership only (not the exact count), so the count value is design-intent. Two modes:
  declare-head  — surgically bump the listed langs (pre-generation).
  from-metadata — regenerate by_language/by_entity_type from pii_anon.metadata.json distributions (post-build
                  honesty re-pin so the committed snapshot reflects the final corpus; membership unchanged).
"""
from __future__ import annotations

import argparse
import json
import os

_HERE = os.path.dirname(__file__)
DEFAULT_SNAP = os.path.join(_HERE, "..", "src", "pii_anon_datasets", "data", "lattice_freq_snapshot.json")
DEFAULT_META = os.path.join(_HERE, "..", "src", "pii_anon_datasets", "data", "pii_anon.metadata.json")


def _write(path, snap):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(snap, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def declare_head(snap_path, langs, *, count: int, source_version: str) -> None:
    snap = json.loads(open(snap_path, encoding="utf-8").read())
    for lang in langs:
        snap["by_language"][lang] = max(int(snap["by_language"].get(lang, 0)), count)
    snap["source_version"] = source_version
    snap["_comment"] = ("PINNED design-time frequency snapshot for the committed lattice. v2.2-dev 2C re-pin: "
                        "ru/th/el/bn/he declared head languages (powered rectangle 12->17). Routine enrichment "
                        "must NOT regenerate this; only deliberate composition changes (a new sub-project) may.")
    _write(snap_path, snap)


def from_metadata(snap_path, meta_path, *, source_version: str) -> None:
    meta = json.loads(open(meta_path, encoding="utf-8").read())
    dist = meta["distributions"]
    snap = json.loads(open(snap_path, encoding="utf-8").read())
    snap["by_language"] = dict(dist["by_language"])
    snap["by_entity_type"] = dict(dist["by_entity_type"])
    snap["source_version"] = source_version
    _write(snap_path, snap)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Re-pin the lattice frequency snapshot (2C).")
    ap.add_argument("--snapshot", default=DEFAULT_SNAP)
    ap.add_argument("--metadata", default=DEFAULT_META)
    ap.add_argument("--mode", choices=["declare-head", "from-metadata"], required=True)
    ap.add_argument("--langs", default="ru,th,el,bn,he")
    ap.add_argument("--count", type=int, default=21000)
    ap.add_argument("--source-version", default="2.2.0-dev")
    args = ap.parse_args(argv)
    if args.mode == "declare-head":
        declare_head(args.snapshot, args.langs.split(","), count=args.count, source_version=args.source_version)
        print(f"declared head langs {args.langs} (>= {args.count}); source_version={args.source_version}")
    else:
        from_metadata(args.snapshot, args.metadata, source_version=args.source_version)
        print(f"re-pinned by_language/by_entity_type from metadata; source_version={args.source_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
