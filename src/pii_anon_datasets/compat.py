"""Back-compatibility accessor (DX-01).

Re-exposes a v2.0.0 record in the v1.3.0 *flat* shape for consumers that still read
top-level ``behavioral_signals`` or ``privacy_risk.re_identification_resistance_score``.
Best-effort: restores the fields the clean restructure moved; the published
``load_dataset()`` signature is unchanged.
"""
from __future__ import annotations

import copy as _copy

_TIER3_TO_PRIVACY_RISK = (
    "re_identification_resistance_score",
    "estimated_reid_recall",
    "tier3_risk_level",
)


def to_v1_record(rec: dict) -> dict:
    """Return a copy of a v2.0.0 record reshaped to the v1.3.0 flat layout."""
    r = dict(rec)
    tier3 = dict(r.get("tier3_evaluation") or {})
    r.pop("schema_version", None)

    privacy_risk = dict(r.get("privacy_risk") or {})
    for key in _TIER3_TO_PRIVACY_RISK:
        if key in tier3:
            privacy_risk[key] = tier3[key]
    r["privacy_risk"] = privacy_risk

    if "behavioral_signals" in tier3:
        r["behavioral_signals"] = tier3["behavioral_signals"]

    # records that ALREADY carried a tier3_evaluation in v1.3.0 keep it; otherwise drop the wrapper
    if set(tier3) <= (set(_TIER3_TO_PRIVACY_RISK) | {"behavioral_signals"}):
        r.pop("tier3_evaluation", None)

    provenance = r.get("provenance") or {}
    if provenance.get("v1_3_0_record_id"):
        r["record_id"] = provenance["v1_3_0_record_id"]
    r["version"] = "1.3.0"
    return r


_HONESTY_CP_KEYS = ("legal_category", "residual_quasi_identifier", "coherence_assumed", "_caveat")
_HONESTY_UM_KEYS = (
    "token_overlap_jaccard_masked",
    "token_overlap_jaccard_pseudonymized",
    "token_overlap_jaccard_llm_sanitized",
    "token_overlap_jaccard_generalized",
    "_caveat",
)


def to_v2_record(rec: dict) -> dict:
    """Return a copy of a v2.1.0 record reshaped back to the flat v2.0.0 shape (strips honesty additions)."""
    r = _copy.deepcopy(rec)
    cp = r.get("context_preservation")
    if isinstance(cp, dict):
        for k in _HONESTY_CP_KEYS:
            cp.pop(k, None)
        um = cp.get("utility_metrics")
        if isinstance(um, dict):
            for k in _HONESTY_UM_KEYS:
                um.pop(k, None)
    t3 = r.get("tier3_evaluation")
    if isinstance(t3, dict):
        t3.pop("exposure_index_prior", None)
        t3.pop("_caveat", None)
    pr = r.get("privacy_risk")
    if isinstance(pr, dict):
        pr.pop("qid_type_count_risk_label", None)  # B-6 honesty addition — not a v2.0.0 field
        pr.pop("_caveat", None)
    r.pop("reg_hipaa_phi_present", None)
    r["version"] = "2.0.0"
    r["schema_version"] = "2.0.0"
    return r
