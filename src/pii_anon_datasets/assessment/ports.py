"""Formal OutcomeDTO contract (CAP-02 C9) — the eval-data ↔ pii-rate-elo consumer boundary.

This is the OutcomeDTO port between eval-data (the ``report`` projection) and the pii-rate-elo consumer: a
``runtime_checkable`` structural Protocol pinning the 4 typed data attributes the report's leaderboard builder
reads off each system outcome. The pii-rate-elo orchestrator constructs :class:`report.SystemOutcome` (Elo +
Glicko-RD PASSED IN, never imported back — the FORBIDDEN EDGE, P1), which conforms to this port by structure.

Structural, not nominal: any producer exposing ``name`` / ``hits`` / ``elo`` / ``rd`` as object attributes
conforms — a plain ``dict`` does NOT (its keys are items, not attributes). ``runtime_checkable`` checks
attribute PRESENCE at ``isinstance``, not value types, so this guards the boundary shape, not the data.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class SystemOutcomePort(Protocol):
    """The OutcomeDTO recall view consumed by ``report.build_leaderboard`` (mirrors ``report.SystemOutcome``).

    Data attributes only (``runtime_checkable`` asserts their PRESENCE, not their types):
      * ``name``  — system identifier.
      * ``hits``  — aligned per-gold-positive recall vector (True == recalled).
      * ``elo``   — tournament Elo rating PASSED IN by the consumer (None when unrated).
      * ``rd``    — Glicko rating-deviation PASSED IN by the consumer (None when unrated).
    """

    name: str
    hits: tuple[bool, ...]
    elo: float | None
    rd: float | None


def conforms(obj: object) -> bool:
    """True iff ``obj`` structurally satisfies the OutcomeDTO port (all 4 attributes present)."""
    return isinstance(obj, SystemOutcomePort)
