"""Pure CoNLL BIO/BILOU conversion (FR-024 / NFR-004) — ported from the top-level CLI, minus IO.

The proven, deterministic char-offset tagging functions from the brownfield top-level
``integrations/conll_format.py`` CLI script, ported VERBATIM (logic-identical) into the package MINUS
its argparse / ``load_dataset`` / ``print`` / ``main`` side-effects, so they can be streamed by
:func:`pii_anon_datasets.distribution.conll_export.export_conll`. Two load-bearing properties:

1. **Pure-stdlib + deterministic (NFR-004 / AX-002).** No third-party deps and NONE of
   {random, time, uuid, datetime, secrets}: the whitespace tokenizer preserves char offsets and the
   BIO/BILOU tagging is a pure function of ``(text, annotations)`` — the same record always yields a
   byte-identical CoNLL string. CoNLL is the lingua franca for NER (spaCy, Flair, HuggingFace
   token-classification), so this is the toolchain-portable export path.
2. **char-offset alignment.** :func:`_assign_bio_tags` tags a token ``B-``/``I-`` iff it overlaps an
   annotation char-span (``tok_start < ann_end and tok_end > ann_start``) — the first overlapping
   token of an entity is ``B-``, the rest ``I-``, everything else ``O``. :func:`_bio_to_bilou`
   collapses single-token entities to ``U-`` and marks the last token of a multi-token entity ``L-``.

``record_to_conll`` is the streaming wrap point (the brownfield ``format`` kwarg is renamed ``fmt``
here to avoid shadowing the builtin); ``build_label2id`` is the HuggingFace token-classification
``label2id`` builder (the brownfield ``_build_label2id``, ported and made public).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

# The supported tagging schemes (HuggingFace/Flair/spaCy all consume BIO; BILOU is the boundary-aware
# variant). ``record_to_conll`` raises ``ValueError`` for anything else.
CONLL_FORMATS: tuple[str, ...] = ("bio", "bilou")


def _tokenize_simple(text: str) -> list[tuple[str, int, int]]:
    """Whitespace tokenizer preserving char offsets: list of ``(token, start, end)``.

    Deterministic and pure: splits on Unicode whitespace and records each token's half-open
    ``[start, end)`` char span into ``text`` (so BIO tags can be aligned to annotation char-offsets).
    """
    tokens: list[tuple[str, int, int]] = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        start = i
        while i < len(text) and not text[i].isspace():
            i += 1
        tokens.append((text[start:i], start, i))
    return tokens


def _assign_bio_tags(
    tokens: Sequence[tuple[str, int, int]],
    annotations: Sequence[Mapping[str, object]],
) -> list[str]:
    """B-/I-/O from char-offset overlap (``tok_start < ann_end and tok_end > ann_start``).

    A token gets ``B-<TYPE>`` if it is the FIRST token overlapping an annotation's char-span and
    ``I-<TYPE>`` for each subsequent overlapping token; non-overlapping tokens stay ``O``. Pure and
    deterministic (a function of the token offsets and the annotation spans only).
    """
    tags = ["O"] * len(tokens)

    for ann in annotations:
        ann_start = int(ann["start"])  # type: ignore[call-overload]
        ann_end = int(ann["end"])  # type: ignore[call-overload]
        entity_type = str(ann["entity_type"])
        first_token = True

        for ti, (_token_text, tok_start, tok_end) in enumerate(tokens):
            # Token overlaps with annotation (half-open spans).
            if tok_start < ann_end and tok_end > ann_start:
                if first_token:
                    tags[ti] = f"B-{entity_type}"
                    first_token = False
                else:
                    tags[ti] = f"I-{entity_type}"

    return tags


def _bio_to_bilou(
    tokens: Sequence[tuple[str, int, int]],
    bio_tags: Sequence[str],
) -> list[str]:
    """B/I/L/O/U conversion (Begin, Inside, Last, Outside, Unit).

    A ``B-`` not followed by an ``I-`` of the same entity becomes ``U-`` (single-token entity); an
    ``I-`` not followed by another ``I-`` of the same entity becomes ``L-`` (last token). Pure.
    """
    bilou_tags = list(bio_tags)
    n = len(bilou_tags)

    for i in range(n):
        tag = bilou_tags[i]
        if tag == "O":
            continue

        prefix, entity = tag.split("-", 1)
        next_tag = bilou_tags[i + 1] if i + 1 < n else "O"
        next_is_inside = next_tag.startswith(f"I-{entity}")

        if prefix == "B":
            if next_is_inside:
                bilou_tags[i] = f"B-{entity}"  # stays B
            else:
                bilou_tags[i] = f"U-{entity}"  # single-token entity
        elif prefix == "I":
            if next_is_inside:
                bilou_tags[i] = f"I-{entity}"  # stays I
            else:
                bilou_tags[i] = f"L-{entity}"  # last token

    return bilou_tags


def record_to_conll(record: Mapping[str, object], *, fmt: str = "bio") -> str:
    """One record -> CoNLL string: newline-split sentences, global-offset tokenize, tab-sep
    ``token\\tTAG``, a blank line between sentences. ``fmt`` in :data:`CONLL_FORMATS`.

    Splits ``record["text"]`` on newlines into sentences; each sentence is whitespace-tokenized and
    its token offsets are lifted to GLOBAL char-offsets (so the record's char-offset ``annotations``
    align), BIO-tagged, optionally converted to BILOU, then emitted ``token\\tTAG`` per line with a
    trailing blank line between sentences. Deterministic and pure-stdlib (NFR-004 / AX-002).

    Raises:
        ValueError: if ``fmt`` is not one of :data:`CONLL_FORMATS`.
    """
    if fmt not in CONLL_FORMATS:
        raise ValueError(f"fmt must be one of {CONLL_FORMATS}, got {fmt!r}")

    text = str(record["text"])
    annotations = record.get("annotations", [])
    if not isinstance(annotations, Sequence):
        annotations = []

    # Split into sentences (simple newline-based).
    lines_output: list[str] = []
    sentences = text.split("\n")

    global_offset = 0
    for sentence in sentences:
        if not sentence.strip():
            global_offset += len(sentence) + 1  # +1 for the newline
            continue

        # Tokenize the sentence, then lift offsets to be global (so annotations align).
        tokens = _tokenize_simple(sentence)
        global_tokens = [(t, s + global_offset, e + global_offset) for t, s, e in tokens]

        if global_tokens:
            bio_tags = _assign_bio_tags(global_tokens, annotations)
            tags = _bio_to_bilou(global_tokens, bio_tags) if fmt == "bilou" else bio_tags

            # tags is built to be exactly len(global_tokens) long, so strict= is satisfiable.
            for (token_text, _, _), tag in zip(global_tokens, tags, strict=True):
                lines_output.append(f"{token_text}\t{tag}")
            lines_output.append("")  # blank line between sentences

        global_offset += len(sentence) + 1

    return "\n".join(lines_output)


def build_label2id(records: Sequence[Mapping[str, object]]) -> dict[str, int]:
    """``O`` + ``B-``/``I-`` per sorted ``entity_type`` (HuggingFace token-classification compat).

    Collects the distinct ``entity_type`` values across ``records``' annotations, sorts them for a
    stable order, and assigns contiguous ids: ``O`` -> 0, then ``B-<TYPE>``/``I-<TYPE>`` per type.
    Deterministic (sorted) and pure-stdlib.
    """
    entity_types: set[str] = set()
    for record in records:
        annotations = record.get("annotations", [])
        if not isinstance(annotations, Sequence):
            continue
        for ann in annotations:
            entity_types.add(str(ann["entity_type"]))

    labels = ["O"]
    for etype in sorted(entity_types):
        labels.append(f"B-{etype}")
        labels.append(f"I-{etype}")

    return {label: i for i, label in enumerate(labels)}
