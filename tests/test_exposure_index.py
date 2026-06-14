"""Tests for the FR-008 deterministic exposure index (pre-screen PRIOR, NOT RRS) and
the index<->measured-RRS correlation (S3-05; DC-07).

The load-bearing distinction (FR-008): the exposure index is a DETERMINISTIC pre-screen
PRIOR that is *explicitly not* measured RRS — a DISTINCT type from MeasuredRRS with NO
rrs/reid_recall/reid_precision field and a non-empty, validated ``note``. This is what
prevents the cheap heuristic from being cited as a re-identification result (the exact
de-circularization concern). ``correlate_index_vs_rrs`` (Pearson + Spearman, stdlib) is
the evidence that the prior tracks the measured attack — Spearman because the relationship
is monotone-but-nonlinear by construction.

Traceability: every function name carries the `fr_008` token; the import-purity guard
also carries `nfr004`. dc_07, ax_002.
"""
import ast
import dataclasses
import math
import pathlib

from pii_anon_datasets.scoring import reidentification, signals

# A fixed behavioral_signals block: exactly the six detector categories, so the per-signal
# contribution is unambiguous. weights = [0.65, 1.0, 0.35, 0.0, 0.0, 0.0]:
#   peak = 1.0, mean = (0.65 + 1.0 + 0.35) / 6 = 0.3333..., density = 0.6*1.0 + 0.4*mean.
FIXED_SIGNALS_BLOCK: dict[str, object] = {
    "writing_style": {"present": True, "uniqueness": "high", "indicators": ["rich_vocabulary"]},
    "professional_domain": {"present": True, "uniqueness": "very_high", "indicators": ["industry_jargon:medical:3"]},
    "interest_topics": {"present": True, "uniqueness": "moderate", "indicators": ["topic:fitness:1"]},
    "temporal_patterns": {"present": False, "uniqueness": "none", "indicators": []},
    "location_signals": {"present": False, "uniqueness": "none", "indicators": []},
    "personal_anecdote": {"present": False, "uniqueness": "none", "indicators": []},
}


# 1. ::test_fr_008_exposure_index_is_prior_not_rrs  [UNIT-TEST]
def test_fr_008_exposure_index_is_prior_not_rrs():
    """ExposureIndex is a DISTINCT type from MeasuredRRS (no rrs/reid_recall/reid_precision
    field), carries a non-empty ``note`` stating it is a pre-screen prior and "NOT measured
    RRS", and pins ``method == "behavioral-signal-density-v1"`` — so the cheap heuristic can
    never be mistaken for a re-identification result (FR-008, load-bearing)."""
    idx = reidentification.exposure_index(FIXED_SIGNALS_BLOCK)

    # DISTINCT type — not a MeasuredRRS, not an RRSResult.
    assert type(idx) is reidentification.ExposureIndex
    assert not isinstance(idx, reidentification.MeasuredRRS)
    assert not isinstance(idx, reidentification.RRSResult)

    # NO re-identification-result fields may leak onto the prior.
    field_names = {f.name for f in dataclasses.fields(idx)}
    assert {"rrs", "reid_recall", "reid_precision"}.isdisjoint(field_names), field_names
    for forbidden in ("rrs", "reid_recall", "reid_precision"):
        assert not hasattr(idx, forbidden)

    # Non-empty note explicitly disclaiming RRS.
    assert idx.note.strip()
    assert "NOT measured RRS" in idx.note
    assert "prior" in idx.note.lower()
    # The module-level constant is the single source of that note.
    assert idx.note == reidentification.EXPOSURE_INDEX_NOTE

    # Versioned method name (auditable).
    assert idx.method == "behavioral-signal-density-v1"


# 2. ::test_fr_008_exposure_index_recomputes_density_transparently  [UNIT-TEST]
def test_fr_008_exposure_index_recomputes_density_transparently():
    """``exposure_index(block).value`` equals ``signals.compute_signal_density(block)`` to
    1e-9 — the value is RECOMPUTED transparently from the annotations via the S3-01 signals
    module, NOT read from any precomputed ``behavioral_signal_density`` scalar."""
    expected = signals.compute_signal_density(FIXED_SIGNALS_BLOCK)
    idx = reidentification.exposure_index(FIXED_SIGNALS_BLOCK)
    assert math.isclose(idx.value, expected, abs_tol=1e-9), (idx.value, expected)
    # the fixed block's known density (0.6*1.0 + 0.4*((0.65+1.0+0.35)/6), 4-dp).
    assert idx.value == 0.7333
    assert 0.0 <= idx.value <= 1.0

    # PROOF it does not trust a precomputed scalar: a poisoned ``behavioral_signal_density``
    # field in the block must be ignored — the value is recomputed from the per-category
    # uniqueness annotations, so it stays at the transparently-recomputed density.
    poisoned = dict(FIXED_SIGNALS_BLOCK)
    poisoned["behavioral_signal_density"] = 0.123456  # a lie the function must NOT read
    poisoned["reidentification_contribution"] = "low"
    assert reidentification.exposure_index(poisoned).value == 0.7333


# 3. ::test_fr_008_exposure_index_per_signal_transparent  [UNIT-TEST]
def test_fr_008_exposure_index_per_signal_transparent():
    """``ExposureIndex.per_signal`` exposes each of the six category weights (auditable):
    a sorted tuple of (category, w_c) where w_c = UNIQUENESS_WEIGHT[category.uniqueness]."""
    idx = reidentification.exposure_index(FIXED_SIGNALS_BLOCK)
    per = idx.per_signal

    # transparent, immutable, sorted by category name.
    assert isinstance(per, tuple)
    categories = [c for c, _ in per]
    assert categories == sorted(categories)

    # exactly the six detector categories are represented.
    assert set(categories) == {
        "writing_style",
        "professional_domain",
        "interest_topics",
        "temporal_patterns",
        "location_signals",
        "personal_anecdote",
    }
    assert len(per) == 6

    # each weight is exactly the UNIQUENESS_WEIGHT for that category's uniqueness label.
    per_map = dict(per)
    assert per_map["writing_style"] == signals.UNIQUENESS_WEIGHT["high"]
    assert per_map["professional_domain"] == signals.UNIQUENESS_WEIGHT["very_high"]
    assert per_map["interest_topics"] == signals.UNIQUENESS_WEIGHT["moderate"]
    assert per_map["temporal_patterns"] == signals.UNIQUENESS_WEIGHT["none"]
    assert per_map["location_signals"] == signals.UNIQUENESS_WEIGHT["none"]
    assert per_map["personal_anecdote"] == signals.UNIQUENESS_WEIGHT["none"]


# 4. ::test_fr_008_correlation_pearson_and_spearman  [UNIT-TEST]
def test_fr_008_correlation_pearson_and_spearman():
    """``correlate_index_vs_rrs(pairs)`` on a monotone-increasing synthetic set yields
    ``spearman_rho == 1.0`` (perfect rank agreement), a Pearson ``r`` in [-1, 1], the
    correct ``n``, and a named ``method`` — the evidence the prior tracks measured RRS."""
    # monotone-but-nonlinear by construction (index grows, RRS grows convexly).
    pairs = [(0.1, 0.01), (0.2, 0.04), (0.3, 0.09), (0.5, 0.25), (0.8, 0.64)]
    corr = reidentification.correlate_index_vs_rrs(pairs)

    assert type(corr) is reidentification.IndexRRSCorrelation
    assert corr.n == len(pairs)
    # strictly monotone ranks → perfect Spearman.
    assert math.isclose(corr.spearman_rho, 1.0, abs_tol=1e-9), corr.spearman_rho
    # Pearson bounded; strong positive but < 1 (nonlinear), so it is genuinely Pearson.
    assert -1.0 <= corr.pearson_r <= 1.0
    assert 0.9 < corr.pearson_r < 1.0, corr.pearson_r
    assert isinstance(corr.method, str) and corr.method.strip()
    assert "spearman" in corr.method.lower() and "pearson" in corr.method.lower()


# 5. ::test_fr_008_correlation_n_zero_graceful  [UNIT-TEST]
def test_fr_008_correlation_n_zero_graceful():
    """Empty pairs → ``n == 0`` and a graceful nan/None result (no division error raised)."""
    corr = reidentification.correlate_index_vs_rrs([])
    assert corr.n == 0
    # nan or None — reported, never raised.
    for v in (corr.pearson_r, corr.spearman_rho):
        assert v is None or (isinstance(v, float) and math.isnan(v)), v


# 6. ::test_fr_008_nfr004_exposure_imports_no_nondeterminism  [PROPERTY-TEST]
def test_fr_008_nfr004_exposure_imports_no_nondeterminism():
    """AX-002/NFR-004: the exposure-index + correlation code added to reidentification.py
    must depend on NO nondeterminism source. Statically prove the module imports none of
    {random, time, uuid, datetime, secrets} and no third-party numeric stack (numpy/scipy/
    pandas) — Pearson/Spearman are computed by hand in pure stdlib."""
    src = pathlib.Path(reidentification.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned = {"random", "time", "uuid", "datetime", "secrets", "numpy", "scipy", "pandas"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), (
        f"reidentification.py imports forbidden modules: {sorted(banned & imported)}"
    )
