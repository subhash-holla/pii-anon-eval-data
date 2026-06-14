"""Append-only, event-sourced held-out leaderboard store (DC-13; FR-023, NFR-014).

An append-only, content-hash-CHAINED JSONL event log for held-out leaderboard submissions. Each
submission-lifecycle event (:class:`EventType` ``submitted`` / ``scored`` / ``published``) is appended
to the log carrying the **content-hash of the prior event** (a hash chain), so the log is
**tamper-evident** -- :meth:`LeaderboardStore.verify_chain` recomputes the chain and detects any
mutation (NFR-014, governance neutrality / auditable).

Load-bearing contracts (the story gate -- security-sast load-bearing -- checks these):

* **append-only** -- ONLY :meth:`LeaderboardStore.append` writes, and it opens the log in mode ``"a"``
  (append). There is **no** ``update`` / ``delete`` / ``__setitem__`` / mutate method: this is an
  event-sourced log, so a prior event is never rewritten or removed. A second ``append`` grows the file
  and leaves the earlier lines' bytes unchanged.
* **no held-out gold (FR-023)** -- :meth:`LeaderboardStore.append` REJECTS (``ValueError``) any payload
  containing :data:`_FORBIDDEN_PAYLOAD_KEYS` (``gold`` / ``gold_labels`` / ``held_out`` /
  ``held_out_labels`` / ``answers`` / ``ground_truth``). The store records **scores + config/version
  attestation + provenance** and NEVER the undistributed held-out gold labels.
* **hash chain (NFR-014)** -- each event's ``prev_hash`` is the prior event's
  :meth:`LeaderboardEvent.content_hash`; the first event's ``prev_hash`` is :data:`GENESIS_HASH`
  (``"0" * 64``). :meth:`LeaderboardStore.verify_chain` recomputes every link and returns ``False`` on
  any mutated line.
* **deterministic (AX-002)** -- ordering is a monotonic ``seq`` (0..N-1), and hashing is over
  **canonical JSON** (``sort_keys=True``). There is **NO clock and NO RNG**: this module does not
  import ``time`` / ``datetime`` / ``random`` / ``uuid`` / ``secrets``. Any wall-clock timestamp is an
  *optional caller-provided payload field*, never generated here. Re-appending the same events to a
  fresh log therefore yields byte-identical content hashes.
* **pure-stdlib (NFR-004)** -- only :mod:`json` + :mod:`hashlib` + stdlib (``enum`` / ``dataclasses`` /
  ``pathlib`` / ``collections.abc``).

No hosted service in v1: this append-only hash-chained store IS the governance seam (gov-03 -- it
carries the affiliation + attestation that S6-03 produces; S6-02 policy reads it).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class EventType(str, Enum):
    """Submission-lifecycle event kinds appended to the leaderboard log."""

    SUBMITTED = "submitted"
    SCORED = "scored"
    PUBLISHED = "published"


GENESIS_HASH: str = "0" * 64  # prev_hash of the first event

# Held-out GOLD must NEVER enter the store (FR-023). Reject these payload keys.
_FORBIDDEN_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {"gold", "gold_labels", "held_out", "held_out_labels", "answers", "ground_truth"}
)


def _hash(
    seq: int,
    event_type: str,
    submission_id: str,
    payload: Mapping[str, object],
    prev_hash: str,
) -> str:
    """sha256 over the canonical JSON of the event's chained fields (sort_keys -> stable)."""
    blob = json.dumps(
        {
            "seq": seq,
            "event_type": event_type,
            "submission_id": submission_id,
            "payload": payload,
            "prev_hash": prev_hash,
        },
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LeaderboardEvent:
    """One immutable, content-hash-chained leaderboard event.

    ``payload`` carries scores / config_version / attestation / provenance -- NEVER held-out gold
    (FR-023; enforced by :meth:`LeaderboardStore.append`). ``prev_hash`` links this event to its
    predecessor (:data:`GENESIS_HASH` for the first).
    """

    seq: int
    event_type: EventType
    submission_id: str
    payload: Mapping[str, object]  # scores / config_version / attestation — NEVER gold
    prev_hash: str

    def content_hash(self) -> str:
        return _hash(self.seq, self.event_type.value, self.submission_id, self.payload, self.prev_hash)

    def as_dict(self) -> dict[str, object]:
        return {
            "seq": self.seq,
            "event_type": self.event_type.value,
            "submission_id": self.submission_id,
            "payload": dict(self.payload),
            "prev_hash": self.prev_hash,
        }


class LeaderboardStore:
    """Append-only, content-hash-chained JSONL event log. No update/delete (event-sourced)."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def events(self) -> list[LeaderboardEvent]:
        if not self.path.exists():
            return []
        out: list[LeaderboardEvent] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            out.append(
                LeaderboardEvent(
                    d["seq"],
                    EventType(d["event_type"]),
                    d["submission_id"],
                    d["payload"],
                    d["prev_hash"],
                )
            )
        return out

    def append(
        self,
        event_type: EventType,
        submission_id: str,
        payload: Mapping[str, object],
    ) -> LeaderboardEvent:
        bad = _FORBIDDEN_PAYLOAD_KEYS & set(payload)
        if bad:
            raise ValueError(f"held-out gold must not be stored (FR-023): forbidden keys {sorted(bad)}")
        existing = self.events()
        seq = len(existing)
        prev_hash = existing[-1].content_hash() if existing else GENESIS_HASH
        event = LeaderboardEvent(seq, event_type, submission_id, dict(payload), prev_hash)
        with self.path.open("a", encoding="utf-8") as f:  # APPEND only — never rewrites prior lines
            f.write(json.dumps(event.as_dict(), sort_keys=True, ensure_ascii=False) + "\n")
        return event

    def verify_chain(self) -> bool:
        prev = GENESIS_HASH
        for i, ev in enumerate(self.events()):
            if ev.seq != i or ev.prev_hash != prev:
                return False
            prev = ev.content_hash()
        return True
