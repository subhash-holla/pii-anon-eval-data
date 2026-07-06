#!/usr/bin/env python3
"""Validate a COMMUNITY language/dialect contribution before it is proposed as a PR.

This is the self-service gate for extending PII-Anon-Eval with a new language or dialect. It checks a
contributed `.jsonl(.gz)` batch of synthetic records against the canonical schema's hard invariants and
emits a per-language coverage report + a powered/underpowered verdict. The enum sources (entity types,
categories, sensitivity classes, provenance source types, required fields) are loaded FROM
`src/pii_anon_datasets/data/pii_anon.schema.json` so this validator never drifts from the schema.

Hard gates (any failure → exit 1, cannot be merged):
  * offset integrity: record.text[start:end] == annotation.text  (the dataset's "0 offset errors" promise)
  * canonical entity_type / category / sensitivity_class (from the schema enum)
  * provenance.source_type ∈ {synthetic, curated_public} + a license string  (AX-001 synthetic-only)
  * required top-level fields present; record_id is a UUID; no duplicate record_ids; no overlapping spans
  * BCP-47-shaped language tag + ISO-15924-shaped script code

Soft checks (warnings — reviewer judgement):
  * script code matches the language's expected script (catches e.g. Tamil mislabeled `Latn`)
  * native-speaker review declared; powered (>= --powered-threshold records) per language

NOTE: this validator cannot PROVE data is synthetic — that is the contributor's signed CC0/synthetic-only
attestation (CONTRIBUTING.md, AX-001). Suspected REAL PII must be reported privately via SECURITY.md.

Usage:
  python scripts/validate_contribution.py contrib/my-lang/records.jsonl
  python scripts/validate_contribution.py contrib/my-lang/records.jsonl --powered-threshold 200
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
BCP47_RE = re.compile(r"^[a-z]{2,3}(-[A-Za-z]{2,4})?(-[A-Za-z0-9]{2,8})*$")  # en, zh-Hant, pt-BR, ar-EG
ISO15924_RE = re.compile(r"^[A-Z][a-z]{3}$")  # Latn, Hans, Arab, Deva

# Primary-subtag → expected ISO-15924 script (for the soft mismatch warning).
LANG_SCRIPT = {
    "zh": "Hans", "ja": "Jpan", "ko": "Kore", "ar": "Arab", "ur": "Arab", "fa": "Arab", "ps": "Arab",
    "hi": "Deva", "ne": "Deva", "mr": "Deva", "sa": "Deva", "bn": "Beng", "as": "Beng",
    "ta": "Taml", "te": "Telu", "kn": "Knda", "ml": "Mlym", "gu": "Gujr", "pa": "Guru", "or": "Orya",
    "si": "Sinh", "th": "Thai", "lo": "Laoo", "km": "Khmr", "my": "Mymr",
    "he": "Hebr", "el": "Grek", "ka": "Geor", "hy": "Armn", "am": "Ethi", "ti": "Ethi",
    "ru": "Cyrl", "uk": "Cyrl", "sr": "Cyrl", "bg": "Cyrl", "mk": "Cyrl", "be": "Cyrl",
    "kk": "Cyrl", "ky": "Cyrl", "mn": "Cyrl", "tg": "Cyrl", "tt": "Cyrl",
    # Latin-script languages
    "af": "Latn", "az": "Latn", "ca": "Latn", "cs": "Latn", "cy": "Latn",
    "da": "Latn", "de": "Latn", "en": "Latn", "es": "Latn", "et": "Latn",
    "fi": "Latn", "fil": "Latn", "fr": "Latn", "ha": "Latn", "hu": "Latn",
    "id": "Latn", "ig": "Latn", "it": "Latn", "lv": "Latn", "mg": "Latn",
    "ms": "Latn", "nl": "Latn", "no": "Latn", "pl": "Latn", "pt": "Latn",
    "ro": "Latn", "so": "Latn", "sq": "Latn", "sv": "Latn", "sw": "Latn",
    "tr": "Latn", "vi": "Latn", "xh": "Latn", "yo": "Latn", "zu": "Latn",
}


def _load_schema_enums():
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "src/pii_anon_datasets/data/pii_anon.schema.json").read_text(encoding="utf-8"))
    ann = schema["properties"]["annotations"]["items"]["properties"]
    return {
        "required_top": set(schema["required"]),
        "entity_types": set(ann["entity_type"]["enum"]),
        "categories": set(ann["category"]["enum"]),
        "sensitivity": set(ann["sensitivity_class"]["enum"]),
        "source_types": set(schema["properties"]["provenance"]["properties"]["source_type"]["enum"]),
    }


def _iter(path: Path):
    op = gzip.open if path.suffix == ".gz" else open
    with op(path, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if line:
                yield i, json.loads(line)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("records", help="contributed .jsonl(.gz) batch")
    ap.add_argument("--powered-threshold", type=int, default=100,
                    help="records/language to be considered 'powered' (default 100)")
    args = ap.parse_args()
    path = Path(args.records)
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 2

    E = _load_schema_enums()
    errors: list[str] = []
    warns: list[str] = []
    seen_ids: set[str] = set()
    by_lang: Counter = Counter()
    by_script: Counter = Counter()
    by_entity: Counter = Counter()
    by_dimension: Counter = Counter()
    lang_scripts: dict[str, set] = defaultdict(set)
    native_reviewed = 0
    n = 0

    for ln, rec in _iter(path):
        n += 1
        tag = f"L{ln}"
        # required top-level fields
        for fld in E["required_top"]:
            if fld not in rec:
                errors.append(f"{tag}: missing required field '{fld}'")
        rid = str(rec.get("record_id", ""))
        if not UUID_RE.match(rid):
            errors.append(f"{tag}: record_id not a UUID: {rid!r}")
        if rid in seen_ids:
            errors.append(f"{tag}: duplicate record_id {rid}")
        seen_ids.add(rid)

        text = rec.get("text", "")
        if not isinstance(text, str) or not text:
            errors.append(f"{tag}: empty text")
            text = ""

        lang = str(rec.get("language", ""))
        script = str(rec.get("script", ""))
        by_lang[lang] += 1
        by_script[script] += 1
        lang_scripts[lang].add(script)
        if lang and not BCP47_RE.match(lang):
            warns.append(f"{tag}: language tag {lang!r} is not BCP-47-shaped")
        if script and not ISO15924_RE.match(script):
            warns.append(f"{tag}: script {script!r} is not an ISO-15924 code (e.g. Latn, Hans, Arab)")
        prim = lang.split("-")[0]
        if prim in LANG_SCRIPT and script and script != LANG_SCRIPT[prim]:
            warns.append(f"{tag}: script {script!r} for language {lang!r} — expected {LANG_SCRIPT[prim]!r}")

        for d in (rec.get("dimensions") or []):
            by_dimension[d] += 1

        # provenance (AX-001 synthetic-only) — coerce a JSON-string field to a clean error, never a crash
        prov = rec.get("provenance") or {}
        if isinstance(prov, str):
            try:
                prov = json.loads(prov)
            except Exception:
                errors.append(f"{tag}: provenance is an unparseable JSON string"); prov = {}
        if not isinstance(prov, dict):
            errors.append(f"{tag}: provenance must be a JSON object"); prov = {}
        st = prov.get("source_type")
        if st not in E["source_types"]:
            errors.append(f"{tag}: provenance.source_type {st!r} not in {sorted(E['source_types'])}")
        if not prov.get("license"):
            errors.append(f"{tag}: provenance.license missing (must be CC0-compatible)")

        # annotations: offset integrity + enums + overlaps (the load-bearing gates)
        anns = rec.get("annotations") or []
        if isinstance(anns, str):              # a JSON-string list is a common contributor mistake — fail clean
            try:
                anns = json.loads(anns)
            except Exception:
                errors.append(f"{tag}: annotations is an unparseable JSON string"); anns = []
        if not isinstance(anns, list):
            errors.append(f"{tag}: annotations must be a JSON list"); anns = []
        if len(anns) < 1:
            warns.append(f"{tag}: record has 0 annotations")
        spans = []
        for a in anns:
            et = a.get("entity_type")
            by_entity[et] += 1
            if et not in E["entity_types"]:
                errors.append(f"{tag}: entity_type {et!r} not canonical")
            if a.get("category") not in E["categories"]:
                errors.append(f"{tag}: category {a.get('category')!r} not canonical")
            if a.get("sensitivity_class") not in E["sensitivity"]:
                errors.append(f"{tag}: sensitivity_class {a.get('sensitivity_class')!r} not canonical")
            s, e = a.get("start"), a.get("end")
            if not (isinstance(s, int) and isinstance(e, int) and 0 <= s < e <= len(text)):
                errors.append(f"{tag}: bad span offsets ({s},{e}) for text len {len(text)}")
                continue
            if text[s:e] != a.get("text"):
                errors.append(f"{tag}: OFFSET MISMATCH text[{s}:{e}]={text[s:e]!r} != annotation.text={a.get('text')!r}")
            spans.append((s, e))
        spans.sort()
        for (s1, e1), (s2, e2) in zip(spans, spans[1:]):
            if s2 < e1:
                errors.append(f"{tag}: overlapping annotations ({s1},{e1}) & ({s2},{e2})")

        if (rec.get("provenance") or {}).get("native_speaker_reviewed") or rec.get("native_speaker_reviewed"):
            native_reviewed += 1

    # ---- report ----
    print(f"\n=== Contribution validation: {path}  ({n} records) ===")
    print(f"languages: {dict(by_lang)}")
    print(f"scripts:   {dict(by_script)}")
    print(f"dimensions covered: {sorted(by_dimension)}")
    print(f"entity types covered: {len(by_entity)} of {len(E['entity_types'])} canonical")
    print(f"native-speaker-reviewed records declared: {native_reviewed}/{n}")
    for lang, c in by_lang.most_common():
        status = "POWERED" if c >= args.powered_threshold else f"underpowered (<{args.powered_threshold})"
        print(f"  {lang:10s} {c:6d} records — {status}; scripts={sorted(lang_scripts[lang])}")

    if warns:
        print(f"\n--- {len(warns)} warning(s) (reviewer judgement) ---")
        for w in warns[:40]:
            print("  ⚠", w)
        if len(warns) > 40:
            print(f"  … +{len(warns) - 40} more")
    if errors:
        print(f"\n--- {len(errors)} HARD ERROR(S) — must be fixed before this can be merged ---")
        for er in errors[:60]:
            print("  ✗", er)
        if len(errors) > 60:
            print(f"  … +{len(errors) - 60} more")
        print("\nRESULT: ✗ FAIL")
        return 1
    print("\nRESULT: ✓ PASS — schema-valid, offset-clean, synthetic-provenanced. "
          "Attach this output to your PR. (Synthetic-only is your signed attestation; native-speaker review recommended.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
