"""Detector registry — maps a detector name to its repo-root adapter module and resolves the ``ADAPTER``.

Bridges the pure-stdlib package orchestrator to the (non-packaged, namespace-package) repo-root
``baselines/`` adapter modules: it puts the repo root on ``sys.path`` (the same idiom every adapter and the
CLI use via ``cli._repo_root``) and imports the module LAZILY. ``available()`` is a ``find_spec`` probe (no
heavy import), so listing / availability stays NFR-050-clean — importing this module pulls in no detector lib
and no adapter module.

Cloud detectors (aws / gcp / azure) are registered but partitioned out of the default local set: they are
built behind keys and must never run without explicit ``--cloud`` opt-in + a confirmed budget.
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Iterable

from ..cli import _repo_root
from .contract import DetectorAdapter

DETECTOR_REGISTRY: dict[str, str] = {
    "regex": "baselines.regex_baseline",
    "presidio": "baselines.presidio_baseline",
    "spacy": "baselines.spacy_baseline",
    "gliner": "baselines.gliner_baseline",
    "piiranha": "baselines.piiranha_baseline",
    "scrubadub": "baselines.scrubadub_baseline",
    "stanza": "baselines.stanza_baseline",
    "flair": "baselines.flair_baseline",
    "llm": "baselines.llm_baseline",
    "aws": "baselines.aws_comprehend_baseline",
    "gcp": "baselines.gcp_dlp_baseline",
    "azure": "baselines.azure_baseline",
    "pii_anon": "baselines.pii_anon_baseline",
    "pii_anon_swarm": "baselines.pii_anon_swarm_baseline",
    "null": "baselines.null_baseline",
    "always_person_name": "baselines.always_person_name_baseline",
    "oracle": "baselines.oracle_perfect_baseline",
}

CLOUD_DETECTORS: tuple[str, ...] = ("aws", "gcp", "azure")
SANITY_DETECTORS: tuple[str, ...] = ("null", "always_person_name", "oracle")
LOCAL_DETECTORS: tuple[str, ...] = tuple(
    n for n in DETECTOR_REGISTRY if n not in CLOUD_DETECTORS and n not in SANITY_DETECTORS
)


def _ensure_repo_on_path() -> None:
    """Put the repo root on ``sys.path`` so ``import baselines.<name>_baseline`` resolves."""
    root = str(_repo_root())
    if root not in sys.path:
        sys.path.insert(0, root)


def load_adapter(name: str) -> DetectorAdapter:
    """Import the repo-root adapter module for ``name`` and return its contract-conforming ``ADAPTER``."""
    if name not in DETECTOR_REGISTRY:
        raise KeyError(f"unknown detector {name!r}; known: {sorted(DETECTOR_REGISTRY)}")
    _ensure_repo_on_path()
    module = importlib.import_module(DETECTOR_REGISTRY[name])
    adapter = module.ADAPTER
    if not isinstance(adapter, DetectorAdapter):
        raise TypeError(f"{name}: {DETECTOR_REGISTRY[name]}.ADAPTER does not satisfy the DetectorAdapter contract")
    return adapter


def resolve(names: Iterable[str]) -> list[DetectorAdapter]:
    """Resolve an ordered list of adapters by name (order preserved)."""
    return [load_adapter(n) for n in names]


def available_detectors(*, include_cloud: bool = False) -> list[str]:
    """The registered detectors whose library (and, for cloud, credentials) are present. Cloud detectors are
    excluded unless ``include_cloud`` is set. A module that fails to import is treated as unavailable."""
    names = DETECTOR_REGISTRY if include_cloud else LOCAL_DETECTORS
    out: list[str] = []
    for name in names:
        try:
            if load_adapter(name).available():
                out.append(name)
        except Exception:  # noqa: BLE001 - an unimportable/missing adapter is simply unavailable
            continue
    return out
