"""Streaming CoNLL exporter (FR-024 / NFR-004) — a THIN wrap over the packaged BIO/BILOU functions.

:func:`export_conll` STREAMS a corpus to a ``.conll`` file. Two load-bearing contracts:

1. **Thin wrap (no business logic here).** All BIO/BILOU tagging lives in
   :func:`pii_anon_datasets.integrations.conll_format.record_to_conll` (the functions ported from the
   proven top-level CLI). This module contains NO tokenization/tagging logic of its own — it only
   streams records through ``record_to_conll`` and writes the double-blank-line document separator.
2. **Streaming (load-bearing).** ``records`` is consumed as a ONE-PASS iterator and written
   record-by-record; the input is NEVER ``list()``-ed / ``len()``-ed / indexed, so the full 575K
   corpus is never held in memory.

Pure-stdlib (NFR-004): no third-party deps and none of {random, time, uuid, datetime, secrets}, so
the same records always produce a byte-identical file (AX-002). Writes a LOCAL file only — no network
egress (AX-001).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from pii_anon_datasets.integrations.conll_format import record_to_conll


def export_conll(
    records: Iterable[Mapping[str, object]],
    out_path: str,
    *,
    fmt: str = "bio",
) -> str:
    """Stream ``records`` to a CoNLL file at ``out_path``; return ``out_path`` (FR-024).

    Streaming (load-bearing): ``records`` is consumed as a ONE-PASS iterator and each record is
    written through :func:`pii_anon_datasets.integrations.conll_format.record_to_conll` (the thin
    wrap — no tagging logic here). A double blank line (one written ``"\\n"`` joining two records that
    each already end on a blank line) separates documents; ``record_to_conll`` itself emits the
    single blank line between sentences. The input is NEVER ``list()``-ed / ``len()``-ed / indexed.

    ``fmt`` ("bio"/"bilou") is forwarded to ``record_to_conll`` (which raises ``ValueError`` for an
    unknown value). Pure-stdlib and deterministic (AX-002); writes a LOCAL file only (AX-001).
    """
    with open(out_path, "w", encoding="utf-8") as f:
        first = True
        for record in records:  # one-pass iteration — no list()/len()/indexing (streaming)
            if not first:
                f.write("\n")  # double blank line between documents
            f.write(record_to_conll(record, fmt=fmt))
            first = False
    return out_path
