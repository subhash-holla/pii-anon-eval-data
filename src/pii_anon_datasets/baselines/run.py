"""End-to-end ``pii-anon baselines`` run: resolve the named detectors, score the records via the audited
scorer, and emit ``baseline_results.json`` + run-record + sha256 provenance.

Thin glue over :func:`registry.resolve`, :func:`orchestrator.score_detectors`, and
:func:`provenance.emit_baseline_artifacts`. Records are passed IN (the CLI loads the split; tests inject a
slice), and all determinism inputs are injected — so the function is pure-stdlib and easy to test offline.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path

from .orchestrator import score_detectors
from .provenance import emit_baseline_artifacts
from .registry import resolve
from .results import BaselineResults


def run_baselines(
    records: Sequence[Mapping[str, object]],
    detector_names: Iterable[str],
    *,
    out_dir: str | Path,
    dataset_info: Mapping[str, object],
    run_id: str,
    seed: int,
    code_commit: str,
    content_hash: str,
    timestamp: str,
    generated_at: str,
    confidence: float = 0.95,
    progress: Callable[[dict], None] | None = None,
) -> dict[str, object]:
    """Score ``detector_names`` over ``records`` and emit artifacts into ``out_dir``.

    Returns ``{"results": BaselineResults, "paths": {results/run_record/provenance: Path}}``.
    """
    adapters = resolve(detector_names)
    results: BaselineResults = score_detectors(
        records, adapters, dataset_info=dataset_info, confidence=confidence, progress=progress
    )
    paths = emit_baseline_artifacts(
        results,
        out_dir,
        run_id=run_id,
        seed=seed,
        code_commit=code_commit,
        content_hash=content_hash,
        timestamp=timestamp,
        generated_at=generated_at,
    )
    return {"results": results, "paths": paths}
