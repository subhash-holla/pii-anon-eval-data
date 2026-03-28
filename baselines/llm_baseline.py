#!/usr/bin/env python3
"""
LLM-based PII detection baseline.

Provides evaluation scripts for LLM-based PII detection using:
- OpenAI GPT-4o / GPT-4o-mini
- Anthropic Claude 3.5 Sonnet / Claude 3 Haiku
- Open-source models via HuggingFace (Llama, Mistral)

Each LLM is prompted to identify PII spans in text, and results are
evaluated against gold annotations using the shared evaluation harness.

Usage:
    PYTHONPATH=. python baselines/llm_baseline.py --model gpt-4o-mini --limit 100
    PYTHONPATH=. python baselines/llm_baseline.py --model claude-3-haiku --split test_adversarial
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pii_anon_datasets import load_dataset
from baselines.evaluate import Span, evaluate_predictions, print_report, save_results

RESULTS_DIR = Path(__file__).parent / "results"

# Prompt template for LLM-based PII detection
DETECTION_PROMPT = """Identify all Personally Identifiable Information (PII) in the following text.

For each PII entity found, return a JSON array where each element has:
- "text": the exact text span
- "entity_type": the PII category (use types like PERSON_NAME, EMAIL_ADDRESS, PHONE_NUMBER, SOCIAL_SECURITY_NUMBER, STREET_ADDRESS, DATE_OF_BIRTH, CREDIT_CARD_NUMBER, MEDICAL_RECORD_NUMBER, IP_ADDRESS, ORGANIZATION_NAME, etc.)
- "start": character offset where the entity starts (0-indexed)
- "end": character offset where the entity ends (exclusive)

Return ONLY the JSON array, no other text.

Text:
\"\"\"
{text}
\"\"\"
"""


def parse_llm_response(response_text: str) -> list[Span]:
    """Parse LLM response into Span objects."""
    try:
        # Try to extract JSON array from response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            entities = json.loads(json_match.group())
            return [
                Span(
                    start=e.get("start", 0),
                    end=e.get("end", 0),
                    entity_type=e.get("entity_type", "UNKNOWN"),
                    text=e.get("text", ""),
                )
                for e in entities
                if isinstance(e, dict) and "text" in e
            ]
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return []


def detect_pii_openai(text: str, model: str = "gpt-4o-mini") -> list[Span]:
    """Detect PII using OpenAI API."""
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": DETECTION_PROMPT.format(text=text)}],
            temperature=0,
            max_tokens=4096,
        )
        return parse_llm_response(response.choices[0].message.content)
    except Exception as e:
        print(f"  OpenAI error: {e}")
        return []


def detect_pii_anthropic(text: str, model: str = "claude-3-haiku-20240307") -> list[Span]:
    """Detect PII using Anthropic API."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": DETECTION_PROMPT.format(text=text)}],
        )
        return parse_llm_response(response.content[0].text)
    except Exception as e:
        print(f"  Anthropic error: {e}")
        return []


MODEL_HANDLERS = {
    "gpt-4o": lambda text: detect_pii_openai(text, "gpt-4o"),
    "gpt-4o-mini": lambda text: detect_pii_openai(text, "gpt-4o-mini"),
    "claude-3-5-sonnet": lambda text: detect_pii_anthropic(text, "claude-3-5-sonnet-20241022"),
    "claude-3-haiku": lambda text: detect_pii_anthropic(text, "claude-3-haiku-20240307"),
}


def main():
    parser = argparse.ArgumentParser(description="LLM PII detection baseline")
    parser.add_argument("--model", required=True, choices=list(MODEL_HANDLERS.keys()),
                        help="LLM model to use")
    parser.add_argument("--split", default="test", help="Dataset split")
    parser.add_argument("--limit", type=int, default=100, help="Max records to evaluate (API cost control)")
    parser.add_argument("--language", default="en", help="Filter by language")
    args = parser.parse_args()

    detect_fn = MODEL_HANDLERS[args.model]

    print(f"Loading {args.split} split (language={args.language})...")
    records = load_dataset(split=args.split, language=args.language)
    if args.limit:
        records = records[:args.limit]
    print(f"Loaded {len(records)} records")

    print(f"Running {args.model} detection...")
    predictions = {}
    for i, rec in enumerate(records):
        if i % 10 == 0:
            print(f"  Processing {i+1}/{len(records)}...")
        predictions[rec["record_id"]] = detect_fn(rec["text"])

    print("Evaluating...")
    results = evaluate_predictions(records, predictions)
    print_report(results)
    save_results(results, RESULTS_DIR / f"{args.model}_{args.split}.json", args.model)


if __name__ == "__main__":
    main()
