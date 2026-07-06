"""LANG_SCRIPT must cover every language in the corpus (no record left un-canonicalizable)."""
import gzip
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("vc", ROOT / "scripts" / "validate_contribution.py")
_vc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vc)
CORPUS = ROOT / "src" / "pii_anon_datasets" / "data" / "pii_anon.jsonl.gz"


def test_lang_script_covers_all_corpus_languages():
    langs = set()
    with gzip.open(CORPUS, "rt", encoding="utf-8") as f:
        for line in f:
            langs.add(json.loads(line).get("language"))
    missing = sorted(lang for lang in langs if lang and lang not in _vc.LANG_SCRIPT)
    assert not missing, f"LANG_SCRIPT missing corpus languages: {missing}"
