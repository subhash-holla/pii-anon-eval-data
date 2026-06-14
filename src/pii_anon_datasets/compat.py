"""Back-compatibility accessor (DX-01).

Re-exposes a v2.0.0 record in the v1.3.0 *flat* shape for consumers that still read
top-level ``behavioral_signals`` or ``privacy_risk.re_identification_resistance_score``.
Best-effort: restores the fields the clean restructure moved; the published
``load_dataset()`` signature is unchanged.
"""
from __future__ import annotations

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
