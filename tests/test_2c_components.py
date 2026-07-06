"""Tests for v2.2.0 sub-project 2C: name pools, B-5 art9 array, B-7 jurisdiction count."""
from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import generate_records as gr  # noqa: E402


def _script_of(s: str) -> set[str]:
    return {unicodedata.name(c).split(" ")[0] for c in s if c.strip()}

def test_name_db_has_native_el_bn_he():
    for lang, marker in (("el", "GREEK"), ("bn", "BENGALI"), ("he", "HEBREW")):
        assert lang in gr.NAME_DB, f"{lang} missing from NAME_DB"
        firsts, lasts = gr.NAME_DB[lang]
        assert 12 <= len(firsts) and 10 <= len(lasts), f"{lang} pools too small"
        sample = "".join(firsts + lasts)
        assert any(marker in n for n in _script_of(sample)), f"{lang} names are not {marker}-script"


sys.path.insert(0, str(ROOT / "src"))

def test_b5_art9_array_derives_from_crosswalk():
    import enrich  # scripts/enrich.py
    from pii_anon_datasets.compliance.entity_crosswalk import _ART9_SPECIAL_CATEGORY
    recs = [
        {"annotations": [{"entity_type": "GENETIC_DATA"}, {"entity_type": "PERSON_NAME"}]},
        {"annotations": [{"entity_type": "PERSON_NAME"}, {"entity_type": "EMAIL_ADDRESS"}]},
        {"annotations": [{"entity_type": "ETHNICITY"}, {"entity_type": "RELIGIOUS_BELIEF"}]},
    ]
    n = enrich.enrich_art9_special_categories(recs)
    assert recs[0]["art9_special_categories"] == ["GENETIC_DATA"]
    assert recs[1]["art9_special_categories"] == []
    assert recs[2]["art9_special_categories"] == ["ETHNICITY", "RELIGIOUS_BELIEF"]  # sorted
    assert n == 2  # records with >=1 art9 type
    for r in recs:
        assert set(r["art9_special_categories"]) <= set(_ART9_SPECIAL_CATEGORY)


def test_b7_jurisdiction_identifier_types_subset_of_canonical():
    from pii_anon_datasets import taxonomy as tx
    j = tx.JURISDICTION_IDENTIFIER_TYPES
    assert set(j) <= set(tx.CANONICAL_ENTITY_TYPES), "jurisdiction list must be canonical types"
    assert tx.JURISDICTION_IDENTIFIER_COUNT == len(j)
    assert 5 <= tx.JURISDICTION_IDENTIFIER_COUNT <= 20  # a plausible, non-exhaustive count
    assert "SOCIAL_SECURITY_NUMBER" in j and "PASSPORT_NUMBER" in j


def test_repin_declares_new_head_langs(tmp_path):
    import json as _json
    sys.path.insert(0, str(ROOT / "scripts"))
    import repin_lattice_snapshot as rp
    snap = {"_comment": "x", "by_entity_type": {"PERSON_NAME": 100000},
            "by_language": {"en": 100000, "ru": 431, "th": 277, "el": 236, "bn": 229, "he": 229},
            "source_version": "1.3.0"}
    p = tmp_path / "snap.json"
    p.write_text(_json.dumps(snap), encoding="utf-8")
    rp.declare_head(p, ["ru", "th", "el", "bn", "he"], count=21000, source_version="2.2.0-dev")
    out = _json.loads(p.read_text(encoding="utf-8"))
    for lang in ("ru", "th", "el", "bn", "he"):
        assert out["by_language"][lang] >= 753
    assert out["by_language"]["en"] == 100000  # untouched
    assert out["source_version"] == "2.2.0-dev"


def test_name_db_th_is_native_and_parallel():
    # native lists exist, are Thai-script, index-parallel to the romanized lists, and NAME_DB uses them
    assert len(gr.FIRST_NAMES_TH_NATIVE) == len(gr.FIRST_NAMES_TH)
    assert len(gr.LAST_NAMES_TH_NATIVE) == len(gr.LAST_NAMES_TH)
    firsts, lasts = gr.NAME_DB["th"]
    assert firsts is gr.FIRST_NAMES_TH_NATIVE and lasts is gr.LAST_NAMES_TH_NATIVE
    sample = "".join(gr.FIRST_NAMES_TH_NATIVE + gr.LAST_NAMES_TH_NATIVE)
    assert any("THAI" in n for n in _script_of(sample)), "th native names are not THAI-script"
    # no romanized leftovers (no ASCII letters in the native lists)
    assert not any(c.isascii() and c.isalpha() for c in sample), "native lists contain Latin letters"
