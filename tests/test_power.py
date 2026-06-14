"""Tests for stats.power (FR-029, NFR-018, AX-003) and taxonomy risk tiers.

Pins: NIST targets derive to 1,522/753/200; the design-time projection path is continuous
(NOT integer-guarded, unlike the measured wilson_interval); cell classification + audit +
McNemar efficiency; determinism (NFR-004).
"""
import math

import pytest

from pii_anon_datasets import taxonomy as tx
from pii_anon_datasets.stats import power as pw
from pii_anon_datasets.stats.intervals import Interval, wilson_interval


# ── risk tiers (taxonomy) ────────────────────────────────────────────────────────────────
def test_risk_tiers_partition_63_types():
    tiers = {t: tx.risk_tier(t) for t in tx.CANONICAL_ENTITY_TYPES}
    crit = [t for t, r in tiers.items() if r == "critical"]
    std = [t for t, r in tiers.items() if r == "standard"]
    lt = [t for t, r in tiers.items() if r == "long_tail"]
    assert len(crit) == 22 and len(std) == 31 and len(lt) == 10
    assert len(crit) + len(std) + len(lt) == tx.ENTITY_TYPE_COUNT == 63


def test_risk_tier_membership():
    assert tx.risk_tier("IBAN") == "critical"            # financial
    assert tx.risk_tier("API_KEY") == "critical"          # credential
    assert tx.risk_tier("SOCIAL_SECURITY_NUMBER") == "critical"  # strong gov-id
    assert tx.risk_tier("PERSON_NAME") == "standard"
    assert tx.risk_tier("EMAIL_ADDRESS") == "standard"
    assert tx.risk_tier("AGE") == "long_tail"
    assert tx.risk_tier("POLITICAL_OPINION") == "long_tail"


def test_risk_tier_unknown_fails_loud():
    with pytest.raises(KeyError):
        tx.risk_tier("NOT_A_REAL_TYPE")


def test_types_in_tier_round_trips():
    for tier in ("critical", "standard", "long_tail"):
        assert all(tx.risk_tier(t) == tier for t in tx.types_in_tier(tier))


# ── NIST sample sizing: the targets are DERIVED, not hand-typed (NFR-018 anti-drift) ──────
def test_required_n_reproduces_canonical_targets():
    assert pw.required_n(0.99, 0.005) == 1522
    assert pw.required_n(0.98, 0.010) == 753
    assert pw.required_n(0.95, 0.03025) == 200


def test_tier_specs_targets_are_derived():
    for tier, spec in pw.TIER_SPECS.items():
        assert spec.target_n == pw.required_n(spec.p_ref, spec.half_width)
    assert pw.target_for_tier(pw.Tier.CRITICAL) == 1522
    assert pw.target_for_tier("standard") == 753
    assert pw.target_for_tier("long_tail") == 200


def test_required_n_rejects_bad_inputs():
    for p in (0.0, 1.0, -0.1, 1.5):
        with pytest.raises(ValueError):
            pw.required_n(p, 0.01)
    with pytest.raises(ValueError):
        pw.required_n(0.98, 0.0)


# ── design-time projection is CONTINUOUS and distinct from the measured path ──────────────
def test_projection_accepts_continuous_p_ref_no_integer_guard():
    # wilson_interval rejects fractional counts; the projection accepts a continuous p_ref.
    with pytest.raises(TypeError):
        wilson_interval(98.5, 100)  # type: ignore[arg-type]
    hw = pw.projected_wilson_halfwidth(0.987, 1234)  # continuous p_ref, no raise
    assert 0.0 < hw < 1.0


def test_projected_interval_is_marked_projected():
    iv = pw.projected_interval(0.98, 753)
    assert isinstance(iv, Interval)
    assert iv.method == "wilson-projected"      # never confusable with a measured CI
    assert iv.point == pytest.approx(0.98)
    assert 0.0 <= iv.low < iv.point < iv.high <= 1.0


def test_projected_halfwidth_at_target_matches_tier_precision():
    # at n == target_n the projected half-width is ~ the tier's design half-width
    assert pw.projected_wilson_halfwidth(0.99, 1522) == pytest.approx(0.005, abs=7e-4)
    assert pw.projected_wilson_halfwidth(0.98, 753) == pytest.approx(0.010, abs=1e-3)


def test_projection_n_zero_is_nan():
    iv = pw.projected_interval(0.98, 0)
    assert math.isnan(iv.point) and (iv.low, iv.high) == (0.0, 1.0)
    assert pw.projected_wilson_halfwidth(0.98, 0) == 1.0


# ── classification ───────────────────────────────────────────────────────────────────────
def test_classify():
    assert pw.classify(800, 753) is pw.PowerClass.WELL_POWERED
    assert pw.classify(753, 753) is pw.PowerClass.WELL_POWERED
    assert pw.classify(700, 753) is pw.PowerClass.UNDER_POWERED
    assert pw.classify(0, 753) is pw.PowerClass.EMPTY


def test_classify_rejects_non_integer():
    with pytest.raises(TypeError):
        pw.classify(700.0, 753)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        pw.classify(True, 753)


# ── max-of-members tier rule ─────────────────────────────────────────────────────────────
def test_default_tier_of_cell():
    assert pw.default_tier_of((("entity_type", "IBAN"),)) is pw.Tier.CRITICAL
    assert pw.default_tier_of((("entity_type", "PERSON_NAME"),)) is pw.Tier.STANDARD
    assert pw.default_tier_of((("entity_type", "AGE"),)) is pw.Tier.LONG_TAIL
    # 2-way cell: max-of-members → critical because CVV is critical
    assert pw.default_tier_of((("language", "fr"), ("entity_type", "CVV"))) is pw.Tier.CRITICAL
    # no entity_type → standard
    assert pw.default_tier_of((("domain", "financial"), ("track", "clean"))) is pw.Tier.STANDARD


# ── McNemar paired efficiency ────────────────────────────────────────────────────────────
def test_required_discordant_pairs_positive_and_monotone():
    near = pw.required_discordant_pairs(1.5)   # small effect → many pairs
    far = pw.required_discordant_pairs(4.0)     # big effect → fewer pairs
    assert isinstance(near, int) and near > far > 0


def test_required_discordant_pairs_rejects_no_effect():
    with pytest.raises(ValueError):
        pw.required_discordant_pairs(1.0)
    with pytest.raises(ValueError):
        pw.required_discordant_pairs(0.0)


def test_paired_more_efficient_than_independent_for_correlated_errors():
    # strong detectors agree on the easy majority (positively-correlated errors) → small
    # p_disc → paired is more efficient than two independent arms.
    assert pw.paired_vs_independent_ratio(p_ref=0.98, p_disc=0.02) < 1.0
    # honest about the regime: if errors were independent/anti-correlated (large p_disc),
    # the variance ratio can exceed 1 — the function does not over-claim.
    assert pw.paired_vs_independent_ratio(p_ref=0.98, p_disc=0.10) > 1.0
    # boundary is exactly 2·p(1-p)
    assert pw.paired_vs_independent_ratio(0.98, 2 * 0.98 * 0.02) == pytest.approx(1.0)


# ── corpus audit → PowerMatrix ───────────────────────────────────────────────────────────
def test_audit_crossing_classifies_and_summarizes():
    counts = {
        (("entity_type", "IBAN"),): 2000,        # critical, well (>=1522)
        (("entity_type", "CVV"),): 1500,          # critical, under (<1522)
        (("entity_type", "PERSON_NAME"),): 800,   # standard, well (>=753)
        (("entity_type", "URL"),): 186,           # standard, under
        (("entity_type", "AGE"),): 189,           # long_tail, under (<200)
        (("entity_type", "GENDER"),): 494,        # long_tail, well (>=200)
        (("entity_type", "VISA_NUMBER"),): 0,     # critical, empty
    }
    m = pw.audit_crossing(counts)
    s = m.summary()
    assert s["cells"] == 7
    assert s["well_powered"] == 3   # IBAN, PERSON_NAME, GENDER
    assert s["under_powered"] == 3  # CVV, URL, AGE
    assert s["empty"] == 1          # VISA_NUMBER
    # shortfall = (1522-1500)+(753-186)+(200-189)+(1522-0) = 22+567+11+1522 = 2122
    assert s["total_shortfall"] == 22 + 567 + 11 + 1522
    assert m.axes == ("entity_type",)


def test_audit_attaches_measured_ci_when_given():
    counts = {(("entity_type", "IBAN"),): 2000}
    m = pw.audit_crossing(counts, measured_recall={(("entity_type", "IBAN"),): (1980, 2000)})
    cell = m.cells[0]
    assert cell.measured_ci is not None and cell.measured_ci.method == "wilson"
    assert cell.projected_ci.method == "wilson-projected"   # both present, distinct


def test_powermatrix_renderers_deterministic_and_sorted():
    counts = {(("entity_type", "CVV"),): 100, (("entity_type", "IBAN"),): 2000}
    a = pw.audit_crossing(counts)
    b = pw.audit_crossing(counts)
    assert a.to_markdown() == b.to_markdown()
    assert a.to_csv() == b.to_csv()
    # sorted by cell_id → CVV row before IBAN row
    md = a.to_markdown()
    assert md.index("entity_type=CVV") < md.index("entity_type=IBAN")
    assert "cell_id,n,tier,target_n,power_class,shortfall" in a.to_csv()


def test_powermatrix_verdict():
    allgood = pw.audit_crossing({(("entity_type", "IBAN"),): 2000})
    assert allgood.verdict() == "LARGE"
    halfbad = pw.audit_crossing({
        (("entity_type", "IBAN"),): 2000, (("entity_type", "CVV"),): 1,
    })
    assert halfbad.verdict() == "SMALL"
