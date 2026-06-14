"""CAP-02 P1 run-path integrity (DC-22 / NFR-019/020/050) — S8 precondition gate (eval-data side).

P1 (SHOWSTOPPER): the assessment run path computes ALL inference with the AUDITED eval-data stats; the
fabricated ``pii_rate_elo_pipeline.analysis.significance`` must never be on the call graph. This file pins
the two eval-data-side predicates that are testable in S8 (the full static-AST closure over the pii-rate-elo
assessment entrypoint completes in S10 when that entrypoint exists):

  (1) NFR-020 fabrication ban — the three verified fabrication signatures appear in significance.py
      (positive control: the lint actually detects them) and are ABSENT from the audited stats ring
      (negative control: intervals / paired / multitest / power are clean).
  (2) FORBIDDEN EDGE — importing ``pii_anon_datasets.assessment`` must NOT pull in pii_rate_elo_pipeline
      (the one-way dependency: eval-data OWNS, never imports the consumer — D5 §4.5).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from pii_anon_datasets.assessment._guards import scan_for_fabricated_stats

_EVAL_ROOT = Path(__file__).resolve().parents[1]
_STATS = _EVAL_ROOT / "src" / "pii_anon_datasets" / "stats"
_AUDITED = [_STATS / f"{m}.py" for m in ("intervals", "paired", "multitest", "power")]
_SIGNIFICANCE = (
    _EVAL_ROOT.parent
    / "pii-anon-research-paper"
    / "pii-rate-elo-pipeline"
    / "src"
    / "pii_rate_elo_pipeline"
    / "analysis"
    / "significance.py"
)


def test_lint_detects_fabricated_significance() -> None:
    """Positive control: the fabricated SignificanceTester signatures are detected where they live."""
    if not _SIGNIFICANCE.exists():
        pytest.skip("pii-rate-elo significance.py not present in this checkout")
    matches = scan_for_fabricated_stats([_SIGNIFICANCE])
    assert matches, "fabrication lint failed to detect known-fabricated significance.py signatures"


def test_audited_stats_ring_is_clean() -> None:
    """Negative control: the audited stats ring contains none of the fabrication signatures (NFR-020)."""
    matches = scan_for_fabricated_stats(_AUDITED)
    assert matches == [], f"fabrication signatures found in the audited stats ring: {matches}"


def test_assessment_package_does_not_import_consumer() -> None:
    """FORBIDDEN EDGE: importing the eval-data assessment package must not import pii_rate_elo_pipeline."""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(_EVAL_ROOT / "src")
    code = (
        "import sys; import pii_anon_datasets.assessment; "
        "bad=[m for m in sys.modules if m=='pii_rate_elo_pipeline' or m.startswith('pii_rate_elo_pipeline.')]; "
        "assert not bad, bad; print('OK')"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    assert proc.returncode == 0, f"assessment imported the consumer (forbidden edge): {proc.stdout}{proc.stderr}"
    assert "OK" in proc.stdout
