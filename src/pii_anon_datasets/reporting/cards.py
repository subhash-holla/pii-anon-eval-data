"""Mechanically regenerate the marker-delimited leaderboard blocks in the public cards (BASELINES.md /
README.md) from a ``baseline_results.json`` — so "report accordingly" is deterministic, not hand-edited.

Two capabilities, both pure-stdlib (NFR-004):

* :func:`replace_between_markers` — swap the body between ``<!-- BEGIN-{name} ... -->`` and
  ``<!-- END-{name} -->``, preserving both comment lines verbatim. Idempotent, and a name-boundary guard
  stops ``LEADERBOARD`` from matching the longer ``LEADERBOARD-MULTILINGUAL`` sibling.
* The **by-language F2 matrix** for the full multilingual section: rows = detectors, columns = languages,
  cell = the AUDITED micro-F2 read straight from each run's ``by_language`` slice (an em dash where a
  provider does not support that language). This module RE-DERIVES NO STATISTIC — it only formats + places
  text the audited scorer already produced.

Cloud per-language shards are read directly (one single-language run per cell), because the per-detector
:func:`pii_anon_datasets.baselines.orchestrator.merge_results` is last-wins on a name collision and so
cannot pool same-detector/different-language runs — the matrix sidesteps that by reading each cell's F2.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence


def replace_between_markers(text: str, name: str, new_block: str) -> str:
    """Return ``text`` with the body between ``BEGIN-{name}`` and ``END-{name}`` replaced by ``new_block``.

    Both marker comment lines are preserved verbatim (including any "generated from …" note on the BEGIN
    line). Raises ``ValueError`` if either marker is missing or out of order. The ``(?![-\\w])`` boundary
    guard ensures ``name="LEADERBOARD"`` does not match ``BEGIN-LEADERBOARD-MULTILINGUAL``.
    """
    begin = re.search(rf"^.*BEGIN-{re.escape(name)}(?![-\w]).*$", text, re.MULTILINE)
    end = re.search(rf"^.*END-{re.escape(name)}(?![-\w]).*$", text, re.MULTILINE)
    if not begin or not end or end.start() < begin.end():
        raise ValueError(f"markers BEGIN-{name} / END-{name} not found in order in the target text")
    block = new_block if new_block.endswith("\n") else new_block + "\n"
    return text[: begin.end()] + "\n" + block + text[end.start() :]


def language_f2(detector_block: Mapping[str, object]) -> dict[str, float]:
    """The ``{language: micro_f2}`` map from one detector block's audited ``by_language`` slice."""
    by_lang = detector_block.get("by_language") or {}
    return {lang: float(sc["f2"]) for lang, sc in by_lang.items()}  # type: ignore[index]


def cloud_provider_f2(shards: Sequence[Mapping[str, object]], provider: str) -> dict[str, float]:
    """Union one cloud ``provider``'s per-language shard F2s into a single ``{language: f2}`` map.

    Each shard is a single-language run; only ``scored`` blocks contribute (an ``unsupported-language`` /
    ``unavailable`` / ``errored`` shard adds nothing, so the matrix shows an em dash there).
    """
    out: dict[str, float] = {}
    for shard in shards:
        det = (shard.get("detectors") or {}).get(provider)  # type: ignore[union-attr]
        if det and det.get("status") == "scored":
            out.update(language_f2(det))
    return out


def render_language_matrix(rows: Sequence[tuple[str, Mapping[str, float]]], languages: Sequence[str]) -> str:
    """A markdown F2-by-language matrix: one row per detector, one column per language, em dash for a
    language a detector did not score (unsupported by the provider, or simply absent)."""
    out = [
        "| Detector | " + " | ".join(languages) + " |",
        "|---|" + "|".join("---:" for _ in languages) + "|",
    ]
    for name, lang_f2 in rows:
        cells = " | ".join(f"{lang_f2[lang]:.3f}" if lang in lang_f2 else "—" for lang in languages)
        out.append(f"| {name} | {cells} |")
    return "\n".join(out) + "\n"
