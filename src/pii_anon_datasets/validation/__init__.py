"""Real-data validation seam (DC-14, v1.1; FR-027).

The synthetic benchmark's external-validity claim is a real-data Pass-2 item: synthetic
scores are correlated against a real corpus (i2b2-2014 / TAB) via a pre-registered
Kendall-tau / Spearman rho + seeded bootstrap CI + Bland-Altman agreement view. BUT the real
corpus is NOT present in this repository (licensing), so :func:`correlate` returns a
:class:`RealDataAbsent` sentinel and NEVER fabricates a correlation (FR-027 / epistemic
honesty). This package is the *seam*; the real-data correlation is the Pass-2 deliverable.
"""

from .correlation import (
    CORRELATION_CAVEAT,
    REAL_DATA_ABSENT_NOTE,
    CorrelationResult,
    RealDataAbsent,
    bland_altman,
    correlate,
    kendall_tau,
    spearman_rho,
)

__all__ = [
    # S7-03: real-data validation correlation harness — sentinel-guarded (FR-027 / DC-14 v1.1)
    "REAL_DATA_ABSENT_NOTE",
    "CORRELATION_CAVEAT",
    "RealDataAbsent",
    "CorrelationResult",
    "kendall_tau",
    "spearman_rho",
    "bland_altman",
    "correlate",
]
