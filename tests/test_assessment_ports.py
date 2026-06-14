"""Contract test for the formal OutcomeDTO port (CAP-02 C9 — the consumer boundary).

Pins the runtime-checkable structural contract between eval-data's ``report.SystemOutcome`` (the de-facto DTO
the pii-rate-elo orchestrator constructs) and any conforming producer: ``conforms`` accepts the canonical
``SystemOutcome`` and any object exposing the 4 typed data attributes, and REJECTS one missing an attribute.
"""
from __future__ import annotations

import types
from dataclasses import dataclass

from pii_anon_datasets.assessment.ports import SystemOutcomePort, conforms
from pii_anon_datasets.assessment.report import SystemOutcome


def test_report_system_outcome_conforms() -> None:
    # The de-facto port the pii-rate-elo orchestrator builds MUST satisfy the formal contract.
    o = SystemOutcome(name="sys-a", hits=(True, False), elo=1500.0, rd=50.0)
    assert isinstance(o, SystemOutcomePort) is True
    assert conforms(o) is True


def test_minimal_simplenamespace_conforms() -> None:
    # Any duck-typed producer exposing the 4 attributes conforms (structural, not nominal).
    o = types.SimpleNamespace(name="sys-b", hits=(False, True, True), elo=None, rd=None)
    assert conforms(o) is True


def test_minimal_frozen_dataclass_conforms() -> None:
    @dataclass(frozen=True)
    class _MiniOutcome:
        name: str
        hits: tuple[bool, ...]
        elo: float | None
        rd: float | None

    assert conforms(_MiniOutcome(name="sys-c", hits=(True,), elo=1400.0, rd=80.0)) is True


def test_object_missing_rd_does_not_conform() -> None:
    # Drop one required attribute (``rd``) -> the runtime_checkable Protocol must reject it.
    o = types.SimpleNamespace(name="sys-d", hits=(True, True), elo=1600.0)  # no `rd`
    assert conforms(o) is False
    assert isinstance(o, SystemOutcomePort) is False


def test_plain_dict_does_not_conform() -> None:
    # Cross-repo note: a plain dict carries the keys as items, NOT as object attributes, so it does NOT
    # conform — the pii-rate-elo orchestrator therefore builds report.SystemOutcome objects, never dicts.
    d = {"name": "sys-e", "hits": (True, False), "elo": 1500.0, "rd": 50.0}
    assert conforms(d) is False
