"""Outbound adversary port — value objects + Protocol (FR-010; DC-07; reidx-01).

Establishes the interchangeable re-identification attacker contract that the
measured-attack RRS scorer (DC-07 / S3-04), the anonymization residual-risk scorer
(DC-06), and the LLM adversary (S3-03) all plug into. No adversary *implementation*
lives here — only the contract + the frozen value objects.

FR-010: a consumer supplies an object exposing ``adversary_id``, ``deterministic`` and
``attack(...)``; the scoring core type-checks it against :class:`Adversary` and pins
its ``adversary_id`` for version-pinning ("vs adversary@version").

reidx-01 (LOAD-BEARING): :class:`Target` carries ``observed_signals`` RE-EXTRACTED from
the anonymized text via :func:`pii_anon_datasets.scoring.signals.extract` — never the
gold ``Persona.behavioral_signals``. Copying gold would collapse a downstream RRS back
into the precomputed heuristic, the exact defect the SME panel flagged.

Determinism (AX-002): the value objects are frozen dataclasses; the headline adversary
is expected to set ``deterministic=True``.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..signals import SignalsBlock

ADVERSARY_PORT_VERSION = "adversary-port-v1"


@dataclass(frozen=True)
class Persona:
    """The REAL side of a paired record — the ground-truth identity (read-only gold)."""

    persona_id: str
    """Stable identity key; equals the source ``record_id``."""
    record_id: str
    """Source corpus ``record_id``."""
    quasi_identifiers: tuple[tuple[str, str], ...]
    """Sorted ``((entity_type, value), ...)`` extracted from the record annotations."""
    behavioral_signals: SignalsBlock
    """Gold ``tier3_evaluation.behavioral_signals`` (read-only; never the adversary's view)."""
    source_text: str
    """The original real text."""


@dataclass(frozen=True)
class Target:
    """The PSEUDONYMOUS side the adversary attacks."""

    target_id: str
    """Ground-truth link: equals the ``persona_id`` of its true source."""
    anonymized_text: str
    """e.g. ``context_preservation.anonymized_pseudonymized``."""
    observed_signals: SignalsBlock
    """RE-EXTRACTED from ``anonymized_text`` via ``signals.extract`` — NOT gold (reidx-01)."""


@dataclass(frozen=True)
class Guess:
    """An adversary's ranked attribution for one target."""

    target_id: str
    guessed_persona_id: str | None
    """``None`` == abstain (excluded from the precision denominator); a string == a commitment."""
    score: float
    """Similarity / confidence for ranking."""


@runtime_checkable
class Adversary(Protocol):
    """Outbound port: an interchangeable re-identification attacker (FR-010).

    A conforming object exposes a version-pinned ``adversary_id`` (so results can be
    cited as "vs adversary@version"), a ``deterministic`` flag (the headline RRS uses a
    deterministic offline adversary — reidx-01), and an ``attack`` method that maps a set
    of pseudonymous :class:`Target` s against a candidate pool of real :class:`Persona` s,
    under an explicit closed-world ``candidate_set_size`` (|C|), to ranked :class:`Guess` es.
    """

    adversary_id: str
    deterministic: bool

    def attack(
        self,
        targets: Sequence[Target],
        candidates: Sequence[Persona],
        candidate_set_size: int,
    ) -> list[Guess]:
        """Re-link each pseudonymous ``Target`` against the real ``candidates`` pool.

        Returns one ranked :class:`Guess` per target (``guessed_persona_id=None`` to
        abstain). ``candidate_set_size`` (|C|) fixes the closed-world the recall/precision
        are measured against. Implementations MUST be pure in ``(targets, candidates,
        candidate_set_size)`` when ``deterministic`` is ``True``.
        """
        ...
