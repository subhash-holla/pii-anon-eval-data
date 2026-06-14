#!/usr/bin/env python3
"""Flair NER PII detection adapter (the 4-class CoNLL-03 ``ner`` model by default).

Flair's default English NER is CoNLL-03 (PER / LOC / ORG / MISC) — so it covers only names, locations, and
organizations; ``MISC`` is dropped. Low coverage, disclosed. The model loads LAZILY in ``build()`` and is
downloaded on first use.
"""

from __future__ import annotations

import importlib.util

from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

_MODEL = "ner"  # Flair CoNLL-03 4-class English NER

# Flair CoNLL-03 label -> canonical-63 type, or None to drop.
LABEL_MAP: dict[str, str | None] = {
    "PER": "PERSON_NAME",
    "PERSON": "PERSON_NAME",
    "ORG": "ORGANIZATION_NAME",
    "LOC": "LOCATION_NAME",
    "MISC": None,
}


class _FlairAdapter:
    name = "flair"
    model_id = _MODEL
    label_map = LABEL_MAP
    deterministic = True

    def available(self) -> bool:
        return importlib.util.find_spec("flair") is not None

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get((native or "").strip().upper())

    def build(self) -> object:
        try:
            from flair.models import SequenceTagger
        except ImportError as e:  # pragma: no cover - exercised only on a lib-less checkout
            raise RuntimeError('flair not installed — pip install -e ".[engines]"') from e
        return SequenceTagger.load(_MODEL)

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        if not text:
            return []
        from flair.data import Sentence

        sentence = Sentence(text)
        model.predict(sentence)
        out: list[AdapterSpan] = []
        for span in sentence.get_spans("ner"):
            et = self.map_label(str(span.tag))
            if et is not None:
                out.append(AdapterSpan(int(span.start_position), int(span.end_position), et, span.text))
        return out

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _FlairAdapter()
