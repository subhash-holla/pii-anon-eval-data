"""Held-out leaderboard governance seam (DC-13; FR-023, NFR-014).

Re-exports the append-only, content-hash-chained store API
(:class:`~pii_anon_datasets.leaderboard.store.LeaderboardStore` /
:class:`~pii_anon_datasets.leaderboard.store.LeaderboardEvent` /
:class:`~pii_anon_datasets.leaderboard.store.EventType` /
:data:`~pii_anon_datasets.leaderboard.store.GENESIS_HASH`) plus the S6-02 submission-policy API
(:class:`~pii_anon_datasets.leaderboard.policy.PolicyConfig` /
:class:`~pii_anon_datasets.leaderboard.policy.Submission` /
:class:`~pii_anon_datasets.leaderboard.policy.PolicyDecision` /
:func:`~pii_anon_datasets.leaderboard.policy.evaluate_submission` — opt-in publish + anti-gaming over the
store) and the S6-03 conflict-of-interest API
(:class:`~pii_anon_datasets.leaderboard.coi.CoIRecord` /
:data:`~pii_anon_datasets.leaderboard.coi.NO_PREPUB_ATTESTATION` — a submitter's affiliation + a
non-strippable no-pre-publication-access attestation + a maintainer/``pii-anon-core`` recusal flag,
embeddable as a ``submitted``-event provenance payload), and provides the minimal CLI :func:`main` that
wires the S5-05 ``pii-anon leaderboard`` verb (``verify <log>`` -> ``verify_chain``).
"""

from __future__ import annotations

import sys
from collections.abc import Sequence

from pii_anon_datasets.leaderboard.coi import NO_PREPUB_ATTESTATION, CoIRecord
from pii_anon_datasets.leaderboard.policy import (
    PolicyConfig,
    PolicyDecision,
    Submission,
    evaluate_submission,
)
from pii_anon_datasets.leaderboard.store import (
    GENESIS_HASH,
    EventType,
    LeaderboardEvent,
    LeaderboardStore,
)

__all__ = [
    "GENESIS_HASH",
    "NO_PREPUB_ATTESTATION",
    "CoIRecord",
    "EventType",
    "LeaderboardEvent",
    "LeaderboardStore",
    "PolicyConfig",
    "PolicyDecision",
    "Submission",
    "evaluate_submission",
    "main",
]


def main(argv: Sequence[str] | None = None) -> int:
    """Minimal leaderboard CLI (wires the S5-05 ``pii-anon leaderboard`` verb). ``verify <log>``."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) >= 2 and args[0] == "verify":
        ok = LeaderboardStore(args[1]).verify_chain()
        print("chain OK" if ok else "chain BROKEN", file=sys.stderr)
        return 0 if ok else 1
    print("usage: pii-anon leaderboard verify <log.jsonl>", file=sys.stderr)
    return 2
