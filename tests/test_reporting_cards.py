"""Mechanical card regeneration — the marker-delimited block replacement that makes "report accordingly"
deterministic instead of hand-edited, plus the cross-detector by-language F2 matrix used for the full
multilingual section.

Every matrix cell is an AUDITED F2 read straight from a run's ``by_language`` slice — this module
re-derives no statistic (it only formats + places text). The marker replacer preserves both comment lines
verbatim and is idempotent, so re-running the sync never drifts the cards.
"""

from __future__ import annotations

import pytest
from pii_anon_datasets.reporting import cards


# --------------------------------------------------------------------------------------------------------
# replace_between_markers — the load-bearing, idempotent block swap
# --------------------------------------------------------------------------------------------------------
_DOC = (
    "intro line\n"
    "<!-- BEGIN-LEADERBOARD (generated from X; do not hand-edit) -->\n"
    "OLD TABLE\n"
    "more old\n"
    "<!-- END-LEADERBOARD -->\n"
    "outro line\n"
)


def test_replaces_only_between_markers_preserving_both_comment_lines() -> None:
    out = cards.replace_between_markers(_DOC, "LEADERBOARD", "NEW TABLE\n")
    assert "OLD TABLE" not in out
    assert "NEW TABLE" in out
    assert "<!-- BEGIN-LEADERBOARD (generated from X; do not hand-edit) -->" in out  # begin line verbatim
    assert "<!-- END-LEADERBOARD -->" in out
    assert out.startswith("intro line\n") and out.endswith("outro line\n")  # outside untouched


def test_replacement_is_idempotent() -> None:
    once = cards.replace_between_markers(_DOC, "LEADERBOARD", "NEW\n")
    twice = cards.replace_between_markers(once, "LEADERBOARD", "NEW\n")
    assert once == twice


def test_marker_name_boundary_does_not_match_a_longer_sibling() -> None:
    # A doc holding BOTH LEADERBOARD and LEADERBOARD-MULTILINGUAL: replacing one must not touch the other.
    doc = (
        "<!-- BEGIN-LEADERBOARD -->\nA\n<!-- END-LEADERBOARD -->\n"
        "<!-- BEGIN-LEADERBOARD-MULTILINGUAL -->\nB\n<!-- END-LEADERBOARD-MULTILINGUAL -->\n"
    )
    out = cards.replace_between_markers(doc, "LEADERBOARD", "A2\n")
    assert "A2" in out and "A\n" not in out
    assert "<!-- BEGIN-LEADERBOARD-MULTILINGUAL -->\nB\n" in out  # sibling block untouched

    out2 = cards.replace_between_markers(doc, "LEADERBOARD-MULTILINGUAL", "B2\n")
    assert "B2" in out2 and "<!-- BEGIN-LEADERBOARD -->\nA\n" in out2  # the short block untouched


def test_missing_marker_raises() -> None:
    with pytest.raises(ValueError):
        cards.replace_between_markers("no markers here", "LEADERBOARD", "x")


# --------------------------------------------------------------------------------------------------------
# by-language F2 extraction + matrix rendering (reads audited F2; invents nothing)
# --------------------------------------------------------------------------------------------------------
def _det_block(by_language: dict[str, float]) -> dict:
    return {"status": "scored", "by_language": {lang: {"f2": f2} for lang, f2 in by_language.items()}}


def test_language_f2_extracts_the_by_language_slice() -> None:
    block = _det_block({"en": 0.73, "fr": 0.41})
    assert cards.language_f2(block) == {"en": 0.73, "fr": 0.41}


def test_cloud_provider_f2_unions_single_language_shards() -> None:
    shard_en = {"detectors": {"azure": _det_block({"en": 0.70})}}
    shard_fr = {"detectors": {"azure": _det_block({"fr": 0.52})}}
    shard_unscored = {"detectors": {"azure": {"status": "unsupported-language"}}}
    got = cards.cloud_provider_f2([shard_en, shard_fr, shard_unscored], "azure")
    assert got == {"en": 0.70, "fr": 0.52}


def test_render_language_matrix_uses_dashes_for_missing_cells() -> None:
    rows = [
        ("gliner", {"en": 0.74, "fr": 0.60, "hi": 0.31}),
        ("azure", {"en": 0.70, "fr": 0.52}),  # azure does not support hi -> em dash
    ]
    md = cards.render_language_matrix(rows, ["en", "fr", "hi"])
    lines = md.strip().splitlines()
    assert lines[0] == "| Detector | en | fr | hi |"
    assert lines[1] == "|---|---:|---:|---:|"
    assert lines[2] == "| gliner | 0.740 | 0.600 | 0.310 |"
    assert lines[3] == "| azure | 0.700 | 0.520 | — |"  # honest: unsupported language shown, not faked
