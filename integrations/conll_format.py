#!/usr/bin/env python3
"""
Export PII-Anon dataset to CoNLL BIO/BILOU format.

CoNLL format is the lingua franca for NER — compatible with spaCy, Flair,
HuggingFace token classification, and most NER training frameworks.

Output format (tab-separated):
    token    BIO_tag

Sentences are separated by blank lines.

Usage:
    PYTHONPATH=. python integrations/conll_format.py --split train --output data/train.conll
    PYTHONPATH=. python integrations/conll_format.py --split test --format bilou
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pii_anon_datasets import load_dataset

REPO_ROOT = Path(__file__).resolve().parent.parent


def _tokenize_simple(text: str) -> list[tuple[str, int, int]]:
    """Simple whitespace tokenizer that preserves character offsets.

    Returns list of (token, start_offset, end_offset).
    """
    tokens = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        start = i
        while i < len(text) and not text[i].isspace():
            i += 1
        tokens.append((text[start:i], start, i))
    return tokens


def _assign_bio_tags(
    tokens: list[tuple[str, int, int]],
    annotations: list[dict],
) -> list[str]:
    """Assign BIO tags to tokens based on character-offset annotations."""
    tags = ["O"] * len(tokens)

    for ann in annotations:
        ann_start = ann["start"]
        ann_end = ann["end"]
        entity_type = ann["entity_type"]
        first_token = True

        for ti, (token_text, tok_start, tok_end) in enumerate(tokens):
            # Token overlaps with annotation
            if tok_start < ann_end and tok_end > ann_start:
                if first_token:
                    tags[ti] = f"B-{entity_type}"
                    first_token = False
                else:
                    tags[ti] = f"I-{entity_type}"

    return tags


def _bio_to_bilou(tokens: list[tuple[str, int, int]], bio_tags: list[str]) -> list[str]:
    """Convert BIO tags to BILOU (Begin, Inside, Last, Outside, Unit)."""
    bilou_tags = list(bio_tags)
    n = len(bilou_tags)

    for i in range(n):
        tag = bilou_tags[i]
        if tag == "O":
            continue

        prefix, entity = tag.split("-", 1)
        next_tag = bilou_tags[i + 1] if i + 1 < n else "O"
        next_is_inside = next_tag.startswith(f"I-{entity}")

        if prefix == "B":
            if next_is_inside:
                bilou_tags[i] = f"B-{entity}"  # stays B
            else:
                bilou_tags[i] = f"U-{entity}"  # single-token entity
        elif prefix == "I":
            if next_is_inside:
                bilou_tags[i] = f"I-{entity}"  # stays I
            else:
                bilou_tags[i] = f"L-{entity}"  # last token

    return bilou_tags


def record_to_conll(
    record: dict,
    format: str = "bio",
) -> str:
    """Convert a single record to CoNLL format.

    Args:
        record: A PII-Anon record dict.
        format: "bio" or "bilou".

    Returns:
        CoNLL-formatted string for this record.
    """
    text = record["text"]
    annotations = record.get("annotations", [])

    # Split into sentences (simple newline-based)
    lines_output = []
    sentences = text.split("\n")

    global_offset = 0
    for sentence in sentences:
        if not sentence.strip():
            global_offset += len(sentence) + 1  # +1 for the newline
            continue

        # Tokenize the sentence
        tokens = _tokenize_simple(sentence)

        # Adjust offsets to be global
        global_tokens = [(t, s + global_offset, e + global_offset) for t, s, e in tokens]

        if global_tokens:
            # Assign BIO tags
            bio_tags = _assign_bio_tags(global_tokens, annotations)

            if format == "bilou":
                tags = _bio_to_bilou(global_tokens, bio_tags)
            else:
                tags = bio_tags

            for (token_text, _, _), tag in zip(global_tokens, tags):
                lines_output.append(f"{token_text}\t{tag}")
            lines_output.append("")  # blank line between sentences

        global_offset += len(sentence) + 1

    return "\n".join(lines_output)


def export_conll(
    records: list[dict],
    output_path: Path,
    format: str = "bio",
):
    """Export records to a CoNLL file.

    Args:
        records: List of PII-Anon records.
        output_path: Path to write the CoNLL file.
        format: "bio" or "bilou".
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for i, rec in enumerate(records):
            if i > 0:
                f.write("\n")  # double blank line between documents
            conll = record_to_conll(rec, format=format)
            f.write(conll)
            if i % 5000 == 0 and i > 0:
                print(f"  Exported {i}/{len(records)} records...")

    print(f"Wrote {len(records)} records to {output_path}")

    # Compute stats
    entity_tags = set()
    with open(output_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and "\t" in line:
                _, tag = line.rsplit("\t", 1)
                if tag != "O":
                    entity_tags.add(tag.split("-", 1)[1])
    print(f"Entity types in output: {len(entity_tags)}")


def _build_label2id(records: list[dict]) -> dict[str, int]:
    """Build label2id mapping from records for HuggingFace compatibility."""
    entity_types = set()
    for rec in records:
        for ann in rec.get("annotations", []):
            entity_types.add(ann["entity_type"])

    labels = ["O"]
    for etype in sorted(entity_types):
        labels.append(f"B-{etype}")
        labels.append(f"I-{etype}")

    return {label: i for i, label in enumerate(labels)}


def main():
    parser = argparse.ArgumentParser(description="Export PII-Anon to CoNLL format")
    parser.add_argument("--split", default="train", help="Dataset split")
    parser.add_argument("--output", type=Path, default=None, help="Output file path")
    parser.add_argument("--format", choices=["bio", "bilou"], default="bio",
                        help="Tagging format (default: bio)")
    parser.add_argument("--language", default=None, help="Filter by language code")
    parser.add_argument("--limit", type=int, default=None, help="Limit records")
    parser.add_argument("--label2id", action="store_true",
                        help="Also output label2id.json for HuggingFace")
    args = parser.parse_args()

    if args.output is None:
        args.output = REPO_ROOT / "integrations" / "output" / f"{args.split}.{args.format}.conll"

    print(f"Loading {args.split} split...")
    kwargs = {"split": args.split}
    if args.language:
        kwargs["language"] = args.language
    records = load_dataset(**kwargs)
    if args.limit:
        records = records[:args.limit]
    print(f"Loaded {len(records)} records")

    export_conll(records, args.output, format=args.format)

    if args.label2id:
        import json
        label2id = _build_label2id(records)
        label2id_path = args.output.parent / "label2id.json"
        with open(label2id_path, "w") as f:
            json.dump(label2id, f, indent=2)
        print(f"Wrote {len(label2id)} labels to {label2id_path}")


if __name__ == "__main__":
    main()
