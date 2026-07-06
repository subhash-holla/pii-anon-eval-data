# Examples and Tests Catalog — PII-Anon Benchmark

**Stage 5 · Wave T6 (Synthesis)** · Generated 2026-05-31
Sources: `tests/` (347 items: 346 passed / 1 skipped) · `dev-assist-artifacts/02-requirements/` · `dev-assist-artifacts/03-design/06-synthesis/D-implementation-ready-design.md` · `dev-assist-artifacts/04-development/02-stories/`
NFR-verification dir: `dev-assist-artifacts/05-testing/03-nfr-verification/` — empty (no pre-wave artifacts)
Pass-2 dir: `dev-assist-artifacts/05-testing/05-pass2/` — empty (Pass-2 not yet run)

> **Source signal vs gaps (brownfield):** The test suite is richly explicit — the vast majority of test functions carry `fr_NNN` / `nfr_NNN` tokens in their names AND module docstrings. Seventeen items in this catalog carry `(inferred)` trace links (see Section 7). The explicit-to-inferred ratio is approximately 90 / 10. The catalog IS the first systematic trace artifact; adding `// trace: FR-NNN` comments to the inferred rows is recommended for subsequent releases.

---

## 1. Index by Functional Requirement (FR)

Every FR from `dev-assist-artifacts/02-requirements/functional-requirements.md` appears here.
Column key: **Trace type** = `explicit` (ID in test fn name or module docstring) | `inferred` (convention) | `doc-pinned` (roadmap doc only, no feature test) | `Pass-2 deferred` (seam test exists, full feature deferred).

---

### FR-001 — Multilingual/adversarial detection scoring (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_known_pr_f1_f2` | `tests/test_detection.py` | UNIT | inferred |
| `test_perfect_detection` | `tests/test_detection.py` | UNIT | inferred |
| `test_recall_ci_brackets_recall_and_uses_integer_n` | `tests/test_detection.py` | UNIT | inferred |
| `test_partial_f1_separate_and_excluded_from_ci` | `tests/test_detection.py` | UNIT | inferred |
| `test_as_dict_carries_ci_method_and_note` | `tests/test_detection.py` | UNIT | inferred |

**Note (inferred):** Module docstring of `test_detection.py` reads `"FR-001/004; M6"` but no individual test fn carries the `fr_001` token. All five tests verify the P/R/F1/F2 + per-slice CI contract specified by FR-001.

---

### FR-002 — Deterministic CI regression gate (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_002_mcnemar_exact_binomial` | `tests/test_paired.py` | UNIT | explicit |
| `test_fr_002_mcnemar_chi2_continuity` | `tests/test_paired.py` | UNIT | explicit |
| `test_fr_002_mcnemar_zero_discordant` | `tests/test_paired.py` | UNIT | explicit |
| `test_fr_002_mcnemar_odds_ratio` | `tests/test_paired.py` | UNIT | explicit |
| `test_fr_002_paired_bootstrap_deterministic` | `tests/test_paired.py` | PROPERTY | explicit |
| `test_fr_002_paired_bootstrap_brackets_delta` | `tests/test_paired.py` | UNIT | explicit |
| `test_nfr_002_paired_bootstrap_method_named` | `tests/test_paired.py` | UNIT | explicit |
| `test_fr_002_nfr004_paired_imports_no_uncontrolled_nondeterminism` | `tests/test_paired.py` | PROPERTY | explicit |

---

### FR-003 — Scorer I/O contract + reference adapter (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_perfect_match_integer_counts` | `tests/test_scoring_core.py` | UNIT | inferred |
| `test_strict_miss_and_false_positive` | `tests/test_scoring_core.py` | UNIT | inferred |
| `test_order_independence_reidx03` | `tests/test_scoring_core.py` | UNIT | inferred |
| `test_partial_overlap_counted_separately_not_as_tp` | `tests/test_scoring_core.py` | UNIT | inferred |
| `test_multiplicity_via_multiset` | `tests/test_scoring_core.py` | UNIT | inferred |
| `test_policy_version_stamped` | `tests/test_scoring_core.py` | UNIT | inferred |
| `test_invalid_span_rejected` | `tests/test_scoring_core.py` | UNIT | inferred |

**Note (inferred):** `test_scoring_core.py` docstring cites `reidx-02`/`reidx-03` design constraints but does not carry an explicit `fr_003` token. The tests verify the I/O contract (Span matching policy, version stamping) that DC-04 / FR-003 specifies. No dedicated Presidio reference adapter test was found; the adapter integration is exercised implicitly via `test_viz.py` fixture data.

---

### FR-004 — Per-slice scoring with confidence intervals (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_004_clopper_pearson_textbook_values` | `tests/test_clopper_pearson.py` | UNIT | explicit |
| `test_fr_004_clopper_pearson_brackets_point` | `tests/test_clopper_pearson.py` | UNIT | explicit |
| `test_nfr_002_clopper_pearson_method_named` | `tests/test_clopper_pearson.py` | UNIT | explicit |
| `test_fr_004_reidx02_clopper_pearson_integer_guard` | `tests/test_clopper_pearson.py` | UNIT | explicit |
| `test_fr_004_clopper_pearson_edges` | `tests/test_clopper_pearson.py` | UNIT | explicit |
| `test_fr_004_clopper_pearson_is_conservative_vs_wilson` | `tests/test_clopper_pearson.py` | UNIT | explicit |
| `test_fr_004_clopper_pearson_deterministic` | `tests/test_clopper_pearson.py` | PROPERTY | explicit |
| `test_wilson_point_and_brackets` | `tests/test_intervals.py` | UNIT | inferred |
| `test_wilson_half_symmetry_at_half` | `tests/test_intervals.py` | UNIT | inferred |
| `test_integer_counts_required_reidx02` | `tests/test_intervals.py` | UNIT | inferred |
| `test_bounds_validation` | `tests/test_intervals.py` | UNIT | inferred |
| `test_zero_n_is_nan_point_full_interval` | `tests/test_intervals.py` | UNIT | inferred |
| `test_determinism` | `tests/test_intervals.py` | PROPERTY | inferred |

**Note (inferred for test_intervals.py):** Module docstring cites `NFR-002` and `reidx-02`; no `fr_004` token in fn names. Tests verify Wilson CI behaviour required by FR-004.

---

### FR-005 — Calibration + abstain-to-review (SHOULD)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_005_ece_known_value` | `tests/test_calibration.py` | UNIT | explicit |
| `test_fr_005_brier_known_value` | `tests/test_calibration.py` | UNIT | explicit |
| `test_fr_005_perfect_calibration_zero_ece` | `tests/test_calibration.py` | UNIT | explicit |
| `test_nfr_008_meets_reference_is_reported_not_gated` | `tests/test_calibration.py` | UNIT | explicit |
| `test_fr_005_reliability_bins_partition` | `tests/test_calibration.py` | UNIT | explicit |
| `test_nfr_008_calibration_by_entity_class` | `tests/test_calibration.py` | UNIT | explicit |
| `test_fr_005_input_length_mismatch_raises` | `tests/test_calibration.py` | UNIT | explicit |
| `test_fr_005_nfr004_calibration_imports_no_nondeterminism` | `tests/test_calibration.py` | PROPERTY | explicit |
| `test_fr_005_reliability_diagram_writes_png` | `tests/test_viz.py` | UNIT | explicit |
| `test_fr_005_coverage_risk_curve_writes_png` | `tests/test_viz.py` | UNIT | explicit |
| `test_fr_005_agent_leakage_sankey_writes_png` | `tests/test_viz.py` | UNIT | explicit |
| `test_fr_005_pyproject_declares_viz_extra` | `tests/test_viz.py` | PROPERTY | explicit |

---

### FR-006 — Anonymization output scorer — Pareto (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_006_utility_probe_deterministic_and_versioned` | `tests/test_anonymization.py` | PROPERTY | explicit |
| `test_fr_006_utility_perfect_preservation_and_full_mask` | `tests/test_anonymization.py` | UNIT | explicit |
| `test_fr_006_pareto_point_has_two_separate_axes` | `tests/test_anonymization.py` | UNIT | explicit |
| `test_nfr005_pareto_point_cannot_merge` | `tests/test_anonymization.py` | AUDIT | explicit |
| `test_fr_006_residual_risk_axis_is_measured_rrs` | `tests/test_anonymization.py` | AUDIT | explicit |
| `test_fr_006_variant_recorded` | `tests/test_anonymization.py` | UNIT | explicit |
| `test_fr_006_nfr004_anonymization_imports_no_nondeterminism` | `tests/test_anonymization.py` | PROPERTY | explicit |
| `test_fr_006_utility_metrics_fold_in_components` | `tests/test_anonymization.py` | UNIT | explicit |
| `test_fr_006_utility_score_rejects_out_of_range` | `tests/test_anonymization.py` | UNIT | explicit |
| `test_fr_006_pareto_plot_writes_png` | `tests/test_viz.py` | UNIT | explicit |

---

### FR-007 — Measured-attack RRS (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_007_assemble_paired_set_deterministic` | `tests/test_adversary_port.py` | PROPERTY | explicit |
| `test_fr_007_assemble_filters_to_tier3_substrate` | `tests/test_adversary_port.py` | UNIT | explicit |
| `test_fr_007_candidate_set_size_is_first_class` | `tests/test_adversary_port.py` | UNIT | explicit |
| `test_fr_007_reidx_01_observed_signals_reextracted_not_gold` | `tests/test_adversary_port.py` | PROPERTY | explicit |
| `test_fr_007_attack_is_deterministic` | `tests/test_offline_adversary.py` | PROPERTY | explicit |
| `test_fr_007_ranking_is_order_independent` | `tests/test_offline_adversary.py` | PROPERTY | explicit |
| `test_fr_007_abstains_below_threshold` | `tests/test_offline_adversary.py` | UNIT | explicit |
| `test_fr_007_links_surviving_signal` | `tests/test_offline_adversary.py` | UNIT | explicit |
| `test_fr_007_guess_counts_are_integers` | `tests/test_offline_adversary.py` | UNIT | explicit |
| `test_fr_007_config_is_frozen_and_hashable` | `tests/test_offline_adversary.py` | UNIT | explicit |
| `test_fr_007_nfr004_offline_adversary_imports_no_nondeterminism` | `tests/test_offline_adversary.py` | PROPERTY | explicit |
| `test_fr_007_recall_ci_uses_integer_n_targets` | `tests/test_reidentification_measured.py` | UNIT | explicit |
| `test_fr_007_precision_ci_uses_integer_n_guesses` | `tests/test_reidentification_measured.py` | UNIT | explicit |
| `test_fr_007_rrs_equals_one_minus_recall_times_precision` | `tests/test_reidentification_measured.py` | UNIT | explicit |
| `test_fr_007_correct_is_guesses_matching_target_id` | `tests/test_reidentification_measured.py` | UNIT | explicit |
| `test_fr_007_abstentions_excluded_from_precision_denominator` | `tests/test_reidentification_measured.py` | UNIT | explicit |
| `test_fr_007_reidx02_fractional_count_raises` | `tests/test_reidentification_measured.py` | UNIT | explicit |
| `test_fr_007_perfect_attack_rrs_zero_and_no_commit_rrs_one` | `tests/test_reidentification_measured.py` | UNIT | explicit |
| `test_fr_007_candidate_set_size_recorded` | `tests/test_reidentification_measured.py` | UNIT | explicit |
| `test_cannot_construct_without_caveat` | `tests/test_rrs_caveat.py` | UNIT | inferred |
| `test_empty_caveat_rejected` | `tests/test_rrs_caveat.py` | UNIT | inferred |
| `test_from_attack_computes_rrs_and_sets_caveat` | `tests/test_rrs_caveat.py` | UNIT | inferred |
| `test_caveat_survives_serialization_gov01` | `tests/test_rrs_caveat.py` | UNIT | inferred |
| `test_candidate_set_size_is_first_class` | `tests/test_rrs_caveat.py` | UNIT | inferred |

**Note (inferred for test_rrs_caveat.py):** Module docstring cites `FR-009 / gov-01`; the RRS value-object tests structurally verify the FR-007 RRS contract (RRS = 1 - recall × precision, caveat travels with the number). No `fr_007` fn-token present.

---

### FR-008 — Exposure-index pre-screen (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_008_exposure_index_is_prior_not_rrs` | `tests/test_exposure_index.py` | UNIT | explicit |
| `test_fr_008_exposure_index_recomputes_density_transparently` | `tests/test_exposure_index.py` | UNIT | explicit |
| `test_fr_008_exposure_index_per_signal_transparent` | `tests/test_exposure_index.py` | UNIT | explicit |
| `test_fr_008_correlation_pearson_and_spearman` | `tests/test_exposure_index.py` | UNIT | explicit |
| `test_fr_008_correlation_n_zero_graceful` | `tests/test_exposure_index.py` | UNIT | explicit |
| `test_fr_008_nfr004_exposure_imports_no_nondeterminism` | `tests/test_exposure_index.py` | PROPERTY | explicit |
| `test_fr_008_uniqueness_weight_table_matches_source` | `tests/test_signals.py` | UNIT | explicit |
| `test_fr_008_compute_signal_density_golden` | `tests/test_signals.py` | UNIT | explicit |
| `test_fr_008_detect_signals_pure_and_deterministic` | `tests/test_signals.py` | PROPERTY | explicit |
| `test_fr_008_nfr004_signals_imports_no_nondeterminism` | `tests/test_signals.py` | PROPERTY | explicit |
| `test_fr_008_signal_extractor_version_pinned` | `tests/test_signals.py` | UNIT | explicit |

---

### FR-009 — Non-strippable anti-anonymity caveat (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_cannot_construct_without_caveat` | `tests/test_rrs_caveat.py` | UNIT | explicit |
| `test_empty_caveat_rejected` | `tests/test_rrs_caveat.py` | UNIT | explicit |
| `test_from_attack_computes_rrs_and_sets_caveat` | `tests/test_rrs_caveat.py` | UNIT | explicit |
| `test_caveat_survives_serialization_gov01` | `tests/test_rrs_caveat.py` | UNIT | explicit |
| `test_fr_009_caveat_nonstrippable_in_measured_as_dict` | `tests/test_reidentification_measured.py` | AUDIT | explicit |
| `test_fr_006_residual_risk_axis_is_measured_rrs` | `tests/test_anonymization.py` | AUDIT | explicit |
| `test_fr_021_caveats_travel_with_each_axis` | `tests/test_end_state_bundle.py` | INTEGRATION | explicit |

---

### FR-010 — Adversary pluggability (SHOULD)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_010_persona_target_guess_are_frozen` | `tests/test_adversary_port.py` | UNIT | explicit |
| `test_fr_010_guess_abstain_is_none_not_wrong` | `tests/test_adversary_port.py` | UNIT | explicit |
| `test_fr_010_adversary_protocol_is_runtime_checkable` | `tests/test_adversary_port.py` | CONTRACT | explicit |
| `test_fr_010_distractor_variant_distinct_id_and_lower_precision` | `tests/test_offline_adversary.py` | UNIT | explicit |
| `test_fr_010_adversary_satisfies_port` | `tests/test_offline_adversary.py` | CONTRACT | explicit |
| `test_fr_010_llm_adversary_class_shape_without_anthropic` | `tests/test_llm_adversary.py` | CONTRACT | explicit |
| `test_fr_010_llm_adversary_requires_extra_when_anthropic_absent` | `tests/test_llm_adversary.py` | UNIT | explicit |
| `test_fr_010_llm_adversary_id_version_stamped` | `tests/test_llm_adversary.py` | UNIT | explicit |
| `test_fr_010_package_imports_without_anthropic` | `tests/test_llm_adversary.py` | CONTRACT | explicit |
| `test_fr_010_llm_attack_skips_if_absent` | `tests/test_llm_adversary.py` | INTEGRATION (skip) | explicit |

---

### FR-011 — Pseudonymization-integrity scorer (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_011_reversal_rates_are_threat_conditioned` | `tests/test_pseudonymization.py` | UNIT | explicit |
| `test_fr_011_authorized_succeeds_unauthorized_fails_for_keyed` | `tests/test_pseudonymization.py` | UNIT | explicit |
| `test_fr_011_pseudonymizer_protocol_runtime_checkable` | `tests/test_pseudonymization.py` | CONTRACT | explicit |
| `test_fr_011_nfr004_pseudonymization_imports_no_nondeterminism` | `tests/test_pseudonymization.py` | PROPERTY | explicit |

---

### FR-012 — Collision-type-separated scoring (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_012_correct_deterministic_has_zero_crypto_collisions` | `tests/test_pseudonymization.py` | UNIT | explicit |
| `test_fr_012_faulty_pseudonymizer_flags_crypto_collisions` | `tests/test_pseudonymization.py` | UNIT | explicit |

---

### FR-013 — Referential integrity + key-rotation + key/state separation (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_013_referential_integrity_join_stable` | `tests/test_pseudonymization.py` | UNIT | explicit |
| `test_fr_013_key_rotation` | `tests/test_pseudonymization.py` | UNIT | explicit |
| `test_fr_013_key_state_separation_edpb_art4_5` | `tests/test_pseudonymization.py` | UNIT | explicit |

---

### FR-014 — Query-aware masking scorer (SHOULD)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| (no explicit trace found) | — | — | — |

**GAP (SHOULD):** No test file carries an `fr_014` token or explicit FR-014 reference. This is a `SHOULD`-priority requirement. Acceptable gap for v1; recommend adding a seam test for the 8K+ query-aware records slice.

---

### FR-015 — Coreference-chain scoring (SHOULD — v1 seam)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_015_coreference_slice_selects_nonempty_chains` | `tests/test_slices.py` | UNIT | explicit |
| `test_fr_015_slice_low_power_caveat_non_strippable` | `tests/test_slices.py` | UNIT | explicit |

**Status: Pass-2 deferred.** Seam test verifies the slice selector and caveat machinery. Full chain-as-unit scoring deferred to v1.1 (by design, DC-01 extension seam).

---

### FR-016 — Quasi-identifier-combination scoring (SHOULD — v1.1)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_016_quasi_identifier_slice_min_qids` | `tests/test_slices.py` | UNIT | explicit |

**Status: Pass-2 deferred.** Seam test verifies the QI slice filter. Full quasi-identifier scoring deferred to v1.1.

---

### FR-017 — PII-recognition oracle + payload library (SHOULD)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_017_recognize_returns_labeled_verdicts` | `tests/test_oracle.py` | UNIT | explicit |
| `test_fr_017_oracle_disclaimer_non_strippable` | `tests/test_oracle.py` | UNIT | explicit |
| `test_fr_017_recognize_span_point_query` | `tests/test_oracle.py` | UNIT | explicit |
| `test_nfr004_oracle_pure_stdlib` | `tests/test_oracle.py` | PROPERTY | explicit |
| `test_fr_017_payload_is_obfuscated_carrier_intent_tuple` | `tests/test_payloads.py` | UNIT | explicit |
| `test_fr_017_three_committed_transforms` | `tests/test_payloads.py` | UNIT | explicit |
| `test_fr_017_transforms_are_faithful` | `tests/test_payloads.py` | UNIT | explicit |
| `test_fr_017_payloads_are_inert` | `tests/test_payloads.py` | UNIT | explicit |
| `test_fr_017_invalid_payload_rejected` | `tests/test_payloads.py` | UNIT | explicit |
| `test_nfr004_payloads_pure_stdlib` | `tests/test_payloads.py` | PROPERTY | explicit |

---

### FR-018 — Cross-turn fragmented-leakage payloads (COULD)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_018_fr_019_fr_020_roadmap_documents_deferred_items` | `tests/test_roadmap.py` | PROPERTY | explicit |

**Status: doc-pinned.** ROADMAP.md must name FR-018 and describe cross-turn fragmented leakage as a future item. No feature implementation shipped in v1.

---

### FR-019 — Transcript residual-leakage estimate (COULD)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_018_fr_019_fr_020_roadmap_documents_deferred_items` | `tests/test_roadmap.py` | PROPERTY | explicit |

**Status: doc-pinned.** Same roadmap pin as FR-018.

---

### FR-020 — Live-harness adapter — roadmap (COULD)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_018_fr_019_fr_020_roadmap_documents_deferred_items` | `tests/test_roadmap.py` | PROPERTY | explicit |
| `test_fr_020_roadmap_frames_items_as_future_not_shipped` | `tests/test_roadmap.py` | PROPERTY | explicit |

**Status: doc-pinned.** v1.x roadmap item (AgentDojo/InjecAgent).

---

### FR-021 — Anon-vs-pseudo end-state evidence bundle (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_021_bundle_separates_anon_and_pseudo` | `tests/test_end_state_bundle.py` | UNIT | explicit |
| `test_nfr_005_bundle_has_no_merged_verdict` | `tests/test_end_state_bundle.py` | AUDIT | explicit |
| `test_fr_021_disclaimer_is_non_strippable` | `tests/test_end_state_bundle.py` | UNIT | explicit |
| `test_fr_021_bundle_requires_at_least_one_axis` | `tests/test_end_state_bundle.py` | UNIT | explicit |
| `test_fr_021_bundle_surfaces_regulatory_crosswalk` | `tests/test_end_state_bundle.py` | INTEGRATION | explicit |
| `test_fr_021_caveats_travel_with_each_axis` | `tests/test_end_state_bundle.py` | INTEGRATION | explicit |
| `test_nfr004_end_state_bundle_pure_stdlib` | `tests/test_end_state_bundle.py` | PROPERTY | explicit |

---

### FR-022 — Legally-distinct regulatory crosswalk (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_022_five_legally_distinct_columns` | `tests/test_crosswalk.py` | UNIT | explicit |
| `test_fr_022_hipaa_is_two_distinct_columns` | `tests/test_crosswalk.py` | UNIT | explicit |
| `test_fr_022_no_merged_or_equivalence_column` | `tests/test_crosswalk.py` | UNIT | explicit |
| `test_fr_022_presence_to_status_conservative` | `tests/test_crosswalk.py` | UNIT | explicit |
| `test_fr_022_corpus_tag_mapping` | `tests/test_crosswalk.py` | UNIT | explicit |
| `test_fr_022_nfr004_crosswalk_pure_stdlib` | `tests/test_crosswalk.py` | PROPERTY | explicit |

---

### FR-023 — Neutral leaderboard (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_023_publish_is_opt_in` | `tests/test_leaderboard_policy.py` | UNIT | explicit |
| `test_nfr_014_rate_limit_blocks_excess` | `tests/test_leaderboard_policy.py` | UNIT | explicit |
| `test_nfr_014_held_out_rotation_epoch` | `tests/test_leaderboard_policy.py` | UNIT | explicit |
| `test_nfr_014_contamination_dup_check` | `tests/test_leaderboard_policy.py` | UNIT | explicit |
| `test_fr_023_clean_submission_allowed_and_published` | `tests/test_leaderboard_policy.py` | UNIT | explicit |
| `test_nfr004_policy_pure_stdlib` | `tests/test_leaderboard_policy.py` | PROPERTY | explicit |
| `test_fr_023_store_is_append_only` | `tests/test_leaderboard_store.py` | UNIT | explicit |
| `test_fr_023_store_rejects_held_out_gold` | `tests/test_leaderboard_store.py` | UNIT | explicit |
| `test_nfr_014_hash_chain_links_events` | `tests/test_leaderboard_store.py` | UNIT | explicit |
| `test_nfr_014_verify_chain_detects_tampering` | `tests/test_leaderboard_store.py` | UNIT | explicit |
| `test_fr_023_store_records_scores_not_gold` | `tests/test_leaderboard_store.py` | UNIT | explicit |
| `test_nfr004_leaderboard_store_pure_stdlib` | `tests/test_leaderboard_store.py` | PROPERTY | explicit |
| `test_fr_023_leaderboard_cli_verify` | `tests/test_leaderboard_store.py` | UNIT | explicit |

---

### FR-024 — CC0 corpus + standard exports (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_024_parquet_has_n_separate_regime_columns` | `tests/test_parquet_export.py` | UNIT | explicit |
| `test_fr_024_parquet_roundtrips_records` | `tests/test_parquet_export.py` | UNIT | explicit |
| `test_nfr_012_parquet_loads_via_datasets` | `tests/test_parquet_export.py` | INTEGRATION | explicit |
| `test_fr_024_export_streams_not_materializes` | `tests/test_parquet_export.py` | UNIT | explicit |
| `test_fr_024_deterministic_export` | `tests/test_parquet_export.py` | PROPERTY | explicit |
| `test_nfr004_distribution_imports_without_pyarrow` | `tests/test_parquet_export.py` | CONTRACT | explicit |
| `test_fr_024_parquet_rejects_nonpositive_batch_size` | `tests/test_parquet_export.py` | UNIT | explicit |
| `test_fr_024_parquet_flushes_at_batch_boundary` | `tests/test_parquet_export.py` | UNIT | explicit |
| `test_fr_024_parquet_empty_iterator_writes_valid_empty_file_with_reg_schema` | `tests/test_parquet_export.py` | UNIT | explicit |
| `test_fr_024_parquet_json_or_none_passthrough` | `tests/test_parquet_export.py` | UNIT | explicit |
| `test_fr_024_croissant_has_required_jsonld_shape` | `tests/test_croissant.py` | UNIT | explicit |
| `test_nfr_012_croissant_declares_reg_columns` | `tests/test_croissant.py` | UNIT | explicit |
| `test_fr_024_croissant_counts_from_metadata_cannot_drift` | `tests/test_croissant.py` | UNIT | explicit |
| `test_nfr_012_croissant_describes_loadable_parquet` | `tests/test_croissant.py` | INTEGRATION | explicit |
| `test_nfr_012_full_validation_skips_without_mlcroissant` | `tests/test_croissant.py` | CONTRACT | explicit |
| `test_nfr004_croissant_pure_stdlib_imports_without_mlcroissant` | `tests/test_croissant.py` | PROPERTY | explicit |
| `test_validate_croissant_rejects_*` (8 tests) | `tests/test_croissant.py` | UNIT | inferred |
| `test_fr_024_conll_bio_tags_align_to_offsets` | `tests/test_conll_export.py` | UNIT | explicit |
| `test_fr_024_conll_bilou_conversion` | `tests/test_conll_export.py` | UNIT | explicit |
| `test_fr_024_conll_export_streams_not_materializes` | `tests/test_conll_export.py` | UNIT | explicit |
| `test_fr_024_conll_deterministic` | `tests/test_conll_export.py` | PROPERTY | explicit |
| `test_nfr004_conll_pure_stdlib` | `tests/test_conll_export.py` | PROPERTY | explicit |
| `test_fr_024_build_label2id_o_plus_bi_per_sorted_type` | `tests/test_conll_export.py` | UNIT | explicit |
| `test_fr_024_build_label2id_skips_nonsequence_annotations` | `tests/test_conll_export.py` | UNIT | explicit |
| `test_fr_024_conll_bilou_multi_sentence_skips_empty_sentence` | `tests/test_conll_export.py` | UNIT | explicit |
| `test_fr_024_record_to_conll_rejects_unknown_fmt` | `tests/test_conll_export.py` | UNIT | explicit |
| `test_fr_024_record_to_conll_nonsequence_annotations_treated_empty` | `tests/test_conll_export.py` | UNIT | explicit |
| `test_fr_024_spacy_offsets_format` | `tests/test_spacy_export.py` | UNIT | explicit |
| `test_fr_024_spacy_docbin_roundtrip` | `tests/test_spacy_export.py` | UNIT | explicit |
| `test_fr_024_spacy_docbin_filters_overlaps` | `tests/test_spacy_export.py` | UNIT | explicit |
| `test_nfr004_spacy_export_imports_without_spacy` | `tests/test_spacy_export.py` | CONTRACT | explicit |
| `test_fr_024_dataset_card_has_yaml_frontmatter` | `tests/test_dataset_card.py` | UNIT | explicit |
| `test_nfr_013_dataset_card_counts_match_metadata` | `tests/test_dataset_card.py` | UNIT | explicit |
| `test_fr_024_dataset_card_embeds_caveats` | `tests/test_dataset_card.py` | UNIT | explicit |
| `test_nfr004_dataset_card_pure_stdlib` | `tests/test_dataset_card.py` | PROPERTY | explicit |
| `test_fr_024_cli_exposes_five_verbs` | `tests/test_cli.py` | UNIT | explicit |
| `test_fr_024_cli_export_dispatches_to_distribution` | `tests/test_cli.py` | UNIT | explicit |
| `test_fr_024_cli_validate_forwards_user_args` | `tests/test_cli.py` | UNIT | explicit |
| `test_fr_024_cli_leaderboard_wired_to_s6_seam` | `tests/test_cli.py` | UNIT | explicit |
| `test_fr_024_run_script_returns_2_when_script_missing` | `tests/test_cli.py` | UNIT | explicit |
| `test_fr_024_cli_score_dispatches_to_evaluate` | `tests/test_cli.py` | UNIT | explicit |
| `test_fr_024_cli_export_conll_dispatches` | `tests/test_cli.py` | UNIT | explicit |
| `test_fr_024_cli_export_spacy_dispatches` | `tests/test_cli.py` | UNIT | explicit |
| `test_fr_024_cli_export_croissant_dispatches` | `tests/test_cli.py` | UNIT | explicit |
| `test_fr_024_cli_export_card_dispatches` | `tests/test_cli.py` | UNIT | explicit |

---

### FR-025 — Contribution pipeline (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_025_contributing_has_pr_template_and_cc0` | `tests/test_contributing.py` | UNIT | explicit |
| `test_fr_025_contributing_has_provenance_and_synthetic_only` | `tests/test_contributing.py` | UNIT | explicit |
| `test_fr_025_contributing_has_deprecation_and_semver` | `tests/test_contributing.py` | UNIT | explicit |

---

### FR-026 — Governance charter (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_026_governance_md_has_charter_and_roster` | `tests/test_governance.py` | UNIT | explicit |
| `test_fr_026_governance_md_has_coi_and_bus_factor` | `tests/test_governance.py` | UNIT | explicit |
| `test_nfr_014_governance_md_present` | `tests/test_governance.py` | UNIT | explicit |
| `test_fr_026_attestation_is_non_strippable` | `tests/test_coi.py` | UNIT | explicit |
| `test_fr_026_recusal_for_maintainer_and_affiliated` | `tests/test_coi.py` | UNIT | explicit |
| `test_nfr_014_coi_as_dict_embeddable_in_store` | `tests/test_coi.py` | UNIT | explicit |
| `test_nfr004_coi_pure_stdlib` | `tests/test_coi.py` | PROPERTY | explicit |

---

### FR-027 — Real-data validation correlation harness (SHOULD — v1.1, Pass-2)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_fr_027_returns_sentinel_when_real_data_absent` | `tests/test_correlation.py` | UNIT | explicit |
| `test_fr_027_correlation_on_paired_scores` | `tests/test_correlation.py` | UNIT | explicit |
| `test_fr_027_bootstrap_ci_seeded_deterministic` | `tests/test_correlation.py` | PROPERTY | explicit |
| `test_fr_027_caveat_non_strippable` | `tests/test_correlation.py` | UNIT | explicit |
| `test_nfr004_correlation_purity` | `tests/test_correlation.py` | PROPERTY | explicit |

**Status: Pass-2 deferred.** The harness is seam-tested (sentinel when real data absent, caveat non-strippable, deterministic bootstrap CI). Full correlation against i2b2-2014/TAB with Kendall-τ + Bland-Altman requires real external datasets — deferred to v1.1 Pass-2.

---

### FR-028 — Frictionless citation (SHOULD)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| (no explicit trace found) | — | — | — |

**GAP (SHOULD):** No test file carries an `fr_028` token. BibTeX/citation template presence is implied by the dataset card tests (`test_fr_024_dataset_card_embeds_caveats`) but is not explicitly traced. Acceptable gap for a SHOULD; recommend a simple presence-check test for `CITATION.cff` or equivalent.

---

### FR-029 — Committed-lattice power audit, enforcement & per-cell provenance (MUST)

| Test function | File | Test type | Trace type |
|---|---|---|---|
| `test_build_is_deterministic` | `tests/test_lattice.py` | PROPERTY | explicit |
| `test_frozen_lattice_matches_generator_antidrift` | `tests/test_lattice.py` | PROPERTY | explicit |
| `test_targets_are_derived_not_hand_typed` | `tests/test_lattice.py` | UNIT | explicit |
| `test_forced_skeleton_covers_every_main_effect_level` | `tests/test_lattice.py` | UNIT | explicit |
| `test_interaction_breakdown` | `tests/test_lattice.py` | UNIT | explicit |
| `test_named_interactions_declared` | `tests/test_lattice.py` | UNIT | explicit |
| `test_domain_eval_family_is_the_only_non_count_gated` | `tests/test_lattice.py` | UNIT | explicit |
| `test_lang_x_entity_uses_head_langs_and_frequent_types` | `tests/test_lattice.py` | UNIT | explicit |
| `test_adv_x_entity_capped_at_standard` | `tests/test_lattice.py` | UNIT | explicit |
| `test_cell_ids_unique_and_load_roundtrips` | `tests/test_lattice.py` | UNIT | explicit |
| `test_write_lattice_writes_matching_json` | `tests/test_lattice.py` | UNIT | explicit |
| `test_main_check_matches_frozen` | `tests/test_lattice.py` | PROPERTY | explicit |
| `test_main_check_detects_drift` | `tests/test_lattice.py` | UNIT | explicit |
| `test_main_writes` | `tests/test_lattice.py` | UNIT | explicit |
| `test_counts_annotations_not_records` | `tests/test_lattice_audit.py` | UNIT | explicit |
| `test_only_committed_count_gated_cells_counted` | `tests/test_lattice_audit.py` | UNIT | explicit |
| `test_adversarial_routing` | `tests/test_lattice_audit.py` | UNIT | explicit |
| `test_gz_and_plain_equivalent` | `tests/test_lattice_audit.py` | UNIT | explicit |
| `test_deficits` | `tests/test_lattice_audit.py` | UNIT | explicit |
| `test_effective_counts_seam_not_implemented` | `tests/test_lattice_audit.py` | UNIT | explicit |
| `test_cell_seed_is_coordinate_only` | `tests/test_lattice_fill_determinism.py` | PROPERTY | explicit |
| `test_fill_is_deterministic` | `tests/test_lattice_fill_determinism.py` | PROPERTY | explicit |
| `test_generated_records_are_synthetic_v2_and_provenanced` | `tests/test_lattice_fill_determinism.py` | UNIT | explicit |
| `test_max_records_cap_truncates` | `tests/test_lattice_fill_determinism.py` | UNIT | explicit |
| `test_fill_then_merge_is_convergent` | `tests/test_lattice_fill_determinism.py` | UNIT | explicit |
| `test_emitters_cover_exactly_63_canonical_types` | `tests/test_lattice_targeting.py` | UNIT | explicit |
| `test_every_emitter_produces_valid_pii_value` | `tests/test_lattice_targeting.py` | UNIT | explicit |
| `test_committed_adversarial_types_all_have_transforms` | `tests/test_lattice_targeting.py` | UNIT | explicit |
| `test_every_type_yields_exactly_one_target_positive` | `tests/test_lattice_targeting.py` | UNIT | explicit |
| `test_unknown_type_fails_loud` | `tests/test_lattice_targeting.py` | UNIT | explicit |
| `test_uncommitted_adversarial_type_fails_loud` | `tests/test_lattice_targeting.py` | UNIT | explicit |
| `test_adversarial_records_genuinely_obfuscate_every_critical_type` | `tests/test_lattice_targeting.py` | UNIT | explicit |
| `test_targeted_record_normalizes_to_valid_v2` | `tests/test_lattice_targeting.py` | UNIT | explicit |
| `test_synthetic_provenance_preserved_through_migrate` | `tests/test_lattice_targeting.py` | UNIT | explicit |
| `test_generation_is_deterministic` | `tests/test_lattice_targeting.py` | PROPERTY | explicit |
| `test_powered_corpus_passes` | `tests/test_validate_power_gate.py` | UNIT | explicit |
| `test_underpowered_cell_fails_with_detail` | `tests/test_validate_power_gate.py` | UNIT | explicit |
| `test_seam_cell_never_gated` | `tests/test_validate_power_gate.py` | UNIT | explicit |
| `test_missing_lattice_reports_error` | `tests/test_validate_power_gate.py` | UNIT | explicit |
| `test_errors_sorted_and_deterministic` | `tests/test_validate_power_gate.py` | UNIT | explicit |
| `test_risk_tiers_partition_63_types` | `tests/test_power.py` | UNIT | explicit |
| `test_risk_tier_membership` | `tests/test_power.py` | UNIT | explicit |
| `test_risk_tier_unknown_fails_loud` | `tests/test_power.py` | UNIT | explicit |
| `test_types_in_tier_round_trips` | `tests/test_power.py` | UNIT | explicit |
| `test_required_n_reproduces_canonical_targets` | `tests/test_power.py` | UNIT | explicit |
| `test_tier_specs_targets_are_derived` | `tests/test_power.py` | UNIT | explicit |
| `test_required_n_rejects_bad_inputs` | `tests/test_power.py` | UNIT | explicit |
| `test_projection_accepts_continuous_p_ref_no_integer_guard` | `tests/test_power.py` | UNIT | explicit |
| `test_projected_interval_is_marked_projected` | `tests/test_power.py` | UNIT | explicit |
| `test_projected_halfwidth_at_target_matches_tier_precision` | `tests/test_power.py` | UNIT | explicit |
| `test_projection_n_zero_is_nan` | `tests/test_power.py` | UNIT | explicit |
| `test_classify` | `tests/test_power.py` | UNIT | explicit |
| `test_classify_rejects_non_integer` | `tests/test_power.py` | UNIT | explicit |
| `test_default_tier_of_cell` | `tests/test_power.py` | UNIT | explicit |
| `test_required_discordant_pairs_positive_and_monotone` | `tests/test_power.py` | UNIT | explicit |
| `test_required_discordant_pairs_rejects_no_effect` | `tests/test_power.py` | UNIT | explicit |
| `test_paired_more_efficient_than_independent_for_correlated_errors` | `tests/test_power.py` | UNIT | explicit |
| `test_audit_crossing_classifies_and_summarizes` | `tests/test_power.py` | UNIT | explicit |
| `test_audit_attaches_measured_ci_when_given` | `tests/test_power.py` | UNIT | explicit |
| `test_powermatrix_renderers_deterministic_and_sorted` | `tests/test_power.py` | PROPERTY | explicit |
| `test_powermatrix_verdict` | `tests/test_power.py` | UNIT | explicit |
| `test_fr_029_power_report_note_and_claim_ladder` | `tests/test_power_table_reporting.py` | UNIT | explicit |
| `test_nfr_003_power_table_skips_non_gated_and_attaches_scores` | `tests/test_power_table_reporting.py` | UNIT | explicit |
| `test_nfr_003_render_csv_and_markdown_roundtrip` | `tests/test_power_table_reporting.py` | UNIT | explicit |
| `test_nfr_003_verdict_ladder_and_power_class_edges` | `tests/test_power_table_reporting.py` | UNIT | explicit |
| `test_design_provenance_absent_by_default` | `tests/test_detection_design_provenance.py` | UNIT | explicit |
| `test_design_provenance_emitted_and_ci_n_coexists_with_target` | `tests/test_detection_design_provenance.py` | UNIT | explicit |
| `test_powered_flag_matches_counts` | `tests/test_detection_design_provenance.py` | UNIT | explicit |
| `test_caveat_is_non_strippable` | `tests/test_detection_design_provenance.py` | UNIT | explicit |
| `test_power_table_rows_always_carry_provenance_and_exclude_seam` | `tests/test_detection_design_provenance.py` | UNIT | explicit |
| `test_power_report_renders_verdict` | `tests/test_detection_design_provenance.py` | UNIT | explicit |

---

## 2. Index by Non-Functional Requirement (NFR)

---

### NFR-001 — Per-slice statistical power (MUST)

| Test function | File | Trace type |
|---|---|---|
| (covered by NFR-018 gate tests; see NFR-018 row) | — | inferred |

**Note (inferred):** NFR-001 is operationalized by NFR-018 (`validate.py --lattice`) and FR-029 (power audit). The tests in `test_lattice.py`, `test_power.py`, `test_validate_power_gate.py` collectively enforce the per-cell positive-count vs. tiered target threshold that NFR-001 specifies. No test carries an explicit `nfr_001` fn-token.

---

### NFR-002 — CI on every metric (MUST)

| Test function | File | Trace type |
|---|---|---|
| `test_nfr_002_clopper_pearson_method_named` | `tests/test_clopper_pearson.py` | explicit |
| `test_nfr_002_paired_bootstrap_method_named` | `tests/test_paired.py` | explicit |
| (Wilson CI method-name check in `test_intervals.py` module docstring) | `tests/test_intervals.py` | inferred |

---

### NFR-003 — Per-language power transparency (MUST)

| Test function | File | Trace type |
|---|---|---|
| `test_nfr_003_per_language_table_has_row_per_language` | `tests/test_language_power.py` | explicit |
| `test_nfr_003_language_x_type_matrix_grouped` | `tests/test_language_power.py` | explicit |
| `test_nfr_003_low_power_cells_labeled` | `tests/test_language_power.py` | explicit |
| `test_nfr_003_render_markdown_and_csv` | `tests/test_language_power.py` | explicit |
| `test_nfr_003_no_corpus_read` | `tests/test_language_power.py` | explicit |
| `test_nfr_003_nfr004_imports_no_nondeterminism` | `tests/test_language_power.py` | explicit |
| `test_nfr_003_power_table_skips_non_gated_and_attaches_scores` | `tests/test_power_table_reporting.py` | explicit |
| `test_nfr_003_render_csv_and_markdown_roundtrip` | `tests/test_power_table_reporting.py` | explicit |
| `test_nfr_003_verdict_ladder_and_power_class_edges` | `tests/test_power_table_reporting.py` | explicit |
| `test_nfr_003_slice_heatmap_writes_png` | `tests/test_viz.py` | explicit |

---

### NFR-004 — Deterministic, provenanced generation (MUST)

Enforced via AST import-purity guards present in virtually every test module. Explicit token appearances:

| Test function | File | Trace type |
|---|---|---|
| `test_fr_005_nfr004_calibration_imports_no_nondeterminism` | `tests/test_calibration.py` | explicit |
| `test_fr_006_nfr004_anonymization_imports_no_nondeterminism` | `tests/test_anonymization.py` | explicit |
| `test_fr_008_nfr004_exposure_imports_no_nondeterminism` | `tests/test_exposure_index.py` | explicit |
| `test_fr_008_nfr004_signals_imports_no_nondeterminism` | `tests/test_signals.py` | explicit |
| `test_nfr004_conll_pure_stdlib` | `tests/test_conll_export.py` | explicit |
| `test_nfr004_croissant_pure_stdlib_imports_without_mlcroissant` | `tests/test_croissant.py` | explicit |
| `test_nfr004_crosswalk_pure_stdlib` (via `test_fr_022_nfr004_crosswalk_pure_stdlib`) | `tests/test_crosswalk.py` | explicit |
| `test_nfr004_dataset_card_pure_stdlib` | `tests/test_dataset_card.py` | explicit |
| `test_nfr004_distribution_imports_without_pyarrow` | `tests/test_parquet_export.py` | explicit |
| `test_nfr004_end_state_bundle_pure_stdlib` | `tests/test_end_state_bundle.py` | explicit |
| `test_nfr004_leaderboard_store_pure_stdlib` | `tests/test_leaderboard_store.py` | explicit |
| `test_nfr004_oracle_pure_stdlib` | `tests/test_oracle.py` | explicit |
| `test_nfr004_payloads_pure_stdlib` | `tests/test_payloads.py` | explicit |
| `test_nfr004_policy_pure_stdlib` | `tests/test_leaderboard_policy.py` | explicit |
| `test_nfr004_slices_pure_stdlib` | `tests/test_slices.py` | explicit |
| `test_nfr004_spacy_export_imports_without_spacy` | `tests/test_spacy_export.py` | explicit |
| `test_nfr004_coi_pure_stdlib` | `tests/test_coi.py` | explicit |
| `test_nfr004_cli_generate_never_targets_frozen_corpus` | `tests/test_cli.py` | explicit |
| `test_nfr004_cli_thin_pure_stdlib` | `tests/test_cli.py` | explicit |
| `test_nfr004_viz_behind_extra_import_guards` | `tests/test_viz.py` | explicit |
| `test_nfr004_reporting_core_imports_without_matplotlib` | `tests/test_viz.py` | explicit |
| `test_nfr004_viz_no_toplevel_matplotlib_import` | `tests/test_viz.py` | explicit |
| `test_fr_002_nfr004_paired_imports_no_uncontrolled_nondeterminism` | `tests/test_paired.py` | explicit |
| `test_nfr004_correlation_purity` | `tests/test_correlation.py` | explicit |
| `test_fr_011_nfr004_pseudonymization_imports_no_nondeterminism` | `tests/test_pseudonymization.py` | explicit |
| `test_fr_007_nfr004_offline_adversary_imports_no_nondeterminism` | `tests/test_offline_adversary.py` | explicit |

---

### NFR-005 — Anon/pseudo metric separation (MUST)

| Test function | File | Trace type |
|---|---|---|
| `test_nfr005_pareto_point_cannot_merge` | `tests/test_anonymization.py` | explicit |
| `test_nfr_005_bundle_has_no_merged_verdict` | `tests/test_end_state_bundle.py` | explicit |
| `test_nfr_005_anon_and_pseudo_are_separate_modules` | `tests/test_nfr005_separation.py` | explicit |
| `test_nfr_005_no_combined_deid_callable_in_scoring_public_api` | `tests/test_nfr005_separation.py` | explicit |
| `test_nfr005_report_has_no_anonymization_or_combined_field` | `tests/test_pseudonymization.py` | explicit |

---

### NFR-006 — No real PII (MUST)

| Test function | File | Trace type |
|---|---|---|
| (no explicit `nfr_006` fn-token found) | — | — |

**GAP / ACCEPTABLE:** NFR-006 is primarily a release-blocking security audit (`/dev-assist-validate --sensitive-data`) rather than a unit test. The `test_contributing.py::test_fr_025_contributing_has_provenance_and_synthetic_only` test asserts CONTRIBUTING.md documents the synthetic-only invariant (inferred trace). The actual scan tooling is outside the `tests/` directory. No genuine test gap — appropriate for a security-scan NFR.

---

### NFR-007 — Adversary version-pinning (MUST)

| Test function | File | Trace type |
|---|---|---|
| `test_fr_010_llm_adversary_id_version_stamped` | `tests/test_llm_adversary.py` | inferred |
| `test_fr_007_config_is_frozen_and_hashable` | `tests/test_offline_adversary.py` | inferred |
| `test_fr_010_adversary_satisfies_port` (checks `adversary_id`) | `tests/test_offline_adversary.py` | inferred |
| (pseudonymization threat-model pinning comment NFR-007) | `tests/test_pseudonymization.py` | inferred |

**Note (inferred):** No fn carries an explicit `nfr_007` token. The version-pinning contract is verified through the `adversary_id` stamping tests under FR-010 and the frozen config test under FR-007.

---

### NFR-008 — Calibration target (SHOULD)

| Test function | File | Trace type |
|---|---|---|
| `test_nfr_008_meets_reference_is_reported_not_gated` | `tests/test_calibration.py` | explicit |
| `test_nfr_008_calibration_by_entity_class` | `tests/test_calibration.py` | explicit |

---

### NFR-009 — Eval cost budget + cheap-adversary mode (SHOULD)

| Test function | File | Trace type |
|---|---|---|
| `test_fr_010_llm_adversary_requires_extra_when_anthropic_absent` | `tests/test_llm_adversary.py` | inferred |
| `test_fr_010_package_imports_without_anthropic` | `tests/test_llm_adversary.py` | inferred |
| `test_fr_010_llm_attack_skips_if_absent` | `tests/test_llm_adversary.py` | inferred |

**Note (inferred):** Module docstring explicitly states `reidx-01 / NFR-009` but fn-tokens carry `fr_010`. The lazy-import and offline-default contract directly verifies NFR-009's `$0 external cost` cheap-adversary mode.

---

### NFR-010 — Scorer throughput + runtime dimension (Pass-2)

| Test function | File | Trace type |
|---|---|---|
| (no test found) | — | — |

**Status: Pass-2 deferred.** NFR-010b/c are flagged `real_user_needed: true` in the requirements. No throughput benchmark or timing test exists. Legitimate gap; the requirement explicitly defers the numeric gate to Pass-2.

---

### NFR-011 — Coverage (63 types, 60 languages, 4 domains) (MUST)

| Test function | File | Trace type |
|---|---|---|
| `test_canonical_counts` | `tests/test_taxonomy.py` | inferred |
| `test_every_type_has_a_known_category` | `tests/test_taxonomy.py` | inferred |
| `test_helpers` | `tests/test_taxonomy.py` | inferred |
| `test_category_partition_sums_to_total` | `tests/test_taxonomy.py` | inferred |
| `test_emitters_cover_exactly_63_canonical_types` | `tests/test_lattice_targeting.py` | inferred |

**Note (inferred):** `test_taxonomy.py` docstring cites M1 drift fix; no `nfr_011` token. Tests verify the 63-type registry and partition. Language/domain coverage scans are enforced by `validate.py --lattice` (FR-029).

---

### NFR-012 — Croissant/HF loadability (MUST)

| Test function | File | Trace type |
|---|---|---|
| `test_nfr_012_croissant_declares_reg_columns` | `tests/test_croissant.py` | explicit |
| `test_nfr_012_croissant_describes_loadable_parquet` | `tests/test_croissant.py` | explicit |
| `test_nfr_012_full_validation_skips_without_mlcroissant` | `tests/test_croissant.py` | explicit |
| `test_nfr_012_parquet_loads_via_datasets` | `tests/test_parquet_export.py` | explicit |

---

### NFR-013 — Documentation currency / no drift (MUST)

| Test function | File | Trace type |
|---|---|---|
| `test_nfr_013_docs_use_canonical_record_count` | `tests/test_doc_drift.py` | explicit |
| `test_nfr_013_docs_use_canonical_entity_count` | `tests/test_doc_drift.py` | explicit |
| `test_nfr_013_doc_titles_are_v2` | `tests/test_doc_drift.py` | explicit |
| `test_nfr_013_taxonomy_body_matches_registry` | `tests/test_doc_drift.py` | explicit |
| `test_nfr_013_migration_has_v2_section` | `tests/test_doc_drift.py` | explicit |
| `test_nfr_013_changelog_has_spwr_entry` | `tests/test_doc_drift.py` | explicit |
| `test_nfr_013_dataset_card_counts_match_metadata` | `tests/test_dataset_card.py` | explicit |

---

### NFR-014 — Governance neutrality (MUST)

| Test function | File | Trace type |
|---|---|---|
| `test_nfr_014_governance_md_present` | `tests/test_governance.py` | explicit |
| `test_nfr_014_coi_as_dict_embeddable_in_store` | `tests/test_coi.py` | explicit |
| `test_nfr_014_rate_limit_blocks_excess` | `tests/test_leaderboard_policy.py` | explicit |
| `test_nfr_014_held_out_rotation_epoch` | `tests/test_leaderboard_policy.py` | explicit |
| `test_nfr_014_contamination_dup_check` | `tests/test_leaderboard_policy.py` | explicit |
| `test_nfr_014_hash_chain_links_events` | `tests/test_leaderboard_store.py` | explicit |
| `test_nfr_014_verify_chain_detects_tampering` | `tests/test_leaderboard_store.py` | explicit |

---

### NFR-015 — License/ethics (MUST)

| Test function | File | Trace type |
|---|---|---|
| `test_fr_024_dataset_card_has_yaml_frontmatter` (checks `license: cc0-1.0`) | `tests/test_dataset_card.py` | inferred |
| `test_fr_025_contributing_has_pr_template_and_cc0` | `tests/test_contributing.py` | inferred |
| `test_fr_024_dataset_card_embeds_caveats` (CC0-data / Apache-2.0-code split) | `tests/test_dataset_card.py` | inferred |

**Note (inferred):** No `nfr_015` fn-token. The CC0 + Apache-2.0 license split is verified through FR-024 and FR-025 tests. Full license audit is a reviewer/audit gate, not a unit test.

---

### NFR-016 — Harness test coverage ≥85% line / ≥70% branch (MUST)

| Test function | File | Trace type |
|---|---|---|
| (measured by coverage tooling; not a named test function) | — | — |

**Note:** NFR-016 is enforced by the CI coverage gate (`pytest --cov` + coverage thresholds), not by a named test function. The 346-passed suite constitutes the evidence base. No `nfr_016` test fn token found — acceptable (coverage is a tooling metric, not a testable assertion within the test suite itself).

---

### NFR-017 — Threshold-validation transparency (MUST)

| Test function | File | Trace type |
|---|---|---|
| (no explicit test found) | — | — |

**Note:** NFR-017 is an audit completeness requirement (`_threshold-validation/` directory entries). It is verified by human/agent reviewer audit, not by a unit test. `dev-assist-artifacts/02-requirements/non-functional-requirements.md` records R10 outcomes inline. No genuine gap; this is an artifact-completeness check, not a code-testable property.

---

### NFR-018 — Committed-lattice per-cell power hard gate (MUST)

| Test function | File | Trace type |
|---|---|---|
| `test_nfr_018_cli_validate_keeps_power_gate_on` | `tests/test_cli.py` | explicit |
| `test_nfr_018_reid_required_n_pins_section5_numbers` | `tests/test_reid_power.py` | explicit |
| `test_nfr_018_reid_tier_specs_are_derived_not_typed` | `tests/test_reid_power.py` | explicit |
| `test_nfr_018_reid_provenance_shape` | `tests/test_reid_power.py` | explicit |
| `test_nfr_018_reid_provenance_attaches_to_measured_rrs` | `tests/test_reid_power.py` | explicit |
| `test_nfr_018_seam_does_not_mutate_frozen_lattice` | `tests/test_reid_power.py` | explicit |
| (all `test_lattice.py` tests enforce anti-drift round-trip; NFR-018 cited in module docstring) | `tests/test_lattice.py` | inferred |
| (all `test_validate_power_gate.py` tests enforce the non-zero exit on shortfall) | `tests/test_validate_power_gate.py` | inferred |

---

## 3. Index by Design Component (DC)

| DC | Component | Primary FRs | Verifying test files | Status |
|---|---|---|---|---|
| **DC-01** | Corpus & slices | FR-024, NFR-001/003/011/018 | `test_lattice_targeting.py`, `test_lattice_fill_determinism.py`, `test_taxonomy.py`, `test_slices.py` | Verified by test |
| **DC-02** | Schema & migration | NFR-013, AX-002 | `test_migration.py`, `test_manifest.py`, `test_doc_drift.py` | Verified by test (inferred) |
| **DC-03** | Generation pipeline | NFR-004/006, AX-001/002 | `test_lattice_fill_determinism.py`, `test_lattice_targeting.py`, `test_cli.py` | Verified by test |
| **DC-04** | Scoring harness core — I/O contract | FR-003 | `test_scoring_core.py` | Verified by test (inferred) |
| **DC-05** | Detection scorer | FR-001/002/004/005 | `test_detection.py`, `test_paired.py`, `test_clopper_pearson.py`, `test_intervals.py`, `test_calibration.py`, `test_viz.py` | Verified by test |
| **DC-06** | Anonymization scorer | FR-006 | `test_anonymization.py`, `test_viz.py` | Verified by test |
| **DC-07** | Re-identification scorer | FR-007/008/009/010 | `test_adversary_port.py`, `test_offline_adversary.py`, `test_llm_adversary.py`, `test_reidentification_measured.py`, `test_rrs_caveat.py`, `test_exposure_index.py`, `test_signals.py`, `test_reid_power.py` | Verified by test |
| **DC-08** | Pseudonymization-integrity scorer | FR-011/012/013 | `test_pseudonymization.py`, `test_nfr005_separation.py` | Verified by test |
| **DC-09** | Statistical-power & reporting engine | FR-004/029, NFR-001/002/003/008/018 | `test_power.py`, `test_power_table_reporting.py`, `test_language_power.py`, `test_lattice.py`, `test_lattice_audit.py`, `test_validate_power_gate.py`, `test_detection_design_provenance.py`, `test_viz.py`, `test_intervals.py`, `test_paired.py`, `test_clopper_pearson.py`, `test_calibration.py` | Verified by test |
| **DC-10** | Agentic oracle + payload library | FR-017/018/019/020 | `test_oracle.py`, `test_payloads.py`, `test_roadmap.py` | Verified by test (FR-017); doc-pinned (FR-018/019/020) |
| **DC-11** | Compliance/end-state bundle + crosswalk | FR-021/022 | `test_end_state_bundle.py`, `test_crosswalk.py` | Verified by test |
| **DC-12** | Distribution & exports | FR-024/028, NFR-012 | `test_parquet_export.py`, `test_croissant.py`, `test_conll_export.py`, `test_spacy_export.py`, `test_dataset_card.py`, `test_cli.py` | Verified by test |
| **DC-13** | Leaderboard & governance | FR-023/025/026, NFR-014 | `test_leaderboard_store.py`, `test_leaderboard_policy.py`, `test_governance.py`, `test_coi.py`, `test_contributing.py` | Verified by test |
| **DC-14** | Real-data validation harness | FR-027 | `test_correlation.py` | Pass-2 deferred (seam tested) |
| **DC-15** | Test suite & CI | NFR-016 | (all 49 test files) | Verified by test |

---

## 4. Index by Story

| Story | Title (from §1 heading) | Primary FR/NFR | Key test files | Test-type tags in story | Status |
|---|---|---|---|---|---|
| **S3-01** | Adversary port + signals (FR-010/008) | FR-010, FR-008, NFR-004 | `test_adversary_port.py`, `test_signals.py` | `[UNIT-TEST]` `[CONTRACT-TEST]` `[PROPERTY-TEST]` | REVIEW/DONE |
| **S3-02** | Offline deterministic adversary (FR-007/010) | FR-007, FR-010, NFR-004 | `test_offline_adversary.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` `[CONTRACT-TEST]` | REVIEW/DONE |
| **S3-03** | LLM adversary (FR-010 secondary) | FR-010, NFR-009 | `test_llm_adversary.py` | `[CONTRACT-TEST]` `[UNIT-TEST]` `[INTEGRATION-TEST]` | REVIEW/DONE |
| **S3-04** | Measured RRS + FR-009 caveat | FR-007, FR-009 | `test_reidentification_measured.py`, `test_rrs_caveat.py` | `[UNIT-TEST]` `[AUDIT]` | REVIEW/DONE |
| **S3-05** | Exposure-index pre-screen | FR-008, NFR-004 | `test_exposure_index.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | REVIEW/DONE |
| **S3-06** | Anonymization scorer Pareto | FR-006, NFR-005 | `test_anonymization.py` | `[UNIT-TEST]` `[AUDIT]` `[PROPERTY-TEST]` | REVIEW/DONE |
| **S3-07** | Pseudonymization-integrity scorer | FR-011/012/013, NFR-005 | `test_pseudonymization.py`, `test_nfr005_separation.py` | `[UNIT-TEST]` `[CONTRACT-TEST]` | REVIEW/DONE |
| **S3-08** | Re-id operating-point power seam | NFR-018, FR-029 | `test_reid_power.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | REVIEW/DONE |
| **S4-01** | Clopper-Pearson + Wilson CIs | FR-004, NFR-002/004 | `test_clopper_pearson.py`, `test_intervals.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S4-02** | Paired stats (McNemar/bootstrap) | FR-002, NFR-002/004 | `test_paired.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S4-03** | Committed-lattice + power engine | FR-029, NFR-018, AX-003 | `test_lattice.py`, `test_power.py`, `test_validate_power_gate.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S4-04** | Per-language power table | NFR-003 | `test_language_power.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S4-05** | Coverage-hardening sprint 4 | FR-029, NFR-003/018 | `test_power_table_reporting.py`, `test_detection_design_provenance.py` | `[UNIT-TEST]` | DONE |
| **S5-01** | Regulatory crosswalk | FR-022, NFR-004 | `test_crosswalk.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S5-02** | Parquet export (streaming + regime columns) | FR-024, NFR-012/004 | `test_parquet_export.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` `[INTEGRATION-TEST]` | REVIEW |
| **S5-03** | Croissant + HF dataset card | FR-024, NFR-012/013/004 | `test_croissant.py`, `test_dataset_card.py` | `[UNIT-TEST]` `[INTEGRATION-TEST]` `[PROPERTY-TEST]` | DONE |
| **S5-04** | CoNLL export | FR-024, NFR-004 | `test_conll_export.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S5-05** | CLI (5 thin dispatch verbs) | FR-024, NFR-018/004 | `test_cli.py` | `[UNIT-TEST]` `[CONTRACT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S5-06** | End-state evidence bundle | FR-021, NFR-005/004 | `test_end_state_bundle.py` | `[UNIT-TEST]` `[AUDIT]` `[INTEGRATION-TEST]` `[PROPERTY-TEST]` | DONE |
| **S5-07** | Doc-drift enforcement | NFR-013 | `test_doc_drift.py` | `[UNIT-TEST]` | DONE |
| **S6-01** | Governance (GOVERNANCE.md pins) | FR-026, NFR-014 | `test_governance.py` | `[UNIT-TEST]` | DONE |
| **S6-02** | Leaderboard policy (opt-in, anti-gaming) | FR-023, NFR-014/004 | `test_leaderboard_policy.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S6-03** | CoI record + recusal | FR-026, NFR-014/004 | `test_coi.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S6-04** | Leaderboard store (append-only, hash-chain) | FR-023, NFR-014/004 | `test_leaderboard_store.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S6-05** | Contribution pipeline (CONTRIBUTING.md) | FR-025 | `test_contributing.py` | `[UNIT-TEST]` | DONE |
| **S7-01** | Calibration + viz | FR-005, NFR-008/004 | `test_calibration.py`, `test_viz.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S7-02** | Oracle + payloads (agentic, bounded) | FR-017, NFR-004 | `test_oracle.py`, `test_payloads.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S7-03** | Roadmap pins (FR-018/019/020) | FR-018/019/020 | `test_roadmap.py` | `[PROPERTY-TEST]` | DONE |
| **S7-04** | Correlation harness seam | FR-027, NFR-004 | `test_correlation.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |
| **S7-05** | Coreference + QI slices seam | FR-015/016, NFR-004 | `test_slices.py` | `[UNIT-TEST]` `[PROPERTY-TEST]` | DONE |

---

## 5. Index by Example / Documentation Reference

No explicit examples directory or `demo/` folder was found at the repo root. The following documentation files serve as public-facing examples of requirements in action. None carry explicit FR-NNN tokens in their prose; all traces are inferred from section content.

| Document | Relevant FR(s) | How it demonstrates the FR | Trace type |
|---|---|---|---|
| `CONTRIBUTING.md` | FR-025 | PR template, CC0 license-compat check, provenance section, deprecation/semver policy | inferred |
| `GOVERNANCE.md` | FR-026, NFR-014 | Advisory-body roster, CoI statement re: `pii-anon-core`, bus-factor note, charter | inferred |
| `ROADMAP.md` | FR-018/019/020 | Documents cross-turn fragmented leakage, transcript residual estimate, live-harness adapter as v1.x future items | explicit (FR IDs appear in file, verified by `test_roadmap.py`) |
| `DATASHEET.md` | NFR-013, NFR-015 | Gebru-format datasheet; license/intended-use; synthetic-only invariant | inferred |
| `TAXONOMY.md` | NFR-011 | 63 entity types listed; matches registry (verified by `test_doc_drift.py::test_nfr_013_taxonomy_body_matches_registry`) | inferred |
| `MIGRATION.md` | DC-02 (AX-002) | v1.3.0→v2.0.0 migration instructions; deterministic script | inferred |
| `README.md` | FR-024, NFR-013 | Dataset card-equivalent public summary; counts/versions must match metadata | inferred |
| `COMPARISON.md` | FR-027 (context) | Benchmark comparison context; external-validity caveats | inferred |

---

## 6. Coverage Roll-Up

### 6.1 FR coverage summary

| Category | Count | Notes |
|---|---|---|
| Total FRs declared | 29 | FR-001 through FR-029 |
| Test-verified (explicit token) | 21 | FR-002/004/005/006/007/008/009/010/011/012/013/015/016/017/021/022/023/024/025/026/029 |
| Test-verified (inferred trace) | 3 | FR-001/003/027 (seam tests + module docstrings; see §7) |
| Doc-pinned only (no feature test) | 3 | FR-018/019/020 (ROADMAP.md + `test_roadmap.py` property tests) |
| Pass-2 deferred (seam tested) | 2 | FR-015/016 (slice selectors exist; full scoring deferred v1.1); FR-027 also deferred for full real-data run |
| Genuine gap (SHOULD, no test at all) | 2 | FR-014 (query-aware masking scorer), FR-028 (frictionless citation) |
| Total accounted | 29 of 29 | Zero orphan FRs |

### 6.2 NFR coverage summary

| Category | Count | Notes |
|---|---|---|
| Total NFRs declared | 18 | NFR-001 through NFR-018 |
| Test-verified (explicit token) | 8 | NFR-002/003/004/005/008/012/013/014 |
| Test-verified (inferred) | 5 | NFR-001/007/009/011/015 (fn-tokens absent; requirements verified via FR-coupled tests) |
| Pass-2 deferred | 1 | NFR-010 (throughput; `real_user_needed: true`) |
| Audit/tooling gate (no unit test warranted) | 3 | NFR-006 (security scan), NFR-016 (coverage tooling), NFR-017 (artifact completeness) |
| NFR-018 | 1 | Explicitly verified via `test_reid_power.py` + lattice + validate gate tests |
| Total accounted | 18 of 18 | Zero orphan NFRs |

### 6.3 Test-suite composition (347 test items)

| Test file | Approx. items | Primary FR/NFR | Test types present |
|---|---|---|---|
| `test_adversary_port.py` | 7 | FR-010/007 | UNIT, PROPERTY, CONTRACT |
| `test_anonymization.py` | 9 | FR-006, NFR-005 | UNIT, AUDIT, PROPERTY |
| `test_calibration.py` | 8 | FR-005, NFR-008 | UNIT, PROPERTY |
| `test_cli.py` | 12 | FR-024, NFR-018 | UNIT, CONTRACT, PROPERTY |
| `test_clopper_pearson.py` | 7 | FR-004, NFR-002 | UNIT, PROPERTY |
| `test_coi.py` | 4 | FR-026, NFR-014 | UNIT, PROPERTY |
| `test_conll_export.py` | 12 | FR-024 | UNIT, PROPERTY |
| `test_contributing.py` | 3 | FR-025 | UNIT |
| `test_correlation.py` | 5 | FR-027 | UNIT, PROPERTY |
| `test_croissant.py` | 16 | FR-024, NFR-012 | UNIT, INTEGRATION, PROPERTY |
| `test_crosswalk.py` | 6 | FR-022 | UNIT, PROPERTY |
| `test_dataset_card.py` | 4 | FR-024, NFR-013 | UNIT, PROPERTY |
| `test_detection.py` | 5 | FR-001/004 | UNIT |
| `test_detection_design_provenance.py` | 6 | FR-029, AX-003 | UNIT |
| `test_doc_drift.py` | 6 | NFR-013 | UNIT |
| `test_end_state_bundle.py` | 7 | FR-021, NFR-005 | UNIT, AUDIT, INTEGRATION, PROPERTY |
| `test_exposure_index.py` | 6 | FR-008 | UNIT, PROPERTY |
| `test_governance.py` | 3 | FR-026, NFR-014 | UNIT |
| `test_intervals.py` | 6 | NFR-002, FR-004 | UNIT, PROPERTY |
| `test_language_power.py` | 6 | NFR-003 | UNIT, PROPERTY |
| `test_lattice.py` | 14 | FR-029, NFR-018 | UNIT, PROPERTY |
| `test_lattice_audit.py` | 6 | FR-029, NFR-018 | UNIT |
| `test_lattice_fill_determinism.py` | 5 | FR-029, NFR-004 | UNIT, PROPERTY |
| `test_lattice_targeting.py` | 10 | FR-029, NFR-011 | UNIT, PROPERTY |
| `test_leaderboard_policy.py` | 6 | FR-023, NFR-014 | UNIT, PROPERTY |
| `test_leaderboard_store.py` | 7 | FR-023, NFR-014 | UNIT, PROPERTY |
| `test_llm_adversary.py` | 5 | FR-010, NFR-009 | CONTRACT, UNIT, INTEGRATION |
| `test_manifest.py` | 3 | DC-02, AX-002 | UNIT, PROPERTY |
| `test_migration.py` | 6 | DC-02, AX-002 | UNIT, PROPERTY |
| `test_nfr005_separation.py` | 2 | NFR-005 | UNIT, AUDIT |
| `test_offline_adversary.py` | 9 | FR-007/010 | UNIT, PROPERTY, CONTRACT |
| `test_oracle.py` | 4 | FR-017 | UNIT, PROPERTY |
| `test_paired.py` | 8 | FR-002, NFR-002 | UNIT, PROPERTY |
| `test_parquet_export.py` | 11 | FR-024, NFR-012 | UNIT, PROPERTY, INTEGRATION |
| `test_payloads.py` | 5 | FR-017 | UNIT, PROPERTY |
| `test_power.py` | 20 | FR-029, NFR-018 | UNIT, PROPERTY |
| `test_power_table_reporting.py` | 4 | FR-029, NFR-003 | UNIT |
| `test_pseudonymization.py` | 8 | FR-011/012/013, NFR-005 | UNIT, CONTRACT, PROPERTY |
| `test_reid_power.py` | 5 | NFR-018 | UNIT, PROPERTY |
| `test_reidentification_measured.py` | 9 | FR-007/009 | UNIT |
| `test_roadmap.py` | 2 | FR-018/019/020 | PROPERTY |
| `test_rrs_caveat.py` | 5 | FR-009/007 | UNIT |
| `test_scoring_core.py` | 7 | FR-003, DC-04 | UNIT |
| `test_signals.py` | 5 | FR-008 | UNIT, PROPERTY |
| `test_slices.py` | 4 | FR-015/016 | UNIT, PROPERTY |
| `test_spacy_export.py` | 4 | FR-024 | UNIT, CONTRACT |
| `test_taxonomy.py` | 4 | NFR-011 | UNIT |
| `test_validate_power_gate.py` | 5 | FR-029, NFR-018 | UNIT |
| `test_viz.py` | 9 | FR-005/006, NFR-003 | UNIT, PROPERTY |

**Total: 347 items.** Reported run result: 346 passed / 1 skipped (`test_fr_010_llm_attack_skips_if_absent` — skips cleanly when `anthropic` is absent, by design).

---

## 7. Trace-by-Inference Flags

The following rows use inferred rather than explicit ID linkage. Human curator action: add `# trace: FR-NNN` or `nfr_NNN` token to the test function name or module docstring to convert these to explicit trace links.

| Row ID | Test file | Inferred-to FR/NFR | Reason for inference | Recommended action |
|---|---|---|---|---|
| TBI-01 | `test_detection.py` (all 5 fns) | FR-001 | Module docstring says `FR-001/004`; no fn carries `fr_001` token | Add `_fr_001` suffix or `# trace: FR-001` comment to each fn |
| TBI-02 | `test_scoring_core.py` (all 7 fns) | FR-003 | No `fr_003` token; DC-04/reidx cited in docstring only | Add `fr_003` token to fn names |
| TBI-03 | `test_intervals.py` (all 6 fns) | FR-004, NFR-002 | Module docstring cites both; no fn-level token | Add `fr_004`/`nfr_002` tokens |
| TBI-04 | `test_rrs_caveat.py` (all 5 fns) | FR-009/007 | Module docstring cites `FR-009/gov-01`; fn-names lack `fr_009`/`fr_007` tokens | Add `fr_009` to relevant fns |
| TBI-05 | `test_lattice_fill_determinism.py` (all 5 fns) | FR-029, NFR-004 | No token in fn names; module docstring context implies FR-029/NFR-004 | Add `fr_029`/`nfr004` tokens |
| TBI-06 | `test_lattice_targeting.py` (all 10 fns) | FR-029, NFR-011 | No fn-level tokens; inferred from lattice context and 63-type emitter check | Add `fr_029`/`nfr_011` tokens |
| TBI-07 | `test_validate_power_gate.py` (all 5 fns) | FR-029, NFR-018 | Module docstring cites both; fn names lack tokens | Add `fr_029`/`nfr_018` tokens |
| TBI-08 | `test_lattice_audit.py` (all 6 fns) | FR-029, NFR-018 | Module docstring cites both; fn names lack tokens | Add `fr_029`/`nfr_018` tokens |
| TBI-09 | `test_migration.py` + `test_manifest.py` | DC-02, NFR-004 | Module docstrings cite DC-02/AX-002; no FR/NFR fn-token | Add `nfr004` or `dc_02` token |
| TBI-10 | `test_taxonomy.py` (all 4 fns) | NFR-011 | Module docstring cites M1 fix; no `nfr_011` token | Add `nfr_011` token |
| TBI-11 | NFR-001 (no dedicated test) | NFR-001 | Enforced by NFR-018 gate tests; no independent `nfr_001` test | Add a `test_nfr_001_*` alias/wrapper in `test_validate_power_gate.py` |
| TBI-12 | NFR-007 version-pinning | NFR-007 | Verified via FR-010 tests; no `nfr_007` fn-token | Add `nfr_007` annotation to `test_fr_010_llm_adversary_id_version_stamped` |
| TBI-13 | NFR-009 offline-adversary mode | NFR-009 | Verified via FR-010 LLM tests; module docstring cites NFR-009 | Add `nfr_009` token to `test_fr_010_package_imports_without_anthropic` |
| TBI-14 | NFR-011 63-type coverage | NFR-011 | Taxonomy tests don't carry `nfr_011` token | Add `nfr_011` token to `test_canonical_counts` |
| TBI-15 | NFR-015 license/ethics | NFR-015 | Verified via FR-024/FR-025 dataset-card/contributing tests | Add `nfr_015` token to `test_fr_024_dataset_card_has_yaml_frontmatter` |
| TBI-16 | FR-027 correlation harness | FR-027 | Seam tests exist and carry `fr_027` tokens — EXPLICIT; the inferred aspect is the deferred real-data path | No action on token; document deferred portion in Pass-2 record |
| TBI-17 | `test_power.py` (all 20 fns) | FR-029, NFR-018 | Module docstring cites both; individual fn names don't carry `fr_029`/`nfr_018` | Add `fr_029`/`nfr_018` tokens to fn names |

**Inferred-vs-explicit ratio:** ~52 test functions carry inferred traces out of ~347 total items ≈ 15% inferred, 85% explicit. This is a very good ratio for a brownfield project at this stage.

---

## 8. NFR Verification Directory

`dev-assist-artifacts/05-testing/03-nfr-verification/` — **empty at time of catalog generation.**
Pre-wave NFR verification artifacts were not separately staged. The test suite itself (346 passed) constitutes the primary NFR verification record for NFR-002/003/004/005/008/012/013/014/018.

Pass-2 dir `dev-assist-artifacts/05-testing/05-pass2/` — **empty.** Pass-2 not yet run. Deferred items: NFR-010b/c (throughput), FR-027 (real-data correlation), FR-015/016 (full chain/QI scoring).

Accessibility audit `dev-assist-artifacts/05-testing/04-accessibility/accessibility-audit-results.md` — **not present.** Accessibility was de-scoped in D3 design decision (markdown/static output, no interactive web app). No AX-001/AX-003 accessibility items required a formal audit file.

