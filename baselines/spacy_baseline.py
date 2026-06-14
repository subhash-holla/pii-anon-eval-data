#!/usr/bin/env python3
"""spaCy NER PII detection adapter (``en_core_web_lg`` by default).

A general-purpose NER model: it covers names / organizations / locations well, but its broad OntoNotes
labels do NOT map cleanly onto the corpus's specific PII types. To stay HONEST about precision we DROP the
coarse labels rather than inflate false positives — e.g. spaCy ``DATE`` is any date (not the corpus's
specific ``DATE_OF_BIRTH`` / ``TIMESTAMP``), and ``NORP`` conflates nationality / religion / politics. The
resulting low coverage is the point: it is disclosed, not hidden. Model loads LAZILY in ``build()``.
"""

from __future__ import annotations

import importlib.util

from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

_MODEL = "en_core_web_lg"

# spaCy OntoNotes label -> canonical-63 type, or None to DROP (coarse / not a clean PII mapping).
LABEL_MAP: dict[str, str | None] = {
    "PERSON": "PERSON_NAME",
    "ORG": "ORGANIZATION_NAME",
    "GPE": "LOCATION_NAME",
    "LOC": "LOCATION_NAME",
    "FAC": "LOCATION_NAME",
    "NORP": None,  # nationality/religion/politics conflated — too coarse for one taxonomy type
    "DATE": None,  # generic date != the corpus's specific DATE_OF_BIRTH/TIMESTAMP (would inflate FPs)
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


class _SpacyAdapter:
    name = "spacy"
    model_id = _MODEL
    label_map = LABEL_MAP
    deterministic = True

    def available(self) -> bool:
        return importlib.util.find_spec("spacy") is not None

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get((native or "").strip().upper())

    def build(self) -> object:
        try:
            import spacy
        except ImportError as e:  # pragma: no cover - exercised only on a lib-less checkout
            raise RuntimeError('spacy not installed — pip install -e ".[engines]"') from e
        try:
            return spacy.load(_MODEL, disable=["lemmatizer", "tagger", "parser"])
        except OSError as e:  # model not downloaded
            raise RuntimeError(f"spaCy model {_MODEL!r} missing — python -m spacy download {_MODEL}") from e

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        if not text:
            return []
        out: list[AdapterSpan] = []
        for ent in model(text).ents:
            et = self.map_label(ent.label_)
            if et is not None:
                out.append(AdapterSpan(int(ent.start_char), int(ent.end_char), et, ent.text))
        return out

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _SpacyAdapter()
