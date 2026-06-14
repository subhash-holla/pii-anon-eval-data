"""RED→GREEN tests for the per-artifact sha256 provenance index (NFR-043; AX-005 element 4).

Pure-stdlib. Validates: full coverage of the given files with correct (hashlib-cross-checked) sha256;
byte-stable index across calls for a fixed ``generated_at``; tamper-detection (rewriting a file's bytes
changes ITS sha256); missing path raises ``FileNotFoundError`` (never a fabricated hash).
"""
from __future__ import annotations

import hashlib
import json

import pytest
from pii_anon_datasets.assessment import provenance


def _write(path, data: bytes) -> None:
    path.write_bytes(data)


def test_index_covers_all_with_correct_sha256(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.bin"
    c = tmp_path / "c.json"
    payloads = {a: b"alpha\n", b: b"\x00\x01\x02beta", c: b'{"k": 1}\n'}
    for p, d in payloads.items():
        _write(p, d)

    index = provenance.build_provenance_index(
        [c, a, b], generated_at="2026-06-01T00:00:00Z"
    )

    assert index["schema"] == provenance.PROVENANCE_SCHEMA
    assert index["harness_version"] == provenance.HARNESS_VERSION
    assert index["generated_at"] == "2026-06-01T00:00:00Z"

    arts = index["artifacts"]
    assert len(arts) == 3
    # sorted by path for determinism (basenames here)
    assert [x["path"] for x in arts] == sorted(["a.txt", "b.bin", "c.json"])

    by_path = {x["path"]: x for x in arts}
    for p, d in payloads.items():
        rec = by_path[p.name]
        assert rec["sha256"] == hashlib.sha256(d).hexdigest()
        assert rec["bytes"] == len(d)


def test_sha256_file_matches_hashlib(tmp_path):
    p = tmp_path / "blob"
    data = b"x" * 5000
    _write(p, data)
    assert provenance.sha256_file(p) == hashlib.sha256(data).hexdigest()


def test_index_is_byte_stable_for_fixed_generated_at(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    _write(a, b"one")
    _write(b, b"two")

    gen = "2026-06-01T12:34:56Z"
    i1 = provenance.build_provenance_index([a, b], generated_at=gen)
    i2 = provenance.build_provenance_index([b, a], generated_at=gen)  # order swapped
    assert i1 == i2
    s1 = json.dumps(i1, sort_keys=True)
    s2 = json.dumps(i2, sort_keys=True)
    assert s1 == s2


def test_tamper_changes_sha256(tmp_path):
    p = tmp_path / "doc.txt"
    _write(p, b"original-content")
    before = provenance.build_provenance_index([p], generated_at="2026-06-01T00:00:00Z")
    sha_before = before["artifacts"][0]["sha256"]

    _write(p, b"TAMPERED-content!!")  # rewrite the same path
    after = provenance.build_provenance_index([p], generated_at="2026-06-01T00:00:00Z")
    sha_after = after["artifacts"][0]["sha256"]

    assert sha_before != sha_after
    assert sha_after == hashlib.sha256(b"TAMPERED-content!!").hexdigest()


def test_missing_path_raises_filenotfound(tmp_path):
    present = tmp_path / "here.txt"
    _write(present, b"present")
    missing = tmp_path / "gone.txt"  # never created
    with pytest.raises(FileNotFoundError):
        provenance.build_provenance_index([present, missing], generated_at="2026-06-01T00:00:00Z")


def test_write_provenance_index_canonical_json(tmp_path):
    p = tmp_path / "a.txt"
    _write(p, b"data")
    index = provenance.build_provenance_index([p], generated_at="2026-06-01T00:00:00Z")
    out = tmp_path / "index.json"
    written = provenance.write_provenance_index(index, out)

    assert written == out
    text = out.read_text(encoding="utf-8")
    assert text.endswith("\n")
    # canonical: sorted keys, round-trips to the same dict
    assert json.loads(text) == index
    assert text == json.dumps(index, sort_keys=True, ensure_ascii=False) + "\n"
