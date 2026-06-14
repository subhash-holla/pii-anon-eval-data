"""Tests for scoring.detection (FR-001/004; M6 — scores a system's spans)."""
import pytest

from pii_anon_datasets.scoring.core import Span
from pii_anon_datasets.scoring.detection import score_detection


def test_perfect_detection():
    gold = [Span(0, 10, "PERSON_NAME"), Span(20, 30, "EMAIL_ADDRESS")]
    s = score_detection(gold, list(gold))
    assert s.precision == 1.0 and s.recall == 1.0 and s.f1 == 1.0 and s.f2 == 1.0


def test_known_pr_f1_f2():
    # 4 gold, predict 3 (2 correct, 1 wrong) → tp=2, fp=1, fn=2
    gold = [Span(i * 10, i * 10 + 5, "T") for i in range(4)]
    pred = [Span(0, 5, "T"), Span(10, 15, "T"), Span(100, 105, "T")]
    s = score_detection(gold, pred)
    assert s.precision == pytest.approx(2 / 3)
    assert s.recall == pytest.approx(2 / 4)
    assert s.f1 == pytest.approx(2 * (2 / 3) * 0.5 / ((2 / 3) + 0.5))
    # F2 weights recall higher than F1 → since recall(0.5) < precision(0.667), F2 < F1 here
    assert s.f2 < s.f1


def test_recall_ci_brackets_recall_and_uses_integer_n():
    gold = [Span(i, i + 1, "T") for i in range(100)]
    pred = gold[:98]  # recall 0.98 on n=100 gold
    s = score_detection(gold, pred)
    assert s.recall == pytest.approx(0.98)
    assert s.recall_ci.n == 100  # n_gold, an integer
    assert s.recall_ci.low < s.recall < s.recall_ci.high
    assert s.recall_ci.method == "wilson"


def test_partial_f1_separate_and_excluded_from_ci():
    gold = [Span(0, 10, "T")]
    pred = [Span(2, 8, "T")]  # partial overlap only
    s = score_detection(gold, pred)
    assert s.f1 == 0.0  # strict F1 gives no credit
    assert s.partial_f1 > 0.0  # partial F1 gives 0.5 credit, reported separately
    # the CI is computed on STRICT tp (0), not on the partial credit
    assert s.recall_ci.point == 0.0


def test_as_dict_carries_ci_method_and_note():
    s = score_detection([Span(0, 5, "T")], [Span(0, 5, "T")])
    d = s.as_dict()
    assert d["recall_ci"]["method"] == "wilson"
    assert "partial_f1" in d and "EXCLUDED" in d["_note"]
