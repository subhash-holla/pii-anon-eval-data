#!/usr/bin/env python3
"""Piiranha (token-classification NER) PII detection adapter.

Wraps ``iiiorg/piiranha-v1-detect-personal-information`` via a HuggingFace ``transformers`` pipeline behind
the uniform detector contract. The native→63-type label map MIRRORS the audited pii-rate-elo
``detectors/piiranha_adapter.py`` map (re-implemented — eval-data never imports the sister repo). BIO
prefixes (``B-`` / ``I-``) are tolerated. The pipeline loads LAZILY in ``build()`` (NFR-050).
"""

from __future__ import annotations

import importlib.util

from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

_MODEL = "iiiorg/piiranha-v1-detect-personal-information"

# Native Piiranha label (BIO prefix stripped) -> canonical-63 type, or None to drop. Mirrors the audited
# sister-repo map verbatim.
LABEL_MAP: dict[str, str | None] = {
    "GIVENNAME": "PERSON_NAME",
    "SURNAME": "PERSON_NAME",
    "MIDDLENAME": "PERSON_NAME",
    "TITLE": None,  # honorific — not a taxonomy span
    "EMAIL": "EMAIL_ADDRESS",
    "TELEPHONENUM": "PHONE_NUMBER",
    "SOCIALNUM": "SOCIAL_SECURITY_NUMBER",
    "IDCARDNUM": "NATIONAL_ID_NUMBER",
    "DRIVERLICENSENUM": "DRIVER_LICENSE_NUMBER",
    "PASSPORTNUM": "PASSPORT_NUMBER",
    "TAXNUM": "TAX_ID",
    "ACCOUNTNUM": "BANK_ACCOUNT_NUMBER",
    "CREDITCARDNUMBER": "CREDIT_CARD_NUMBER",
    "BUILDINGNUM": "STREET_ADDRESS",
    "STREET": "STREET_ADDRESS",
    "CITY": "LOCATION_NAME",
    "ZIPCODE": "POSTAL_CODE",
    "DATEOFBIRTH": "DATE_OF_BIRTH",
    "USERNAME": "USERNAME",
    "PASSWORD": "PASSWORD",
}


class _PiiranhaAdapter:
    name = "piiranha"
    model_id = _MODEL
    label_map = LABEL_MAP
    deterministic = True

    def available(self) -> bool:
        return importlib.util.find_spec("transformers") is not None

    def map_label(self, native: str) -> str | None:
        lbl = (native or "").strip().upper()
        if lbl.startswith(("B-", "I-")):
            lbl = lbl[2:]
        return LABEL_MAP.get(lbl)

    def build(self) -> object:
        try:
            from transformers import pipeline
        except ImportError as e:  # pragma: no cover - exercised only on a lib-less checkout
            raise RuntimeError('transformers not installed — pip install -e ".[engines]"') from e
        return pipeline("token-classification", model=_MODEL, aggregation_strategy="simple")

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        if not text:
            return []
        out: list[AdapterSpan] = []
        for pred in model(text):
            raw = str(pred.get("entity_group") or pred.get("entity") or pred.get("label") or "")
            et = self.map_label(raw)
            if et is not None:
                start, end = int(pred["start"]), int(pred["end"])
                out.append(AdapterSpan(start, end, et, text[start:end]))
        return out

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _PiiranhaAdapter()
