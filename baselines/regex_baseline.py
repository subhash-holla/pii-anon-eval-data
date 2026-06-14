#!/usr/bin/env python3
"""
Regex-only PII detection baseline.

Uses regular expression patterns for common PII types. This represents the
lower bound of detection capability — no ML, no context understanding.

Usage:
    PYTHONPATH=. python baselines/regex_baseline.py
    PYTHONPATH=. python baselines/regex_baseline.py --split test_adversarial
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from baselines.evaluate import Span, evaluate_predictions, print_report, save_results
from pii_anon_datasets import load_dataset
from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

RESULTS_DIR = Path(__file__).parent / "results"

# Regex patterns for common PII types
PATTERNS = {
    "EMAIL_ADDRESS": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "PHONE_NUMBER": re.compile(r'\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'),
    "SOCIAL_SECURITY_NUMBER": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    "IP_ADDRESS": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    "CREDIT_CARD_NUMBER": re.compile(r'\b(?:\d{4}[\s-]?){3}\d{4}\b'),
    "DATE_OF_BIRTH": re.compile(r'\b\d{4}-\d{2}-\d{2}\b'),
    "IBAN": re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}(?:[A-Z0-9]?){0,16}\b'),
    "MAC_ADDRESS": re.compile(r'\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b'),
    "TIMESTAMP": re.compile(r'\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?\b'),
}


def detect_pii_regex(text: str) -> list[Span]:
    """Detect PII using regex patterns."""
    spans = []
    for entity_type, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            spans.append(Span(
                start=match.start(),
                end=match.end(),
                entity_type=entity_type,
                text=match.group(),
            ))
    return spans


# Native label -> canonical-63 type. Regex emits canonical types directly, so the map is the identity
# over PATTERNS' keys (all of which are canonical). It exists so the orchestrator can report coverage.
LABEL_MAP: dict[str, str | None] = {t: t for t in PATTERNS}


class _RegexAdapter:
    """Uniform-contract wrapper over the pure-stdlib regex detector (the recall lower bound)."""

    name = "regex"
    model_id = ""
    label_map = LABEL_MAP
    deterministic = True

    def available(self) -> bool:
        return True  # pure-stdlib — always available

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get(native)

    def build(self) -> object:
        return None  # no model to load

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        # Reuse the dev-harness detector; baselines.evaluate.Span is field-compatible with AdapterSpan.
        return [AdapterSpan(s.start, s.end, s.entity_type, s.text) for s in detect_pii_regex(text or "")]

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _RegexAdapter()


def main():
    parser = argparse.ArgumentParser(description="Regex PII detection baseline")
    parser.add_argument("--split", default="test", help="Dataset split to evaluate on")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records")
    args = parser.parse_args()

    print(f"Loading {args.split} split...")
    records = load_dataset(split=args.split)
    if args.limit:
        records = records[:args.limit]
    print(f"Loaded {len(records)} records")

    print("Running regex detection...")
    predictions = {}
    for rec in records:
        predictions[rec["record_id"]] = detect_pii_regex(rec["text"])

    print("Evaluating...")
    results = evaluate_predictions(records, predictions)
    print_report(results)
    save_results(results, RESULTS_DIR / f"regex_{args.split}.json", "regex")


if __name__ == "__main__":
    main()
