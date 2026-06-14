"""Tests for the data integrity manifest + migrate idempotence (P5; M2, AX-002)."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import write_manifest as wm  # noqa: E402
import lattice_targeting as lt  # noqa: E402
from pii_anon_datasets.migration import migrate_record  # noqa: E402


def test_sha256_deterministic(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"committed-lattice power\n")
    assert wm._sha256(p) == wm._sha256(p)
    q = tmp_path / "y.bin"
    q.write_bytes(b"committed-lattice power!")
    assert wm._sha256(p) != wm._sha256(q)


def test_compute_manifest_is_idempotent():
    # reads the real package data; two computations must be byte-identical (NFR-004)
    assert wm.compute_manifest() == wm.compute_manifest()
    assert "# pii-anon data manifest" in wm.compute_manifest()


def test_migrate_record_idempotent_on_v2():
    # the merge normalization re-applies migrate_record only to non-v2 records, but it must be a
    # fixed point on already-v2 records so a double-apply never mutates the corpus.
    f = lt.PIIFactory(random.Random(7), "en")
    rec = lt.gen_targeted_record(f, entity_type="IBAN", language="en", domain="financial",
                                 difficulty="easy", adversarial_type=None, rng=random.Random(7))
    once = migrate_record(rec)
    twice = migrate_record(dict(once))
    assert once["record_id"] == twice["record_id"]
    assert once["schema_version"] == twice["schema_version"] == "2.0.0"
    assert once["annotations"] == twice["annotations"]
    assert once["text"] == twice["text"]
