"""Targeted stratified enrichment — fill every under-powered committed cell to its tiered
target (P4; NFR-018, FR-029; AX-001 synthetic-only, AX-002 deterministic+provenanced).

Reads the frozen committed lattice + the current corpus, computes per-cell deficits (shared
``lattice_audit``), and generates EXACTLY enough seeded synthetic records to close each deficit
— with a running counter so a record's incidental positives (e.g. the filler PERSON_NAME in an
IBAN record) reduce later cells' deficits and we never over-generate.

Determinism (AX-002): a per-cell sub-seed derived only from the cell id + the top-level
SEED_LATTICE, so each cell is independently reproducible and a partial re-run is a byte-identical
prefix. Records are stamped with lattice provenance then normalized to v2.0.0 via
``migration.migrate_record`` (closes the generators' v1-shape gap).

CLI:
  PYTHONPATH=.:scripts:src python scripts/generate_lattice_fill.py --dry-run     # report only
  PYTHONPATH=.:scripts:src python scripts/generate_lattice_fill.py                # write fill JSONL
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _p in (str(_HERE), str(_HERE.parent), str(_HERE.parent / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lattice_audit as audit  # noqa: E402
import lattice_targeting as lt  # noqa: E402
from pii_anon_datasets.migration import migrate_record  # noqa: E402
from pii_anon_datasets.stats import lattice as latmod  # noqa: E402

SEED_LATTICE = 91237   # distinct from core(42)/v120(162)/v130(172)/coverage(4242)
LATTICE_VERSION = latmod.LATTICE_VERSION
DATA_DIR = _HERE.parent / "src" / "pii_anon_datasets" / "data"
DEFAULT_CORPUS = DATA_DIR / "pii_anon.jsonl.gz"
DEFAULT_LATTICE = latmod.LATTICE_PATH
DEFAULT_OUTPUT = DATA_DIR / "pii_anon_lattice_fill.jsonl"

_FILL_DEFAULT_TYPES = ("PERSON_NAME", "EMAIL_ADDRESS", "PHONE_NUMBER")
_DIFFICULTIES = ("easy", "moderate", "hard", "challenging")


def cell_seed(cell_id: str) -> int:
    """Deterministic 64-bit per-cell sub-seed from cell coordinates only (order-independent)."""
    h = hashlib.sha256(f"{SEED_LATTICE}|{cell_id}".encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def cell_fill_params(cell: dict, rng: random.Random) -> dict:
    """Resolve gen_targeted_record kwargs from a cell's dimensions, choosing defaults for any
    dimension the cell does not pin (so entity-less cells — adv marginals, domain×adv_track — are
    fillable too). Every produced record adds exactly one positive to the target cell."""
    dims = cell["dimensions"]
    entity_type = dims.get("entity_type") or rng.choice(_FILL_DEFAULT_TYPES)
    language = dims.get("language") or "en"
    domain = dims.get("domain") or "general"
    difficulty = dims.get("difficulty") or rng.choice(_DIFFICULTIES)
    if "adversarial" in dims:
        adversarial_type = dims["adversarial"]
    elif dims.get("adv_track") == "adversarial":
        adversarial_type = rng.choice(latmod.DEFAULT_DETECTION_ADVERSARIAL_TYPES)
    else:
        adversarial_type = None
    return dict(entity_type=entity_type, language=language, domain=domain,
                difficulty=difficulty, adversarial_type=adversarial_type)


def _stamp(rec: dict, cell: dict, seed: int) -> dict:
    p = dict(rec.get("provenance") or {})
    p.update({
        "source_type": "synthetic_lattice_enrichment",
        "generation_seed": seed,
        "lattice_seed": SEED_LATTICE,
        "lattice_cell_id": cell["id"],
        "lattice_tier": cell["tier"],
        "lattice_version": LATTICE_VERSION,
    })
    rec["provenance"] = p
    return rec


def _synthetic_record(params: dict) -> dict:
    """A coords-only stand-in for a real targeted record (same annotation entity-types: target +
    PERSON_NAME + EMAIL_ADDRESS fillers). record_increments is identical to the real record's, so
    the estimate plan equals the real plan byte-for-byte (cell params come from an independent RNG)."""
    et = params["entity_type"]
    types = [et]
    if et != "PERSON_NAME":
        types.append("PERSON_NAME")
    if et != "EMAIL_ADDRESS":
        types.append("EMAIL_ADDRESS")
    return {
        "language": params["language"], "domain": params["domain"],
        "difficulty_level": params["difficulty"],
        "primary_dimension": "edge_cases" if params["adversarial_type"] else "diverse_pii_types",
        "adversarial": {"type": params["adversarial_type"]},
        "annotations": [{"entity_type": t} for t in types],
    }


def plan_fill(corpus_path: Path, lattice: dict, *, max_records: int | None = None,
              generate: bool = True):
    """Greedy deficit close with a running counter (incidental positives reduce later deficits).

    ``generate=True``  → emit real v2.0.0 records (returns them).
    ``generate=False`` → fast EXACT estimate (no text generated; returns []); identical plan/report
    because cell params come from an independent RNG and increments are coords-only.
    """
    index = audit.committed_index(lattice)
    observed = audit.audit_positives(corpus_path, lattice)
    running = dict(observed)
    gated = sorted((c for c in lattice["cells"] if c["count_gated"]), key=lambda c: c["id"])

    records: list[dict] = []
    per_cell: list[dict] = []
    total_made = 0
    stopped = False
    for cell in gated:
        need = cell["target_n"] - running.get(cell["id"], 0)
        if need <= 0:
            continue
        seed = cell_seed(cell["id"])
        params_rng = random.Random(seed)                       # independent of generation RNGs
        factory = lt.PIIFactory(random.Random(seed ^ 0x5DEECE66D),
                                cell["dimensions"].get("language") or "en") if generate else None
        gen_rng = random.Random(seed ^ 0x9E3779B9) if generate else None
        made = 0
        for _ in range(need):
            if running.get(cell["id"], 0) >= cell["target_n"]:
                break  # earlier incidental fills already satisfied this cell mid-loop
            if max_records is not None and total_made >= max_records:
                stopped = True
                break
            params = cell_fill_params(cell, params_rng)
            if generate:
                rec = lt.gen_targeted_record(factory, rng=gen_rng, nonce=f"{seed:x}-{made}", **params)
                rec = migrate_record(_stamp(rec, cell, seed))
                records.append(rec)
                inc = audit.record_increments(rec, index)
            else:
                inc = audit.record_increments(_synthetic_record(params), index)
            made += 1
            total_made += 1
            for cid, v in inc.items():
                running[cid] = running.get(cid, 0) + v
        if made:
            per_cell.append({"id": cell["id"], "tier": cell["tier"], "target": cell["target_n"],
                             "observed": observed.get(cell["id"], 0), "generated": made})
        if stopped:
            break

    report = {
        "committed_count_gated_cells": len(gated),
        "cells_filled": len(per_cell),
        "records_generated": total_made,
        "max_records_cap_hit": stopped,
        "per_cell": per_cell,
    }
    return records, report


def _baseline_records() -> int | None:
    meta = DATA_DIR / "pii_anon.metadata.json"
    if meta.exists():
        try:
            return json.loads(meta.read_text(encoding="utf-8")).get("total_records")
        except Exception:
            return None
    return None


def _print_report(report: dict, corpus_path: Path) -> None:
    print(f"== lattice fill plan — corpus {corpus_path.name} ==")
    print(f"  committed count-gated cells : {report['committed_count_gated_cells']}")
    print(f"  cells needing fill          : {report['cells_filled']}")
    print(f"  records to generate         : {report['records_generated']:,}")
    base = _baseline_records()
    if base:
        after = base + report["records_generated"]
        print(f"  projected corpus growth     : {base:,} -> {after:,} "
              f"(+{report['records_generated']/base*100:.0f}%, ×{after/base:.2f})")
    if report["max_records_cap_hit"]:
        print("  WARNING: --max-records cap hit; plan is TRUNCATED")
    by_tier: dict[str, int] = {}
    for c in report["per_cell"]:
        by_tier[c["tier"]] = by_tier.get(c["tier"], 0) + c["generated"]
    if by_tier:
        print(f"  records by tier             : {by_tier}")
    top = sorted(report["per_cell"], key=lambda c: -c["generated"])[:12]
    if top:
        print("  top cells by generated records:")
        for c in top:
            print(f"    {c['id']:56s} tier={c['tier']:9s} have={c['observed']:6d} +{c['generated']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Fill under-powered committed lattice cells (NFR-018).")
    ap.add_argument("--input", type=Path, default=DEFAULT_CORPUS)
    ap.add_argument("--lattice", type=Path, default=DEFAULT_LATTICE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--max-records", type=int, default=None, help="safety cap on records generated")
    ap.add_argument("--dry-run", action="store_true", help="report the plan + projected growth; write nothing")
    args = ap.parse_args(argv)

    lattice = audit.load_lattice(args.lattice)
    if args.dry_run:
        _, report = plan_fill(args.input, lattice, max_records=args.max_records, generate=False)
        _print_report(report, args.input)
        print("  (dry-run: no file written)")
        return 0

    records, report = plan_fill(args.input, lattice, max_records=args.max_records, generate=True)
    _print_report(report, args.input)

    with open(args.output, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"  wrote {len(records)} records -> {args.output}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
