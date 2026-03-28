#!/usr/bin/env python3
"""
Microsoft Presidio PII detection baseline.

Uses Presidio Analyzer with default configuration for English text.
Requires: pip install presidio-analyzer presidio-anonymizer spacy
          python -m spacy download en_core_web_lg

Usage:
    PYTHONPATH=. python baselines/presidio_baseline.py
    PYTHONPATH=. python baselines/presidio_baseline.py --split test_adversarial
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pii_anon_datasets import load_dataset
from baselines.evaluate import Span, evaluate_predictions, print_report, save_results

RESULTS_DIR = Path(__file__).parent / "results"

# Map Presidio entity types to our taxonomy
PRESIDIO_TO_PII_ANON = {
    "PERSON": "PERSON_NAME",
    "EMAIL_ADDRESS": "EMAIL_ADDRESS",
    "PHONE_NUMBER": "PHONE_NUMBER",
    "US_SSN": "SOCIAL_SECURITY_NUMBER",
    "CREDIT_CARD": "CREDIT_CARD_NUMBER",
    "IP_ADDRESS": "IP_ADDRESS",
    "IBAN_CODE": "IBAN",
    "US_BANK_NUMBER": "BANK_ACCOUNT_NUMBER",
    "US_PASSPORT": "PASSPORT_NUMBER",
    "US_DRIVER_LICENSE": "DRIVER_LICENSE_NUMBER",
    "LOCATION": "STREET_ADDRESS",
    "DATE_TIME": "TIMESTAMP",
    "NRP": "NATIONALITY",
    "MEDICAL_LICENSE": "NPI_NUMBER",
    "URL": "URL",
    "CRYPTO": "CRYPTOCURRENCY_ADDRESS",
    "US_ITIN": "TAX_ID",
    "UK_NHS": "HEALTH_INSURANCE_ID",
    "ORGANIZATION": "ORGANIZATION_NAME",
}


def detect_pii_presidio(text: str, analyzer, score_threshold: float = 0.5) -> list[Span]:
    """Detect PII using Presidio Analyzer."""
    results = analyzer.analyze(text=text, language="en", score_threshold=score_threshold)
    spans = []
    for result in results:
        entity_type = PRESIDIO_TO_PII_ANON.get(result.entity_type, result.entity_type)
        spans.append(Span(
            start=result.start,
            end=result.end,
            entity_type=entity_type,
            text=text[result.start:result.end],
        ))
    return spans


def main():
    parser = argparse.ArgumentParser(description="Presidio PII detection baseline")
    parser.add_argument("--split", default="test", help="Dataset split to evaluate on")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records")
    parser.add_argument("--score-threshold", type=float, default=0.5,
                        help="Minimum confidence score for detections")
    args = parser.parse_args()

    try:
        from presidio_analyzer import AnalyzerEngine
    except ImportError:
        print("ERROR: presidio-analyzer not installed.")
        print("Install with: pip install presidio-analyzer spacy")
        print("Then: python -m spacy download en_core_web_lg")
        sys.exit(1)

    print("Initializing Presidio Analyzer...")
    analyzer = AnalyzerEngine()

    print(f"Loading {args.split} split (English only)...")
    records = load_dataset(split=args.split, language="en")
    if args.limit:
        records = records[:args.limit]
    print(f"Loaded {len(records)} English records")

    print("Running Presidio detection...")
    predictions = {}
    for i, rec in enumerate(records):
        if i % 1000 == 0 and i > 0:
            print(f"  Processed {i}/{len(records)} records...")
        predictions[rec["record_id"]] = detect_pii_presidio(rec["text"], analyzer, args.score_threshold)

    print("Evaluating...")
    results = evaluate_predictions(records, predictions)
    print_report(results)
    save_results(results, RESULTS_DIR / f"presidio_{args.split}.json", "presidio")


if __name__ == "__main__":
    main()
