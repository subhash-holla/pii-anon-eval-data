# tests/test_compat_v2.py
from pii_anon_datasets.compat import to_v2_record
from pii_anon_datasets.honesty import apply_honesty


def test_to_v2_record_strips_honesty_additions():
    v20 = {
        "record_id": "r1",
        "version": "2.0.0",
        "context_preservation": {
            "anonymized_masked": "x",
            "coherence_preserved_pseudonymized": True,
            "utility_metrics": {"semantic_similarity_masked": 0.5},
        },
        "tier3_evaluation": {"re_identification_resistance_score": 0.8},
        "privacy_risk": {"k_anonymity_estimate": 5},
    }
    v21 = apply_honesty(dict(v20))
    v21["version"] = v21["schema_version"] = "2.1.0"
    back = to_v2_record(v21)
    assert back["version"] == "2.0.0"
    assert "_caveat" not in back["context_preservation"]
    assert "legal_category" not in back["context_preservation"]
    assert "coherence_assumed" not in back["context_preservation"]  # B-6 honesty addition stripped
    assert "qid_type_count_risk_label" not in back["privacy_risk"]  # B-6 honesty addition stripped
    assert "exposure_index_prior" not in back["tier3_evaluation"]
    assert "reg_hipaa_phi_present" not in back
    # original v2.0.0 keys survive
    assert back["tier3_evaluation"]["re_identification_resistance_score"] == 0.8
    assert back["privacy_risk"]["k_anonymity_estimate"] == 5  # old key preserved (additive-first)
    assert back["context_preservation"]["coherence_preserved_pseudonymized"] is True  # old key preserved
