"""Conflict-of-interest record + recusal control (DC-13; gov-03 / FR-026 / NFR-014).

A frozen :class:`CoIRecord` value object captures a leaderboard submitter's **affiliation** plus a
**mandatory non-strippable** attestation that they (and their affiliated org) had **NO pre-publication
access** to the held-out evaluation set and did not train or tune on it (gov-03 / FR-026). The
attestation is non-strippable: it is a non-defaulted-validated field whose ``__post_init__`` rejects an
empty/whitespace value, following the same pattern as the
:data:`~pii_anon_datasets.compliance.crosswalk.CROSSWALK_DISCLAIMER` (a module constant +
``__post_init__`` guard).

:attr:`CoIRecord.requires_recusal` is ``True`` for a ``maintainer`` / ``pii-anon-core``-affiliated
submitter — such a submitter must be **recused** from self-adjudicating their own leaderboard entry (the
governance-neutrality control, NFR-014). It matches an exact affiliation token (case-insensitive) or any
``pii-anon-core`` substring, and is ``False`` for an external submitter (e.g. an academic institution).

:meth:`CoIRecord.as_dict` makes the record an embeddable **provenance payload** of a ``submitted`` event
in the S6-01 :class:`~pii_anon_datasets.leaderboard.store.LeaderboardStore` — it carries
submitter/affiliation/attestation/requires_recusal and is NEVER a held-out-gold key (so the store accepts
it; FR-023).

Pure-stdlib (NFR-004); deterministic — no clock/RNG, no import of {random, time, uuid, datetime,
secrets} (AX-002).
"""

from __future__ import annotations

from dataclasses import dataclass

# Non-strippable (gov-03): the held-out set must not have been seen pre-publication.
NO_PREPUB_ATTESTATION: str = (
    "I attest that I and my affiliated organization had NO pre-publication access to the held-out "
    "evaluation set, and did not train or tune on it (gov-03 / FR-026)."
)

# Affiliations that REQUIRE recusal from self-adjudicating a leaderboard entry (governance neutrality).
# Exact tokens + a substring match for any 'pii-anon-core'-affiliated org.
_RECUSAL_TOKENS: frozenset[str] = frozenset({"maintainer", "pii-anon-core"})
_RECUSAL_SUBSTRING: str = "pii-anon-core"


@dataclass(frozen=True)
class CoIRecord:
    """A submitter's affiliation + non-strippable no-pre-publication-access attestation (gov-03).

    ``requires_recusal`` is True for a maintainer / pii-anon-core-affiliated submitter — they cannot
    self-adjudicate their own leaderboard entry. ``attestation`` is mandatory + non-strippable.
    """

    submitter: str
    affiliation: str
    attestation: str = NO_PREPUB_ATTESTATION

    def __post_init__(self) -> None:
        if not self.attestation.strip():
            raise ValueError("CoI attestation required (gov-03 non-strippable)")

    @property
    def requires_recusal(self) -> bool:
        a = self.affiliation.strip().lower()
        return a in _RECUSAL_TOKENS or _RECUSAL_SUBSTRING in a

    def as_dict(self) -> dict[str, object]:
        """Provenance payload for a `submitted` store event (S6-01) — never a held-out-gold key."""
        return {
            "submitter": self.submitter,
            "affiliation": self.affiliation,
            "attestation": self.attestation,
            "requires_recusal": self.requires_recusal,
        }
