"""Coreference-chain UNIT scoring (FR-015; DC-01, v1.1 — AX linkage AX-001/002/003).

A coreference chain is scored as a UNIT, not as atomic spans: it is "leaked" iff ANY of its
mentions is recovered by the detector (any-mention semantics — FR-015). ``score_coreference``
aggregates the FRACTION of chains leaked + integer counts over a corpus slice.

Both the per-chain ``ChainLeak`` and the aggregate ``CoreferenceScore`` carry a **non-strippable
v1.1 LOW-POWER caveat** (~72% formulaic synthetic enrichment — epistemic honesty; AX-003): empty
-> ``ValueError``. Pure-stdlib + deterministic (NFR-004 / AX-002): test #5 is an AST guard pinning
out {random, time, uuid, datetime, secrets}.
"""

from __future__ import annotations

import ast
import pathlib

import pytest
from pii_anon_datasets.scoring import coreference as coref_mod
from pii_anon_datasets.scoring.coreference import (
    COREFERENCE_CAVEAT,
    ChainLeak,
    CoreferenceScore,
    score_coreference,
    score_coreference_chain,
)


def test_fr_015_chain_leaked_if_any_mention_recovered() -> None:
    """A 3-mention chain with only 1 mention recovered is LEAKED — [UNIT-TEST].

    Any-mention semantics (FR-015): recovering even a single mention re-identifies the whole
    coreference chain, so the chain counts as leaked as a UNIT.
    """
    leak = score_coreference_chain(["m1", "m2", "m3"], {"m2"})

    assert isinstance(leak, ChainLeak)
    assert leak.leaked is True
    assert leak.n_mentions == 3
    assert leak.n_recovered == 1


def test_fr_015_chain_not_leaked_when_zero_recovered() -> None:
    """A chain with NONE of its mentions recovered is not leaked — [UNIT-TEST]."""
    leak = score_coreference_chain(["m1", "m2", "m3"], {"x9", "y8"})

    assert leak.leaked is False
    assert leak.n_mentions == 3
    assert leak.n_recovered == 0


def test_fr_015_score_aggregates_fraction_leaked() -> None:
    """score_coreference aggregates the FRACTION of chains leaked + counts — [UNIT-TEST].

    Two of three chains have >= 1 recovered mention -> fraction_leaked == 2/3 (chains scored as
    UNITS — FR-015), with integer chain counts.
    """
    chains = [["a1", "a2"], ["b1", "b2", "b3"], ["c1"]]
    recovered = {"a2", "b1"}  # chain a leaked, chain b leaked, chain c not

    score = score_coreference(chains, recovered)

    assert isinstance(score, CoreferenceScore)
    assert score.n_chains == 3
    assert score.n_leaked == 2
    assert score.fraction_leaked == pytest.approx(2 / 3)
    assert all(isinstance(v, int) for v in (score.n_chains, score.n_leaked))


def test_fr_015_score_empty_corpus_is_zero_fraction() -> None:
    """No chains -> fraction_leaked is 0.0 (no division-by-zero) — [UNIT-TEST]."""
    score = score_coreference([], set())

    assert score.n_chains == 0
    assert score.n_leaked == 0
    assert score.fraction_leaked == 0.0


def test_fr_015_caveat_non_strippable() -> None:
    """The v1.1 low-power caveat is non-strippable on BOTH dataclasses — [UNIT-TEST].

    ``ChainLeak`` and ``CoreferenceScore`` constructed with an empty caveat raise ``ValueError``;
    ``COREFERENCE_CAVEAT`` states the ~72%-formulaic limited-power / external-validity honesty
    caveat (FR-015 v1.1; AX-003).
    """
    with pytest.raises(ValueError):
        ChainLeak(leaked=True, n_mentions=1, n_recovered=1, caveat="")
    with pytest.raises(ValueError):
        ChainLeak(leaked=True, n_mentions=1, n_recovered=1, caveat="   ")
    with pytest.raises(ValueError):
        CoreferenceScore(n_chains=0, n_leaked=0, fraction_leaked=0.0, caveat="")

    lowered = COREFERENCE_CAVEAT.lower()
    assert "72%" in COREFERENCE_CAVEAT
    assert any(token in lowered for token in ("v1.1", "low", "limited"))
    assert any(token in lowered for token in ("external validity", "power"))


def test_nfr004_coreference_pure_stdlib() -> None:
    """AST guard (NFR-004 / AX-002): coreference.py imports no nondeterminism — [PROPERTY-TEST].

    The module imports none of {random, time, uuid, datetime, secrets} — pure-stdlib, deterministic.
    """
    src = pathlib.Path(coref_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)

    banned = {"random", "time", "uuid", "datetime", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), f"coreference.py imports nondeterministic modules: {sorted(banned & imported)}"
