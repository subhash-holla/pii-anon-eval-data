"""Tests for the anonymization scorer (DC-06; FR-006, supporting NFR-005/AX-004 + FR-009) — S3-06 §6.

Pins the *Pareto* guarantee (FR-006): given a system's anonymized text + assembled adversary
inputs, :func:`score_anonymization` emits a :class:`ParetoPoint` whose two axes —
residual re-identification risk (a :class:`MeasuredRRS`, reusing the S3-04 measured-attack
machinery — the privacy axis, carrying the non-strippable FR-009 caveat) and downstream
utility (a pinned deterministic ``token-preservation-v1`` probe — the utility axis) — are
**two separate nested value objects that NO code path can fuse into one scalar**.

THE headline guard (NFR-005 / AX-004): ``ParetoPoint`` is structurally unmergeable — the two
axes are nested objects of *different types* (``MeasuredRRS`` vs ``UtilityScore``); there is no
``combined``/``overall``/``overall_score``/``deid``/``de_identification_score``/``score``
attribute or property, and no ``__float__``. ``test_nfr005_pareto_point_cannot_merge`` asserts
this both by introspection AND by a source grep ([AUDIT]).

Traceability (LEARNED from S3-01/02/04 — every test fn carries a canonical token so
``pytest -k fr_006`` / ``-k nfr005`` / ``-k nfr004`` selects them):
  * ``fr_006`` — deterministic versioned utility probe; perfect-vs-masked utility; the two
    separate Pareto axes; the residual-risk axis is a ``MeasuredRRS``; the variant label.
  * ``nfr005`` — the structural no-merge guard ([AUDIT]).
  * ``nfr004`` — import purity ([PROPERTY-TEST]).

Test-data discipline (§6): inline original/anonymized text pairs + a tiny assembled
targets/candidates set + a scripted stub Adversary (and the real
:class:`OfflineDeterministicAdversary` end-to-end). Deterministic.
"""
import ast
import pathlib
from collections.abc import Sequence

import pytest
from pii_anon_datasets.scoring import anonymization as anon_mod
from pii_anon_datasets.scoring.adversary.base import Guess, Persona, Target
from pii_anon_datasets.scoring.adversary.offline_adversary import OfflineDeterministicAdversary
from pii_anon_datasets.scoring.anonymization import (
    UTILITY_PROBE_VERSION,
    ParetoPoint,
    UtilityScore,
    score_anonymization,
    score_utility,
)
from pii_anon_datasets.scoring.reidentification import MeasuredRRS
from pii_anon_datasets.scoring.signals import extract

# ─── tiny inline stub adversary: scripted guesses → exactly-known residual risk ───


class _StubAdversary:
    """A scripted :class:`Adversary` — returns a fixed ``guesses`` list verbatim.

    Lets a test fix the residual-risk axis exactly without depending on a real adversary's
    internals (§6 test-data discipline). Conforms to the Protocol via structural typing.
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
    return [Target(target_id=tid, anonymized_text="", observed_signals=extract("")) for tid in ids]


def _guess(target_id: str, guessed: str | None, score: float = 0.9) -> Guess:
    return Guess(target_id=target_id, guessed_persona_id=guessed, score=score)


# An original document and a couple of anonymized variants used across the FR-006 utility tests.
_ORIGINAL = (
    "Jane Doe lives at 42 Beacon Street in Boston and her account number is 1234. "
    "She called the clinic about her prognosis on Tuesday."
)
_REDACTED = (
    "[NAME] lives at [ADDRESS] in [CITY] and her account number is [ACCT]. "
    "She called the clinic about her prognosis on [DAY]."
)
_FULL_MASK = "[REDACTED] [REDACTED] [REDACTED] [REDACTED]"


# ── 1. utility probe deterministic + versioned, in [0,1] [UNIT-TEST] ──
def test_fr_006_utility_probe_deterministic_and_versioned():
    a = score_utility(_ORIGINAL, _REDACTED)
    b = score_utility(_ORIGINAL, _REDACTED)
    assert isinstance(a, UtilityScore)
    assert a == b                                   # deterministic: same inputs → same object
    assert a.probe == "token-preservation-v1" == UTILITY_PROBE_VERSION
    assert 0.0 <= a.utility <= 1.0
    # components are transparent named sub-scores (a tuple of (name, value) pairs)
    assert isinstance(a.components, tuple) and len(a.components) >= 1
    assert all(isinstance(n, str) and 0.0 <= v <= 1.0 for n, v in a.components)


# ── 2. perfect preservation ≈ 1.0; full-mask (structure lost) → low utility [UNIT-TEST] ──
def test_fr_006_utility_perfect_preservation_and_full_mask():
    perfect = score_utility(_ORIGINAL, _ORIGINAL)      # identical → all non-PII tokens preserved
    masked = score_utility(_ORIGINAL, _FULL_MASK)      # structure obliterated → little preserved
    assert perfect.utility == pytest.approx(1.0)
    assert masked.utility < perfect.utility
    assert masked.utility < 0.5                         # heavy loss when nearly everything is masked


# ── 3. ParetoPoint exposes exactly two SEPARATE typed axes (+ variant + note) [UNIT-TEST] ──
def test_fr_006_pareto_point_has_two_separate_axes():
    targets = _targets("t1", "t2")
    point = score_anonymization(
        _StubAdversary([_guess("t1", "t1"), _guess("t2", "t2")]),
        targets,
        [],
        candidate_set_size=10,
        original_text=_ORIGINAL,
        anonymized_text=_REDACTED,
        variant="anonymized_redacted",
    )
    assert isinstance(point, ParetoPoint)
    # the two axes are nested objects of DIFFERENT types
    assert isinstance(point.residual_risk, MeasuredRRS)
    assert isinstance(point.utility, UtilityScore)
    assert type(point.residual_risk) is not type(point.utility)
    d = point.as_dict()
    # exactly: a privacy sub-object, a utility sub-object, plus variant + note
    assert set(d.keys()) == {"privacy", "utility", "variant", "note"}
    assert isinstance(d["privacy"], dict) and isinstance(d["utility"], dict)
    # the two sub-objects are distinct dicts, not one fused scalar
    assert d["privacy"] is not d["utility"]
    assert "rrs" in d["privacy"]               # the MeasuredRRS serialization (privacy axis)
    assert "utility" in d["utility"] and d["utility"]["probe"] == "token-preservation-v1"


# ── 4. [AUDIT] THE headline guard: ParetoPoint structurally cannot merge (NFR-005 / AX-004) ──
def test_nfr005_pareto_point_cannot_merge():
    targets = _targets("t1")
    point = score_anonymization(
        _StubAdversary([_guess("t1", "t1")]),
        targets,
        [],
        candidate_set_size=10,
        original_text=_ORIGINAL,
        anonymized_text=_REDACTED,
        variant="anonymized_redacted",
    )
    forbidden = {
        "combined", "overall", "overall_score", "deid",
        "de_identification_score", "deidentification_score", "score",
    }
    # (A) introspection: no forbidden attribute/property on the instance or class
    for name in forbidden:
        assert not hasattr(point, name), f"ParetoPoint must not expose a merged metric '{name}'"
        assert not hasattr(ParetoPoint, name), f"ParetoPoint class must not define '{name}'"
    # no __float__ → a Pareto point cannot collapse to a single number
    assert not hasattr(point, "__float__")
    with pytest.raises(TypeError):
        float(point)  # type: ignore[arg-type]
    # (B) as_dict() yields no single scalar fusing privacy+utility — privacy & utility are dicts
    d = point.as_dict()
    assert isinstance(d["privacy"], dict) and isinstance(d["utility"], dict)
    assert forbidden.isdisjoint(d.keys())
    # (C) source grep: anonymization.py defines none of the forbidden names as a merged metric
    src = pathlib.Path(anon_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    defined: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined.add(node.name)                          # def / property names
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            defined.add(node.target.id)                     # annotated dataclass fields
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    defined.add(tgt.id)                     # plain assignments
    leaked = forbidden & defined
    assert not leaked, f"anonymization.py defines forbidden merged-metric name(s): {sorted(leaked)}"
    # (D) the separation note is a constructed invariant — an empty note is rejected (§8b),
    # so a ParetoPoint can never be built without the "NEVER combined" disclaimer.
    with pytest.raises(ValueError):
        ParetoPoint(residual_risk=point.residual_risk, utility=point.utility, variant="v", note="   ")


# ── 5. [AUDIT] residual-risk axis is a MeasuredRRS; its FR-009 caveat survives as_dict() ──
def test_fr_006_residual_risk_axis_is_measured_rrs():
    # The privacy axis is produced by running the adversary (reuses S3-04 score_reidentification),
    # and the nested anti-anonymity caveat (FR-009) is non-strippable through ParetoPoint.as_dict().
    boston = (
        "On the T into Beacon Hill the attending discussed the differential diagnosis, "
        "the prognosis and the comorbidity at follow-up. Presents with classic pathology."
    )
    candidates = [
        Persona(
            persona_id="p-boston",
            record_id="p-boston",
            quasi_identifiers=(("LOCATION", "Beacon Hill"),),
            behavioral_signals=extract(boston),
            source_text=boston,
        ),
    ]
    targets = [Target(target_id="p-boston", anonymized_text=boston, observed_signals=extract(boston))]
    point = score_anonymization(
        OfflineDeterministicAdversary(),
        targets,
        candidates,
        candidate_set_size=1,
        original_text=boston,
        anonymized_text="[REDACTED] discussed the [REDACTED] at follow-up.",
        variant="anonymized_redacted",
    )
    assert isinstance(point.residual_risk, MeasuredRRS)
    assert point.residual_risk.adversary_id == "offline-deterministic-v1"
    d = point.as_dict()
    # the caveat is nested under privacy → rrs → caveat and is NON-strippable (FR-009)
    assert "caveat" in d["privacy"]["rrs"]
    assert "MUST NOT be cited" in d["privacy"]["rrs"]["caveat"]


# ── 6. the scored anonymized_* variant label is recorded on the ParetoPoint [UNIT-TEST] ──
def test_fr_006_variant_recorded():
    targets = _targets("t1")
    point = score_anonymization(
        _StubAdversary([_guess("t1", "t1")]),
        targets,
        [],
        candidate_set_size=5,
        original_text=_ORIGINAL,
        anonymized_text=_REDACTED,
        variant="anonymized_pseudonymized",
    )
    assert point.variant == "anonymized_pseudonymized"
    assert point.as_dict()["variant"] == "anonymized_pseudonymized"
    # the separation note is present and non-empty (constructed-invariant — see test below)
    assert point.note.strip()
    assert "NEVER" in point.note and "single de-identification score" in point.note


# ── 7. [PROPERTY-TEST] NFR-004 import purity: no nondeterminism imports ──
def test_fr_006_nfr004_anonymization_imports_no_nondeterminism():
    """AST guard: anonymization.py imports NONE of {random, time, uuid, datetime, secrets}."""
    src = pathlib.Path(anon_mod.__file__).read_text(encoding="utf-8")
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
        f"anonymization.py imports nondeterministic modules: {sorted(banned & imported)}"
    )


# ── 8. utility_metrics fold-in: optional secondary components + edge coercions [UNIT-TEST] ──
def test_fr_006_utility_metrics_fold_in_components():
    """When ``utility_metrics`` is supplied, the optional ``information_retained`` and
    ``coherence`` components fold in; a bool/non-numeric ratio coerces to 0.0 (``_as_ratio``);
    two empty texts are vacuously fully-preserved (1.0). Covers the optional enrichment branches
    so the utility probe's full surface — not just the bare Jaccard — is exercised."""
    s = score_utility(
        _ORIGINAL, _REDACTED,
        utility_metrics={"information_loss_ratio": 0.25, "coherence": True},
    )
    comp = dict(s.components)
    assert {"token_preservation_jaccard", "information_retained", "coherence"} <= comp.keys()
    assert comp["information_retained"] == pytest.approx(0.75)   # 1 - 0.25
    assert comp["coherence"] == 1.0
    assert 0.0 <= s.utility <= 1.0
    # a bool/non-numeric information_loss_ratio is REJECTED by _as_ratio → 0.0 → retained 1.0
    s2 = score_utility(
        _ORIGINAL, _REDACTED,
        utility_metrics={"information_loss_ratio": True, "coherence": False},
    )
    comp2 = dict(s2.components)
    assert comp2["information_retained"] == 1.0                  # _as_ratio(True) == 0.0
    assert comp2["coherence"] == 0.0
    # an out-of-range ratio is clamped into [0,1] (defensive), keeping utility valid
    s3 = score_utility(_ORIGINAL, _REDACTED, utility_metrics={"information_loss_ratio": 9.0})
    assert dict(s3.components)["information_retained"] == 0.0    # 1 - clamp(9.0)→1.0
    # two empty texts → preservation is vacuously 1.0 (no utility was lost)
    assert score_utility("", "").utility == pytest.approx(1.0)


# ── 9. UtilityScore enforces its [0,1] invariant at construction [UNIT-TEST] ──
def test_fr_006_utility_score_rejects_out_of_range():
    """``UtilityScore.__post_init__`` rejects a utility outside [0,1] — the invariant the
    weighted-mean clamp upholds can never be bypassed by direct construction."""
    with pytest.raises(ValueError):
        UtilityScore(utility=1.5, components=(("x", 1.5),))
    with pytest.raises(ValueError):
        UtilityScore(utility=-0.1, components=())
