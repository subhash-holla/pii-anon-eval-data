"""Quasi-identifier COMBINATION scoring (FR-016; DC-01, v1.1 — AX linkage AX-001/002/003).

A quasi-identifier COMBINATION is "re-identifying" iff >= ``k`` of its quasi-identifiers are
recovered/present (k configurable, default 2 — FR-016): indirect/contextual identification distinct
from direct-span detection. ``score_quasi_identifier`` aggregates the FRACTION of combinations that
are re-identifying + integer counts over a corpus slice.

Both the per-combo ``QidCombo`` and the aggregate ``QuasiIdScore`` carry a **non-strippable v1.1
LOW-POWER caveat** (~72% formulaic synthetic enrichment — epistemic honesty; AX-003): empty ->
``ValueError``. Pure-stdlib + deterministic (NFR-004 / AX-002): test #6 is an AST guard pinning out
{random, time, uuid, datetime, secrets}.
"""

from __future__ import annotations

import ast
import pathlib

import pytest
from pii_anon_datasets.scoring import quasi_identifier as qid_mod
from pii_anon_datasets.scoring.quasi_identifier import (
    QUASI_IDENTIFIER_CAVEAT,
    QidCombo,
    QuasiIdScore,
    score_qid_combination,
    score_quasi_identifier,
)


def test_fr_016_combination_reidentifying_when_k_recovered() -> None:
    """A 3-qid combination with k=2 and 2 recovered is re-identifying — [UNIT-TEST].

    >= k recovered quasi-identifiers re-identify the combination (FR-016, default k=2).
    """
    combo = score_qid_combination(
        ["DATE_OF_BIRTH", "ORGANIZATION_NAME", "CITY"], {"DATE_OF_BIRTH", "CITY"}, k=2,
    )

    assert isinstance(combo, QidCombo)
    assert combo.reidentifying is True
    assert combo.n_qids == 3
    assert combo.n_recovered == 2
    assert combo.k == 2


def test_fr_016_combination_not_reidentifying_below_k() -> None:
    """Only 1 recovered with k=2 is NOT re-identifying — [UNIT-TEST]."""
    combo = score_qid_combination(
        ["DATE_OF_BIRTH", "ORGANIZATION_NAME", "CITY"], {"DATE_OF_BIRTH"}, k=2,
    )

    assert combo.reidentifying is False
    assert combo.n_recovered == 1


def test_fr_016_k1_any_one_recovered_reidentifies() -> None:
    """k=1: recovering ANY single quasi-identifier re-identifies the combination — [UNIT-TEST]."""
    combo = score_qid_combination(["DATE_OF_BIRTH", "CITY"], {"CITY"}, k=1)

    assert combo.reidentifying is True
    assert combo.k == 1
    assert combo.n_recovered == 1


def test_fr_016_score_aggregates_fraction_reidentifying() -> None:
    """score_quasi_identifier aggregates the FRACTION re-identifying + counts — [UNIT-TEST].

    With k=2, two of three combinations reach the threshold -> fraction_reidentifying == 2/3, with
    integer combination counts.
    """
    records_qids = [
        ["DATE_OF_BIRTH", "CITY"],                       # both recovered -> re-id
        ["ORGANIZATION_NAME", "POSTCODE", "JOB_TITLE"],  # 2 recovered -> re-id
        ["NATIONALITY"],                                 # 0 recovered -> not
    ]
    recovered = {"DATE_OF_BIRTH", "CITY", "POSTCODE", "JOB_TITLE"}

    score = score_quasi_identifier(records_qids, recovered, k=2)

    assert isinstance(score, QuasiIdScore)
    assert score.n_combinations == 3
    assert score.n_reidentifying == 2
    assert score.k == 2
    assert score.fraction_reidentifying == pytest.approx(2 / 3)
    assert all(isinstance(v, int) for v in (score.n_combinations, score.n_reidentifying))


def test_fr_016_caveat_non_strippable() -> None:
    """The v1.1 low-power caveat is non-strippable on BOTH dataclasses — [UNIT-TEST].

    ``QidCombo`` and ``QuasiIdScore`` constructed with an empty caveat raise ``ValueError``;
    ``QUASI_IDENTIFIER_CAVEAT`` states the ~72%-formulaic limited-power / external-validity honesty
    caveat (FR-016 v1.1; AX-003).
    """
    with pytest.raises(ValueError):
        QidCombo(reidentifying=False, n_qids=1, n_recovered=0, k=2, caveat="")
    with pytest.raises(ValueError):
        QidCombo(reidentifying=False, n_qids=1, n_recovered=0, k=2, caveat="   ")
    with pytest.raises(ValueError):
        QuasiIdScore(n_combinations=0, n_reidentifying=0, k=2, fraction_reidentifying=0.0, caveat="")

    lowered = QUASI_IDENTIFIER_CAVEAT.lower()
    assert "72%" in QUASI_IDENTIFIER_CAVEAT
    assert any(token in lowered for token in ("v1.1", "low", "limited"))
    assert any(token in lowered for token in ("external validity", "power"))


def test_nfr004_quasi_identifier_pure_stdlib() -> None:
    """AST guard (NFR-004 / AX-002): quasi_identifier.py imports no nondeterminism — [PROPERTY-TEST].

    The module imports none of {random, time, uuid, datetime, secrets} — pure-stdlib, deterministic.
    """
    src = pathlib.Path(qid_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)

    banned = {"random", "time", "uuid", "datetime", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), f"quasi_identifier.py imports nondeterministic modules: {sorted(banned & imported)}"
