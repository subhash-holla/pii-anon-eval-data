"""merge_results must refuse a heterogeneous (cross-split) merge (sp2 review).

A merged leaderboard ranks every detector's micro-F2 against every other's.
That is only valid if all inputs scored the same split/version/records — a
silent dev+test merge would forge a leaderboard (an easy-split F2 ranked
against a hard-split F2). The guard fails loud instead.
"""
from __future__ import annotations

import pytest
from pii_anon_datasets.baselines.orchestrator import merge_results
from pii_anon_datasets.baselines.results import BaselineResults


def _result(split: str, n_records: int, detector: str, f2: float) -> BaselineResults:
    return BaselineResults(
        dataset={"split": split, "dataset_version": "2.0.0", "language": "en", "n_records": n_records},
        confidence=0.95,
        ranking=[],
        detectors={
            detector: {"status": "scored", "micro": {"f2": f2}, "macro": {"f2": f2 / 2}}
        },
    )


def test_homogeneous_merge_succeeds() -> None:
    merged = merge_results(
        [_result("test", 30995, "a", 0.7), _result("test", 30995, "b", 0.9)]
    )
    assert [r["detector"] for r in merged.ranking] == ["b", "a"]


def test_cross_split_merge_is_refused() -> None:
    with pytest.raises(ValueError, match="heterogeneous merge"):
        merge_results(
            [_result("dev", 15484, "easy", 0.95), _result("test", 30995, "hard", 0.70)]
        )


def test_record_count_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="heterogeneous merge"):
        merge_results(
            [_result("test", 2000, "partial", 0.8), _result("test", 30995, "full", 0.7)]
        )
