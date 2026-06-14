"""First-party pii-anon adapters conform to the uniform contract (sp2).

Pure label-map / coverage / contract assertions run with NO heavy import. The vanilla
detector is regex-only (fast, deterministic, no model download) — its live ``detect()``
smoke runs whenever the sibling ``pii_anon`` library is importable. The swarm detector
pools model-backed engines (GLiNER et al.), so its live smoke is gated behind
``PII_ANON_RUN_LIVE_DETECTORS=1`` like the other model-backed baselines.

The label map here projects pii-anon NATIVE labels onto the canonical 63 — designed in
THIS repo (like the spacy/scrubadub/stanza/flair maps); the sister library is imported
only inside ``build()``, exactly as gliner imports gliner (NFR-050 lazy discipline).
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import pathlib
import sys

import pytest
from pii_anon_datasets import taxonomy
from pii_anon_datasets.baselines.contract import DetectorAdapter

# Repo-root holds the (namespace-package) `baselines/` adapter modules — put it on the
# path so `import baselines.<name>_baseline` resolves (mirrors the registry idiom).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

_PII_ANON_PRESENT = importlib.util.find_spec("pii_anon") is not None
_RUN_LIVE = os.environ.get("PII_ANON_RUN_LIVE_DETECTORS") == "1"
_MODULES = ["baselines.pii_anon_baseline", "baselines.pii_anon_swarm_baseline"]


@pytest.mark.parametrize("module_name", _MODULES)
def test_adapter_conforms_to_contract(module_name: str) -> None:
    adapter = importlib.import_module(module_name).ADAPTER
    assert isinstance(adapter, DetectorAdapter)


@pytest.mark.parametrize("module_name", _MODULES)
def test_label_map_targets_are_canonical_or_none(module_name: str) -> None:
    adapter = importlib.import_module(module_name).ADAPTER
    bad = {
        v
        for v in adapter.label_map.values()
        if v is not None and v not in taxonomy.CANONICAL_ENTITY_TYPES
    }
    assert not bad, f"non-canonical label-map targets: {sorted(bad)}"


def test_shared_label_map_single_source() -> None:
    # The swarm adapter must reuse the vanilla LABEL_MAP object — one projection,
    # two detectors (drift between the two maps would silently skew the comparison).
    vanilla = importlib.import_module("baselines.pii_anon_baseline")
    swarm = importlib.import_module("baselines.pii_anon_swarm_baseline")
    assert swarm.ADAPTER.label_map is vanilla.LABEL_MAP


def test_vanilla_coverage_is_63_of_63() -> None:
    # Exact anchor: with the sp2 coverage tranche every canonical type is
    # reachable — 63/63 (vs aws 24/63, gliner 23/63). A map edit that changes
    # reach must update this anchor CONSCIOUSLY.
    adapter = importlib.import_module("baselines.pii_anon_baseline").ADAPTER
    assert adapter.coverage() == 63


def test_registered_in_registry_as_local_detectors() -> None:
    from pii_anon_datasets.baselines.registry import (
        CLOUD_DETECTORS,
        DETECTOR_REGISTRY,
        LOCAL_DETECTORS,
    )

    assert DETECTOR_REGISTRY["pii_anon"] == "baselines.pii_anon_baseline"
    assert DETECTOR_REGISTRY["pii_anon_swarm"] == "baselines.pii_anon_swarm_baseline"
    assert "pii_anon" in LOCAL_DETECTORS
    assert "pii_anon_swarm" in LOCAL_DETECTORS
    assert "pii_anon" not in CLOUD_DETECTORS
    assert "pii_anon_swarm" not in CLOUD_DETECTORS


def test_map_label_normalizes_case_and_whitespace() -> None:
    adapter = importlib.import_module("baselines.pii_anon_baseline").ADAPTER
    assert adapter.map_label(" email_address ") == "EMAIL_ADDRESS"
    assert adapter.map_label("US_SSN") == "SOCIAL_SECURITY_NUMBER"
    assert adapter.map_label("DATE_ISO") is None  # deliberate drop (ambiguous)
    assert adapter.map_label("NEVER_SEEN_LABEL") is None


@pytest.mark.skipif(not _PII_ANON_PRESENT, reason="pii_anon library not installed")
def test_vanilla_live_detect_smoke() -> None:
    adapter = importlib.import_module("baselines.pii_anon_baseline").ADAPTER
    assert adapter.available()
    model = adapter.build()
    text = "Contact alice@example.com or call 555-867-5309."
    spans = adapter.detect(text, model)
    assert any(
        s.entity_type == "EMAIL_ADDRESS" and text[s.start : s.end] == "alice@example.com"
        for s in spans
    ), spans
    # Everything emitted is canonical (DX-02 holds by construction).
    assert all(s.entity_type in taxonomy.CANONICAL_ENTITY_TYPES for s in spans)


@pytest.mark.skipif(
    not (_PII_ANON_PRESENT and _RUN_LIVE),
    reason="model-backed pool; set PII_ANON_RUN_LIVE_DETECTORS=1",
)
def test_swarm_live_detect_smoke() -> None:
    adapter = importlib.import_module("baselines.pii_anon_swarm_baseline").ADAPTER
    model = adapter.build()
    text = "Contact alice@example.com today."
    spans = adapter.detect(text, model)
    assert any(s.entity_type == "EMAIL_ADDRESS" for s in spans), spans
