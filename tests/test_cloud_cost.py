"""Cloud-DLP cost estimate — the budget guardrail behind the multilingual cloud run.

Mirrors the verified-June-2026 list pricing in ``CLOUD_DLP_COST.md`` with the same ×2 safety ceiling, and
honours the per-document minimums that make short docs cost more than a naive chars/unit calc (AWS 3-unit
floor; Azure rounds per document to a 1,000-char text record). Pure arithmetic — no data load, no network.
"""

from __future__ import annotations

import math

from pii_anon_datasets.baselines import cloud_cost as cc


def test_aws_applies_the_three_unit_minimum_on_short_docs() -> None:
    # 50 chars -> ceil(0.5)=1 unit, but the 3-unit floor applies -> 3 units * $0.0001 * 2 safety.
    assert cc.estimate_usd("aws", [50]) == 3 * 0.0001 * 2.0


def test_aws_charges_per_hundred_chars_above_the_floor() -> None:
    # 350 chars -> ceil(3.5)=4 units * $0.0001 * 2.
    assert cc.estimate_usd("aws", [350]) == 4 * 0.0001 * 2.0


def test_azure_rounds_per_document_to_a_thousand_char_text_record() -> None:
    # 295 chars (the English-test average) still bills as one whole 1,000-char text record.
    assert cc.estimate_usd("azure", [295]) == 1 * 0.001 * 2.0
    # 1,500 chars -> ceil(1.5)=2 records.
    assert cc.estimate_usd("azure", [1500]) == 2 * 0.001 * 2.0


def test_gcp_is_free_under_the_one_gigabyte_tier() -> None:
    # A few million chars is well under 1 GB -> $0 (GCP DLP's 1 GB/month free tier).
    assert cc.estimate_usd("gcp", [1000] * 5000) == 0.0


def test_gcp_charges_three_dollars_per_gb_over_the_free_gigabyte() -> None:
    two_gb_in_chars = [1_000_000] * 2000  # 2e9 chars ~= 2 GB
    # (2 - 1) GB * $3 * 2 safety = $6.
    assert cc.estimate_usd("gcp", two_gb_in_chars) == pytest_approx(6.0)


def test_unknown_provider_costs_nothing() -> None:
    assert cc.estimate_usd("nope", [100, 200]) == 0.0


def test_total_sums_per_document_minimums_not_the_aggregate() -> None:
    # Two 50-char docs each hit the AWS 3-unit floor -> 6 units, NOT ceil(100/100)=1.
    assert cc.estimate_usd("aws", [50, 50]) == 6 * 0.0001 * 2.0


def pytest_approx(value: float):
    # tiny float tolerance without importing pytest.approx at module top (keeps the asserts readable)
    class _Approx:
        def __eq__(self, other: object) -> bool:
            return isinstance(other, (int, float)) and math.isclose(other, value, rel_tol=1e-9, abs_tol=1e-9)

    return _Approx()
