"""P1 run-path integrity guards (CAP-02 DC-22 / NFR-019/020/050).

P1 (SHOWSTOPPER): the assessment run path computes ALL inference with the AUDITED ``stats`` ring; the
fabricated ``pii_rate_elo_pipeline.analysis.significance.SignificanceTester`` must never be on the call
graph. This module supplies the testable lint:

* :func:`scan_for_fabricated_stats` — regex-scans source files for the three VERIFIED fabrication
  signatures (read firsthand from ``significance.py`` 2026-06-01): a fake standard error ``/ 100``,
  Gaussian-noise-as-bootstrap (``np.random.normal``), and a McNemar that never counts discordant pairs
  (``n_approx`` / ``pooled_sd = 0.1``). Zero matches required on the declared run-path module set (NFR-020).

Pure-stdlib (``re`` + ``pathlib`` — NFR-050). Used by ``tests/test_p1_runpath_guard.py`` and (from S10) by
the assessment report layer's self-lint.
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

# The three verified fabrication signatures from pii_rate_elo_pipeline/analysis/significance.py.
FABRICATION_PATTERNS: tuple[str, ...] = (
    r"\(\s*1\s*-\s*[A-Za-z_][\w.]*\s*\)\s*/\s*100",  # se = metric * (1 - metric) / 100
    r"np\.random\.normal",                            # additive Gaussian noise masquerading as a bootstrap
    r"\bn_approx\b",                                   # McNemar with a hardcoded approximate n
    r"pooled_sd\s*=\s*0\.1",                           # hardcoded pooled SD for a fake effect size
)
_COMPILED: tuple[re.Pattern[str], ...] = tuple(re.compile(p) for p in FABRICATION_PATTERNS)


def scan_for_fabricated_stats(paths: Iterable[str | Path]) -> list[tuple[str, int, str]]:
    """Scan source files for fabricated-statistics signatures (NFR-020 fabrication ban).

    Returns ``(path, lineno, stripped_line)`` for every line matching any fabrication pattern; an empty
    list means clean. Missing files are skipped silently — the caller decides whether absence matters
    (e.g. the positive-control test skips when the pii-rate-elo checkout is not present).
    """
    findings: list[tuple[str, int, str]] = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if any(pat.search(line) for pat in _COMPILED):
                findings.append((str(path), lineno, line.strip()))
    return findings
