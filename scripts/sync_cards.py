#!/usr/bin/env python3
"""Regenerate the marker-delimited leaderboard blocks in the public cards from baseline_results.json.

Thin CLI over :mod:`pii_anon_datasets.reporting.cards` + the audited ``render_baseline_leaderboard`` — so
"report accordingly" is one command, not a hand-edit. All statistics come from the audited scorer; this
script only formats + places text between ``<!-- BEGIN-{marker} -->`` / ``<!-- END-{marker} -->`` lines.

  # Regenerate a full leaderboard block from one results JSON (e.g. the English headline, or local census):
  python scripts/sync_cards.py block  --results results/baselines/tier1-en-all/baseline_results.json \
                                      --file BASELINES.md --marker LEADERBOARD [--dry-run]

  # Build the cross-detector by-language F2 matrix for the full multilingual section:
  python scripts/sync_cards.py matrix --local results/baselines/fulltest-local/baseline_results.json \
                                      --cloud-glob 'results/baselines/fulltest-cloud/*/*/baseline_results.json' \
                                      --file BASELINES.md --marker LEADERBOARD-MULTILINGUAL [--dry-run]

``--dry-run`` prints the new block to stdout and writes nothing. Without it, the file is rewritten in place
(only the bytes between the markers change — verify with ``git diff``).
"""

from __future__ import annotations

import argparse
import glob
import json
import pathlib
import sys

_REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "src"))

from pii_anon_datasets.reporting import cards  # noqa: E402
from pii_anon_datasets.reporting.baselines import render_baseline_leaderboard  # noqa: E402

# PII-Anon's 12 "major" languages, by descending test-split record count (each >6k records; ~96% of split).
_DEFAULT_LANGUAGES = "en,nl,hi,ko,pt,it,es,ar,zh,fr,ja,de"
_CLOUD = ("aws", "gcp", "azure")


def _load(path: str) -> dict:
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def _apply(file: str, marker: str, block: str, dry_run: bool) -> int:
    if dry_run:
        print(block)
        print(f"\n[dry-run] would write block between BEGIN-{marker}/END-{marker} in {file}", file=sys.stderr)
        return 0
    target = pathlib.Path(file)
    updated = cards.replace_between_markers(target.read_text(encoding="utf-8"), marker, block)
    target.write_text(updated, encoding="utf-8")
    print(f"sync_cards: updated BEGIN-{marker}/END-{marker} in {file}")
    return 0


def _cmd_block(args: argparse.Namespace) -> int:
    block = render_baseline_leaderboard(_load(args.results))
    return _apply(args.file, args.marker, block, args.dry_run)


def _cmd_sanity(args: argparse.Namespace) -> int:
    import gzip
    import json as _json

    from pii_anon_datasets.baselines import orchestrator, registry
    from pii_anon_datasets.reporting.baselines import render_leaderboard_table

    path = args.split
    opener = gzip.open if path.endswith(".gz") else open
    records = [_json.loads(line) for line in opener(path, "rt", encoding="utf-8") if line.strip()]
    # Inject a synthetic record_id for records that lack one (e.g. test fixtures).
    for i, rec in enumerate(records):
        if "record_id" not in rec:
            rec["record_id"] = str(i)
    if args.language:
        records = [r for r in records if (r.get("language") or r.get("lang")) == args.language]
    adapters = registry.resolve(registry.SANITY_DETECTORS)
    results = orchestrator.score_detectors(
        records, adapters, dataset_info={"split": "sanity-check", "language": args.language or "en"})
    block = render_leaderboard_table(results.as_dict())
    return _apply(args.file, args.marker, block, args.dry_run)


def _cmd_matrix(args: argparse.Namespace) -> int:
    languages = [c.strip() for c in args.languages.split(",") if c.strip()]
    local = _load(args.local)
    shards = [_load(p) for p in sorted(glob.glob(args.cloud_glob))]

    rows: list[tuple[str, dict[str, float]]] = []
    for row in local.get("ranking", []):  # local detectors in their F2-ranked order
        det = local["detectors"][row["detector"]]
        rows.append((row["detector"], cards.language_f2(det)))
    for provider in _CLOUD:  # cloud providers, assembled from their per-language shards
        cells = cards.cloud_provider_f2(shards, provider)
        if cells:
            rows.append((provider, cells))

    ds = local.get("dataset", {})
    note = (
        f"Full multilingual `{ds.get('split', 'test')}` split — **F2 by language** (β=2, recall-weighted). "
        f"Local detectors run over all 60 languages; each cloud provider runs only the languages it "
        f"officially supports for PII (— = unsupported by that provider, never faked). "
        f"Columns are the 12 major languages (each >6k records); the full 60-language breakdown is in "
        f"`{args.local}`.\n"
    )
    block = note + "\n" + cards.render_language_matrix(rows, languages)
    return _apply(args.file, args.marker, block, args.dry_run)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sync_cards", description="Regenerate card leaderboard blocks.")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("block", help="replace a marker block with a full rendered leaderboard")
    b.add_argument("--results", required=True)
    b.add_argument("--file", required=True)
    b.add_argument("--marker", required=True)
    b.add_argument("--dry-run", action="store_true")
    b.set_defaults(func=_cmd_block)

    s = sub.add_parser("sanity", help="score SANITY_DETECTORS on a split and fill the SANITY marker")
    s.add_argument("--split", required=True, help="path to a .jsonl[.gz] records file")
    s.add_argument("--language", default="en")
    s.add_argument("--file", default="BASELINES.md")
    s.add_argument("--marker", default="SANITY")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=_cmd_sanity)

    m = sub.add_parser("matrix", help="replace a marker block with the by-language F2 matrix")
    m.add_argument("--local", required=True, help="fulltest-local baseline_results.json (8 local detectors)")
    m.add_argument("--cloud-glob", required=True, help="glob for the per-(provider,language) cloud shards")
    m.add_argument("--file", required=True)
    m.add_argument("--marker", required=True)
    m.add_argument("--languages", default=_DEFAULT_LANGUAGES)
    m.add_argument("--dry-run", action="store_true")
    m.set_defaults(func=_cmd_matrix)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
