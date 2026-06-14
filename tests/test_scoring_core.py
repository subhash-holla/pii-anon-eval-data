"""Tests for scoring.core (reidx-02 integer counts; reidx-03 order-independence)."""
import random

import pytest

from pii_anon_datasets.scoring.core import (
    MATCHING_POLICY_VERSION,
    Counts,
    Span,
    match_strict,
)


def _g():
    return [Span(0, 10, "PERSON_NAME"), Span(20, 30, "EMAIL_ADDRESS"), Span(40, 45, "PHONE_NUMBER")]


def test_perfect_match_integer_counts():
    gold = _g()
    c = match_strict(gold, list(gold))
    assert (c.tp, c.fp, c.fn, c.partial) == (3, 0, 0, 0)
    assert c.n_gold == 3 and c.n_pred == 3
    # counts are integers, never fractional (reidx-02)
    assert all(isinstance(v, int) for v in (c.tp, c.fp, c.fn, c.partial))


def test_strict_miss_and_false_positive():
    gold = _g()
    pred = [Span(0, 10, "PERSON_NAME"), Span(20, 30, "PHONE_NUMBER")]  # 2nd is wrong type
    c = match_strict(gold, pred)
    assert c.tp == 1
    assert c.fn == 2
    assert c.fp == 1


def test_order_independence_reidx03():
    gold = _g()
    pred = _g()
    base = match_strict(gold, pred)
    rng = random.Random(7)
    for _ in range(8):
        shuffled = pred[:]
        rng.shuffle(shuffled)
        assert match_strict(gold, shuffled) == base  # counts independent of input order


def test_partial_overlap_counted_separately_not_as_tp():
    gold = [Span(0, 10, "PERSON_NAME")]
    pred = [Span(2, 8, "PERSON_NAME")]  # overlaps but boundaries differ → NOT strict
    c = match_strict(gold, pred)
    assert c.tp == 0
    assert c.partial == 1  # surfaced separately, will get 0.5 credit only outside CIs
    assert c.fn == 1 and c.fp == 1


def test_multiplicity_via_multiset():
    gold = [Span(0, 5, "X"), Span(0, 5, "X")]
    pred = [Span(0, 5, "X")]
    c = match_strict(gold, pred)
    assert c.tp == 1 and c.fn == 1 and c.fp == 0


def test_policy_version_stamped():
    assert match_strict(_g(), _g()).policy == MATCHING_POLICY_VERSION


def test_invalid_span_rejected():
    with pytest.raises(ValueError):
        Span(10, 5, "X")
