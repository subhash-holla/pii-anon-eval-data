"""Tests for the headline-lock sub-project: B-2 frozen label-map registry + B-1 coverage decomposition."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_label_map_registry as blmr  # noqa: E402
import coverage_decomposition as cd  # noqa: E402

LEADERBOARD = ("aws", "azure", "flair", "gcp", "gliner", "piiranha",
               "presidio", "regex", "scrubadub", "spacy", "stanza")
ART9 = ("SEXUAL_ORIENTATION", "TRADE_UNION_MEMBERSHIP", "GENETIC_DATA")


def test_canonical_63_is_66_minus_art9():
    c63 = blmr.canonical_63()
    assert len(c63) == 63
    assert not (set(ART9) & set(c63)), "Art-9 types must be excluded from the frozen 63"


def test_registry_has_11_coi_clean_detectors():
    reg = blmr.build_registry(blmr.DEFAULT_RESULTS)
    assert reg["of_total"] == 63
    assert "pii_anon" not in reg["detectors"], "own system excluded for COI"
    assert tuple(sorted(reg["detectors"])) == tuple(sorted(LEADERBOARD))


def test_registry_reachable_matches_run_coverage():
    reg = blmr.build_registry(blmr.DEFAULT_RESULTS)
    run = json.loads(Path(blmr.DEFAULT_RESULTS).read_text(encoding="utf-8"))["detectors"]
    for name, block in reg["detectors"].items():
        assert block["reachable_types"] == sorted(run[name]["coverage"]["reachable_types"])
        assert block["reachable_count"] == run[name]["coverage"]["reachable"]


def test_overall_r_reproduces_0797():
    run = cd.load_run(cd.DEFAULT_RESULTS)
    reg = cd.load_registry(cd.DEFAULT_REGISTRY)
    rows = [cd.detector_row(n, run["detectors"][n], reg["detectors"][n], "XW-EXACT") for n in cd.DETECTORS]
    r_overall = cd._pearson([r["coverage"] for r in rows], [r["micro_recall"] for r in rows])
    assert round(r_overall, 3) == 0.797


def test_within_reach_recall_isolates_skill():
    run = cd.load_run(cd.DEFAULT_RESULTS)
    reg = cd.load_registry(cd.DEFAULT_REGISTRY)
    rows = {r["detector"]: r for r in
            (cd.detector_row(n, run["detectors"][n], reg["detectors"][n], "XW-EXACT") for n in cd.DETECTORS)}
    # within-reach recall >= overall recall for every detector (unreachable types only drag overall down)
    for name, r in rows.items():
        assert r["within_reach_recall"] >= r["micro_recall"] - 1e-9, name
    # SC-02b published spread: AWS/regex high, scrubadub low
    assert rows["aws"]["within_reach_recall"] >= 0.85
    assert rows["scrubadub"]["within_reach_recall"] <= 0.45


def test_within_reach_drop_holds_under_xw_exact():
    res = cd.decompose(cd.load_run(cd.DEFAULT_RESULTS), cd.load_registry(cd.DEFAULT_REGISTRY), "XW-EXACT")
    assert round(res["r_overall"], 3) == 0.797
    assert abs(res["r_within"]) < 0.3, "within-reach r must be near zero (decoupled)"
    assert res["drop"] > 0.5, "the drop must be large"
    # SC-02b(a) operationalized as a PAIRED bootstrap of the drop excluding 0 (NOT a marginal-CI
    # comparison: at n=11 the marginal Fisher-z CIs overlap; the paired bootstrap of Δr is the
    # powerful, seed-robust test SC-02b prescribes — "test the drop via bootstrap/LOO").
    assert res["drop_bootstrap_ci"][0] > 0.0, "paired bootstrap CI of the drop must exclude 0"
    # leave-one-out stability: within-reach r stays near zero under every single-detector removal
    assert max(abs(r) for r in res["r_within_loo"]) < 0.3


def test_fisher_z_ci_is_symmetric_in_z():
    lo, hi = cd.fisher_z_ci(0.5, n=11)
    assert lo < 0.5 < hi


def test_drop_bootstrap_ci_excludes_zero_and_is_seed_deterministic():
    run, reg = cd.load_run(cd.DEFAULT_RESULTS), cd.load_registry(cd.DEFAULT_REGISTRY)
    a = cd.decompose(run, reg, "XW-EXACT")["drop_bootstrap_ci"]
    b = cd.decompose(run, reg, "XW-EXACT")["drop_bootstrap_ci"]
    assert a == b, "fixed seed -> identical paired-bootstrap CI"
    assert a[0] > 0.0


def test_xw_broad_is_monotone_superset_of_xw_exact():
    reg = cd.load_registry(cd.DEFAULT_REGISTRY)
    for name, det in reg["detectors"].items():
        exact = cd.reachable_set(det, "XW-EXACT")
        broad = cd.reachable_set(det, "XW-BROAD")
        assert exact <= broad, f"{name}: XW-BROAD must be a superset of XW-EXACT (monotone)"
    # the grant must actually move at least one low-reach detector (else it is not an independent crosswalk)
    spacy = reg["detectors"]["spacy"]
    assert cd.reachable_set(spacy, "XW-BROAD") > cd.reachable_set(spacy, "XW-EXACT")


def test_drop_holds_in_sign_under_both_crosswalks():
    allres = cd.decompose_all(cd.load_run(cd.DEFAULT_RESULTS), cd.load_registry(cd.DEFAULT_REGISTRY))
    assert set(allres["by_crosswalk"]) == {"XW-EXACT", "XW-BROAD", "XW-BROAD-PRIME"}
    for xw, res in allres["by_crosswalk"].items():
        assert res["drop"] > 0, f"{xw}: decoupling drop must stay positive (sign holds)"
    assert allres["verdict"]["headline_reproduced"] is True


def test_mean_within_reach_skill_floor():
    allres = cd.decompose_all(cd.load_run(cd.DEFAULT_RESULTS), cd.load_registry(cd.DEFAULT_REGISTRY))
    assert allres["by_crosswalk"]["XW-EXACT"]["mean_within_reach_skill"] >= 0.6


def test_outputs_written_and_deterministic(tmp_path):
    rc = cd.main(["--out-dir", str(tmp_path)])
    assert rc == 0
    j1 = (tmp_path / "coverage_decomposition.json").read_text(encoding="utf-8")
    md1 = (tmp_path / "coverage_decomposition.md").read_text(encoding="utf-8")
    assert "headline_reproduced" in j1
    assert "Within-reach decomposition" in md1 and "0.797" in md1
    cd.main(["--out-dir", str(tmp_path)])  # rerun
    assert (tmp_path / "coverage_decomposition.json").read_text(encoding="utf-8") == j1, "must be deterministic"


def test_denominator_is_frozen_at_63_decoupled_from_live_taxonomy(monkeypatch):
    """Spec §5 guard (injection-not-import): the headline denominator is the frozen 63, NOT the live taxonomy.

    Three layers of protection so the decoupling cannot silently regress:
    1. value — `cd.OF_TOTAL == 63` while the live taxonomy is 66;
    2. structural — coverage_decomposition.py never imports the taxonomy (so it *cannot* derive 63 from it,
       even after a future taxonomy bump). A regression like `OF_TOTAL = taxonomy.ENTITY_TYPE_COUNT - 3`
       would re-introduce a taxonomy import and trip this check;
    3. artifact — the committed registry stays pinned at of_total=63 even when the live taxonomy grows.
    """
    import pii_anon_datasets.taxonomy as tx
    assert tx.ENTITY_TYPE_COUNT == 66 and cd.OF_TOTAL == 63  # live 66, headline frozen at 63

    # (2) structural: the estimand module must not couple to the live taxonomy at all
    src = (ROOT / "scripts" / "coverage_decomposition.py").read_text(encoding="utf-8")
    assert "OF_TOTAL = 63" in src, "the denominator must be a hard literal"
    assert "taxonomy" not in src, "coverage_decomposition must not import/reference the live taxonomy"

    # (1) every coverage denominator is 63 (reachable_count == round(coverage * 63))
    res = cd.decompose(cd.load_run(cd.DEFAULT_RESULTS), cd.load_registry(cd.DEFAULT_REGISTRY), "XW-EXACT")
    for r in res["rows"]:
        assert round(r["coverage"] * 63) == r["reachable_count"]

    # (3) grow the LIVE taxonomy to a 67th type; the frozen artifact + denominator are unmoved
    monkeypatch.setattr(tx, "CANONICAL_ENTITY_TYPES",
                        frozenset(set(tx.CANONICAL_ENTITY_TYPES) | {"FAKE_67TH_TYPE"}))
    assert cd.OF_TOTAL == 63, "B-1 denominator must be immune to taxonomy drift"
    reg = json.loads((ROOT / "src" / "pii_anon_datasets" / "data" / "label_maps_63.json")
                     .read_text(encoding="utf-8"))
    assert reg["of_total"] == 63 and len(reg["canonical_63"]) == 63
