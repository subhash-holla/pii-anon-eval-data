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
        # FIREWALL: this registry is the frozen-63 PROJECTION of whatever the current leaderboard is. The
        # live corpus canonical has since grown (63 -> 66, the 3 GDPR Art-9 types in 2C), so the source run
        # is scored against >= 63 types; we project its reachability onto the frozen 63 and never widen it.
        assert cov["of_total"] >= 63, f"{name}: run coverage of_total < 63 (source below the frozen basis)"
        native_map = dict(registry.load_adapter(name).label_map)
        # The adapter map's canonical targets, projected onto the frozen 63 (drop None + any non-63 target).
        reachable_from_map = sorted({v for v in native_map.values() if v in c63_set})
        run_reachable = sorted(set(cov["reachable_types"]) & c63_set)  # project the run onto the frozen 63
        assert reachable_from_map == run_reachable, (
            f"{name}: adapter map projects to {reachable_from_map} but the scored run says {run_reachable}"
        )
        detectors[name] = {
            "native_to_canonical": native_map,
            "reachable_types": run_reachable,
            "reachable_count": len(run_reachable),  # count of the frozen-63 projection (matches reachable_types)
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
