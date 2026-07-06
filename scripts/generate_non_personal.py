#!/usr/bin/env python3
"""Generate >=400 records whose ONLY entities are non-personal (ORGANIZATION_NAME / URL /
INVOICE_NUMBER / VEHICLE_MODEL / TIMESTAMP) and which carry NO gdpr/ccpa regulatory tag, so the
record-level crosswalk emits reg_gdpr = out_of_scope (makes reg_gdpr discriminative).

Deterministic/seeded (AX-002), synthetic-only (AX-001). v1-shaped for merge_and_rebuild.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from generate_records import PIIFactory, build_record  # noqa: E402
from lattice_targeting import EMITTERS  # noqa: E402

SEED = 20260618
NONPERSONAL = ["ORGANIZATION_NAME", "URL", "INVOICE_NUMBER", "VEHICLE_MODEL", "TIMESTAMP"]
LANGS = ["en", "nl", "pt", "it", "es", "fr", "de"]  # Latin powered subset (non-personal emitters are English-anchored)
TOTAL = 420  # >=400
OUT = os.path.join(os.path.dirname(__file__), "..", "pii_anon_non_personal.jsonl")


def _seed(*parts: object) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:16], 16)


def main() -> int:
    n = 0
    with open(OUT, "w", encoding="utf-8") as fout:
        for i in range(TOTAL):
            lang = LANGS[i % len(LANGS)]
            rng = random.Random(_seed(SEED, "nonpersonal", i))
            factory = PIIFactory(rng, lang)
            pair = rng.sample(NONPERSONAL, 2)
            slots = {"a": EMITTERS[pair[0]](factory), "b": EMITTERS[pair[1]](factory)}
            template = "Asset record — {a}; reference {b}."
            rec = build_record(
                template, slots,
                language=lang,
                primary_dimension="format_variations",
                domain="technology",
                difficulty="easy",
                rng=rng,
            )
            # No personal entity → not GDPR/CCPA material scope (record-level crosswalk is tag-driven).
            rec["regulatory_domains"] = []
            rec["_non_personal"] = True   # marker so enrich.py leaves regulatory_domains empty
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    print(f"wrote {n} non-personal records -> {os.path.relpath(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
