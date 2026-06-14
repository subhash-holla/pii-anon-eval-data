"""CAP-02 — operating-point reporting (DC-27 / FR-048; NFR-046): the false-positive tax.

A detection operating-point view must show a recall-priority Fβ with β RECORDED and β ≥ 2 (committed default
β=2) OR a stated integer FN:FP cost ratio, AND a threshold-free AUPRC, AND a precision-at-fixed-recall readout
(non-null) at a recall target RECORDED in the pre-registration, AND the operating point must EQUAL the
pre-registered threshold rule (not a post-hoc single threshold). A lone F1, a free/low β with no FN:FP cost, an
absent precision-at-recall, an absent AUPRC, or an operating point that disagrees with the prereg => rejected.

The audited operating-point MATH lives in eval-data stats (pure-stdlib); the figure is lazy-matplotlib.
"""
from __future__ import annotations

import pytest
from pii_anon_datasets.assessment import report as R
from pii_anon_datasets.stats import operating_point as OP


# ---- audited operating-point math (stats/operating_point.py) ----
def test_fbeta_recall_priority() -> None:
    # beta=2 weights recall higher than precision
    assert OP.fbeta(precision=0.5, recall=1.0, beta=2.0) > OP.fbeta(precision=1.0, recall=0.5, beta=2.0)
    assert OP.fbeta(precision=0.0, recall=0.0, beta=2.0) == 0.0


def test_auprc_trapezoidal_and_degenerate_single_point() -> None:
    # full curve from (0,1) down to (1,0): area ~ 0.5
    curve = [(0.0, 1.0), (0.5, 0.5), (1.0, 0.0)]
    assert OP.auprc(curve) == pytest.approx(0.5, abs=1e-9)
    # a single (recall, precision) point (hit-only synthetic system) -> degenerate rectangle area
    assert OP.auprc([(0.8, 0.9)]) == pytest.approx(0.8 * 0.9)


def test_precision_at_recall_reads_off_curve() -> None:
    curve = [(0.2, 0.95), (0.6, 0.80), (0.9, 0.60)]
    p, reached = OP.precision_at_recall(curve, target=0.6)
    assert p == pytest.approx(0.80) and reached is True
    # target above the system's max recall -> closest (max-recall) precision, reached False, still non-null
    p2, reached2 = OP.precision_at_recall(curve, target=0.99)
    assert p2 == pytest.approx(0.60) and reached2 is False


# ---- the validated report view (report.build_operating_point_view) ----
def _prereg_dp():
    return {"beta": 2, "recall_target": 0.90, "threshold_rule": "argmax-fbeta@prereg"}


def test_valid_view_with_beta_ge_2():
    v = R.build_operating_point_view(
        precision=0.71, recall=0.93, beta=2, auprc=0.85, precision_at_recall=0.71, recall_target_reached=True,
        recall_target=0.90, fn_fp_cost=None, threshold_rule="argmax-fbeta@prereg", prereg_design_point=_prereg_dp(),
    )
    assert v.beta == 2 and v.fbeta > 0 and v.auprc == 0.85
    assert v.matches_prereg is True
    d = v.as_dict()
    assert d["precision_at_recall"] == 0.71 and d["recall_target"] == 0.90 and "fbeta" in d
    # hit-only single-point curve -> the AUPRC is the degenerate rectangle, flagged in the serialized view
    assert d["auprc_degenerate"] is True and d["n_curve_points"] == 1


def test_auprc_degeneracy_flag_clears_for_a_swept_curve():
    v = R.build_operating_point_view(
        precision=0.71, recall=0.93, beta=2, auprc=0.85, precision_at_recall=0.71, recall_target_reached=True,
        recall_target=0.90, fn_fp_cost=None, threshold_rule="argmax-fbeta@prereg", prereg_design_point=_prereg_dp(),
        n_curve_points=12,
    )
    assert v.auprc_degenerate is False and v.n_curve_points == 12


def test_lone_f1_rejected():
    # beta=1 (a lone F1) with no FN:FP cost is rejected
    with pytest.raises(ValueError):
        R.build_operating_point_view(
            precision=0.8, recall=0.8, beta=1, auprc=0.7, precision_at_recall=0.8, recall_target_reached=True,
            recall_target=0.90, fn_fp_cost=None, threshold_rule="argmax-fbeta@prereg", prereg_design_point=_prereg_dp(),
        )


def test_low_beta_allowed_with_stated_integer_fn_fp_cost():
    v = R.build_operating_point_view(
        precision=0.8, recall=0.8, beta=1, auprc=0.7, precision_at_recall=0.8, recall_target_reached=True,
        recall_target=0.90, fn_fp_cost=10, threshold_rule="argmax-fbeta@prereg", prereg_design_point=_prereg_dp(),
    )
    assert v.fn_fp_cost == 10


def test_absent_precision_at_recall_rejected():
    with pytest.raises(ValueError):
        R.build_operating_point_view(
            precision=0.8, recall=0.9, beta=2, auprc=0.7, precision_at_recall=None, recall_target_reached=True,
            recall_target=0.90, fn_fp_cost=None, threshold_rule="argmax-fbeta@prereg", prereg_design_point=_prereg_dp(),
        )


def test_absent_auprc_rejected():
    with pytest.raises(ValueError):
        R.build_operating_point_view(
            precision=0.8, recall=0.9, beta=2, auprc=None, precision_at_recall=0.8, recall_target_reached=True,
            recall_target=0.90, fn_fp_cost=None, threshold_rule="argmax-fbeta@prereg", prereg_design_point=_prereg_dp(),
        )


def test_operating_point_must_match_prereg_threshold_rule():
    # post-hoc tuned threshold (disagrees with prereg) is rejected
    with pytest.raises(ValueError):
        R.build_operating_point_view(
            precision=0.8, recall=0.9, beta=2, auprc=0.7, precision_at_recall=0.8, recall_target_reached=True,
            recall_target=0.90, fn_fp_cost=None, threshold_rule="post-hoc-best-on-eval", prereg_design_point=_prereg_dp(),
        )
    # recall target disagreeing with prereg is rejected too
    with pytest.raises(ValueError):
        R.build_operating_point_view(
            precision=0.8, recall=0.9, beta=2, auprc=0.7, precision_at_recall=0.8, recall_target_reached=True,
            recall_target=0.80, fn_fp_cost=None, threshold_rule="argmax-fbeta@prereg", prereg_design_point=_prereg_dp(),
        )


# ---- lazy-matplotlib figure (skips gracefully when matplotlib absent) ----
def test_operating_point_figure_lazy(tmp_path):
    pytest.importorskip("matplotlib")
    from pii_anon_datasets.reporting import viz
    out = viz.operating_point_curve([(0.2, 0.95), (0.6, 0.8), (0.9, 0.6)], tmp_path / "op.png",
                                    operating_point=(0.9, 0.6))
    assert out.exists()


def test_viz_has_no_toplevel_matplotlib_import():
    """NFR-050: matplotlib stays lazy — never imported at module top in reporting.viz."""
    import ast
    import pathlib
    src = pathlib.Path("src/pii_anon_datasets/reporting/viz.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    toplevel = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    names = [a.name for n in toplevel if isinstance(n, ast.Import) for a in n.names]
    mods = [n.module for n in toplevel if isinstance(n, ast.ImportFrom)]
    assert not any("matplotlib" in (m or "") for m in mods + names)
