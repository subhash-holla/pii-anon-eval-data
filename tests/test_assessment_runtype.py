"""CAP-02 — run-type rigor-bar ENFORCEMENT (NFR-025/033/034).

The committed run-type selects a rigor bar (config `run_types`): smoke/dev -> "suppressed",
leaderboard-submission/filing-grade -> "full-AX005". A full-corpus run carries
`inferential_target="descriptive-census"`. Under EITHER a suppressed rigor bar OR a descriptive census,
the audited report must OMIT confidence-interval and p-value fields (no inferential claims) and instead
surface an explicit, non-strippable suppression note — while still reporting point-estimate recall + the
power verdict (NFR-025: full-corpus census is no-CI by default; NFR-033/034: run-type scope, smoke inert).

These tests pin the enforcement: today the report ALWAYS emits CIs + Holm p-values; the default
(unspecified rigor bar) MUST stay full-bar so the existing leaderboard behavior is unchanged.
"""
from __future__ import annotations

from pii_anon_datasets.assessment import report as R


def _o(name: str, hits: list[bool], elo: float | None = None, rd: float | None = None):
    return R.SystemOutcome(name=name, hits=tuple(hits), elo=elo, rd=rd)


def _systems():
    return [_o("A", [True] * 18 + [False] * 2), _o("B", [True] * 6 + [False] * 14)]


# ---- canonical run-type -> rigor-bar mapping (mirrors configs/assessment.yaml run_types) ----
def test_rigor_bar_for_run_type_mapping() -> None:
    assert R.rigor_bar_for_run_type("smoke") == "suppressed"
    assert R.rigor_bar_for_run_type("dev") == "suppressed"
    assert R.rigor_bar_for_run_type("leaderboard-submission") == "full-AX005"
    assert R.rigor_bar_for_run_type("filing-grade") == "full-AX005"


# ---- default (unspecified) stays FULL BAR — regression guard for the existing leaderboard ----
def test_default_is_full_bar_emits_ci_and_pvalues() -> None:
    rep = R.build_leaderboard(_systems(), seed=7)
    assert rep.inferential_suppressed is False
    assert rep.rows[0].recall_ci_low is not None
    assert rep.rows[0].recall_ci_method in ("wilson", "clopper-pearson")
    assert len(rep.pair_verdicts) == 1
    d = rep.as_dict()
    assert "recall_ci" in d["rows"][0] and "recall_ci_method" in d["rows"][0]
    assert len(d["pair_verdicts"]) == 1


def test_full_ax005_superpopulation_keeps_full_bar() -> None:
    rep = R.build_leaderboard(_systems(), seed=7, rigor_bar="full-AX005",
                              inferential_target="super-population")
    assert rep.inferential_suppressed is False
    assert rep.rows[0].recall_ci_low is not None
    assert len(rep.pair_verdicts) == 1


# ---- suppressed rigor bar (smoke/dev): omit CI + p-value fields, add a non-strippable note ----
def test_suppressed_rigor_bar_omits_ci_and_pvalues() -> None:
    rep = R.build_leaderboard(_systems(), seed=7, rigor_bar="suppressed")
    assert rep.inferential_suppressed is True
    # point estimate stays; CI is None (never fabricated)
    assert rep.rows[0].recall == rep.rows[0].recall  # present
    assert rep.rows[0].recall_ci_low is None and rep.rows[0].recall_ci_high is None
    assert rep.rows[0].recall_ci_method == "suppressed"
    # no pairwise inference under suppression
    assert rep.pair_verdicts == ()
    assert all(r.tie_group == 0 for r in rep.rows)
    # serialized form OMITS the CI + p-value keys
    d = rep.as_dict()
    assert "recall_ci" not in d["rows"][0] and "recall_ci_method" not in d["rows"][0]
    assert d["pair_verdicts"] == []
    # explicit, non-strippable suppression note naming the NFRs + the reason
    assert any("SUPPRESSED" in f and "NFR-025" in f for f in rep.honest_flags)


# ---- full-corpus descriptive census suppresses even at a full rigor bar (NFR-025) ----
def test_descriptive_census_suppresses_even_with_full_bar() -> None:
    rep = R.build_leaderboard(_systems(), seed=7, rigor_bar="full-AX005",
                              inferential_target="descriptive-census")
    assert rep.inferential_suppressed is True
    assert rep.rows[0].recall_ci_low is None
    assert rep.pair_verdicts == ()
    assert any("descriptive-census" in f or "census" in f.lower() for f in rep.honest_flags)


def test_as_dict_exposes_rigor_fields() -> None:
    rep = R.build_leaderboard(_systems(), seed=7, rigor_bar="suppressed")
    d = rep.as_dict()
    assert d["rigor_bar"] == "suppressed"
    assert d["inferential_target"] == "super-population"
    assert d["inferential_suppressed"] is True


def test_synthetic_caveat_survives_suppression() -> None:
    """Suppressing inference must NOT strip the synthetic-only caveat (AX-001 rides regardless)."""
    rep = R.build_leaderboard(_systems(), seed=7, rigor_bar="suppressed")
    assert "synthetic" in rep.caveat.lower()
    assert any("synthetic" in f.lower() for f in rep.honest_flags)
