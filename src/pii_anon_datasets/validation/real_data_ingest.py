"""Path-activated real-data ingest for the FR-027 correlation slice (cycle-1 UC-13; DC-14).

The real i2b2-2014 / TAB de-id corpora are NOT in this repository (licensing / DUA). This module is the
ACTIVATION seam: it correlates synthetic-vs-real detector scores ONLY when a maintainer drops a DERIVED
paired-score file at a configured path (the ``PII_ANON_REAL_DEID_PATH`` environment variable, or an explicit
argument). Until that file exists, :func:`correlate_from_path` returns the :class:`RealDataAbsent` sentinel and
NEVER fabricates a correlation (FR-027). The dropped file is a DERIVED score matrix only — paired per-cell
synthetic/real detector scores — so raw PHI never enters the repo; the audited :func:`correlate` does the rest.

Pure-stdlib. Drop-in payload schema: ``{"synthetic": [float, ...], "real": [float, ...]}`` (equal length, >= 2).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .correlation import CorrelationResult, RealDataAbsent, correlate

REAL_DEID_PATH_ENV = "PII_ANON_REAL_DEID_PATH"


def resolve_real_data_path(explicit: str | os.PathLike[str] | None = None) -> Path | None:
    """Resolve the real-data score file path (explicit arg > env var); ``None`` if unset or absent on disk."""
    raw = explicit if explicit is not None else os.environ.get(REAL_DEID_PATH_ENV)
    if not raw:
        return None
    path = Path(raw)
    return path if path.exists() else None


def load_score_pairs(path: str | os.PathLike[str]) -> tuple[list[float], list[float]]:
    """Load the DERIVED paired scores ``(synthetic, real)`` from the dropped JSON file.

    Raises ``ValueError`` on a malformed / unequal-length / under-length payload — it NEVER pads, truncates, or
    fabricates to force a result (FR-027)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    try:
        syn = [float(v) for v in data["synthetic"]]
        real = [float(v) for v in data["real"]]
    except (KeyError, TypeError, ValueError) as e:
        raise ValueError(f"real-data score file malformed (need numeric 'synthetic'/'real' arrays): {e}") from e
    if len(syn) != len(real) or len(syn) < 2:
        raise ValueError("real-data score file needs >= 2 equal-length paired 'synthetic' / 'real' arrays")
    return syn, real


def correlate_from_path(
    explicit_path: str | os.PathLike[str] | None = None, *, seed: int = 0, n_boot: int = 1000
) -> CorrelationResult | RealDataAbsent:
    """Path-activated correlation: returns :class:`RealDataAbsent` unless a real-data score file is present at the
    configured path; then runs the audited :func:`correlate`. NEVER fabricates a correlation (FR-027)."""
    path = resolve_real_data_path(explicit_path)
    if path is None:
        return RealDataAbsent()
    syn, real = load_score_pairs(path)
    return correlate(syn, real, seed=seed, n_boot=n_boot)
