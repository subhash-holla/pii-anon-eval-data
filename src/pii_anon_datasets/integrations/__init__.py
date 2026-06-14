"""Packaged NER-toolchain integrations (FR-024).

Hosts the PURE conversion functions that turn PII-Anon records into the formats the standard
NER-training toolchains consume, with NO CLI / IO / print side-effects (those live in the brownfield
top-level ``integrations/`` scripts). Today that is :mod:`pii_anon_datasets.integrations.conll_format`
— the BIO/BILOU char-offset tagging logic ported verbatim from the proven top-level
``integrations/conll_format.py`` CLI script, minus its argparse / ``load_dataset`` / print. These
functions are deterministic and pure-stdlib (NFR-004 / AX-002), so the streaming
:func:`pii_anon_datasets.distribution.conll_export.export_conll` thin-wraps
:func:`pii_anon_datasets.integrations.conll_format.record_to_conll` with no business logic of its own.
"""

from __future__ import annotations

from pii_anon_datasets.integrations.conll_format import (
    CONLL_FORMATS,
    build_label2id,
    record_to_conll,
)

__all__ = [
    "CONLL_FORMATS",
    "build_label2id",
    "record_to_conll",
]
