"""Tests for scripts/lattice_audit (P4; FR-029, NFR-018 counting + deficit math)."""
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import lattice_audit as audit  # noqa: E402


def _cell(dims, *, tier="standard", target=753, gated=True):
    cid = "X:" + "|".join(f"{k}={dims[k]}" for k in sorted(dims))
    return {"id": cid, "dimensions": dims, "tier": tier, "target_n": target,
            "committed": True, "count_gated": gated, "interaction": "x"}


def _lattice():
    return {"cells": [
        _cell({"entity_type": "IBAN"}, tier="critical", target=1522),
        _cell({"language": "en"}),
        _cell({"entity_type": "IBAN", "language": "en"}, tier="critical", target=1522),
        _cell({"adversarial": "base64_encoding"}),
        _cell({"adversarial": "base64_encoding", "entity_type": "IBAN"}),
        _cell({"adv_track": "clean", "domain": "general"}),
        _cell({"adv_track": "adversarial", "domain": "general"}),
        _cell({"domain": "general", "eval_family": "detection"}, gated=False),  # seam → ignored
    ]}


def _rec(annots, *, language="en", domain="general", difficulty="easy",
         dimension="diverse_pii_types", adversarial=None):
    return {
        "language": language, "domain": domain, "difficulty_level": difficulty,
        "primary_dimension": dimension, "adversarial": {"type": adversarial},
        "annotations": [{"entity_type": t} for t in annots],
    }


def _write(tmp_path, recs, name="c.jsonl"):
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    return p


def test_counts_annotations_not_records(tmp_path):
    lat = _lattice()
    corpus = _write(tmp_path, [_rec(["IBAN", "IBAN", "PERSON_NAME"])])
    counts = audit.audit_positives(corpus, lat)
    assert counts["X:entity_type=IBAN"] == 2          # two IBAN annotations
    assert counts["X:language=en"] == 3               # all three annotations are in en
    assert counts["X:entity_type=IBAN|language=en"] == 2
    assert counts["X:adv_track=clean|domain=general"] == 3   # all clean+general


def test_only_committed_count_gated_cells_counted(tmp_path):
    lat = _lattice()
    corpus = _write(tmp_path, [_rec(["IBAN"], domain="general")])
    counts = audit.audit_positives(corpus, lat)
    # the non-gated eval_family seam cell is absent from the counter entirely
    assert all("eval_family" not in cid for cid in counts)


def test_adversarial_routing(tmp_path):
    lat = _lattice()
    corpus = _write(tmp_path, [_rec(["IBAN"], adversarial="base64_encoding")])
    counts = audit.audit_positives(corpus, lat)
    assert counts["X:adversarial=base64_encoding"] == 1
    assert counts["X:adversarial=base64_encoding|entity_type=IBAN"] == 1
    assert counts["X:adv_track=adversarial|domain=general"] == 1
    assert counts["X:adv_track=clean|domain=general"] == 0     # this record is adversarial


def test_gz_and_plain_equivalent(tmp_path):
    lat = _lattice()
    recs = [_rec(["IBAN", "IBAN"]), _rec(["IBAN"], adversarial="base64_encoding")]
    plain = _write(tmp_path, recs, "c.jsonl")
    gzp = tmp_path / "c.jsonl.gz"
    with gzip.open(gzp, "wt", encoding="utf-8") as f:
        f.write("\n".join(json.dumps(r) for r in recs) + "\n")
    assert audit.audit_positives(plain, lat) == audit.audit_positives(gzp, lat)


def test_deficits(tmp_path):
    lat = _lattice()
    corpus = _write(tmp_path, [_rec(["IBAN"])])   # IBAN marginal target 1522, observed 1
    defs = {d["id"]: d for d in audit.deficits(audit.audit_positives(corpus, lat), lat)}
    assert defs["X:entity_type=IBAN"]["deficit"] == 1521
    assert defs["X:entity_type=IBAN"]["observed"] == 1
    # a cell at/over target is NOT a deficit
    assert "X:language=en" in defs  # en marginal observed 1 < 753 → still a deficit here
    # ids are sorted
    ids = [d["id"] for d in audit.deficits(audit.audit_positives(corpus, lat), lat)]
    assert ids == sorted(ids)


def test_effective_counts_seam_not_implemented(tmp_path):
    import pytest
    lat = _lattice()
    corpus = _write(tmp_path, [_rec(["IBAN"])])
    with pytest.raises(NotImplementedError):
        audit.audit_positives(corpus, lat, effective=True)
