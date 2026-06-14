"""S4 sprint coverage-hardening for the DC-09 power-table reporter (FR-029 / NFR-003 / AX-003).

The S-PWR `reporting/power_table.py` shipped the per-cell table + matrix but its render_csv /
render_markdown / power_report(note=...) / scores-attach paths were under-tested (74% line). This
sprint is "stats/reporting COMPLETION", so these tests close the reporter's render surface. Tokened
`nfr_003` (the power-transparency reporting NFR) / `fr_029` (committed-lattice provenance).
"""
from pii_anon_datasets.reporting.power_table import (
    _power_class,
    _verdict,
    power_report,
    power_table,
    render_csv,
    render_markdown,
)
from pii_anon_datasets.stats.intervals import wilson_interval


def _lattice() -> dict:
    """Tiny committed lattice: 2 count-gated cells (one powered, one under) + 1 non-gated (skipped)."""
    return {
        "cells": [
            {"id": "M:entity_type=IBAN", "dimensions": (("entity_type", "IBAN"),), "tier": "critical",
             "target_n": 1522, "count_gated": True, "interaction": "marginal:entity_type"},
            {"id": "LxE:entity_type=EMAIL|language=fr", "dimensions": (("entity_type", "EMAIL"), ("language", "fr")),
             "tier": "standard", "target_n": 753, "count_gated": True, "interaction": "language_x_entity_type"},
            {"id": "RRS:seam", "dimensions": (("track", "rrs"),), "tier": "standard",
             "target_n": 753, "count_gated": False, "interaction": "rrs_seam"},
        ]
    }


class _Score:
    """Minimal DetectionScore-shaped stub: a measured recall + a real Wilson CI."""
    recall = 0.98
    recall_ci = wilson_interval(98, 100)


def test_nfr_003_power_table_skips_non_gated_and_attaches_scores():
    lattice = _lattice()
    observed = {"M:entity_type=IBAN": 1600, "LxE:entity_type=EMAIL|language=fr": 400}
    rows = power_table(lattice, observed, scores={"M:entity_type=IBAN": _Score()})
    # the non-count-gated RRS seam cell is excluded; 2 gated cells remain, sorted by id
    assert [r["cell_id"] for r in rows] == ["LxE:entity_type=EMAIL|language=fr", "M:entity_type=IBAN"]
    # every row carries non-strippable design provenance (AX-003)
    assert all("design_provenance" in r for r in rows)
    iban = next(r for r in rows if r["cell_id"] == "M:entity_type=IBAN")
    assert iban["powered"] is True and iban["power_class"] == "well_powered"
    # the scored cell got its recall + Wilson CI attached
    assert iban["recall"] == 0.98 and iban["recall_ci"]["method"] == "wilson"
    email = next(r for r in rows if r["cell_id"].startswith("LxE:"))
    assert email["powered"] is False and email["power_class"] == "under_powered"
    assert "recall" not in email   # not in scores → no measured recall attached


def test_nfr_003_render_csv_and_markdown_roundtrip():
    rows = power_table(_lattice(), {"M:entity_type=IBAN": 1600, "LxE:entity_type=EMAIL|language=fr": 400})
    csv_out = render_csv(rows)
    assert csv_out.startswith("cell_id,tier,target_n,observed_positives,power_class,powered")
    assert len(csv_out.strip().splitlines()) == 1 + len(rows)        # header + one row per cell
    md = render_markdown(rows)
    assert md.startswith("| cell | tier | target | observed | class |")
    assert md.count("\n| ") >= len(rows)
    # max_rows truncates the body
    md1 = render_markdown(rows, max_rows=1)
    assert md1.count("| M:") + md1.count("| LxE:") == 1


def test_fr_029_power_report_note_and_claim_ladder():
    report = power_report(_lattice(), {"M:entity_type=IBAN": 1600, "LxE:entity_type=EMAIL|language=fr": 400},
                          title="S4 test matrix", note="_synthetic fixture_")
    assert "# S4 test matrix" in report
    assert "_synthetic fixture_" in report                          # the note path (line 101)
    assert "By named interaction" in report and "By risk tier" in report
    assert "Claim ladder" in report and "not external" in report     # the non-strippable caveat
    # 1 well-powered of 2 committed → 50% → SMALL overall verdict
    assert "overall verdict: **SMALL**" in report


def test_nfr_003_verdict_ladder_and_power_class_edges():
    # the claim-ladder thresholds (covers the EMPTY/LARGE/ADEQUATE/SMALL branches)
    assert _verdict(0, 0) == "EMPTY"
    assert _verdict(10, 10) == "LARGE"
    assert _verdict(8, 10) == "ADEQUATE"
    assert _verdict(1, 10) == "SMALL"
    # power-class edges
    assert _power_class(0, 753) == "empty"
    assert _power_class(700, 753) == "under_powered"
    assert _power_class(800, 753) == "well_powered"
