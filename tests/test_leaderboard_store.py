"""S6-01 — Append-only event-sourced held-out leaderboard store (DC-13; FR-023, NFR-014).

Tokened ``fr_023`` / ``nfr_014`` / ``nfr004`` so the traceability gate can map test->requirement
and ``pytest -k`` selects them. The store is an **append-only, content-hash-CHAINED** JSONL event log
(``submitted`` / ``scored`` / ``published``). It records **scores + config/version attestation +
provenance and NEVER the held-out GOLD** (FR-023: the gold stays undistributed). ``verify_chain()``
recomputes the chain and detects any mutation (NFR-014, tamper-evident). Pure-stdlib (``json`` +
``hashlib``); **no clock/RNG** -- ordering is a monotonic ``seq`` (AX-002), so re-appending the same
events to a fresh log yields byte-identical content hashes.

Load-bearing invariants the gate checks (security-sast is load-bearing):
  * append-only -- ONLY ``append`` writes (mode ``"a"``); no update/delete/__setitem__/mutate API.
  * no held-out gold (FR-023) -- ``append`` rejects ``{gold, gold_labels, held_out, held_out_labels,
    answers, ground_truth}`` -> ``ValueError``.
  * hash chain (NFR-014) -- ``events[i].prev_hash == events[i-1].content_hash()``; first event's
    ``prev_hash == GENESIS_HASH``; ``verify_chain()`` returns ``False`` on any line mutation.
  * deterministic (AX-002) -- seq-ordered, canonical-JSON hashing (sort_keys), no clock/RNG.
  * pure-stdlib (NFR-004) -- AST guard bans {random, time, uuid, datetime, secrets}.

Uses ``tmp_path`` for the JSONL log (no real FS outside the pytest tempdir; deterministic).
"""

from __future__ import annotations

import ast
import inspect
import json
import pathlib

import pytest
from pii_anon_datasets import leaderboard
from pii_anon_datasets.leaderboard import store as store_mod
from pii_anon_datasets.leaderboard.store import (
    GENESIS_HASH,
    EventType,
    LeaderboardStore,
)


# --------------------------------------------------------------------------------------
# 1. append-only — no update/delete/setitem; a second append grows the file, line 1 unchanged
# --------------------------------------------------------------------------------------
def test_fr_023_store_is_append_only(tmp_path):
    """[UNIT-TEST] ``LeaderboardStore`` exposes ``append`` / ``events`` / ``verify_chain`` but NO
    ``update`` / ``delete`` / ``__setitem__`` / mutate method (introspection); a second ``append``
    GROWS the file and leaves the first line's bytes unchanged."""
    log = tmp_path / "lb.jsonl"
    store = LeaderboardStore(log)

    # (A) the append-only surface exists ...
    for present in ("append", "events", "verify_chain"):
        assert callable(getattr(store, present)), f"missing append-only method '{present}'"
    # ... and the mutating surface does NOT (event-sourced: no in-place edit/remove)
    for forbidden in (
        "update",
        "delete",
        "remove",
        "pop",
        "set",
        "edit",
        "mutate",
        "replace",
        "__setitem__",
        "__delitem__",
    ):
        assert not hasattr(store, forbidden), f"store exposes a mutating method '{forbidden}'"
        assert not hasattr(LeaderboardStore, forbidden), f"class exposes a mutating method '{forbidden}'"

    # (B) a second append GROWS the file and leaves the first line's bytes byte-for-byte unchanged
    store.append(EventType.SUBMITTED, "sub-1", {"model": "alpha"})
    after_first = log.read_bytes()
    first_line_bytes = after_first.splitlines(keepends=True)[0]

    store.append(EventType.SCORED, "sub-1", {"scores": {"f1": 0.9}})
    after_second = log.read_bytes()

    assert len(after_second) > len(after_first), "second append did not grow the log"
    assert after_second.startswith(after_first), "append rewrote earlier bytes (not append-only)"
    assert after_second.splitlines(keepends=True)[0] == first_line_bytes, "first line's bytes mutated"
    assert len(store.events()) == 2


# --------------------------------------------------------------------------------------
# 2. no held-out gold — append rejects any forbidden payload key (FR-023)
# --------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "forbidden_key",
    ["gold", "gold_labels", "held_out", "held_out_labels", "answers", "ground_truth"],
)
def test_fr_023_store_rejects_held_out_gold(tmp_path, forbidden_key):
    """[CONTRACT-TEST] ``append(..., payload=...)`` with a payload containing any of
    ``{gold, gold_labels, held_out, held_out_labels, answers, ground_truth}`` raises ``ValueError``
    (the held-out gold can NEVER enter the store)."""
    store = LeaderboardStore(tmp_path / "lb.jsonl")
    with pytest.raises(ValueError):
        store.append(EventType.SCORED, "sub-1", {"scores": {"f1": 0.9}, forbidden_key: ["X", "Y"]})
    # the rejected append left NO trace — nothing was written
    assert store.events() == []
    assert not (tmp_path / "lb.jsonl").exists() or (tmp_path / "lb.jsonl").read_text() == ""


# --------------------------------------------------------------------------------------
# 3. hash chain — prev_hash links each event; seq monotonic; first == GENESIS (NFR-014)
# --------------------------------------------------------------------------------------
def test_nfr_014_hash_chain_links_events(tmp_path):
    """[PROPERTY-TEST] for N appended events, ``events[i].prev_hash == events[i-1].content_hash()``
    and ``events[0].prev_hash == GENESIS_HASH``; ``seq`` is 0..N-1 monotonic."""
    store = LeaderboardStore(tmp_path / "lb.jsonl")
    store.append(EventType.SUBMITTED, "sub-1", {"model": "alpha"})
    store.append(EventType.SCORED, "sub-1", {"scores": {"f1": 0.9}, "config_version": "v2"})
    store.append(EventType.PUBLISHED, "sub-1", {"slice": "overall"})

    events = store.events()
    assert len(events) == 3
    assert GENESIS_HASH == "0" * 64
    assert events[0].prev_hash == GENESIS_HASH
    for i, ev in enumerate(events):
        assert ev.seq == i, f"seq not monotonic at index {i}: {ev.seq}"
        if i > 0:
            assert ev.prev_hash == events[i - 1].content_hash(), f"broken chain link at index {i}"


# --------------------------------------------------------------------------------------
# 4. tamper detection — verify_chain True intact, False after one persisted line is mutated (NFR-014)
# --------------------------------------------------------------------------------------
def test_nfr_014_verify_chain_detects_tampering(tmp_path):
    """[PROPERTY-TEST] ``verify_chain()`` is ``True`` on an intact log; after rewriting one persisted
    JSONL line (mutating a payload value), a freshly-opened store's ``verify_chain()`` is ``False``."""
    log = tmp_path / "lb.jsonl"
    store = LeaderboardStore(log)
    store.append(EventType.SUBMITTED, "sub-1", {"model": "alpha"})
    store.append(EventType.SCORED, "sub-1", {"scores": {"f1": 0.9}})
    store.append(EventType.PUBLISHED, "sub-1", {"slice": "overall"})
    assert store.verify_chain() is True

    # tamper: rewrite the middle line, mutating a payload value (the score)
    lines = log.read_text(encoding="utf-8").splitlines()
    mid = json.loads(lines[1])
    mid["payload"]["scores"]["f1"] = 0.99  # the gaming attack the chain must catch
    lines[1] = json.dumps(mid, sort_keys=True, ensure_ascii=False)
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # a freshly-opened store over the tampered log fails verification
    assert LeaderboardStore(log).verify_chain() is False


# --------------------------------------------------------------------------------------
# 5. records scores not gold + deterministic — round-trip provenance; re-append → identical hashes
# --------------------------------------------------------------------------------------
def test_fr_023_store_records_scores_not_gold(tmp_path):
    """[PROPERTY-TEST] a ``scored`` event's payload carries ``scores`` + ``config_version``
    (provenance) and round-trips via ``events()``; the store contains no gold key -- and is
    deterministic (re-appending the same events to a fresh log -> identical content hashes; no
    clock/RNG)."""
    payload = {
        "scores": {"f1": 0.9, "precision": 0.88, "recall": 0.92},
        "config_version": "harness-v2.1",
        "attestation": {"affiliation": "neutral-lab", "model": "alpha"},
    }
    store_a = LeaderboardStore(tmp_path / "a.jsonl")
    ev_a = store_a.append(EventType.SCORED, "sub-1", payload)

    # provenance round-trips (scores + config_version recorded), and NO gold leaked
    (round_tripped,) = store_a.events()
    assert round_tripped.payload["scores"] == payload["scores"]
    assert round_tripped.payload["config_version"] == "harness-v2.1"
    serialized = (tmp_path / "a.jsonl").read_text(encoding="utf-8")
    for gold_key in ("gold", "gold_labels", "held_out", "held_out_labels", "answers", "ground_truth"):
        assert gold_key not in serialized, f"gold key '{gold_key}' leaked into the store"

    # deterministic: re-append the SAME event to a FRESH log -> byte-identical content hash (no clock/RNG)
    store_b = LeaderboardStore(tmp_path / "b.jsonl")
    ev_b = store_b.append(EventType.SCORED, "sub-1", payload)
    assert ev_a.content_hash() == ev_b.content_hash(), "non-deterministic hash (clock/RNG leaked in?)"
    assert ev_a.prev_hash == ev_b.prev_hash == GENESIS_HASH


# --------------------------------------------------------------------------------------
# 6. pure-stdlib — AST guard bans {random, time, uuid, datetime, secrets} (NFR-004 / AX-002)
# --------------------------------------------------------------------------------------
def test_nfr004_leaderboard_store_pure_stdlib():
    """[PROPERTY-TEST] AST guard: ``store.py`` imports none of {random, time, uuid, datetime, secrets}
    (only ``json`` + ``hashlib`` + stdlib); ``import pii_anon_datasets.leaderboard`` succeeds."""
    # the package import itself must succeed (no nondeterministic side-effect import)
    import importlib

    importlib.import_module("pii_anon_datasets.leaderboard")

    src = pathlib.Path(inspect.getsourcefile(store_mod)).read_text(encoding="utf-8")
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
        f"store.py imports nondeterministic modules (no clock/RNG allowed): {sorted(banned & imported)}"
    )
    # positively: json + hashlib are the persistence + chaining primitives
    assert {"json", "hashlib"} <= imported, "store.py must use json + hashlib"


# --------------------------------------------------------------------------------------
# 7. CLI verb — leaderboard.main(["verify", log]) -> 0 intact / non-zero tampered (wires S5-05)
# --------------------------------------------------------------------------------------
def test_fr_023_leaderboard_cli_verify(tmp_path):
    """[CONTRACT-TEST] ``leaderboard.main(["verify", str(log)])`` returns ``0`` on an intact log and
    a non-zero code on a tampered log (wires the S5-05 ``pii-anon leaderboard`` CLI verb)."""
    log = tmp_path / "lb.jsonl"
    store = LeaderboardStore(log)
    store.append(EventType.SUBMITTED, "sub-1", {"model": "alpha"})
    store.append(EventType.SCORED, "sub-1", {"scores": {"f1": 0.9}})

    # intact -> 0
    assert leaderboard.main(["verify", str(log)]) == 0

    # tamper one line -> non-zero
    lines = log.read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[0])
    rec["payload"]["model"] = "beta"
    lines[0] = json.dumps(rec, sort_keys=True, ensure_ascii=False)
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert leaderboard.main(["verify", str(log)]) != 0
