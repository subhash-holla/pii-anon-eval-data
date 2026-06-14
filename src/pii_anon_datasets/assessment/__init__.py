"""CAP-02 Powered Assessment Workflow — eval-data OWNS sampling + observability + reporting.

This package implements the assessment spine (``load → sample → run → score → rate → report``): the
powered lattice-stratified sampler (``sample.py``), the manifest seam (``manifest.py``), power/honesty
verdicts (``verdicts.py``), pre-registration (``prereg.py``), observability run-records (``runrecord.py``),
and the report projection that wires the AUDITED ``stats`` ring (``report.py``). Pure-stdlib cores; heavy
deps (numpy / matplotlib) are lazy-imported only inside figure code.

INVARIANT (D5 §4.5 — the FORBIDDEN EDGE): this package imports ONLY stdlib + ``pii_anon_datasets``
internals; it NEVER imports ``pii_rate_elo_pipeline``. The dependency is one-way — the consumer
(pii-rate-elo) imports us, never the reverse — which is what keeps the fabricated
``pii_rate_elo_pipeline.analysis.significance`` off the assessment call graph (P1).
"""
from __future__ import annotations

__all__: list[str] = []
