#!/usr/bin/env python3
"""Cost-normalized leaderboard companion (WS2). Joins June-2026 cloud list-price estimates to the
tier1-en-all leaderboard; local detectors are free. Writes results/tier-a/cost_axis.{md,json} and injects
a BEGIN-COST/END-COST block into BASELINES.md.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pii_anon_datasets import load_dataset  # noqa: E402
from pii_anon_datasets.baselines.cloud_cost import estimate_usd  # noqa: E402
from pii_anon_datasets.reporting.baselines import render_cost_table  # noqa: E402
from pii_anon_datasets.reporting.cards import replace_between_markers  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results" / "baselines" / "tier1-en-all" / "baseline_results.json"
OUT_DIR = ROOT / "results" / "tier-a"
PROVIDERS = {"aws": "aws", "gcp": "gcp", "azure": "azure"}


def main() -> int:
    data = json.loads(RESULTS.read_text())
    records = [r for r in load_dataset(split="test") if str(r.get("language")) == "en"]
    lengths = [len(str(r.get("text", "") or "")) for r in records]
    n = len(records)
    cost_per_detector: dict[str, dict] = {}
    for name in [row["detector"] for row in data.get("ranking", [])]:
        provider = PROVIDERS.get(name)
        usd = estimate_usd(provider, lengths) if provider else 0.0
        cost_per_detector[name] = {
            "usd_total": usd,
            "usd_per_1k": (usd / (n / 1000)) if n else None,
            "cloud": provider is not None,
        }
    footnote = (
        "\n_`free` = on-host local model (no API cost). `free-tier*` = a **paid cloud DLP** service whose "
        f"cost is $0 only because this {n:,}-doc English slice is under the provider's free tier "
        "(e.g. GCP's 1 GB/month); it is NOT free at production scale._\n"
    )
    md = (
        "# Cost-normalized leaderboard (companion)\n\n"
        f"English test split: {n:,} docs. Cloud = June-2026 list price ×2 safety (CLOUD_DLP_COST.md); "
        "local detectors are free (on-host).\n\n" + render_cost_table(data, cost_per_detector) + footnote
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "cost_axis.md").write_text(md)
    (OUT_DIR / "cost_axis.json").write_text(json.dumps(cost_per_detector, indent=2))
    baselines = ROOT / "BASELINES.md"
    text = baselines.read_text()
    block = "\n### Cost-normalized (companion lens)\n\n" + render_cost_table(data, cost_per_detector) + footnote
    baselines.write_text(replace_between_markers(text, "COST", block))
    print(f"wrote {OUT_DIR / 'cost_axis.md'} + injected BASELINES.md COST block ({n} docs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
