"""CAP-02 S10 — audited report projection (DC-22/26/28). The academic heart, eval-data side.

Given per-system ALIGNED recall-hit vectors (the OutcomeDTO) + optional Elo/RD, the projection computes every
published number with the AUDITED stats ring ONLY (intervals + paired + multitest — never pii-rate-elo's
fabricated significance): per-system recall + Wilson/Clopper-Pearson CI (interval-selection rule), adjacent-pair
McNemar + paired-bootstrap Δ (the rank oracle), Holm across the confirmatory family, tie-gating, and the
non-strippable synthetic-only caveat + honest-verdict bundle (RD-NOT-CONVERGED etc.). Deterministic (seeded).
"""
from __future__ import annotations

import pytest
from pii_anon_datasets.assessment import report as R


def _outcome(name: str, hits: list[bool], elo: float | None = None, rd: float | None = None):
    return R.SystemOutcome(name=name, hits=tuple(hits), elo=elo, rd=rd)


def test_recall_and_ci_per_system() -> None:
    # 8/10 recalled -> recall 0.8; n>=small_n_cutoff(15)? n=10<15 -> Clopper-Pearson selected
    rep = R.build_leaderboard([_outcome("A", [True] * 8 + [False] * 2)], seed=1, small_n_cutoff=15)
    row = rep.rows[0]
    assert row.system == "A"
    assert row.recall == pytest.approx(0.8)
    assert row.recall_ci_method == "clopper-pearson"  # n=10 < cutoff
    assert 0.0 <= row.recall_ci_low <= 0.8 <= row.recall_ci_high <= 1.0


def test_interval_selection_wilson_above_cutoff() -> None:
    rep = R.build_leaderboard([_outcome("A", [True] * 16 + [False] * 4)], seed=1, small_n_cutoff=15)
    assert rep.rows[0].recall_ci_method == "wilson"  # n=20 >= cutoff


def test_ranked_descending_by_recall() -> None:
    rep = R.build_leaderboard(
        [_outcome("low", [True] * 3 + [False] * 7), _outcome("high", [True] * 9 + [False] * 1)],
        seed=1,
    )
    assert [r.system for r in rep.rows] == ["high", "low"]
    assert rep.rows[0].rank == 1 and rep.rows[1].rank == 2


def test_adjacent_pair_has_mcnemar_and_paired_delta() -> None:
    # A clearly better than B on the SAME positives -> a paired verdict exists
    a = [True] * 18 + [False] * 2
    b = [True] * 6 + [False] * 14
    rep = R.build_leaderboard([_outcome("A", a), _outcome("B", b)], seed=7)
    assert len(rep.pair_verdicts) == 1
    pv = rep.pair_verdicts[0]
    assert {pv.system_a, pv.system_b} == {"A", "B"}
    assert 0.0 <= pv.mcnemar_p <= 1.0
    assert 0.0 <= pv.mcnemar_p_holm <= 1.0
    assert pv.delta_recall == pytest.approx(0.6)
    assert pv.delta_ci_low <= pv.delta_recall <= pv.delta_ci_high
    assert pv.significant is True


def test_identical_systems_not_significant_tie() -> None:
    same = [True] * 10 + [False] * 10
    rep = R.build_leaderboard([_outcome("A", list(same)), _outcome("B", list(same))], seed=3)
    pv = rep.pair_verdicts[0]
    assert pv.significant is False  # b=c=0 discordant -> p=1.0
    assert rep.rows[0].tie_group == rep.rows[1].tie_group  # grouped as a tie


def test_holm_applied_across_confirmatory_family() -> None:
    # 3 systems -> 2 adjacent pairs -> Holm family size 2; holm p >= raw p
    rep = R.build_leaderboard(
        [_outcome("A", [True] * 18 + [False] * 2), _outcome("B", [True] * 12 + [False] * 8),
         _outcome("C", [True] * 4 + [False] * 16)],
        seed=5,
    )
    assert rep.holm_family_size == 2
    for pv in rep.pair_verdicts:
        assert pv.mcnemar_p_holm + 1e-12 >= pv.mcnemar_p


def test_non_strippable_synthetic_caveat_always_present() -> None:
    rep = R.build_leaderboard([_outcome("A", [True] * 5 + [False] * 5)], seed=1)
    assert "synthetic" in rep.caveat.lower()
    assert any("synthetic" in f.lower() for f in rep.honest_flags)


def test_rd_not_converged_flag() -> None:
    rep = R.build_leaderboard(
        [_outcome("A", [True] * 9 + [False], elo=1550.0, rd=180.0),
         _outcome("B", [True] * 5 + [False] * 5, elo=1450.0, rd=60.0)],
        seed=1, rd_threshold=100.0,
    )
    assert any("RD-NOT-CONVERGED" in f or "not-converged" in f.lower() for f in rep.honest_flags)
    assert rep.converged is False


def test_converged_when_all_rd_below_threshold() -> None:
    rep = R.build_leaderboard(
        [_outcome("A", [True] * 9 + [False], elo=1550.0, rd=40.0),
         _outcome("B", [True] * 5 + [False] * 5, elo=1450.0, rd=55.0)],
        seed=1, rd_threshold=100.0,
    )
    assert rep.converged is True


def test_deterministic_seeded() -> None:
    sys_ = [_outcome("A", [True] * 14 + [False] * 6), _outcome("B", [True] * 9 + [False] * 11)]
    r1 = R.build_leaderboard(sys_, seed=42)
    r2 = R.build_leaderboard(sys_, seed=42)
    assert r1.as_dict() == r2.as_dict()


def test_requires_aligned_hit_vectors() -> None:
    with pytest.raises(ValueError):
        R.build_leaderboard([_outcome("A", [True, False]), _outcome("B", [True])], seed=1)


def test_empty_systems_rejected() -> None:
    with pytest.raises(ValueError):
        R.build_leaderboard([], seed=1)


def test_as_dict_carries_caveat_and_flags() -> None:
    rep = R.build_leaderboard([_outcome("A", [True] * 5 + [False] * 5)], seed=1)
    d = rep.as_dict()
    assert d["caveat"] == rep.caveat
    assert "rows" in d and "pair_verdicts" in d and "honest_flags" in d
