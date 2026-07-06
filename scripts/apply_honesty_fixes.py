#!/usr/bin/env python3
"""Additive honesty layer for the shipped Parquet — closes the SME 'honesty-doesn't-travel-into-the-data'
gap WITHOUT a destructive rename (which would break the scorer/tests/schema/croissant that read the old keys).

It is strictly ADDITIVE: every existing key/column is preserved, and we ADD
  * honestly-named aliases   — `token_overlap_jaccard_*` (= the mislabeled `semantic_similarity_*`),
                               `exposure_index_prior` (= the heuristic `re_identification_resistance_score`),
                               `reg_hipaa_phi_present` column (= `reg_hipaa_safe_harbor`, which models PHI-content
                               presence, NOT the 18-identifier Safe Harbor standard);
  * the in-code caveats       — propagated INTO the data (the FR-009 / EXPOSURE_INDEX_NOTE / CROSSWALK_DISCLAIMER
                               strings imported verbatim from the package), as per-record `_caveat` fields AND as
                               file-level schema metadata, so a cold CC0 consumer can never read e.g.
                               `tier3_risk_level: low` without the anti-anonymity caveat beside it;
  * legal / residual flags    — `context_preservation.legal_category` (per-variant GDPR classification:
                               pseudonymized/llm_sanitized are STILL personal data under Art.4(5)) and
                               `residual_quasi_identifier` (True when a variant retains a partial identifier such
                               as a `***-**-NNNN` SSN tail — a recognised QI presented as a de-id endpoint).

Old keys are untouched → readers keep working. The destructive renames + the reg_gdpr-constant fix (needs
genuinely non-personal records) + Art.9 coverage are documented as reviewed follow-ups in
results/tier-a/honesty_fixes.md, not applied blindly here.

Usage: python scripts/apply_honesty_fixes.py --in dist/hf/data/test_legal.parquet --out /tmp/test_legal.honest.parquet
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from pii_anon_datasets.honesty import (
    FILE_META,
    augment_context_preservation,
    augment_privacy_risk,
    augment_tier3,
)


def _loads(v):
    if v in (None, "", "null"):
        return None
    return json.loads(v) if isinstance(v, str) else v


def transform_cp(v):
    o = _loads(v)
    if not isinstance(o, dict):
        return v
    augment_context_preservation(o)
    return json.dumps(o, ensure_ascii=False)


def transform_t3(v):
    o = _loads(v)
    if not isinstance(o, dict):
        return v
    augment_tier3(o)
    return json.dumps(o, ensure_ascii=False)


def transform_pr(v):
    o = _loads(v)
    if not isinstance(o, dict):
        return v
    augment_privacy_risk(o)
    return json.dumps(o, ensure_ascii=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    args = ap.parse_args()

    t = pq.read_table(args.inp)
    names = list(t.schema.names)
    d = {n: t.column(n) for n in names}

    def xf(col, fn):
        if col in d:
            d[col] = pa.array([fn(v) for v in t.column(col).to_pylist()], type=pa.string())
            return sum(1 for v in t.column(col).to_pylist() if _loads(v) is not None)
        return 0

    n_cp = xf("context_preservation", transform_cp)
    n_t3 = xf("tier3_evaluation", transform_t3)
    n_pr = xf("privacy_risk", transform_pr)

    # honest alias column: reg_hipaa_phi_present == reg_hipaa_safe_harbor (it models PHI-content, not Safe Harbor)
    if "reg_hipaa_safe_harbor" in d:
        d["reg_hipaa_phi_present"] = t.column("reg_hipaa_safe_harbor")

    new = pa.table(d)
    new = new.replace_schema_metadata({**(t.schema.metadata or {}), **FILE_META})
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(new, args.out)
    print(f"Wrote {args.out}: +reg_hipaa_phi_present col; caveats/aliases on "
          f"context_preservation({n_cp}) / tier3_evaluation({n_t3}) / privacy_risk({n_pr}); file-metadata disclaimers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
