"""CAP-02 — leaderboard hygiene + governance/anti-gaming (DC-29 / FR-051/052; NFR-048/049; AX-005 #6).

A published assessment run must carry a structured, non-strippable governance block
{corpus_owner, label_holder, evaluator}; reject any submitted system whose contamination_status is 'unknown';
require a well-formed held-out-non-exposure attestation {submitter_id, statement, signature, signed_at} that
VERIFIES under a configured key (HMAC-SHA256, stdlib); enforce a recusal record when an evaluator owns an
entry; and prove (via the scoring-API-surface oracle) that a scoring response never leaks the held-out label.
"""
from __future__ import annotations

import pytest
from pii_anon_datasets.assessment import governance as G


# ---- governance block (FR-052): structured + non-strippable ----
def test_governance_block_requires_all_identities() -> None:
    with pytest.raises(ValueError):
        G.GovernanceBlock(corpus_owner="", label_holder="L", evaluator="E")
    with pytest.raises(ValueError):
        G.GovernanceBlock(corpus_owner="C", label_holder="  ", evaluator="E")


def test_governance_block_as_dict_carries_disclaimer() -> None:
    gb = G.GovernanceBlock(corpus_owner="PII-Anon maintainers", label_holder="held-out custodian",
                           evaluator="neutral evaluator")
    d = gb.as_dict()
    assert d["corpus_owner"] and d["label_holder"] and d["evaluator"]
    assert d["disclaimer"].strip()  # non-strippable neutrality disclaimer


def test_disclaimer_cannot_be_emptied() -> None:
    with pytest.raises(ValueError):
        G.GovernanceBlock(corpus_owner="C", label_holder="L", evaluator="E", disclaimer="")


# ---- contamination control (FR-051/FR-043): 'unknown' rejected ----
def test_contamination_unknown_rejected() -> None:
    assert G.require_contamination_known("clean") == "clean"
    for bad in ("unknown", "UNKNOWN", " unknown ", ""):
        with pytest.raises(ValueError):
            G.require_contamination_known(bad)


# ---- held-out-non-exposure attestation (FR-051; AX-005 #6) ----
def test_attestation_requires_all_fields() -> None:
    with pytest.raises(ValueError):
        G.Attestation(submitter_id="s", statement="held out not exposed", signature="x", signed_at="")


def test_attestation_sign_verify_roundtrip_and_tamper() -> None:
    key = b"reference-key"
    sig = G.sign_attestation(submitter_id="s1", statement="labels not exposed", signed_at="2026-06-01T00:00:00Z",
                             key=key)
    att = G.Attestation(submitter_id="s1", statement="labels not exposed", signature=sig,
                        signed_at="2026-06-01T00:00:00Z")
    assert G.verify_attestation(att, key=key) is True
    tampered = G.Attestation(submitter_id="s1", statement="labels not exposed", signature=sig,
                             signed_at="2030-01-01T00:00:00Z")
    assert G.verify_attestation(tampered, key=key) is False
    # no key configured -> structural presence is the bar
    assert G.verify_attestation(att, key=None) is True


# ---- the leaderboard hygiene gate (FR-051/052) ----
def _gov():
    return G.GovernanceBlock(corpus_owner="C", label_holder="L", evaluator="neutral")


def test_gate_rejects_unknown_contamination() -> None:
    entries = [G.LeaderboardEntry(system="A", contamination_status="unknown")]
    with pytest.raises(ValueError):
        G.gate_leaderboard(governance=_gov(), entries=entries)


def test_gate_rejects_failed_attestation_signature() -> None:
    key = b"k"
    att = G.Attestation(submitter_id="A", statement="ok", signature="deadbeef", signed_at="t")
    entries = [G.LeaderboardEntry(system="A", contamination_status="clean", attestation=att)]
    with pytest.raises(ValueError):
        G.gate_leaderboard(governance=_gov(), entries=entries, key=key)


def test_gate_requires_recusal_when_evaluator_owns_entry() -> None:
    entries = [G.LeaderboardEntry(system="A", contamination_status="clean", owner_identities=("neutral",))]
    assert G.recusal_required("neutral", entries) is True
    with pytest.raises(ValueError):
        G.gate_leaderboard(governance=_gov(), entries=entries)          # evaluator 'neutral' owns A, no record
    block = G.gate_leaderboard(governance=_gov(), entries=entries, recusal_records={"neutral": "recused 2026-06-01"})
    assert block["recusal_records"]["neutral"]


def test_gate_returns_structured_block_for_every_page() -> None:
    key = b"k"
    sig = G.sign_attestation(submitter_id="A", statement="ok", signed_at="t", key=key)
    entries = [G.LeaderboardEntry(system="A", contamination_status="clean",
                                  attestation=G.Attestation(submitter_id="A", statement="ok", signature=sig, signed_at="t"))]
    block = G.gate_leaderboard(governance=_gov(), entries=entries, key=key)
    assert set(block) == {"governance", "contamination", "attestations", "recusal_records"}
    assert block["governance"]["evaluator"] == "neutral"
    assert block["contamination"]["A"] == "clean"


# ---- scoring-API-surface oracle (FR-051): held-out labels NEVER returned ----
def test_scoring_response_oracle_rejects_label_leak() -> None:
    assert G.scoring_response_is_clean({"predictions": [{"start": 0, "end": 4, "entity_type": "PER"}]}) is True
    assert G.scoring_response_is_clean({"predictions": [], "annotations": [{"start": 0}]}) is False
    assert G.scoring_response_is_clean({"gold_label": "PER"}) is False
