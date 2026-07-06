# tests/test_sanity_adapters.py
"""TDD tests for the three sanity-bound detectors (null / always-PERSON / oracle) + registry partitions."""
from pii_anon_datasets.baselines.contract import DetectorAdapter
from pii_anon_datasets.baselines.registry import SANITY_DETECTORS, load_adapter


def test_sanity_detectors_registered_and_excluded_from_local():
    from pii_anon_datasets.baselines.registry import LOCAL_DETECTORS
    for n in ("null", "always_person_name", "oracle"):
        assert n in SANITY_DETECTORS
        assert n not in LOCAL_DETECTORS
        assert isinstance(load_adapter(n), DetectorAdapter)


def test_null_detects_nothing():
    a = load_adapter("null")
    assert a.detect("John lives at 1 Main St", a.build()) == []


def test_always_person_name_tags_every_token():
    a = load_adapter("always_person_name")
    spans = a.detect("John Smith", a.build())
    assert len(spans) == 2
    assert all(s.entity_type == "PERSON_NAME" for s in spans)


def test_oracle_returns_gold():
    a = load_adapter("oracle")
    assert getattr(a, "wants_record", False) is True
    rec = {"annotations": [{"start": 0, "end": 4, "entity_type": "PERSON_NAME"}]}
    spans = a.detect("John lives here", a.build(), record=rec)
    assert [(s.start, s.end, s.entity_type) for s in spans] == [(0, 4, "PERSON_NAME")]
