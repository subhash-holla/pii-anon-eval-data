"""Cloud-DLP cost estimate — the budget guardrail for the multilingual cloud baseline run.

Encodes the verified-June-2026 list pricing from ``CLOUD_DLP_COST.md`` with the same conservative **×2
safety ceiling** (retries, request overhead, the per-request minimums, and price drift). The per-document
minimums are the decisive part — PII-Anon docs average ~295 chars, so each is billed as a *whole* AWS
3-unit floor and a *whole* Azure 1,000-char text record; a naive total-chars/unit calc understates cost.

Pure arithmetic (NFR-004) — takes per-document character lengths, returns USD. No data load, no network.
Verify pricing again at run time (per-region rates and tiers change).
"""

from __future__ import annotations

import math
from collections.abc import Sequence

_SAFETY = 2.0

# AWS Comprehend DetectPiiEntities: $0.0001 / unit, 1 unit = 100 chars, 3-unit (300-char) minimum/request.
_AWS_USD_PER_UNIT = 0.0001
_AWS_CHARS_PER_UNIT = 100
_AWS_MIN_UNITS = 3

# Azure AI Language PII: $1.00 / 1,000 text records (0–500K tier); 1 record = 1,000 chars, rounded/document.
_AZURE_USD_PER_RECORD = 1.00 / 1000
_AZURE_CHARS_PER_RECORD = 1000

# GCP Sensitive Data Protection content.inspect: $3.00 / GB inspected, with the first 1 GB/month free.
_GCP_USD_PER_GB = 3.00
_GCP_FREE_GB = 1.0


def estimate_usd(provider: str, doc_char_lengths: Sequence[int], safety: float = _SAFETY) -> float:
    """Estimated USD to run ``provider`` over documents of the given character lengths (×``safety``).

    ``provider`` is one of ``aws`` / ``azure`` / ``gcp``; any other returns 0.0 (nothing billable).
    """
    if provider == "aws":
        units = sum(max(_AWS_MIN_UNITS, math.ceil(c / _AWS_CHARS_PER_UNIT)) for c in doc_char_lengths)
        gross = units * _AWS_USD_PER_UNIT
    elif provider == "azure":
        records = sum(max(1, math.ceil(c / _AZURE_CHARS_PER_RECORD)) for c in doc_char_lengths)
        gross = records * _AZURE_USD_PER_RECORD
    elif provider == "gcp":
        gb = sum(doc_char_lengths) / 1e9  # ~1 byte/char; conservative for Latin, low for multibyte scripts
        gross = max(0.0, gb - _GCP_FREE_GB) * _GCP_USD_PER_GB
    else:
        return 0.0
    return gross * safety
