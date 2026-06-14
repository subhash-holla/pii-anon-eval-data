"""S5-04 — spaCy export (FR-024 / NFR-004): char-offset tuples + a serialized DocBin (lazy spaCy).

Pins the spaCy side of the NER-training exports. ``to_spacy_offsets`` is the pure-stdlib spaCy
training format ``(text, {"entities": [(start, end, entity_type), …]})`` (entities sorted by
``(start, end)``) — needs NO spaCy. ``export_spacy_docbin`` streams records to a serialized
``DocBin``, importing spaCy LAZILY (only inside ``_require_spacy``) behind the ``[baselines]`` extra.
The contracts:

* ``to_spacy_offsets`` returns sorted ``(start, end, entity_type)`` tuples matching the record's
  annotations — pure-stdlib (``fr_024``);
* ``export_spacy_docbin`` round-trips: ``DocBin().from_disk(path)`` -> ``db.get_docs(nlp.vocab)``
  preserve the docs' ``ents`` labels + char offsets (spaCy 3.8.3 present -> RUNS) (``fr_024``);
* misaligned ``char_span`` (None) is skipped and overlaps are dropped via
  ``spacy.util.filter_spans`` (a ``DocBin`` cannot hold overlapping ``ents``) (``fr_024``);
* ``import pii_anon_datasets.distribution.spacy_export`` succeeds with ``spacy`` blocked (lazy);
  calling ``export_spacy_docbin`` then raises a clear ``RuntimeError`` naming ``pip install
  pii-anon-datasets[baselines]``; AST guard: ``spacy`` only inside ``_require_spacy`` (``nfr004`` /
  NFR-004).

spaCy 3.8.3 IS installed in this env, so the DocBin round-trip + overlap-filter tests RUN; the
top-level ``importorskip`` keeps the module honest on a stdlib-only box without lying about coverage.
"""

from __future__ import annotations

import ast
import builtins
import importlib
import pathlib

import pytest
from pii_anon_datasets.distribution import spacy_export as spacy_export_mod
from pii_anon_datasets.distribution.spacy_export import export_spacy_docbin, to_spacy_offsets


def _record(text: str, annotations: list[dict]) -> dict:
    """A tiny synthetic record — no real corpus, no PII (AX-001); deterministic."""
    return {"record_id": "rec-x", "text": text, "annotations": annotations}


def test_fr_024_spacy_offsets_format() -> None:
    """[UNIT-TEST] ``to_spacy_offsets(record)`` returns ``(text, {"entities": [(start, end,
    entity_type), …]})`` with entities sorted by ``(start, end)`` and matching the record's
    annotations — pure-stdlib, no spaCy."""
    text = "John Smith met Acme Corp"
    # Annotations DELIBERATELY out of offset order -> must come back sorted by (start, end).
    record = _record(
        text,
        [
            {"start": 15, "end": 24, "entity_type": "ORG", "text": "Acme Corp"},
            {"start": 0, "end": 10, "entity_type": "PERSON", "text": "John Smith"},
        ],
    )
    out_text, payload = to_spacy_offsets(record)

    assert out_text == text
    assert payload["entities"] == [(0, 10, "PERSON"), (15, 24, "ORG")]
    # Tuples carry exactly (start, end, entity_type) — matching the record's annotation spans.
    assert all(len(ent) == 3 for ent in payload["entities"])


def test_fr_024_spacy_docbin_roundtrip(tmp_path: pathlib.Path) -> None:
    """[INTEGRATION-TEST] ``export_spacy_docbin(records, path)`` then ``DocBin().from_disk(path)`` ->
    ``list(db.get_docs(nlp.vocab))``: the docs' ``ents`` preserve the labels + char offsets of the
    (non-overlapping) annotations (spaCy 3.8.3 present -> RUNS)."""
    spacy = pytest.importorskip("spacy")
    from spacy.tokens import DocBin

    records = [
        _record(
            "John Smith met Acme Corp",
            [
                {"start": 0, "end": 10, "entity_type": "PERSON"},
                {"start": 15, "end": 24, "entity_type": "ORG"},
            ],
        ),
        _record("Paris is nice", [{"start": 0, "end": 5, "entity_type": "CITY"}]),
    ]
    out = tmp_path / "train.spacy"
    returned = export_spacy_docbin(records, str(out))

    assert returned == str(out)
    assert out.exists()

    nlp = spacy.blank("xx")
    db = DocBin().from_disk(out)
    docs = list(db.get_docs(nlp.vocab))
    assert len(docs) == 2

    # Doc 1: PERSON + ORG ents preserve labels AND char offsets.
    ents0 = sorted((e.start_char, e.end_char, e.label_) for e in docs[0].ents)
    assert ents0 == [(0, 10, "PERSON"), (15, 24, "ORG")]
    # Doc 2: the single CITY ent survives with its offsets.
    ents1 = [(e.start_char, e.end_char, e.label_) for e in docs[1].ents]
    assert ents1 == [(0, 5, "CITY")]


def test_fr_024_spacy_docbin_filters_overlaps(tmp_path: pathlib.Path) -> None:
    """[UNIT-TEST] A record with overlapping/misaligned annotations exports without error: a
    misaligned ``char_span`` (None) is skipped and overlaps are dropped via
    ``spacy.util.filter_spans`` (a ``DocBin`` cannot hold overlapping ``ents``)."""
    spacy = pytest.importorskip("spacy")
    from spacy.tokens import DocBin

    text = "John Smith met Acme Corp"
    record = _record(
        text,
        [
            {"start": 0, "end": 10, "entity_type": "PERSON"},  # "John Smith"
            {"start": 5, "end": 10, "entity_type": "SURNAME"},  # "Smith" — OVERLAPS the PERSON span
            {"start": 1, "end": 4, "entity_type": "MISALIGNED"},  # mid-token -> char_span None -> skipped
        ],
    )
    out = tmp_path / "overlap.spacy"
    # Must NOT raise even though spans overlap / one is token-misaligned.
    export_spacy_docbin([record], str(out))

    nlp = spacy.blank("xx")
    docs = list(DocBin().from_disk(out).get_docs(nlp.vocab))
    assert len(docs) == 1
    ents = sorted((e.start_char, e.end_char, e.label_) for e in docs[0].ents)
    # filter_spans keeps the longest non-overlapping span -> PERSON wins over SURNAME; the
    # token-misaligned MISALIGNED span (char_span None) was skipped entirely. No overlapping ents.
    assert ents == [(0, 10, "PERSON")]
    char_ranges = [(s, e) for s, e, _ in ents]
    for i in range(1, len(char_ranges)):
        assert char_ranges[i][0] >= char_ranges[i - 1][1], "DocBin must hold no overlapping ents"


def test_nfr004_spacy_export_imports_without_spacy(monkeypatch: pytest.MonkeyPatch) -> None:
    """[CONTRACT-TEST] ``import pii_anon_datasets.distribution.spacy_export`` succeeds with ``spacy``
    blocked (lazy); calling ``export_spacy_docbin`` then raises a clear ``RuntimeError`` naming
    ``pip install pii-anon-datasets[baselines]``; AST guard: ``spacy`` only inside ``_require_spacy``."""
    # (a) Lazy import: the module imports even when spacy cannot be imported (block it first, then
    #     reload so any module-top ``import spacy`` would fail at import time — it must not exist).
    real_import = builtins.__import__

    def _block_spacy(name: str, *args: object, **kwargs: object) -> object:
        if name == "spacy" or name.startswith("spacy."):
            raise ImportError(f"No module named {name!r}")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", _block_spacy)
    reloaded = importlib.reload(importlib.import_module("pii_anon_datasets.distribution.spacy_export"))
    assert reloaded is not None
    assert hasattr(reloaded, "export_spacy_docbin")

    # (b) With spacy still blocked, the lazy guard raises a clear install RuntimeError.
    with pytest.raises(RuntimeError) as excinfo:
        reloaded.export_spacy_docbin([_record("x", [])], "unused.spacy")
    assert "pip install pii-anon-datasets[baselines]" in str(excinfo.value), (
        f"RuntimeError must name the install command; got: {str(excinfo.value)!r}"
    )

    # (c) AST guard (NFR-004 lazy contract): NO spacy import at module TOP (so the module imports on
    #     a pure-stdlib box), and the bare top-level ``import spacy`` lives ONLY inside
    #     ``_require_spacy``. The function-local ``from spacy.tokens import DocBin`` inside
    #     ``export_spacy_docbin`` is also lazy (reached only AFTER ``_require_spacy()`` has gated the
    #     extra), so it is permitted — what the contract forbids is a MODULE-TOP spacy import.
    src = pathlib.Path(spacy_export_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)

    def _imports_spacy(node: ast.AST) -> bool:
        if isinstance(node, ast.Import) and any(a.name.split(".")[0] == "spacy" for a in node.names):
            return True
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "spacy":
            return True
        return False

    require_spacy_fns = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_require_spacy"]
    assert require_spacy_fns, "expected a _require_spacy function guarding the lazy import"

    # Module-top import STATEMENTS (directly in the module body) must NOT import spacy — this is the
    # load-bearing NFR-004 guarantee (the module imports without spaCy installed).
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            assert not _imports_spacy(node), "spacy must not be imported at module top (lazy only)"

    # The bare ``import spacy`` (the top-level package) must appear ONLY inside _require_spacy.
    require_body = set()
    for fn in require_spacy_fns:
        require_body.update(id(child) for child in ast.walk(fn))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(a.name.split(".")[0] == "spacy" for a in node.names):
            assert id(node) in require_body, "the bare `import spacy` must live ONLY inside _require_spacy (lazy guard)"
