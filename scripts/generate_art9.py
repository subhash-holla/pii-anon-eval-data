#!/usr/bin/env python3
"""Generate >=400 GDPR Art-9 special-category spans per type across the 12 powered languages.

Synthetic-only (AX-001). Record CONTENT (text + annotation offsets/types) is seeded and deterministic
(AX-002); the transient `record_id` from `build_record` (uuid4) is NOT byte-stable here but is REPLACED
with a content-addressed deterministic id by `merge_and_rebuild` (`migration.migrate_record`), so the
final corpus is fully reproducible. Uses the committed `gen_targeted_record` primitive (one positive of
the target type per record, + a person name + email = a realistic Art-9 record). Writes v1-shaped
records to pii_anon_art9.jsonl for merge_and_rebuild to pick up.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from generate_records import PIIFactory  # noqa: E402
from lattice_targeting import gen_targeted_record  # noqa: E402

SEED = 20260618
ART9_TYPES = [
    "SEXUAL_ORIENTATION", "TRADE_UNION_MEMBERSHIP", "GENETIC_DATA",
    "POLITICAL_OPINION", "RELIGIOUS_BELIEF", "ETHNICITY",
]
POWERED_LANGS = ["en", "nl", "hi", "ko", "pt", "it", "es", "ar", "zh", "fr", "ja", "de"]
DOMAINS = ["general", "clinical", "financial", "legal", "technology"]
DIFFICULTIES = ["easy", "moderate", "hard", "challenging"]
PER_TYPE_NEW = 408  # >=400; 34 per powered language (guarantees >=400 even for the 3 absent types)
OUT = os.path.join(os.path.dirname(__file__), "..", "pii_anon_art9.jsonl")


def _seed(*parts: object) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:16], 16)


def main() -> int:
    n = 0
    with open(OUT, "w", encoding="utf-8") as fout:
        for etype in ART9_TYPES:
            for li, lang in enumerate(POWERED_LANGS):
                per_lang = PER_TYPE_NEW // len(POWERED_LANGS) + (1 if li < PER_TYPE_NEW % len(POWERED_LANGS) else 0)
                rng = random.Random(_seed(SEED, etype, lang))
                factory = PIIFactory(rng, lang)
                for i in range(per_lang):
                    rec = gen_targeted_record(
                        factory,
                        entity_type=etype,
                        language=lang,
                        domain=rng.choice(DOMAINS),
                        difficulty=rng.choice(DIFFICULTIES),
                        adversarial_type=None,
                        rng=rng,
                        nonce=f"a9-{etype[:4]}-{lang}-{i}",
                    )
                    fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    n += 1
    print(f"wrote {n} Art-9 records -> {os.path.relpath(OUT)} "
          f"({len(ART9_TYPES)} types x {len(POWERED_LANGS)} langs, >=400/type)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
