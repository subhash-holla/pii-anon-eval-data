"""Tests for validation.correlation (FR-027 real-data validation correlation harness).

S7-03 — the DC-14 (v1.1) real-data validation seam: a pre-registered Kendall-tau /
Spearman rho + a **seeded** bootstrap CI + a Bland-Altman agreement view over paired
synthetic-vs-real scores. The crux is **epistemic honesty**: the real i2b2-2014 / TAB data
is NOT present (licensing), so ``correlate`` returns a ``RealDataAbsent`` sentinel and
**NEVER fabricates** a correlation (FR-027). Pure-stdlib + deterministic (NFR-004 / AX-002):
the bootstrap MUST use a local ``random.Random(seed)`` — never the module-global RNG — so two
runs with the same seed are byte-identical. Every test fn carries an ``fr_027``/``nfr004`` token.
"""

import ast
import pathlib

import pytest
from pii_anon_datasets.validation import correlation as correlation_mod
from pii_anon_datasets.validation.correlation import (
    CORRELATION_CAVEAT,
    CorrelationResult,
    RealDataAbsent,
    correlate,
)


def test_fr_027_returns_sentinel_when_real_data_absent() -> None:
    """Absent real data -> RealDataAbsent sentinel; NEVER a fabricated correlation — [CONTRACT-TEST].

    ``correlate(synthetic, real_scores=None)`` AND ``correlate(synthetic, real_scores=[])``
    BOTH return a ``RealDataAbsent`` (``available is False``), never a ``CorrelationResult`` —
    the harness refuses to invent a correlation when the real scores are absent (FR-027). The
    sentinel ``note`` makes the absence explicit ("not present" + "fabricate"/"Pass-2").
    """
    synthetic = [0.1, 0.2, 0.3, 0.4, 0.5]

    absent_cases: list[list[float] | None] = [None, []]
    for absent in absent_cases:
        result = correlate(synthetic, real_scores=absent)
        assert isinstance(result, RealDataAbsent)
        assert not isinstance(result, CorrelationResult)  # NEVER a fabricated correlation
        assert result.available is False
        note = result.note.lower()
        assert "not present" in note
        assert ("fabricate" in note) or ("pass-2" in note)


def test_fr_027_correlation_on_paired_scores() -> None:
    """Paired scores -> CorrelationResult; tau/rho in [-1,1]; concordant->~1, discordant->~-1 — [UNIT-TEST].

    A perfectly-concordant pair (y monotone-increasing in x) -> tau ~= 1.0 and rho ~= 1.0;
    a perfectly-discordant pair (y monotone-decreasing in x) -> tau ~= -1.0 and rho ~= -1.0.
    ``n`` == len(x); the Bland-Altman mean difference + +/-1.96 sd limits are computed.
    """
    x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    y_concordant = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]  # strictly increasing in x
    y_discordant = [12.0, 10.0, 8.0, 6.0, 4.0, 2.0]  # strictly decreasing in x

    res = correlate(x, y_concordant, seed=0, n_boot=200)
    assert isinstance(res, CorrelationResult)
    assert res.n == len(x)
    assert -1.0 <= res.kendall_tau <= 1.0
    assert -1.0 <= res.spearman_rho <= 1.0
    assert res.kendall_tau == pytest.approx(1.0, abs=1e-9)
    assert res.spearman_rho == pytest.approx(1.0, abs=1e-9)
    # Bland-Altman: per-pair diff x-y is constant -x here, so mean_diff is well-defined and
    # the limits bracket it (sd is finite; lo <= mean_diff <= hi).
    lo, hi = res.bland_altman_limits
    assert lo <= res.bland_altman_mean_diff <= hi

    rev = correlate(x, y_discordant, seed=0, n_boot=200)
    assert isinstance(rev, CorrelationResult)
    assert rev.kendall_tau == pytest.approx(-1.0, abs=1e-9)
    assert rev.spearman_rho == pytest.approx(-1.0, abs=1e-9)
    assert -1.0 <= rev.kendall_tau <= 1.0
    assert -1.0 <= rev.spearman_rho <= 1.0


def test_fr_027_bootstrap_ci_seeded_deterministic() -> None:
    """Same seed -> byte-identical tau_ci / rho_ci; the CI brackets the point estimate — [PROPERTY-TEST].

    Reproducibility is driven by a LOCAL ``random.Random(seed)`` (NFR-004 / AX-002), NOT the
    module-global RNG: two independent calls with the same seed must agree exactly, and the
    ambient global RNG state must not influence the result.
    """
    # a non-degenerate paired sample so the discrete bootstrap genuinely resolves the endpoints
    x = [1.0, 3.0, 2.0, 5.0, 4.0, 7.0, 6.0, 9.0, 8.0, 10.0]
    y = [2.0, 2.5, 3.0, 4.0, 4.5, 6.5, 6.0, 9.5, 8.0, 10.5]

    a = correlate(x, y, seed=42, n_boot=500)
    b = correlate(x, y, seed=42, n_boot=500)
    assert isinstance(a, CorrelationResult) and isinstance(b, CorrelationResult)
    assert a.tau_ci == b.tau_ci  # byte-identical
    assert a.rho_ci == b.rho_ci

    # the CI brackets the point estimate
    assert a.tau_ci[0] <= a.kendall_tau <= a.tau_ci[1]
    assert a.rho_ci[0] <= a.spearman_rho <= a.rho_ci[1]

    # the module-global RNG state must NOT influence the result (proves it is not consulted)
    import random as _r

    _r.seed(0)
    c0 = correlate(x, y, seed=42, n_boot=500)
    _r.seed(999999)
    c1 = correlate(x, y, seed=42, n_boot=500)
    assert isinstance(c0, CorrelationResult) and isinstance(c1, CorrelationResult)
    assert c0.tau_ci == c1.tau_ci == a.tau_ci
    assert c0.rho_ci == c1.rho_ci == a.rho_ci

    # a different seed yields a different bootstrap draw (the seed is actually consulted)
    other = correlate(x, y, seed=7, n_boot=500)
    assert isinstance(other, CorrelationResult)
    assert (other.tau_ci, other.rho_ci) != (a.tau_ci, a.rho_ci)


def test_fr_027_caveat_non_strippable() -> None:
    """Empty caveat/note rejected; CORRELATION_CAVEAT names external validity + FR-027 — [UNIT-TEST].

    A ``CorrelationResult`` constructed with ``caveat=""`` raises ``ValueError``; a
    ``RealDataAbsent`` constructed with ``note=""`` likewise raises. ``CORRELATION_CAVEAT``
    mentions "external validity" and "FR-027" (synthetic agreement is NOT external validity).
    """
    assert "external validity" in CORRELATION_CAVEAT
    assert "FR-027" in CORRELATION_CAVEAT

    with pytest.raises(ValueError):
        CorrelationResult(
            n=5,
            kendall_tau=0.5,
            spearman_rho=0.5,
            tau_ci=(0.0, 1.0),
            rho_ci=(0.0, 1.0),
            bland_altman_mean_diff=0.0,
            bland_altman_limits=(-1.0, 1.0),
            caveat="",
        )
    with pytest.raises(ValueError):
        CorrelationResult(
            n=5,
            kendall_tau=0.5,
            spearman_rho=0.5,
            tau_ci=(0.0, 1.0),
            rho_ci=(0.0, 1.0),
            bland_altman_mean_diff=0.0,
            bland_altman_limits=(-1.0, 1.0),
            caveat="   ",  # whitespace-only is still empty
        )
    with pytest.raises(ValueError):
        RealDataAbsent(note="")


def test_nfr004_correlation_purity() -> None:
    """AST guard (NFR-004 / AX-002): correlation.py imports none of {time,uuid,datetime,secrets};
    ``random`` IS allowed but ONLY via ``random.Random(seed)`` — assert there is NO module-global
    ``random.<fn>`` call in the source (the bootstrap must own a local RNG) — mirrors
    ``stats/paired.py`` — [PROPERTY-TEST].
    """
    src = pathlib.Path(correlation_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)

    banned = {"time", "uuid", "datetime", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), f"correlation.py imports nondeterministic modules: {sorted(banned & imported)}"

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
    assert not offending, f"correlation.py must use only random.Random(seed), not the module-global RNG: {offending}"
