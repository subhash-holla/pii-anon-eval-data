"""S6-03 — Conflict-of-interest record + recusal (DC-13; gov-03 / FR-026 / NFR-014).

Tokened ``fr_026`` / ``nfr_014`` / ``nfr004`` so the traceability gate can map test->requirement and
``pytest -k`` selects them. A :class:`CoIRecord` captures a leaderboard submitter's **affiliation** + a
**mandatory non-strippable** attestation that they (and their affiliated org) had **NO pre-publication
access** to the held-out evaluation set and did not train/tune on it (gov-03). ``requires_recusal`` is
True for a ``maintainer`` / ``pii-anon-core``-affiliated submitter — they cannot self-adjudicate their
own leaderboard entry (the governance-neutrality control, NFR-014). ``as_dict()`` makes the record an
embeddable provenance payload of a ``submitted`` event in the S6-01 store (never a held-out-gold key).

Load-bearing invariants the gate checks (axiom-compliance is load-bearing):
  * non-strippable attestation (gov-03 / FR-026) -- ``NO_PREPUB_ATTESTATION`` constant; non-defaulted-
    validated field; ``__post_init__`` rejects an empty/whitespace attestation -> ``ValueError``.
  * recusal (gov-03) -- ``requires_recusal`` True for ``maintainer`` / any ``pii-anon-core``-affiliated
    submitter (case-insensitive + substring), False for an external submitter.
  * embeddable provenance (NFR-014) -- ``as_dict()`` is a clean ``submitted``-event payload that the
    S6-01 store accepts (no forbidden held-out-gold key).
  * pure-stdlib + deterministic (NFR-004 / AX-002) -- AST guard bans {random, time, uuid, datetime,
    secrets}; no clock/RNG.

Uses ``tmp_path`` for the JSONL store log (no real FS outside the pytest tempdir; deterministic).
"""

from __future__ import annotations

import ast
import inspect
import pathlib

import pytest
from pii_anon_datasets.leaderboard import coi as coi_mod
from pii_anon_datasets.leaderboard.coi import NO_PREPUB_ATTESTATION, CoIRecord
from pii_anon_datasets.leaderboard.store import EventType, LeaderboardStore


# --------------------------------------------------------------------------------------
# 1. non-strippable attestation — empty/whitespace rejected; default attests no pre-pub access
#    (gov-03 / FR-026)
# --------------------------------------------------------------------------------------
@pytest.mark.parametrize("empty", ["", "   ", "\t", "\n  \n"])
def test_fr_026_attestation_is_non_strippable(empty):
    """[UNIT-TEST] An empty/whitespace ``attestation`` is rejected (``ValueError``); the default
    ``NO_PREPUB_ATTESTATION`` attests no pre-publication access to the held-out set and no train/tune."""
    with pytest.raises(ValueError):
        CoIRecord(submitter="Dr. Ada", affiliation="Acme University", attestation=empty)

    # the default constant is the mandatory non-strippable attestation text.
    default = NO_PREPUB_ATTESTATION.lower()
    assert "pre-publication" in default and "access" in default
    assert "held-out" in default
    assert "train" in default or "tune" in default
    # a record built with the default carries that exact (non-empty) attestation.
    rec = CoIRecord(submitter="Dr. Ada", affiliation="Acme University")
    assert rec.attestation == NO_PREPUB_ATTESTATION
    assert rec.attestation.strip()


# --------------------------------------------------------------------------------------
# 2. recusal — maintainer / pii-anon-core-affiliated submitter must be recused (gov-03)
# --------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "affiliation",
    ["maintainer", "pii-anon-core", "Pii-Anon-Core Labs", "  MAINTAINER  ", "PII-ANON-CORE"],
)
def test_fr_026_recusal_for_maintainer_and_affiliated(affiliation):
    """[UNIT-TEST] ``requires_recusal`` is True for a ``maintainer`` / ``pii-anon-core``-affiliated
    submitter (case-insensitive exact token + ``pii-anon-core`` substring), False for an external one."""
    assert CoIRecord(submitter="Self", affiliation=affiliation).requires_recusal is True

    # an external affiliation does NOT require recusal.
    assert CoIRecord(submitter="Dr. Ada", affiliation="Acme University").requires_recusal is False
    assert CoIRecord(submitter="Dr. Ada", affiliation="Independent Researcher").requires_recusal is False


# --------------------------------------------------------------------------------------
# 3. embeddable provenance — as_dict() is a clean `submitted`-event payload in the S6-01 store
#    (NFR-014); not a forbidden held-out-gold key
# --------------------------------------------------------------------------------------
def test_nfr_014_coi_as_dict_embeddable_in_store(tmp_path):
    """[INTEGRATION-TEST] ``record.as_dict()`` yields submitter/affiliation/attestation/requires_recusal,
    and a ``LeaderboardStore.append(EventType.SUBMITTED, …, payload=record.as_dict())`` succeeds — the
    CoI provenance is logged (it is NOT a forbidden held-out-gold key)."""
    record = CoIRecord(submitter="Self", affiliation="pii-anon-core")
    payload = record.as_dict()
    assert set(payload) >= {"submitter", "affiliation", "attestation", "requires_recusal"}
    assert payload["submitter"] == "Self"
    assert payload["affiliation"] == "pii-anon-core"
    assert payload["attestation"] == NO_PREPUB_ATTESTATION
    assert payload["requires_recusal"] is True

    store = LeaderboardStore(tmp_path / "log.jsonl")
    event = store.append(EventType.SUBMITTED, "sub-1", payload)
    assert event.event_type is EventType.SUBMITTED
    # round-trips through the append-only log and the chain still verifies.
    assert store.events()[0].payload["requires_recusal"] is True
    assert store.verify_chain() is True


# --------------------------------------------------------------------------------------
# 4. pure-stdlib — AST guard: coi.py imports none of {random, time, uuid, datetime, secrets}
#    (NFR-004 / AX-002)
# --------------------------------------------------------------------------------------
def test_nfr004_coi_pure_stdlib():
    """[PROPERTY-TEST] AST guard: ``coi.py`` imports none of {random, time, uuid, datetime, secrets}
    (no clock/RNG -> deterministic); ``import pii_anon_datasets.leaderboard`` succeeds."""
    import importlib

    importlib.import_module("pii_anon_datasets.leaderboard")

    src = pathlib.Path(inspect.getsourcefile(coi_mod)).read_text(encoding="utf-8")
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
        f"coi.py imports nondeterministic modules (no clock/RNG allowed): {sorted(banned & imported)}"
    )
