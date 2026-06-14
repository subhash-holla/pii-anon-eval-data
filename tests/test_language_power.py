"""S4-04 — per-language + language×entity_type power table (NFR-003 transparency).

A THIN reporter over the FROZEN committed lattice + ``reporting/power_table``: it never reads the
corpus — it operates on ``(lattice, observed_counts)`` passed in (same src-purity discipline as
``reporting/power_table.py``). These tests use a TINY inline lattice + observed_counts fixture that
mirrors the real ``eval_lattice.json`` cell shape (dimensions nested under ``c["dimensions"]``,
``interaction`` marking the marginal / ``language_x_entity_type`` crossing) — they do NOT load the
corpus. Every test carries an ``nfr_003`` token.
"""
from __future__ import annotations

import ast
import csv
import io
from pathlib import Path

from pii_anon_datasets.reporting import language_power

_LANG_POWER_SRC = (
    Path(__file__).resolve().parents[1] / "src/pii_anon_datasets/reporting/language_power.py"
)


# ── tiny inline lattice mirroring the real eval_lattice.json cell shape ──────────────────
# Cell dict shape (read from data/eval_lattice.json): {id, dimensions:{...}, tier, target_n,
# committed, count_gated, interaction}. Language marginals carry interaction "marginal:language"
# (id prefix "M:language="); language×type cells carry interaction "language_x_entity_type"
# (id prefix "LxE:") with dimensions {entity_type, language}.
def _cell(cid: str, dims: dict, tier: str, target_n: int, interaction: str,
          *, count_gated: bool = True) -> dict:
    return {
        "id": cid,
        "dimensions": dict(dims),
        "tier": tier,
        "target_n": target_n,
        "committed": True,
        "count_gated": count_gated,
        "interaction": interaction,
    }


def _tiny_lattice() -> dict:
    cells = [
        # language marginals (2 languages)
        _cell("M:language=en", {"language": "en"}, "standard", 753, "marginal:language"),
        _cell("M:language=fr", {"language": "fr"}, "standard", 753, "marginal:language"),
        # a non-language marginal that MUST be excluded from the per-language table
        _cell("M:entity_type=IBAN", {"entity_type": "IBAN"}, "critical", 1522,
              "marginal:entity_type"),
        # language × entity_type crossing (2 langs × 2 types)
        _cell("LxE:entity_type=IBAN|language=en", {"language": "en", "entity_type": "IBAN"},
              "critical", 1522, "language_x_entity_type"),
        _cell("LxE:entity_type=EMAIL|language=en", {"language": "en", "entity_type": "EMAIL"},
              "standard", 753, "language_x_entity_type"),
        _cell("LxE:entity_type=IBAN|language=fr", {"language": "fr", "entity_type": "IBAN"},
              "critical", 1522, "language_x_entity_type"),
        _cell("LxE:entity_type=EMAIL|language=fr", {"language": "fr", "entity_type": "EMAIL"},
              "standard", 753, "language_x_entity_type"),
        # a non-language-crossing 2-way that MUST be excluded from the matrix
        _cell("DxT:adv_track=clean|domain=legal", {"domain": "legal", "adv_track": "clean"},
              "standard", 753, "domain_x_track"),
    ]
    return {"lattice_version": "test", "cell_count": len(cells), "cells": cells}


def _observed() -> dict:
    # keyed by cell id (mirrors power_table.observed_counts). en well-powered, fr under-powered.
    return {
        "M:language=en": 800,                       # >= 753 → well_powered
        "M:language=fr": 100,                        # <  753 → under_powered
        "LxE:entity_type=IBAN|language=en": 1600,    # >= 1522 → well_powered
        "LxE:entity_type=EMAIL|language=en": 50,     # <  753  → under_powered
        "LxE:entity_type=IBAN|language=fr": 0,       # == 0    → empty
        "LxE:entity_type=EMAIL|language=fr": 900,    # >= 753  → well_powered
        # DxT / entity-type-marginal intentionally absent (default 0) and must be ignored anyway
    }


# ── 1. per-language table: one row per language marginal cell ────────────────────────────
def test_nfr_003_per_language_table_has_row_per_language():
    rows = language_power.per_language_table(_tiny_lattice(), _observed())
    # exactly one row per language marginal (en, fr); the IBAN entity_type marginal excluded.
    assert [r["language"] for r in rows] == ["en", "fr"], "one sorted row per language marginal"
    for r in rows:
        assert {"language", "positives", "target_n", "tier", "power_class"} <= r.keys()
    by_lang = {r["language"]: r for r in rows}
    assert by_lang["en"]["positives"] == 800
    assert by_lang["en"]["target_n"] == 753
    assert by_lang["fr"]["positives"] == 100
    assert by_lang["en"]["tier"] == "standard"


# ── 2. language × entity_type matrix grouped by language (forward/reverse navigable) ─────
def test_nfr_003_language_x_type_matrix_grouped():
    rows = language_power.language_x_type_matrix(_tiny_lattice(), _observed())
    # only the LxE crossing cells (4 of them); DxT / marginals excluded.
    assert len(rows) == 4
    for r in rows:
        assert {"language", "entity_type", "positives", "target_n", "tier", "power_class"} <= r.keys()
    langs = {r["language"] for r in rows}
    types = {r["entity_type"] for r in rows}
    assert langs == {"en", "fr"}                     # forward: grouped by language
    assert types == {"IBAN", "EMAIL"}                # reverse: navigable by entity_type
    # group-by-language is contiguous + sorted (en block, then fr block).
    assert [r["language"] for r in rows] == ["en", "en", "fr", "fr"]
    en_iban = next(r for r in rows if r["language"] == "en" and r["entity_type"] == "IBAN")
    assert en_iban["positives"] == 1600
    assert en_iban["target_n"] == 1522


# ── 3. low-power cells labelled (under target → low-power; ≥ target → well-powered) ──────
def test_nfr_003_low_power_cells_labeled():
    lat, obs = _tiny_lattice(), _observed()
    lang_rows = {r["language"]: r for r in language_power.per_language_table(lat, obs)}
    # fr (100 < 753) is low-power; en (800 >= 753) is well-powered.
    assert lang_rows["fr"]["power_class"] == "under_powered"
    assert lang_rows["en"]["power_class"] == "well_powered"

    matrix = language_power.language_x_type_matrix(lat, obs)
    cell = {(r["language"], r["entity_type"]): r for r in matrix}
    assert cell[("en", "EMAIL")]["power_class"] == "under_powered"   # 50 < 753
    assert cell[("fr", "IBAN")]["power_class"] == "empty"            # 0 positives
    assert cell[("en", "IBAN")]["power_class"] == "well_powered"     # 1600 >= 1522
    # every below-target cell is labelled as NOT well-powered (the NFR-003 low-power flag).
    for r in lang_rows.values():
        assert (r["power_class"] == "well_powered") == (r["positives"] >= r["target_n"])
    for r in matrix:
        assert (r["power_class"] == "well_powered") == (r["positives"] >= r["target_n"])


# ── 4. markdown + csv renderers: header-bearing, non-empty, CSV round-trips ──────────────
def test_nfr_003_render_markdown_and_csv():
    lat, obs = _tiny_lattice(), _observed()
    rows = language_power.language_x_type_matrix(lat, obs)

    md = language_power.render_markdown(rows)
    assert isinstance(md, str) and md.strip(), "markdown must be non-empty"
    assert md.lstrip().startswith("|"), "markdown must lead with a table header row"
    assert "power_class" in md or "class" in md   # a power column header is present
    # every cell's language appears in the rendered table.
    for r in rows:
        assert r["language"] in md

    out = language_power.render_csv(rows)
    assert isinstance(out, str) and out.strip(), "csv must be non-empty"
    parsed = list(csv.DictReader(io.StringIO(out)))
    assert len(parsed) == len(rows), "CSV round-trips to the same row count"
    assert "power_class" in parsed[0], "csv carries a power_class column"


# ── 5. [PROPERTY-TEST] src-purity: the reporter reads NO corpus ─────────────────────────
def test_nfr_003_no_corpus_read():
    """AST guard: language_power.py imports no corpus loader (``load_dataset``) and never opens /
    gzips a corpus — it is pure over the passed-in ``(lattice, observed_counts)`` args, mirroring
    ``reporting/power_table.py``. The audit that produces observed_counts lives elsewhere."""
    src = _LANG_POWER_SRC.read_text(encoding="utf-8")
    tree = ast.parse(src)

    imported: set[str] = set()
    called: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                called.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                called.add(fn.attr)

    assert "load_dataset" not in imported, "reporter must not import a corpus loader"
    assert "load_dataset" not in called, "reporter must not call load_dataset"
    # no corpus byte I/O in this src-layer reporter (open/gzip are how the corpus would be read).
    assert "gzip" not in imported, "reporter must not import gzip (corpus byte I/O)"
    assert "open" not in called, "reporter must not open() a file"
    assert "load_lattice" not in called, "reporter takes the lattice as an arg, never loads it"


# ── 6. [PROPERTY-TEST] NFR-004 import purity: no nondeterminism imports ──────────────────
def test_nfr_003_nfr004_imports_no_nondeterminism():
    """AST guard: language_power.py imports NONE of {random, time, uuid, datetime, secrets}."""
    src = _LANG_POWER_SRC.read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned = {"random", "time", "uuid", "datetime", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), (
        f"language_power.py imports nondeterministic modules: {sorted(banned & imported)}"
    )
