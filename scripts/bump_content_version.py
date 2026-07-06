#!/usr/bin/env python3
"""Bump the CONTENT version across the corpus + scored shards + validator + pyproject + corpus metadata.

A byte-safe, targeted version-FIELD re-stamp — NO re-generation, NO schema change, NO offset recompute.
The schema is unchanged (2.1.0 -> 2.2.0 adds records/languages/native-Thai, not fields), but the project
policy is that ``schema_version`` tracks the content version (check_version_sync Tier-1), so both the
``version`` and ``schema_version`` record fields advance. The ARCHIVED/DOI version (CITATION.cff,
.zenodo.json, release/citation.py, check_version_sync ARCHIVED_VERSION) is bumped SEPARATELY at the
Zenodo mint — this script never touches it.

Idempotent (a second run finds nothing to replace). Corpus writes are streaming + atomic (.tmp + replace).

Usage: python scripts/bump_content_version.py 2.1.0 2.2.0

Follow-ups this script does NOT do (printed at the end): pip install -e . --no-deps; re-derive the
version-bearing tier-a artifacts + re-sync BASELINES; bump TIER-1 doc titles; write_manifest.py (data) +
--frozen (EX00); validate.py; check_version_sync.py; pytest.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _restamp(text: str, old: str, new: str) -> str:
    # "version": "X" cannot match inside "schema_version": "X" (the leading quote differs), so order-safe.
    return (text.replace(f'"schema_version": "{old}"', f'"schema_version": "{new}"')
                .replace(f'"version": "{old}"', f'"version": "{new}"'))


def restamp_corpus(old: str, new: str) -> tuple[int, int]:
    files = changed = 0
    for p in sorted(glob.glob(str(ROOT / "src/pii_anon_datasets/**/*.jsonl.gz"), recursive=True)):
        files += 1
        tmp = p + ".tmp"
        hit = False
        with gzip.open(p, "rt", encoding="utf-8") as fin, gzip.open(tmp, "wt", encoding="utf-8") as fout:
            for line in fin:
                out = _restamp(line, old, new)
                if out != line:
                    hit = True
                fout.write(out)
        if hit:
            os.replace(tmp, p)
            changed += 1
        else:
            os.remove(tmp)
    return files, changed


def restamp_metadata(old: str, new: str) -> int:
    n = 0
    for name in ("pii_anon.metadata.json",):
        p = ROOT / "src/pii_anon_datasets/data" / name
        if p.exists():
            s = p.read_text(encoding="utf-8")
            r = s.replace(f'"version": "{old}"', f'"version": "{new}"')
            if r != s:
                p.write_text(r, encoding="utf-8")
                n += 1
    return n


def restamp_shards(old: str, new: str) -> int:
    n = 0
    for root in ("tier1-en-all", "en-local", "fulltest-local", "aws-en-full", "fulltest-cloud"):
        pat = str(ROOT / f"results/baselines/{root}/**")
        for p in (glob.glob(pat + "/baseline_results.json", recursive=True)
                  + glob.glob(pat + "/baseline_run_record.jsonl", recursive=True)):
            s = Path(p).read_text(encoding="utf-8")
            r = s.replace(f'"dataset_version": "{old}"', f'"dataset_version": "{new}"')
            if r != s:
                Path(p).write_text(r, encoding="utf-8")
                n += 1
    return n


def restamp_code(old: str, new: str) -> None:
    pp = ROOT / "pyproject.toml"
    pp.write_text(pp.read_text().replace(f'version = "{old}"', f'version = "{new}"', 1), encoding="utf-8")
    v = ROOT / "scripts/validate.py"
    v.write_text(v.read_text().replace(f'SCHEMA_VERSION = "{old}"', f'SCHEMA_VERSION = "{new}"', 1), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    args = ap.parse_args(argv)
    nfiles, ncorpus = restamp_corpus(args.old, args.new)
    nmeta = restamp_metadata(args.old, args.new)
    nshard = restamp_shards(args.old, args.new)
    restamp_code(args.old, args.new)
    print(f"corpus: {ncorpus}/{nfiles} .jsonl.gz re-stamped; metadata: {nmeta}; shards+run-records: {nshard}; "
          f"pyproject + validate.py SCHEMA_VERSION -> {args.new}")
    print("FOLLOW-UPS (not done here): pip install -e . --no-deps ; re-derive tier-a + sync BASELINES/README ; "
          "bump TIER-1 doc titles (README/DATASHEET/BASELINES/RELEASE_CHECKLIST) ; write_manifest.py + --frozen ; "
          "validate.py ; check_version_sync.py ; pytest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
