# tests/test_honesty_fixes.py
"""v2.1.0 additive honesty transform (DC-honesty). Strictly additive + value-idempotent."""
from __future__ import annotations

import copy

from pii_anon_datasets.honesty import apply_honesty


def _record() -> dict:
    return {
        "record_id": "r1",
        "text": "SSN ***-**-1234 here",
        "context_preservation": {
            "anonymized_masked": "SSN [SSN] here",
            "anonymized_generalized": "SSN ***-**-1234 here",
            "anonymized_pseudonymized": "SSN 555-44-3333 here",
            "anonymized_llm_sanitized": "SSN 111-22-9999 here",
            "utility_metrics": {"semantic_similarity_masked": 0.7},
        },
        "tier3_evaluation": {"re_identification_resistance_score": 0.81},
        "privacy_risk": {"k_anonymity_estimate": 20},
    }


def test_adds_honest_aliases_and_caveats():
    out = apply_honesty(_record())
    cp = out["context_preservation"]
    assert cp["utility_metrics"]["token_overlap_jaccard_masked"] == 0.7
    assert "Jaccard" in cp["utility_metrics"]["_caveat"]
    assert cp["legal_category"]["pseudonymized"].startswith("pseudonymization")
    assert cp["residual_quasi_identifier"]["generalized"] is True  # ***-**-1234 tail
    assert "Recital 26" in cp["_caveat"]
    assert out["tier3_evaluation"]["exposure_index_prior"] == 0.81
    assert "HEURISTIC PRIOR" in out["tier3_evaluation"]["_caveat"]
    assert "quasi-identifier-TYPE-count" in out["privacy_risk"]["_caveat"]


def test_is_additive_and_does_not_mutate_input():
    rec = _record()
    snapshot = copy.deepcopy(rec)
    apply_honesty(rec)
    assert rec == snapshot  # input untouched (apply_honesty returns a copy)


def test_value_idempotent():
    once = apply_honesty(_record())
    twice = apply_honesty(once)
    assert once == twice


def test_no_existing_key_removed():
    out = apply_honesty(_record())
    assert out["context_preservation"]["utility_metrics"]["semantic_similarity_masked"] == 0.7
    assert out["tier3_evaluation"]["re_identification_resistance_score"] == 0.81


def test_reg_hipaa_alias_additive_and_idempotent():
    out = apply_honesty({"reg_hipaa_safe_harbor": "in_scope"})
    assert out["reg_hipaa_phi_present"] == "in_scope"
    assert out["reg_hipaa_safe_harbor"] == "in_scope"  # additive — original kept
    assert apply_honesty(out) == out  # idempotent via setdefault


def test_b6_coherence_assumed_alias_added():
    from pii_anon_datasets.honesty import apply_honesty
    rec = {"context_preservation": {"utility_metrics": {"semantic_similarity_masked": 0.8},
                                    "coherence_preserved_pseudonymized": True}}
    out = apply_honesty(rec)
    assert out["context_preservation"]["coherence_assumed"] is True


def test_b6_qid_type_count_risk_label_alias_added():
    from pii_anon_datasets.honesty import apply_honesty
    rec = {"privacy_risk": {"k_anonymity_estimate": 20, "quasi_identifiers": ["x", "y"]}}
    out = apply_honesty(rec)
    assert out["privacy_risk"]["qid_type_count_risk_label"] == 20  # same value, honest name
