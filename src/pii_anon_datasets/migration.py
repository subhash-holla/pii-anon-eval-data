"""v1.3.0 → v2.0.0 record migration (DC-02).

Deterministic + content-addressed (AX-002, reidx-05): `record_id` derives from the
text + sorted annotation offsets — NOT the order-dependent ``i`` counter the v1
migration used.

Clean restructure (the true-v2.0.0 decision): consolidate the scattered tier3
re-identification-resistance signal into one ``tier3_evaluation`` wrapper (matching
the shape the README documents), MERGING — never clobbering — any
``tier3_evaluation`` already present (the 7,003 paired-profile records).
"""
from __future__ import annotations

import hashlib
import uuid

from .taxonomy import is_known_entity_type

SCHEMA_VERSION = "2.0.0"
_UNIT_SEP = "␟"
# tier3 re-id-resistance fields that move OUT of privacy_risk → tier3_evaluation
_PRIVACY_RISK_TIER3 = (
    "re_identification_resistance_score",
    "estimated_reid_recall",
    "tier3_risk_level",
)


def deterministic_record_id(text: str, annotations: list | None) -> str:
    """Content-addressed id: stable across runs and INDEPENDENT of annotation order."""
    offsets = sorted(
        (a.get("start"), a.get("end"), a.get("entity_type")) for a in (annotations or [])
    )
    digest = hashlib.sha256((text + _UNIT_SEP + repr(offsets)).encode("utf-8")).hexdigest()
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"pii-anon-v2.0.0:{digest}"))


def migrate_record(rec: dict) -> dict:
    """Pure v1.3.0 → v2.0.0 transform of a single record."""
    r = dict(rec)

    # --- consolidate tier3 (merge into any existing wrapper; never clobber) ---
    tier3 = dict(r.get("tier3_evaluation") or {})
    privacy_risk = dict(r.get("privacy_risk") or {})
    for key in _PRIVACY_RISK_TIER3:
        if key in privacy_risk:
            tier3.setdefault(key, privacy_risk.pop(key))
    if "behavioral_signals" in r:
        tier3.setdefault("behavioral_signals", r.pop("behavioral_signals"))
    r["privacy_risk"] = privacy_risk
    r["tier3_evaluation"] = tier3

    # --- lineage + version ---
    provenance = dict(r.get("provenance") or {})
    if r.get("record_id") and "v1_3_0_record_id" not in provenance:
        provenance["v1_3_0_record_id"] = r["record_id"]
    r["provenance"] = provenance
    r["schema_version"] = SCHEMA_VERSION
    r["version"] = SCHEMA_VERSION

    # --- deterministic, content-addressed record_id ---
    r["record_id"] = deterministic_record_id(r.get("text", ""), r.get("annotations"))
    return r


def unknown_entity_types(rec: dict) -> set[str]:
    """Entity types in a record that are NOT in the canonical registry (should be empty)."""
    return {
        a["entity_type"]
        for a in (rec.get("annotations") or [])
        if a.get("entity_type") and not is_known_entity_type(a["entity_type"])
    }
