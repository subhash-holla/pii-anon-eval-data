"""Tests for stats.paired (FR-002 paired detector A/B regression; NFR-002 named method).

S4-02 — the MEASUREMENT side of the FR-002 detector-regression gate: McNemar's test
(exact binomial tail + Edwards continuity-corrected χ²) over the discordant pairs, plus a
**seeded** paired bootstrap for the recall-difference CI. Pure-stdlib + deterministic (NFR-004):
the bootstrap MUST use a local ``random.Random(seed)`` — never the module-global RNG — so two
runs with the same seed are byte-identical. Every test fn carries an ``fr_002``/``nfr_002`` token.
"""
import ast
import math
import pathlib

import pytest
from pii_anon_datasets.stats import paired as paired_mod
from pii_anon_datasets.stats.intervals import Interval
from pii_anon_datasets.stats.paired import (
    McNemarResult,
    mcnemar_chi2,
    mcnemar_exact,
    paired_bootstrap_recall_delta,
)


def test_fr_002_mcnemar_exact_binomial() -> None:
    """Two-sided exact binomial tail over the discordant pairs (b, c) — [UNIT-TEST].

    b=10, c=0 is maximally discordant → p = 2·0.5^10 ≈ 0.00195 (one tail only).
    b=5, c=5 is symmetric → p ≈ 1.0 (no evidence of asymmetry).
    """
    far = mcnemar_exact(b=10, c=0)
    assert isinstance(far, McNemarResult)
    assert far.statistic == 0.0  # statistic = min(b, c)
    assert far.p_value == pytest.approx(0.001953125, abs=1e-9)
    assert far.p_value == pytest.approx(0.00195, abs=1e-4)
    assert far.method == "mcnemar-exact"

    sym = mcnemar_exact(b=5, c=5)
    assert sym.p_value == pytest.approx(1.0, abs=1e-9)
    assert sym.statistic == 5.0


def test_fr_002_mcnemar_chi2_continuity() -> None:
    """Edwards continuity-corrected χ² = (|b−c|−1)²/(b+c); p = erfc(sqrt(χ²/2)) — [UNIT-TEST].

    b=20, c=10 → χ² = (10−1)²/30 = 2.7, p = erfc(sqrt(2.7/2)) ≈ 0.1003.
    """
    res = mcnemar_chi2(b=20, c=10, continuity=True)
    assert res.statistic == pytest.approx(2.7, abs=1e-9)
    assert res.p_value == pytest.approx(math.erfc(math.sqrt(2.7 / 2.0)), abs=1e-12)
    assert res.p_value == pytest.approx(0.1003, abs=1e-3)
    assert res.method == "mcnemar-chi2-continuity"
    # without the continuity correction the statistic is larger: (b−c)²/n = 100/30 ≈ 3.333
    raw = mcnemar_chi2(b=20, c=10, continuity=False)
    assert raw.statistic == pytest.approx(100.0 / 30.0, abs=1e-9)
    assert raw.statistic > res.statistic
    assert raw.method == "mcnemar-chi2"


def test_fr_002_mcnemar_zero_discordant() -> None:
    """b+c==0 → no discordance ⇒ no detectable difference: statistic 0.0, p 1.0 — [UNIT-TEST]."""
    for res in (mcnemar_exact(b=0, c=0), mcnemar_chi2(b=0, c=0)):
        assert res.statistic == 0.0
        assert res.p_value == 1.0


def test_fr_002_mcnemar_odds_ratio() -> None:
    """odds_ratio == b/c, and None when c==0 (undefined) — [UNIT-TEST]."""
    assert mcnemar_exact(b=20, c=10).odds_ratio == pytest.approx(2.0)
    assert mcnemar_chi2(b=30, c=15).odds_ratio == pytest.approx(2.0)
    assert mcnemar_exact(b=10, c=0).odds_ratio is None
    assert mcnemar_chi2(b=10, c=0).odds_ratio is None


def test_fr_002_paired_bootstrap_deterministic() -> None:
    """Same seed → byte-identical Interval; different seed differs — [PROPERTY-TEST].

    Reproducibility is driven by a LOCAL ``random.Random(seed)`` (NFR-004), NOT the
    module-global RNG. Two independent calls with the same seed must agree exactly.
    """
    # a richer 50-pair mix so the discrete bootstrap distribution genuinely resolves a
    # seed change at the percentile endpoints (a tiny low-cardinality sample can alias).
    pairs = ([(True, False)] * 7 + [(False, True)] * 5
             + [(True, True)] * 9 + [(False, False)] * 4) * 2
    a = paired_bootstrap_recall_delta(pairs, n_boot=2000, seed=42)
    b = paired_bootstrap_recall_delta(pairs, n_boot=2000, seed=42)
    assert a.as_dict() == b.as_dict()  # byte-identical
    assert a.low == b.low and a.high == b.high and a.point == b.point

    other = paired_bootstrap_recall_delta(pairs, n_boot=2000, seed=7)
    assert (other.low, other.high) != (a.low, a.high)

    # the global RNG state must NOT influence the result (proves it is not consulted)
    import random as _r
    _r.seed(0)
    c0 = paired_bootstrap_recall_delta(pairs, n_boot=2000, seed=42)
    _r.seed(999999)
    c1 = paired_bootstrap_recall_delta(pairs, n_boot=2000, seed=42)
    assert c0.as_dict() == c1.as_dict() == a.as_dict()


def test_fr_002_paired_bootstrap_brackets_delta() -> None:
    """Percentile interval brackets the observed recall-Δ; n==len(pairs); A>B ⇒ low>0 — [UNIT-TEST]."""
    # strongly A-favouring: A hits all, B hits almost none → observed Δ ≈ +0.9
    pairs = [(True, False)] * 18 + [(True, True)] * 2
    iv = paired_bootstrap_recall_delta(pairs, n_boot=4000, seed=123)
    observed = sum(a for a, _ in pairs) / len(pairs) - sum(b for _, b in pairs) / len(pairs)
    assert iv.point == pytest.approx(observed)
    assert iv.n == len(pairs)
    assert iv.low <= iv.point <= iv.high
    assert iv.low > 0.0  # CI excludes 0 ⇒ A significantly out-recalls B
    assert -1.0 <= iv.low <= iv.high <= 1.0


def test_nfr_002_paired_bootstrap_method_named() -> None:
    """Every published result carries a NAMED method (NFR-002) — [UNIT-TEST]."""
    pairs = [(True, False), (False, True), (True, True), (False, False)]
    iv = paired_bootstrap_recall_delta(pairs, n_boot=500, seed=1)
    assert isinstance(iv, Interval)
    assert iv.method == "paired-bootstrap"
    assert iv.confidence == 0.95
    assert mcnemar_exact(b=4, c=1).method == "mcnemar-exact"
    assert mcnemar_chi2(b=4, c=1).method in {"mcnemar-chi2-continuity", "mcnemar-chi2"}
    # round-trippable for reporting
    assert iv.as_dict()["method"] == "paired-bootstrap"


def test_fr_002_nfr004_paired_imports_no_uncontrolled_nondeterminism() -> None:
    """AST guard (NFR-004 / AX-002): paired.py imports none of {time,uuid,datetime,secrets};
    ``random`` IS allowed but ONLY via ``random.Random(seed)`` — assert there is NO module-global
    ``random.<fn>`` call in the source (the bootstrap must own a local RNG) — [PROPERTY-TEST].
    """
    src = pathlib.Path(paired_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)

    banned = {"time", "uuid", "datetime", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), (
        f"paired.py imports nondeterministic modules: {sorted(banned & imported)}"
    )

    # No module-global RNG: every `random.<attr>` access must be exactly `random.Random`.
    offending: list[str] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "random"
            and node.attr != "Random"
        ):
            offending.append(f"random.{node.attr}")
    assert not offending, (
        f"paired.py must use only random.Random(seed), not the module-global RNG: {offending}"
    )
