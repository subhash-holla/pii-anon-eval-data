# 2F Gold Spot-Check Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. NOTE: a **human adjudication step** sits between Task 3 (generate the review CSV) and Task 4 (aggregate) — the PI fills the CSV; that is not a code task.

**Goal:** Build a deterministic stratified gold-span sampler + a Horvitz–Thompson-weighted aggregator so the PI can adjudicate ~500 gold spans (type-correctness + realism, with a 25% blind-to-type subset) and the corpus reports ONE powered weighted corroboration rate per axis + ≤6 powered per-script cells, framed as a single-pass author corroboration (never κ/IAA).

**Architecture:** Two pure-stdlib scripts. `gold_spotcheck_sample.py` streams the corpus once (reservoirs cap memory), allocates ~500 spans across `(script, entity_type)` strata satisfying floors (≥2/type, ≥24 per priority script), records each span's inclusion probability `p_incl` + a seeded 25% `blind` flag + a `tranche` tag, and writes a review CSV. The PI fills `type_correct`/`realistic`/`recovered_type`/`note`. `gold_spotcheck_aggregate.py` HT-weights (inverse-`p_incl`) the overall rate per axis (correcting long-tail over-sampling), computes Wilson CIs on the Kish effective-n, the blind type-recovery rate, the 6 powered per-script cells, and descriptive per-type/per-script coverage → `results/tier-a/gold_spotcheck.md` + a datasheet line.

**Tech Stack:** Python 3 stdlib (`csv, json, math, random, argparse, gzip`); reuse `pii_anon_datasets.load_dataset` and `pii_anon_datasets.stats.intervals.wilson_interval`. pytest + ruff. Run with `PYTHONPATH=src`.

**Spec:** `docs/superpowers/specs/2026-06-19-2f-gold-spotcheck-design.md`. SME rationale: `results/tier-a/2f_sample_size_sme_review.md`.

---

## Verified ground truth (do not re-derive)

- `load_dataset(split="test")` (or no arg = full corpus) yields records with `record_id, language, script, text, annotations[]`. Each annotation: `entity_type, start, end, text` (+ others). `text[start:end] == annotation["text"]` (offset-validated).
- Record `script` is an **ISO-15924 code**: `Latn, Deva, Hebr, Arab, Beng, Hans, Grek, Kore, Thai, Jpan, Cyrl` (+ tail `Geor/Telu/Khmr/Mymr/Sinh/Ethi/Laoo/Taml` at ~50 each). The **6 priority scripts** = `Cyrl, Thai, Grek, Beng, Hebr, Latn` (all ≥8k in the test split; the 5 new 2C scripts + Latin).
- `wilson_interval(k: int, n: int, confidence: float = 0.95) -> Interval` with fields `.point, .low, .high, .n, .confidence`. Rejects non-int/bool k,n and requires `0 <= k <= n`.
- `SEED = 20260619`. Sample ~500. `blind` ≈ 25%. Per-type floor ≥2. Priority-script floor ≥24.
- The audit universe is the **full corpus** (all gold spans); sampling from `load_dataset()` (no split) is the gold universe. Use the **test split** if a faster representative universe is preferred — the spec allows either; this plan samples the **full corpus** for representativeness.

---

## File Structure

- **Create** `scripts/gold_spotcheck_sample.py` — stratified seeded sampler → review CSV.
- **Create** `scripts/gold_spotcheck_aggregate.py` — HT-weighted aggregator → `gold_spotcheck.md` + datasheet line.
- **Create** `tests/test_gold_spotcheck.py` — sampler determinism/stratification + aggregator math (mocked CSV).
- **Generate** `results/tier-a/gold_spotcheck_review.csv` (unfilled → PI fills → committed audit record).
- **Generate** `results/tier-a/gold_spotcheck.md` + a DATASHEET line (after adjudication).

---

## Task 1: Sampler — `scripts/gold_spotcheck_sample.py`

**Files:** Create `scripts/gold_spotcheck_sample.py`; Test `tests/test_gold_spotcheck.py` (create).

- [ ] **Step 1: Write the failing test** — create `tests/test_gold_spotcheck.py`:

```python
"""Tests for sub-project 2F: gold spot-check sampler + aggregator."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import gold_spotcheck_sample as gss  # noqa: E402

PRIORITY = ("Cyrl", "Thai", "Grek", "Beng", "Hebr", "Latn")


def _fake_corpus():
    # 8 types x several scripts; enough population per (script,type) to exercise floors.
    recs = []
    types = ["PERSON_NAME", "EMAIL_ADDRESS", "IBAN", "GENETIC_DATA", "PHONE_NUMBER",
             "SSN_RARE", "ETHNICITY", "API_KEY"]
    scripts = list(PRIORITY) + ["Hans", "Arab"]
    rid = 0
    for sc in scripts:
        for t in types:
            for _ in range(40):  # population 40 per (script,type)
                rid += 1
                recs.append({"record_id": f"r{rid}", "language": "en", "script": sc,
                             "text": f"x {t} y", "annotations": [{"entity_type": t, "start": 2, "end": 2 + len(t), "text": t}]})
    return recs


def test_sampler_deterministic_and_floors():
    a = gss.sample(_fake_corpus(), total=300, seed=gss.SEED)
    b = gss.sample(_fake_corpus(), total=300, seed=gss.SEED)
    assert [r["span_id"] for r in a] == [r["span_id"] for r in b], "same seed -> identical sample"
    # per-type floor: every type present has >= 2
    from collections import Counter
    by_type = Counter(r["entity_type"] for r in a)
    assert all(v >= 2 for v in by_type.values()), by_type
    # priority-script floor: each priority script present has >= 24
    by_script = Counter(r["script"] for r in a)
    for sc in PRIORITY:
        assert by_script[sc] >= 24, (sc, by_script[sc])
    # p_incl recorded, in (0,1]; blind ~25%
    assert all(0 < r["p_incl"] <= 1 for r in a)
    blind_frac = sum(r["blind"] for r in a) / len(a)
    assert 0.15 <= blind_frac <= 0.35, blind_frac
```

- [ ] **Step 2: Run, verify it fails** — `PYTHONPATH=src python -m pytest tests/test_gold_spotcheck.py -k sampler -q` → FAIL (no module).

- [ ] **Step 3: Implement** — create `scripts/gold_spotcheck_sample.py`:

```python
#!/usr/bin/env python3
"""2F gold spot-check sampler — deterministic stratified ~500-span sample → a human review CSV.

Streams the corpus once (per-stratum reservoirs cap memory), allocates across (script, entity_type) strata
satisfying floors (>=2 per type, >=24 per priority script), records each span's inclusion probability p_incl
(for the aggregator's Horvitz-Thompson weighting), a seeded ~25% blind-to-type subset, and a tranche tag.
Output: results/tier-a/gold_spotcheck_review.csv (the PI fills type_correct/realistic/recovered_type/note).
"""
from __future__ import annotations

import argparse
import csv
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pii_anon_datasets import load_dataset  # noqa: E402

SEED = 20260619
PRIORITY_SCRIPTS = ("Cyrl", "Thai", "Grek", "Beng", "Hebr", "Latn")
PER_TYPE_FLOOR = 2
PRIORITY_SCRIPT_FLOOR = 24
BLIND_FRACTION = 0.25
RES_CAP = 60  # reservoir cap per (script, type) stratum
CONTEXT_PAD = 60
_HERE = os.path.dirname(__file__)
DEFAULT_OUT = os.path.join(_HERE, "..", "results", "tier-a", "gold_spotcheck_review.csv")
REALISM_RUBRIC = ("Realism rubric (mark realistic=1 if the value is a plausible instance of its type IN THIS "
                  "CONTEXT): 1=plausible (e.g. a well-formed email, a native-script name in its language); "
                  "0=implausible (e.g. an English/US value in a non-English carrier, malformed format). "
                  "Examples: 'pedro@x.com' as EMAIL=1; 'James Smith' as PERSON_NAME in a Greek record=0.")


def _iter_spans(corpus):
    for rec in corpus:
        for i, a in enumerate(rec.get("annotations", [])):
            yield {"record_id": rec["record_id"], "ann_idx": i, "language": rec.get("language", ""),
                   "script": rec.get("script", ""), "entity_type": a["entity_type"],
                   "span_text": a.get("text", ""), "rec_text": rec.get("text", ""),
                   "start": a.get("start", 0), "end": a.get("end", 0)}


def _stream_strata(corpus, rng):
    """One pass: per (script, entity_type) stratum -> population count + a seeded reservoir of <=RES_CAP spans."""
    pop: dict[tuple, int] = {}
    res: dict[tuple, list] = {}
    seen = 0
    for sp in _iter_spans(corpus):
        key = (sp["script"], sp["entity_type"])
        pop[key] = pop.get(key, 0) + 1
        bucket = res.setdefault(key, [])
        n = pop[key]
        if len(bucket) < RES_CAP:
            bucket.append(sp)
        else:  # reservoir replacement (Algorithm R), seeded
            j = rng.randrange(n)
            if j < RES_CAP:
                bucket[j] = sp
        seen += 1
    return pop, res, seen


def sample(corpus, *, total: int = 500, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed)
    pop, res, _ = _stream_strata(corpus, rng)
    keys = sorted(pop)  # deterministic order
    draw: dict[tuple, int] = {k: 0 for k in keys}

    def _take(key, k):
        draw[key] = min(pop[key], draw[key] + k)

    # 1) per-type floor: ensure >=PER_TYPE_FLOOR per entity_type (from its largest (script,type) cell)
    types = sorted({t for (_s, t) in keys})
    for t in types:
        cells = sorted((k for k in keys if k[1] == t), key=lambda k: -pop[k])
        have = sum(draw[k] for k in cells)
        for k in cells:
            if have >= PER_TYPE_FLOOR:
                break
            add = min(PER_TYPE_FLOOR - have, pop[k] - draw[k])
            _take(k, add)
            have += add
    # 2) priority-script floor: ensure >=PRIORITY_SCRIPT_FLOOR per priority script (round-robin its types)
    for sc in PRIORITY_SCRIPTS:
        cells = sorted((k for k in keys if k[0] == sc), key=lambda k: -pop[k])
        if not cells:
            continue
        idx = 0
        while sum(draw[k] for k in cells) < PRIORITY_SCRIPT_FLOOR and any(draw[k] < pop[k] for k in cells):
            k = cells[idx % len(cells)]
            if draw[k] < pop[k]:
                _take(k, 1)
            idx += 1
    # 3) proportional fill to `total` (HT weighting corrects any residual imbalance)
    current = sum(draw.values())
    remaining = max(0, total - current)
    total_pop = sum(pop.values())
    if remaining and total_pop:
        # largest-remainder proportional over headroom
        room = {k: pop[k] - draw[k] for k in keys}
        weights = {k: pop[k] / total_pop for k in keys}
        alloc = {k: min(room[k], int(remaining * weights[k])) for k in keys}
        for k in keys:
            _take(k, alloc[k])
        # top up any rounding shortfall deterministically by population
        for k in sorted(keys, key=lambda k: -pop[k]):
            if sum(draw.values()) >= total:
                break
            if draw[k] < pop[k]:
                _take(k, 1)

    # materialize: draw the allocated count from each stratum's reservoir (seeded), set p_incl + tranche
    out: list[dict] = []
    for k in keys:
        n = draw[k]
        if not n:
            continue
        bucket = res[k]
        picks = rng.sample(bucket, min(n, len(bucket)))
        p_incl = min(1.0, len(picks) / pop[k])
        for sp in picks:
            s, e = sp["start"], sp["end"]
            ctx = sp["rec_text"][max(0, s - CONTEXT_PAD): e + CONTEXT_PAD]
            out.append({
                "span_id": f"{sp['record_id']}#{sp['ann_idx']}", "record_id": sp["record_id"],
                "language": sp["language"], "script": sp["script"], "entity_type": sp["entity_type"],
                "span_text": sp["span_text"], "context": ctx.replace("\n", " "),
                "p_incl": round(p_incl, 8), "tranche": "stratified",
            })
    out.sort(key=lambda r: r["span_id"])
    # seeded ~25% blind subset (stratified by script so blinding isn't concentrated)
    brng = random.Random(seed ^ 0x9E3779B9)
    for sc in sorted({r["script"] for r in out}):
        rows = [r for r in out if r["script"] == sc]
        k = round(len(rows) * BLIND_FRACTION)
        for r in brng.sample(rows, k):
            r["blind"] = 1
    for r in out:
        r.setdefault("blind", 0)
    return out


FIELDS = ["span_id", "record_id", "language", "script", "entity_type", "span_text", "context",
          "p_incl", "blind", "tranche", "type_correct", "realistic", "recovered_type", "note"]


def write_review_csv(rows: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(f"# 2F gold spot-check review — fill type_correct(1/0), realistic(1/0), recovered_type(blind rows only), note.\n")
        f.write(f"# {REALISM_RUBRIC}\n")
        f.write("# BLIND rows (blind=1): entity_type is WITHHELD below — write your recovered_type BEFORE looking it up.\n")
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            row = dict(r)
            if r.get("blind"):
                row["entity_type"] = ""  # withhold for blind type-recovery
            row.setdefault("type_correct", "")
            row.setdefault("realistic", "")
            row.setdefault("recovered_type", "")
            row.setdefault("note", "")
            w.writerow(row)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="2F gold spot-check sampler.")
    ap.add_argument("--total", type=int, default=500)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--split", default=None, help="dataset split (default: full corpus)")
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    corpus = load_dataset(split=args.split) if args.split else load_dataset()
    rows = sample(corpus, total=args.total, seed=args.seed)
    write_review_csv(rows, args.out)
    print(f"wrote {os.path.relpath(args.out)} — {len(rows)} spans "
          f"({sum(r['blind'] for r in rows)} blind); fill it, then run gold_spotcheck_aggregate.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify it passes** — `PYTHONPATH=src python -m pytest tests/test_gold_spotcheck.py -k sampler -q` → PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/gold_spotcheck_sample.py tests/test_gold_spotcheck.py
git commit -m "feat(2F): stratified gold spot-check sampler (floors + p_incl + 25% blind)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Aggregator — `scripts/gold_spotcheck_aggregate.py`

**Files:** Create `scripts/gold_spotcheck_aggregate.py`; Test `tests/test_gold_spotcheck.py` (append).

- [ ] **Step 1: Write the failing test (append)** — uses a hand-computable mocked filled CSV:

```python
import csv as _csv  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
import gold_spotcheck_aggregate as gsa  # noqa: E402


def _write_mock(path):
    rows = [
        # p_incl=0.5 -> w=2 ; p_incl=0.1 -> w=10 (long-tail, upweighted)
        {"span_id": "a#0", "script": "Latn", "entity_type": "PERSON_NAME", "p_incl": "0.5", "blind": "0",
         "type_correct": "1", "realistic": "1", "recovered_type": "", "note": ""},
        {"span_id": "b#0", "script": "Latn", "entity_type": "PERSON_NAME", "p_incl": "0.5", "blind": "0",
         "type_correct": "1", "realistic": "0", "recovered_type": "", "note": "english value"},
        {"span_id": "c#0", "script": "Cyrl", "entity_type": "GENETIC_DATA", "p_incl": "0.1", "blind": "1",
         "type_correct": "0", "realistic": "1", "recovered_type": "PERSON_NAME", "note": "mislabel"},
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("# header\n")
        w = _csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def test_ht_weighted_rate_corrects_long_tail(tmp_path):
    p = tmp_path / "filled.csv"
    _write_mock(p)
    rows = gsa.read_filled(str(p))
    # type_correct: weighted = (2*1 + 2*1 + 10*0)/(2+2+10) = 4/14 ≈ 0.2857 (long-tail 0 dominates via weight)
    res = gsa.weighted_rate(rows, "type_correct")
    assert abs(res["rate"] - 4 / 14) < 1e-6
    assert res["eff_n"] > 0 and 0 <= res["ci"][0] <= res["rate"] <= res["ci"][1] <= 1
    # blind type-recovery: 1 blind row, recovered PERSON_NAME but true (hidden) was GENETIC_DATA -> 0/1
    rec = gsa.blind_recovery_rate(rows)
    assert rec["n"] == 1 and rec["rate"] == 0.0
```

- [ ] **Step 2: Run, verify it fails** — `PYTHONPATH=src python -m pytest tests/test_gold_spotcheck.py -k "ht_weighted or recovery" -q` → FAIL (no module).

- [ ] **Step 3: Implement** — create `scripts/gold_spotcheck_aggregate.py`:

```python
#!/usr/bin/env python3
"""2F gold spot-check aggregator — Horvitz-Thompson-weighted corroboration rates from the filled review CSV.

Reads results/tier-a/gold_spotcheck_review.csv (PI-filled). Emits results/tier-a/gold_spotcheck.md + a
datasheet line: ONE weighted overall rate per axis (the only powered claim; inverse-p_incl HT estimate that
corrects the per-type floor's long-tail over-sampling), Wilson 95% CI on the Kish effective-n; the blind
type-recovery rate; the 6 priority per-script powered cells; descriptive per-type/per-script coverage
(flagged UNDERPOWERED). Single-pass author corroboration — NEVER kappa/IAA (AX-002).
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pii_anon_datasets.stats.intervals import wilson_interval  # noqa: E402

PRIORITY_SCRIPTS = ("Cyrl", "Thai", "Grek", "Beng", "Hebr", "Latn")
_HERE = os.path.dirname(__file__)
DEFAULT_IN = os.path.join(_HERE, "..", "results", "tier-a", "gold_spotcheck_review.csv")
DEFAULT_MD = os.path.join(_HERE, "..", "results", "tier-a", "gold_spotcheck.md")


def read_filled(path: str) -> list[dict]:
    """Rows with a non-blank type_correct OR realistic (adjudicated); skip comment lines + blanks."""
    out = []
    with open(path, encoding="utf-8") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    for r in csv.DictReader(lines):
        if (r.get("type_correct") or "").strip() == "" and (r.get("realistic") or "").strip() == "":
            continue
        out.append(r)
    return out


def _wilson_from_rate(rate: float, eff_n: float) -> tuple[float, float]:
    """Wilson CI on a weighted rate via the Kish effective sample size (k = round(rate*eff_n))."""
    n = max(1, int(round(eff_n)))
    k = min(n, max(0, int(round(rate * n))))
    iv = wilson_interval(k, n)
    return (iv.low, iv.high)


def weighted_rate(rows: list[dict], axis: str) -> dict:
    """HT inverse-p_incl weighted rate for a 0/1 axis + Kish effective-n + Wilson CI."""
    xs, ws = [], []
    for r in rows:
        v = (r.get(axis) or "").strip()
        if v not in ("0", "1"):
            continue
        p = float(r.get("p_incl") or 0) or 1e-9
        ws.append(1.0 / p)
        xs.append(int(v))
    if not xs:
        return {"rate": float("nan"), "eff_n": 0.0, "ci": (float("nan"), float("nan")), "n": 0}
    sw = sum(ws)
    rate = sum(w * x for w, x in zip(ws, xs)) / sw
    eff_n = (sw * sw) / sum(w * w for w in ws)  # Kish effective sample size
    return {"rate": rate, "eff_n": eff_n, "ci": _wilson_from_rate(rate, eff_n), "n": len(xs),
            "pooled": sum(xs) / len(xs)}


def blind_recovery_rate(rows: list[dict]) -> dict:
    """Over blind rows: did recovered_type match the true entity_type? (anchoring-resistant)."""
    n = k = 0
    for r in rows:
        if str(r.get("blind", "0")).strip() != "1":
            continue
        rec = (r.get("recovered_type") or "").strip().upper()
        true = (r.get("entity_type") or "").strip().upper()
        if not rec or not true:
            continue
        n += 1
        k += int(rec == true)
    if not n:
        return {"rate": float("nan"), "n": 0, "ci": (float("nan"), float("nan"))}
    iv = wilson_interval(k, n)
    return {"rate": k / n, "n": n, "ci": (iv.low, iv.high)}


def per_group_cells(rows: list[dict], key: str, axis: str = "type_correct") -> dict:
    """Per-group (script or entity_type) raw rate + Wilson CI + n (descriptive unless n large)."""
    groups: dict[str, list[int]] = {}
    for r in rows:
        v = (r.get(axis) or "").strip()
        if v not in ("0", "1"):
            continue
        groups.setdefault(r.get(key, ""), []).append(int(v))
    cells = {}
    for g, vals in groups.items():
        k, n = sum(vals), len(vals)
        iv = wilson_interval(k, n)
        cells[g] = {"rate": k / n, "n": n, "ci": (iv.low, iv.high), "powered": n >= 24}
    return cells
```

- [ ] **Step 4: Run, verify it passes** — `PYTHONPATH=src python -m pytest tests/test_gold_spotcheck.py -k "ht_weighted or recovery" -q` → PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/gold_spotcheck_aggregate.py tests/test_gold_spotcheck.py
git commit -m "feat(2F): HT-weighted aggregator core (overall rate, blind recovery, per-group cells)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Aggregator rendering + CLI; generate the review CSV

**Files:** Modify `scripts/gold_spotcheck_aggregate.py` (append `render_md` + `main`); Test append; generate `results/tier-a/gold_spotcheck_review.csv`.

- [ ] **Step 1: Write the failing test (append)**

```python
def test_render_and_main_smoke(tmp_path):
    p = tmp_path / "filled.csv"
    _write_mock(p)
    out = tmp_path / "gold_spotcheck.md"
    rc = gsa.main(["--input", str(p), "--md", str(out)])
    assert rc == 0
    md = out.read_text(encoding="utf-8")
    assert "corroboration rate" in md.lower()
    assert "NOT" in md and ("kappa" in md.lower() or "inter-annotator" in md.lower())  # AX-002 framing present
    assert "UNDERPOWERED" in md  # descriptive cells flagged
```

- [ ] **Step 2: Run, verify it fails** — `PYTHONPATH=src python -m pytest tests/test_gold_spotcheck.py -k render_and_main -q` → FAIL (no `main`).

- [ ] **Step 3: Implement (append to `scripts/gold_spotcheck_aggregate.py`)**

```python
def render_md(rows: list[dict]) -> str:
    tc = weighted_rate(rows, "type_correct")
    rl = weighted_rate(rows, "realistic")
    rec = blind_recovery_rate(rows)
    by_script = per_group_cells(rows, "script", "type_correct")
    by_type = per_group_cells(rows, "entity_type", "type_correct")
    n_adj = max(tc["n"], rl["n"])
    L = [
        "# Gold-validity spot-check (single-pass author corroboration)",
        "",
        "> **AX-002 / AX-001 framing.** This is a SINGLE-PASS gold-validity corroboration by ONE rater (the "
        "author) against the programmatic gold — it is **NOT** inter-annotator agreement, **NOT** Cohen's "
        "kappa, **NOT** a multi-annotator panel, and **NOT** external validity. Self-adjudication is a named "
        "limitation: the type-correctness rate is an upper bound; the **blind type-recovery rate** is its "
        "anchoring-resistant complement. Realism is the author's synthetic-plausibility judgment (AX-001). "
        "Logged as a disclosed post-hoc AMEND to the preregistration (commissioned by MAJOR-3).",
        "",
        f"**Adjudicated:** {n_adj} spans (Horvitz–Thompson inverse-`p_incl` weighted to the corpus marginal; "
        f"the per-type coverage floor over-samples the long tail, so the weighted rate — not the raw pooled "
        f"mean — is the corpus estimand).",
        "",
        "## Powered claims (the only reportable rates)",
        "",
        "| Axis | weighted rate | Wilson 95% CI | eff. n | pooled (sample-level) |",
        "|---|---:|---|---:|---:|",
        f"| type-correctness | {tc['rate']:.3f} | [{tc['ci'][0]:.3f}, {tc['ci'][1]:.3f}] | {tc['eff_n']:.0f} | {tc.get('pooled', float('nan')):.3f} |",
        f"| realism | {rl['rate']:.3f} | [{rl['ci'][0]:.3f}, {rl['ci'][1]:.3f}] | {rl['eff_n']:.0f} | {rl.get('pooled', float('nan')):.3f} |",
        "",
        f"**Blind type-recovery** (author named the type before the label was revealed, {rec['n']} blind spans): "
        + (f"{rec['rate']:.3f} [CI {rec['ci'][0]:.3f}, {rec['ci'][1]:.3f}]" if rec["n"] else "n/a") + ".",
        "",
        "## Powered per-script cells (priority scripts, n≥24)",
        "",
        "| Script | rate | Wilson 95% CI | n | status |",
        "|---|---:|---|---:|---|",
    ]
    for sc in PRIORITY_SCRIPTS:
        c = by_script.get(sc)
        if c:
            status = "POWERED" if c["powered"] else "UNDERPOWERED"
            L.append(f"| {sc} | {c['rate']:.3f} | [{c['ci'][0]:.3f}, {c['ci'][1]:.3f}] | {c['n']} | {status} |")
    L += ["", "## Descriptive coverage — per entity type (NOT powered claims; wide CIs)", "",
          "| Entity type | rate | Wilson 95% CI | n | status |", "|---|---:|---|---:|---|"]
    for t in sorted(by_type):
        c = by_type[t]
        status = "POWERED" if c["powered"] else "UNDERPOWERED"
        L.append(f"| {t} | {c['rate']:.3f} | [{c['ci'][0]:.3f}, {c['ci'][1]:.3f}] | {c['n']} | {status} |")
    # disagreements
    dis = [r for r in rows if (r.get("type_correct") or "").strip() == "0"
           or (r.get("realistic") or "").strip() == "0"]
    L += ["", f"## Disagreements ({len(dis)})", ""]
    for r in dis:
        L.append(f"- `{r.get('span_id','')}` {r.get('entity_type','?')} ({r.get('script','')}): "
                 f"type_correct={r.get('type_correct','')} realistic={r.get('realistic','')} — {r.get('note','')}")
    L += ["", "_Datasheet line:_ "
          f"single-pass author gold-validity corroboration on n={n_adj} stratified spans — "
          f"type-correctness {tc['rate']:.3f} (Wilson 95% [{tc['ci'][0]:.3f},{tc['ci'][1]:.3f}]), realism "
          f"{rl['rate']:.3f}; NOT inter-annotator agreement / kappa (AX-002); synthetic-only (AX-001)."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="2F gold spot-check aggregator.")
    ap.add_argument("--input", default=DEFAULT_IN)
    ap.add_argument("--md", default=DEFAULT_MD)
    args = ap.parse_args(argv)
    rows = read_filled(args.input)
    os.makedirs(os.path.dirname(args.md), exist_ok=True)
    with open(args.md, "w", encoding="utf-8") as f:
        f.write(render_md(rows))
    print(f"wrote {os.path.relpath(args.md)} — {len(rows)} adjudicated spans")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test, then generate the REAL review CSV**

```bash
PYTHONPATH=src python -m pytest tests/test_gold_spotcheck.py -q   # all sampler+aggregator tests pass
PYTHONPATH=src python scripts/gold_spotcheck_sample.py            # writes results/tier-a/gold_spotcheck_review.csv (~500 spans)
```
Confirm: `python3 -c "import csv; rows=[r for r in csv.DictReader(open('results/tier-a/gold_spotcheck_review.csv')) ]" ` parses; ~500 rows; ~25% blind (entity_type blank).

- [ ] **Step 5: Commit the scripts + the unfilled review CSV**

```bash
git add scripts/gold_spotcheck_aggregate.py tests/test_gold_spotcheck.py results/tier-a/gold_spotcheck_review.csv
git commit -m "feat(2F): aggregator render/CLI + generate the ~500-span review CSV (ready for adjudication)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## ⏸ HUMAN STEP (not a code task): PI adjudicates `results/tier-a/gold_spotcheck_review.csv`

The PI opens the CSV (spreadsheet), reads the rubric in the header, and fills per row: `type_correct` (1/0),
`realistic` (1/0), `recovered_type` (blind rows only — name the type from `span_text`+`context` BEFORE
looking up the true label), `note` for any 0. Partial completion is fine. This is the actual spot-check.

---

## Task 4: Aggregate the filled CSV + docs + final gate

**Files:** Generate `results/tier-a/gold_spotcheck.md`; Modify `DATASHEET.md`; Modify `CHANGELOG.md`.

- [ ] **Step 1: Aggregate the filled CSV**

```bash
PYTHONPATH=src python scripts/gold_spotcheck_aggregate.py   # writes results/tier-a/gold_spotcheck.md
```
Read `gold_spotcheck.md`: confirm the weighted rates + CIs, blind-recovery, powered per-script cells, the UNDERPOWERED-flagged per-type coverage, the AX-002 framing block, and the datasheet line.

- [ ] **Step 2: Add the DATASHEET line + AMEND note** — in `DATASHEET.md`, near the gold/annotation-quality
section, add the datasheet line printed by the aggregator (single-pass author corroboration; type-correctness
+ realism rates with Wilson CIs; "NOT IAA/kappa (AX-002); synthetic-only (AX-001)"; "post-hoc AMEND to the
preregistration"). In `CHANGELOG.md` `[2.2-dev]` section, add a line: "2F gold spot-check — single-pass
author gold-validity corroboration (n≈500 stratified, HT-weighted, 25% blind subset); see
results/tier-a/gold_spotcheck.md. NOT inter-annotator agreement (AX-002)."

- [ ] **Step 3: Final gate**

```bash
PYTHONPATH=src python -m pytest -q                                          # green
ruff check scripts/gold_spotcheck_sample.py scripts/gold_spotcheck_aggregate.py tests/test_gold_spotcheck.py
PYTHONPATH=src python scripts/check_version_sync.py                         # content stays 2.1.0
PYTHONPATH=src python -m pytest tests/test_doc_drift.py -q                  # DATASHEET edits don't break drift
```

- [ ] **Step 4: Commit the audit artifacts + filled CSV**

```bash
git add results/tier-a/gold_spotcheck.md results/tier-a/gold_spotcheck_review.csv DATASHEET.md CHANGELOG.md
git commit -m "feat(2F): gold spot-check results + datasheet corroboration line + AMEND note

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage:** §1 done-when: (1) stratified ~500 sampler + floors + p_incl + blind → Task 1; (2) CSV columns/withheld blind type → Task 1 `write_review_csv`; (3) human step + rubric → header + the ⏸ step; (4) HT-weighted rate per axis + Wilson + blind-recovery + 6 powered per-script + descriptive coverage + disagreements → Tasks 2–3; (5) framing/noun → `render_md`; (6) tests + gates → Tasks 1–4. ✅ §10 scope-honesty + AMEND → render_md framing block + Task 4 docs. ✅

**Placeholder scan:** real code throughout; the 6 priority scripts, seed, floors, blind fraction, rubric are concrete. The only non-code step is the PI adjudication (inherently manual) — explicitly marked, not a placeholder.

**Type consistency:** `sample()` row keys (`span_id, script, entity_type, p_incl, blind, …`) are the CSV `FIELDS` the aggregator's `read_filled`/`weighted_rate`/`blind_recovery_rate`/`per_group_cells` consume; `weighted_rate` returns `{rate, eff_n, ci, n, pooled}` used identically in the test + `render_md`; `wilson_interval(k,n).low/.high` used consistently. ✅

**Note for the executor:** the sampler streams the full 782k corpus once (a few minutes) — run it in the foreground for Task 3 step 4 or background it. If memory is tight, pass `--split test` (157k, representative). The HT weighting makes the overall rate unbiased regardless of the exact allocation, so do NOT hand-tune the proportional fill.
