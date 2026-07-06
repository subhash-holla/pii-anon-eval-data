#!/usr/bin/env python3
"""Azure AI Language PII (``recognize_pii_entities``) adapter (cloud — BUILT BEHIND KEYS, NOT RUN default).

``available()`` is True only when ``azure-ai-textanalytics`` imports AND an Azure Language key + endpoint
are present. The client loads lazily in ``build()``; offsets are requested as ``UnicodeCodePoint`` so they
are Python ``str`` indices. Marked NON-DETERMINISTIC (server-side model versions). Budget-gated behind
``--cloud`` — and Azure is the cost-dominant provider, so cost the run before enabling it.
"""

from __future__ import annotations

import importlib.util
import os

from pii_anon_datasets.baselines import cloud_languages
from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

_ENDPOINT = os.environ.get("AZURE_LANGUAGE_ENDPOINT", "")
_KEY = os.environ.get("AZURE_LANGUAGE_KEY", "")

# Azure AI Language PII category -> canonical-63 type, or None to drop.
LABEL_MAP: dict[str, str | None] = {
    "PERSON": "PERSON_NAME",
    "EMAIL": "EMAIL_ADDRESS",
    "PHONENUMBER": "PHONE_NUMBER",
    "ADDRESS": "STREET_ADDRESS",
    "USSOCIALSECURITYNUMBER": "SOCIAL_SECURITY_NUMBER",
    "CREDITCARDNUMBER": "CREDIT_CARD_NUMBER",
    "INTERNATIONALBANKINGACCOUNTNUMBER": "IBAN",
    "SWIFTCODE": "SWIFT_BIC_CODE",
    "IPADDRESS": "IP_ADDRESS",
    "URL": "URL",
    "DATETIME": "DATE_OF_BIRTH",
    "DATE": "DATE_OF_BIRTH",
    "ORGANIZATION": "ORGANIZATION_NAME",
    "USDRIVERSLICENSENUMBER": "DRIVER_LICENSE_NUMBER",
    "USPASSPORTNUMBER": "PASSPORT_NUMBER",
    "USBANKACCOUNTNUMBER": "BANK_ACCOUNT_NUMBER",
    "USINDIVIDUALTAXPAYERIDENTIFICATION": "TAX_ID",
    "AGE": "AGE",
}


class _AzureAdapter:
    name = "azure"
    model_id = "azure-ai-language-pii"
    label_map = LABEL_MAP
    deterministic = False
    # The dataset language code for the current run (the orchestrator sets this per shard before build());
    # ``detect`` maps it to Azure's locale string (e.g. 'pt' -> 'pt-PT', 'zh' -> 'zh-hans').
    language = "en"

    def supports_language(self, language: str) -> bool:
        return cloud_languages.is_supported(self.name, language)

    def available(self) -> bool:
        try:  # find_spec on a dotted name imports the parent; absent azure raises
            has_lib = importlib.util.find_spec("azure.ai.textanalytics") is not None
        except Exception:  # noqa: BLE001
            has_lib = False
        return has_lib and bool(_ENDPOINT and _KEY)

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get((native or "").strip().upper().replace(" ", "").replace("_", ""))

    def build(self) -> object:
        try:
            from azure.ai.textanalytics import TextAnalyticsClient
            from azure.core.credentials import AzureKeyCredential
        except ImportError as e:  # pragma: no cover - cloud extra not installed
            raise RuntimeError('azure-ai-textanalytics not installed — pip install -e ".[cloud]"') from e
        return TextAnalyticsClient(endpoint=_ENDPOINT, credential=AzureKeyCredential(_KEY))

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        if not text:
            return []
        response = model.recognize_pii_entities(
            [text], language=cloud_languages.api_code(self.name, self.language), string_index_type="UnicodeCodePoint"
        )
        out: list[AdapterSpan] = []
        for doc in response:
            if getattr(doc, "is_error", False):
                continue
            for ent in doc.entities:
                et = self.map_label(str(ent.category))
                if et is None:
                    continue
                start, end = int(ent.offset), int(ent.offset) + int(ent.length)
                out.append(AdapterSpan(start, end, et, text[start:end]))
        return out

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _AzureAdapter()
