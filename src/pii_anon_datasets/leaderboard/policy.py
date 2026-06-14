"""Held-out leaderboard submission policy: opt-in publish + anti-gaming (DC-13; FR-023, NFR-014).

A **pure-stdlib** submission policy layered over the S6-01 append-only
:class:`~pii_anon_datasets.leaderboard.store.LeaderboardStore`. :func:`evaluate_submission` returns a
:class:`PolicyDecision` ``(allowed, published, reasons)`` applying the FR-023 controls. The policy only
READS the store (it filters prior ``submitted`` events); the **caller** appends the resulting outcome
event — :func:`evaluate_submission` never writes.

Load-bearing contracts (the story gate -- security-sast is load-bearing -- checks these):

* **opt-in publish (FR-023)** -- ``published`` is True ONLY if the submission is ``allowed`` AND the
  submitter opted in (``Submission.publish_opt_in``). A disallowed submission is NEVER published.
* **anti-gaming active (NFR-014)** -- three controls are enforced, each contributing a distinct
  ``reason``: (1) **rate-limit** -- once a submitter reaches ``max_submissions_per_epoch`` prior
  ``submitted`` events in the current epoch, the next submission is ``"rate_limit"``-blocked;
  (2) **held-out rotation epoch** -- a submission whose ``declared_epoch`` != ``current_epoch`` is
  ``"stale_epoch"``-blocked (the held-out set rotates; stale-epoch submissions are invalid);
  (3) **contamination / duplicate** -- a re-used ``submission_hash`` is ``"duplicate"``-flagged.
* **read-only over the store (NFR-014)** -- :func:`evaluate_submission` calls only
  :meth:`~pii_anon_datasets.leaderboard.store.LeaderboardStore.events` (a read); it never appends. The
  caller records the outcome event, keeping the append-only log the single writer surface.
* **pure-stdlib + deterministic (NFR-004 / AX-002)** -- the decision is a pure function of (store events,
  submission, config). NO clock and NO RNG: this module does not import ``time`` / ``datetime`` /
  ``random`` / ``uuid`` / ``secrets``. Re-evaluating the same (store, submission, config) yields the
  same :class:`PolicyDecision`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from pii_anon_datasets.leaderboard.store import EventType, LeaderboardStore


@dataclass(frozen=True)
class PolicyConfig:
    current_epoch: int = 0  # the active held-out rotation epoch
    max_submissions_per_epoch: int = 5


@dataclass(frozen=True)
class Submission:
    submitter: str
    submission_hash: str  # content hash of the submission artifact (for contamination/dup)
    declared_epoch: int
    publish_opt_in: bool = False


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    published: bool
    reasons: tuple[str, ...]  # e.g. ("rate_limit",), ("stale_epoch",), ("duplicate",); () if clean


def _prior_submitted(store: LeaderboardStore) -> list[Mapping[str, object]]:
    """Payloads of prior ``submitted`` events."""
    return [e.payload for e in store.events() if e.event_type is EventType.SUBMITTED]


def evaluate_submission(store: LeaderboardStore, submission: Submission, config: PolicyConfig) -> PolicyDecision:
    """Apply the FR-023 controls; return a PolicyDecision. Pure-read over the store (no append)."""
    reasons: list[str] = []
    prior = _prior_submitted(store)

    # held-out rotation epoch: a submission must target the CURRENT epoch.
    if submission.declared_epoch != config.current_epoch:
        reasons.append("stale_epoch")

    # rate-limit: count this submitter's prior submissions in the current epoch.
    submitter_count = sum(
        1
        for p in prior
        if p.get("submitter") == submission.submitter and p.get("declared_epoch") == config.current_epoch
    )
    if submitter_count >= config.max_submissions_per_epoch:
        reasons.append("rate_limit")

    # contamination / duplicate: a re-used submission_hash.
    if any(p.get("submission_hash") == submission.submission_hash for p in prior):
        reasons.append("duplicate")

    allowed = not reasons
    published = allowed and submission.publish_opt_in
    return PolicyDecision(allowed=allowed, published=published, reasons=tuple(reasons))
