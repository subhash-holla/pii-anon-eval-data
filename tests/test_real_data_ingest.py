"""FR-027 — path-activated real-data ingest for the correlation slice (cycle-1 UC-13; DC-14).

The real i2b2-2014 / TAB de-id data is NOT in this repo (licensing). The ingest seam ACTIVATES only when a
maintainer drops a DERIVED paired-score file at a configured path (env PII_ANON_REAL_DEID_PATH or an explicit
argument). Until then it returns the RealDataAbsent sentinel — NEVER a fabricated correlation. When real
derived scores ARE present it runs the audited correlate(). Raw PHI never enters the repo (derived scores only).
"""
from __future__ import annotations

import json

import pytest
from pii_anon_datasets.validation import correlation as C
from pii_anon_datasets.validation import real_data_ingest as RDI


def test_absent_path_returns_sentinel(monkeypatch) -> None:
    monkeypatch.delenv(RDI.REAL_DEID_PATH_ENV, raising=False)
    res = RDI.correlate_from_path()
    assert isinstance(res, C.RealDataAbsent)
    assert res.available is False


def test_nonexistent_configured_path_returns_sentinel(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv(RDI.REAL_DEID_PATH_ENV, str(tmp_path / "not-there.json"))
    assert RDI.resolve_real_data_path() is None
    assert isinstance(RDI.correlate_from_path(), C.RealDataAbsent)


def test_dropped_real_scores_activate_real_correlation(tmp_path) -> None:
    # a maintainer drops a DERIVED paired-score file (no raw PHI)
    f = tmp_path / "real_deid_scores.json"
    f.write_text(json.dumps({
        "synthetic": [0.1, 0.5, 0.9, 0.3, 0.7],
        "real": [0.15, 0.45, 0.95, 0.35, 0.6],
    }), encoding="utf-8")
    res = RDI.correlate_from_path(str(f), seed=1, n_boot=200)
    assert isinstance(res, C.CorrelationResult)
    assert res.n == 5
    assert "external validity" in res.caveat.lower()  # non-strippable caveat rides the real result too


def test_malformed_real_file_raises_never_fabricates(tmp_path) -> None:
    f = tmp_path / "bad.json"
    f.write_text(json.dumps({"synthetic": [0.1, 0.2], "real": [0.1]}), encoding="utf-8")  # unequal length
    with pytest.raises(ValueError):
        RDI.correlate_from_path(str(f))
