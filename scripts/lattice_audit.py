"""Shared committed-cell positive audit + deficit math (P4; FR-029, NFR-018).

ONE module used by BOTH the enrichment fill (to compute deficits) and ``validate.py`` (to
enforce the gate) — so "what we fill" == "what we enforce" (no drift). Counts gold positive
annotations per COMMITTED, COUNT-GATED cell in a single streaming pass; per annotation it does
O(1) candidate-key lookups against a dict keyed by the lattice's own dimension tuples (the key
set is bounded by #committed-cells, not the cross-product).

v1 counts RAW positives. A typed seam (``effective=False``) is reserved for the near-duplicate-
collapsed *effective* positive count (reidx-04) — flagged, not silently CI-inflating.
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _p in (str(_HERE), str(_HERE.parent), str(_HERE.parent / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pii_anon_datasets.stats import lattice as _lattice  # noqa: E402

load_lattice = _lattice.load_lattice
LATTICE_PATH = _lattice.LATTICE_PATH


def committed_index(lattice: dict) -> dict:
    """canonical dimension-tuple -> committed COUNT-GATED cell (the audit/enforcement lookup)."""
    return {
        tuple(sorted(c["dimensions"].items())): c
        for c in lattice["cells"] if c["count_gated"]
    }


def _record_coords(rec: dict) -> dict:
    adv = (rec.get("adversarial") or {}).get("type")
    return {
        "language": rec.get("language"),
        "domain": rec.get("domain"),
        "difficulty": rec.get("difficulty_level"),
        "dimension": rec.get("primary_dimension"),
        "adversarial": adv,
        "adv_track": "clean" if adv is None else "adversarial",
    }


def _candidate_keys(coords: dict, entity_type: str) -> list[tuple]:
    """Every committed-cell dimension-tuple a single annotation could match."""
    keys = [
        (("entity_type", entity_type),),
        (("language", coords["language"]),),
        (("domain", coords["domain"]),),
        (("difficulty", coords["difficulty"]),),
        (("dimension", coords["dimension"]),),
        tuple(sorted((("entity_type", entity_type), ("language", coords["language"])))),
        tuple(sorted((("adv_track", coords["adv_track"]), ("domain", coords["domain"])))),
    ]
    if coords["adversarial"] is not None:
        keys.append((("adversarial", coords["adversarial"]),))
        keys.append(tuple(sorted((("adversarial", coords["adversarial"]), ("entity_type", entity_type)))))
    return keys


def record_increments(rec: dict, index: dict) -> Counter:
    """Counter of committed cell_id -> number of this record's annotations that hit it."""
    coords = _record_coords(rec)
    inc: Counter = Counter()
    for ann in rec.get("annotations", []):
        et = ann.get("entity_type")
        if et is None:
            continue
        for key in _candidate_keys(coords, et):
            cell = index.get(key)
            if cell is not None:
                inc[cell["id"]] += 1
    return inc


def audit_positives(corpus_path, lattice: dict, *, effective: bool = False) -> dict:
    """One streaming pass → {cell_id: observed positive count} for committed count-gated cells.

    ``effective=True`` (near-duplicate-collapsed counts, reidx-04) is a reserved seam — NotImplemented
    until the shingle/MinHash collapser lands, so the gate is never silently dedup-inflated.
    """
    if effective:
        raise NotImplementedError(
            "effective (near-duplicate-collapsed) counts are a reserved seam (reidx-04); v1 uses raw counts"
        )
    index = committed_index(lattice)
    counts: Counter = Counter({c["id"]: 0 for c in lattice["cells"] if c["count_gated"]})
    path = Path(corpus_path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            counts.update(record_increments(json.loads(line), index))
    return dict(counts)


def deficits(counts: dict, lattice: dict) -> list[dict]:
    """Committed count-gated cells below their tiered target, sorted by id (deterministic)."""
    out = []
    for c in lattice["cells"]:
        if not c["count_gated"]:
            continue
        have = counts.get(c["id"], 0)
        if have < c["target_n"]:
            out.append({**c, "observed": have, "deficit": c["target_n"] - have})
    out.sort(key=lambda c: c["id"])
    return out
