"""S6-02 — Leaderboard submission policy: opt-in publish + anti-gaming (DC-13; FR-023, NFR-014).

Tokened ``fr_023`` / ``nfr_014`` / ``nfr004`` so the traceability gate can map test->requirement and
``pytest -k`` selects them. A **pure-stdlib** policy over the S6-01 append-only
:class:`~pii_anon_datasets.leaderboard.store.LeaderboardStore`. ``evaluate_submission(store, submission,
config)`` returns a :class:`~pii_anon_datasets.leaderboard.policy.PolicyDecision` applying the FR-023
controls:

  * **opt-in publish (FR-023)** — ``published`` is True ONLY if the submission is ``allowed`` AND the
    submitter opted in (``publish_opt_in``). A disallowed submission is NEVER published.
  * **rate-limit (NFR-014)** — once a submitter reaches ``max_submissions_per_epoch`` prior ``submitted``
    events in the current epoch, the next submission is blocked with a ``"rate_limit"`` reason.
  * **held-out rotation epoch (NFR-014)** — a submission whose ``declared_epoch`` != ``current_epoch`` is
    blocked with a ``"stale_epoch"`` reason (the held-out set rotates; stale-epoch submissions are stale).
  * **contamination / duplicate (NFR-014)** — a re-used ``submission_hash`` (already in a prior
    ``submitted`` event) is blocked with a ``"duplicate"`` reason.

Load-bearing (security-sast): the policy only READS the store (never appends — the caller records the
outcome event), and the decision is a **pure function** of (store events, submission, config) — no
clock/RNG (NFR-004 / AX-002). The ``nfr004`` AST guard pins the pure-stdlib import surface.

Uses ``tmp_path`` for the JSONL log (no real FS outside the pytest tempdir; deterministic). Prior
``submitted`` events are appended via the real store so the policy reads exactly what the caller wrote.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

from pii_anon_datasets.leaderboard import policy as policy_mod
from pii_anon_datasets.leaderboard.policy import (
    PolicyConfig,
    PolicyDecision,
    Submission,
    evaluate_submission,
)
from pii_anon_datasets.leaderboard.store import EventType, LeaderboardStore


def _store(tmp_path: pathlib.Path) -> LeaderboardStore:
    """A fresh append-only store backed by a JSONL log inside the pytest tempdir (deterministic)."""
    return LeaderboardStore(tmp_path / "lb.jsonl")


# --------------------------------------------------------------------------------------
# 1. opt-in publish (FR-023) — an allowed submission is published ONLY on publish_opt_in=True
# --------------------------------------------------------------------------------------
def test_fr_023_publish_is_opt_in(tmp_path: pathlib.Path) -> None:
    """[UNIT-TEST] An allowed (fresh/in-epoch/under-limit) submission with ``publish_opt_in=False`` is
    NOT published; the same submission with ``publish_opt_in=True`` IS published. Opt-in gates
    publication — the publish decision turns solely on the submitter's consent, not on allowance."""
    store = _store(tmp_path)
    config = PolicyConfig(current_epoch=0, max_submissions_per_epoch=5)

    opted_out = Submission(submitter="alice", submission_hash="h-out", declared_epoch=0, publish_opt_in=False)
    decision_out = evaluate_submission(store, opted_out, config)
    assert decision_out.allowed is True
    assert decision_out.published is False  # allowed but did NOT opt in -> not published

    opted_in = Submission(submitter="alice", submission_hash="h-in", declared_epoch=0, publish_opt_in=True)
    decision_in = evaluate_submission(store, opted_in, config)
    assert decision_in.allowed is True
    assert decision_in.published is True  # allowed AND opted in -> published


# --------------------------------------------------------------------------------------
# 2. rate-limit (NFR-014) — once a submitter hits max_submissions_per_epoch in-epoch, block
# --------------------------------------------------------------------------------------
def test_nfr_014_rate_limit_blocks_excess(tmp_path: pathlib.Path) -> None:
    """[UNIT-TEST] After ``max_submissions_per_epoch`` prior ``submitted`` events by a submitter in the
    CURRENT epoch, the next ``evaluate_submission`` for that submitter returns ``allowed is False`` with a
    ``"rate_limit"`` reason. The count is read from the store's prior ``submitted`` events (anti-gaming)."""
    store = _store(tmp_path)
    config = PolicyConfig(current_epoch=2, max_submissions_per_epoch=3)

    # 3 prior in-epoch submissions by alice -> she is now AT the per-epoch limit.
    for i in range(config.max_submissions_per_epoch):
        store.append(
            EventType.SUBMITTED,
            f"alice-{i}",
            {"submitter": "alice", "submission_hash": f"alice-h-{i}", "declared_epoch": 2},
        )

    # the 4th distinct in-epoch submission by alice is rate-limited.
    excess = Submission(submitter="alice", submission_hash="alice-h-new", declared_epoch=2, publish_opt_in=True)
    decision = evaluate_submission(store, excess, config)
    assert decision.allowed is False
    assert "rate_limit" in decision.reasons
    assert decision.published is False  # blocked -> never published even with opt-in

    # a DIFFERENT submitter is unaffected by alice's count (the limit is per-submitter).
    other = Submission(submitter="bob", submission_hash="bob-h-1", declared_epoch=2, publish_opt_in=False)
    other_decision = evaluate_submission(store, other, config)
    assert other_decision.allowed is True
    assert "rate_limit" not in other_decision.reasons


# --------------------------------------------------------------------------------------
# 3. held-out rotation epoch (NFR-014) — declared_epoch != current_epoch -> stale_epoch block
# --------------------------------------------------------------------------------------
def test_nfr_014_held_out_rotation_epoch(tmp_path: pathlib.Path) -> None:
    """[UNIT-TEST] A submission whose ``declared_epoch`` != ``config.current_epoch`` returns ``allowed is
    False`` with a ``"stale_epoch"`` reason (the held-out set ROTATES; a submission is valid only against
    the current epoch). A submission against the current epoch carries no ``stale_epoch`` reason."""
    store = _store(tmp_path)
    config = PolicyConfig(current_epoch=5, max_submissions_per_epoch=5)

    stale = Submission(submitter="carol", submission_hash="carol-h", declared_epoch=4, publish_opt_in=True)
    stale_decision = evaluate_submission(store, stale, config)
    assert stale_decision.allowed is False
    assert "stale_epoch" in stale_decision.reasons
    assert stale_decision.published is False  # disallowed -> not published

    # the same submitter targeting the CURRENT epoch is not stale-blocked.
    current = Submission(submitter="carol", submission_hash="carol-h2", declared_epoch=5, publish_opt_in=False)
    current_decision = evaluate_submission(store, current, config)
    assert "stale_epoch" not in current_decision.reasons


# --------------------------------------------------------------------------------------
# 4. contamination / duplicate (NFR-014) — a re-used submission_hash is flagged
# --------------------------------------------------------------------------------------
def test_nfr_014_contamination_dup_check(tmp_path: pathlib.Path) -> None:
    """[UNIT-TEST] A ``submission_hash`` already present in a prior ``submitted`` event returns ``allowed
    is False`` with a ``"duplicate"`` (contamination) reason — a re-used content hash means a recycled /
    contaminated submission. A novel hash is not flagged."""
    store = _store(tmp_path)
    config = PolicyConfig(current_epoch=0, max_submissions_per_epoch=5)

    store.append(
        EventType.SUBMITTED,
        "dave-1",
        {"submitter": "dave", "submission_hash": "seen-hash", "declared_epoch": 0},
    )

    dup = Submission(submitter="dave", submission_hash="seen-hash", declared_epoch=0, publish_opt_in=True)
    dup_decision = evaluate_submission(store, dup, config)
    assert dup_decision.allowed is False
    assert "duplicate" in dup_decision.reasons
    assert dup_decision.published is False  # disallowed -> not published

    # a fresh hash by the same submitter is NOT a duplicate.
    fresh = Submission(submitter="dave", submission_hash="novel-hash", declared_epoch=0, publish_opt_in=False)
    fresh_decision = evaluate_submission(store, fresh, config)
    assert "duplicate" not in fresh_decision.reasons


# --------------------------------------------------------------------------------------
# 5. clean submission (FR-023) — fresh + in-epoch + under-limit + opt-in -> allowed & published
# --------------------------------------------------------------------------------------
def test_fr_023_clean_submission_allowed_and_published(tmp_path: pathlib.Path) -> None:
    """[UNIT-TEST] A fresh, in-epoch, under-limit submission with ``publish_opt_in=True`` returns
    ``allowed is True`` AND ``published is True`` with ``reasons == ()`` — the clean-path: none of the
    anti-gaming controls fires, and opt-in permits publication. Returns a real ``PolicyDecision``."""
    store = _store(tmp_path)
    config = PolicyConfig(current_epoch=7, max_submissions_per_epoch=5)

    # one unrelated prior submission by a different submitter (under the limit; different hash/epoch-ok).
    store.append(
        EventType.SUBMITTED,
        "erin-1",
        {"submitter": "erin", "submission_hash": "erin-h", "declared_epoch": 7},
    )

    clean = Submission(submitter="frank", submission_hash="frank-fresh", declared_epoch=7, publish_opt_in=True)
    decision = evaluate_submission(store, clean, config)
    assert isinstance(decision, PolicyDecision)
    assert decision.allowed is True
    assert decision.published is True
    assert decision.reasons == ()


# --------------------------------------------------------------------------------------
# 6. pure-stdlib (NFR-004 / AX-002) — AST guard bans {random, time, uuid, datetime, secrets}
# --------------------------------------------------------------------------------------
def test_nfr004_policy_pure_stdlib() -> None:
    """[PROPERTY-TEST] AST guard: ``policy.py`` imports none of {random, time, uuid, datetime, secrets}
    (no clock/RNG -> the decision is a pure function of store events + submission + config); the
    ``import pii_anon_datasets.leaderboard`` package import succeeds with the policy symbols present."""
    import importlib

    importlib.import_module("pii_anon_datasets.leaderboard")

    source_file = inspect.getsourcefile(policy_mod)
    assert source_file is not None  # policy_mod is a real on-disk module
    src = pathlib.Path(source_file).read_text(encoding="utf-8")
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
        f"policy.py imports nondeterministic modules (no clock/RNG allowed): {sorted(banned & imported)}"
    )
