"""Tests for scripts/lattice_targeting (P3; AX-001 synthetic-only, AX-002 determinism).

Pins: EMITTERS cover EXACTLY the 63 canonical types; each emits a valid PIIValue; every
targeted record has exactly one positive of the requested type; adversarial cells genuinely
obfuscate; records normalize to valid v2.0.0; generation is deterministic.
"""
import random
import re
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import lattice_targeting as lt  # noqa: E402

from pii_anon_datasets import taxonomy as tx  # noqa: E402
from pii_anon_datasets.migration import migrate_record  # noqa: E402
from pii_anon_datasets.stats.lattice import DEFAULT_DETECTION_ADVERSARIAL_TYPES  # noqa: E402

_PLACEHOLDER = re.compile(r"\{\w+\}")
_CRITICAL = tx.types_in_tier("critical")


def _factory(seed=1, lang="en"):
    return lt.PIIFactory(random.Random(seed), lang)


# ── emitter completeness + validity (AX-001 fail-loud) ───────────────────────────────────
def test_emitters_cover_exactly_63_canonical_types():
    assert set(lt.EMITTERS) == set(tx.CANONICAL_ENTITY_TYPES)
    assert len(lt.EMITTERS) == 63


def test_every_emitter_produces_valid_pii_value():
    f = _factory()
    for t in tx.CANONICAL_ENTITY_TYPES:
        pv = lt.EMITTERS[t](f)
        assert pv.entity_type == t
        assert pv.category == tx.category_of(t)
        assert pv.sensitivity_class in tx.SENSITIVITY_CLASSES
        assert isinstance(pv.value, str) and pv.value != ""


def test_committed_adversarial_types_all_have_transforms():
    for adv in DEFAULT_DETECTION_ADVERSARIAL_TYPES:
        assert adv in lt.ADVERSARIAL_TRANSFORMS


# ── the one-positive-per-cell invariant (makes deficit == records_to_generate) ───────────
def test_every_type_yields_exactly_one_target_positive():
    f = _factory(seed=5)
    for t in tx.CANONICAL_ENTITY_TYPES:
        rec = lt.gen_targeted_record(f, entity_type=t, language="en", domain="general",
                                     difficulty="easy", adversarial_type=None,
                                     rng=random.Random(5))
        counts = Counter(a["entity_type"] for a in rec["annotations"])
        assert counts[t] == 1, (t, dict(counts))


def test_unknown_type_fails_loud():
    with pytest.raises(KeyError):
        lt.gen_targeted_record(_factory(), entity_type="NOPE", language="en", domain="general",
                               difficulty="easy", adversarial_type=None, rng=random.Random(1))


def test_uncommitted_adversarial_type_fails_loud():
    with pytest.raises(KeyError):
        lt.gen_targeted_record(_factory(), entity_type="IBAN", language="en", domain="general",
                               difficulty="easy", adversarial_type="not_a_real_attack",
                               rng=random.Random(1))


# ── adversarial fidelity: a committed adv cell is a GENUINE attack, never a bare tag ──────
def test_adversarial_records_genuinely_obfuscate_every_critical_type():
    for adv in DEFAULT_DETECTION_ADVERSARIAL_TYPES:
        for t in _CRITICAL:
            f = _factory(seed=11)
            clean = lt.gen_targeted_record(f, entity_type=t, language="en", domain="general",
                                           difficulty="moderate", adversarial_type=None,
                                           rng=random.Random(11))
            f2 = _factory(seed=11)
            adv_rec = lt.gen_targeted_record(f2, entity_type=t, language="en", domain="general",
                                             difficulty="moderate", adversarial_type=adv,
                                             rng=random.Random(11))
            assert adv_rec["adversarial"]["type"] == adv
            clean_val = next(a["text"] for a in clean["annotations"] if a["entity_type"] == t)
            adv_val = next(a["text"] for a in adv_rec["annotations"] if a["entity_type"] == t)
            assert adv_val != clean_val, f"{adv} did not perturb a {t} value"


# ── records normalize to valid v2.0.0 (closes the v1-shape gap) ──────────────────────────
def test_targeted_record_normalizes_to_valid_v2():
    f = _factory(seed=3, lang="de")
    rec = lt.gen_targeted_record(f, entity_type="CVV", language="de", domain="financial",
                                 difficulty="hard", adversarial_type=None, rng=random.Random(3))
    m = migrate_record(rec)
    assert m["schema_version"] == "2.0.0"
    assert isinstance(m.get("tier3_evaluation"), dict)
    assert len(m["record_id"]) == 36                       # content-addressed uuid5
    assert not _PLACEHOLDER.search(m["text"])               # no leftover {slot}
    for a in m["annotations"]:                              # offset integrity
        assert m["text"][a["start"]:a["end"]] == a["text"]
        assert a["entity_type"] in tx.CANONICAL_ENTITY_TYPES


def test_synthetic_provenance_preserved_through_migrate():
    f = _factory(seed=4)
    rec = lt.gen_targeted_record(f, entity_type="IBAN", language="en", domain="financial",
                                 difficulty="easy", adversarial_type=None, rng=random.Random(4))
    assert rec["provenance"]["source_type"] == "synthetic"   # fill script restamps to lattice tag
    m = migrate_record(rec)
    assert m["provenance"].get("source_type")                # survives migration


# ── determinism (AX-002): same seeds → byte-identical migrated record ─────────────────────
def test_generation_is_deterministic():
    def gen():
        f = lt.PIIFactory(random.Random(42), "fr")
        rec = lt.gen_targeted_record(f, entity_type="SOCIAL_SECURITY_NUMBER", language="fr",
                                     domain="general", difficulty="moderate",
                                     adversarial_type="ocr_artifact", rng=random.Random(99))
        return migrate_record(rec)
    a, b = gen(), gen()
    assert a["record_id"] == b["record_id"]
    assert a["text"] == b["text"]
    assert a["annotations"] == b["annotations"]
