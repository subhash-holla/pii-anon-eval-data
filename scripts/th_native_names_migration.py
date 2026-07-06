#!/usr/bin/env python3
"""v2.2.0 SP-I: Thai romanized -> native-script name migration (approach γ').

Deterministic, streaming, in-place (`.tmp` + atomic replace), naturally idempotent. Rewrites Thai
PERSON_NAME (token-wise, variant-agnostic) and name-derived EMAIL_ADDRESS (segment-wise) span values to
Thai script via a fixed romanized->native map, recomputing span offsets. Non-Thai records pass through
byte-identical. Does NOT re-stamp version (content stays 2.1.0 until SP-III).

Usage:
  PYTHONPATH=src python scripts/th_native_names_migration.py --dry-run            # report only, write nothing
  PYTHONPATH=src python scripts/th_native_names_migration.py --in PATH            # one file
  PYTHONPATH=src python scripts/th_native_names_migration.py                      # ALL canonical sources, in place
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))  # generate_records
import generate_records as gr  # noqa: E402

# romanized (lowercased) -> Thai-script, built from the index-parallel lists in generate_records.
TH_MAP: dict[str, str] = {
    **{r.lower(): n for r, n in zip(gr.FIRST_NAMES_TH, gr.FIRST_NAMES_TH_NATIVE, strict=True)},
    **{r.lower(): n for r, n in zip(gr.LAST_NAMES_TH, gr.LAST_NAMES_TH_NATIVE, strict=True)},
}

_TRAIL_DIGITS = re.compile(r"\d+$")
_HONORIFICS = {"mr.", "mrs.", "ms.", "dr."}  # intentional Latin in formal PERSON_NAME variant


def _has_residual_roman_tokens(text: str) -> bool:
    """True if any whitespace-token has ASCII letters and is NOT a known honorific (a romanized leftover)."""
    return any(any(c.isascii() and c.isalpha() for c in tok) and tok.lower() not in _HONORIFICS
               for tok in text.split(" "))


def translit_name(text: str) -> str:
    """Token-wise: map any whitespace-token whose lowercase is a known romanized Thai name; leave others."""
    return " ".join(TH_MAP.get(tok.lower(), tok) for tok in text.split(" "))


def translit_email(text: str) -> tuple[str, bool]:
    """Segment-wise on the local part: map the alpha part of each dotted segment (preserving a trailing
    digit run); leave domain + unmapped segments. Returns (new_email, changed)."""
    if "@" not in text:
        return text, False
    local, _, domain = text.partition("@")
    changed = False
    out = []
    for seg in local.split("."):
        m = _TRAIL_DIGITS.search(seg)
        num = m.group(0) if m else ""
        alpha = seg[: len(seg) - len(num)] if num else seg
        if alpha.lower() in TH_MAP:
            out.append(TH_MAP[alpha.lower()] + num)
            changed = True
        else:
            out.append(seg)
    return ".".join(out) + "@" + domain, changed


def migrate_record(rec: dict) -> tuple[dict, int, list]:
    """Rewrite Thai PERSON_NAME + name-derived EMAIL span values to Thai script, recomputing offsets.
    Returns (rec, n_spans_changed, flags). Non-Thai records and already-Thai records return unchanged."""
    flags: list = []
    if (rec.get("language") or rec.get("lang")) != "th":
        return rec, 0, flags
    text = rec.get("text", "")
    anns = rec.get("annotations") or []

    new_vals: dict[int, str] = {}  # id(ann) -> new span text
    for a in anns:
        et = a.get("entity_type")
        old = a.get("text", "")
        if et == "PERSON_NAME":
            new = translit_name(old)
            if new != old:
                new_vals[id(a)] = new
                if _has_residual_roman_tokens(new):
                    flags.append(("person_name_residual_romanized", a.get("mention_variant"), new))
            elif any(c.isascii() and c.isalpha() for c in old):
                # unchanged AND still has Latin letters => a romanized name we failed to map (not already-Thai)
                flags.append(("person_name_unmapped", a.get("mention_variant"), old))
        elif et == "EMAIL_ADDRESS":
            new, changed = translit_email(old)
            if changed and new != old:
                new_vals[id(a)] = new
                local = new.split("@")[0]
                if any(c.isascii() and c.isalpha() for c in local):
                    flags.append(("email_residual_romanized", None, new))

    if not new_vals:
        return rec, 0, flags

    edits = []  # (start, end, new)
    for a in anns:
        if id(a) in new_vals:
            if text[a["start"]:a["end"]] != a["text"]:
                raise ValueError(f"pre-migration offset drift at {a['start']}:{a['end']}")
            edits.append((a["start"], a["end"], new_vals[id(a)]))
    edits.sort(key=lambda e: e[0])

    # rebuild text
    out, prev = [], 0
    for s, e, nv in edits:
        out.append(text[prev:s])
        out.append(nv)
        prev = e
    out.append(text[prev:])
    new_text = "".join(out)

    def delta_before(pos: int) -> int:
        return sum(len(nv) - (e - s) for s, e, nv in edits if e <= pos)

    for a in anns:
        s, e = a["start"], a["end"]
        if id(a) in new_vals:
            nv = new_vals[id(a)]
            ns = s + delta_before(s)
            a["start"], a["end"], a["text"] = ns, ns + len(nv), nv
        else:
            d = delta_before(s)
            a["start"], a["end"] = s + d, e + d

    rec["text"] = new_text
    for a in anns:  # post-assert every span aligns
        if new_text[a["start"]:a["end"]] != a["text"]:
            raise ValueError(f"post-migration offset drift for {a.get('entity_type')}")
    return rec, len(edits), flags


_PKG = os.path.join(os.path.dirname(__file__), "..", "src", "pii_anon_datasets")
DEFAULT_IN = os.path.join(_PKG, "data", "pii_anon.jsonl.gz")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "results", "th_native_names_migration_report.md")


def canonical_sources() -> list[str]:
    pats = [os.path.join(_PKG, "data", "pii_anon.jsonl.gz"),
            os.path.join(_PKG, "splits", "*.jsonl.gz"),
            os.path.join(_PKG, "subsets", "**", "*.jsonl.gz")]
    out: list[str] = []
    for p in pats:
        out.extend(sorted(glob.glob(p, recursive=True)))
    seen: set[str] = set()
    return [p for p in out if not (p in seen or seen.add(p))]


def migrate_file(inp: str, *, dry_run: bool = False) -> dict:
    """Stream one jsonl.gz, migrating Thai records in place. Returns a stats dict; collects edge-case flags."""
    stats = {"file": os.path.relpath(inp), "records": 0, "th_records": 0, "records_changed": 0,
             "spans_changed": 0, "flags": []}
    tmp = inp + ".tmp"
    fout = None if dry_run else gzip.open(tmp, "wt", encoding="utf-8")
    try:
        with gzip.open(inp, "rt", encoding="utf-8") as fin:
            for line in fin:
                line = line.rstrip("\n")
                if not line:
                    continue
                stats["records"] += 1
                rec = json.loads(line)
                if (rec.get("language") or rec.get("lang")) == "th":
                    stats["th_records"] += 1
                rec, n, flags = migrate_record(rec)
                if n:
                    stats["records_changed"] += 1
                    stats["spans_changed"] += n
                for f in flags:
                    stats["flags"].append((rec.get("record_id"), *f))
                if fout is not None:
                    fout.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    except BaseException:
        if fout is not None:
            fout.close()
            if os.path.exists(tmp):
                os.remove(tmp)
        raise
    finally:
        if fout is not None and not fout.closed:
            fout.close()
    if not dry_run:
        os.replace(tmp, inp)
    return stats


def write_report(all_stats: list[dict]) -> None:
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    tot = {k: sum(s[k] for s in all_stats) for k in ("records", "th_records", "records_changed", "spans_changed")}
    flags = [(s["file"], *f) for s in all_stats for f in s["flags"]]
    lines = ["# Thai native-names migration report (v2.2.0 SP-I, approach γ′)", "",
             f"- sources migrated: {len(all_stats)}",
             f"- records scanned: {tot['records']:,}",
             f"- Thai records: {tot['th_records']:,}",
             f"- records changed: {tot['records_changed']:,}",
             f"- spans changed (PERSON_NAME + EMAIL): {tot['spans_changed']:,}",
             f"- edge-case flags (unmapped name/email left unchanged): {len(flags)}", "",
             "## Per-source", "", "| source | records | th | changed | spans |", "|---|---|---|---|---|"]
    for s in all_stats:
        lines.append(f"| {s['file']} | {s['records']:,} | {s['th_records']:,} | "
                     f"{s['records_changed']:,} | {s['spans_changed']:,} |")
    if flags:
        lines += ["", "## Edge cases (left unchanged, for review)", ""]
        for f in flags[:500]:
            lines.append(f"- `{f[0]}` {f[1]} :: {f[2:]}")
        if len(flags) > 500:
            lines.append(f"- … and {len(flags) - 500} more")
    lines += ["", "_Untouched name-bearing types (by design): USERNAME (not name-derived), "
              "ORGANIZATION_NAME / LOCATION_NAME / MEDICATION_NAME / PROCEDURE_NAME (non-person pools)._", ""]
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Thai romanized->native name migration (v2.2.0 SP-I).")
    ap.add_argument("--in", dest="inp", default=None, help="migrate one file (default: ALL canonical sources)")
    ap.add_argument("--dry-run", action="store_true", help="report only; write nothing")
    args = ap.parse_args(argv)
    sources = [args.inp] if args.inp else canonical_sources()
    print(f"{'DRY-RUN ' if args.dry_run else ''}migrating {len(sources)} source(s)...")
    all_stats = []
    for path in sources:
        s = migrate_file(path, dry_run=args.dry_run)
        all_stats.append(s)
        print(f"  {s['file']}: {s['records']:,} recs, {s['th_records']:,} th, "
              f"{s['records_changed']:,} changed, {s['spans_changed']:,} spans")
    write_report(all_stats)
    print(f"report -> {os.path.relpath(REPORT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
