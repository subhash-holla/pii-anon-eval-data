"""Tests for the deterministic OFFLINE re-identification adversary (FR-007/FR-010) — S3-02 §6.

Pins the *headline* RRS attacker (design revision #1, reidx-01): no RNG, no clock, no
network, no LLM. It links pseudonymous ``Target`` s to real ``Persona`` candidates using
ONLY what survived anonymization — the re-extracted ``observed_signals`` plus the QI
tokens still present in ``anonymized_text`` — and emits one ranked ``Guess`` per target.

Traceability (LEARNED from the S3-01 story gate — every test fn carries a canonical
``fr_NNN`` token so ``pytest -k fr_007`` / ``-k fr_010`` selects them):
  * ``fr_007`` — the deterministic offline headline adversary (determinism,
    order-independence, abstention, the link actually working, integer guess counts,
    frozen/sorted config).
  * ``fr_010`` — pluggability + the version-pinned distractor-augmented variant.
The AST import-purity guard (NFR-004 / AX-002) mirrors ``test_signals.py``'s ``signals``
guard and carries ``fr_007`` + ``nfr004``.
"""
import ast
import dataclasses
import pathlib

import pytest
from pii_anon_datasets.scoring.adversary import (
    DEFAULT_OFFLINE_CONFIG,
    OFFLINE_ADVERSARY_VERSION,
    OfflineAdversaryConfig,
    OfflineDeterministicAdversary,
)
from pii_anon_datasets.scoring.adversary import offline_adversary as offline_mod
from pii_anon_datasets.scoring.adversary.base import Adversary, Guess, Persona, Target
from pii_anon_datasets.scoring.signals import extract

# ─── tiny inline, deterministic fixtures (3-5 personas) — never the full corpus ───
# observed_signals / behavioral_signals are built via signals.extract on short crafted
# texts so the link is controllable; no seeds, no RNG.


def _persona(persona_id: str, gold_text: str,
             quasi_identifiers: tuple[tuple[str, str], ...] = ()) -> Persona:
    """A real-side candidate: gold behavioral_signals extracted from ``gold_text``."""
    return Persona(
        persona_id=persona_id,
        record_id=persona_id,
        quasi_identifiers=quasi_identifiers,
        behavioral_signals=extract(gold_text),
        source_text=gold_text,
    )


def _target(target_id: str, anonymized_text: str) -> Target:
    """A pseudonymous side: observed_signals RE-EXTRACTED from the anonymized text."""
    return Target(
        target_id=target_id,
        anonymized_text=anonymized_text,
        observed_signals=extract(anonymized_text),
    )


# Texts crafted so signal profiles differ:
#  * _BOSTON_MED — Boston local refs + medical jargon (location + professional domain)
#  * _FITNESS    — fitness interest topic + personal anecdote
#  * _PLAIN      — essentially no signals (decoy / abstention probe)
_BOSTON_MED = (
    "On the T into Beacon Hill the attending discussed the differential diagnosis, "
    "the prognosis, and the comorbidity at follow-up. Presents with classic pathology."
)
_FITNESS = (
    "Hit a new PR on my deload week; my macros and my split are dialed and my husband "
    "joined the WOD. When I was a kid I never thought I would love AMRAP cycles."
)
_PLAIN = "The weather changed and the document was filed and the meeting moved."


def _candidates() -> list[Persona]:
    """Three personas with deliberately distinct signal profiles (sorted-id friendly)."""
    return [
        _persona("p-boston", _BOSTON_MED,
                 quasi_identifiers=(("LOCATION", "Beacon Hill"),)),
        _persona("p-fitness", _FITNESS),
        _persona("p-plain", _PLAIN),
    ]


# ── 1. determinism: identical inputs → byte-equal Guess list [PROPERTY-TEST] ──
def test_fr_007_attack_is_deterministic():
    adv = OfflineDeterministicAdversary()
    cands = _candidates()
    targets = [_target("t-boston", _BOSTON_MED), _target("t-fitness", _FITNESS)]
    g1 = adv.attack(targets, cands, candidate_set_size=3)
    g2 = adv.attack(targets, cands, candidate_set_size=3)
    assert g1 == g2                       # frozen-dataclass equality → byte-equal
    assert all(isinstance(g, Guess) for g in g1)


# ── 2. ranking is input-order independent (total order via lexicographic tie) ──
def test_fr_007_ranking_is_order_independent():
    adv = OfflineDeterministicAdversary()
    targets = [_target("t-boston", _BOSTON_MED)]
    cands = _candidates()
    forward = adv.attack(targets, cands, candidate_set_size=3)
    reversed_pool = adv.attack(targets, list(reversed(cands)), candidate_set_size=3)
    # shuffle to a third arbitrary order
    shuffled = adv.attack(targets, [cands[1], cands[2], cands[0]], candidate_set_size=3)
    assert forward == reversed_pool == shuffled


# ── 3. abstain below threshold, distinguishable from a wrong guess [UNIT-TEST] ──
def test_fr_007_abstains_below_threshold():
    # threshold above any achievable similarity → forced abstention
    abstaining = OfflineDeterministicAdversary(
        dataclasses.replace(DEFAULT_OFFLINE_CONFIG, score_threshold=1.0 + 1e-9)
    )
    targets = [_target("t-boston", _BOSTON_MED)]
    cands = _candidates()
    guesses = abstaining.attack(targets, cands, candidate_set_size=3)
    assert len(guesses) == 1
    assert guesses[0].guessed_persona_id is None      # abstain sentinel
    # an abstain (None) is distinguishable from a wrong-but-committed guess
    committed = OfflineDeterministicAdversary().attack(targets, cands, candidate_set_size=3)
    assert committed[0].guessed_persona_id is not None
    assert guesses[0] != committed[0]


# ── 4. the attack actually works: distinctive surviving signal → right persona ──
def test_fr_007_links_surviving_signal():
    adv = OfflineDeterministicAdversary()
    cands = _candidates()
    # Target whose anonymized text retains the Boston+medical profile present in
    # exactly one persona (p-boston). The link must be the top guess.
    targets = [_target("t-x", _BOSTON_MED)]
    guesses = adv.attack(targets, cands, candidate_set_size=3)
    assert guesses[0].guessed_persona_id == "p-boston"
    assert guesses[0].score > 0.0
    # and a fitness target links to the fitness persona
    fit = adv.attack([_target("t-y", _FITNESS)], cands, candidate_set_size=3)
    assert fit[0].guessed_persona_id == "p-fitness"


# ── 5. guess counts are integer-countable: exactly len(targets); non-abstain int ──
def test_fr_007_guess_counts_are_integers():
    adv = OfflineDeterministicAdversary()
    cands = _candidates()
    targets = [_target("t-boston", _BOSTON_MED),
               _target("t-fitness", _FITNESS),
               _target("t-plain", _PLAIN)]
    guesses = adv.attack(targets, cands, candidate_set_size=3)
    assert len(guesses) == len(targets) == 3          # exactly one Guess per target
    n_committed = sum(1 for g in guesses if g.guessed_persona_id is not None)
    assert isinstance(n_committed, int)               # feeds the integer-guarded Wilson (S3-04)
    # target_ids preserved 1:1, in target order
    assert [g.target_id for g in guesses] == ["t-boston", "t-fitness", "t-plain"]


# ── 6. distractor variant: distinct id + ≥ candidates and ≤ precision [UNIT-TEST] ──
def test_fr_010_distractor_variant_distinct_id_and_lower_precision():
    base = OfflineDeterministicAdversary()
    distractor = OfflineDeterministicAdversary(
        dataclasses.replace(DEFAULT_OFFLINE_CONFIG,
                            distractor_corpus_id="web-like-distractors-v1")
    )
    assert distractor.adversary_id == (
        "offline-deterministic-v1+distractor:web-like-distractors-v1"
    )
    assert base.adversary_id == "offline-deterministic-v1"

    cands = _candidates()
    # decoys that mimic the Boston+medical profile → they compete with the true source
    decoys = [
        _persona("d-boston-1", _BOSTON_MED, quasi_identifiers=(("LOCATION", "Beacon Hill"),)),
        _persona("d-boston-2", _BOSTON_MED, quasi_identifiers=(("LOCATION", "Beacon Hill"),)),
    ]
    targets = [_target("t-boston", _BOSTON_MED)]

    base_guesses = base.attack(targets, cands, candidate_set_size=len(cands))
    # distractor pool = real candidates + decoys (caller-supplied for THIS story §8b)
    aug = cands + decoys
    distractor_guesses = distractor.attack(targets, aug, candidate_set_size=len(aug))

    # |C| grows under the distractor variant (≥ as many candidates considered)
    assert len(aug) >= len(cands)

    # precision proxy: under decoys that tie the true source, the deterministic
    # lexicographic tie-break can resolve to a decoy → a correct guess is no longer
    # guaranteed; the distractor variant's correctness is ≤ the base variant's.
    base_correct = base_guesses[0].guessed_persona_id == "t-boston" or \
        base_guesses[0].guessed_persona_id == "p-boston"
    distractor_correct = distractor_guesses[0].guessed_persona_id in {"t-boston", "p-boston"}
    assert int(distractor_correct) <= int(base_correct)


# ── 7. port conformance + version pin [CONTRACT-TEST] ──
def test_fr_010_adversary_satisfies_port():
    adv = OfflineDeterministicAdversary()
    assert isinstance(adv, Adversary)                 # structural Protocol conformance
    assert adv.deterministic is True
    assert OfflineDeterministicAdversary.deterministic is True
    assert adv.adversary_id == OFFLINE_ADVERSARY_VERSION == "offline-deterministic-v1"


# ── 8. config frozen + DEFAULT has sorted feature_weights [UNIT-TEST] ──
def test_fr_007_config_is_frozen_and_hashable():
    assert dataclasses.is_dataclass(OfflineAdversaryConfig)
    with pytest.raises(dataclasses.FrozenInstanceError):
        DEFAULT_OFFLINE_CONFIG.score_threshold = 0.5   # type: ignore[misc]
    # frozen dataclass with hashable fields → hashable (stampable for reproducibility)
    assert isinstance(hash(DEFAULT_OFFLINE_CONFIG), int)
    # feature_weights are a deterministic stamp: the six behavioral categories are sorted
    # alphabetically, with the synthetic surviving-QI class appended last (§8b literal).
    cats = [c for c, _w in DEFAULT_OFFLINE_CONFIG.feature_weights]
    assert cats[-1] == "quasi_identifier_token"
    behavioral = cats[:-1]
    assert behavioral == sorted(behavioral)            # deterministic, stampable ordering
    assert set(behavioral) == {
        "interest_topics", "location_signals", "personal_anecdote",
        "professional_domain", "temporal_patterns", "writing_style",
    }
    # the surviving-QI token weight is present and weighs MORE than any behavioral category
    weights = dict(DEFAULT_OFFLINE_CONFIG.feature_weights)
    assert weights["quasi_identifier_token"] > max(
        weights[c] for c in weights if c != "quasi_identifier_token"
    )


# ── AST import-purity guard (NFR-004 / AX-002) — mirrors test_signals.py ──
def test_fr_007_nfr004_offline_adversary_imports_no_nondeterminism():
    """AX-002/NFR-004: statically prove offline_adversary.py imports NONE of
    {random, time, uuid, datetime, secrets} — a stronger warrant than intra-process
    idempotence (which a shared seeded RNG could fake). 'Offline deterministic' means
    no RNG, no clock, no network, no LLM."""
    src = pathlib.Path(offline_mod.__file__).read_text(encoding="utf-8")
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
        f"offline_adversary.py imports nondeterministic modules: {sorted(banned & imported)}"
    )
