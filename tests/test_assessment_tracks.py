"""CAP-02 — multi-family assessment tracks, never merged (NFR-045/055; AX-004).

A privacy assessment scores DIFFERENT metric families — detection (recall), anonymization (residual re-id risk +
utility Pareto), pseudonymization (reversal / collision / referential integrity) — that are NEVER collapsed into
one 'de-identification' score (AX-004 / NFR-005). This lifts the cycle-1 structural separation to the ASSESSMENT
level: AssessmentTracks holds the families as SEPARATE sections, structurally forbids a merged cross-family
headline (no combined/overall/deid/score field; not float-coercible), and is mutation-tested against fusion.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest
from pii_anon_datasets.assessment import report as R
from pii_anon_datasets.assessment import tracks as T


def _detection_report():
    o = [R.SystemOutcome(name="A", hits=(True,) * 8 + (False,) * 2),
         R.SystemOutcome(name="B", hits=(True,) * 4 + (False,) * 6)]
    return R.build_leaderboard(o, seed=1)


# ---- the three families are named + separate ----
def test_tracks_enumerates_three_separate_families() -> None:
    assert T.TRACKS == ("detection", "anonymization", "pseudonymization")


def test_separation_note_non_strippable() -> None:
    with pytest.raises(ValueError):
        T.AssessmentTracks(separation_note="")


def test_as_dict_yields_separate_sections_no_fused_scalar() -> None:
    at = T.AssessmentTracks(detection=_detection_report(),
                            anonymization=("anon-result",), pseudonymization=("pseudo-result",))
    d = at.as_dict()
    assert set(d["tracks"]) == {"detection", "anonymization", "pseudonymization"}
    assert "rows" in d["detection"]                       # the detection family carries its own leaderboard
    assert d["anonymization"] == ["anon-result"] and d["pseudonymization"] == ["pseudo-result"]
    # no merged headline key anywhere at the top level
    assert not ({"combined", "overall", "deid", "de_identification_score", "score"} & set(d))


# ---- the structural no-merge guard (AX-004) — mutation-tested ----
def test_guard_passes_for_separated_tracks() -> None:
    T.assert_no_merged_family(T.AssessmentTracks(detection=_detection_report()))


@pytest.mark.parametrize("bad_field", ["combined", "overall", "deid", "de_identification_score", "score", "fused"])
def test_guard_rejects_merged_family_field(bad_field) -> None:
    @dataclass(frozen=True)
    class _Fused:
        pass
    obj = _Fused()
    object.__setattr__(obj, bad_field, 0.5)  # graft a forbidden merged-family field
    with pytest.raises(ValueError):
        T.assert_no_merged_family(obj)


def test_guard_rejects_float_coercible_fused_score() -> None:
    class _Scalar:
        def __float__(self) -> float:
            return 0.5
    with pytest.raises(ValueError):
        T.assert_no_merged_family(_Scalar())


def test_guard_rejects_int_only_fused_score() -> None:
    # an __int__-only object is NOT float()-coercible but is still a fused scalar -> must be rejected
    class _IntScalar:
        def __int__(self) -> int:
            return 1
    with pytest.raises(ValueError):
        T.assert_no_merged_family(_IntScalar())


def test_guard_rejects_index_coercible_fused_score() -> None:
    class _IdxScalar:
        def __index__(self) -> int:
            return 1
    with pytest.raises(ValueError):
        T.assert_no_merged_family(_IdxScalar())


def test_assessment_tracks_is_not_float_coercible() -> None:
    with pytest.raises(TypeError):
        float(T.AssessmentTracks())
