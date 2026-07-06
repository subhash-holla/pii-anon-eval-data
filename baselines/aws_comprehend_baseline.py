#!/usr/bin/env python3
"""AWS Comprehend ``DetectPiiEntities`` adapter (cloud — BUILT BEHIND KEYS, NOT RUN by default).

``available()`` is True only when ``boto3`` imports AND AWS credentials are present, so the orchestrator
records it as ``unavailable`` until both are supplied AND ``--cloud`` is passed (budget-gated). The client
loads lazily in ``build()``. Marked NON-DETERMINISTIC: cloud model versions can change server-side, so a
run is INDICATIVE, never byte-reproducible.
"""

from __future__ import annotations

import importlib.util
import os

from pii_anon_datasets.baselines import cloud_languages
from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

_REGION = os.environ.get("AWS_REGION", "us-east-1")

# AWS Comprehend PII entity type -> canonical-63 type, or None to drop. AWS returns character offsets.
LABEL_MAP: dict[str, str | None] = {
    "NAME": "PERSON_NAME",
    "EMAIL": "EMAIL_ADDRESS",
    "PHONE": "PHONE_NUMBER",
    "ADDRESS": "STREET_ADDRESS",
    "SSN": "SOCIAL_SECURITY_NUMBER",
    "CREDIT_DEBIT_NUMBER": "CREDIT_CARD_NUMBER",
    "CREDIT_DEBIT_CVV": "CVV",
    "CREDIT_DEBIT_EXPIRY": None,
    "PIN": "PIN",
    "BANK_ACCOUNT_NUMBER": "BANK_ACCOUNT_NUMBER",
    "BANK_ROUTING": "BANK_ROUTING_NUMBER",
    "INTERNATIONAL_BANK_ACCOUNT_NUMBER": "IBAN",
    "SWIFT_CODE": "SWIFT_BIC_CODE",
    "DATE_TIME": "DATE_OF_BIRTH",
    "IP_ADDRESS": "IP_ADDRESS",
    "MAC_ADDRESS": "MAC_ADDRESS",
    "URL": "URL",
    "AGE": "AGE",
    "USERNAME": "USERNAME",
    "PASSWORD": "PASSWORD",
    "DRIVER_ID": "DRIVER_LICENSE_NUMBER",
    "LICENSE_PLATE": "LICENSE_PLATE",
    "VEHICLE_IDENTIFICATION_NUMBER": "VEHICLE_IDENTIFICATION_NUMBER",
    "PASSPORT_NUMBER": "PASSPORT_NUMBER",
    "AWS_ACCESS_KEY": "API_KEY",
    "AWS_SECRET_KEY": "API_KEY",
}


class _AwsComprehendAdapter:
    name = "aws"
    model_id = "aws-comprehend-detect-pii-entities"
    label_map = LABEL_MAP
    deterministic = False
    # The dataset language code for the current run (the orchestrator sets this per shard before build());
    # ``detect`` maps it to Comprehend's LanguageCode. AWS Comprehend PII is English-only, so in practice
    # this stays "en" — but it is threaded for symmetry + the supports_language guard.
    language = "en"

    def supports_language(self, language: str) -> bool:
        return cloud_languages.is_supported(self.name, language)

    def available(self) -> bool:
        has_lib = importlib.util.find_spec("boto3") is not None
        # boto3's default credential chain also reads the shared ~/.aws/credentials file, not only env vars.
        has_creds = bool(
            os.environ.get("AWS_ACCESS_KEY_ID")
            or os.environ.get("AWS_PROFILE")
            or os.path.exists(os.path.expanduser("~/.aws/credentials"))
        )
        return has_lib and has_creds

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get((native or "").strip().upper())

    def build(self) -> object:
        try:
            import boto3
        except ImportError as e:  # pragma: no cover - cloud extra not installed
            raise RuntimeError('boto3 not installed — pip install -e ".[cloud]"') from e
        return boto3.client("comprehend", region_name=_REGION)

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        if not text:
            return []
        resp = model.detect_pii_entities(Text=text, LanguageCode=cloud_languages.api_code(self.name, self.language))
        out: list[AdapterSpan] = []
        for ent in resp.get("Entities", []):
            et = self.map_label(str(ent.get("Type", "")))
            if et is not None:
                start, end = int(ent["BeginOffset"]), int(ent["EndOffset"])
                out.append(AdapterSpan(start, end, et, text[start:end]))
        return out

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _AwsComprehendAdapter()
