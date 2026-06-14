"""Tests for the pluggable LLM re-identification adversary (FR-010 secondary) — S3-03 §6.

Pins the **SECONDARY, version-stamped** adversary (design revision #1 / reidx-01): the
offline deterministic adversary (S3-02) is the headline; this LLM variant is
``deterministic=False`` and runs behind the optional ``[llm]`` extra (``anthropic``).

LOAD-BEARING (reidx-01 / NFR-009): ``anthropic`` is a LAZY import — the package, the
``scoring`` surface, and the :class:`LLMAdversary` class itself MUST import cleanly WITHOUT
``anthropic`` (no eager ``import anthropic`` at module load). Only *instantiating* the
adversary against the live API requires the extra; that path is exercised via an injectable
``client`` stub (class-shape tests) or skipped via ``pytest.importorskip`` (live path).

Traceability (per the S3-01/S3-02 convention — every test fn carries the canonical
``fr_010`` token so ``pytest -k fr_010`` selects them):
  * ``fr_010`` — adversary pluggability: the LLM variant satisfies the ``Adversary`` port
    with version-pinning ("vs adversary@version") and is the non-deterministic SECONDARY.

In THIS environment ``anthropic`` is intentionally absent, so:
  * tests 1-4 exercise the import-guard / class-shape / no-eager-import contract, and
  * test 5 (the live attack) SKIPS cleanly via ``pytest.importorskip("anthropic")`` —
    a skip is not a failure; it documents the live contract for envs that have the extra.
"""
import ast
import importlib
import pathlib
import sys

import pytest

# These imports MUST succeed with anthropic absent (lazy import — reidx-01 / NFR-009).
# If they raised, the whole module would error at collection, which is itself the failure
# signal that the eager-import contract is broken.
from pii_anon_datasets.scoring.adversary import llm_adversary as llm_mod
from pii_anon_datasets.scoring.adversary.base import Adversary, Guess, Persona, Target
from pii_anon_datasets.scoring.adversary.llm_adversary import (
    LLMAdversary,
    make_adversary_id,
)
from pii_anon_datasets.scoring.signals import extract

_LLM_MODULE_PATH = pathlib.Path(llm_mod.__file__)


# ─── tiny inline, deterministic fixtures — never a live API, never the full corpus ───


class _StubMessages:
    """A stub of ``anthropic.Anthropic().messages`` — abstains for every target.

    Lets the class-shape tests construct + exercise :class:`LLMAdversary` WITHOUT the
    ``[llm]`` extra and WITHOUT any network egress: the injected ``client`` short-circuits
    the lazy ``_require_anthropic()`` path entirely.
    """

    def __init__(self) -> None:
        self.calls = 0

    def create(self, *args: object, **kwargs: object) -> object:
        self.calls += 1

        class _Block:
            text = "ABSTAIN"

        class _Resp:
            content = [_Block()]

        return _Resp()


class _StubClient:
    """Minimal stand-in for ``anthropic.Anthropic()`` (only ``.messages`` is touched)."""

    def __init__(self) -> None:
        self.messages = _StubMessages()


def _persona(persona_id: str, gold_text: str) -> Persona:
    return Persona(
        persona_id=persona_id,
        record_id=persona_id,
        quasi_identifiers=(),
        behavioral_signals=extract(gold_text),
        source_text=gold_text,
    )


def _target(target_id: str, anonymized_text: str) -> Target:
    return Target(
        target_id=target_id,
        anonymized_text=anonymized_text,
        observed_signals=extract(anonymized_text),
    )


def _candidates() -> list[Persona]:
    return [
        _persona("p_boston", "On the T into Beacon Hill the attending discussed prognosis."),
        _persona("p_fitness", "Hit a new PR on my deload week; my macros are dialed."),
    ]


def _targets() -> list[Target]:
    return [
        _target("p_boston", "Commuting to the hospital, reviewed the clinical follow-up."),
        _target("p_fitness", "Logged another workout; the training block is going well."),
    ]


# ─────────────────────────────── Test 1 ────────────────────────────────────────────
# [CONTRACT-TEST] class shape importable WITHOUT anthropic; deterministic is False (secondary)


def test_fr_010_llm_adversary_class_shape_without_anthropic() -> None:
    """LLMAdversary is importable + structurally an Adversary, with deterministic=False.

    The class is inspected (and exercised via an injected stub ``client``) WITHOUT
    requiring ``anthropic`` — proving the SECONDARY adversary's shape is available offline.
    """
    # The class object exists and exposes the Adversary surface without instantiation.
    assert hasattr(LLMAdversary, "deterministic")
    assert hasattr(LLMAdversary, "attack")
    # The SECONDARY, non-deterministic figure (reidx-01): NOT the headline.
    assert LLMAdversary.deterministic is False

    # Construct via the injectable stub client — no anthropic, no network.
    adv = LLMAdversary(model="claude-x", client=_StubClient())
    assert hasattr(adv, "adversary_id")
    assert hasattr(adv, "deterministic")
    assert adv.deterministic is False
    # Structurally satisfies the runtime-checkable Adversary Protocol.
    assert isinstance(adv, Adversary)

    # attack(...) returns exactly len(targets) Guesses (one per target).
    targets, candidates = _targets(), _candidates()
    guesses = adv.attack(targets, candidates, candidate_set_size=len(candidates))
    assert isinstance(guesses, list)
    assert len(guesses) == len(targets)
    assert all(isinstance(g, Guess) for g in guesses)
    assert [g.target_id for g in guesses] == [t.target_id for t in targets]


# ─────────────────────────────── Test 2 ────────────────────────────────────────────
# [UNIT-TEST] constructing without anthropic AND without a client raises a clear [llm] error


def test_fr_010_llm_adversary_requires_extra_when_anthropic_absent() -> None:
    """Without ``anthropic`` and without an injected client, construction raises a clear error.

    Testable now precisely because ``anthropic`` is absent in this env: the lazy
    ``_require_anthropic()`` must raise a ``RuntimeError`` naming the ``[llm]`` extra.
    """
    assert "anthropic" not in sys.modules or sys.modules.get("anthropic") is None
    with pytest.raises(RuntimeError) as excinfo:
        LLMAdversary(model="claude-x")  # no client → must hit _require_anthropic()
    msg = str(excinfo.value)
    assert "pip install pii-anon-datasets[llm]" in msg
    assert "llm" in msg


# ─────────────────────────────── Test 3 ────────────────────────────────────────────
# [UNIT-TEST] adversary_id is version-stamped "llm:<model>@<date>" ("vs adversary@version")


def test_fr_010_llm_adversary_id_version_stamped() -> None:
    """``adversary_id`` is the version-stamped ``"llm:<model>@<date>"`` (FR-010).

    Built via ``make_adversary_id`` (no live API) and via a stub-client instance — so
    results read "vs adversary@version" and are comparable across runs.
    """
    assert make_adversary_id("claude-3-5-sonnet") == "llm:claude-3-5-sonnet@v1"
    assert make_adversary_id("m", date="2026-05-29") == "llm:m@2026-05-29"

    adv = LLMAdversary(model="claude-3-5-sonnet", date="2026-05-29", client=_StubClient())
    assert adv.adversary_id == "llm:claude-3-5-sonnet@2026-05-29"
    # Frozen per (model, date): same inputs → same id.
    again = LLMAdversary(model="claude-3-5-sonnet", date="2026-05-29", client=_StubClient())
    assert again.adversary_id == adv.adversary_id


# ─────────────────────────────── Test 4 ────────────────────────────────────────────
# [CONTRACT-TEST] package imports without anthropic — NO eager `import anthropic` at load


def test_fr_010_package_imports_without_anthropic() -> None:
    """``import pii_anon_datasets.scoring`` + ``from ... import LLMAdversary`` need no anthropic.

    Hard requirement (reidx-01 / NFR-009: offline is the default). Verified two ways:
      (a) the scoring surface imports and re-exports ``LLMAdversary`` with anthropic absent,
          and importing it does NOT pull ``anthropic`` into ``sys.modules`` (no eager import);
      (b) an AST scan of ``llm_adversary.py`` finds NO top-level ``import anthropic``
          (it may only appear inside a function body — the lazy guard).
    """
    # Precondition for this env: anthropic genuinely absent.
    assert importlib.util.find_spec("anthropic") is None

    # (a) Re-import the scoring package fresh and assert no eager anthropic import.
    for name in [m for m in sys.modules if m.startswith("pii_anon_datasets")]:
        del sys.modules[name]
    sys.modules.pop("anthropic", None)

    scoring = importlib.import_module("pii_anon_datasets.scoring")
    assert hasattr(scoring, "LLMAdversary")
    from pii_anon_datasets.scoring import LLMAdversary as ReexportedLLMAdversary

    assert ReexportedLLMAdversary is scoring.LLMAdversary
    # The whole point: loading the package must NOT have imported anthropic.
    assert "anthropic" not in sys.modules

    # (b) Static guarantee: no top-level `import anthropic` in the module source.
    tree = ast.parse(_LLM_MODULE_PATH.read_text(encoding="utf-8"))
    top_level_imports: list[str] = []
    for node in tree.body:  # tree.body == module top level only (lazy imports are nested)
        if isinstance(node, ast.Import):
            top_level_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top_level_imports.append(node.module)
    assert not any(
        name == "anthropic" or name.startswith("anthropic.") for name in top_level_imports
    ), f"eager top-level anthropic import found: {top_level_imports}"


# ─────────────────────────────── Test 5 ────────────────────────────────────────────
# [INTEGRATION-TEST] the LIVE attack path — skips cleanly when the [llm] extra is absent


def test_fr_010_llm_attack_skips_if_absent() -> None:
    """Live re-link contract — guarded by ``importorskip`` so it SKIPS without the extra.

    Documents the live behaviour for envs that have ``[llm]``: a default-constructed
    LLMAdversary (real ``anthropic.Anthropic`` client) returns exactly ``len(targets)``
    Guesses against the candidate pool. In THIS env (anthropic absent) it skips at the
    ``importorskip`` line before constructing anything — a skip, not a failure.
    """
    pytest.importorskip("anthropic")  # SKIPS here (anthropic intentionally absent)

    adv = LLMAdversary(model="claude-3-5-sonnet")  # real client, real network
    targets, candidates = _targets(), _candidates()
    guesses = adv.attack(targets, candidates, candidate_set_size=len(candidates))
    assert len(guesses) == len(targets)
    assert [g.target_id for g in guesses] == [t.target_id for t in targets]
    assert all(isinstance(g, Guess) for g in guesses)
