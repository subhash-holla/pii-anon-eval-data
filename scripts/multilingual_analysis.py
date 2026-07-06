#!/usr/bin/env python3
"""DEPRECATED (v2.2.0 cut) — SUPERSEDED by `scripts/multilingual_by_script_lb.py`, which regenerates BOTH
`multilingual_leaderboard.md` (per-language F2) AND `multilingual_by_script.md` from the current
`results/baselines/fulltest-local` aggregate (the same source as the BASELINES.md matrix). This script read
a separate per-record `results/per-record/multilingual` dump (retired to `_v200stale/` on the v2.2.0 cut)
and collided on the `multilingual_by_script.md` filename. Kept only for provenance; do NOT run it.

Multilingual leaderboard analysis — per-language + per-script-family detector performance, with an
Asian-language focus and a similar-vs-different-script breakdown. Pure post-processing over the
multilingual per-record dump (results/per-record/multilingual). No detector runs.

Script grouping is keyed off the BCP-47 LANGUAGE CODE → canonical script (reliable), NOT the dataset's
`script` column (which is inconsistent: Latn/Latin/… and mislabels e.g. Tamil/Telugu as Latn — surfaced
as a data-quality finding).

Outputs:
  * multilingual_leaderboard.md — per-language F2 for every detector (Asian languages flagged).
  * multilingual_by_script.md   — per-script-family pooled F2 + the cross-script collapse: each detector's
                                  mean F2 on Latin (non-English) vs non-Latin scripts, and which detectors
                                  transfer (gliner/piiranha) vs collapse (English-tuned NER).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

DETECTORS = ["gliner", "piiranha", "regex", "presidio", "spacy", "stanza", "scrubadub"]
MULTILINGUAL_CAPABLE = {"gliner", "piiranha", "regex"}  # the rest are English-tuned (collapse probes)

# BCP-47 language code → canonical script (reliable; overrides the buggy `script` column).
LANG_SCRIPT = {
    # Latin
    **{c: "Latin" for c in ["en", "de", "nl", "sv", "da", "no", "is", "af", "lb",
                            "es", "fr", "it", "pt", "ro", "ca", "gl",
                            "pl", "cs", "sk", "sl", "hr", "bs",
                            "vi", "id", "ms", "tl", "jv", "su", "ceb",
                            "sw", "yo", "ha", "ig", "zu", "xh", "mg", "so", "fil",
                            "tr", "az", "uz", "et", "fi", "hu", "lv", "lt", "cy", "ga", "sq", "eu", "mt"]},
    # Cyrillic
    **{c: "Cyrillic" for c in ["ru", "uk", "sr", "bg", "mk", "be", "kk", "ky", "mn", "tg", "tt"]},
    # East Asian
    "zh": "Han", "ja": "Japanese", "ko": "Hangul",
    # Arabic
    **{c: "Arabic" for c in ["ar", "ur", "fa", "ps", "sd", "ug"]},
    # Brahmic / Indic
    "hi": "Devanagari", "ne": "Devanagari", "mr": "Devanagari", "sa": "Devanagari",
    "bn": "Bengali", "as": "Bengali", "ta": "Tamil", "te": "Telugu", "kn": "Kannada",
    "ml": "Malayalam", "gu": "Gujarati", "pa": "Gurmukhi", "or": "Odia", "si": "Sinhala",
    # SE Asian
    "th": "Thai", "lo": "Lao", "km": "Khmer", "my": "Myanmar",
    # Other
    "he": "Hebrew", "el": "Greek", "ka": "Georgian", "hy": "Armenian", "am": "Ethiopic", "ti": "Ethiopic",
}
ASIAN = set(["zh", "ja", "ko", "hi", "ne", "mr", "bn", "as", "ta", "te", "kn", "ml", "gu", "pa", "or", "si",
             "th", "lo", "km", "my", "vi", "id", "ms", "tl", "jv", "su", "ceb", "ur", "fa", "ps", "ka", "hy",
             "kk", "ky", "mn", "uz", "tg", "ug", "sd"])
# raw-label canonicalizer for the fallback + the data-quality mismatch report
SCRIPT_CANON = {"Latn": "Latin", "Latin": "Latin", "Cyrl": "Cyrillic", "Cyrillic": "Cyrillic",
                "Arab": "Arabic", "Arabic": "Arabic", "Hans": "Han", "Hant": "Han", "CJK": "Han",
                "Jpan": "Japanese", "Kore": "Hangul", "Hangul": "Hangul", "Deva": "Devanagari",
                "Devanagari": "Devanagari", "Beng": "Bengali", "Bengali": "Bengali", "Taml": "Tamil",
                "Tamil": "Tamil", "Telu": "Telugu", "Telugu": "Telugu", "Sinh": "Sinhala", "Thai": "Thai",
                "Laoo": "Lao", "Lao": "Lao", "Khmr": "Khmer", "Khmer": "Khmer", "Mymr": "Myanmar",
                "Myanmar": "Myanmar", "Hebr": "Hebrew", "Hebrew": "Hebrew", "Grek": "Greek", "Greek": "Greek",
                "Geor": "Georgian", "Georgian": "Georgian", "Ethi": "Ethiopic", "Ethiopic": "Ethiopic"}


def _f2(tp, n_pred, n_gold):
    p = tp / n_pred if n_pred else 0.0
    r = tp / n_gold if n_gold else 0.0
    f2 = (5 * p * r / (4 * p + r)) if (4 * p + r) else 0.0
    return p, r, f2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", default="results/per-record/multilingual")
    ap.add_argument("--out", default="results/tier-a")
    args = ap.parse_args()
    dump, out = Path(args.dump), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    g = pq.read_table(dump / "gold.parquet").to_pydict()
    n = len(g["record_id"])
    lang = np.array(g["language"], dtype=object)
    raw_script = np.array(g["script"], dtype=object)
    gold_rid = g["record_id"]
    dets = [d for d in DETECTORS if (dump / f"hits_{d}.parquet").exists()]
    hits, npred = {}, {}
    for d in dets:
        ht = pq.read_table(dump / f"hits_{d}.parquet").to_pydict()
        assert len(ht["hit"]) == n and ht["record_id"] == gold_rid, f"{d}: gold misalignment"
        hits[d] = np.array(ht["hit"], dtype=bool)
        pc = pq.read_table(dump / f"predcounts_{d}.parquet").to_pydict()
        npred[d] = dict(zip(pc["record_id"], pc["n_pred"]))
    rec_lang = {}
    for rid, l in zip(gold_rid, lang):
        rec_lang.setdefault(rid, l)
    langs = sorted(set(lang.tolist()))
    print(f"Loaded {n:,} gold spans across {len(langs)} languages × {len(dets)} detectors", flush=True)

    # ONE canonical script per LANGUAGE, used consistently for numerator (gold mask) AND denominator
    # (n_pred). LANG_SCRIPT (language-code keyed) is authoritative; an unmapped language falls back to its
    # DOMINANT raw `script` value in the data (canonicalized) — applied the SAME way everywhere, so
    # numerator and denominator can never disagree (the fil/mg/so inconsistency). Unmapped langs are warned.
    dom_raw = {}
    for l, s in zip(lang.tolist(), raw_script.tolist()):
        dom_raw.setdefault(l, Counter())[s] += 1
    lang2script = {}
    for l in langs:
        if l in LANG_SCRIPT:
            lang2script[l] = LANG_SCRIPT[l]
        else:
            raw = dom_raw[l].most_common(1)[0][0]
            lang2script[l] = SCRIPT_CANON.get(raw, raw or "unknown")
            print(f"  [warn] language {l!r} not in LANG_SCRIPT — using data script {lang2script[l]!r}; add it to the map", flush=True)

    # canonical script per gold row (via lang2script) + data-quality mismatch tally vs the raw `script` column
    canon = np.array([lang2script[l] for l in lang.tolist()], dtype=object)
    mism = sum(1 for s, c in zip(raw_script.tolist(), canon.tolist()) if SCRIPT_CANON.get(s, s) != c)
    # per-detector n_pred by language (for per-language + per-script precision)
    npred_lang = {d: defaultdict(int) for d in dets}
    for d in dets:
        for rid, k in npred[d].items():
            npred_lang[d][rec_lang.get(rid, "unknown")] += k

    # ---- per-language table ----
    per_lang = {}
    for l in langs:
        mask = lang == l
        ng = int(mask.sum())
        np_l = {d: npred_lang[d].get(l, 0) for d in dets}
        row = {"n_gold": ng, "script": lang2script[l], "asian": l in ASIAN}
        for d in dets:
            tp = int(hits[d][mask].sum())
            p, r, f2 = _f2(tp, np_l[d], ng)
            row[d] = {"recall": r, "precision": p, "f2": f2}
        per_lang[l] = row

    # ---- per-script aggregation (numerator gold mask AND denominator n_pred BOTH via lang2script) ----
    scripts = sorted(set(canon.tolist()))
    per_script = {}
    for sc in scripts:
        mask = canon == sc
        ng = int(mask.sum())
        sc_langs = sorted(l for l in langs if lang2script[l] == sc)
        row = {"n_gold": ng, "n_lang": len(sc_langs), "langs": sc_langs}
        for d in dets:
            np_sc = sum(npred_lang[d].get(l, 0) for l in sc_langs)
            tp = int(hits[d][mask].sum())
            p, r, f2 = _f2(tp, np_sc, ng)
            row[d] = {"recall": r, "precision": p, "f2": f2, "n_pred": np_sc}
        per_script[sc] = row

    # similar-vs-different: mean detector F2 on Latin(non-en) vs non-Latin (both via lang2script)
    latin_nonen = [l for l in langs if lang2script[l] == "Latin" and l != "en"]
    nonlatin = [l for l in langs if lang2script[l] != "Latin"]

    def pooled_f2(det, lang_subset):
        mask = np.isin(lang, np.array(lang_subset, dtype=object))
        tp = int(hits[det][mask].sum())
        ng = int(mask.sum())
        npp = sum(npred_lang[det].get(l, 0) for l in lang_subset)
        return _f2(tp, npp, ng)[2], ng

    transfer = {}
    for d in dets:
        en_f2 = per_lang.get("en", {}).get(d, {}).get("f2", float("nan"))
        lat_f2, lat_n = pooled_f2(d, latin_nonen)
        nl_f2, nl_n = pooled_f2(d, nonlatin)
        transfer[d] = {"en": en_f2, "latin_nonen": lat_f2, "non_latin": nl_f2,
                       "drop_en_to_nonlatin": (en_f2 - nl_f2) if en_f2 == en_f2 else None}

    # ---- write JSON ----
    (out / "multilingual_analysis.json").write_text(json.dumps(
        {"per_language": per_lang, "per_script": per_script, "transfer": transfer,
         "n_gold": n, "n_languages": len(langs), "script_mismatch_rows": mism}, indent=2, default=float),
        encoding="utf-8")

    # ---- leaderboard md ----
    show = [d for d in ["gliner", "piiranha", "regex", "presidio", "spacy", "stanza", "scrubadub"] if d in dets]
    md = ["# Multilingual leaderboard — per-language F2 (all detectors)\n",
          f"{n:,} gold spans across **{len(langs)} languages** (per-language cap applied for balance). "
          f"F2, strict-v1. ⚠ = Asian language. Languages with very low n_gold are underpowered (wide CIs).\n",
          "| Lang | Script | n_gold | " + " | ".join(show) + " |",
          "|---|---|---:|" + "---:|" * len(show)]
    for l in sorted(langs, key=lambda x: per_lang[x]["n_gold"], reverse=True):
        r = per_lang[l]
        flag = " ⚠" if r["asian"] else ""
        md.append(f"| {l}{flag} | {r['script']} | {r['n_gold']:,} | "
                  + " | ".join(f"{r[d]['f2']:.3f}" for d in show) + " |")
    (out / "multilingual_leaderboard.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # ---- by-script md ----
    md2 = ["# Multilingual performance by script family (similar vs different scripts)\n",
           "Detectors pooled per canonical script (keyed off language code, not the buggy `script` column). "
           "F2, strict-v1.\n",
           "| Script | #lang | n_gold | " + " | ".join(show) + " |",
           "|---|---:|---:|" + "---:|" * len(show)]
    for sc in sorted(scripts, key=lambda s: per_script[s]["n_gold"], reverse=True):
        r = per_script[sc]
        md2.append(f"| {sc} | {r['n_lang']} | {r['n_gold']:,} | "
                   + " | ".join(f"{r[d]['f2']:.3f}" for d in show) + " |")
    md2 += ["\n## Cross-script transfer — English vs Latin(non-EN) vs non-Latin\n",
            "Does performance survive a change of writing system? (mean pooled F2)\n",
            "| Detector | type | English | Latin (non-EN) | non-Latin | EN→non-Latin drop |",
            "|---|---|---:|---:|---:|---:|"]
    for d in show:
        t = transfer[d]
        kind = "multilingual" if d in MULTILINGUAL_CAPABLE else "English-tuned"
        drop = t["drop_en_to_nonlatin"]
        md2.append(f"| {d} | {kind} | {t['en']:.3f} | {t['latin_nonen']:.3f} | {t['non_latin']:.3f} | "
                   + (f"{drop:+.3f}" if drop is not None else "—") + " |")
    md2 += ["\n## Asian-language focus (multilingual-capable detectors)\n",
            "| Lang | Script | n_gold | " + " | ".join(d for d in show if d in MULTILINGUAL_CAPABLE) + " |",
            "|---|---|---:|" + "---:|" * len([d for d in show if d in MULTILINGUAL_CAPABLE])]
    asian_present = [l for l in langs if per_lang[l]["asian"]]
    for l in sorted(asian_present, key=lambda x: per_lang[x]["n_gold"], reverse=True):
        r = per_lang[l]
        md2.append(f"| {l} | {r['script']} | {r['n_gold']:,} | "
                   + " | ".join(f"{r[d]['f2']:.3f}" for d in show if d in MULTILINGUAL_CAPABLE) + " |")
    md2.append(f"\n_Data-quality note: {mism:,} gold rows have a `script` column value inconsistent with the "
               "language code's canonical script (e.g. Tamil/Telugu tagged `Latn`); the analysis uses the "
               "language-derived script and recommends canonicalizing the `script` field._")
    (out / "multilingual_by_script.md").write_text("\n".join(md2) + "\n", encoding="utf-8")

    print("Wrote multilingual_leaderboard.md, multilingual_by_script.md, multilingual_analysis.json", flush=True)
    print(f"  languages: {len(langs)}; script-field mismatches: {mism:,}", flush=True)
    for d in ("gliner", "piiranha"):
        if d in transfer:
            print(f"  {d}: en F2={transfer[d]['en']:.3f}  Latin(non-en)={transfer[d]['latin_nonen']:.3f}  "
                  f"non-Latin={transfer[d]['non_latin']:.3f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
