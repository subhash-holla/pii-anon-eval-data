#!/usr/bin/env python3
"""Run the (built-but-never-run) measured Tier-3 re-identification adversary and publish a real
MeasuredRRS — superseding the shipped heuristic `re_identification_resistance_score` prior.

The SME panel found the shipped RRS is a closed-form transform of `behavioral_signal_density`
(no attacker), and that an ad-hoc run of the real adversary scored RRS~1.0 non-discriminating.
This script settles that honestly with a controlled experiment over the paired Tier-2/3 substrate
(records carrying `context_preservation` with 4 aligned anonymized variants of the same source text):

  * Build a closed-world candidate pool of N real Personas (gold signals + QI tokens from the ORIGINAL).
  * For each TARGET set — {ORIGINAL (control), masked, generalized, pseudonymized, llm_sanitized} —
    re-extract `observed_signals` from that text (reidx-01: never gold) and run
    `OfflineDeterministicAdversary` + `score_reidentification` against the SAME pool.
  * The ORIGINAL control is the discrimination probe: the original retains every QI token + signal,
    so the attack MUST re-identify it (low RRS / high recall). If the control also fails, the
    behavioral-signal substrate is too weak to be a re-id testbed (a dataset finding). If the
    control succeeds but the variants don't, anonymization is effective — and we can see whether
    RRS differs ACROSS variant strengths (the discrimination the SME said was absent).

Deterministic, offline, no LLM/RNG/clock. Output: results/tier-a/measured_rrs.{json,md}.

Usage: python scripts/measured_rrs.py --limit 2000 --out results/tier-a
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pii_anon_datasets import load_dataset
from pii_anon_datasets.scoring.adversary.base import Persona, Target
from pii_anon_datasets.scoring.adversary.offline_adversary import OfflineDeterministicAdversary
from pii_anon_datasets.scoring.reidentification import score_reidentification
from pii_anon_datasets.scoring.signals import extract

VARIANTS = [
    ("original_control", None),  # None ⇒ use rec["text"] (the discrimination probe)
    ("masked", "anonymized_masked"),
    ("generalized", "anonymized_generalized"),
    ("pseudonymized", "anonymized_pseudonymized"),
    ("llm_sanitized", "anonymized_llm_sanitized"),
]


def _cp(rec):
    cp = rec.get("context_preservation")
    if isinstance(cp, str):
        try:
            cp = json.loads(cp)
        except Exception:
            cp = None
    return cp if isinstance(cp, dict) else None


def _annotations(rec):
    a = rec.get("annotations") or []
    if isinstance(a, str):
        try:
            a = json.loads(a)
        except Exception:
            a = []
    return a if isinstance(a, list) else []


def _gold_signals(rec):
    """Candidate/persona (real) side reads GOLD tier3 behavioral_signals — reidx-01: only the pseudonymous
    TARGET re-extracts from anonymized text; the candidate substrate is gold. Falls back to extract(text)
    if the record carries no tier3 gold."""
    t3 = rec.get("tier3_evaluation")
    if isinstance(t3, str):
        try:
            t3 = json.loads(t3)
        except Exception:
            t3 = {}
    bs = (t3 or {}).get("behavioral_signals")
    return bs if isinstance(bs, dict) else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    ap.add_argument("--limit", type=int, default=2000, help="paired records to use (closed-world |C|)")
    ap.add_argument("--out", default="results/tier-a")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print("Loading records…", flush=True)
    recs = load_dataset(split=args.split, language=None)
    # deterministic selection: the first N records that carry all 4 variants
    paired = []
    for r in recs:
        cp = _cp(r)
        if cp and all(cp.get(k) for _, k in VARIANTS if k):
            paired.append((r, cp))
        if len(paired) >= args.limit:
            break
    n = len(paired)
    print(f"Paired records with all 4 variants: {n}", flush=True)
    if n < 50:
        print("Too few paired records; aborting.", flush=True)
        return 1

    # Candidate pool: one Persona per record (gold side, from the ORIGINAL text).
    print("Building persona pool (gold signals + QI tokens from originals)…", flush=True)
    personas = []
    for r, _cpd in paired:
        rid = str(r["record_id"])
        qis = tuple((str(a["entity_type"]), str(a.get("text") or "")) for a in _annotations(r) if a.get("text"))
        personas.append(
            Persona(
                persona_id=rid,
                record_id=rid,
                quasi_identifiers=qis,
                behavioral_signals=_gold_signals(r) or extract(str(r.get("text", "") or "")),
                source_text=str(r.get("text", "") or ""),
            )
        )
    cset = len(personas)  # closed-world |C|
    adv = OfflineDeterministicAdversary()

    rows = []
    measured = {}
    for label, key in VARIANTS:
        print(f"Attacking variant: {label} (|C|={cset})…", flush=True)
        targets = []
        for (r, cp) in paired:
            rid = str(r["record_id"])
            text = str(r.get("text", "") or "") if key is None else str(cp.get(key) or "")
            targets.append(Target(target_id=rid, anonymized_text=text, observed_signals=extract(text)))
        m = score_reidentification(adv, targets, personas, candidate_set_size=cset)
        measured[label] = m.as_dict()
        rows.append({
            "variant": label,
            "n_targets": m.n_targets,
            "n_committed": m.n_guesses,
            "correct": m.correct,
            "recall": m.rrs.reid_recall,
            "precision": m.rrs.reid_precision,
            "rrs": m.rrs.rrs,
            "recall_ci_low": m.reid_recall_ci.low,
            "recall_ci_high": m.reid_recall_ci.high,
        })
        print(f"  {label}: recall={m.rrs.reid_recall:.3f} precision={m.rrs.reid_precision:.3f} "
              f"RRS={m.rrs.rrs:.3f} (correct {m.correct}/{m.n_targets}, committed {m.n_guesses})", flush=True)

    (out / "measured_rrs.json").write_text(
        json.dumps({"candidate_set_size": cset, "n_paired": n, "adversary_id": adv.adversary_id,
                    "variants": measured}, indent=2),
        encoding="utf-8")

    ctrl = next(r for r in rows if r["variant"] == "original_control")
    anon = [r for r in rows if r["variant"] != "original_control"]
    discriminates = (max(a["rrs"] for a in anon) - min(a["rrs"] for a in anon)) if anon else 0.0
    control_works = ctrl["recall"] >= 0.5

    md = [
        "# Measured Tier-3 re-identification (real attack, supersedes the heuristic RRS prior)\n",
        f"Adversary: `{adv.adversary_id}` (deterministic, offline). Closed-world **|C| = {cset}** "
        f"paired personas. RRS = 1 − recall×precision; higher = more re-id-resistant. Wilson 95% CIs on recall.\n",
        "| Target | n | committed | correct | recall [95% CI] | precision | **RRS** |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        star = " ⟵ control" if r["variant"] == "original_control" else ""
        md.append(
            f"| {r['variant']}{star} | {r['n_targets']} | {r['n_committed']} | {r['correct']} | "
            f"{r['recall']:.3f} [{r['recall_ci_low']:.3f}, {r['recall_ci_high']:.3f}] | "
            f"{r['precision']:.3f} | **{r['rrs']:.3f}** |"
        )
    md += [
        "\n## Diagnosis\n",
        f"- **Control (original text) recall = {ctrl['recall']:.3f}, RRS = {ctrl['rrs']:.3f}.** "
        + ("The attack CAN re-identify when identifying tokens survive — the testbed is functional."
           if control_works else
           "**The attack fails even on the original text** — the behavioral-signal substrate is too sparse "
           "to support re-identification, so the measured RRS is uninformative about anonymization strength "
           "(a dataset limitation, not a privacy guarantee). This confirms the SME finding."),
        f"- **Spread of RRS across the 4 anonymized variants = {discriminates:.3f}.** "
        + ("The measured attack discriminates between anonymization strategies." if discriminates >= 0.05 else
           "The variants are **indistinguishable** to this attack (RRS spread < 0.05): every variant removes the "
           "surviving QI tokens the attack relies on, and the behavioral signals are too sparse to separate strengths. "
           "An LLM adversary and/or richer behavioral signals would be needed to grade variant strength."),
        "\n## Honesty note\n",
        "This is the FR-007 measured attack (deterministic offline adversary) — a real, CI-bearing number that "
        "replaces the shipped `re_identification_resistance_score`, which is a heuristic prior over "
        "`behavioral_signal_density` with no attacker (rename recommended: `exposure_index_prior`). "
        "Per the dataset's FR-009 caveat, an RRS measured on SYNTHETIC data MUST NOT be cited as evidence that any "
        "record is anonymised under GDPR Recital 26. AX-001: synthetic-distribution precision, not external validity.",
    ]
    (out / "measured_rrs.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nControl recall={ctrl['recall']:.3f}  variant-RRS-spread={discriminates:.3f}  → {out}/measured_rrs.md", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
