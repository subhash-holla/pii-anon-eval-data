"""Distribution surface (DC-12): standard corpus exports (FR-024).

Ships three things that make the CC0 corpus machine-discoverable and LOADABLE:

* the Parquet exporter (S5-02) that **supersedes** the v1.3.0 ``scripts/export_parquet.py`` (whose
  line-54 flattened ``regulatory_domains`` into ONE JSON blob — the gov-02 bug) — it emits each
  FR-022 regime as its OWN typed ``reg_*`` column (via
  :func:`pii_anon_datasets.compliance.crosswalk.as_columns`, S5-01) and **streams** records through a
  ``pyarrow`` ``ParquetWriter`` so the 575K corpus is never materialised in memory;
* the Croissant 1.0 JSON-LD emitter (S5-03) — :func:`build_croissant` describes that Parquet (the
  ``reg_*`` columns survive into the recordSet, gov-02) and :func:`validate_croissant` runs an
  always-on pure-stdlib schema-shape check (NFR-012);
* the HF dataset-card builder (S5-03) — :func:`build_dataset_card` whose counts derive from the
  packaged metadata, so they cannot drift (NFR-013);
* the NER-training exporters (S5-04) — :func:`export_conll` (a THIN stream over the packaged
  :mod:`pii_anon_datasets.integrations.conll_format` BIO/BILOU functions; pure-stdlib),
  :func:`to_spacy_offsets` (pure-stdlib spaCy char-offset training tuples), and
  :func:`export_spacy_docbin` (a serialized spaCy ``DocBin``; spaCy is a LAZY import behind the
  ``[baselines]`` extra) — so the corpus is consumable by spaCy / Flair / HuggingFace
  token-classification.

**Lazy heavy deps (NFR-004 / AX-001).** ``pyarrow`` (``[distribution]``), ``mlcroissant``
(``[croissant]``) and ``spacy`` (``[baselines]``) are imported ONLY inside the functions that need
them — so ``import pii_anon_datasets.distribution`` succeeds on a pure-stdlib box. Nothing here
performs network egress or HF upload: export writes a local file (Parquet / CoNLL / DocBin), the
emitters return local strings/dicts; publishing is a separate, opt-in step (not wired into this
module).
"""

from __future__ import annotations

from pii_anon_datasets.distribution.conll_export import export_conll
from pii_anon_datasets.distribution.croissant import build_croissant, validate_croissant
from pii_anon_datasets.distribution.dataset_card import build_dataset_card
from pii_anon_datasets.distribution.parquet_export import export_parquet
from pii_anon_datasets.distribution.spacy_export import export_spacy_docbin, to_spacy_offsets

__all__ = [
    "build_croissant",
    "build_dataset_card",
    "export_conll",
    "export_parquet",
    "export_spacy_docbin",
    "to_spacy_offsets",
    "validate_croissant",
]
