#!/usr/bin/env python3
"""Canonicalize the `script` field to ISO 15924 (script = LANG_SCRIPT[language]) on the main corpus.

Fixes the genuine Latn mislabels (ta/te/my) AND collapses the human-readable duplicates
(Cyrillic->Cyrl, Bengali->Beng, ...). Run BEFORE generate_subsets.py so the re-derived splits/subsets
inherit canonical scripts. Streaming, count-checked, atomic (mirrors scripts/v2_0_0_to_v2_1_0.py).
"""
from __future__ import annotations

import gzip
import importlib.util
import json
import os
import sys
from pathlib import Path

_vcspec = importlib.util.spec_from_file_location("_vc", Path(__file__).resolve().parent / "validate_contribution.py")
_vc = importlib.util.module_from_spec(_vcspec)
_vcspec.loader.exec_module(_vc)
LANG_SCRIPT = _vc.LANG_SCRIPT

DEFAULT_IN = os.path.join(os.path.dirname(__file__), "..", "src", "pii_anon_datasets", "data", "pii_anon.jsonl.gz")


def main() -> int:
    inp = sys.argv[sys.argv.index("--in") + 1] if "--in" in sys.argv else DEFAULT_IN
    tmp = inp + ".tmp"
    n_in = n_out = changed = unmapped = 0
    with gzip.open(inp, "rt", encoding="utf-8") as fin, gzip.open(tmp, "wt", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            n_in += 1
            rec = json.loads(line)
            lang = rec.get("language")
            iso = LANG_SCRIPT.get(lang)
            if iso is None:
                unmapped += 1
            elif rec.get("script") != iso:
                rec["script"] = iso
                changed += 1
            fout.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
            n_out += 1
    if n_out != n_in:
        print(f"ABORT: count mismatch in={n_in} out={n_out}", file=sys.stderr)
        os.remove(tmp)
        return 1
    os.replace(tmp, inp)
    print(f"canonicalized {n_out} records -> {os.path.relpath(inp)} (changed={changed}, unmapped_lang={unmapped})")
    if unmapped:
        print(f"WARNING: {unmapped} records have a language not in LANG_SCRIPT — extend the map", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
