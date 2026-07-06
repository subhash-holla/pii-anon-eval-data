"""Task 5 — Wilson recall lower-bound per ISO-15924 script (Path-B, multilingual aggregate)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import multilingual_by_script_lb as m  # noqa: E402


def test_script_bucketing_and_wilson_lb(tmp_path):
    results = {
        "detectors": {
            "gliner": {
                "by_language": {
                    "en": {"counts": {"tp": 80, "fp": 10, "fn": 20}},
                    "ru": {"counts": {"tp": 30, "fp": 5, "fn": 70}},
                }
            }
        }
    }
    p = tmp_path / "br.json"
    p.write_text(json.dumps(results))
    table = m.build_by_script(str(p))
    cyr = table["Cyrillic"]["gliner"]
    assert abs(cyr["recall"] - 0.30) < 1e-9
    assert 0.0 < cyr["recall_lb"] < 0.30
    assert table["Latin"]["gliner"]["recall_lb"] < 0.80
