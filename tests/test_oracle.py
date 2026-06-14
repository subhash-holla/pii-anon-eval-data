"""PII-recognition oracle tests (S7-01; FR-017, NFR-004).

The oracle is a callable PII-**recognition** API: ``recognize(record)`` returns labeled-entity
verdicts (which gold-annotated spans are PII + their type) so a live agent harness can call
PII-Anon as a recognition oracle. The load-bearing scope guard (FR-017) is the **non-strippable
disclaimer** that the oracle is NEVER marketed as agent-leakage scoring.

Synthetic gold annotations only (AX-001); pure-stdlib + deterministic (NFR-004 / AX-002).
"""

from __future__ import annotations

import ast
import pathlib

import pytest
from pii_anon_datasets.scoring.adversary import (
    ORACLE_DISCLAIMER,
    OracleVerdict,
    RecognizedEntity,
    recognize,
    recognize_span,
)
from pii_anon_datasets.scoring.adversary import oracle as oracle_mod


def _synthetic_record() -> dict[str, object]:
    """A tiny synthetic record with two gold annotation spans over a fabricated text.

    AX-001: every value is synthetic. ``annotations`` are ``{start, end, entity_type, text}``
    char-offset spans, the shape ``load_dataset()`` records carry.
    """
    text = "Call Robin Vale at robin@example.test about the invoice."
    return {
        "record_id": "syn-oracle-0001",
        "text": text,
        "annotations": [
            {"start": 5, "end": 15, "entity_type": "PERSON", "text": "Robin Vale"},
            {"start": 19, "end": 36, "entity_type": "EMAIL", "text": "robin@example.test"},
        ],
    }


# 1. ::test_fr_017_recognize_returns_labeled_verdicts  [UNIT-TEST]
def test_fr_017_recognize_returns_labeled_verdicts():
    """``recognize(record)`` returns an ``OracleVerdict`` whose ``recognized`` is one
    ``RecognizedEntity(start, end, entity_type, text)`` per gold annotation, and whose
    ``.labels()`` equals the record's annotation entity_types in order (FR-017)."""
    record = _synthetic_record()
    verdict = recognize(record)

    assert isinstance(verdict, OracleVerdict)
    assert len(verdict.recognized) == len(record["annotations"])  # type: ignore[arg-type]
    assert all(isinstance(e, RecognizedEntity) for e in verdict.recognized)

    first = verdict.recognized[0]
    assert (first.start, first.end, first.entity_type, first.text) == (5, 15, "PERSON", "Robin Vale")

    # order-preserved labels mirror the gold annotation entity_types
    assert verdict.labels() == ("PERSON", "EMAIL")


# 2. ::test_fr_017_oracle_disclaimer_non_strippable  [UNIT-TEST]
def test_fr_017_oracle_disclaimer_non_strippable():
    """The FR-017 disclaimer is non-strippable: an empty disclaimer is rejected, and the
    module constant declares this is a *recognition* oracle, NEVER agent-leakage scoring."""
    with pytest.raises(ValueError):
        OracleVerdict(recognized=(), disclaimer="")

    lowered = ORACLE_DISCLAIMER.lower()
    assert "recognition" in lowered
    assert "never" in lowered
    assert ("agent-leakage" in lowered) or ("agent leakage" in lowered)
    assert "fr-017" in lowered


# 3. ::test_fr_017_recognize_span_point_query  [UNIT-TEST]
def test_fr_017_recognize_span_point_query():
    """``recognize_span(record, start, end)`` returns the ``RecognizedEntity`` whose span
    exactly matches a known PII span, and ``None`` for a non-PII / unmatched span (FR-017)."""
    record = _synthetic_record()

    hit = recognize_span(record, 19, 36)
    assert isinstance(hit, RecognizedEntity)
    assert hit.entity_type == "EMAIL"
    assert hit.text == "robin@example.test"

    # a span that matches no gold annotation -> not recognized as PII
    assert recognize_span(record, 0, 4) is None


# 4. ::test_nfr004_oracle_pure_stdlib  [PROPERTY-TEST]
def test_nfr004_oracle_pure_stdlib():
    """NFR-004 / AX-002: statically prove ``oracle.py`` imports none of
    {random, time, uuid, datetime, secrets} — a recognition oracle has no clock/RNG."""
    src = pathlib.Path(oracle_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned = {"random", "time", "uuid", "datetime", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), f"oracle.py imports nondeterministic modules: {sorted(banned & imported)}"
