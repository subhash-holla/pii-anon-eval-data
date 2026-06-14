"""Coreference + quasi-identifier corpus slices (FR-015/016; DC-01, v1.1).

``coreference_slice(records)`` selects records with a NON-EMPTY
``entity_tracking.coreference_chains`` (a chain scored as a UNIT — FR-015);
``quasi_identifier_slice(records, min_qids=2)`` selects records with >= ``min_qids``
``privacy_risk.quasi_identifiers`` (multi-span indirect identification — FR-016). Both carry a
non-strippable v1.1 LOW-POWER caveat (~72% formulaic synthetic enrichment — epistemic honesty).

Pure-stdlib (NFR-004 / AX-002): test #4 is an AST guard pinning out {random, time, uuid,
datetime, secrets}. Every test fn carries an ``fr_015`` / ``fr_016`` / ``nfr004`` token.
"""

from __future__ import annotations

import ast
import pathlib

import pytest
from pii_anon_datasets.subsets import slices as slices_mod
from pii_anon_datasets.subsets.slices import (
    SLICE_CAVEAT,
    Slice,
    coreference_slice,
    quasi_identifier_slice,
)


def _rec(
    *,
    chains: object = None,
    qids: object = None,
) -> dict[str, object]:
    """A tiny in-memory record exposing only the fields the slices read."""
    return {
        "entity_tracking": {"coreference_chains": chains},
        "privacy_risk": {"quasi_identifiers": qids},
    }


def test_fr_015_coreference_slice_selects_nonempty_chains() -> None:
    """coreference_slice keeps only records with a non-empty chain list — [UNIT-TEST].

    A record with an empty (or missing) ``entity_tracking.coreference_chains`` is excluded; a
    record with one or more chains (scored as a UNIT — FR-015) is kept, order preserved.
    """
    with_chain = _rec(chains=[["mention_a", "mention_b"]])
    empty_chain = _rec(chains=[])
    missing_chain = _rec(chains=None)
    no_entity_tracking: dict[str, object] = {"privacy_risk": {"quasi_identifiers": []}}

    sl = coreference_slice([with_chain, empty_chain, missing_chain, no_entity_tracking])

    assert isinstance(sl, Slice)
    assert sl.name == "coreference"
    assert tuple(sl.records) == (with_chain,)
    assert len(sl) == 1


def test_fr_016_quasi_identifier_slice_min_qids() -> None:
    """quasi_identifier_slice keeps records with >= min_qids qids; min_qids tightens — [UNIT-TEST].

    Default ``min_qids=2``: 0 or 1 qid is excluded, >= 2 kept (multi-span indirect ID — FR-016).
    Raising ``min_qids=3`` excludes the 2-qid record.
    """
    two_qids = _rec(qids=["DATE_OF_BIRTH", "ORGANIZATION_NAME"])
    three_qids = _rec(qids=["DATE_OF_BIRTH", "ORGANIZATION_NAME", "CITY"])
    one_qid = _rec(qids=["DATE_OF_BIRTH"])
    zero_qids = _rec(qids=[])
    records = [two_qids, three_qids, one_qid, zero_qids]

    default_slice = quasi_identifier_slice(records)
    assert default_slice.name == "quasi_identifier"
    assert tuple(default_slice.records) == (two_qids, three_qids)

    tighter = quasi_identifier_slice(records, min_qids=3)
    assert tuple(tighter.records) == (three_qids,)


def test_fr_015_slice_low_power_caveat_non_strippable() -> None:
    """The v1.1 low-power caveat is non-strippable: empty -> ValueError — [UNIT-TEST].

    A ``Slice`` constructed with ``caveat=""`` raises ``ValueError``; ``SLICE_CAVEAT`` states the
    ~72%-formulaic limited-power / external-validity honesty caveat (FR-015/016 v1.1).
    """
    with pytest.raises(ValueError):
        Slice(name="coreference", records=(), caveat="")
    with pytest.raises(ValueError):
        Slice(name="coreference", records=(), caveat="   ")

    lowered = SLICE_CAVEAT.lower()
    assert "72%" in SLICE_CAVEAT
    assert any(token in lowered for token in ("v1.1", "low", "limited"))
    assert any(token in lowered for token in ("external validity", "power"))


def test_nfr004_slices_pure_stdlib() -> None:
    """AST guard (NFR-004 / AX-002): slices.py imports no nondeterminism — [PROPERTY-TEST].

    The module imports none of {random, time, uuid, datetime, secrets} — pure-stdlib.
    """
    src = pathlib.Path(slices_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)

    banned = {"random", "time", "uuid", "datetime", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), f"slices.py imports nondeterministic modules: {sorted(banned & imported)}"
