"""S5-04 — CoNLL export (FR-024 / NFR-004): BIO/BILOU tags aligned to char offsets + streaming.

Pins the CoNLL side of the NER-training exports. The packaged ``integrations.conll_format`` ports
the proven, deterministic BIO/BILOU conversion functions from the brownfield top-level
``integrations/conll_format.py`` CLI script (minus its argparse / ``load_dataset`` / print
side-effects); ``distribution.conll_export.export_conll`` is a THIN streaming wrapper around
``record_to_conll`` (no tagging logic of its own). The contracts:

* BIO tags align to the record's char-offset ``annotations`` (``B-`` on the first overlapping token
  of an entity, ``I-`` on the rest, ``O`` elsewhere); ``fmt="bilou"`` converts single-token
  entities to ``U-`` and multi-token to ``B-…``/``L-`` (``fr_024``);
* ``export_conll`` STREAMS a one-shot iterator — never ``list()``/``len()``/index — with a
  double blank line between documents (``fr_024``);
* exporting the same records twice is byte-identical (no clock/RNG, stable tokenization)
  (``fr_024`` / AX-002);
* the CoNLL core is pure-stdlib — AST guard bans {random, time, uuid, datetime, secrets} from both
  ``integrations/conll_format.py`` AND ``distribution/conll_export.py`` (``nfr004`` / NFR-004).

CoNLL needs no third-party dep, so every test here RUNS on a pure-stdlib box (spaCy lives in
``test_spacy_export.py``).
"""

from __future__ import annotations

import ast
import pathlib
from collections.abc import Iterator

import pytest
from pii_anon_datasets.distribution import conll_export as conll_export_mod
from pii_anon_datasets.distribution.conll_export import export_conll
from pii_anon_datasets.integrations import conll_format as conll_format_mod
from pii_anon_datasets.integrations.conll_format import record_to_conll

_BANNED_NONDETERMINISTIC = {"random", "time", "uuid", "datetime", "secrets"}


def _record(text: str, annotations: list[dict]) -> dict:
    """A tiny synthetic record — no real corpus, no PII (AX-001); deterministic."""
    return {"record_id": "rec-x", "text": text, "annotations": annotations}


def _parse_conll(conll: str) -> list[tuple[str, str]]:
    """Parse ``token\\tTAG`` lines (skipping blanks) into ``(token, tag)`` pairs for assertions."""
    pairs: list[tuple[str, str]] = []
    for line in conll.splitlines():
        if not line.strip():
            continue
        token, tag = line.split("\t")
        pairs.append((token, tag))
    return pairs


def test_fr_024_conll_bio_tags_align_to_offsets() -> None:
    """[UNIT-TEST] A record whose ``annotations`` cover a known char-span yields ``B-<TYPE>`` on the
    first overlapping token and ``I-<TYPE>`` on subsequent tokens of a multi-token entity; non-entity
    tokens are ``O``; output is tab-separated ``token\\tTAG``."""
    # "My name is John Smith here" — PERSON spans the two tokens "John Smith".
    text = "My name is John Smith here"
    start = text.index("John")
    end = text.index("Smith") + len("Smith")
    conll = record_to_conll(_record(text, [{"start": start, "end": end, "entity_type": "PERSON"}]))

    pairs = _parse_conll(conll)
    tags = {tok: tag for tok, tag in pairs}
    # Multi-token entity: B- on the first token, I- on the next.
    assert tags["John"] == "B-PERSON"
    assert tags["Smith"] == "I-PERSON"
    # Every non-entity token is O.
    for tok in ("My", "name", "is", "here"):
        assert tags[tok] == "O", f"expected O for {tok!r}, got {tags[tok]!r}"
    # Tab-separated token\tTAG shape (exactly one tab per non-blank line).
    for line in conll.splitlines():
        if line.strip():
            assert line.count("\t") == 1, f"line not tab-separated token\\tTAG: {line!r}"


def test_fr_024_conll_bilou_conversion() -> None:
    """[UNIT-TEST] With ``fmt="bilou"``: a single-token entity -> ``U-<TYPE>``; a multi-token entity
    -> ``B-…`` then ``L-<TYPE>`` (and ``I-`` in the middle for >=3 tokens)."""
    # One single-token CITY ("Paris") and one three-token ORG ("Acme Global Corp").
    text = "Paris hosts Acme Global Corp today"
    city_start = text.index("Paris")
    city_end = city_start + len("Paris")
    org_start = text.index("Acme")
    org_end = text.index("Corp") + len("Corp")
    conll = record_to_conll(
        _record(
            text,
            [
                {"start": city_start, "end": city_end, "entity_type": "CITY"},
                {"start": org_start, "end": org_end, "entity_type": "ORG"},
            ],
        ),
        fmt="bilou",
    )

    tags = {tok: tag for tok, tag in _parse_conll(conll)}
    # Single-token entity collapses to U-.
    assert tags["Paris"] == "U-CITY"
    # Three-token entity: B- / I- / L-.
    assert tags["Acme"] == "B-ORG"
    assert tags["Global"] == "I-ORG"
    assert tags["Corp"] == "L-ORG"
    # Non-entity token stays O.
    assert tags["today"] == "O"


def test_fr_024_conll_export_streams_not_materializes(tmp_path: pathlib.Path) -> None:
    """[PROPERTY-TEST] ``export_conll`` consumes a ONE-SHOT generator to exhaustion (no
    ``list()``/``len()``/indexing); a blank line separates sentences, a double blank line separates
    documents.

    A one-shot generator can be iterated exactly once; if the exporter materialised it (or iterated
    twice) the second pass would yield nothing. We assert the generator was driven to exhaustion AND
    that the document/sentence separators land where the contract says."""
    records = [
        # Doc 1: two sentences (newline-split) -> a blank line BETWEEN them inside the doc.
        _record("Alpha line\nBeta line", []),
        # Doc 2: a single sentence -> separated from doc 1 by a DOUBLE blank line.
        _record("Gamma line", []),
    ]
    consumed: list[str] = []

    def one_shot() -> Iterator[dict]:
        for rec in records:
            consumed.append(rec["text"])  # observe consumption order/count
            yield rec

    gen = one_shot()
    out = tmp_path / "corpus.conll"
    returned = export_conll(gen, str(out))

    # Returns the path it wrote (FR-024 contract).
    assert returned == str(out)
    # Streamed exactly once, in order (no re-iteration, no materialisation)...
    assert consumed == ["Alpha line\nBeta line", "Gamma line"]
    # ...and the generator is exhausted (one-shot honoured: a second pass yields nothing).
    assert list(gen) == []

    text_out = out.read_text(encoding="utf-8")
    lines = text_out.split("\n")
    # Sentence separator: a single blank line between "Alpha line" and "Beta line" tokens within doc 1.
    assert lines[:5] == ["Alpha\tO", "line\tO", "", "Beta\tO", "line\tO"]
    # Both documents' content reached the file (the stream wrote every record).
    assert "Alpha\tO" in text_out and "Beta\tO" in text_out and "Gamma\tO" in text_out

    # Document separator: ``export_conll`` writes an EXTRA ``"\n"`` between documents (beyond each
    # record's own trailing newline), so the doc1->doc2 boundary carries one more newline than simply
    # concatenating the two records' ``record_to_conll`` strings would. We prove that extra separator
    # is present (the thin wrap's only own output) without over-pinning the literal newline count.
    no_sep = record_to_conll(records[0]) + record_to_conll(records[1])
    assert text_out == record_to_conll(records[0]) + "\n" + record_to_conll(records[1])
    assert text_out != no_sep, "export_conll must add a blank-line separator between documents"
    assert text_out.count("\n") == no_sep.count("\n") + 1
    # The boundary lands exactly where doc1's last token ends and doc2's first token begins.
    assert "line\tO\n\nGamma\tO" in text_out, "doc separator must sit between doc1's tail and doc2's head"


def test_fr_024_conll_deterministic(tmp_path: pathlib.Path) -> None:
    """[PROPERTY-TEST] Exporting the same records twice -> byte-identical ``.conll`` (no clock/RNG;
    stable whitespace tokenization)."""
    records = [
        _record("John Smith called", [{"start": 0, "end": 10, "entity_type": "PERSON"}]),
        _record("Acme Corp paid", [{"start": 0, "end": 9, "entity_type": "ORG"}]),
    ]
    out_a = tmp_path / "a.conll"
    out_b = tmp_path / "b.conll"
    export_conll(records, str(out_a))
    export_conll(records, str(out_b))

    assert out_a.read_bytes() == out_b.read_bytes(), (
        "same records exported twice produced differing CoNLL bytes (non-deterministic)"
    )


def _module_imports(module_file: str) -> set[str]:
    """AST-collect the top-level package names imported anywhere in ``module_file``'s source."""
    src = pathlib.Path(module_file).read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    return imported


def test_nfr004_conll_pure_stdlib() -> None:
    """[PROPERTY-TEST] AST guard: ``integrations/conll_format.py`` AND
    ``distribution/conll_export.py`` import NONE of {random, time, uuid, datetime, secrets}
    (deterministic, pure-stdlib — NFR-004)."""
    for module_file in (conll_format_mod.__file__, conll_export_mod.__file__):
        imported = _module_imports(module_file)
        assert _BANNED_NONDETERMINISTIC.isdisjoint(imported), (
            f"{pathlib.Path(module_file).name} imports nondeterministic modules: "
            f"{sorted(_BANNED_NONDETERMINISTIC & imported)}"
        )


# --- S5-close coverage hardening: build_label2id, multi-sentence/empty-sentence BILOU, bad fmt ---
# Lift integrations/conll_format.py to >=85% line coverage by exercising the label2id builder, the
# empty/whitespace-sentence skip branch (offset bookkeeping), and the unknown-fmt guard.

from pii_anon_datasets.integrations.conll_format import (  # noqa: E402
    CONLL_FORMATS,
    build_label2id,
)


def test_fr_024_build_label2id_o_plus_bi_per_sorted_type() -> None:
    """[UNIT-TEST] ``build_label2id`` collects distinct ``entity_type``s across records and assigns
    ``O`` -> 0 then ``B-``/``I-`` per SORTED type with contiguous ids (HuggingFace token-classification
    compat) — lines 171-184."""
    records = [
        _record("x", [{"start": 0, "end": 1, "entity_type": "PERSON"}]),
        _record("y", [{"start": 0, "end": 1, "entity_type": "ORG"}]),
        # Duplicate type + a record whose annotations key is absent (covers the get-default path).
        _record("z", [{"start": 0, "end": 1, "entity_type": "PERSON"}]),
        {"record_id": "no-ann", "text": "w"},
    ]

    label2id = build_label2id(records)

    # O is always id 0; types are sorted (ORG before PERSON) with contiguous B-/I- ids.
    assert label2id == {
        "O": 0,
        "B-ORG": 1,
        "I-ORG": 2,
        "B-PERSON": 3,
        "I-PERSON": 4,
    }


def test_fr_024_build_label2id_skips_nonsequence_annotations() -> None:
    """[UNIT-TEST] A record whose ``annotations`` is not a Sequence is skipped (the
    ``isinstance(..., Sequence)`` guard at line 174-175) — only the well-formed record contributes."""
    records: list[dict] = [
        {"record_id": "bad", "text": "x", "annotations": {"not": "a-sequence"}},
        _record("y", [{"start": 0, "end": 1, "entity_type": "EMAIL"}]),
    ]

    label2id = build_label2id(records)

    assert label2id == {"O": 0, "B-EMAIL": 1, "I-EMAIL": 2}


def test_fr_024_conll_bilou_multi_sentence_skips_empty_sentence() -> None:
    """[UNIT-TEST] ``record_to_conll(fmt="bilou")`` over a MULTI-sentence record with a blank/whitespace
    sentence in the middle: the empty sentence is skipped (lines 142-144, the offset += len()+1
    bookkeeping) while global offsets stay aligned so the entity in the LAST sentence still tags
    correctly as a single-token ``U-``."""
    # Three newline-split sentences; the middle one is whitespace-only (exercises the skip branch).
    # Offsets must stay global so "Paris" in the third sentence aligns to its annotation.
    text = "Hello there\n   \nParis"
    paris_start = text.index("Paris")
    paris_end = paris_start + len("Paris")
    conll = record_to_conll(
        _record(text, [{"start": paris_start, "end": paris_end, "entity_type": "CITY"}]),
        fmt="bilou",
    )

    tags = {tok: tag for tok, tag in _parse_conll(conll)}
    # The first sentence's tokens are non-entities …
    assert tags["Hello"] == "O"
    assert tags["there"] == "O"
    # … the whitespace-only middle sentence contributes NO token lines (skipped) …
    assert "   " not in conll
    # … and the entity in the third sentence still aligns despite the skipped sentence's offsets:
    # a single-token entity collapses to U- under BILOU.
    assert tags["Paris"] == "U-CITY"


def test_fr_024_record_to_conll_rejects_unknown_fmt() -> None:
    """[UNIT-TEST] An ``fmt`` outside :data:`CONLL_FORMATS` raises ``ValueError`` naming the allowed
    set (line 128-129)."""
    assert set(CONLL_FORMATS) == {"bio", "bilou"}
    with pytest.raises(ValueError, match="fmt must be one of"):
        record_to_conll(_record("hi there", []), fmt="iob2")


def test_fr_024_record_to_conll_nonsequence_annotations_treated_empty() -> None:
    """[UNIT-TEST] A record whose ``annotations`` is not a Sequence is treated as empty (line 133-134):
    every token is ``O`` rather than crashing."""
    rec = {"record_id": "bad", "text": "John Smith here", "annotations": 12345}
    conll = record_to_conll(rec)  # must not raise
    tags = {tok: tag for tok, tag in _parse_conll(conll)}
    assert set(tags.values()) == {"O"}
