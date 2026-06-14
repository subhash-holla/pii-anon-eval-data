"""Tests for scripts/benchmark_throughput (NFR-010 Pass-2 harness).

Asserts harness CORRECTNESS + AX-002 DETERMINISM of the reproducible parts
(slice selection, span conversion, percentile math, run-record schema) — NOT the
host-dependent throughput numbers (those are the measurement, by definition not pinned).

Pins one honesty invariant at code level (NFR-010 protocol §2): the agent host must
NEVER mark itself as the canonical reference host, and the canonical verdict the harness
emits for its own run is INSUFFICIENT_EVIDENCE.
"""
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import benchmark_throughput as bench  # noqa: E402


# --------------------------------------------------------------------------- fixtures
def _rec(rid, text, lang="en", anns=None):
    return {
        "record_id": rid,
        "text": text,
        "language": lang,
        "annotations": anns if anns is not None else [],
    }


def _write_jsonl_gz(tmp_path, records, name="corpus.jsonl.gz"):
    p = tmp_path / name
    with gzip.open(p, "wt", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return p


def _write_jsonl(tmp_path, records, name="corpus.jsonl"):
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    return p


# --------------------------------------------------------------------------- percentiles
def test_percentiles_nearest_rank():
    # 1..10; nearest-rank(ceil): p50 -> rank ceil(.5*10)=5 -> value 5;
    # p95 -> ceil(.95*10)=10 -> 10; p99 -> ceil(.99*10)=10 -> 10
    out = bench.percentiles([10, 9, 8, 7, 6, 5, 4, 3, 2, 1], (50, 95, 99))
    assert out[50] == 5
    assert out[95] == 10
    assert out[99] == 10


def test_percentiles_single_and_empty():
    assert bench.percentiles([42.0], (50, 95, 99)) == {50: 42.0, 95: 42.0, 99: 42.0}
    empty = bench.percentiles([], (50, 95, 99))
    assert empty == {50: 0.0, 95: 0.0, 99: 0.0}


# --------------------------------------------------------------------------- streaming reader
def test_iter_corpus_streams_gz_and_filters_language(tmp_path):
    recs = [_rec("a", "x", "en"), _rec("b", "y", "fr"), _rec("c", "z", "en")]
    gz = _write_jsonl_gz(tmp_path, recs)
    assert [r["record_id"] for r in bench.iter_corpus(gz, language="en")] == ["a", "c"]
    assert [r["record_id"] for r in bench.iter_corpus(gz, language=None)] == ["a", "b", "c"]


def test_iter_corpus_reads_plain_jsonl(tmp_path):
    recs = [_rec("a", "x", "en"), _rec("b", "y", "en")]
    plain = _write_jsonl(tmp_path, recs)
    assert [r["record_id"] for r in bench.iter_corpus(plain, language="en")] == ["a", "b"]


# --------------------------------------------------------------------------- slice selection
def test_select_slice_head_is_first_n_in_order(tmp_path):
    recs = [_rec(f"r{i}", "t", "en") for i in range(5)]
    gz = _write_jsonl_gz(tmp_path, recs)
    sel = bench.select_slice(gz, n=3, language="en", sample="head")
    assert [r["record_id"] for r in sel] == ["r0", "r1", "r2"]


def test_select_slice_random_is_seed_reproducible(tmp_path):
    recs = [_rec(f"r{i}", "t", "en") for i in range(50)]
    gz = _write_jsonl_gz(tmp_path, recs)
    a = bench.select_slice(gz, n=10, language="en", sample="random", seed=123)
    b = bench.select_slice(gz, n=10, language="en", sample="random", seed=123)
    assert [r["record_id"] for r in a] == [r["record_id"] for r in b]  # byte-identical (AX-002)
    assert len(a) == 10
    assert {r["record_id"] for r in a} <= {f"r{i}" for i in range(50)}


# --------------------------------------------------------------------------- span conversion
def test_gold_core_spans_from_annotations_skips_invalid():
    rec = _rec("a", "Sara at a@b.com", anns=[
        {"start": 0, "end": 4, "entity_type": "PERSON_NAME"},
        {"start": 8, "end": 15, "entity_type": "EMAIL_ADDRESS"},
        {"start": 9, "end": 3, "entity_type": "BROKEN"},        # end<start -> skipped
        {"start": 0, "entity_type": "MISSING_END"},             # missing key -> skipped
    ])
    spans = bench.gold_core_spans(rec)
    assert len(spans) == 2
    assert {(s.start, s.end, s.entity_type) for s in spans} == {
        (0, 4, "PERSON_NAME"), (8, 15, "EMAIL_ADDRESS")}
    # converted to the 3-field frozen core.Span
    assert all(type(s).__name__ == "Span" and not hasattr(s, "text") for s in spans)


def test_pred_core_spans_drops_text_field():
    det = bench.detect_regex("Reach me at a@b.com please")
    core = bench.pred_core_spans(det)
    assert core, "expected at least one predicted span"
    assert all(hasattr(s, "entity_type") and not hasattr(s, "text") for s in core)


# --------------------------------------------------------------------------- reused detector
def test_detect_regex_finds_email_and_ssn():
    spans = bench.detect_regex("Email a@b.com and SSN 123-45-6789 here")
    types = {s.entity_type for s in spans}
    assert "EMAIL_ADDRESS" in types
    assert "SOCIAL_SECURITY_NUMBER" in types


def test_detection_output_is_deterministic():
    t = "Contact Sara at sara@x.com or 555-123-4567; IP 10.0.0.1"
    a = [(s.entity_type, s.start, s.end) for s in bench.detect_regex(t)]
    b = [(s.entity_type, s.start, s.end) for s in bench.detect_regex(t)]
    assert a == b


# --------------------------------------------------------------------------- timing stage
def test_time_stage_smoke(tmp_path):
    recs = [_rec(f"r{i}", "Email a@b.com SSN 123-45-6789", "en") for i in range(12)]
    out = bench.time_stage(recs, lambda r: bench.detect_regex(r["text"]),
                           warmup=2, chunk_size=4)
    assert out["n_timed"] == 10            # 12 total - 2 warmup
    assert out["rec_per_sec"] > 0
    for k in ("p50", "p95", "p99"):
        assert k in out["latency_us"]
    assert out["total_seconds"] > 0


# --------------------------------------------------------------------------- NFR-010c extrapolation
def test_full_scan_estimate_math():
    est = bench.full_scan_estimate(1000.0, total_records=575604, budget_seconds=60)
    assert abs(est["wall_clock_seconds"] - 575.604) < 1e-6
    assert est["total_records"] == 575604
    # rows processable inside the budget = rec_per_sec * budget
    assert est["recommended_sampling_rows"] == 60000


# --------------------------------------------------------------------------- host spec honesty
def test_host_spec_is_never_the_reference_host():
    h = bench.host_spec()
    assert h["is_reference_host"] is False
    assert "cores_logical" in h and "python_version" in h
    # the honesty note must flag this is NOT the declared 8-core reference host
    assert "reference host" in h["note"].lower() or "8-core" in h["note"].lower()


# --------------------------------------------------------------------------- run-record schema
def _stub_spacy_skipped(records, **kw):
    # Keep the harness unit tests hermetic — never spin up Presidio/spaCy/torch in the unit layer
    # (test-architecture anti-pattern: no heavy deps in 'unit' files). The live spaCy path is
    # exercised only in the real agent-env run, never in pytest.
    return {"class": "spacy_ner", "status": "skipped", "floored": False,
            "reason": "stubbed in unit test (no heavy deps)"}


def test_build_run_record_schema_and_json_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(bench, "run_spacy_ner_class", _stub_spacy_skipped)
    recs = [_rec(f"r{i}", "Email a@b.com SSN 123-45-6789 IP 10.0.0.1", "en")
            for i in range(20)]
    gz = _write_jsonl_gz(tmp_path, recs)
    rr = bench.build_run_record(
        corpus_path=gz, n=20, language="en", sample="head",
        seed=bench.SEED_BENCHMARK, warmup=2, chunk_size=8, runs=2,
        timestamp="2026-05-31T00:00:00Z",
    )
    # JSON-serializable
    assert json.loads(json.dumps(rr)) == rr
    # required top-level structure
    for key in ("schema", "seed", "host", "corpus", "detector_classes",
                "score_leg", "nfr_010a", "nfr_010b", "nfr_010c", "provenance"):
        assert key in rr, f"missing run-record key: {key}"
    # NFR-010b carries the target and the measured regex number + a meets_target bool
    assert rr["nfr_010b"]["target_rec_per_sec"] == 5000
    assert "meets_target" in rr["nfr_010b"]
    # the canonical verdict for THIS (agent) run is INSUFFICIENT_EVIDENCE, never a pass
    assert rr["provenance"]["is_reference_host"] is False
    assert rr["provenance"]["canonical_verdict"] == "INSUFFICIENT_EVIDENCE"


def test_run_record_marks_transformer_and_llm_exempt(tmp_path, monkeypatch):
    monkeypatch.setattr(bench, "run_spacy_ner_class", _stub_spacy_skipped)
    recs = [_rec(f"r{i}", "Email a@b.com SSN 123-45-6789", "en") for i in range(16)]
    gz = _write_jsonl_gz(tmp_path, recs)
    rr = bench.build_run_record(
        corpus_path=gz, n=16, language="en", sample="head",
        seed=bench.SEED_BENCHMARK, warmup=2, chunk_size=8, runs=1,
        timestamp="2026-05-31T00:00:00Z",
    )
    classes = {c["class"]: c for c in rr["detector_classes"]}
    assert "regex" in classes and classes["regex"]["status"] == "measured"
    assert classes["regex"]["floored"] is True          # the ≥5000 floor applies to regex
    # transformer + llm are reported but EXEMPT from the throughput floor (NFR-010a)
    for exempt in ("transformer", "llm"):
        assert exempt in classes
        assert classes[exempt]["status"] == "exempt"
        assert classes[exempt]["floored"] is False
    # spaCy/Presidio class is either measured (extra installed) or honestly skipped
    assert classes["spacy_ner"]["status"] in ("measured", "skipped")


def test_build_run_record_bounds_spacy_subslice(tmp_path, monkeypatch):
    # The (slow, heavy) spaCy-NER class times only a bounded sub-slice; the floored regex path
    # still uses the full slice. Keeps the run tractable on any host.
    seen = {}

    def _capture(records, **kw):
        seen["n"] = len(records)
        return {"class": "spacy_ner", "status": "skipped", "floored": False, "reason": "captured"}

    monkeypatch.setattr(bench, "run_spacy_ner_class", _capture)
    recs = [_rec(f"r{i}", "Email a@b.com", "en") for i in range(40)]
    gz = _write_jsonl_gz(tmp_path, recs)
    bench.build_run_record(
        corpus_path=gz, n=40, language="en", sample="head", seed=bench.SEED_BENCHMARK,
        warmup=2, chunk_size=8, runs=1, spacy_records=10, timestamp="2026-05-31T00:00:00Z",
    )
    assert seen["n"] == 10   # spaCy timed on the bounded sub-slice, not all 40 records


def test_seed_constant_is_distinct():
    # must not collide with the established corpus-generation seeds
    assert bench.SEED_BENCHMARK not in {42, 162, 172, 4242, 91237}
