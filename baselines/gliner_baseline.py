#!/usr/bin/env python3
"""GLiNER zero-shot PII detection adapter.

Wraps ``urchade/gliner_multi_pii-v1`` behind the uniform detector contract. The native→63-type label map
MIRRORS the audited pii-rate-elo ``detectors/gliner_adapter.py`` map (re-implemented here — eval-data must
never import the sister repo: the forbidden edge). The model loads LAZILY in ``build()`` (NFR-050);
``available()`` only probes the import.
"""

from __future__ import annotations

import importlib.util

from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

_MODEL = "urchade/gliner_multi_pii-v1"
_THRESHOLD = 0.5

# Native GLiNER prompt label (lower-cased) -> canonical-63 type, or None to drop. Mirrors the audited
# sister-repo map verbatim (re-implemented, not imported).
LABEL_MAP: dict[str, str | None] = {
    "person": "PERSON_NAME",
    "person name": "PERSON_NAME",
    "full name": "PERSON_NAME",
    "email": "EMAIL_ADDRESS",
    "email address": "EMAIL_ADDRESS",
    "phone number": "PHONE_NUMBER",
    "phone": "PHONE_NUMBER",
    "location": "LOCATION_NAME",
    "city": "LOCATION_NAME",
    "address": "STREET_ADDRESS",
    "street address": "STREET_ADDRESS",
    "postal code": "POSTAL_CODE",
    "zip code": "POSTAL_CODE",
    "organization": "ORGANIZATION_NAME",
    "company": "ORGANIZATION_NAME",
    "ip address": "IP_ADDRESS",
    "mac address": "MAC_ADDRESS",
    "url": "URL",
    "username": "USERNAME",
    "password": "PASSWORD",
    "credit card number": "CREDIT_CARD_NUMBER",
    "credit card": "CREDIT_CARD_NUMBER",
    "social security number": "SOCIAL_SECURITY_NUMBER",
    "passport number": "PASSPORT_NUMBER",
    "driver license": "DRIVER_LICENSE_NUMBER",
    "drivers license": "DRIVER_LICENSE_NUMBER",
    "bank account": "BANK_ACCOUNT_NUMBER",
    "iban": "IBAN",
    "date of birth": "DATE_OF_BIRTH",
    "tax id": "TAX_ID",
    "national id": "NATIONAL_ID_NUMBER",
    "medication": "MEDICATION_NAME",
    "health condition": "HEALTH_CONDITION",
}
PROMPT_LABELS = tuple(LABEL_MAP)


class _GlinerAdapter:
    name = "gliner"
    model_id = _MODEL
    label_map = LABEL_MAP
    deterministic = True

    def available(self) -> bool:
        return importlib.util.find_spec("gliner") is not None

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get((native or "").strip().lower())

    def build(self) -> object:
        try:
            from gliner import GLiNER
        except ImportError as e:  # pragma: no cover - exercised only on a lib-less checkout
            raise RuntimeError('gliner not installed — pip install -e ".[engines]"') from e
        return GLiNER.from_pretrained(_MODEL)

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        if not text:
            return []
        out: list[AdapterSpan] = []
        for pred in model.predict_entities(text, list(PROMPT_LABELS), threshold=_THRESHOLD):
            et = self.map_label(str(pred.get("label", "")))
            if et is not None:
                start, end = int(pred["start"]), int(pred["end"])
                out.append(AdapterSpan(start, end, et, text[start:end]))
        return out

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _GlinerAdapter()
