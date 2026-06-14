"""Tests for per-cell DesignProvenance on published detection metrics (P7; FR-029, AX-003)."""
import pytest

from pii_anon_datasets.reporting import power_table
from pii_anon_datasets.scoring import DesignProvenance, Span, score_detection
from pii_anon_datasets.scoring.detection import DESIGN_CAVEAT

_CELL = {"id": "LxE:entity_type=IBAN|language=fr", "tier": "critical", "target_n": 1522}


def _g(start, end, t="IBAN"):
    return Span(start, end, t)


def test_design_provenance_absent_by_default():
    s = score_detection([_g(0, 5)], [_g(0, 5)])
    assert "design_provenance" not in s.as_dict()      # corpus-level score: back-compat unchanged


def test_design_provenance_emitted_and_ci_n_coexists_with_target():
    dp = DesignProvenance.from_cell(_CELL, observed_positives=1531)
    s = score_detection([_g(0, 5)], [_g(0, 5)], design_provenance=dp)
    d = s.as_dict()
    assert d["design_provenance"]["lattice_cell_id"] == _CELL["id"]
    assert d["design_provenance"]["tier"] == "critical"
    assert d["design_provenance"]["target_n"] == 1522
    assert d["design_provenance"]["powered"] is True
    # the AX-003 side-by-side property: CI denominator AND the cell target both present
    assert "n" in d["recall_ci"] and d["design_provenance"]["target_n"] == 1522


def test_powered_flag_matches_counts():
    assert DesignProvenance.from_cell(_CELL, 1522).powered is True
    assert DesignProvenance.from_cell(_CELL, 1521).powered is False


def test_caveat_is_non_strippable():
    with pytest.raises(ValueError):
        DesignProvenance("c", "standard", 753, 800, True, caveat="")
    assert "synthetic" in DesignProvenance.from_cell(_CELL, 1600).as_dict()["caveat"].lower()
    assert DESIGN_CAVEAT


def test_power_table_rows_always_carry_provenance_and_exclude_seam():
    lattice = {"cells": [
        {"id": "X:entity_type=IBAN", "dimensions": {"entity_type": "IBAN"}, "tier": "critical",
         "target_n": 1522, "count_gated": True, "interaction": "marginal:entity_type"},
        {"id": "DxT:domain=general|eval_family=detection", "dimensions": {"domain": "general", "eval_family": "detection"},
         "tier": "standard", "target_n": 753, "count_gated": False, "interaction": "domain_x_track"},
    ]}
    rows = power_table(lattice, {"X:entity_type=IBAN": 2000})
    assert len(rows) == 1                                   # the non-gated eval-family seam excluded
    assert rows[0]["powered"] is True
    assert rows[0]["design_provenance"]["caveat"]           # never emitted without the power statement
    assert rows[0]["power_class"] == "well_powered"


def test_power_report_renders_verdict():
    from pii_anon_datasets.reporting import power_report
    lattice = {"cells": [
        {"id": "X:entity_type=IBAN", "dimensions": {"entity_type": "IBAN"}, "tier": "critical",
         "target_n": 1522, "count_gated": True, "interaction": "marginal:entity_type"},
    ]}
    md = power_report(lattice, {"X:entity_type=IBAN": 2000})
    assert "LARGE" in md and "Power Matrix" in md
    md2 = power_report(lattice, {"X:entity_type=IBAN": 1})
    assert "SMALL" in md2
