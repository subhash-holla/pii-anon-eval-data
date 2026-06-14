#!/usr/bin/env python3
"""Stanza NER PII detection adapter (English OntoNotes NER by default).

Like spaCy, a general OntoNotes NER model: strong on names / orgs / locations, coarse elsewhere. The same
honesty policy applies — coarse labels (``DATE`` / ``NORP`` / …) are DROPPED rather than mislabeled, so
coverage is low-but-true. The pipeline loads LAZILY in ``build()``; the English models are downloaded on
first use.
"""

from __future__ import annotations

import importlib.util

from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

# Stanza OntoNotes NER label -> canonical-63 type, or None to DROP.
LABEL_MAP: dict[str, str | None] = {
    "PERSON": "PERSON_NAME",
    "ORG": "ORGANIZATION_NAME",
    "GPE": "LOCATION_NAME",
    "LOC": "LOCATION_NAME",
    "FAC": "LOCATION_NAME",
    "NORP": None,
    "DATE": None,
    "TIME": None,
    "MONEY": None,
    "PERCENT": None,
    "QUANTITY": None,
    "ORDINAL": None,
    "CARDINAL": None,
    "PRODUCT": None,
    "EVENT": None,
    "WORK_OF_ART": None,
    "LAW": None,
    "LANGUAGE": None,
}


class _StanzaAdapter:
    name = "stanza"
    model_id = "stanza-en-ontonotes"
    label_map = LABEL_MAP
    deterministic = True

    def available(self) -> bool:
        return importlib.util.find_spec("stanza") is not None

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get((native or "").strip().upper())

    def build(self) -> object:
        try:
            import stanza
        except ImportError as e:  # pragma: no cover - exercised only on a lib-less checkout
            raise RuntimeError('stanza not installed — pip install -e ".[engines]"') from e
        return stanza.Pipeline(lang="en", processors="tokenize,ner", verbose=False)

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        if not text:
            return []
        out: list[AdapterSpan] = []
        for ent in model(text).entities:
            et = self.map_label(str(ent.type))
            if et is not None:
                out.append(AdapterSpan(int(ent.start_char), int(ent.end_char), et, ent.text))
        return out

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _StanzaAdapter()
