"""Baselines detector contract (the uniform adapter interface) — the AdapterSpan→scoring.core.Span
convert seam, the per-detector label-map coverage / lossiness disclosure, and the structural
DetectorAdapter Protocol. Pure-stdlib and lib-independent: this whole file runs with NO detector
library installed (it never imports presidio/spacy/gliner/etc.).
"""

from __future__ import annotations

import pytest
from pii_anon_datasets import taxonomy
from pii_anon_datasets.baselines import contract
from pii_anon_datasets.scoring.core import Span


def test_to_scoring_spans_converts_and_drops_text() -> None:
    """AdapterSpan (which carries debug `text`) converts to the scorer's frozen Span (no text)."""
    out = contract.to_scoring_spans([contract.AdapterSpan(0, 4, "PERSON_NAME", "John")])
    assert out == [Span(0, 4, "PERSON_NAME")]
    assert all(isinstance(s, Span) for s in out)


def test_to_scoring_spans_fails_loud_on_non_canonical() -> None:
    """DX-02: a span whose type is not one of the canonical 63 must fail loud, never pass through."""
    with pytest.raises(ValueError):
        contract.to_scoring_spans([contract.AdapterSpan(0, 3, "NOT_A_REAL_TYPE", "xxx")])


def test_coverage_of_counts_distinct_canonical_targets() -> None:
    """Coverage = number of DISTINCT canonical-63 types a label map can reach (None == drop)."""
    label_map = {"PER": "PERSON_NAME", "PERSON": "PERSON_NAME", "MAIL": "EMAIL_ADDRESS", "MISC": None}
    assert contract.coverage_of(label_map) == 2  # PERSON_NAME + EMAIL_ADDRESS; MISC dropped


def test_lossiness_reports_reachable_dropped_and_unreachable() -> None:
    """The lossiness disclosure names what's reachable, what native labels are dropped, and the
    canonical types a detector can NEVER emit (the projection ceiling)."""
    loss = contract.lossiness({"PER": "PERSON_NAME", "MISC": None})
    assert loss["reachable"] == 1
    assert loss["of_total"] == taxonomy.ENTITY_TYPE_COUNT
    assert "MISC" in loss["dropped_native"]
    assert "PERSON_NAME" not in loss["unreachable_types"]
    assert len(loss["unreachable_types"]) == taxonomy.ENTITY_TYPE_COUNT - 1


def test_detector_adapter_protocol_is_structural() -> None:
    """The DetectorAdapter Protocol is runtime-checkable on its methods: a conforming duck passes,
    one missing `detect()` fails — this is the registry's structural gate."""

    class _Good:
        name = "fake"
        model_id = ""
        label_map = {"PER": "PERSON_NAME"}

        def available(self) -> bool:
            return True

        def map_label(self, native: str) -> str | None:
            return self.label_map.get(native)

        def build(self) -> object:
            return object()

        def detect(self, text: str, model: object) -> list[contract.AdapterSpan]:
            return []

        def coverage(self) -> int:
            return 1

    class _Bad:
        def available(self) -> bool:
            return True

    assert isinstance(_Good(), contract.DetectorAdapter)
    assert not isinstance(_Bad(), contract.DetectorAdapter)
