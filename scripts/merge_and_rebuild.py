#!/usr/bin/env python3
"""
Merge the migrated v2 canonical dataset with newly generated records,
then rebuild the compressed canonical file and metadata.

Usage:
    python scripts/merge_and_rebuild.py
"""

import gzip
import json
import hashlib
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "pii_anon_datasets" / "data"
CANONICAL_GZ = DATA_DIR / "pii_anon_v2.jsonl.gz"
GENERATED = DATA_DIR / "pii_anon_v2_generated.jsonl"
OUTPUT_JSONL = DATA_DIR / "pii_anon_v2.jsonl"
OUTPUT_GZ = DATA_DIR / "pii_anon_v2.jsonl.gz"
METADATA = DATA_DIR / "pii_anon_v2.metadata.json"


def content_hash(record: dict) -> str:
    """Hash text + annotations for deduplication."""
    text = record.get("text", "")
    anns = json.dumps(
        [(a["entity_type"], a["start"], a["end"]) for a in record.get("annotations", [])],
        sort_keys=True,
    )
    return hashlib.sha256(f"{text}|{anns}".encode()).hexdigest()


def main():
    # 1. Load existing canonical records — only keep v1 migrated records
    print("Loading existing canonical dataset (v1 migrated only)...")
    existing = []
    skipped_gen = 0
    with gzip.open(CANONICAL_GZ, "rt", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("provenance", {}).get("v1_record_id"):
                existing.append(rec)
            else:
                skipped_gen += 1
    print(f"  Loaded {len(existing)} v1 migrated records (skipped {skipped_gen} previously generated)")

    # 2. Load generated records
    print("Loading generated records...")
    generated = []
    with open(GENERATED, "r", encoding="utf-8") as f:
        for line in f:
            generated.append(json.loads(line))
    print(f"  Loaded {len(generated)} generated records")

    # 3. Deduplicate by content hash
    print("Deduplicating...")
    seen_hashes = set()
    merged = []
    for rec in existing + generated:
        h = content_hash(rec)
        if h not in seen_hashes:
            seen_hashes.add(h)
            merged.append(rec)
    print(f"  Merged: {len(merged)} unique records (removed {len(existing) + len(generated) - len(merged)} duplicates)")

    # 4. Write uncompressed JSONL
    print("Writing uncompressed JSONL...")
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for rec in merged:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 5. Write compressed
    print("Writing compressed JSONL.gz...")
    with gzip.open(OUTPUT_GZ, "wt", encoding="utf-8") as f:
        for rec in merged:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 6. Build metadata
    print("Building metadata...")
    dim_counts = Counter(r["primary_dimension"] for r in merged)
    lang_counts = Counter(r["language"] for r in merged)
    domain_counts = Counter(r["domain"] for r in merged)
    diff_counts = Counter(r["difficulty_level"] for r in merged)
    entity_type_counts = Counter()
    category_counts = Counter()
    total_annotations = 0
    for r in merged:
        for a in r["annotations"]:
            entity_type_counts[a["entity_type"]] += 1
            category_counts[a["category"]] += 1
            total_annotations += 1

    script_counts = Counter(r.get("script", "unknown") for r in merged)
    data_type_counts = Counter(r.get("data_type", "unknown") for r in merged)

    metadata = {
        "version": "2.0.0",
        "total_records": len(merged),
        "total_annotations": total_annotations,
        "entity_types": len(entity_type_counts),
        "entity_categories": len(category_counts),
        "languages": len(lang_counts),
        "writing_scripts": len(script_counts),
        "evaluation_dimensions": len(dim_counts),
        "distributions": {
            "by_dimension": dict(dim_counts.most_common()),
            "by_language": dict(lang_counts.most_common()),
            "by_domain": dict(domain_counts.most_common()),
            "by_difficulty": dict(diff_counts.most_common()),
            "by_entity_type": dict(entity_type_counts.most_common()),
            "by_category": dict(category_counts.most_common()),
            "by_script": dict(script_counts.most_common()),
            "by_data_type": dict(data_type_counts.most_common()),
        },
    }

    with open(METADATA, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # 7. Print summary
    print(f"\n{'='*60}")
    print(f"MERGED DATASET SUMMARY")
    print(f"{'='*60}")
    print(f"Total records:     {len(merged):,}")
    print(f"Total annotations: {total_annotations:,}")
    print(f"Entity types:      {len(entity_type_counts)}")
    print(f"Languages:         {len(lang_counts)}")
    print(f"Writing scripts:   {len(script_counts)}")
    print(f"\nDimension distribution:")
    for d, c in dim_counts.most_common():
        pct = c / len(merged) * 100
        print(f"  {d:30s} {c:>6,} ({pct:.1f}%)")
    print(f"\nDomain distribution:")
    for d, c in domain_counts.most_common():
        pct = c / len(merged) * 100
        print(f"  {d:30s} {c:>6,} ({pct:.1f}%)")
    print(f"\nTop 15 entity types:")
    for t, c in entity_type_counts.most_common(15):
        print(f"  {t:30s} {c:>8,}")

    # Clean up generated file
    print(f"\nCleaning up {GENERATED}...")
    GENERATED.unlink()

    # Clean up uncompressed JSONL (gitignored)
    if OUTPUT_JSONL.exists():
        OUTPUT_JSONL.unlink()

    print("Done!")


if __name__ == "__main__":
    main()
