"""Tests for scripts/generate_lattice_fill (P4; AX-002 determinism + idempotence/convergence)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import generate_lattice_fill as fill  # noqa: E402
import lattice_audit as audit  # noqa: E402
from pii_anon_datasets.stats.lattice import build_committed_lattice  # noqa: E402


def _tiny_lattice():
    # 3 real types so taxonomy.risk_tier works; IBAN critical, PERSON_NAME standard, AGE long_tail.
    return json.loads(build_committed_lattice(
        entity_registry={"IBAN": "financial", "PERSON_NAME": "identity_demographics",
                         "AGE": "identity_demographics"},
        lang_records={"en": 5000, "xx": 100},
        entity_positives={"IBAN": 5000, "PERSON_NAME": 5000, "AGE": 100},
        domains=("general",), difficulties=("easy",), dimensions=("diverse_pii_types",),
        adversarial_types=("base64_encoding",), eval_families=(), adv_tracks=("clean",),
        source_metadata_version="test",
    ).to_json())


def _empty_corpus(tmp_path):
    p = tmp_path / "corpus.jsonl"
    p.write_text("", encoding="utf-8")
    return p


def test_cell_seed_is_coordinate_only():
    assert fill.cell_seed("AxE:a=b|c=d") == fill.cell_seed("AxE:a=b|c=d")
    assert fill.cell_seed("AxE:a=b|c=d") != fill.cell_seed("AxE:a=b|c=e")


def test_fill_is_deterministic(tmp_path):
    lat = _tiny_lattice()
    corpus = _empty_corpus(tmp_path)
    recs1, rep1 = fill.plan_fill(corpus, lat, max_records=400)
    recs2, rep2 = fill.plan_fill(corpus, lat, max_records=400)
    assert rep1 == rep2
    # byte-identical migrated records (content-addressed ids + deterministic text)
    assert [r["record_id"] for r in recs1] == [r["record_id"] for r in recs2]
    assert [r["text"] for r in recs1] == [r["text"] for r in recs2]


def test_generated_records_are_synthetic_v2_and_provenanced(tmp_path):
    lat = _tiny_lattice()
    recs, _ = fill.plan_fill(_empty_corpus(tmp_path), lat, max_records=50)
    assert recs, "expected some fill records for an empty corpus"
    for r in recs[:50]:
        assert r["schema_version"] == "2.0.0"
        assert isinstance(r.get("tier3_evaluation"), dict)
        p = r["provenance"]
        assert p["source_type"] == "synthetic_lattice_enrichment"
        assert p["lattice_seed"] == fill.SEED_LATTICE
        assert p["lattice_cell_id"] and p["lattice_tier"]


def test_max_records_cap_truncates(tmp_path):
    lat = _tiny_lattice()
    recs, rep = fill.plan_fill(_empty_corpus(tmp_path), lat, max_records=10)
    assert len(recs) == 10
    assert rep["max_records_cap_hit"] is True


def test_fill_then_merge_is_convergent(tmp_path):
    """fill → add to corpus → re-audit: every count-gated cell now meets its target (no deficit)."""
    lat = _tiny_lattice()
    corpus = _empty_corpus(tmp_path)
    recs, _ = fill.plan_fill(corpus, lat, max_records=None)
    merged = tmp_path / "merged.jsonl"
    merged.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    remaining = audit.deficits(audit.audit_positives(merged, lat), lat)
    assert remaining == [], f"expected zero deficit after fill, got {[d['id'] for d in remaining]}"
    # and a second fill round generates nothing (idempotent at the corpus level)
    recs2, rep2 = fill.plan_fill(merged, lat, max_records=None)
    assert rep2["records_generated"] == 0
