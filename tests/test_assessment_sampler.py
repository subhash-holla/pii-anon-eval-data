"""CAP-02 S9 — powered lattice-stratified sampler + 4-state verdicts + manifest seam (DC-17/18/19).

Tests run against a SYNTHETIC tiny lattice + tiny corpus (the real 575,604 draw is exercised by a guarded
slow test + Stage-5). The load-bearing oracles: (a) 4-state power classification vs realized positives;
(b) byte-reproducible manifest for a fixed seed (AX-002 / NFR-030); (c) NO head-truncation — back-loaded
positives are still reached (FR-032); (d) non-strippable synthetic-only caveat on the manifest (AX-001).
"""
from __future__ import annotations

import gzip
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pii_anon_datasets.assessment import manifest as M
from pii_anon_datasets.assessment import sample as S
from pii_anon_datasets.assessment import verdicts as V

_EVAL_SRC = Path(__file__).resolve().parents[1] / "src"


# --------------------------------------------------------------------------- verdicts (pure)
def test_classify_well_powered() -> None:
    assert V.classify_cell(n_sample=5, n_full=10, target_n=5) is V.PowerClass.WELL_POWERED


def test_classify_under_sampled_is_fixable() -> None:
    # corpus HAS enough (n_full >= target) but the draw got too few -> fixable by drawing more
    assert V.classify_cell(n_sample=2, n_full=10, target_n=5) is V.PowerClass.UNDER_SAMPLED


def test_classify_corpus_limited_is_irreducible() -> None:
    # corpus itself is short (n_full < target) -> drawing more cannot fix it
    assert V.classify_cell(n_sample=3, n_full=3, target_n=5) is V.PowerClass.CORPUS_LIMITED


def test_classify_empty() -> None:
    assert V.classify_cell(n_sample=0, n_full=0, target_n=5) is V.PowerClass.EMPTY


def test_classify_not_assessed_outside_envelope() -> None:
    assert V.classify_cell(n_sample=0, n_full=0, target_n=5, in_envelope=False) is V.PowerClass.NOT_ASSESSED


def test_shortfall_named_in_realized_positives() -> None:
    assert V.shortfall(n_sample=2, target_n=5) == 3
    assert V.shortfall(n_sample=9, target_n=5) == 0


# --------------------------------------------------------------------------- fixtures
def _tiny_lattice() -> dict:
    return {
        "lattice_version": "test-0001",
        "cells": [
            {"id": "M:entity_type=EMAIL_ADDRESS", "dimensions": {"entity_type": "EMAIL_ADDRESS"},
             "tier": "long_tail", "target_n": 2, "count_gated": True},
            {"id": "M:entity_type=IBAN", "dimensions": {"entity_type": "IBAN"},
             "tier": "critical", "target_n": 5, "count_gated": True},
        ],
    }


def _write_corpus(path: Path, records: list[dict]) -> None:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "wt", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _rec(rid: str, ets: list[str], text: str = "x" * 40) -> dict:
    return {
        "record_id": rid, "text": text, "language": "en", "domain": "general",
        "difficulty_level": "easy", "primary_dimension": "diverse_pii_types", "adversarial": None,
        "annotations": [{"entity_type": et, "start": 0, "end": 5} for et in ets],
    }


# --------------------------------------------------------------------------- sampler
def test_sampler_byte_reproducible(tmp_path: Path) -> None:
    """Same seed -> byte-identical manifest canonical JSON (AX-002 / NFR-030)."""
    corpus = tmp_path / "c.jsonl"
    _write_corpus(corpus, [_rec(f"r{i}", ["EMAIL_ADDRESS"]) for i in range(10)])
    r1 = S.draw_sample(corpus_path=corpus, lattice=_tiny_lattice(), preset="powered-representative", seed=7)
    r2 = S.draw_sample(corpus_path=corpus, lattice=_tiny_lattice(), preset="powered-representative", seed=7)
    m1 = M.to_canonical_json(M.build_manifest(r1, corpus_content_hash="deadbeef", code_commit="abc123"))
    m2 = M.to_canonical_json(M.build_manifest(r2, corpus_content_hash="deadbeef", code_commit="abc123"))
    assert m1 == m2
    assert tuple(r1.record_ids) == tuple(r2.record_ids)


def test_sampler_no_head_truncation(tmp_path: Path) -> None:
    """Back-loaded positives must still be reached (FR-032) — a head-truncation path would miss them."""
    corpus = tmp_path / "c.jsonl"
    # 20 non-matching records first, then 3 EMAIL records at the TAIL
    recs = [_rec(f"pad{i}", ["PERSON_NAME"]) for i in range(20)] + [_rec(f"mail{i}", ["EMAIL_ADDRESS"]) for i in range(3)]
    _write_corpus(corpus, recs)
    res = S.draw_sample(corpus_path=corpus, lattice=_tiny_lattice(), preset="powered-representative", seed=1)
    email_cell = next(c for c in res.per_cell if c.cell_id == "M:entity_type=EMAIL_ADDRESS")
    assert email_cell.realized_positive_count >= 2, "back-loaded EMAIL positives were not reached (head-truncation bug)"
    assert email_cell.power_class is V.PowerClass.WELL_POWERED


def test_sampler_corpus_limited_flag(tmp_path: Path) -> None:
    """IBAN target_n=5 but only 3 in corpus -> CORPUS_LIMITED with a named shortfall (honest under-power)."""
    corpus = tmp_path / "c.jsonl"
    _write_corpus(corpus, [_rec(f"ib{i}", ["IBAN"]) for i in range(3)])
    res = S.draw_sample(corpus_path=corpus, lattice=_tiny_lattice(), preset="powered-representative", seed=2)
    iban = next(c for c in res.per_cell if c.cell_id == "M:entity_type=IBAN")
    assert iban.power_class is V.PowerClass.CORPUS_LIMITED
    assert iban.realized_positive_shortfall == 2
    email = next(c for c in res.per_cell if c.cell_id == "M:entity_type=EMAIL_ADDRESS")
    assert email.power_class is V.PowerClass.EMPTY  # no EMAIL records present


def test_full_corpus_preset_scores_everything(tmp_path: Path) -> None:
    corpus = tmp_path / "c.jsonl"
    recs = [_rec(f"r{i}", ["EMAIL_ADDRESS"]) for i in range(6)]
    _write_corpus(corpus, recs)
    res = S.draw_sample(corpus_path=corpus, lattice=_tiny_lattice(), preset="full-corpus", seed=0)
    assert len(res.record_ids) == 6
    assert res.inferential_target == "descriptive-census"  # FR-036 / integrity-MAJOR-1


def test_manifest_carries_non_strippable_caveat(tmp_path: Path) -> None:
    corpus = tmp_path / "c.jsonl"
    _write_corpus(corpus, [_rec("r0", ["EMAIL_ADDRESS"])])
    res = S.draw_sample(corpus_path=corpus, lattice=_tiny_lattice(), preset="powered-representative", seed=3)
    man = M.build_manifest(res, corpus_content_hash="h", code_commit="c")
    assert man["caveat"].strip(), "manifest must carry a non-empty synthetic-only caveat (AX-001)"
    assert "synthetic" in man["caveat"].lower()
    assert man["schema"] == M.SCHEMA


def test_manifest_build_rejects_empty_caveat(tmp_path: Path) -> None:
    corpus = tmp_path / "c.jsonl"
    _write_corpus(corpus, [_rec("r0", ["EMAIL_ADDRESS"])])
    res = S.draw_sample(corpus_path=corpus, lattice=_tiny_lattice(), preset="powered-representative", seed=3)
    with pytest.raises(ValueError):
        M.build_manifest(res, corpus_content_hash="h", code_commit="c", caveat="   ")


def test_manifest_canonical_json_is_sorted_and_newline_terminated(tmp_path: Path) -> None:
    corpus = tmp_path / "c.jsonl"
    _write_corpus(corpus, [_rec("r0", ["EMAIL_ADDRESS"])])
    res = S.draw_sample(corpus_path=corpus, lattice=_tiny_lattice(), preset="powered-representative", seed=3)
    js = M.to_canonical_json(M.build_manifest(res, corpus_content_hash="h", code_commit="c"))
    assert js.endswith("\n")
    parsed = json.loads(js)
    assert list(parsed.keys()) == sorted(parsed.keys())


def test_sampler_reproducible_across_processes(tmp_path: Path) -> None:
    """The byte-repro guarantee must survive PYTHONHASHSEED variation (AX-002): a hash-salted tuple seed would
    diverge across processes; the string seed must not. Two fresh interpreters with different hash seeds must
    emit an identical canonical manifest."""
    corpus = tmp_path / "c.jsonl"
    _write_corpus(corpus, [_rec(f"r{i}", ["EMAIL_ADDRESS", "IBAN"]) for i in range(12)])
    driver = tmp_path / "driver.py"
    driver.write_text(
        "import sys\n"
        "from pii_anon_datasets.assessment import sample as S, manifest as M\n"
        "lat = {'lattice_version': 't', 'cells': [\n"
        "  {'id': 'M:entity_type=EMAIL_ADDRESS', 'dimensions': {'entity_type': 'EMAIL_ADDRESS'},"
        " 'tier': 'long_tail', 'target_n': 2, 'count_gated': True},\n"
        "  {'id': 'M:entity_type=IBAN', 'dimensions': {'entity_type': 'IBAN'},"
        " 'tier': 'critical', 'target_n': 3, 'count_gated': True}]}\n"
        "r = S.draw_sample(corpus_path=sys.argv[1], lattice=lat, preset='powered-representative', seed=7)\n"
        "print(M.to_canonical_json(M.build_manifest(r, corpus_content_hash='h', code_commit='c')), end='')\n",
        encoding="utf-8",
    )
    base = dict(os.environ)
    base["PYTHONPATH"] = str(_EVAL_SRC)

    def _run(hashseed: str) -> subprocess.CompletedProcess[str]:
        env = dict(base)
        env["PYTHONHASHSEED"] = hashseed
        return subprocess.run(
            [sys.executable, str(driver), str(corpus)], capture_output=True, text=True, env=env
        )

    a = _run("0")
    b = _run("1")
    assert a.returncode == 0, a.stderr
    assert b.returncode == 0, b.stderr
    assert a.stdout and a.stdout == b.stdout, (
        "manifest differs across PYTHONHASHSEED — the per-cell RNG seed is hash-salted, not byte-reproducible"
    )
