#!/usr/bin/env python3
"""Project the cloud-DLP spend for a multilingual baseline run BEFORE any money is spent, and compute a
budget-capped run plan (which languages each provider can afford).

For each provider it intersects the split with that provider's supported-language allowlist
(:mod:`pii_anon_datasets.baselines.cloud_languages`), counts billable documents/characters PER LANGUAGE,
and applies the ×2-safety cost model (:mod:`pii_anon_datasets.baselines.cloud_cost`). Read-only — spends
nothing.

  python scripts/cloud_cost_preflight.py --split test                       # human cost table
  python scripts/cloud_cost_preflight.py --split test --max-azure-usd 90 --format plan
      -> {"aws": ["en"], "gcp": [..12..], "azure": ["en","nl",...]}   # the affordable language set

Azure is the budget risk (per-document 1,000-char rounding); with the default $90 cap it covers English +
the next-most-represented languages that fit. AWS Comprehend PII is English-only; GCP DLP is < 1 GB → free.
The orchestrator (`run_full_leaderboard.sh`) reads the ``plan`` form to decide exactly which shards to run.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

_REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "src"))

from pii_anon_datasets import load_dataset  # noqa: E402
from pii_anon_datasets.baselines import cloud_cost, cloud_languages  # noqa: E402

_PROVIDERS = ("aws", "azure", "gcp")


def _gather(split: str) -> dict[str, list[int]]:
    """Map language code -> per-document character lengths for the whole split (a single load)."""
    by_lang: dict[str, list[int]] = {}
    for rec in load_dataset(split=split, language=None):
        by_lang.setdefault(str(rec.get("language")), []).append(len(str(rec.get("text", "") or "")))
    return by_lang


def _per_language_cost(provider: str, by_lang: dict[str, list[int]]) -> dict[str, dict]:
    """For each language ``provider`` supports: ``{lang: {"n_docs", "est_usd"}}`` (descending record count)."""
    langs = cloud_languages.supported(provider) & set(by_lang)
    ordered = sorted(langs, key=lambda lng: len(by_lang[lng]), reverse=True)  # most-represented first
    return {
        lng: {"n_docs": len(by_lang[lng]), "est_usd": round(cloud_cost.estimate_usd(provider, by_lang[lng]), 2)}
        for lng in ordered
    }


def _affordable(per_lang: dict[str, dict], cap: float | None) -> list[str]:
    """Greedily keep languages (most-represented first, English always first if present) under ``cap``.

    ``cap is None`` -> no limit (keep all). English leads because it is the headline language already wired
    into the English all-11 table; the rest follow by descending record count until the budget is hit.
    """
    order = (["en"] if "en" in per_lang else []) + [lng for lng in per_lang if lng != "en"]
    if cap is None:
        return order
    kept: list[str] = []
    spent = 0.0
    for lng in order:
        cost = per_lang[lng]["est_usd"]
        if spent + cost > cap:
            continue
        kept.append(lng)
        spent += cost
    return kept


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cloud_cost_preflight")
    ap.add_argument("--split", default="test")
    ap.add_argument("--format", choices=("table", "plan"), default="table")
    ap.add_argument("--max-azure-usd", type=float, default=None, help="cap Azure's language set to this USD")
    ap.add_argument("--max-aws-usd", type=float, default=None)
    ap.add_argument("--max-gcp-usd", type=float, default=None)
    args = ap.parse_args(argv)

    by_lang = _gather(args.split)
    per = {p: _per_language_cost(p, by_lang) for p in _PROVIDERS}
    caps = {"aws": args.max_aws_usd, "azure": args.max_azure_usd, "gcp": args.max_gcp_usd}
    plan = {p: _affordable(per[p], caps[p]) for p in _PROVIDERS}

    if args.format == "plan":
        print(json.dumps(plan))
        return 0

    print(f"Cloud-DLP cost preflight — split '{args.split}' (×2 safety ceiling; verify pricing at run time)")
    for p in _PROVIDERS:
        kept = set(plan[p])
        full_usd = round(sum(d["est_usd"] for d in per[p].values()), 2)
        kept_usd = round(sum(per[p][lng]["est_usd"] for lng in kept), 2)
        cap = caps[p]
        cap_s = f"  (capped to ${cap:.0f} → ${kept_usd:.2f})" if cap is not None else ""
        print(f"\n{p.upper()}: {len(per[p])} supported langs, full est ${full_usd:.2f}{cap_s}")
        for lng, d in per[p].items():
            mark = "✓" if lng in kept else "·"
            print(f"  {mark} {lng:4s} {d['n_docs']:7,d} docs   ${d['est_usd']:8.2f}")
    azure_usd = round(sum(per["azure"][lng]["est_usd"] for lng in plan["azure"]), 2)
    print(f"\nPlanned cloud spend (after caps): "
          f"AWS ${round(sum(per['aws'][l]['est_usd'] for l in plan['aws']),2):.2f}  "
          f"GCP ${round(sum(per['gcp'][l]['est_usd'] for l in plan['gcp']),2):.2f}  "
          f"Azure ${azure_usd:.2f}")
    print("GCP DLP is < 1 GB → free. Azure dominates (per-document 1,000-char rounding); the run halts for")
    print("confirmation before any spend — see run_full_leaderboard.sh --max-azure-usd.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
