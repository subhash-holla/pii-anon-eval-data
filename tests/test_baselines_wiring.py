"""Registry (name -> repo-root adapter bridge) + the end-to-end run_baselines wrapper.

The registry resolves the real repo-root adapters (regex is offline + always available, so it anchors the
tests). run_baselines is exercised end-to-end with injected records + the regex detector → a real
baseline_results.json + run-record + provenance, with no heavy lib or corpus read.
"""

from __future__ import annotations

import json

import pytest
from pii_anon_datasets.baselines import registry, run
from pii_anon_datasets.baselines.contract import DetectorAdapter
from pii_anon_datasets.baselines.results import BaselineResults


def test_load_adapter_resolves_a_real_adapter() -> None:
    a = registry.load_adapter("regex")
    assert isinstance(a, DetectorAdapter) and a.name == "regex"


def test_load_adapter_unknown_raises_keyerror() -> None:
    with pytest.raises(KeyError):
        registry.load_adapter("does-not-exist")


def test_resolve_preserves_order() -> None:
    assert [a.name for a in registry.resolve(["regex", "scrubadub"])] == ["regex", "scrubadub"]


def test_available_detectors_includes_offline_regex_excludes_cloud_by_default() -> None:
    avail = registry.available_detectors()
    assert "regex" in avail  # pure-stdlib — always available
    assert not (set(avail) & set(registry.CLOUD_DETECTORS))  # cloud never auto-listed


def test_registry_partitions_local_and_cloud() -> None:
    assert {"regex", "presidio", "spacy", "gliner", "piiranha", "scrubadub", "stanza", "flair", "llm"} <= set(
        registry.LOCAL_DETECTORS
    )
    assert set(registry.CLOUD_DETECTORS) == {"aws", "gcp", "azure"}


def _records():
    return [
        {
            "record_id": "r1",
            "text": "Email jane@example.com or call 555-123-4567.",
            "domain": "technology",
            "language": "en",
            "annotations": [
                {"start": 6, "end": 22, "entity_type": "EMAIL_ADDRESS"},
                {"start": 31, "end": 43, "entity_type": "PHONE_NUMBER"},
            ],
        }
    ]


def test_run_baselines_end_to_end_emits_artifacts(tmp_path) -> None:
    out = run.run_baselines(
        _records(),
        ["regex"],
        out_dir=tmp_path,
        dataset_info={"split": "test", "language": "en", "dataset_version": "2.0.0"},
        run_id="run-x",
        seed=20260603,
        code_commit="abc123",
        content_hash="deadbeef",
        timestamp="2026-06-03T00:00:00Z",
        generated_at="2026-06-03T00:00:00Z",
    )
    assert isinstance(out["results"], BaselineResults)
    parsed = json.loads(out["paths"]["results"].read_text(encoding="utf-8"))
    regex = parsed["detectors"]["regex"]
    assert regex["status"] == "scored"
    # The email is matched exactly (a strict-v1 TP); the phone regex grabs the leading space so its span
    # differs from gold under strict matching — exactly the boundary behavior the policy is meant to expose.
    assert regex["by_entity_type"]["EMAIL_ADDRESS"]["counts"]["tp"] == 1
    assert regex["micro"]["counts"]["tp"] >= 1
    assert out["paths"]["run_record"].exists() and out["paths"]["provenance"].exists()
