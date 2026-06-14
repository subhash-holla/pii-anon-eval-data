#!/usr/bin/env python3
"""Google Cloud DLP ``inspect_content`` adapter (cloud — BUILT BEHIND KEYS, NOT RUN by default).

``available()`` is True only when ``google-cloud-dlp`` imports AND a GCP project + credentials are present.
The client loads lazily in ``build()``; offsets are read from the finding's CODEPOINT range (Python str
indices). Marked NON-DETERMINISTIC (server-side model versions). Budget-gated behind ``--cloud``.
"""

from __future__ import annotations

import importlib.util
import os
import time

from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

_PROJECT = os.environ.get("GCP_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT", "")

# GCP DLP infoType -> canonical-63 type, or None to drop. The inspect request requests these infoTypes.
LABEL_MAP: dict[str, str | None] = {
    "PERSON_NAME": "PERSON_NAME",
    "EMAIL_ADDRESS": "EMAIL_ADDRESS",
    "PHONE_NUMBER": "PHONE_NUMBER",
    "STREET_ADDRESS": "STREET_ADDRESS",
    "US_SOCIAL_SECURITY_NUMBER": "SOCIAL_SECURITY_NUMBER",
    "CREDIT_CARD_NUMBER": "CREDIT_CARD_NUMBER",
    "IBAN_CODE": "IBAN",
    "SWIFT_CODE": "SWIFT_BIC_CODE",
    "IP_ADDRESS": "IP_ADDRESS",
    "MAC_ADDRESS": "MAC_ADDRESS",
    "URL": "URL",
    "DATE_OF_BIRTH": "DATE_OF_BIRTH",
    "PASSPORT": "PASSPORT_NUMBER",
    "US_DRIVERS_LICENSE_NUMBER": "DRIVER_LICENSE_NUMBER",
    "US_BANK_ROUTING_MICR": "BANK_ROUTING_NUMBER",
    "US_INDIVIDUAL_TAXPAYER_IDENTIFICATION_NUMBER": "TAX_ID",
    "ORGANIZATION_NAME": "ORGANIZATION_NAME",
    "LOCATION": "LOCATION_NAME",
}
_INFO_TYPES = sorted({k for k in LABEL_MAP})


def _is_rate_limit(exc: Exception) -> bool:
    """True for a GCP DLP per-minute-quota rejection (HTTP 429 / gRPC RESOURCE_EXHAUSTED). Matched by class
    name + status WITHOUT importing ``google.api_core`` — the lazy-import guard (NFR-050) forbids pulling the
    cloud lib at module import, and google's exception class is named exactly ``ResourceExhausted``."""
    return (
        type(exc).__name__ == "ResourceExhausted"
        or getattr(exc, "code", None) == 429
        or getattr(exc, "grpc_status_code", None) == 8
    )


class _GcpDlpAdapter:
    name = "gcp"
    model_id = "gcp-dlp-inspect-content"
    label_map = LABEL_MAP
    deterministic = False
    max_retries = 6          # transient-429 retries before surfacing a real record-error
    backoff_base_s = 0.5     # exponential backoff seconds: 0.5, 1, 2, 4, … (tests set 0 to skip the sleep)

    def available(self) -> bool:
        try:  # find_spec on a dotted name imports the parent; absent google.cloud raises
            has_lib = importlib.util.find_spec("google.cloud.dlp_v2") is not None
        except Exception:  # noqa: BLE001
            has_lib = False
        has_creds = bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") and _PROJECT)
        return has_lib and has_creds

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get((native or "").strip().upper())

    def build(self) -> object:
        try:
            from google.cloud import dlp_v2
        except ImportError as e:  # pragma: no cover - cloud extra not installed
            raise RuntimeError('google-cloud-dlp not installed — pip install -e ".[cloud]"') from e
        return dlp_v2.DlpServiceClient()

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        if not text:
            return []
        parent = f"projects/{_PROJECT}"
        config = {"info_types": [{"name": t} for t in _INFO_TYPES], "include_quote": False}
        resp = self._inspect_with_retry(model, parent, config, text)
        out: list[AdapterSpan] = []
        for finding in resp.result.findings:
            et = self.map_label(str(finding.info_type.name))
            if et is None:
                continue
            rng = finding.location.codepoint_range
            start, end = int(rng.start), int(rng.end)
            out.append(AdapterSpan(start, end, et, text[start:end]))
        return out

    def _inspect_with_retry(self, model: object, parent: str, config: dict, text: str) -> object:
        """Call ``inspect_content``, retrying transient 429 throttling with exponential backoff. DLP enforces
        a per-minute request quota; a sustained full-corpus run exceeds it, and an unretried 429 would force
        the record's gold spans to false-negatives (silently deflating recall). Non-throttle errors propagate
        immediately. The backoff also self-throttles the loop toward the quota's refill rate."""
        request = {"parent": parent, "inspect_config": config, "item": {"value": text}}
        attempt = 0
        while True:
            try:
                return model.inspect_content(request=request)
            except Exception as exc:  # noqa: BLE001 - re-raised below unless it's a retryable 429
                if not _is_rate_limit(exc) or attempt >= self.max_retries:
                    raise
                time.sleep(self.backoff_base_s * (2 ** attempt))
                attempt += 1

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _GcpDlpAdapter()
