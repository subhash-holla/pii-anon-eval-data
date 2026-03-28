#!/usr/bin/env python3
"""
Shared evaluation harness for PII detection baselines.

Computes entity-level metrics using the SemEval 2013 evaluation protocol:
- Strict F1 (exact boundary + type match)
- Partial F1 (overlap with 0.5 credit)
- F2 score (β=2, recall-biased — recommended by Microsoft Presidio)
- Per-entity-type breakdown
- Per-domain breakdown
- Micro and macro averaging

Usage:
    from baselines.evaluate import evaluate_predictions, print_report

    results = evaluate_predictions(gold_records, predictions)
    print_report(results)
"""

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Span:
    """A detected PII span."""
    start: int
    end: int
    entity_type: str
    text: str = ""


@dataclass
class EvalResults:
    """Evaluation results container."""
    # Overall metrics
    strict_precision: float = 0.0
    strict_recall: float = 0.0
    strict_f1: float = 0.0
    strict_f2: float = 0.0
    partial_precision: float = 0.0
    partial_recall: float = 0.0
    partial_f1: float = 0.0
    # Counts
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    partial_matches: int = 0
    total_gold: int = 0
    total_predicted: int = 0
    # Per-entity-type metrics
    per_type: dict = field(default_factory=dict)
    # Per-domain metrics
    per_domain: dict = field(default_factory=dict)
    # Raw data for further analysis
    records_evaluated: int = 0


def _spans_overlap(s1: Span, s2: Span) -> bool:
    """Check if two spans overlap."""
    return s1.start < s2.end and s2.start < s1.end


def _spans_match_strict(gold: Span, pred: Span) -> bool:
    """Strict match: exact boundary + same type."""
    return (gold.start == pred.start and gold.end == pred.end and
            gold.entity_type == pred.entity_type)


def _spans_match_partial(gold: Span, pred: Span) -> float:
    """Partial match: returns overlap ratio (0.0 to 1.0) if same type."""
    if gold.entity_type != pred.entity_type:
        return 0.0
    if not _spans_overlap(gold, pred):
        return 0.0
    overlap_start = max(gold.start, pred.start)
    overlap_end = min(gold.end, pred.end)
    overlap_len = overlap_end - overlap_start
    union_len = max(gold.end, pred.end) - min(gold.start, pred.start)
    return overlap_len / union_len if union_len > 0 else 0.0


def _f_score(precision: float, recall: float, beta: float = 1.0) -> float:
    """Compute F-score with given beta."""
    if precision + recall == 0:
        return 0.0
    return (1 + beta**2) * (precision * recall) / (beta**2 * precision + recall)


def _compute_metrics(tp: int, fp: int, fn: int, partial: float = 0) -> dict:
    """Compute precision, recall, F1, F2 from counts."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = _f_score(precision, recall, beta=1.0)
    f2 = _f_score(precision, recall, beta=2.0)

    # Partial metrics
    p_precision = (tp + 0.5 * partial) / (tp + fp + partial) if (tp + fp + partial) > 0 else 0.0
    p_recall = (tp + 0.5 * partial) / (tp + fn + partial) if (tp + fn + partial) > 0 else 0.0
    p_f1 = _f_score(p_precision, p_recall, beta=1.0)

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "f2": round(f2, 4),
        "partial_precision": round(p_precision, 4),
        "partial_recall": round(p_recall, 4),
        "partial_f1": round(p_f1, 4),
        "tp": tp, "fp": fp, "fn": fn,
        "partial_matches": int(partial),
    }


def evaluate_predictions(
    gold_records: list[dict],
    predictions: dict[str, list[Span]],
) -> EvalResults:
    """Evaluate predictions against gold annotations.

    Args:
        gold_records: List of gold standard records with annotations.
        predictions: Dict mapping record_id to list of predicted Span objects.

    Returns:
        EvalResults with comprehensive metrics.
    """
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_partial = 0

    type_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "partial": 0})
    domain_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "partial": 0})

    for rec in gold_records:
        rid = rec["record_id"]
        domain = rec.get("domain", "unknown")

        gold_spans = [
            Span(a["start"], a["end"], a["entity_type"], a.get("text", ""))
            for a in rec.get("annotations", [])
        ]
        pred_spans = predictions.get(rid, [])

        # Match gold to predictions
        matched_gold = set()
        matched_pred = set()

        # Pass 1: strict matches
        for gi, gold in enumerate(gold_spans):
            for pi, pred in enumerate(pred_spans):
                if pi not in matched_pred and _spans_match_strict(gold, pred):
                    matched_gold.add(gi)
                    matched_pred.add(pi)
                    total_tp += 1
                    type_counts[gold.entity_type]["tp"] += 1
                    domain_counts[domain]["tp"] += 1
                    break

        # Pass 2: partial matches (for unmatched spans)
        for gi, gold in enumerate(gold_spans):
            if gi in matched_gold:
                continue
            best_overlap = 0.0
            best_pi = -1
            for pi, pred in enumerate(pred_spans):
                if pi in matched_pred:
                    continue
                overlap = _spans_match_partial(gold, pred)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_pi = pi
            if best_overlap > 0.0 and best_pi >= 0:
                matched_gold.add(gi)
                matched_pred.add(best_pi)
                total_partial += 1
                type_counts[gold.entity_type]["partial"] += 1
                domain_counts[domain]["partial"] += 1

        # False negatives (unmatched gold)
        for gi, gold in enumerate(gold_spans):
            if gi not in matched_gold:
                total_fn += 1
                type_counts[gold.entity_type]["fn"] += 1
                domain_counts[domain]["fn"] += 1

        # False positives (unmatched predictions)
        for pi, pred in enumerate(pred_spans):
            if pi not in matched_pred:
                total_fp += 1
                type_counts[pred.entity_type]["fp"] += 1
                domain_counts[domain]["fp"] += 1

    # Compute overall metrics
    overall = _compute_metrics(total_tp, total_fp, total_fn, total_partial)

    # Per-type metrics
    per_type = {}
    for etype, counts in sorted(type_counts.items()):
        per_type[etype] = _compute_metrics(
            counts["tp"], counts["fp"], counts["fn"], counts["partial"]
        )

    # Per-domain metrics
    per_domain = {}
    for domain, counts in sorted(domain_counts.items()):
        per_domain[domain] = _compute_metrics(
            counts["tp"], counts["fp"], counts["fn"], counts["partial"]
        )

    # Macro F1
    type_f1s = [m["f1"] for m in per_type.values() if m["tp"] + m["fn"] > 0]
    macro_f1 = sum(type_f1s) / len(type_f1s) if type_f1s else 0.0

    results = EvalResults(
        strict_precision=overall["precision"],
        strict_recall=overall["recall"],
        strict_f1=overall["f1"],
        strict_f2=overall["f2"],
        partial_precision=overall["partial_precision"],
        partial_recall=overall["partial_recall"],
        partial_f1=overall["partial_f1"],
        true_positives=total_tp,
        false_positives=total_fp,
        false_negatives=total_fn,
        partial_matches=total_partial,
        total_gold=total_tp + total_fn + total_partial,
        total_predicted=total_tp + total_fp + total_partial,
        per_type=per_type,
        per_domain=per_domain,
        records_evaluated=len(gold_records),
    )

    return results


def print_report(results: EvalResults):
    """Print a formatted evaluation report."""
    print("=" * 70)
    print("PII DETECTION EVALUATION REPORT")
    print("=" * 70)
    print(f"\nRecords evaluated: {results.records_evaluated:,}")
    print(f"Gold entities: {results.total_gold:,}")
    print(f"Predicted entities: {results.total_predicted:,}")

    print(f"\n--- Overall Metrics ---")
    print(f"Strict Precision: {results.strict_precision:.4f}")
    print(f"Strict Recall:    {results.strict_recall:.4f}")
    print(f"Strict F1:        {results.strict_f1:.4f}")
    print(f"Strict F2 (β=2):  {results.strict_f2:.4f}")
    print(f"Partial F1:       {results.partial_f1:.4f}")

    print(f"\n--- Per-Entity-Type (top 20 by support) ---")
    sorted_types = sorted(results.per_type.items(),
                          key=lambda x: x[1]["tp"] + x[1]["fn"], reverse=True)
    print(f"{'Entity Type':<35} {'Prec':>6} {'Rec':>6} {'F1':>6} {'F2':>6} {'Support':>8}")
    print("-" * 70)
    for etype, metrics in sorted_types[:20]:
        support = metrics["tp"] + metrics["fn"] + metrics["partial_matches"]
        print(f"{etype:<35} {metrics['precision']:>6.3f} {metrics['recall']:>6.3f} "
              f"{metrics['f1']:>6.3f} {metrics['f2']:>6.3f} {support:>8}")

    if results.per_domain:
        print(f"\n--- Per-Domain ---")
        print(f"{'Domain':<20} {'Prec':>6} {'Rec':>6} {'F1':>6} {'F2':>6}")
        print("-" * 45)
        for domain, metrics in sorted(results.per_domain.items()):
            print(f"{domain:<20} {metrics['precision']:>6.3f} {metrics['recall']:>6.3f} "
                  f"{metrics['f1']:>6.3f} {metrics['f2']:>6.3f}")


def save_results(results: EvalResults, output_path: Path, baseline_name: str):
    """Save results to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "baseline": baseline_name,
        "records_evaluated": results.records_evaluated,
        "overall": {
            "strict_precision": results.strict_precision,
            "strict_recall": results.strict_recall,
            "strict_f1": results.strict_f1,
            "strict_f2": results.strict_f2,
            "partial_f1": results.partial_f1,
        },
        "counts": {
            "true_positives": results.true_positives,
            "false_positives": results.false_positives,
            "false_negatives": results.false_negatives,
            "partial_matches": results.partial_matches,
        },
        "per_entity_type": results.per_type,
        "per_domain": results.per_domain,
    }
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nResults saved to {output_path}")
