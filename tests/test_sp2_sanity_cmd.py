import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import sync_cards  # noqa: E402


def test_sanity_renders_floor_and_ceiling(tmp_path):
    import json

    recs = [
        {
            "language": "en",
            "text": "Call John Smith.",
            "annotations": [
                {"entity_type": "PERSON_NAME", "start": 5, "end": 15, "text": "John Smith"}
            ],
        }
    ]
    p = tmp_path / "recs.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in recs))
    md = tmp_path / "CARD.md"
    md.write_text("<!-- BEGIN-SANITY -->\nold\n<!-- END-SANITY -->\n")
    rc = sync_cards.main(["sanity", "--split", str(p), "--file", str(md), "--marker", "SANITY"])
    assert rc == 0
    out = md.read_text()
    assert "oracle" in out and "null" in out and "always_person_name" in out
    assert "BEGIN-SANITY" in out and "old" not in out
