#!/usr/bin/env python3
"""Train/test contamination & near-duplicate leakage audit.

A templated synthetic corpus invites the obvious reviewer objection: "the test set is just the train
set with the numbers changed — leakage." This audit quantifies it on two axes and reframes it correctly:

  * EXACT-TEXT overlap   — fraction of test records whose verbatim text also appears in train.
                           For a detection benchmark this should be ~0 (a real leak if high).
  * TEMPLATE-SKELETON overlap — fraction of test records whose PII-REDACTED skeleton (every gold span
                           replaced by its entity-type tag) also appears in train. This is EXPECTED to
                           be non-trivial by construction (templated generation) and is NOT label
                           leakage: the task is detecting the *unseen PII values*, which differ even
                           when the surrounding template is shared. Reporting it pre-empts the objection
                           and supplies the honest "N% shared template structure, 0% leaked values" line.

Read-only over dist/hf/data/{train,test}.parquet via pyarrow batches (bounded memory). No detector runs.

Usage: python scripts/leakage_audit.py --train dist/hf/data/train.parquet --test dist/hf/data/test.parquet --out results/tier-a/leakage_audit.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq


def _h(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()


def _skeleton(text: str, annotations) -> str:
    """Replace each gold span [start,end) with its entity-type tag, left-to-right, non-overlapping."""
    if isinstance(annotations, str):
        try:
            annotations = json.loads(annotations)
        except Exception:
            annotations = []
    spans = sorted(
        ((int(a["start"]), int(a["end"]), str(a["entity_type"])) for a in (annotations or [])),
        key=lambda t: (t[0], t[1]),
    )
    out, cur = [], 0
    for s, e, et in spans:
        if s < cur:  # skip overlaps to keep a deterministic skeleton
            continue
        out.append(text[cur:s])
        out.append(f"[{et}]")
        cur = e
    out.append(text[cur:])
    return "".join(out)


def _scan(path: str, want_skeleton: bool):
    """Yield (text_hash, skeleton_hash) over a parquet in batches."""
    pf = pq.ParquetFile(path)
    cols = ["text", "annotations"] if want_skeleton else ["text"]
    for batch in pf.iter_batches(batch_size=8192, columns=cols):
        d = batch.to_pydict()
        texts = d["text"]
        anns = d.get("annotations", [None] * len(texts))
        for i, t in enumerate(texts):
            t = t or ""
            yield _h(t), (_h(_skeleton(t, anns[i])) if want_skeleton else None)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="dist/hf/data/train.parquet")
    ap.add_argument("--test", default="dist/hf/data/test.parquet")
    ap.add_argument("--out", default="results/tier-a/leakage_audit.md")
    args = ap.parse_args()

    print("Scanning train…", flush=True)
    train_text, train_skel = set(), set()
    n_train = 0
    for th, sh in _scan(args.train, want_skeleton=True):
        train_text.add(th)
        train_skel.add(sh)
        n_train += 1
    print(f"  train: {n_train:,} records  ({len(train_text):,} distinct texts, {len(train_skel):,} distinct skeletons)", flush=True)

    print("Scanning test…", flush=True)
    n_test = exact_hits = skel_hits = 0
    test_text_distinct = set()
    for th, sh in _scan(args.test, want_skeleton=True):
        n_test += 1
        test_text_distinct.add(th)
        if th in train_text:
            exact_hits += 1
        if sh in train_skel:
            skel_hits += 1
    print(f"  test: {n_test:,} records", flush=True)

    exact_pct = 100 * exact_hits / n_test if n_test else 0.0
    skel_pct = 100 * skel_hits / n_test if n_test else 0.0
    intra_test_dup = 100 * (1 - len(test_text_distinct) / n_test) if n_test else 0.0

    md = [
        "# Train/test contamination & near-duplicate leakage audit\n",
        f"Train: **{n_train:,}** records ({len(train_text):,} distinct texts). "
        f"Test: **{n_test:,}** records. Read-only over the published Parquet; no detector runs.\n",
        "| Axis | Test records matched in train | % of test |",
        "|---|---:|---:|",
        f"| **Exact-text overlap** (verbatim text in train) | {exact_hits:,} | **{exact_pct:.2f}%** |",
        f"| **Template-skeleton overlap** (PII-redacted structure in train) | {skel_hits:,} | **{skel_pct:.2f}%** |",
        f"| Intra-test exact duplicate texts | — | {intra_test_dup:.2f}% |",
        "\n## Interpretation (the honest framing)\n",
        f"- **Exact-text leakage is {exact_pct:.2f}%** — "
        + ("a real leak to investigate." if exact_pct > 1 else "negligible; test texts are not verbatim copies of train."),
        f"- **Template-skeleton overlap is {skel_pct:.2f}%.** This is EXPECTED for a templated synthetic"
        " corpus and is **NOT label leakage**: the detection task is recovering the *unseen PII values*,"
        " which are regenerated per record even when the surrounding template is shared. The defensible"
        f" claim is: \"{exact_pct:.1f}% verbatim duplication; {skel_pct:.0f}% shared template structure by"
        " design, disclosed\" — never \"0 contamination\".",
        "- A harder *novel-template* test slice (test skeletons NOT present in train) can be carved from"
        " this audit if a reviewer wants a leakage-free subset.",
        "\n_Method: exact = sha1(text) set-membership train↔test; skeleton = sha1 of text with every gold"
        " span replaced by its entity-type tag (left-to-right, overlaps skipped). AX-001: synthetic-only —"
        " this measures internal corpus structure, not real-world generalization._",
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nExact-text: {exact_pct:.2f}%   Template-skeleton: {skel_pct:.2f}%   → {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
