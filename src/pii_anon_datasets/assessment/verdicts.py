"""4-state power classification + corpus verdict (CAP-02 DC-18 / NFR-035/036/037).

Extends the audited ``stats/power.py`` 3-state ``PowerClass`` (WELL / UNDER / EMPTY) with the assessment's
sample-vs-corpus distinction — **UNDER_SAMPLED** (the corpus HAS enough positives, the draw got too few → a
bigger draw fixes it) vs **CORPUS_LIMITED** (the corpus itself is short → drawing more cannot fix it) — plus
**NOT_ASSESSED** for cells outside the coverage envelope. ``stats/power.py::classify`` is NOT mutated; the
4th/5th states are DERIVED here against full-corpus realized positives so the audited core stays unchanged.

POWER SCOPING (stat-03): ``required_n`` / ``TIER_SPECS`` size the RECALL operating point only, so a cell's
``power_class`` covers ``recall@p_ref`` and NOTHING else; precision / Fβ / AUPRC / re-id are ``NOT_ASSESSED``
for power unless re-sized by a matching ladder. Pure-stdlib, deterministic.
"""
from __future__ import annotations

from collections.abc import Iterable
from enum import Enum

POWER_OPERATING_POINT = "recall@p_ref"


class PowerClass(str, Enum):
    WELL_POWERED = "well_powered"
    UNDER_SAMPLED = "under_sampled"      # fixable: corpus has enough, draw more
    CORPUS_LIMITED = "corpus_limited"    # irreducible: corpus itself short
    EMPTY = "empty"
    NOT_ASSESSED = "not_assessed"        # outside coverage envelope


def _require_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be a non-bool int; got {value!r}")


def classify_cell(n_sample: int, n_full: int, target_n: int, *, in_envelope: bool = True) -> PowerClass:
    """4-state power class for a committed cell, against REALIZED positives (recall operating point, stat-03)."""
    _require_int("n_sample", n_sample)
    _require_int("n_full", n_full)
    _require_int("target_n", target_n)
    if not in_envelope:
        return PowerClass.NOT_ASSESSED
    if n_sample == 0 and n_full == 0:
        return PowerClass.EMPTY
    if n_sample >= target_n:
        return PowerClass.WELL_POWERED
    if n_full >= target_n:
        return PowerClass.UNDER_SAMPLED
    return PowerClass.CORPUS_LIMITED


def shortfall(n_sample: int, target_n: int) -> int:
    """Named shortfall in REALIZED positives (integer, non-strippable in the report; NFR-036)."""
    _require_int("n_sample", n_sample)
    _require_int("target_n", target_n)
    return max(0, target_n - n_sample)


def corpus_verdict(power_classes: Iterable[PowerClass]) -> str:
    """Corpus-level SMALL / ADEQUATE / LARGE, mirroring ``power.PowerMatrix.verdict`` thresholds
    (LARGE iff fraction well-powered ≥ 0.999, ADEQUATE iff ≥ 0.80, else SMALL). NOT_ASSESSED cells are
    excluded from the denominator. A sample run never renders a bare ``LARGE`` — the manifest/report bind
    this token to the synthetic-only / conditional-on-this-sample caveat (integrity-MAJOR-2)."""
    assessed = [pc for pc in power_classes if pc is not PowerClass.NOT_ASSESSED]
    if not assessed:
        return "SMALL"
    frac = sum(1 for pc in assessed if pc is PowerClass.WELL_POWERED) / len(assessed)
    if frac >= 0.999:
        return "LARGE"
    if frac >= 0.80:
        return "ADEQUATE"
    return "SMALL"
