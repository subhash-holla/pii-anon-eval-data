"""Pluggable LLM re-identification adversary (FR-010 SECONDARY; DC-07; reidx-01).

The **non-deterministic, version-stamped SECONDARY** attacker (design revision #1 /
reidx-01): it satisfies the :class:`~.base.Adversary` port but sets
``deterministic = False`` so any :class:`~..reidentification.MeasuredRRS` it produces is
flagged non-deterministic. The **headline** RRS uses the offline deterministic adversary
(S3-02 — :class:`~.offline_adversary.OfflineDeterministicAdversary`); this LLM path is the
ONLY network egress in the scoring harness and is strictly opt-in.

reidx-01 / NFR-009 (LOAD-BEARING): ``anthropic`` is a **LAZY** import. This module — and
the whole ``pii_anon_datasets.scoring`` surface that re-exports :class:`LLMAdversary` —
MUST import cleanly with ``anthropic`` absent (offline is the default). ``anthropic`` is
imported ONLY inside :func:`_require_anthropic` (called from ``__init__`` when no ``client``
is injected, and reachable from :meth:`LLMAdversary.attack`), never at module top level.
Instantiating the adversary without the optional ``[llm]`` extra raises a clear
``RuntimeError`` pointing at ``pip install pii-anon-datasets[llm]``.

FR-010: ``adversary_id`` is version-stamped ``"llm:<model>@<date>"`` (via
:func:`make_adversary_id`) so results read "vs adversary@version" and stay comparable.

Testability: ``__init__`` accepts an injectable ``client`` so the class shape can be
exercised with a stub (no live API, no network); the live path is exercised under
``pytest.importorskip("anthropic")``.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .base import Guess, Persona, Target

# Version family of this adversary adapter (the per-run id additionally stamps model+date).
LLM_ADVERSARY_VERSION = "llm-adversary-v1"

# Sentinel the prompt instructs the model to emit when it cannot commit to a candidate.
_ABSTAIN_TOKEN = "ABSTAIN"


def _require_anthropic() -> Any:
    """Lazily import ``anthropic`` or raise a clear ``[llm]``-extra install error.

    Kept out of module scope on purpose (reidx-01 / NFR-009): importing this module must
    never pull in ``anthropic``. Called only when the LLM path is actually used (no
    ``client`` injected, or the live attack runs).
    """
    # The optional [llm] extra is absent in the offline default env — that absence is the
    # very condition this guard handles, so the unresolved import and the unused binding
    # are both suppressed on the import line below (reidx-01 / NFR-009).
    try:
        import anthropic  # type: ignore[import-not-found] # noqa: F401
    except ImportError as e:
        raise RuntimeError(
            "LLMAdversary needs the optional 'llm' extra: pip install pii-anon-datasets[llm]"
        ) from e
    return anthropic


def make_adversary_id(model: str, *, date: str = "v1") -> str:
    """Version-stamped adversary id ``"llm:<model>@<date>"`` ("vs adversary@version", FR-010).

    Frozen per ``(model, date)`` so two runs with the same model+date are comparable.
    """
    return f"llm:{model}@{date}"


def _build_prompt(
    target: Target, candidates: Sequence[Persona], candidate_set_size: int
) -> str:
    """Deterministic prompt string re-linking one ``target`` against the candidate pool.

    The candidate pool is presented in sorted ``persona_id`` order and truncated to the
    closed-world ``candidate_set_size`` (|C|) so the prompt is reproducible given fixed
    inputs (the *model's* answer is not — hence ``deterministic = False``). The model is
    asked to emit a single ``persona_id`` from the pool, or ``ABSTAIN``.
    """
    pool = sorted(candidates, key=lambda c: c.persona_id)[: max(0, candidate_set_size)]
    lines = [f"- {c.persona_id}: {c.source_text}" for c in pool]
    catalogue = "\n".join(lines)
    return (
        "You are a re-identification adversary. Given an anonymized text, identify which "
        "candidate persona it most likely belongs to.\n"
        f"Reply with EXACTLY one candidate id from the list, or '{_ABSTAIN_TOKEN}' if none "
        "is a confident match. Reply with the id and nothing else.\n\n"
        f"Anonymized text:\n{target.anonymized_text}\n\n"
        f"Candidates (|C|={len(pool)}):\n{catalogue}\n"
    )


def _extract_text(response: Any) -> str:
    """Pull the first text block out of an Anthropic ``messages.create`` response.

    Tolerant of the response shape used by both the live SDK (``response.content`` is a
    list of content blocks each carrying ``.text``) and a test stub of the same shape.
    Returns ``""`` if no text block is present (→ treated as an abstention upstream).
    """
    content = getattr(response, "content", None)
    if not content:
        return ""
    first = content[0]
    return str(getattr(first, "text", "") or "")


class LLMAdversary:
    """Consumer-named, version-pinned LLM re-identifier — the non-deterministic SECONDARY.

    Satisfies the :class:`~.base.Adversary` Protocol: a version-stamped :attr:`adversary_id`
    (``"llm:<model>@<date>"``), ``deterministic = False`` (the SECONDARY figure — reidx-01),
    and an :meth:`attack` that emits exactly one :class:`~.base.Guess` per target.

    Network egress / opt-in (security): the live path uses ``anthropic`` (the only network
    dependency in the scoring harness) and is NEVER wired into a default/headline path. A
    ``client`` may be injected so the class can be exercised with a stub (no live API).
    """

    deterministic = False  # the SECONDARY, non-deterministic figure (reidx-01)

    def __init__(
        self,
        model: str,
        *,
        date: str = "v1",
        temperature: float = 0.0,
        client: object | None = None,
    ) -> None:
        # Version-stamp the id BEFORE touching anthropic so identity is defined even if the
        # extra is missing (and so the error path below is the only thing that can fail).
        self.adversary_id = make_adversary_id(model, date=date)
        # Lazy: only resolve a live anthropic client when none is injected. With the extra
        # absent and no client, _require_anthropic() raises the clear [llm] install error.
        # Typed ``Any`` on purpose: the client is structurally duck-typed (a live
        # ``anthropic.Anthropic`` OR a test stub exposing ``.messages.create``).
        self._client: Any = client if client is not None else _require_anthropic().Anthropic()
        self._model = model
        self._temperature = temperature

    def attack(
        self,
        targets: Sequence[Target],
        candidates: Sequence[Persona],
        candidate_set_size: int,
    ) -> list[Guess]:
        """Re-link each pseudonymous ``Target`` against the real ``candidates`` pool via the LLM.

        For each target: prompt the model to pick a single ``persona_id`` from the (sorted,
        |C|-truncated) candidate pool or abstain; parse the reply to a :class:`~.base.Guess`.
        An unrecognized / ``ABSTAIN`` reply maps to ``guessed_persona_id=None`` (excluded
        from the precision denominator). Returns exactly ``len(targets)`` guesses, in target
        order, so the non-abstain count is integer-countable for the Wilson interval (S3-04).

        Non-deterministic (``deterministic = False``): the same inputs may yield different
        guesses across runs — which is why the offline adversary, not this one, is the headline.
        """
        pool = sorted(candidates, key=lambda c: c.persona_id)[: max(0, candidate_set_size)]
        valid_ids = {c.persona_id for c in pool}

        guesses: list[Guess] = []
        for target in targets:
            prompt = _build_prompt(target, pool, candidate_set_size)
            response = self._client.messages.create(
                model=self._model,
                max_tokens=64,
                temperature=self._temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            reply = _extract_text(response).strip()
            committed = reply if reply in valid_ids else None
            score = 1.0 if committed is not None else 0.0
            guesses.append(
                Guess(target_id=target.target_id, guessed_persona_id=committed, score=score)
            )
        return guesses
