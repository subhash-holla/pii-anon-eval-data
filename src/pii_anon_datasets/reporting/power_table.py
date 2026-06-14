"""Per-cell power table + committed-lattice power matrix (DC-09; FR-029, NFR-003, AX-003).

Every published per-cell row carries a non-strippable ``DesignProvenance`` (n + tier + target +
powered + external-validity caveat) so a reader/regulator can verify the metric was computed on a
powered cell. ``power_report`` renders the before/after power matrix with a SMALL/ADEQUATE/LARGE
verdict per the sampling-design claim ladder. Takes ``observed_counts`` as input (computed by the
audit) — does not read the corpus, keeping this src-layer pure.
"""
from __future__ import annotations

import io
from collections import defaultdict

from ..scoring.detection import DesignProvenance


def _power_class(observed: int, target: int) -> str:
    if observed <= 0:
        return "empty"
    return "well_powered" if observed >= target else "under_powered"


def power_table(lattice: dict, observed_counts: dict, *, scores: dict | None = None) -> list[dict]:
    """Per committed COUNT-GATED cell: a row with observed n, tier target, and DesignProvenance.

    ``scores`` (optional) maps cell_id -> DetectionScore to attach a measured recall + Wilson CI.
    A row can NEVER be emitted without its design provenance (non-strippable, AX-003).
    """
    rows = []
    for c in lattice["cells"]:
        if not c["count_gated"]:
            continue
        obs = int(observed_counts.get(c["id"], 0))
        dp = DesignProvenance.from_cell(c, obs)
        row = {
            "cell_id": c["id"],
            "dimensions": dict(c["dimensions"]),
            "tier": c["tier"],
            "target_n": c["target_n"],
            "observed_positives": obs,
            "power_class": _power_class(obs, c["target_n"]),
            "powered": dp.powered,
            "design_provenance": dp.as_dict(),   # non-strippable
        }
        if scores and c["id"] in scores:
            s = scores[c["id"]]
            row["recall"] = s.recall
            row["recall_ci"] = s.recall_ci.as_dict()
        rows.append(row)
    rows.sort(key=lambda r: r["cell_id"])
    return rows


def _verdict(well: int, total: int) -> str:
    if total == 0:
        return "EMPTY"
    frac = well / total
    return "LARGE" if frac >= 0.999 else "ADEQUATE" if frac >= 0.80 else "SMALL"


def render_csv(rows: list[dict]) -> str:
    import csv
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["cell_id", "tier", "target_n", "observed_positives", "power_class", "powered"])
    for r in rows:
        w.writerow([r["cell_id"], r["tier"], r["target_n"], r["observed_positives"],
                    r["power_class"], r["powered"]])
    return buf.getvalue()


def render_markdown(rows: list[dict], *, max_rows: int = 0) -> str:
    out = ["| cell | tier | target | observed | class |", "|---|---|---:|---:|---|"]
    shown = rows if max_rows <= 0 else rows[:max_rows]
    for r in shown:
        out.append(f"| {r['cell_id']} | {r['tier']} | {r['target_n']} | "
                   f"{r['observed_positives']} | {r['power_class']} |")
    return "\n".join(out) + "\n"


def power_report(lattice: dict, observed_counts: dict, *, title: str = "Committed-Lattice Power Matrix",
                 note: str = "") -> str:
    """Markdown power matrix grouped by interaction + tier, with the claim-ladder verdict."""
    rows = power_table(lattice, observed_counts)
    by_int: dict = defaultdict(lambda: [0, 0, 0, 0])      # well, under, empty, shortfall
    by_tier: dict = defaultdict(lambda: [0, 0, 0, 0])
    interaction_of = {c["id"]: c["interaction"] for c in lattice["cells"]}
    tot = [0, 0, 0, 0]
    for r in rows:
        pc = r["power_class"]
        idx = {"well_powered": 0, "under_powered": 1, "empty": 2}[pc]
        short = max(0, r["target_n"] - r["observed_positives"])
        for bucket in (by_int[interaction_of[r["cell_id"]]], by_tier[r["tier"]], tot):
            bucket[idx] += 1
            bucket[3] += short
    well, under, empty, short = tot
    total = well + under + empty

    lines = [f"# {title}", ""]
    if note:
        lines += [note, ""]
    lines += [
        f"- committed count-gated cells: **{total}** · well-powered **{well}** · "
        f"under-powered **{under}** · empty **{empty}**",
        f"- total positive shortfall: **{short:,}** · overall verdict: **{_verdict(well, total)}**",
        "",
        "## By named interaction",
        "| interaction | cells | well | under | empty | shortfall | verdict |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for inter in sorted(by_int):
        w, u, e, s = by_int[inter]
        lines.append(f"| {inter} | {w+u+e} | {w} | {u} | {e} | {s:,} | {_verdict(w, w+u+e)} |")
    lines += ["", "## By risk tier",
              "| tier | cells | well | under | empty | shortfall | verdict |",
              "|---|---:|---:|---:|---:|---:|---|"]
    for tier in sorted(by_tier):
        w, u, e, s = by_tier[tier]
        lines.append(f"| {tier} | {w+u+e} | {w} | {u} | {e} | {s:,} | {_verdict(w, w+u+e)} |")
    lines += ["", "## Claim ladder (sampling-design.md §7)",
              "- **Marginals** (per language/type/domain/difficulty/adversarial/dimension): "
              "single-factor recall claims with 95% Wilson CIs.",
              "- **Named 2-ways** (language×entity-type rectangle, domain×track, adversarial-type×"
              "entity-type): estimable on committed cells only.",
              "- **Unnamed 2-way / ≥3-way / full grid**: NOT estimable — exploratory only.",
              "",
              "_Power on a synthetic cell is precision on the synthetic distribution, not external "
              "validity (cf. FR-027 real-data correlation slice)._"]
    return "\n".join(lines) + "\n"
