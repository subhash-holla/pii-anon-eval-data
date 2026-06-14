"""Tests for the validate.py committed-cell power gate (P6; NFR-018, FR-029)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import validate  # noqa: E402


def _lattice(tmp_path, target=753):
    lat = {"cells": [
        {"id": "X:entity_type=IBAN", "dimensions": {"entity_type": "IBAN"}, "tier": "critical",
         "target_n": target, "committed": True, "count_gated": True, "interaction": "marginal:entity_type"},
        {"id": "X:entity_type=PERSON_NAME", "dimensions": {"entity_type": "PERSON_NAME"}, "tier": "standard",
         "target_n": target, "committed": True, "count_gated": True, "interaction": "marginal:entity_type"},
        {"id": "DxT:domain=general|eval_family=detection", "dimensions": {"domain": "general", "eval_family": "detection"},
         "tier": "standard", "target_n": target, "committed": True, "count_gated": False, "interaction": "domain_x_track"},
    ]}
    p = tmp_path / "lat.json"
    p.write_text(json.dumps(lat), encoding="utf-8")
    return p


def _corpus(tmp_path, iban_n, person_n):
    recs = []
    for _ in range(iban_n):
        recs.append({"language": "en", "domain": "general", "difficulty_level": "easy",
                     "primary_dimension": "diverse_pii_types", "adversarial": {"type": None},
                     "annotations": [{"entity_type": "IBAN"}]})
    for _ in range(person_n):
        recs.append({"language": "en", "domain": "general", "difficulty_level": "easy",
                     "primary_dimension": "diverse_pii_types", "adversarial": {"type": None},
                     "annotations": [{"entity_type": "PERSON_NAME"}]})
    p = tmp_path / "corpus.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    return p


def test_powered_corpus_passes(tmp_path):
    lat = _lattice(tmp_path, target=5)
    corpus = _corpus(tmp_path, iban_n=5, person_n=5)
    assert validate.check_committed_cell_power(corpus, lat) == []


def test_underpowered_cell_fails_with_detail(tmp_path):
    lat = _lattice(tmp_path, target=10)
    corpus = _corpus(tmp_path, iban_n=3, person_n=10)   # IBAN under (3<10), PERSON_NAME ok
    errs = validate.check_committed_cell_power(corpus, lat)
    assert len(errs) == 1
    assert "X:entity_type=IBAN" in errs[0]
    assert "observed=3" in errs[0] and "target=10" in errs[0] and "deficit 7" in errs[0]


def test_seam_cell_never_gated(tmp_path):
    # the non-count-gated eval-family cell is ignored even with an empty corpus
    lat = _lattice(tmp_path, target=10)
    corpus = _corpus(tmp_path, iban_n=10, person_n=10)
    errs = validate.check_committed_cell_power(corpus, lat)
    assert all("eval_family" not in e for e in errs)
    assert errs == []


def test_missing_lattice_reports_error(tmp_path):
    corpus = _corpus(tmp_path, 5, 5)
    errs = validate.check_committed_cell_power(corpus, tmp_path / "nope.json")
    assert errs and "not found" in errs[0]


def test_errors_sorted_and_deterministic(tmp_path):
    lat = _lattice(tmp_path, target=10)
    corpus = _corpus(tmp_path, iban_n=1, person_n=1)
    a = validate.check_committed_cell_power(corpus, lat)
    b = validate.check_committed_cell_power(corpus, lat)
    assert a == b and len(a) == 2
    assert [e.split("]")[0] for e in a] == sorted(e.split("]")[0] for e in a)
