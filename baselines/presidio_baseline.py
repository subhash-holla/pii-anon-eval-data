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
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from baselines.evaluate import Span, evaluate_predictions, print_report, save_results
from pii_anon_datasets import load_dataset
from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

RESULTS_DIR = Path(__file__).parent / "results"

# Native Presidio entity type -> canonical-63 type, or None to DROP. This is the ONE canonical Presidio
# crosswalk (the dev `score` path and the published `baselines` path share it), reconciled to the audited
# pii-rate-elo map (re-implemented, not imported). Corrections vs the prior eval-data map: LOCATION ->
# LOCATION_NAME (was STREET_ADDRESS — Presidio LOCATION is a place name), DATE_TIME -> DATE_OF_BIRTH (was
# TIMESTAMP), NRP -> None (was NATIONALITY — NRP conflates nationality/religion/politics, too coarse),
# MEDICAL_LICENSE -> DEA_NUMBER (was NPI_NUMBER). Both US_BANK_NUMBER (the real Presidio label) and the
# sister's US_BANK_ACCOUNT_NUMBER are mapped so the crosswalk is robust to either.
LABEL_MAP: dict[str, str | None] = {
    "PERSON": "PERSON_NAME",
    "EMAIL_ADDRESS": "EMAIL_ADDRESS",
    "PHONE_NUMBER": "PHONE_NUMBER",
    "LOCATION": "LOCATION_NAME",
    "GPE": "LOCATION_NAME",
    "ADDRESS": "STREET_ADDRESS",
    "ORGANIZATION": "ORGANIZATION_NAME",
    "ORG": "ORGANIZATION_NAME",
    "NRP": None,
    "IP_ADDRESS": "IP_ADDRESS",
    "URL": "URL",
    "DOMAIN_NAME": "URL",
    "CREDIT_CARD": "CREDIT_CARD_NUMBER",
    "CRYPTO": "CRYPTOCURRENCY_ADDRESS",
    "IBAN_CODE": "IBAN",
    "US_BANK_NUMBER": "BANK_ACCOUNT_NUMBER",
    "US_BANK_ACCOUNT_NUMBER": "BANK_ACCOUNT_NUMBER",
    "US_SSN": "SOCIAL_SECURITY_NUMBER",
    "US_ITIN": "TAX_ID",
    "US_DRIVER_LICENSE": "DRIVER_LICENSE_NUMBER",
    "US_PASSPORT": "PASSPORT_NUMBER",
    "DATE_TIME": "DATE_OF_BIRTH",
    "MEDICAL_LICENSE": "DEA_NUMBER",
    "IN_PAN": "TAX_ID",
    "IN_AADHAAR": "NATIONAL_ID_NUMBER",
    "SG_NRIC_FIN": "NATIONAL_ID_NUMBER",
    "AU_TFN": "TAX_ID",
    "UK_NHS": "HEALTH_INSURANCE_ID",
}


def detect_pii_presidio(text: str, analyzer, score_threshold: float = 0.5) -> list[Span]:
    """Detect PII using Presidio Analyzer; map to the canonical taxonomy and DROP unmapped types
    (never pass a native label through — the audited canonical-purity contract, DX-02)."""
    results = analyzer.analyze(text=text, language="en", score_threshold=score_threshold)
    spans = []
    for result in results:
        entity_type = LABEL_MAP.get(result.entity_type)
        if entity_type is None:
            continue
        spans.append(Span(
            start=result.start,
            end=result.end,
            entity_type=entity_type,
            text=text[result.start:result.end],
        ))
    return spans


class _PresidioAdapter:
    """Uniform-contract wrapper over Presidio (reuses :func:`detect_pii_presidio`; threshold 0.0 = take all
    detections, since the leaderboard reports precision + recall together)."""

    name = "presidio"
    model_id = "presidio-analyzer"
    label_map = LABEL_MAP
    deterministic = True

    def available(self) -> bool:
        return importlib.util.find_spec("presidio_analyzer") is not None

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get((native or "").strip().upper())

    def build(self) -> object:
        try:
            from presidio_analyzer import AnalyzerEngine
        except ImportError as e:  # pragma: no cover - exercised only on a lib-less checkout
            raise RuntimeError('presidio-analyzer not installed — pip install -e ".[baselines]"') from e
        return AnalyzerEngine()

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        return [AdapterSpan(s.start, s.end, s.entity_type, s.text) for s in detect_pii_presidio(text or "", model, 0.0)]

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _PresidioAdapter()


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
