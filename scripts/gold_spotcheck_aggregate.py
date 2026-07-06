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
DEFAULT_KEY = os.path.join(_HERE, "..", "results", "tier-a", "gold_spotcheck_key.csv")
DEFAULT_MD = os.path.join(_HERE, "..", "results", "tier-a", "gold_spotcheck.md")


def load_key(path: str) -> dict[str, str]:
    """Answer key span_id -> true entity_type (blind rows have entity_type withheld in the review CSV)."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    return {r["span_id"]: r.get("entity_type", "") for r in csv.DictReader(lines)}


def _true_type(row: dict, key: dict[str, str]) -> str:
    """The row's true entity_type — from the CSV when present, else the answer key (blind rows)."""
    t = (row.get("entity_type") or "").strip()
    return t if t else key.get(row.get("span_id", ""), "")


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
    rate = sum(w * x for w, x in zip(ws, xs, strict=False)) / sw
    eff_n = (sw * sw) / sum(w * w for w in ws)  # Kish effective sample size
    return {"rate": rate, "eff_n": eff_n, "ci": _wilson_from_rate(rate, eff_n), "n": len(xs),
            "pooled": sum(xs) / len(xs)}


def blind_recovery_rate(rows: list[dict], key: dict[str, str]) -> dict:
    """Over blind rows: did recovered_type match the (answer-key) true entity_type? (anchoring-resistant)."""
    n = k = 0
    for r in rows:
        if str(r.get("blind", "0")).strip() != "1":
            continue
        rec = (r.get("recovered_type") or "").strip().upper()
        true = _true_type(r, key).strip().upper()
        if not rec or not true:
            continue
        n += 1
        k += int(rec == true)
    if not n:
        return {"rate": float("nan"), "n": 0, "ci": (float("nan"), float("nan"))}
    iv = wilson_interval(k, n)
    return {"rate": k / n, "n": n, "ci": (iv.low, iv.high)}


def blind_realism_rate(rows: list[dict]) -> dict:
    """Anchoring-resistant realism: realism rated over the BLIND rows (entity_type withheld), so the type
    label could not anchor the plausibility judgment. The blind subset does double duty — type-recovery AND
    this blind realism anchor — so no separate subset is needed."""
    n = k = 0
    for r in rows:
        if str(r.get("blind", "0")).strip() != "1":
            continue
        rated = (r.get("realistic") or "").strip()
        if rated not in ("0", "1"):
            continue
        n += 1
        k += int(rated == "1")
    if not n:
        return {"rate": float("nan"), "n": 0, "ci": (float("nan"), float("nan"))}
    iv = wilson_interval(k, n)
    return {"rate": k / n, "n": n, "ci": (iv.low, iv.high)}


def per_group_cells(rows: list[dict], key: dict[str, str], group_field: str = "entity_type",
                    axis: str = "type_correct") -> dict:
    """Per-group (script or entity_type) raw rate + Wilson CI + n. entity_type uses the answer key so blind
    rows group by their true type (their CSV entity_type is withheld)."""
    groups: dict[str, list[int]] = {}
    for r in rows:
        v = (r.get(axis) or "").strip()
        if v not in ("0", "1"):
            continue
        g = _true_type(r, key) if group_field == "entity_type" else r.get(group_field, "")
        groups.setdefault(g, []).append(int(v))
    cells = {}
    for g, vals in groups.items():
        k, n = sum(vals), len(vals)
        iv = wilson_interval(k, n)
        cells[g] = {"rate": k / n, "n": n, "ci": (iv.low, iv.high), "powered": n >= 24}
    return cells


def render_md(rows: list[dict], key: dict[str, str]) -> str:
    # type-correctness is judged only where the type is VISIBLE (non-blind rows) — blind rows carry
    # type-recovery + blind realism instead. Realism is judged on every row.
    nonblind = [r for r in rows if str(r.get("blind", "0")).strip() != "1"]
    tc = weighted_rate(nonblind, "type_correct")
    rl = weighted_rate(rows, "realistic")
    rec = blind_recovery_rate(rows, key)
    br = blind_realism_rate(rows)
    by_script = per_group_cells(nonblind, key, "script", "type_correct")
    by_type = per_group_cells(nonblind, key, "entity_type", "type_correct")
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
        "## Powered claims — gold-validity corroboration rate per axis (the only reportable rates)",
        "",
        "| Axis | weighted rate | Wilson 95% CI | eff. n | pooled (sample-level) |",
        "|---|---:|---|---:|---:|",
        f"| type-correctness | {tc['rate']:.3f} | [{tc['ci'][0]:.3f}, {tc['ci'][1]:.3f}] | {tc['eff_n']:.0f} | {tc.get('pooled', float('nan')):.3f} |",
        f"| realism | {rl['rate']:.3f} | [{rl['ci'][0]:.3f}, {rl['ci'][1]:.3f}] | {rl['eff_n']:.0f} | {rl.get('pooled', float('nan')):.3f} |",
        "",
        f"**Blind type-recovery** (author named the type before the label was revealed, {rec['n']} blind spans): "
        + (f"{rec['rate']:.3f} [CI {rec['ci'][0]:.3f}, {rec['ci'][1]:.3f}]" if rec["n"] else "n/a") + ".",
        f"**Blind-realism rate** (author rated realism with the type label withheld, {br['n']} spans): "
        + (f"{br['rate']:.3f} [CI {br['ci'][0]:.3f}, {br['ci'][1]:.3f}]" if br["n"] else "n/a") + ".",
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
    ap.add_argument("--key", default=DEFAULT_KEY)
    ap.add_argument("--md", default=DEFAULT_MD)
    args = ap.parse_args(argv)
    rows = read_filled(args.input)
    key = load_key(args.key)
    os.makedirs(os.path.dirname(args.md), exist_ok=True)
    with open(args.md, "w", encoding="utf-8") as f:
        f.write(render_md(rows, key))
    print(f"wrote {os.path.relpath(args.md)} — {len(rows)} adjudicated spans "
          f"({'with' if key else 'NO'} answer key)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
