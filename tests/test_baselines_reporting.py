"""Baseline leaderboard rendering — the F2-ranked markdown table + breakdowns (lib-less) and the
lazy-matplotlib chart (importorskip-gated). The renderer is fed REAL orchestrator output (via a tiny
inline fake) so its assertions track the actual results schema, not a hand-built mock.
"""

from __future__ import annotations

import pytest
from pii_anon_datasets.baselines import contract, orchestrator
from pii_anon_datasets.reporting import baselines as baselines_report

_AS = contract.AdapterSpan


class _Fake:
    def __init__(self, name, by_text):
        self.name = name
        self.model_id = f"{name}-v0"
        self.label_map = {"P": "PERSON_NAME", "E": "EMAIL_ADDRESS"}
        self.deterministic = True
        self._by_text = by_text

    def available(self) -> bool:
        return True

    def map_label(self, native):
        return self.label_map.get(native)

    def build(self):
        return None

    def detect(self, text, model):
        return list(self._by_text.get(text, []))

    def coverage(self) -> int:
        return contract.coverage_of(self.label_map)


class _Absent:
    name = "absent"
    model_id = ""
    label_map: dict = {}

    def available(self) -> bool:
        return False

    def map_label(self, native):
        return None

    def build(self):
        raise RuntimeError("unavailable")

    def detect(self, text, model):
        return []

    def coverage(self) -> int:
        return 0


def _results():
    records = [
        {
            "record_id": "r1",
            "text": "John email a@b.com",
            "domain": "technology",
            "language": "en",
            "annotations": [
                {"start": 0, "end": 4, "entity_type": "PERSON_NAME"},
                {"start": 11, "end": 18, "entity_type": "EMAIL_ADDRESS"},
            ],
        },
        {
            "record_id": "r2",
            "text": "Mary at NY",
            "domain": "clinical",
            "language": "en",
            "annotations": [{"start": 0, "end": 4, "entity_type": "PERSON_NAME"}],
        },
    ]
    good = _Fake(
        "good",
        {
            "John email a@b.com": [_AS(0, 4, "PERSON_NAME"), _AS(11, 18, "EMAIL_ADDRESS")],
            "Mary at NY": [_AS(0, 4, "PERSON_NAME"), _AS(8, 10, "PERSON_NAME")],
        },
    )
    weak = _Fake("weak", {"John email a@b.com": [_AS(0, 4, "PERSON_NAME")], "Mary at NY": []})
    return orchestrator.score_detectors(
        records, [good, weak, _Absent()], dataset_info={"split": "test", "language": "en", "dataset_version": "2.0.0"}
    )


def test_leaderboard_section_has_title_and_f2_ranked_rows() -> None:
    md = baselines_report.render_baseline_leaderboard(_results())
    assert "## Baseline Detector Performance" in md
    # F2-descending: 'good' row appears before 'weak' row.
    assert md.index("| good ") < md.index("| weak "), "detectors must be listed in F2-descending order"
    # It is a real markdown table (header + separator).
    assert "| Rank |" in md and "|---" in md


def test_leaderboard_surfaces_precision_recall_coverage_and_f2() -> None:
    md = baselines_report.render_baseline_leaderboard(_results())
    # The headline must show PRECISION (the false-positive tax) next to recall + F2, not recall alone.
    for col in ("Precision", "Recall", "F1", "F2"):
        assert col in md, f"leaderboard must show the {col} column"
    assert "2/63" in md, "per-detector label-map coverage (reachable/63) must appear"


def test_leaderboard_embeds_caveat_and_span_matching_disclosure() -> None:
    md = baselines_report.render_baseline_leaderboard(_results())
    assert "AX-001" in md or "synthetic" in md.lower(), "the non-strippable synthetic-only caveat must ride along"
    assert "strict-v1" in md and "partial" in md.lower(), "span-matching policy must be disclosed"


def test_leaderboard_has_per_domain_breakdown_and_notes_unavailable() -> None:
    md = baselines_report.render_baseline_leaderboard(_results())
    assert "domain" in md.lower()
    assert "clinical" in md and "technology" in md
    assert "absent" in md, "an unavailable detector must be disclosed, not silently dropped"


def test_chart_writes_a_nonempty_png(tmp_path) -> None:
    pytest.importorskip("matplotlib")
    out = tmp_path / "detector_f2.png"
    returned = baselines_report.detector_performance_chart(_results(), out)
    assert out.exists() and out.stat().st_size > 0
    assert str(returned) == str(out)
