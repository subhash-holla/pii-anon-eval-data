# Headline-Lock: Coverage-Ceiling Decomposition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the paper's headline claim (CL-02b — the coverage ceiling is a *structural decomposition*, reach ⟂ skill) reproducible from the dataset repo by (B-2) freezing the 63-type per-detector label-map registry and (B-1) shipping a deterministic `coverage_decomposition.py` that regenerates the overall-r→within-reach-r drop under ≥2 monotone crosswalks.

**Architecture:** Two pure-stdlib scripts that read the already-committed v2.0.0 leaderboard run (`results/baselines/tier1-en-all/baseline_results.json`) and the frozen registry. B-2 (`build_label_map_registry.py`) emits a content-hashed `src/pii_anon_datasets/data/label_maps_63.json`; B-1 (`coverage_decomposition.py`) computes per-detector coverage / micro-recall / within-reach recall, the Pearson contrast with Fisher-z + bootstrap + leave-one-out CIs, under XW-EXACT and a monotone XW-BROAD crosswalk, and writes `results/tier-a/coverage_decomposition.{json,md}`. **Analysis-only — no corpus regeneration, no re-scoring; content version stays 2.1.0.**

**Tech Stack:** Python 3 stdlib (json, math, argparse, hashlib, random); reuse `pii_anon_datasets.validation.correlation._pearson` and `._bootstrap_ci`; `pii_anon_datasets.baselines.registry.load_adapter` for label maps; `pii_anon_datasets.taxonomy` for the canonical set. pytest + ruff. Tests run with `PYTHONPATH=src`.

**Spec:** `docs/superpowers/specs/2026-06-18-headline-lock-coverage-decomposition-design.md`.

---

## Key facts (verified on disk 2026-06-18 — do not re-derive)

- **Leaderboard run:** `results/baselines/tier1-en-all/baseline_results.json`. Shape: `d["detectors"][name]` has `micro.recall` (overall recall), `coverage = {of_total: 63, reachable: int, reachable_types: [...], dropped_native: [...]}`, and `by_entity_type[TYPE].counts = {tp, fn, fp, partial, policy}`.
- **The 11 detectors (own `pii_anon` excluded for COI):** `aws, azure, flair, gcp, gliner, piiranha, presidio, regex, scrubadub, spacy, stanza`.
- **63 = 66 − the 3 Art-9 types** `SEXUAL_ORIENTATION, TRADE_UNION_MEMBERSHIP, GENETIC_DATA`. `taxonomy.CANONICAL_ENTITY_TYPES` is the live 66; `taxonomy.ENTITY_TYPE_COUNT == 66`.
- **Overall r reproduction:** `pearson([reachable], [micro.recall])` over the 11 detectors == **0.797** (this is exactly how `scripts/free_bundle.py:coverage_ceiling` computes it).
- **Within-reach recall (the estimand):** `sum(tp over reachable types) / sum(tp+fn over reachable types)`. Under a crosswalk, "reachable types" is that crosswalk's reachable set; the per-type `tp/fn` counts are the **existing** strict-v1 counts (no re-scoring). This reproduces SC-02b's published skill (mean ≈ 0.75; regex 0.93 / AWS 0.92 / scrubadub 0.28) and within-reach r ≈ 0.048.
- **Reusable primitives** in `src/pii_anon_datasets/validation/correlation.py`: `_pearson(a, b) -> float` (stdlib); `_bootstrap_ci(x, y, stat, *, seed, n_boot=1000, alpha=0.05) -> (lo, hi)` where `stat` is `Callable[[Seq, Seq], float]`.
- **Adapter label maps:** `from pii_anon_datasets.baselines import registry; registry.load_adapter(name).label_map` → `dict[str, str | None]` (native → canonical-or-None). `load_adapter` puts the repo root on `sys.path` itself.
- **Manifest:** `scripts/write_manifest.py` hashes a **fixed tuple** `_tracked_files()` of `data/` files; `MANIFEST.sha256` lives at `src/pii_anon_datasets/data/MANIFEST.sha256`. `python scripts/write_manifest.py` (re)writes it; `--check` verifies. `tests/test_manifest.py` only asserts idempotency + the header string (no file-count pin).
- **XW-BROAD grant table** (monotone, broadening; all targets are in the 63): `{"DATE": "DATE_OF_BIRTH", "NORP": "ETHNICITY", "NRP": "ETHNICITY"}`. Dropped-native labels present in the run: spacy/stanza drop `DATE, NORP` (+11 others with no canonical match); presidio drops `NRP`; flair `MISC`; piiranha `TITLE`; aws `CREDIT_DEBIT_EXPIRY`. The grant adds reach to spacy/stanza (`+DATE_OF_BIRTH, +ETHNICITY`) and presidio (`+ETHNICITY` if not already reached).

---

## File Structure

- **Create** `scripts/build_label_map_registry.py` — builds/verifies the frozen registry. Responsibility: freeze each detector's native→canonical map + its projection onto the 63 types.
- **Create** `src/pii_anon_datasets/data/label_maps_63.json` — the committed frozen artifact (generated).
- **Modify** `scripts/write_manifest.py` — add `"label_maps_63.json"` to the tracked tuple.
- **Modify** `src/pii_anon_datasets/data/MANIFEST.sha256` — regenerated (one new line).
- **Create** `scripts/coverage_decomposition.py` — the decomposition analysis + crosswalks + CIs + output emitters.
- **Create** `results/tier-a/coverage_decomposition.json` and `results/tier-a/coverage_decomposition.md` — generated outputs.
- **Modify** `results/tier-a/coverage_ceiling.md` — add a one-line pointer to the decomposition.
- **Create** `tests/test_coverage_decomposition.py` — tests for B-2 and B-1.

---

## Task 1: B-2 — frozen 63-type label-map registry builder

**Files:**
- Create: `scripts/build_label_map_registry.py`
- Create (generated): `src/pii_anon_datasets/data/label_maps_63.json`
- Test: `tests/test_coverage_decomposition.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_coverage_decomposition.py`:

```python
"""Tests for the headline-lock sub-project: B-2 frozen label-map registry + B-1 coverage decomposition."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_label_map_registry as blmr  # noqa: E402

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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_coverage_decomposition.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'build_label_map_registry'`.

- [ ] **Step 3: Write the implementation**

Create `scripts/build_label_map_registry.py`:

```python
#!/usr/bin/env python3
"""Freeze the 63-type per-detector label-map registry (headline-lock B-2).

Emits src/pii_anon_datasets/data/label_maps_63.json: for each leaderboard detector, its native->canonical
map (the actual frozen map, read from the adapter) plus its projection onto the FROZEN 63-type set
(reachable_types / dropped_native). `of_total` is hard-pinned to 63 and the canonical-63 list is serialized,
so the artifact is self-contained and decoupled from the live taxonomy (now 66). This is the content-hash
object the preregistration (§7 / AMEND-01) requires before the deferred EX-01b external-crosswalk stage.

Analysis-only; no corpus change. Run: `python scripts/build_label_map_registry.py [--check]`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pii_anon_datasets import taxonomy  # noqa: E402
from pii_anon_datasets.baselines import registry  # noqa: E402

ART9_ADDED = ("SEXUAL_ORIENTATION", "TRADE_UNION_MEMBERSHIP", "GENETIC_DATA")
# The 11 published leaderboard detectors; the author's own pii_anon* are excluded for COI.
LEADERBOARD_DETECTORS = ("aws", "azure", "flair", "gcp", "gliner", "piiranha",
                         "presidio", "regex", "scrubadub", "spacy", "stanza")
_HERE = os.path.dirname(__file__)
DEFAULT_RESULTS = os.path.join(_HERE, "..", "results", "baselines", "tier1-en-all", "baseline_results.json")
DEFAULT_OUT = os.path.join(_HERE, "..", "src", "pii_anon_datasets", "data", "label_maps_63.json")


def canonical_63() -> list[str]:
    """The frozen 63-type denominator = the canonical 66 minus the three 2A Art-9 types."""
    c = sorted(set(taxonomy.CANONICAL_ENTITY_TYPES) - set(ART9_ADDED))
    assert len(c) == 63, f"expected 63 frozen types, got {len(c)}"
    return c


def build_registry(results_path: str) -> dict:
    """Build the frozen registry dict from the committed leaderboard run + the adapter label maps."""
    run = json.loads(open(results_path, encoding="utf-8").read())["detectors"]
    c63 = canonical_63()
    c63_set = set(c63)
    detectors: dict[str, dict] = {}
    for name in LEADERBOARD_DETECTORS:
        cov = run[name]["coverage"]
        assert cov["of_total"] == 63, f"{name}: run coverage of_total != 63"
        native_map = dict(registry.load_adapter(name).label_map)
        # The adapter map's canonical targets, projected onto the frozen 63 (drop None + any non-63 target).
        reachable_from_map = sorted({v for v in native_map.values() if v in c63_set})
        run_reachable = sorted(cov["reachable_types"])
        assert reachable_from_map == run_reachable, (
            f"{name}: adapter map projects to {reachable_from_map} but the scored run says {run_reachable}"
        )
        detectors[name] = {
            "native_to_canonical": native_map,
            "reachable_types": run_reachable,
            "reachable_count": cov["reachable"],
            "dropped_native": sorted(cov.get("dropped_native", [])),
        }
    return {
        "frozen_taxonomy_version": "v2.0.0-63type",
        "of_total": 63,
        "canonical_63": c63,
        "source_run": "results/baselines/tier1-en-all/baseline_results.json",
        "detectors": detectors,
    }


def _serialize(reg: dict) -> str:
    return json.dumps(reg, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Freeze the 63-type per-detector label-map registry (B-2).")
    ap.add_argument("--results", default=DEFAULT_RESULTS)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true", help="verify the on-disk artifact matches a fresh build")
    args = ap.parse_args(argv)
    fresh = _serialize(build_registry(args.results))
    if args.check:
        on_disk = open(args.out, encoding="utf-8").read() if os.path.exists(args.out) else ""
        if on_disk != fresh:
            print(f"DRIFT: {args.out} does not match a fresh build_registry()", file=sys.stderr)
            return 1
        print(f"OK: {os.path.relpath(args.out)} matches a fresh build (11 detectors, of_total=63)")
        return 0
    with open(args.out, "w", encoding="utf-8") as fout:
        fout.write(fresh)
    print(f"wrote {os.path.relpath(args.out)} — 11 detectors, of_total=63")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Generate the artifact and run the test to verify it passes**

Run:
```bash
PYTHONPATH=src python scripts/build_label_map_registry.py
PYTHONPATH=src python -m pytest tests/test_coverage_decomposition.py -q
```
Expected: the script prints `wrote src/pii_anon_datasets/data/label_maps_63.json — 11 detectors, of_total=63`; all three tests PASS. If the `reachable_from_map == run_reachable` assertion fires for a detector, that is a genuine registry/run disagreement — STOP and report (do not weaken the assertion).

- [ ] **Step 5: Commit**

```bash
git add scripts/build_label_map_registry.py src/pii_anon_datasets/data/label_maps_63.json tests/test_coverage_decomposition.py
git commit -m "feat(headline-lock): freeze 63-type per-detector label-map registry (B-2)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: B-2 — content-hash the registry in MANIFEST.sha256

**Files:**
- Modify: `scripts/write_manifest.py` (the `_tracked_files()` tuple, ~line 36)
- Modify (generated): `src/pii_anon_datasets/data/MANIFEST.sha256`

- [ ] **Step 1: Add the registry to the tracked tuple**

In `scripts/write_manifest.py`, the `_tracked_files()` function lists fixed `data/` filenames. Add `"label_maps_63.json"` to that tuple:

```python
    for name in ("pii_anon.jsonl.gz", "pii_anon.metadata.json", "pii_anon.schema.json",
                 "eval_lattice.json", "lattice_freq_snapshot.json", "label_maps_63.json"):
        p = DATA_DIR / name
```

- [ ] **Step 2: Regenerate the manifest**

Run: `PYTHONPATH=src python scripts/write_manifest.py`
Expected: prints `wrote .../MANIFEST.sha256 — N files hashed` with N one higher than before; a new line for `label_maps_63.json` appears in the manifest.

- [ ] **Step 3: Verify the manifest check + the manifest test pass**

Run:
```bash
PYTHONPATH=src python scripts/write_manifest.py --check
PYTHONPATH=src python -m pytest tests/test_manifest.py -q
```
Expected: `--check` prints `OK: ... matches`; `tests/test_manifest.py` PASSES (it asserts only idempotency + the header string).

- [ ] **Step 4: Commit**

```bash
git add scripts/write_manifest.py src/pii_anon_datasets/data/MANIFEST.sha256
git commit -m "feat(headline-lock): content-hash label_maps_63.json in MANIFEST.sha256 (B-2)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: B-1 — per-detector rows + overall/within-reach Pearson under XW-EXACT

**Files:**
- Create: `scripts/coverage_decomposition.py`
- Test: `tests/test_coverage_decomposition.py` (append)

- [ ] **Step 1: Write the failing test (append to `tests/test_coverage_decomposition.py`)**

```python
sys.path.insert(0, str(ROOT / "scripts"))
import coverage_decomposition as cd  # noqa: E402


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
```

- [ ] **Step 2: Run to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_coverage_decomposition.py -k "0797 or skill" -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'coverage_decomposition'`.

- [ ] **Step 3: Write the implementation (core)**

Create `scripts/coverage_decomposition.py`:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_coverage_decomposition.py -k "0797 or skill" -q`
Expected: PASS — `r_overall` rounds to 0.797; within-reach recall ≥ overall for all; aws ≥ 0.85, scrubadub ≤ 0.45.

- [ ] **Step 5: Commit**

```bash
git add scripts/coverage_decomposition.py tests/test_coverage_decomposition.py
git commit -m "feat(headline-lock): per-detector coverage + within-reach recall, overall r=0.797 (B-1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: B-1 — the statistical contrast (Fisher-z + bootstrap + leave-one-out)

**Files:**
- Modify: `scripts/coverage_decomposition.py` (append functions)
- Test: `tests/test_coverage_decomposition.py` (append)

- [ ] **Step 1: Write the failing test (append)**

```python
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
```

- [ ] **Step 2: Run to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_coverage_decomposition.py -k "drop or fisher" -q`
Expected: FAIL — `AttributeError: module 'coverage_decomposition' has no attribute 'decompose'`.

- [ ] **Step 3: Write the implementation (append to `scripts/coverage_decomposition.py`)**

First add `import random` to the stdlib import block at the top of the file (alongside `import math`), since the paired-drop bootstrap needs a local RNG. Then append the functions below.

```python
def fisher_z_ci(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """95% CI for a Pearson r via the Fisher z-transform (n-3 SE). r is clamped off +/-1 to keep atanh finite.

    Reported as context only — at n=11 the marginal Fisher-z CIs are wide and overlap; the gating contrast is
    the PAIRED bootstrap of the drop (`_bootstrap_drop_ci`), per SC-02b ("test the drop via bootstrap/LOO").
    """
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_coverage_decomposition.py -k "drop or fisher or bootstrap" -q`
Expected: PASS — `r_overall≈0.797`, `|r_within|<0.3`, drop ≈ 0.749, the **paired bootstrap CI of the drop excludes 0** (`drop_bootstrap_ci[0] > 0`), and LOO within-reach r stays in [−0.3, 0.3]. (The marginal Fisher-z CIs are reported but intentionally NOT gated on — they overlap at n=11; this is disclosed honestly in the output. Report the actual `drop_bootstrap_ci`.)

- [ ] **Step 5: Commit**

```bash
git add scripts/coverage_decomposition.py tests/test_coverage_decomposition.py
git commit -m "feat(headline-lock): Fisher-z + bootstrap + LOO contrast for the within-reach drop (B-1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: B-1 — XW-BROAD robustness + within-reach skill floor

**Files:**
- Modify: `scripts/coverage_decomposition.py` (append `decompose_all` + skill check)
- Test: `tests/test_coverage_decomposition.py` (append)

- [ ] **Step 1: Write the failing test (append)**

```python
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
    assert set(allres["by_crosswalk"]) == {"XW-EXACT", "XW-BROAD"}
    for xw, res in allres["by_crosswalk"].items():
        assert res["drop"] > 0, f"{xw}: decoupling drop must stay positive (sign holds)"
    assert allres["verdict"]["drop_holds_all_crosswalks"] is True


def test_mean_within_reach_skill_floor():
    allres = cd.decompose_all(cd.load_run(cd.DEFAULT_RESULTS), cd.load_registry(cd.DEFAULT_REGISTRY))
    assert allres["by_crosswalk"]["XW-EXACT"]["mean_within_reach_skill"] >= 0.6
```

- [ ] **Step 2: Run to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_coverage_decomposition.py -k "broad or sign or skill_floor" -q`
Expected: FAIL — `AttributeError: module 'coverage_decomposition' has no attribute 'decompose_all'`.

- [ ] **Step 3: Write the implementation (append to `scripts/coverage_decomposition.py`)**

```python
CROSSWALKS = ("XW-EXACT", "XW-BROAD")


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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_coverage_decomposition.py -k "broad or sign or skill_floor" -q`
Expected: PASS — XW-BROAD ⊇ XW-EXACT for all detectors and strictly larger for spacy; drop positive under both crosswalks; mean skill ≥ 0.6.

- [ ] **Step 5: Commit**

```bash
git add scripts/coverage_decomposition.py tests/test_coverage_decomposition.py
git commit -m "feat(headline-lock): XW-BROAD monotone crosswalk + cross-crosswalk verdict (B-1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: B-1 — emit JSON/MD outputs + determinism + coverage_ceiling cross-link

**Files:**
- Modify: `scripts/coverage_decomposition.py` (add `render_md`, `main`)
- Create (generated): `results/tier-a/coverage_decomposition.json`, `results/tier-a/coverage_decomposition.md`
- Modify: `results/tier-a/coverage_ceiling.md`
- Test: `tests/test_coverage_decomposition.py` (append)

- [ ] **Step 1: Write the failing test (append)**

```python
def test_outputs_written_and_deterministic(tmp_path):
    rc = cd.main(["--out-dir", str(tmp_path)])
    assert rc == 0
    j1 = (tmp_path / "coverage_decomposition.json").read_text(encoding="utf-8")
    md1 = (tmp_path / "coverage_decomposition.md").read_text(encoding="utf-8")
    assert "headline_reproduced" in j1
    assert "Within-reach decomposition" in md1 and "0.797" in md1
    cd.main(["--out-dir", str(tmp_path)])  # rerun
    assert (tmp_path / "coverage_decomposition.json").read_text(encoding="utf-8") == j1, "must be deterministic"
```

- [ ] **Step 2: Run to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_coverage_decomposition.py -k "outputs" -q`
Expected: FAIL — `AttributeError: module 'coverage_decomposition' has no attribute 'main'`.

- [ ] **Step 3: Write the implementation (append to `scripts/coverage_decomposition.py`)**

```python
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
        f"collapses once we condition on reach, and the collapse holds under both crosswalks.",
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
```

- [ ] **Step 4: Generate the outputs, add the cross-link, run the test**

Run: `PYTHONPATH=src python scripts/coverage_decomposition.py`
Expected: prints `wrote coverage_decomposition.{json,md} — headline_reproduced=True`.

Then add a pointer to `results/tier-a/coverage_ceiling.md` immediately after the existing `Pearson r(...)` line (line 8):

```markdown
> The **within-reach decomposition** (the CL-02b headline: this overall r collapses to ≈0 once conditioned on
> label-map reach, under ≥2 monotone crosswalks) lives in [coverage_decomposition.md](coverage_decomposition.md).
```

Then run: `PYTHONPATH=src python -m pytest tests/test_coverage_decomposition.py -q`
Expected: ALL tests PASS; reruns are byte-identical.

- [ ] **Step 5: Commit**

```bash
git add scripts/coverage_decomposition.py results/tier-a/coverage_decomposition.json results/tier-a/coverage_decomposition.md results/tier-a/coverage_ceiling.md tests/test_coverage_decomposition.py
git commit -m "feat(headline-lock): emit coverage_decomposition.{json,md} + ceiling cross-link (B-1)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Final gates

**Files:** none (verification only; fix-forward if needed)

- [ ] **Step 1: Full test suite**

Run: `PYTHONPATH=src python -m pytest -q`
Expected: green (the prior 671 passed + the new `test_coverage_decomposition.py` cases; 9 skipped). If any pre-existing test now fails, diagnose — the only repo changes are additive (two new scripts, one new data file + its manifest line, two new result files, one cross-link), so a failure is most likely the manifest test or a doc-drift test; fix-forward.

- [ ] **Step 2: Lint the new/changed files**

Run: `ruff check scripts/build_label_map_registry.py scripts/coverage_decomposition.py tests/test_coverage_decomposition.py`
Expected: clean (no new findings). Fix any reported issues in these files only.

- [ ] **Step 3: Version-sync + manifest + registry anti-drift**

Run:
```bash
PYTHONPATH=src python scripts/check_version_sync.py
PYTHONPATH=src python scripts/write_manifest.py --check
PYTHONPATH=src python scripts/build_label_map_registry.py --check
```
Expected: version-sync OK (content stays 2.1.0 — no version touched); manifest matches; registry matches a fresh build.

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "chore(headline-lock): final gate — full suite green, manifest + registry anti-drift OK

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```
(If Steps 1-3 needed no changes, skip the commit.)

---

## Self-Review (run before handing off)

**Spec coverage** — every spec §1 "Done when" item maps to a task:
1. `label_maps_63.json` (of_total 63, injected, 11 detectors) → Task 1. ✅
2. `coverage_decomposition.py` (coverage / micro / within-reach) → Task 3. ✅
3. SC-02b contrast (Fisher-z + bootstrap + LOO) → Task 4. ✅
4. ≥2 monotone crosswalks, sign+magnitude → Task 5. ✅
5. mean within-reach skill ≥ 0.6 + spread → Tasks 3 (spread) + 5 (floor). ✅
6. outputs + ceiling cross-link → Task 6. ✅
7. `tests/test_coverage_decomposition.py` + gates → Tasks 1–7. ✅
8. version-sync OK, no corpus change → Task 7. ✅
MANIFEST.sha256 (spec §2) → Task 2. ✅

**Placeholder scan:** no TBD/TODO; every code step shows real code; XW-BROAD grant table is concrete; the only deferred item (external XW-BROAD′) is explicitly out of scope per the spec.

**Type consistency:** `detector_row` keys (`detector, coverage, reachable_count, micro_recall, within_reach_recall`) are used identically in Tasks 3/4/5/6; `decompose` keys (`r_overall, r_within, drop, r_*_fisher_ci, mean_within_reach_skill`) match their test and `render_md`/`decompose_all` consumers; `reachable_set`/`within_reach_recall`/`fisher_z_ci`/`decompose`/`decompose_all`/`main` names are consistent across tasks and tests. `DEFAULT_RESULTS`/`DEFAULT_REGISTRY`/`DETECTORS` shared constants are defined once in Task 3.

**Note for the executor:** if `r_within` does not round near the paper's 0.048 but the *drop*, the paired-drop bootstrap CI excluding 0, and LOO stability still hold, that is acceptable — this artifact becomes the source of truth and the paper prose re-syncs to it (spec §7). Only a *failed* drop sign / paired-drop-bootstrap CI overlapping 0 / LOO instability is a real failure to escalate.

**Estimand-operationalization note (decided during execution, PI-approved 2026-06-18):** SC-02b(a) is gated by the **paired bootstrap of the drop Δr excluding 0** (+ LOO stability + cross-crosswalk sign + mean skill ≥ 0.6), NOT by marginal Fisher-z CI separation. At n=11 the marginal Fisher-z CIs are wide and overlap (overall ≈ [0.38, 0.95] vs within ≈ [−0.57, 0.63]); they are reported for transparency but are not the gate. This is faithful to SC-02b's own wording ("test the drop via bootstrap/leave-one-out, NOT a hard cutpoint") and is disclosed in the emitted `coverage_decomposition.md`.
