"""Tests for sub-project 2F: gold spot-check sampler + aggregator."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import gold_spotcheck_sample as gss  # noqa: E402

PRIORITY = ("Cyrl", "Thai", "Grek", "Beng", "Hebr", "Latn")


def _fake_corpus():
    # 8 types x several scripts; enough population per (script,type) to exercise floors.
    recs = []
    types = ["PERSON_NAME", "EMAIL_ADDRESS", "IBAN", "GENETIC_DATA", "PHONE_NUMBER",
             "SSN_RARE", "ETHNICITY", "API_KEY"]
    scripts = list(PRIORITY) + ["Hans", "Arab"]
    rid = 0
    for sc in scripts:
        for t in types:
            for _ in range(40):  # population 40 per (script,type)
                rid += 1
                recs.append({"record_id": f"r{rid}", "language": "en", "script": sc,
                             "text": f"x {t} y", "annotations": [{"entity_type": t, "start": 2, "end": 2 + len(t), "text": t}]})
    return recs


def test_sampler_deterministic_and_floors():
    a = gss.sample(_fake_corpus(), total=300, seed=gss.SEED)
    b = gss.sample(_fake_corpus(), total=300, seed=gss.SEED)
    assert [r["span_id"] for r in a] == [r["span_id"] for r in b], "same seed -> identical sample"
    # per-type floor: every type present has >= 2
    from collections import Counter
    by_type = Counter(r["entity_type"] for r in a)
    assert all(v >= 2 for v in by_type.values()), by_type
    # priority-script floor: each priority script present has >= 24
    by_script = Counter(r["script"] for r in a)
    for sc in PRIORITY:
        assert by_script[sc] >= 24, (sc, by_script[sc])
    # p_incl recorded, in (0,1]; blind ~25%
    assert all(0 < r["p_incl"] <= 1 for r in a)
    blind_frac = sum(r["blind"] for r in a) / len(a)
    assert 0.15 <= blind_frac <= 0.35, blind_frac


import csv as _csv  # noqa: E402

import gold_spotcheck_aggregate as gsa  # noqa: E402


def _write_mock(path):
    # c#0 is a BLIND row: its entity_type is WITHHELD in the review CSV (true type lives only in the key).
    rows = [
        # p_incl=0.5 -> w=2 ; p_incl=0.1 -> w=10 (long-tail, upweighted)
        {"span_id": "a#0", "script": "Latn", "entity_type": "PERSON_NAME", "p_incl": "0.5", "blind": "0",
         "type_correct": "1", "realistic": "1", "recovered_type": "", "note": ""},
        {"span_id": "b#0", "script": "Latn", "entity_type": "PERSON_NAME", "p_incl": "0.5", "blind": "0",
         "type_correct": "1", "realistic": "0", "recovered_type": "", "note": "english value"},
        {"span_id": "c#0", "script": "Cyrl", "entity_type": "", "p_incl": "0.1", "blind": "1",
         "type_correct": "0", "realistic": "1", "recovered_type": "PERSON_NAME", "note": "mislabel"},
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("# header\n")
        w = _csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _write_key(path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("# key\n")
        w = _csv.DictWriter(f, fieldnames=["span_id", "entity_type"])
        w.writeheader()
        for sid, t in (("a#0", "PERSON_NAME"), ("b#0", "PERSON_NAME"), ("c#0", "GENETIC_DATA")):
            w.writerow({"span_id": sid, "entity_type": t})


def test_ht_weighted_rate_corrects_long_tail(tmp_path):
    p = tmp_path / "filled.csv"
    kp = tmp_path / "key.csv"
    _write_mock(p)
    _write_key(kp)
    rows = gsa.read_filled(str(p))
    key = gsa.load_key(str(kp))
    # type_correct: weighted = (2*1 + 2*1 + 10*0)/(2+2+10) = 4/14 ≈ 0.2857 (long-tail 0 dominates via weight)
    res = gsa.weighted_rate(rows, "type_correct")
    assert abs(res["rate"] - 4 / 14) < 1e-6
    assert res["eff_n"] > 0 and 0 <= res["ci"][0] <= res["rate"] <= res["ci"][1] <= 1
    # blind type-recovery: 1 blind row (entity_type withheld in CSV); recovered PERSON_NAME but the KEY's
    # true type is GENETIC_DATA -> 0/1. Proves the recovery is scored against the answer key, not the CSV.
    rec = gsa.blind_recovery_rate(rows, key)
    assert rec["n"] == 1 and rec["rate"] == 0.0
    # the blind row groups under its KEY true type (GENETIC_DATA), not under "" (per-type uses the key)
    by_type = gsa.per_group_cells(rows, key, "entity_type", "type_correct")
    assert "GENETIC_DATA" in by_type and "" not in by_type


def test_render_and_main_smoke(tmp_path):
    p = tmp_path / "filled.csv"
    kp = tmp_path / "key.csv"
    _write_mock(p)
    _write_key(kp)
    out = tmp_path / "gold_spotcheck.md"
    rc = gsa.main(["--input", str(p), "--key", str(kp), "--md", str(out)])
    assert rc == 0
    md = out.read_text(encoding="utf-8")
    assert "corroboration rate" in md.lower()
    assert "NOT" in md and ("kappa" in md.lower() or "inter-annotator" in md.lower())  # AX-002 framing present
    assert "UNDERPOWERED" in md  # descriptive cells flagged
    assert "Blind type-recovery" in md and "1 blind spans" in md  # blind recovery now functional
