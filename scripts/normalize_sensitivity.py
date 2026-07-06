#!/usr/bin/env python3
"""Canonicalize sensitivity_class on every annotation in the corpus.

Streams the canonical corpus (default: src/pii_anon_datasets/data/pii_anon.jsonl.gz),
sets each annotation's ``sensitivity_class`` to the authoritative value from
``SENSITIVITY_MAP`` (imported from ``migrate_v1_to_v2``), and atomically replaces the
file after a count check.  Annotations whose ``entity_type`` is NOT in the map are left
unchanged (never invented).

Usage:
    PYTHONPATH=src:. python scripts/normalize_sensitivity.py
    PYTHONPATH=src:. python scripts/normalize_sensitivity.py --in PATH
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from pathlib import Path

# Make repo-root and src importable (mirrors the convention in other scripts here)
_SCRIPTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_DIR.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_SCRIPTS_DIR))

from migrate_v1_to_v2 import SENSITIVITY_MAP  # noqa: E402

_PKG = _REPO_ROOT / "src" / "pii_anon_datasets"
DEFAULT_IN = str(_PKG / "data" / "pii_anon.jsonl.gz")


# ─── Pure / unit-testable transform ─────────────────────────────────────────


def normalize_record(rec: dict) -> dict:
    """Return *rec* (mutated in place) with each annotation's sensitivity_class
    canonicalized to SENSITIVITY_MAP[entity_type].

    Annotations whose entity_type is absent from the map are left untouched.
    """
    for ann in rec.get("annotations", []):
        canonical = SENSITIVITY_MAP.get(ann.get("entity_type", ""))
        if canonical is not None:
            ann["sensitivity_class"] = canonical
    return rec


# ─── Streaming CLI ──────────────────────────────────────────────────────────


def normalize_file(inp: str) -> int:
    """Normalize *inp* in place (atomic write via .tmp).  Returns 0 on success, 1 on abort."""
    tmp_path = inp + ".tmp"

    n_in = n_out = 0
    changed_annotations = 0

    with (
        gzip.open(inp, "rt", encoding="utf-8") as fin,
        gzip.open(tmp_path, "wt", encoding="utf-8") as fout,
    ):
        for line in fin:
            line = line.strip()
            if not line:
                continue
            n_in += 1
            rec = json.loads(line)

            # Track how many annotations change
            before = [
                a.get("sensitivity_class") for a in rec.get("annotations", [])
            ]
            normalize_record(rec)
            after = [
                a.get("sensitivity_class") for a in rec.get("annotations", [])
            ]
            changed_annotations += sum(b != a for b, a in zip(before, after, strict=True))

            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_out += 1

    if n_out != n_in:
        print(
            f"ABORT: count mismatch in={n_in} out={n_out} for {inp}",
            file=sys.stderr,
        )
        os.remove(tmp_path)
        return 1

    os.replace(tmp_path, inp)
    print(f"normalized {n_out:,} records ({changed_annotations:,} annotations changed)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Canonicalize sensitivity_class across the corpus using SENSITIVITY_MAP."
    )
    ap.add_argument(
        "--in",
        dest="inp",
        default=DEFAULT_IN,
        help=f"Input jsonl.gz path (default: {DEFAULT_IN})",
    )
    args = ap.parse_args()
    return normalize_file(args.inp)


if __name__ == "__main__":
    raise SystemExit(main())
