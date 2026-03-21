#!/usr/bin/env python3
"""
Generate subset files from the canonical PII-Anon dataset.

Creates filtered views by dimension, domain, difficulty, and dev/test splits.
All subsets are derived from the single canonical pii_anon.jsonl file.

Usage:
    PYTHONPATH=. python scripts/generate_subsets.py
"""

import argparse
import gzip
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "src" / "pii_anon_datasets" / "data" / "pii_anon.jsonl.gz"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "src" / "pii_anon_datasets"

DIMENSIONS = ["entity_tracking", "multilingual", "context_preservation", "diverse_pii_types", "edge_cases", "format_variations", "temporal_consistency"]
DOMAINS = ["clinical", "financial", "legal", "technology"]
DIFFICULTIES = ["easy", "moderate", "hard", "challenging"]


def write_jsonl_gz(records: list[dict], output_path: Path):
    """Write records to a gzipped JSONL file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(output_path, "wt", encoding="utf-8", compresslevel=6) as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  {output_path.name}: {len(records)} records ({size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Generate PII-Anon subsets")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--dev-ratio", type=float, default=0.1, help="Dev set ratio (default 10%%)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    print(f"Reading canonical dataset: {args.input}")
    all_records = []
    opener = gzip.open if args.input.suffix == ".gz" else open
    with opener(args.input, "rt", encoding="utf-8") as f:
        for line in f:
            all_records.append(json.loads(line))
    print(f"Total records: {len(all_records)}")

    # ─── By Dimension ────────────────────────────────────────────────────
    print("\nGenerating dimension subsets...")
    dim_dir = args.output_root / "subsets" / "by_dimension"
    for dim in DIMENSIONS:
        subset = [r for r in all_records if r.get("primary_dimension") == dim]
        if subset:
            write_jsonl_gz(subset, dim_dir / f"{dim}.jsonl.gz")

    # ─── By Domain ───────────────────────────────────────────────────────
    print("\nGenerating domain subsets...")
    domain_dir = args.output_root / "subsets" / "by_domain"
    for domain in DOMAINS:
        subset = [r for r in all_records if r.get("domain") == domain]
        if subset:
            write_jsonl_gz(subset, domain_dir / f"{domain}.jsonl.gz")

    # ─── By Difficulty ───────────────────────────────────────────────────
    print("\nGenerating difficulty subsets...")
    diff_dir = args.output_root / "subsets" / "by_difficulty"
    for diff in DIFFICULTIES:
        subset = [r for r in all_records if r.get("difficulty_level") == diff]
        if subset:
            write_jsonl_gz(subset, diff_dir / f"{diff}.jsonl.gz")

    # ─── Dev/Test Splits ─────────────────────────────────────────────────
    print("\nGenerating stratified dev/test splits...")
    splits_dir = args.output_root / "splits"

    # Stratify by primary_dimension + language + difficulty
    strata: dict[str, list[dict]] = {}
    for r in all_records:
        key = f"{r.get('primary_dimension', 'unknown')}|{r.get('language', 'unknown')}|{r.get('difficulty_level', 'unknown')}"
        strata.setdefault(key, []).append(r)

    dev_records = []
    test_records = []
    for key, records in strata.items():
        random.shuffle(records)
        split_idx = max(1, int(len(records) * args.dev_ratio))
        dev_records.extend(records[:split_idx])
        test_records.extend(records[split_idx:])

    # Shuffle final sets
    random.shuffle(dev_records)
    random.shuffle(test_records)

    write_jsonl_gz(dev_records, splits_dir / "dev.jsonl.gz")
    write_jsonl_gz(test_records, splits_dir / "test.jsonl.gz")

    # Verify no overlap
    dev_ids = {r["record_id"] for r in dev_records}
    test_ids = {r["record_id"] for r in test_records}
    overlap = dev_ids & test_ids
    if overlap:
        print(f"  WARNING: {len(overlap)} records in both dev and test!")
    else:
        print(f"  No overlap between dev ({len(dev_records)}) and test ({len(test_records)})")

    # ─── Print Summary ───────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("SUBSET GENERATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"Canonical records: {len(all_records)}")
    print(f"Dev set: {len(dev_records)} ({len(dev_records)/len(all_records)*100:.1f}%)")
    print(f"Test set: {len(test_records)} ({len(test_records)/len(all_records)*100:.1f}%)")

    dim_counts = Counter(r.get("primary_dimension") for r in all_records)
    print(f"\nDimension subsets:")
    for dim in DIMENSIONS:
        count = dim_counts.get(dim, 0)
        print(f"  {dim}: {count} ({count/len(all_records)*100:.1f}%)")

    domain_counts = Counter(r.get("domain") for r in all_records)
    print(f"\nDomain subsets:")
    for domain in DOMAINS:
        count = domain_counts.get(domain, 0)
        if count > 0:
            print(f"  {domain}: {count}")


if __name__ == "__main__":
    main()
