"""spaCy NER-training exporter (FR-024 / NFR-004) — char-offset tuples + a serialized DocBin (lazy).

Emits the corpus in the two spaCy training shapes. Two load-bearing contracts:

1. **Pure-stdlib offsets.** :func:`to_spacy_offsets` returns the classic spaCy training tuple
   ``(text, {"entities": [(start, end, entity_type), …]})`` with the entities sorted by
   ``(start, end)`` — a pure function of the record's char-offset ``annotations`` needing NO spaCy.
2. **Lazy DocBin (NFR-004 / [baselines] extra).** :func:`export_spacy_docbin` STREAMS records to a
   serialized :class:`spacy.tokens.DocBin`, importing ``spacy`` ONLY inside :func:`_require_spacy`
   (never at module top) so ``import pii_anon_datasets.distribution.spacy_export`` works on a box
   without spaCy. Per record it builds spans via ``doc.char_span(..., alignment_mode="contract")``,
   SKIPS token-misaligned spans (``char_span`` returns ``None``), and drops overlaps via
   ``spacy.util.filter_spans`` (a ``DocBin`` cannot hold overlapping ``ents``) before
   ``doc.ents = filtered`` — so misaligned/overlapping annotations are filtered, not crashing.

Deterministic (no clock/RNG; stable sorted offsets; one reused ``spacy.blank`` pipeline) — the same
records always serialize the same DocBin (AX-002). Writes a LOCAL file only — no network egress, no
HF upload (AX-001).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def to_spacy_offsets(record: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    """Pure-stdlib spaCy training format: ``(text, {"entities": [(start, end, entity_type), …]})``,
    entities sorted by ``(start, end)``. Needs no spaCy.

    Reads ``record["text"]`` and each ``record["annotations"]`` span's ``start``/``end``/
    ``entity_type``; the entity tuples are sorted (stable, deterministic) so the emitted training
    payload never depends on annotation ordering (AX-002).
    """
    text = str(record.get("text", ""))
    ents = sorted(
        ((int(a["start"]), int(a["end"]), str(a["entity_type"])) for a in record.get("annotations", [])),
        key=lambda t: (t[0], t[1]),
    )
    return text, {"entities": ents}


def _require_spacy() -> Any:
    """Lazily import spaCy, or raise a clear install error (NFR-004 / [baselines] extra).

    Imported here (not at module top) so ``import pii_anon_datasets.distribution.spacy_export`` works
    without spaCy. If the extra is missing, the ``RuntimeError`` names the exact install command.
    """
    try:
        # spaCy 3.8.x ships a py.typed marker, so mypy --strict resolves this import cleanly (no
        # import-untyped suppression needed, unlike parquet_export's unstubbed pyarrow). Kept lazy
        # (inside this guard, never at module top) so the module imports without the [baselines] extra.
        import spacy
    except ImportError as e:
        raise RuntimeError("spaCy export needs the 'baselines' extra: pip install pii-anon-datasets[baselines]") from e
    return spacy


def export_spacy_docbin(
    records: Iterable[Mapping[str, Any]],
    out_path: str,
    *,
    blank_lang: str = "xx",
) -> str:
    """Stream ``records`` to a serialized spaCy ``DocBin`` at ``out_path``; return ``out_path``.

    Lazy spaCy (load-bearing): the import happens inside :func:`_require_spacy`. Reuses ONE blank
    pipeline (``nlp = spacy.blank(blank_lang)``); per record builds ``doc = nlp.make_doc(text)`` and,
    for each ``(start, end, label)`` from :func:`to_spacy_offsets`, ``doc.char_span(..., label=label,
    alignment_mode="contract")`` — SKIPPING ``None`` (token-misaligned) spans. Overlaps are dropped
    via ``spacy.util.filter_spans`` (a ``DocBin`` cannot hold overlapping ``ents``) before
    ``doc.ents = filtered``; ``db.add(doc)``; finally ``db.to_disk(out_path)``.

    Streaming (load-bearing): ``records`` is consumed as a ONE-PASS iterator — never ``list()``-ed /
    ``len()``-ed / indexed. Deterministic (AX-002); writes a LOCAL file only (AX-001).

    Raises:
        RuntimeError: if the ``[baselines]`` extra (spaCy) is not installed — message names the
            install command.
    """
    spacy = _require_spacy()
    from spacy.tokens import DocBin

    nlp = spacy.blank(blank_lang)
    db = DocBin()
    for record in records:  # one-pass iteration — no list()/len()/indexing (streaming)
        text, payload = to_spacy_offsets(record)
        doc = nlp.make_doc(text)
        spans = []
        for start, end, label in payload["entities"]:
            # alignment_mode="contract": shrink to token boundaries; None when no token aligns -> skip.
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is not None:
                spans.append(span)
        # filter_spans drops overlaps (keeping the longest) — a DocBin forbids overlapping ents.
        doc.ents = spacy.util.filter_spans(spans)
        db.add(doc)
    db.to_disk(out_path)
    return out_path
