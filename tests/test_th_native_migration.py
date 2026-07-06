"""Unit tests for the v2.2.0 SP-I Thai-native-names migration (approach γ')."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import th_native_names_migration as mg  # noqa: E402


def test_map_covers_all_romanized_and_is_thai():
    import generate_records as gr
    for roman in gr.FIRST_NAMES_TH + gr.LAST_NAMES_TH:
        assert roman.lower() in mg.TH_MAP, f"{roman} missing from map"
        v = mg.TH_MAP[roman.lower()]
        assert any(ord(c) >= 0x0E00 and ord(c) <= 0x0E7F for c in v), f"{v} not Thai-script"

def test_translit_name_full_and_variants():
    assert mg.translit_name("Pichit Srisai") == mg.TH_MAP["pichit"] + " " + mg.TH_MAP["srisai"]
    assert mg.translit_name("Dr. Rattanakorn") == "Dr. " + mg.TH_MAP["rattanakorn"]
    assert mg.translit_name("Prayut") == mg.TH_MAP["prayut"]
    assert mg.translit_name("John Smith") == "John Smith"

def test_translit_email_keeps_number_and_domain():
    out, changed = mg.translit_email("pichit.srisai31@hotmail.com")
    assert changed is True
    assert out == f"{mg.TH_MAP['pichit']}.{mg.TH_MAP['srisai']}31@hotmail.com"
    out2, changed2 = mg.translit_email("user4821@example.com")
    assert changed2 is False and out2 == "user4821@example.com"


def _rec(text, anns, language="th"):
    return {"language": language, "text": text,
            "annotations": [dict(a) for a in anns], "provenance": {"generation_seed": 1}}

def test_migrate_record_full_name_and_email_offsets():
    text = "Record for Pichit Srisai, contact pichit.srisai31@hotmail.com."
    anns = [{"entity_type": "PERSON_NAME", "start": 11, "end": 24, "text": "Pichit Srisai"},
            {"entity_type": "EMAIL_ADDRESS", "start": 34, "end": 61, "text": "pichit.srisai31@hotmail.com"}]
    rec, n, flags = mg.migrate_record(_rec(text, anns))
    pn, em = rec["annotations"]
    assert pn["text"] == mg.TH_MAP["pichit"] + " " + mg.TH_MAP["srisai"]
    assert em["text"] == f"{mg.TH_MAP['pichit']}.{mg.TH_MAP['srisai']}31@hotmail.com"
    for a in rec["annotations"]:
        assert rec["text"][a["start"]:a["end"]] == a["text"]
    assert n == 2

def test_migrate_record_trailing_span_shifts():
    text = "X Pichit Srisai Y"
    anns = [{"entity_type": "PERSON_NAME", "start": 2, "end": 15, "text": "Pichit Srisai"},
            {"entity_type": "GENERIC", "start": 16, "end": 17, "text": "Y"}]
    rec, n, flags = mg.migrate_record(_rec(text, anns))
    y = rec["annotations"][1]
    assert rec["text"][y["start"]:y["end"]] == "Y"

def test_migrate_record_idempotent():
    text = "Record for Pichit Srisai."
    anns = [{"entity_type": "PERSON_NAME", "start": 11, "end": 24, "text": "Pichit Srisai"}]
    rec1, n1, _ = mg.migrate_record(_rec(text, anns))
    rec2, n2, _ = mg.migrate_record(rec1)
    assert n2 == 0 and rec2 == rec1

def test_migrate_record_non_thai_passthrough():
    text = "Record for Pichit Srisai."
    anns = [{"entity_type": "PERSON_NAME", "start": 11, "end": 24, "text": "Pichit Srisai"}]
    rec_in = _rec(text, anns, language="en")
    rec, n, _ = mg.migrate_record(rec_in)
    assert n == 0 and rec == rec_in

def test_migrate_record_multi_person_consistent():
    text = "Wanida Bunnak and Prasit Charoenpol met. wanida.bunnak5@a.com prasit.charoenpol9@b.com"
    anns = [{"entity_type": "PERSON_NAME", "start": 0, "end": 13, "text": "Wanida Bunnak"},
            {"entity_type": "PERSON_NAME", "start": 18, "end": 35, "text": "Prasit Charoenpol"},
            {"entity_type": "EMAIL_ADDRESS", "start": 41, "end": 61, "text": "wanida.bunnak5@a.com"},
            {"entity_type": "EMAIL_ADDRESS", "start": 62, "end": 86, "text": "prasit.charoenpol9@b.com"}]
    rec, n, _ = mg.migrate_record(_rec(text, anns))
    for a in rec["annotations"]:
        assert rec["text"][a["start"]:a["end"]] == a["text"]
    assert rec["annotations"][0]["text"] == mg.TH_MAP["wanida"] + " " + mg.TH_MAP["bunnak"]


def test_migrate_file_thai_changes_others_identical(tmp_path):
    th = _rec("Record for Pichit Srisai, contact pichit.srisai31@hotmail.com.",
              [{"entity_type": "PERSON_NAME", "start": 11, "end": 24, "text": "Pichit Srisai"},
               {"entity_type": "EMAIL_ADDRESS", "start": 34, "end": 61, "text": "pichit.srisai31@hotmail.com"}])
    en = _rec("Hello Pichit Srisai.",
              [{"entity_type": "PERSON_NAME", "start": 6, "end": 19, "text": "Pichit Srisai"}], language="en")
    p = tmp_path / "c.jsonl.gz"
    with gzip.open(p, "wt", encoding="utf-8") as f:
        for r in (th, en):
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    raw_before = list(gzip.open(p, "rt", encoding="utf-8"))
    stats = mg.migrate_file(str(p))
    raw_after = list(gzip.open(p, "rt", encoding="utf-8"))
    assert raw_after[1] == raw_before[1]          # the en line is byte-identical
    assert raw_after[0] != raw_before[0]          # the th line changed
    assert stats["records"] == 2 and stats["th_records"] == 1 and stats["records_changed"] == 1


def test_partial_romanized_name_is_flagged():
    text = "Hello Pichit Foobar."
    anns = [{"entity_type": "PERSON_NAME", "start": 6, "end": 19, "text": "Pichit Foobar"}]
    rec, n, flags = mg.migrate_record(_rec(text, anns))
    assert n == 1  # edit still applied
    assert any(f[0] == "person_name_residual_romanized" for f in flags)

def test_formal_honorific_not_flagged():
    text = "Hello Dr. Rattanakorn."
    anns = [{"entity_type": "PERSON_NAME", "start": 6, "end": 21, "text": "Dr. Rattanakorn",
             "mention_variant": "formal"}]
    rec, n, flags = mg.migrate_record(_rec(text, anns))
    assert n == 1
    assert not any(f[0] == "person_name_residual_romanized" for f in flags)
    assert rec["annotations"][0]["text"] == "Dr. " + mg.TH_MAP["rattanakorn"]
