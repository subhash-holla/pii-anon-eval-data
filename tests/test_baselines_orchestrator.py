"""Baselines orchestrator aggregation — driven by a fully-controllable FAKE detector so the whole
core is exercised with NO detector library installed (CI-green on a lib-less venv).

The fake returns registered AdapterSpans per exact record text, so every TP/FP/FN below is hand-computed.
Scenario (2 records, en):
  r1 "John email a@b.com"  (technology): gold PERSON_NAME[0,4], EMAIL_ADDRESS[11,18]
  r2 "Mary at NY"          (clinical):   gold PERSON_NAME[0,4]
A perfect-ish fake predicts both r1 golds, the r2 PERSON gold, PLUS a spurious PERSON_NAME[8,10] in r2.
  => micro tp=3 fp=1 fn=0  (precision 0.75, recall 1.0, F2 0.9375)
Crucially, r1 and r2 both have a PERSON_NAME at [0,4]; a correct aggregator must NOT let r2's predicted
[0,4] match r1's gold (record namespacing) — both are independent TPs, not a cross-record collision.
"""

from __future__ import annotations

import json

import pytest
from pii_anon_datasets.assessment.tracks import assert_no_merged_family
from pii_anon_datasets.baselines import contract, orchestrator
from pii_anon_datasets.baselines.results import BaselineResults

_AS = contract.AdapterSpan


class _MapFake:
    """A controllable fake detector: returns the AdapterSpans registered for each exact record text."""

    def __init__(self, name, by_text, *, deterministic=True):
        self.name = name
        self.model_id = f"{name}-v0"
        self.label_map = {"P": "PERSON_NAME", "E": "EMAIL_ADDRESS"}
        self.deterministic = deterministic
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
    """A detector whose library is not installed — available() is False."""

    name = "absent"
    model_id = ""
    label_map: dict = {}

    def available(self) -> bool:
        return False

    def map_label(self, native):
        return None

    def build(self):
        raise RuntimeError("library not installed")

    def detect(self, text, model):
        return []

    def coverage(self) -> int:
        return 0


def _records():
    return [
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


def _good_fake():
    return _MapFake(
        "good",
        {
            "John email a@b.com": [_AS(0, 4, "PERSON_NAME"), _AS(11, 18, "EMAIL_ADDRESS")],
            "Mary at NY": [_AS(0, 4, "PERSON_NAME"), _AS(8, 10, "PERSON_NAME")],  # 2nd is a FP
        },
    )


def _run(*adapters):
    return orchestrator.score_detectors(
        _records(), list(adapters), dataset_info={"split": "test", "language": "en", "dataset_version": "2.0.0"}
    )


def test_micro_counts_and_metrics_are_record_namespaced() -> None:
    res = _run(_good_fake())
    micro = res.detectors["good"]["micro"]
    assert micro["counts"]["tp"] == 3  # both r1 golds + r2 PERSON — NOT collapsed across records
    assert micro["counts"]["fp"] == 1  # the spurious r2 PERSON_NAME[8,10]
    assert micro["counts"]["fn"] == 0
    assert micro["precision"] == pytest.approx(0.75)
    assert micro["recall"] == pytest.approx(1.0)
    assert micro["f2"] == pytest.approx(0.9375)  # recall-weighted (β=2)


def test_micro_carries_wilson_cis_and_relaxed_partial() -> None:
    res = _run(_good_fake())
    micro = res.detectors["good"]["micro"]
    assert micro["recall_ci"]["method"] == "wilson"
    assert micro["precision_ci"]["method"] == "wilson"
    assert "partial_f1" in micro  # the relaxed/partial-overlap variant, reported separately (not CI'd)


def test_breakdowns_per_type_domain_language() -> None:
    res = _run(_good_fake()).detectors["good"]
    bt = res["by_entity_type"]
    assert bt["PERSON_NAME"]["counts"] == {"tp": 2, "fp": 1, "fn": 0, "partial": 0, "policy": "strict-v1"}
    assert bt["EMAIL_ADDRESS"]["counts"]["tp"] == 1 and bt["EMAIL_ADDRESS"]["counts"]["fp"] == 0
    bd = res["by_domain"]
    assert bd["technology"]["counts"]["tp"] == 2 and bd["technology"]["counts"]["fp"] == 0
    assert bd["clinical"]["counts"]["tp"] == 1 and bd["clinical"]["counts"]["fp"] == 1
    assert set(res["by_language"]) == {"en"}


def test_macro_is_unweighted_mean_over_gold_types() -> None:
    res = _run(_good_fake()).detectors["good"]
    # PERSON_NAME f2 (P=2/3,R=1)= 10/11≈0.9091 ; EMAIL f2 (P=1,R=1)=1 ; macro=(.9091+1)/2≈0.9545
    assert res["macro"]["f2"] == pytest.approx((10 / 11 + 1) / 2, abs=1e-6)
    assert res["macro"]["n_types"] == 2


def test_ranking_is_f2_descending() -> None:
    weak = _MapFake("weak", {"John email a@b.com": [_AS(0, 4, "PERSON_NAME")], "Mary at NY": []})  # misses a lot
    res = _run(_good_fake(), weak)
    order = [row["detector"] for row in res.ranking]
    assert order == ["good", "weak"]
    assert res.ranking[0]["rank"] == 1 and res.ranking[1]["rank"] == 2
    assert res.ranking[0]["f2_micro"] >= res.ranking[1]["f2_micro"]


def test_unavailable_detector_recorded_not_dropped() -> None:
    res = _run(_good_fake(), _Absent())
    assert res.detectors["absent"]["status"] == "unavailable"
    assert "absent" not in [row["detector"] for row in res.ranking]  # not ranked
    assert res.detectors["good"]["status"] == "scored"


def test_coverage_disclosure_present_per_detector() -> None:
    res = _run(_good_fake()).detectors["good"]
    cov = res["coverage"]
    assert cov["reachable"] == 2  # PERSON_NAME + EMAIL_ADDRESS
    assert cov["of_total"] == 63
    assert "EMAIL_ADDRESS" in cov["reachable_types"]


def test_results_carry_honesty_metadata_and_are_not_a_merged_family() -> None:
    res = _run(_good_fake())
    assert isinstance(res, BaselineResults)
    assert res.matching_policy == "strict-v1"
    assert "AX-001" in res.caveat or "synthetic" in res.caveat.lower()
    assert "strict-v1" in res.span_matching_disclosure and "partial" in res.span_matching_disclosure.lower()
    assert_no_merged_family(res)  # AX-004: detection family only, no fused score, not numeric


def test_predicted_spans_are_whitespace_trimmed_before_matching() -> None:
    """A detector that returns boundary whitespace (e.g. a transformer tokenizer emitting ' John ') must
    not be penalized: predicted spans are trimmed to their non-whitespace entity boundary before strict
    matching, so a trim-to-gold prediction is a TP, not FP+FN."""
    records = [
        {
            "record_id": "r1",
            "text": "Hi  John  here",  # "John" is the gold span [4, 8]
            "domain": "general",
            "language": "en",
            "annotations": [{"start": 4, "end": 8, "entity_type": "PERSON_NAME"}],
        }
    ]
    fake = _MapFake("trim", {"Hi  John  here": [_AS(2, 9, "PERSON_NAME")]})  # "  John " (padded)
    res = orchestrator.score_detectors(records, [fake], dataset_info={}).detectors["trim"]
    assert res["micro"]["counts"]["tp"] == 1
    assert res["micro"]["counts"]["fp"] == 0


def test_per_record_detect_failure_does_not_kill_the_detector() -> None:
    """In a long census one pathological record (e.g. exceeding a model's max length) must not zero out a
    whole detector: a per-record detect() exception is caught, that record contributes no predictions
    (its gold becomes a miss), and the detector still scores — with the failure count surfaced."""
    records = [
        {"record_id": "r1", "text": "John", "domain": "general", "language": "en",
         "annotations": [{"start": 0, "end": 4, "entity_type": "PERSON_NAME"}]},
        {"record_id": "r2", "text": "BOOM", "domain": "general", "language": "en",
         "annotations": [{"start": 0, "end": 4, "entity_type": "PERSON_NAME"}]},
    ]

    class _Flaky:
        name = "flaky"
        model_id = ""
        label_map = {"P": "PERSON_NAME"}
        deterministic = True

        def available(self) -> bool:
            return True

        def map_label(self, native):
            return self.label_map.get(native)

        def build(self):
            return None

        def detect(self, text, model):
            if text == "BOOM":
                raise RuntimeError("pathological record")
            return [_AS(0, 4, "PERSON_NAME")]

        def coverage(self) -> int:
            return 1

    res = orchestrator.score_detectors(records, [_Flaky()], dataset_info={}).detectors["flaky"]
    assert res["status"] == "scored"  # NOT errored — the run survived the bad record
    assert res["record_errors"] == 1
    assert res["micro"]["counts"]["tp"] == 1  # r1 matched
    assert res["micro"]["counts"]["fn"] == 1  # r2's gold missed (its record errored -> no predictions)


def test_progress_callback_receives_lifecycle_events() -> None:
    """An optional progress callback gets clock-free lifecycle events (start / per-records / done) so the CLI
    can render a live, transparent view of a long run; the core itself emits no time and stays deterministic."""
    events: list[dict] = []
    records = [
        {"record_id": "r1", "text": "John", "domain": "general", "language": "en",
         "annotations": [{"start": 0, "end": 4, "entity_type": "PERSON_NAME"}]},
    ]
    fake = _MapFake("good", {"John": [_AS(0, 4, "PERSON_NAME")]})
    orchestrator.score_detectors(records, [fake], dataset_info={}, progress=events.append)
    kinds = [e["event"] for e in events]
    assert "detector_start" in kinds and "detector_done" in kinds
    rec_events = [e for e in events if e["event"] == "records"]
    assert rec_events and rec_events[-1]["done"] == rec_events[-1]["total"] == 1
    assert all(e.get("detector") == "good" for e in events)


def test_merge_results_unions_detectors_and_reranks() -> None:
    """Per-detector runs (the restart-safe census pattern) merge into one F2-ranked leaderboard."""
    recs = [
        {"record_id": "r1", "text": "John email a@b.com", "domain": "technology", "language": "en",
         "annotations": [{"start": 0, "end": 4, "entity_type": "PERSON_NAME"},
                         {"start": 11, "end": 18, "entity_type": "EMAIL_ADDRESS"}]},
    ]
    ds = {"split": "test", "language": "en", "dataset_version": "2.0.0"}
    good = orchestrator.score_detectors(
        recs, [_MapFake("good", {"John email a@b.com": [_AS(0, 4, "PERSON_NAME"), _AS(11, 18, "EMAIL_ADDRESS")]})],
        dataset_info=ds)
    weak = orchestrator.score_detectors(
        recs, [_MapFake("weak", {"John email a@b.com": [_AS(0, 4, "PERSON_NAME")]})], dataset_info=ds)
    merged = orchestrator.merge_results([good, weak])
    assert set(merged.detectors) == {"good", "weak"}
    assert [r["detector"] for r in merged.ranking] == ["good", "weak"]  # F2-descending
    assert merged.dataset["n_records"] == 1


def test_results_from_dict_round_trips() -> None:
    res = _run(_good_fake())
    assert BaselineResults.from_dict(res.as_dict()).as_dict() == res.as_dict()


def test_results_serialize_to_canonical_sorted_key_json() -> None:
    res = _run(_good_fake())
    txt = res.to_json()
    assert txt.endswith("\n")
    parsed = json.loads(txt)
    # canonical: sorting the parsed object re-serializes byte-identically (keys already sorted)
    assert json.dumps(parsed, sort_keys=True, ensure_ascii=False) + "\n" == txt
    assert parsed["dataset"]["n_records"] == 2
    assert parsed["dataset"]["n_gold"] == 3
