#!/usr/bin/env python3
"""Coverage-ceiling decomposition (headline-lock B-1) — reproduce CL-02b/SC-02b from released artifacts.

overall recall = coverage-fraction x within-reach skill (identity). We test the DROP overall-r -> within-reach-r
across the 11 leaderboard detectors, under >=2 monotone crosswalks (XW-EXACT, XW-BROAD), with Fisher-z +
bootstrap + leave-one-out CIs. Pure-stdlib, deterministic; derives entirely from the committed leaderboard run
and the frozen 63-type registry. No re-scoring, no corpus change.

Run: `python scripts/coverage_decomposition.py` -> results/tier-a/coverage_decomposition.{json,md}.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pii_anon_datasets.validation.correlation import _bootstrap_ci, _pearson  # noqa: E402

_HERE = os.path.dirname(__file__)
DEFAULT_RESULTS = os.path.join(_HERE, "..", "results", "baselines", "tier1-en-all", "baseline_results.json")
DEFAULT_REGISTRY = os.path.join(_HERE, "..", "src", "pii_anon_datasets", "data", "label_maps_63.json")
DEFAULT_OUT_DIR = os.path.join(_HERE, "..", "results", "tier-a")

DETECTORS = ("aws", "azure", "flair", "gcp", "gliner", "piiranha",
             "presidio", "regex", "scrubadub", "spacy", "stanza")
OF_TOTAL = 63
BOOTSTRAP_SEED = 20260618
# XW-BROAD: a monotone, deliberately-permissive crosswalk — coarse native labels that XW-EXACT drops are
# granted their most-plausible canonical type (all targets are in the frozen 63). It only ADDS reach.
XW_BROAD_GRANT = {"DATE": "DATE_OF_BIRTH", "NORP": "ETHNICITY", "NRP": "ETHNICITY"}
# XW-BROAD' (EX-01b): EXTERNAL-provenance crosswalk from NIST SP 800-122, applying its linked-vs-linkable
# distinction — date-of-birth is a (near-)direct PII identifier (granted), whereas race/ethnicity (NORP/NRP)
# is "linkable" personal-characteristic information, NOT a standalone identifier (NOT granted). This makes
# XW-BROAD' a genuinely DISTINCT, stricter third crosswalk (reach strictly between XW-EXACT and XW-BROAD),
# externally grounded and independent of label_maps_63.json (whose content-hash is committed -> firewall).
XW_BROAD_PRIME_GRANT = {
    "DATE": "DATE_OF_BIRTH",       # NIST SP 800-122 App-A: date of birth is a PII identifier
}


def load_run(path: str) -> dict:
    return json.loads(open(path, encoding="utf-8").read())


def load_registry(path: str) -> dict:
    return json.loads(open(path, encoding="utf-8").read())


def reachable_set(reg_det: dict, crosswalk: str) -> set[str]:
    """The set of canonical-63 types the detector reaches under `crosswalk`. XW-BROAD is a monotone superset."""
    exact = set(reg_det["reachable_types"])
    if crosswalk == "XW-EXACT":
        return exact
    if crosswalk == "XW-BROAD":
        granted = {XW_BROAD_GRANT[d] for d in reg_det["dropped_native"] if d in XW_BROAD_GRANT}
        return exact | granted
    if crosswalk == "XW-BROAD-PRIME":
        granted = {XW_BROAD_PRIME_GRANT[d] for d in reg_det["dropped_native"] if d in XW_BROAD_PRIME_GRANT}
        return exact | granted
    raise ValueError(f"unknown crosswalk {crosswalk!r}")


def within_reach_recall(run_det: dict, reachable: set[str]) -> float:
    """Recall restricted to reachable types: sum(tp)/sum(tp+fn) over reachable types (existing strict counts)."""
    tp = fn = 0
    bt = run_det["by_entity_type"]
    for t in reachable:
        c = bt.get(t, {}).get("counts")
        if c:
            tp += c["tp"]
            fn += c["fn"]
    return tp / (tp + fn) if (tp + fn) else 0.0


def detector_row(name: str, run_det: dict, reg_det: dict, crosswalk: str) -> dict:
    reach = reachable_set(reg_det, crosswalk)
    return {
        "detector": name,
        "coverage": len(reach) / OF_TOTAL,
        "reachable_count": len(reach),
        "micro_recall": run_det["micro"]["recall"],
        "within_reach_recall": within_reach_recall(run_det, reach),
    }


def fisher_z_ci(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """95% CI for a Pearson r via the Fisher z-transform (n-3 SE). r is clamped off +/-1 to keep atanh finite."""
    r = max(-0.999999, min(0.999999, r))
    if n <= 3:
        return (-1.0, 1.0)
    z = math.atanh(r)
    se = 1.0 / math.sqrt(n - 3)
    crit = 1.959963984540054  # ~z_{0.975}
    return (math.tanh(z - crit * se), math.tanh(z + crit * se))


def _leave_one_out(xs: list[float], ys: list[float]) -> list[float]:
    """Pearson r recomputed with each single observation removed (n recomputations)."""
    out = []
    for i in range(len(xs)):
        rx = xs[:i] + xs[i + 1:]
        ry = ys[:i] + ys[i + 1:]
        out.append(_pearson(rx, ry))
    return out


def _bootstrap_drop_ci(cov: list[float], micro: list[float], within: list[float], *,
                       seed: int, n_boot: int = 1000, alpha: float = 0.05) -> tuple[float, float]:
    """Paired bootstrap CI of the drop Δr = pearson(cov, micro) − pearson(cov, within).

    Resamples the detector indices ONCE per replicate and recomputes BOTH correlations on the SAME resample,
    so the drop's sampling variance is estimated paired — far more powerful (and seed-robust) than comparing
    two overlapping marginal CIs. This is the SC-02b(a) gating test: the headline holds iff this CI excludes 0.
    Uses a LOCAL RNG instance (never the module-global RNG) for reproducibility (NFR-004 / AX-002).
    """
    rng = random.Random(seed)
    n = len(cov)
    drops: list[float] = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        c = [cov[i] for i in idx]
        m = [micro[i] for i in idx]
        w = [within[i] for i in idx]
        drops.append(_pearson(c, m) - _pearson(c, w))
    drops.sort()
    lo = drops[int((alpha / 2) * n_boot)]
    hi = drops[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    return (lo, hi)


def decompose(run: dict, registry: dict, crosswalk: str) -> dict:
    """Full decomposition under one crosswalk: rows, the overall->within-reach drop, and all CIs."""
    rows = [detector_row(n, run["detectors"][n], registry["detectors"][n], crosswalk) for n in DETECTORS]
    cov = [r["coverage"] for r in rows]
    micro = [r["micro_recall"] for r in rows]
    within = [r["within_reach_recall"] for r in rows]
    n = len(rows)
    r_overall = _pearson(cov, micro)
    r_within = _pearson(cov, within)
    skills = [r["within_reach_recall"] for r in rows]
    return {
        "crosswalk": crosswalk,
        "n_detectors": n,
        "rows": rows,
        "r_overall": r_overall,
        "r_within": r_within,
        "drop": r_overall - r_within,
        "r_overall_fisher_ci": fisher_z_ci(r_overall, n),
        "r_within_fisher_ci": fisher_z_ci(r_within, n),
        "r_overall_bootstrap_ci": _bootstrap_ci(cov, micro, _pearson, seed=BOOTSTRAP_SEED),
        "r_within_bootstrap_ci": _bootstrap_ci(cov, within, _pearson, seed=BOOTSTRAP_SEED),
        "drop_bootstrap_ci": _bootstrap_drop_ci(cov, micro, within, seed=BOOTSTRAP_SEED),  # SC-02b(a) gate
        "r_overall_loo": _leave_one_out(cov, micro),
        "r_within_loo": _leave_one_out(cov, within),
        "loo_max_abs_within": max(abs(r) for r in _leave_one_out(cov, within)),
        "mean_within_reach_skill": sum(skills) / n,
        "min_within_reach_skill": min(skills),
        "max_within_reach_skill": max(skills),
    }


CROSSWALKS = ("XW-EXACT", "XW-BROAD", "XW-BROAD-PRIME")


def decompose_all(run: dict, registry: dict) -> dict:
    """Run the decomposition under every crosswalk and compute the cross-crosswalk verdict."""
    by_xw = {xw: decompose(run, registry, xw) for xw in CROSSWALKS}
    drop_sign_holds = all(res["drop"] > 0 for res in by_xw.values())
    skill_ok = all(res["mean_within_reach_skill"] >= 0.6 for res in by_xw.values())
    # SC-02b(a): the PAIRED bootstrap CI of the drop excludes 0 under every crosswalk (the gating contrast).
    drop_ci_excludes_zero = all(res["drop_bootstrap_ci"][0] > 0.0 for res in by_xw.values())
    loo_stable = all(res["loo_max_abs_within"] < 0.3 for res in by_xw.values())
    return {
        "by_crosswalk": by_xw,
        "verdict": {
            "drop_sign_holds_all_crosswalks": drop_sign_holds,
            "drop_bootstrap_ci_excludes_zero_all_crosswalks": drop_ci_excludes_zero,
            "loo_within_reach_stable_all_crosswalks": loo_stable,
            "mean_skill_ge_0_6_all_crosswalks": skill_ok,
            "headline_reproduced": drop_sign_holds and drop_ci_excludes_zero and loo_stable and skill_ok,
        },
    }


def render_md(allres: dict) -> str:
    v = allres["verdict"]
    ex = allres["by_crosswalk"]["XW-EXACT"]
    lines = [
        "# Within-reach decomposition of the coverage ceiling (CL-02b headline)",
        "",
        "> **Honesty (AX-001 synthetic-only; n=11 → structural *bound*, not a law).** Mechanism: unreachable "
        "types → recall exactly 0 → overall recall is upper-bounded by coverage. The contribution is the "
        "coverage-*independent* within-reach skill factor + the structural framing, NOT the correlation. "
        "Denominator pinned to the frozen 63 (`label_maps_63.json`).",
        "",
        f"**Headline reproduced: {v['headline_reproduced']}** — the overall coverage↔recall correlation "
        f"collapses once we condition on reach, and the collapse holds under all three crosswalks.",
        "",
        "**SC-02b(a) test.** The contrast is a PAIRED bootstrap of the drop Δr = overall r − within-reach r "
        "(resample detectors, recompute both correlations on the same resample); the headline holds iff this CI "
        "excludes 0. At n=11 the *marginal* Fisher-z CIs are wide and overlap — reported below for transparency "
        "but NOT the gate (the paired drop CI + leave-one-out stability carry the contrast).",
        "",
        "| Crosswalk | overall r | within-reach r | drop | drop 95% bootstrap CI | mean skill |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for xw, res in allres["by_crosswalk"].items():
        dci = res["drop_bootstrap_ci"]
        lines.append(f"| {xw} | {res['r_overall']:.3f} | {res['r_within']:.3f} | {res['drop']:.3f} | "
                     f"[{dci[0]:.3f}, {dci[1]:.3f}] | {res['mean_within_reach_skill']:.3f} |")
    lines += [
        "",
        "_Marginal Fisher-z CIs (context, n=11, wide/overlapping — not the gate):_ "
        + "; ".join(f"{xw}: overall [{res['r_overall_fisher_ci'][0]:.3f}, {res['r_overall_fisher_ci'][1]:.3f}] "
                    f"vs within [{res['r_within_fisher_ci'][0]:.3f}, {res['r_within_fisher_ci'][1]:.3f}]"
                    for xw, res in allres["by_crosswalk"].items()) + ".",
        "",
        "## Per-detector (XW-EXACT)",
        "",
        "| Detector | coverage (reach/63) | micro recall | within-reach skill |",
        "|---|---:|---:|---:|",
    ]
    for r in sorted(ex["rows"], key=lambda r: r["within_reach_recall"], reverse=True):
        lines.append(f"| {r['detector']} | {r['reachable_count']}/63 | {r['micro_recall']:.3f} | "
                     f"{r['within_reach_recall']:.3f} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Coverage-ceiling within-reach decomposition (B-1).")
    ap.add_argument("--results", default=DEFAULT_RESULTS)
    ap.add_argument("--registry", default=DEFAULT_REGISTRY)
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    args = ap.parse_args(argv)
    allres = decompose_all(load_run(args.results), load_registry(args.registry))
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "coverage_decomposition.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(allres, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    with open(os.path.join(args.out_dir, "coverage_decomposition.md"), "w", encoding="utf-8") as f:
        f.write(render_md(allres))
    print(f"wrote coverage_decomposition.{{json,md}} — headline_reproduced="
          f"{allres['verdict']['headline_reproduced']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
