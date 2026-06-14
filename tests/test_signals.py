"""Tests for scoring.signals (FR-008 exposure-index substrate; ported from
scripts/enrich_behavioral_signals.py per S3-01 §8b).

Pins the golden UNIQUENESS_WEIGHT table, the compute_signal_density formula
(0.6*peak + 0.4*mean), and the purity/determinism of detect_* (AX-002, NFR-004).

Traceability: function names carry the `fr_008` token (exposure-index pre-screen
substrate; FR-010 port consumes signals.extract for Target.observed_signals); the
purity guard carries `nfr_004`. dc_07, reidx_01, ax_002.
"""
import ast
import math
import pathlib

from pii_anon_datasets.scoring import signals


# 8. ::test_fr_008_uniqueness_weight_table_matches_source  [UNIT-TEST]
def test_fr_008_uniqueness_weight_table_matches_source():
    assert signals.UNIQUENESS_WEIGHT == {
        "none": 0.0,
        "low": 0.15,
        "moderate": 0.35,
        "high": 0.65,
        "very_high": 1.0,
    }


# 9. ::test_fr_008_compute_signal_density_golden  [UNIT-TEST]
def test_fr_008_compute_signal_density_golden():
    # Fixed signals block: weights = [0.65, 1.0, 0.35, 0, 0, 0]
    # peak=1.0, mean=0.3333..., density = 0.6*1.0 + 0.4*0.3333... = 0.73333...
    fixed = {
        "writing_style": {"present": True, "uniqueness": "high", "indicators": ["rich_vocabulary"]},
        "professional_domain": {"present": True, "uniqueness": "very_high", "indicators": ["industry_jargon:medical:3"]},
        "interest_topics": {"present": True, "uniqueness": "moderate", "indicators": ["topic:fitness:1"]},
        "temporal_patterns": {"present": False, "uniqueness": "none", "indicators": []},
        "location_signals": {"present": False, "uniqueness": "none", "indicators": []},
        "personal_anecdote": {"present": False, "uniqueness": "none", "indicators": []},
    }
    # source formula 0.6*peak + 0.4*mean, then round(.., 4) (ported faithfully)
    expected_raw = 0.6 * 1.0 + 0.4 * (0.65 + 1.0 + 0.35) / 6
    expected = round(min(1.0, expected_raw), 4)
    got = signals.compute_signal_density(fixed)
    # reproduces the rounded golden to 1e-9 …
    assert math.isclose(got, expected, abs_tol=1e-9), (got, expected)
    # … and equals the source's 4-dp value exactly
    assert got == 0.7333


# 10. ::test_fr_008_detect_signals_pure_and_deterministic  [PROPERTY-TEST]
def test_fr_008_detect_signals_pure_and_deterministic():
    text = (
        "As an attending physician I review the differential diagnosis daily. "
        "My commute on the T into Beacon Hill takes forever this morning. "
        "Hit a new 1RM on my split — macros are dialed in!! "
        "When I was a kid I lived in a small town near the Cape."
    )
    detectors = [
        signals.detect_writing_style,
        signals.detect_professional_domain,
        signals.detect_interest_topics,
        signals.detect_temporal_patterns,
        signals.detect_location_signals,
        signals.detect_personal_anecdote,
    ]
    for det in detectors:
        a = det(text)
        b = det(text)
        # same input twice → byte-identical output (no RNG / clock / IO)
        assert a == b
        # contract shape (FR-008): present/uniqueness/indicators
        assert set(a.keys()) == {"present", "uniqueness", "indicators"}
        assert isinstance(a["present"], bool)
        assert a["uniqueness"] in signals.UNIQUENESS_WEIGHT
        assert isinstance(a["indicators"], list)

    # extract() is likewise deterministic and yields the full behavioral_signals block
    e1 = signals.extract(text)
    e2 = signals.extract(text)
    assert e1 == e2
    assert {
        "writing_style",
        "professional_domain",
        "interest_topics",
        "temporal_patterns",
        "location_signals",
        "personal_anecdote",
    } <= set(e1.keys())
    assert "behavioral_signal_density" in e1


# 10b. ::test_fr_008_nfr004_signals_imports_no_nondeterminism  [PROPERTY-TEST] / [AUDIT]
def test_fr_008_nfr004_signals_imports_no_nondeterminism():
    """AX-002/NFR-004 hardening (axiom-S3-01-01): the extractor must depend on NO
    nondeterminism source. Statically prove signals.py imports none of
    {random, time, uuid, datetime, secrets} — a stronger warrant than intra-process
    idempotence (which a shared seeded RNG could fake)."""
    src = pathlib.Path(signals.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned = {"random", "time", "uuid", "datetime", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), f"signals.py imports nondeterministic modules: {sorted(banned & imported)}"


# ::test_fr_008_signal_extractor_version_pinned  [UNIT-TEST]
def test_fr_008_signal_extractor_version_pinned():
    assert signals.SIGNAL_EXTRACTOR_VERSION == "signal-extractor-v1"
