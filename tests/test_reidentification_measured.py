"""Tests for the measured-attack RRS scorer (FR-007; supporting FR-009 / reidx-02) — S3-04 §6.

Pins the *headline* measured number (FR-007): run an :class:`Adversary` over assembled
``(targets, candidates, |C|)``, count correct re-links, and emit empirical re-identification
**recall and precision with Wilson CIs on integer counts**, wrapped as
``RRS = 1 − recall × precision`` inside the S1 :class:`RRSResult` so the non-strippable
anti-anonymity caveat (FR-009 / gov-01) travels with the number.

Traceability (LEARNED from the S3-01 / S3-02 story gates — every test fn carries a canonical
``fr_NNN`` token so ``pytest -k fr_007`` / ``-k fr_009`` selects them):
  * ``fr_007`` — empirical recall/precision, integer-guarded Wilson CIs, the exact
    ``1 − r×p`` identity, the ground-truth link, abstention handling, the |C| / adversary
    version-pinning, and the perfect/no-commit edges.
  * ``fr_009`` — the caveat is non-strippable through ``MeasuredRRS.as_dict()`` ([AUDIT]).

Test-data discipline (§6): a tiny inline ``_StubAdversary`` returns SCRIPTED guesses so
recall / precision are exactly known (independent of any real adversary's internals), plus
ONE end-to-end test wiring the real :class:`OfflineDeterministicAdversary`.
"""
from collections.abc import Sequence

import pytest
from pii_anon_datasets.scoring.adversary.base import Adversary, Guess, Persona, Target
from pii_anon_datasets.scoring.adversary.offline_adversary import OfflineDeterministicAdversary
from pii_anon_datasets.scoring.reidentification import MeasuredRRS, score_reidentification
from pii_anon_datasets.scoring.signals import extract

# ─── tiny inline stub adversary: scripted guesses → exactly-known recall/precision ───


class _StubAdversary:
    """A scripted :class:`Adversary` — returns a fixed ``guesses`` list verbatim.

    Lets each test fix ``correct`` / ``n_guesses`` exactly without depending on any real
    adversary's scoring internals (§6 test-data discipline). Conforms to the Protocol:
    exposes ``adversary_id`` + ``deterministic`` and an ``attack(...)`` that ignores its
    inputs and replays the scripted guesses.
    """

    def __init__(
        self,
        guesses: list[Guess],
        *,
        adversary_id: str = "stub-adversary-v0",
        deterministic: bool = True,
    ) -> None:
        self._guesses = guesses
        self.adversary_id = adversary_id
        self.deterministic = deterministic

    def attack(
        self,
        targets: Sequence[Target],
        candidates: Sequence[Persona],
        candidate_set_size: int,
    ) -> list[Guess]:
        return list(self._guesses)


def _targets(*ids: str) -> list[Target]:
    """Minimal targets; only ``target_id`` matters for the stub-driven scoring tests."""
    return [Target(target_id=tid, anonymized_text="", observed_signals=extract("")) for tid in ids]


def _guess(target_id: str, guessed: str | None, score: float = 0.9) -> Guess:
    return Guess(target_id=target_id, guessed_persona_id=guessed, score=score)


# ── 1. recall CI is built on the integer n_targets [UNIT-TEST] ──
def test_fr_007_recall_ci_uses_integer_n_targets():
    # 4 targets, 2 correctly re-linked → recall = 2/4; CI denominator is n_targets (int).
    targets = _targets("t1", "t2", "t3", "t4")
    guesses = [
        _guess("t1", "t1"),       # correct
        _guess("t2", "t2"),       # correct
        _guess("t3", "wrong"),    # committed but wrong
        _guess("t4", None),       # abstain
    ]
    m = score_reidentification(_StubAdversary(guesses), targets, [], candidate_set_size=10)
    assert m.reid_recall_ci.n == 4            # n_targets, an integer (idiom: test_detection.py)
    assert m.reid_recall_ci.method == "wilson"
    assert m.rrs.reid_recall == pytest.approx(0.5)
    assert m.reid_recall_ci.low < m.rrs.reid_recall < m.reid_recall_ci.high


# ── 2. precision CI is built on the integer n_guesses (non-abstain) [UNIT-TEST] ──
def test_fr_007_precision_ci_uses_integer_n_guesses():
    targets = _targets("t1", "t2", "t3", "t4")
    guesses = [
        _guess("t1", "t1"),       # committed + correct
        _guess("t2", "t2"),       # committed + correct
        _guess("t3", "wrong"),    # committed + wrong
        _guess("t4", None),       # abstain → NOT in n_guesses
    ]
    m = score_reidentification(_StubAdversary(guesses), targets, [], candidate_set_size=10)
    assert m.n_guesses == 3                   # 3 committed (one abstention excluded)
    assert m.reid_precision_ci.n == 3         # precision CI denominator == n_guesses
    assert m.reid_precision_ci.method == "wilson"
    assert m.rrs.reid_precision == pytest.approx(2 / 3)
    assert m.reid_precision_ci.low < m.rrs.reid_precision < m.reid_precision_ci.high


# ── 3. RRS = 1 − recall × precision exactly [UNIT-TEST] ──
def test_fr_007_rrs_equals_one_minus_recall_times_precision():
    targets = _targets("t1", "t2", "t3", "t4")
    guesses = [_guess("t1", "t1"), _guess("t2", "t2"), _guess("t3", "wrong"), _guess("t4", None)]
    m = score_reidentification(_StubAdversary(guesses), targets, [], candidate_set_size=10)
    # recall = 2/4 = 0.5, precision = 2/3 → RRS = 1 − 0.5 * (2/3)
    assert m.rrs.rrs == pytest.approx(1.0 - 0.5 * (2 / 3))
    assert m.rrs.rrs == pytest.approx(1.0 - m.rrs.reid_recall * m.rrs.reid_precision)


# ── 4. `correct` counts guesses whose guessed_persona_id == target_id (ground-truth link) [UNIT-TEST] ──
def test_fr_007_correct_is_guesses_matching_target_id():
    # assemble_paired_set set target_id == true persona_id; a correct re-link is exactly that.
    targets = _targets("t1", "t2", "t3")
    guesses = [
        _guess("t1", "t1"),       # matches target_id → correct
        _guess("t2", "t3"),       # guessed a different persona → NOT correct
        _guess("t3", "t3"),       # matches target_id → correct
    ]
    m = score_reidentification(_StubAdversary(guesses), targets, [], candidate_set_size=10)
    assert m.correct == 2
    assert m.n_targets == 3
    assert m.n_guesses == 3
    assert m.rrs.reid_recall == pytest.approx(2 / 3)


# ── 5. abstentions excluded from the precision denominator (not counted as wrong) [UNIT-TEST] ──
def test_fr_007_abstentions_excluded_from_precision_denominator():
    # 3 targets: 1 correct commit, 2 abstain. Precision = 1/1 (abstains drop out of denom),
    # NOT 1/3 — abstaining is not the same as guessing wrong.
    targets = _targets("t1", "t2", "t3")
    guesses = [_guess("t1", "t1"), _guess("t2", None), _guess("t3", None)]
    m = score_reidentification(_StubAdversary(guesses), targets, [], candidate_set_size=10)
    assert m.n_guesses == 1                   # only the single committed guess
    assert m.correct == 1
    assert m.rrs.reid_precision == pytest.approx(1.0)   # 1/1, abstains excluded
    assert m.rrs.reid_recall == pytest.approx(1 / 3)    # recall still over all 3 targets
    assert m.reid_precision_ci.n == 1


# ── 6. [AUDIT] FR-009 caveat is non-strippable through MeasuredRRS.as_dict() ──
def test_fr_009_caveat_nonstrippable_in_measured_as_dict():
    # MeasuredRRS.as_dict() MUST nest rrs.as_dict() so the anti-anonymity caveat is ALWAYS
    # serialized (gov-01) — idiom from tests/test_rrs_caveat.py.
    targets = _targets("t1", "t2")
    guesses = [_guess("t1", "t1"), _guess("t2", "t2")]
    m = score_reidentification(_StubAdversary(guesses), targets, [], candidate_set_size=10)
    assert isinstance(m, MeasuredRRS)                  # the scorer returns the FR-007 value object
    d = m.as_dict()
    assert "rrs" in d and isinstance(d["rrs"], dict)   # the nested RRSResult dict
    assert "caveat" in d["rrs"]                         # the caveat survives nesting
    assert "MUST NOT be cited" in d["rrs"]["caveat"]
    # and the CIs + counts also serialize (auditable n + named method)
    assert d["reid_recall_ci"]["method"] == "wilson"
    assert d["reid_precision_ci"]["method"] == "wilson"
    assert d["correct"] == 2 and d["n_targets"] == 2 and d["n_guesses"] == 2


# ── 7. reidx-02: a fractional count into the Wilson CI raises TypeError (integer guard) [UNIT-TEST] ──
def test_fr_007_reidx02_fractional_count_raises():
    from pii_anon_datasets.stats.intervals import wilson_interval

    # The integer guard the scorer relies on: partial/fractional counts must never feed a
    # binomial CI. The scorer only ever passes integers, but the guard is what makes that safe.
    with pytest.raises(TypeError):
        wilson_interval(1.5, 4)            # type: ignore[arg-type]
    with pytest.raises(TypeError):
        wilson_interval(2, 4.0)            # type: ignore[arg-type]


# ── 8. perfect attack → RRS=0; all-abstain → n_guesses=0, recall=0 → RRS=1 [UNIT-TEST] ──
def test_fr_007_perfect_attack_rrs_zero_and_no_commit_rrs_one():
    targets = _targets("t1", "t2", "t3")
    # Perfect re-link: every guess matches its target_id → recall = precision = 1 → RRS = 0.
    perfect = [_guess("t1", "t1"), _guess("t2", "t2"), _guess("t3", "t3")]
    mp = score_reidentification(_StubAdversary(perfect), targets, [], candidate_set_size=10)
    assert mp.correct == 3 and mp.n_guesses == 3
    assert mp.rrs.reid_recall == pytest.approx(1.0)
    assert mp.rrs.reid_precision == pytest.approx(1.0)
    assert mp.rrs.rrs == pytest.approx(0.0)

    # No-commit: every guess abstains → n_guesses == 0, recall == 0 → RRS == 1. The n=0
    # precision edge is handled gracefully (precision defined as 0.0, CI is the n=0 sentinel).
    none_committed = [_guess("t1", None), _guess("t2", None), _guess("t3", None)]
    mn = score_reidentification(_StubAdversary(none_committed), targets, [], candidate_set_size=10)
    assert mn.n_guesses == 0
    assert mn.correct == 0
    assert mn.rrs.reid_recall == pytest.approx(0.0)
    assert mn.rrs.reid_precision == pytest.approx(0.0)
    assert mn.rrs.rrs == pytest.approx(1.0)
    # n=0 Wilson sentinel: n recorded as 0, conservative [0,1] bounds, method still named.
    assert mn.reid_precision_ci.n == 0
    assert mn.reid_precision_ci.low == pytest.approx(0.0)
    assert mn.reid_precision_ci.high == pytest.approx(1.0)
    assert mn.reid_precision_ci.method == "wilson"


# ── 9. |C| recorded; adversary_id + deterministic propagate (version-pinning) [UNIT-TEST] ──
# Also the ONE end-to-end test wiring the real OfflineDeterministicAdversary (§6).
def test_fr_007_candidate_set_size_recorded():
    boston_med = (
        "On the T into Beacon Hill the attending discussed the differential diagnosis, "
        "the prognosis, and the comorbidity at follow-up. Presents with classic pathology."
    )
    fitness = (
        "Hit a new PR on my deload week; my macros and my split are dialed and my husband "
        "joined the WOD. When I was a kid I never thought I would love AMRAP cycles."
    )
    candidates = [
        Persona(
            persona_id="p-boston",
            record_id="p-boston",
            quasi_identifiers=(("LOCATION", "Beacon Hill"),),
            behavioral_signals=extract(boston_med),
            source_text=boston_med,
        ),
        Persona(
            persona_id="p-fitness",
            record_id="p-fitness",
            quasi_identifiers=(),
            behavioral_signals=extract(fitness),
            source_text=fitness,
        ),
    ]
    # target_id == true persona_id (the ground-truth link assemble_paired_set establishes).
    targets = [
        Target(target_id="p-boston", anonymized_text=boston_med, observed_signals=extract(boston_med)),
        Target(target_id="p-fitness", anonymized_text=fitness, observed_signals=extract(fitness)),
    ]
    adv = OfflineDeterministicAdversary()
    m = score_reidentification(adv, targets, candidates, candidate_set_size=2)

    assert m.candidate_set_size == 2
    assert m.adversary_id == adv.adversary_id == "offline-deterministic-v1"
    assert m.deterministic is True and m.rrs.deterministic is True
    assert m.rrs.adversary_id == "offline-deterministic-v1"
    # The distinctive signal profiles make both targets re-link to their true persona.
    assert m.n_targets == 2
    assert m.correct == 2
    assert m.rrs.reid_recall == pytest.approx(1.0)
    # MeasuredRRS conforms to the Adversary-consuming contract: the wrapped adversary is one,
    # and so is the scripted stub used throughout (structural typing — FR-010).
    assert isinstance(adv, Adversary)
    assert isinstance(_StubAdversary([]), Adversary)
