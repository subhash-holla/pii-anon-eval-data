#!/usr/bin/env python3
"""C1/C2/C3 contribution-tiering figure (WS2). Scope-honesty: what is delivered now vs scoped future.
Writes results/tier-a/contribution_tiering.{md,png}. Matplotlib is optional ([viz]); writes .png.SKIPPED
if absent (house pattern).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))  # scripts/ for _version (canonical content-version source)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from _version import get_version  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "results" / "tier-a"

# Version is derived from pyproject via _version (never hardcoded) so a content bump can't silently drift
# this figure; the record/language/type counts are the current frozen substrate (see corpus census).
TIERS = [
    ("C1", "Delivered now",
     f"English 11-pipeline F2 detection benchmark + the PII-Anon-Eval v{get_version()} corpus "
     "(782,677 records / 60 languages / 66 types, CC0)."),
    ("C2", "Delivered now",
     "Tri-dimensional diagnostics: per-entity-type, per-domain, per-language slicing + the "
     "coverage-ceiling result (r=0.80 reachable↔recall) + harness validity bounds."),
    ("C3", "Scoped future (Phase 2/3 + Papers 2/3)",
     "Multilingual-at-power + real-data external validity (FR-027) + Tier-2/Tier-3 graded benchmarks."),
]


def render_markdown() -> str:
    lines = [
        "# Contribution tiering (C1/C2/C3) — scope honesty\n",
        "All metrics are on the synthetic distribution (AX-001), not external validity.\n",
        "| Tier | Status | Contribution |",
        "|---|---|---|",
    ]
    for tier, status, desc in TIERS:
        lines.append(f"| {tier} | {status} | {desc} |")
    return "\n".join(lines) + "\n"


def render_figure(path: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        path.with_suffix(".png.SKIPPED").write_text("matplotlib not installed ([viz] extra)")
        return
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.axis("off")
    colors = ["#2e7d32", "#2e7d32", "#9e9e9e"]
    for i, ((tier, status, desc), c) in enumerate(zip(TIERS, colors, strict=True)):
        y = len(TIERS) - i
        ax.barh(y, 1.0, color=c, alpha=0.15, height=0.8)
        ax.text(0.01, y, f"{tier} — {status}", va="center", fontsize=11, fontweight="bold", color=c)
        ax.text(0.01, y - 0.28, desc, va="center", fontsize=8, wrap=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0.3, len(TIERS) + 0.7)
    ax.set_title("PII-Anon-Eval contribution tiers — synthetic-only (AX-001)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "contribution_tiering.md").write_text(render_markdown())
    render_figure(OUT_DIR / "contribution_tiering.png")
    print(f"wrote {OUT_DIR / 'contribution_tiering.md'} (+ .png or .png.SKIPPED)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
