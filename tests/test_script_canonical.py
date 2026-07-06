"""Tests for script-field canonicalization and reg_gdpr discriminative property."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("vc", ROOT / "scripts" / "validate_contribution.py")
_vc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vc)
LANG_SCRIPT = _vc.LANG_SCRIPT


def test_script_field_is_canonical_iso15924():
    from pii_anon_datasets import load_dataset
    bad = []
    for r in load_dataset(split="test"):
        lang, script = r.get("language"), r.get("script")
        if lang in LANG_SCRIPT and script != LANG_SCRIPT[lang]:
            bad.append((lang, script, LANG_SCRIPT[lang]))
    assert not bad, f"{len(bad)} records have non-canonical script, e.g. {bad[:5]}"


def test_reg_gdpr_is_discriminative():
    from pii_anon_datasets import load_dataset
    from pii_anon_datasets.compliance.crosswalk import RegimeStatus, crosswalk_record
    recs = load_dataset(split="test")
    statuses = {crosswalk_record(r).gdpr for r in recs}
    assert RegimeStatus.OUT_OF_SCOPE in statuses, "reg_gdpr is still constant (no non-personal records)"
    assert RegimeStatus.IN_SCOPE in statuses
