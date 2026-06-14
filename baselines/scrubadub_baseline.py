#!/usr/bin/env python3
"""scrubadub rule-based PII detection adapter.

A pure-Python, offline rule/regex detector (no model download). Native ``Filth.type`` strings map to the
63-type taxonomy; types scrubadub does not produce are simply absent (low coverage, disclosed). Loads
LAZILY in ``build()`` (constructs a default ``Scrubber``).
"""

from __future__ import annotations

import importlib.util

from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

# scrubadub Filth.type -> canonical-63 type, or None to drop.
LABEL_MAP: dict[str, str | None] = {
    "email": "EMAIL_ADDRESS",
    "phone": "PHONE_NUMBER",
    "url": "URL",
    "credit_card": "CREDIT_CARD_NUMBER",
    "twitter": "SOCIAL_MEDIA_HANDLE",
    "name": "PERSON_NAME",
    "drivers_licence": "DRIVER_LICENSE_NUMBER",
    "national_insurance_number": "NATIONAL_ID_NUMBER",
    "tax_reference_number": "TAX_ID",
    "postalcode": "POSTAL_CODE",
    "vehicle_licence_plate": "LICENSE_PLATE",
    "credential": "PASSWORD",
}


class _ScrubadubAdapter:
    name = "scrubadub"
    model_id = ""
    label_map = LABEL_MAP
    deterministic = True

    def available(self) -> bool:
        return importlib.util.find_spec("scrubadub") is not None

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get((native or "").strip().lower())

    def build(self) -> object:
        try:
            import scrubadub
        except ImportError as e:  # pragma: no cover - exercised only on a lib-less checkout
            raise RuntimeError('scrubadub not installed — pip install -e ".[engines]"') from e
        return scrubadub.Scrubber()

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        if not text:
            return []
        out: list[AdapterSpan] = []
        for filth in model.iter_filth(text):
            ftype = getattr(filth, "type", None)
            if not isinstance(ftype, str):  # MergedFilth (multi-type) carries no single string type
                continue
            et = self.map_label(ftype)
            if et is not None:
                out.append(AdapterSpan(int(filth.beg), int(filth.end), et, text[int(filth.beg):int(filth.end)]))
        return out

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _ScrubadubAdapter()
