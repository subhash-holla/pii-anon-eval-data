# src/pii_anon_datasets/honesty.py
"""Single source of the v2.1.0 additive honesty layer (DC-honesty).

Strictly ADDITIVE + value-idempotent: every existing key is preserved; honest aliases, caveats, and
legal/residual flags are added. Both the record-level jsonl migration (scripts/v2_0_0_to_v2_1_0.py) and
the parquet layer (scripts/apply_honesty_fixes.py) consume this module so the caveat text lives once.
"""
from __future__ import annotations

import copy
import re

from pii_anon_datasets.compliance.crosswalk import CROSSWALK_DISCLAIMER
from pii_anon_datasets.scoring.reidentification import EXPOSURE_INDEX_NOTE

TARGET_VERSION = "2.1.0"

_PARTIAL_ID = re.compile(r"\*\*\*-\*\*-\d{4}|\b\d{4}-\*+|\*{2,}\d{3,4}\b")

_VARIANTS = (
    ("masked", "anonymized_masked"),
    ("generalized", "anonymized_generalized"),
    ("pseudonymized", "anonymized_pseudonymized"),
    ("llm_sanitized", "anonymized_llm_sanitized"),
)

LEGAL_CATEGORY = {
    "anonymized_masked": "redaction — PII spans removed/type-tagged",
    "anonymized_generalized": "generalization — PII categorized; MAY retain quasi-identifiers",
    "anonymized_pseudonymized": "pseudonymization — GDPR Art.4(5): STILL PERSONAL DATA (not anonymised)",
    "anonymized_llm_sanitized": "substitution with synthetic values — STILL PERSONAL DATA (not anonymisation)",
}
UTIL_CAVEAT = (
    "semantic_similarity_* is set-token Jaccard (compute_token_overlap), NOT a semantic/embedding measure "
    "(honest alias: token_overlap_jaccard_*); coherence_preserved_* is an ASSUMED constant (hardcoded True), "
    "not a measured coherence (honest replacement: coherence_assumed=true); information_loss_ratio is an "
    "entity-type prior, not a measured loss."
)
CP_CAVEAT = (
    "No variant is demonstrated anonymised under GDPR Recital 26. anonymized_pseudonymized and "
    "anonymized_llm_sanitized remain PERSONAL DATA (Art.4(5)). residual_quasi_identifier flags a partial "
    "identifier (e.g. ***-**-NNNN SSN tail) retained in a variant — a quasi-identifier, not a safe endpoint. "
    "Synthetic-only (AX-001): synthetic-distribution precision, not external validity."
)
T3_CAVEAT = (
    "re_identification_resistance_score is a HEURISTIC PRIOR (closed-form over behavioral_signal_density), "
    "NOT a measured attack; exposure_index_prior is its honest alias. " + EXPOSURE_INDEX_NOTE +
    " For a measured, CI-bearing number, run the FR-007 MeasuredRRS adversary."
)
PR_CAVEAT = (
    "k_anonymity_estimate is a quasi-identifier-TYPE-count proxy (1->100, 2->20, 3->5, 4+->2), NOT an "
    "equivalence-class k computed over QI values; honest alias: qid_type_count_risk_label; null where "
    "quasi-identifiers are absent."
)

FILE_META: dict[bytes, bytes] = {
    b"honesty_fixes_applied": b"v1-additive-nondestructive",
    b"crosswalk_disclaimer": CROSSWALK_DISCLAIMER.encode("utf-8"),
    b"exposure_index_note": EXPOSURE_INDEX_NOTE.encode("utf-8"),
    b"reg_gdpr_note": (b"reg_gdpr is currently constant (in_scope on every row); material-scope "
                       b"discrimination requires genuinely non-personal records (documented follow-up)."),
    b"ax_001": (b"All metrics are precision on the SYNTHETIC distribution; NOT external validity, NOT a "
                b"GDPR/HIPAA certification. No record is demonstrated anonymised under Recital 26."),
}


def augment_context_preservation(cp: dict) -> None:
    """Additively augment a context_preservation dict in place (value-idempotent)."""
    cp["legal_category"] = {short: LEGAL_CATEGORY[ak] for short, ak in _VARIANTS if ak in cp}
    residual: dict[str, bool] = {}
    for short, ak in _VARIANTS:
        txt = cp.get(ak)
        if isinstance(txt, str) and _PARTIAL_ID.search(txt):
            residual[short] = True
    cp["residual_quasi_identifier"] = residual or False
    um = cp.get("utility_metrics")
    if isinstance(um, dict):
        for short, _ in _VARIANTS:
            ss = um.get(f"semantic_similarity_{short}")
            if ss is not None:
                um[f"token_overlap_jaccard_{short}"] = ss
        um["_caveat"] = UTIL_CAVEAT
    cp["_caveat"] = CP_CAVEAT
    # B-6: coherence_preserved_* is a hardcoded True (zero-variance, not a measurement). Emit the honest
    # `coherence_assumed=true` marker; keep the old keys one version (deprecated).
    if any(k.startswith("coherence_preserved_") for k in cp):
        cp["coherence_assumed"] = True


def augment_tier3(t3: dict) -> None:
    """Additively augment a tier3_evaluation dict in place."""
    if "re_identification_resistance_score" in t3:
        t3["exposure_index_prior"] = t3["re_identification_resistance_score"]
    t3["_caveat"] = T3_CAVEAT


def augment_privacy_risk(pr: dict) -> None:
    """Additively augment a privacy_risk dict in place."""
    if "k_anonymity_estimate" in pr:
        pr["qid_type_count_risk_label"] = pr["k_anonymity_estimate"]  # B-6: honest name, same value
    pr["_caveat"] = PR_CAVEAT


def apply_honesty(record: dict) -> dict:
    """Return a deep copy of ``record`` with the additive honesty layer applied (input untouched)."""
    rec = copy.deepcopy(record)
    cp = rec.get("context_preservation")
    if isinstance(cp, dict):
        augment_context_preservation(cp)
    t3 = rec.get("tier3_evaluation")
    if isinstance(t3, dict):
        augment_tier3(t3)
    pr = rec.get("privacy_risk")
    if isinstance(pr, dict):
        augment_privacy_risk(pr)
    if "reg_hipaa_safe_harbor" in rec:
        rec.setdefault("reg_hipaa_phi_present", rec["reg_hipaa_safe_harbor"])
    return rec
