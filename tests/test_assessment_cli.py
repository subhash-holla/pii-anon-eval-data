"""CAP-02 S9 — ENTRY-A sampler CLI (the DC-20 surface: `python -m pii_anon_datasets.assessment.sample`).

stdout = the manifest path only (machine channel, SP-U2); stderr = the PowerMatrix verdict banner + worst
named shortfalls (human channel). GATE-P3 (SP-W2): a shortfall is a non-fatal honesty FLAG on the default
preset, but exits non-zero under --block-on-underpower (or full-corpus). FR-032/033/034/035 + NFR-035/036.
"""
from __future__ import annotations

import json
from pathlib import Path

from pii_anon_datasets.assessment import manifest as M
from pii_anon_datasets.assessment import sample as S


def _write(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _rec(rid: str, ets: list[str]) -> dict:
    return {
        "record_id": rid, "text": "x" * 40, "language": "en", "domain": "general",
        "difficulty_level": "easy", "primary_dimension": "diverse_pii_types", "adversarial": None,
        "annotations": [{"entity_type": e, "start": 0, "end": 5} for e in ets],
    }


def _lattice_file(path: Path, target_n: int = 2) -> None:
    path.write_text(json.dumps({
        "lattice_version": "test-cli",
        "cells": [{"id": "M:entity_type=EMAIL_ADDRESS", "dimensions": {"entity_type": "EMAIL_ADDRESS"},
                   "tier": "long_tail", "target_n": target_n, "count_gated": True}],
    }), encoding="utf-8")


def test_cli_writes_manifest_and_prints_path(tmp_path: Path, capsys) -> None:
    corpus = tmp_path / "c.jsonl"
    _write(corpus, [_rec(f"r{i}", ["EMAIL_ADDRESS"]) for i in range(5)])
    latf = tmp_path / "lat.json"
    _lattice_file(latf)
    out = tmp_path / "manifest.json"
    rc = S.main([
        "--preset", "powered-representative", "--seed", "7",
        "--corpus", str(corpus), "--lattice", str(latf), "--out", str(out),
    ])
    assert rc == 0
    captured = capsys.readouterr()
    assert str(out) in captured.out  # stdout carries the manifest path (pipeable)
    man = M.read_manifest(out)
    assert man["schema"] == M.SCHEMA
    assert man["preset"] == "powered-representative"
    assert "synthetic" in man["caveat"].lower()
    assert man["repro"]["corpus_content_hash"]  # a real hash was computed


def test_cli_block_on_underpower_exits_nonzero(tmp_path: Path) -> None:
    corpus = tmp_path / "c.jsonl"
    _write(corpus, [_rec("r0", ["EMAIL_ADDRESS"])])  # 1 positive, target 2 -> shortfall
    latf = tmp_path / "lat.json"
    _lattice_file(latf, target_n=2)
    out = tmp_path / "m.json"
    rc = S.main([
        "--preset", "powered-representative", "--seed", "1",
        "--corpus", str(corpus), "--lattice", str(latf), "--out", str(out), "--block-on-underpower",
    ])
    assert rc != 0  # GATE-P3 fatal under --block-on-underpower


def test_cli_default_underpower_is_nonfatal_flag(tmp_path: Path) -> None:
    corpus = tmp_path / "c.jsonl"
    _write(corpus, [_rec("r0", ["EMAIL_ADDRESS"])])  # under target, but default preset must not halt
    latf = tmp_path / "lat.json"
    _lattice_file(latf, target_n=2)
    out = tmp_path / "m.json"
    rc = S.main([
        "--preset", "powered-representative", "--seed", "1",
        "--corpus", str(corpus), "--lattice", str(latf), "--out", str(out),
    ])
    assert rc == 0  # honest FLAG, not a halt (the study's strongest delight)
    assert out.exists()
