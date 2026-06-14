"""Leaderboard hygiene + governance / anti-gaming (CAP-02 DC-29 / FR-051/052; NFR-048/049; AX-005 #6).

Structured, non-strippable governance for a published assessment run:

- :class:`GovernanceBlock` ``{corpus_owner, label_holder, evaluator}`` — a neutrality/provenance statement
  rendered on EVERY report page (FR-052); a managed conflict triggers a required ``recusal_record``.
- ``contamination_status`` per submitted system — ``'unknown'`` is REJECTED (FR-051 / FR-043).
- :class:`Attestation` ``{submitter_id, statement, signature, signed_at}`` — a held-out-non-exposure
  attestation that is present + well-formed and, when a key is configured, VERIFIES under an HMAC-SHA256 keyed
  scheme (pure-stdlib; AX-005 element 6). A real asymmetric scheme can drop in behind the same verify seam.
- :func:`scoring_response_is_clean` — the scoring-API-surface oracle: a scoring response that leaks a held-out
  gold-label field is rejected (labels never returned).

Pure-stdlib (NFR-050); deterministic. This module computes/validates hygiene; it never scores.
"""
from __future__ import annotations

import hashlib
import hmac
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

CONTAMINATION_UNKNOWN = "unknown"

# Gold / held-out label field names a scoring RESPONSE must never carry (the API-surface oracle, FR-051).
HELD_OUT_LABEL_FIELDS = ("held_out_label", "held_out_labels", "gold", "gold_label", "gold_spans", "annotations")

GOVERNANCE_DISCLAIMER = (
    "Governance block is a NEUTRALITY / PROVENANCE statement (who controls the corpus, who holds the held-out "
    "labels, who runs the eval) — NOT an endorsement. A vendor self-benchmark without it is inadmissible (FR-052)."
)


@dataclass(frozen=True)
class GovernanceBlock:
    """Per-page neutrality statement (FR-052). All three identities + the disclaimer are non-strippable."""

    corpus_owner: str
    label_holder: str
    evaluator: str
    disclaimer: str = GOVERNANCE_DISCLAIMER

    def __post_init__(self) -> None:
        for name in ("corpus_owner", "label_holder", "evaluator"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"GovernanceBlock requires a non-empty {name} (FR-052)")
        if not self.disclaimer.strip():
            raise ValueError("GovernanceBlock requires a non-empty neutrality disclaimer (FR-052)")

    def as_dict(self) -> dict[str, str]:
        return {
            "corpus_owner": self.corpus_owner,
            "label_holder": self.label_holder,
            "evaluator": self.evaluator,
            "disclaimer": self.disclaimer,
        }


@dataclass(frozen=True)
class Attestation:
    """Signed held-out-non-exposure attestation (FR-051; AX-005 element 6). All fields non-empty."""

    submitter_id: str
    statement: str
    signature: str
    signed_at: str

    def __post_init__(self) -> None:
        for name in ("submitter_id", "statement", "signature", "signed_at"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"Attestation requires a non-empty {name} (FR-051)")

    def as_dict(self) -> dict[str, str]:
        return {
            "submitter_id": self.submitter_id,
            "statement": self.statement,
            "signature": self.signature,
            "signed_at": self.signed_at,
        }


def sign_attestation(*, submitter_id: str, statement: str, signed_at: str, key: bytes) -> str:
    """Deterministic HMAC-SHA256 signature over the canonical attestation payload (stdlib; AX-005 #6)."""
    msg = f"{submitter_id}\x1f{statement}\x1f{signed_at}".encode()
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def verify_attestation(att: Attestation, *, key: bytes | None = None) -> bool:
    """Well-formedness is enforced at construction; when a key is configured the HMAC signature must verify."""
    if key is None:
        return True  # no signing scheme configured -> structural presence is the bar (FR-051)
    expected = sign_attestation(
        submitter_id=att.submitter_id, statement=att.statement, signed_at=att.signed_at, key=key
    )
    return hmac.compare_digest(expected, att.signature)


def require_contamination_known(status: str) -> str:
    """Return ``status`` or raise if it is empty / ``'unknown'`` (FR-051 / FR-043)."""
    s = str(status).strip()
    if not s or s.lower() == CONTAMINATION_UNKNOWN:
        raise ValueError(f"contamination_status {status!r} rejected: must be known (not 'unknown') — FR-051/FR-043")
    return status


@dataclass(frozen=True)
class LeaderboardEntry:
    """A submitted system's hygiene metadata (consumed by :func:`gate_leaderboard`)."""

    system: str
    contamination_status: str
    owner_identities: tuple[str, ...] = ()          # who owns / submitted this system
    attestation: Attestation | None = None


def recusal_required(evaluator: str, entries: Sequence[LeaderboardEntry]) -> bool:
    """True iff the evaluator identity owns any leaderboard entry (a managed conflict — FR-052)."""
    ev = evaluator.strip().lower()
    return any(ev == o.strip().lower() for e in entries for o in e.owner_identities)


def gate_leaderboard(
    *,
    governance: GovernanceBlock,
    entries: Sequence[LeaderboardEntry],
    recusal_records: Mapping[str, str] | None = None,
    key: bytes | None = None,
) -> dict:
    """Validate the hygiene gate (FR-051/052; NFR-048/049) and return the structured governance dict to embed
    in the run-record + every report page. Raises ``ValueError`` on any violation."""
    records = {k.strip().lower(): v for k, v in dict(recusal_records or {}).items()}
    for e in entries:
        require_contamination_known(e.contamination_status)               # 'unknown' rejected
        if e.attestation is not None and not verify_attestation(e.attestation, key=key):
            raise ValueError(f"attestation for {e.system!r} failed signature verification (FR-051)")
    if recusal_required(governance.evaluator, entries) and not records.get(governance.evaluator.strip().lower()):
        raise ValueError(
            f"evaluator {governance.evaluator!r} owns a leaderboard entry but has no recusal_record (FR-052)"
        )
    return {
        "governance": governance.as_dict(),
        "contamination": {e.system: e.contamination_status for e in entries},
        "attestations": {e.system: (e.attestation.as_dict() if e.attestation else None) for e in entries},
        "recusal_records": {k: v for k, v in records.items()},
    }


def scoring_response_is_clean(response: Mapping[str, object]) -> bool:
    """The scoring-API-surface oracle (FR-051): a scoring response must NOT carry any held-out gold-label field."""
    return not any(field in response for field in HELD_OUT_LABEL_FIELDS)
