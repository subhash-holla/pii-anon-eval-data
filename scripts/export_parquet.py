#!/usr/bin/env python3
"""
Export PII-Anon dataset to Parquet format for HuggingFace Hub distribution.

Requires: pip install pyarrow

Usage:
    PYTHONPATH=. python scripts/export_parquet.py
    PYTHONPATH=. python scripts/export_parquet.py --output-dir huggingface/data
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "huggingface" / "data"


def main():
    parser = argparse.ArgumentParser(description="Export PII-Anon to Parquet")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("ERROR: pyarrow not installed. Install with: pip install pyarrow")
        sys.exit(1)

    from pii_anon_datasets import load_dataset

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for split in ["train", "dev", "test"]:
        print(f"Exporting {split} split...")
        records = load_dataset(split=split)

        # Flatten for Parquet: store annotations as JSON string
        rows = []
        for rec in records:
            row = dict(rec)
            row["annotations"] = json.dumps(rec["annotations"], ensure_ascii=False)
            row["entity_tracking"] = json.dumps(rec.get("entity_tracking"), ensure_ascii=False)
            row["adversarial"] = json.dumps(rec.get("adversarial"), ensure_ascii=False)
            row["privacy_risk"] = json.dumps(rec.get("privacy_risk"), ensure_ascii=False)
            row["query_context"] = json.dumps(rec.get("query_context"), ensure_ascii=False)
            row["provenance"] = json.dumps(rec.get("provenance"), ensure_ascii=False)
            row["dimensions"] = json.dumps(rec.get("dimensions", []), ensure_ascii=False)
            row["regulatory_domains"] = json.dumps(rec.get("regulatory_domains", []), ensure_ascii=False)
            rows.append(row)

        table = pa.Table.from_pylist(rows)
        output_path = args.output_dir / f"{split}.parquet"
        pq.write_table(table, output_path, compression="snappy")
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  {output_path.name}: {len(records)} records ({size_mb:.1f} MB)")

    # Write dataset_info.json
    info = {
        "description": "PII-Anon Evaluation Dataset v1.2.0 — Comprehensive multilingual benchmark for PII detection",
        "splits": {
            "train": {"num_examples": len(load_dataset(split="train"))},
            "dev": {"num_examples": len(load_dataset(split="dev"))},
            "test": {"num_examples": len(load_dataset(split="test"))},
        },
    }
    with open(args.output_dir / "dataset_info.json", "w") as f:
        json.dump(info, f, indent=2)

    print(f"\nParquet files written to {args.output_dir}")
    print("Ready for HuggingFace Hub upload with: huggingface-cli upload")


if __name__ == "__main__":
    main()
