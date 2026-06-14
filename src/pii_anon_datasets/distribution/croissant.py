"""Croissant 1.0 JSON-LD emitter (FR-024 / NFR-012) — validate-AND-load + gov-02 reg_* fields.

Emits a Croissant 1.0 JSON-LD description of the CC0 corpus so it is machine-discoverable AND
loadable (not merely present). Two load-bearing contracts close **NFR-012**:

1. **Always-on schema-shape validation** — :func:`validate_croissant` is pure-stdlib (no
   ``mlcroissant`` needed) and asserts the Croissant 1.0 shape: the required top-level keys, ``@type``
   Dataset, a ``distribution`` FileObject, a ``recordSet`` of typed ``cr:Field``s, **and the five
   gov-02 ``reg_*`` fields declared** (from :data:`pii_anon_datasets.compliance.crosswalk.REGIMES`,
   the single source — never re-listed here). It raises :class:`ValueError` on the first violation, so
   dropping any ``reg_*`` field FAILS validation (gov-02 must survive into the description).
2. **Loads via HF datasets** — the Croissant describes the Parquet that
   :func:`pii_anon_datasets.distribution.parquet_export.export_parquet` (S5-02) writes; the
   ``distribution`` FileObject points at ``parquet_filename`` and the ``recordSet`` declares the same
   ``reg_*`` columns the exporter emits, so the description matches the data.

Counts (``total_records``/``total_annotations``/``entity_types``/``languages``/...) come from the
packaged ``pii_anon.metadata.json`` — the SAME single source ``stats/lattice.py`` reads via the
``_DATA_DIR`` pattern — so the description **cannot drift** from canonical.

``mlcroissant`` is a LAZY import (ONLY inside :func:`validate_with_mlcroissant`, never at module top)
behind the ``[croissant]`` extra, so this module — and the ``pii_anon_datasets.distribution`` package —
import on a pure-stdlib box (NFR-004). The emit is deterministic: no clock/RNG, ordered structures
(AX-002). It builds a local JSON-LD dict only — no network egress, no HF upload (AX-001).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pii_anon_datasets.compliance.crosswalk import REGIMES
from pii_anon_datasets.release.citation import CITATION_METADATA, render_bibtex

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_METADATA = _DATA_DIR / "pii_anon.metadata.json"

CROISSANT_VERSION = "1.0"
CROISSANT_CONFORMS_TO = "http://mlcommons.org/croissant/1.0"
# Locked revision #11 — data is CC0, code is Apache-2.0. The Croissant 'license' is the DATA license.
DATA_LICENSE = "https://creativecommons.org/publicdomain/zero/1.0/"

# The canonical Croissant 1.0 @context (schema.org ``sc:`` + mlcommons ``cr:`` + ``dct:`` namespaces,
# with the dataType/field/recordSet/distribution/fileObject term mappings). The standard published
# Croissant 1.0 context — a fixed literal (deterministic, no clock/RNG).
_CROISSANT_CONTEXT: dict[str, Any] = {
    "@language": "en",
    "@vocab": "https://schema.org/",
    "sc": "https://schema.org/",
    "cr": "http://mlcommons.org/croissant/",
    "dct": "http://purl.org/dc/terms/",
    "conformsTo": "dct:conformsTo",
    "citeAs": "cr:citeAs",
    "column": "cr:column",
    "data": {"@id": "cr:data", "@type": "@json"},
    "dataType": {"@id": "cr:dataType", "@type": "@vocab"},
    "extract": "cr:extract",
    "field": "cr:field",
    "fileObject": "cr:fileObject",
    "fileSet": "cr:fileSet",
    "format": "cr:format",
    "includes": "cr:includes",
    "isLiveDataset": "cr:isLiveDataset",
    "jsonPath": "cr:jsonPath",
    "key": "cr:key",
    "md5": "cr:md5",
    "sha256": "sc:sha256",  # schema.org term (mlcroissant maps sha256 -> SDO.sha256, NOT cr:)
    "datePublished": "sc:datePublished",  # schema.org term ("citeAs" already mapped above)
    "parentField": "cr:parentField",
    "path": "cr:path",
    "recordSet": "cr:recordSet",
    "references": "cr:references",
    "regex": "cr:regex",
    "repeated": "cr:repeated",
    "replace": "cr:replace",
    "source": "cr:source",
    "subField": "cr:subField",
    "transform": "cr:transform",
}

# Core scalar fields every record carries (mirrors the Parquet scalar columns ``_row`` writes); each
# becomes a Croissant Field with dataType ``sc:Text``. The five ``reg_*`` fields are appended from
# REGIMES (the single source) so gov-02 survives into the description.
_CORE_FIELDS: tuple[tuple[str, str], ...] = (
    ("record_id", "sc:Text"),
    ("text", "sc:Text"),
    ("language", "sc:Text"),
    ("domain", "sc:Text"),
    ("primary_dimension", "sc:Text"),
)

# The single FileObject @id / RecordSet @id — fixed literals (deterministic).
_FILE_OBJECT_ID = "parquet"
_RECORD_SET_ID = "records"
_PARQUET_ENCODING = "application/x-parquet"


def load_metadata(path: Path = _METADATA) -> dict[str, Any]:
    """Load the packaged canonical metadata (the single count source — cannot drift)."""
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _field(name: str, data_type: str) -> dict[str, Any]:
    """One Croissant ``cr:Field`` mapping a column of the FileObject to a typed JSON-LD field.

    ``source`` references the FileObject column of the same ``name`` (the recordSet draws from the
    Parquet distribution). Deterministic and pure.
    """
    return {
        "@type": "cr:Field",
        "@id": f"{_RECORD_SET_ID}/{name}",
        "name": name,
        "dataType": data_type,
        "source": {
            "fileObject": {"@id": _FILE_OBJECT_ID},
            "extract": {"column": name},
        },
    }


def _file_object(filename: str, sha256: str | None = None) -> dict[str, Any]:
    """The Croissant ``cr:FileObject`` for the Parquet distribution (``filename``).

    ``contentUrl`` is the relative filename (a local artifact — no network egress / no upload); the
    ``encodingFormat`` marks it Parquet so HF ``datasets`` knows how to load it (NFR-012). When a
    ``sha256`` is injected (the release step computes it over the built Parquet), it is emitted as the
    content hash — the Croissant spec requires a FileObject to carry ``md5`` or ``sha256``, and
    mlcroissant rejects one that carries neither.
    """
    obj: dict[str, Any] = {
        "@type": "cr:FileObject",
        "@id": _FILE_OBJECT_ID,
        "name": filename,
        "contentUrl": filename,
        "encodingFormat": _PARQUET_ENCODING,
    }
    if sha256 is not None:
        obj["sha256"] = sha256
    return obj


def _describe(md: Mapping[str, Any]) -> str:
    """Human-readable description interpolating the canonical counts (so it cannot drift).

    Reads ``total_records``/``total_annotations``/``entity_types``/``languages`` straight from
    ``md`` — the same packaged metadata ``stats/lattice.py`` uses — so the emitted string always
    tracks canonical. Deterministic (no clock/RNG).
    """
    # Raw (un-grouped) integers: the Croissant is machine-discovery metadata, so the counts are
    # embedded as their bare canonical values (no thousands separators) — directly matchable against
    # ``metadata[...]`` (the human-facing thousands-grouped form lives in the dataset card).
    return (
        f"PII-Anon: a CC0 multilingual PII benchmark corpus of {md['total_records']} records "
        f"with {md['total_annotations']} entity annotations spanning {md['entity_types']} entity "
        f"types across {md['languages']} languages. Each record carries the five legally-distinct "
        f"regulatory regime signals (gov-02 / FR-022) as separate reg_* fields. "
        f"Corpus version {md['version']}."
    )


def build_croissant(
    metadata: Mapping[str, Any] | None = None,
    *,
    parquet_filename: str = "pii_anon.parquet",
    parquet_sha256: str | None = None,
) -> dict[str, Any]:
    """Croissant 1.0 JSON-LD for the corpus; counts DERIVED from ``metadata`` (default: packaged).

    Emits ``@context`` + ``@type`` Dataset + ``conformsTo`` (1.0) + ``name``/``description``/
    ``version``/``license`` + a ``distribution`` FileObject for ``parquet_filename`` + a ``recordSet``
    whose fields are :data:`_CORE_FIELDS` followed by one ``reg_<regime>`` Field per
    :data:`REGIMES` (gov-02 survives into the description). The description string interpolates
    ``total_records``/``total_annotations``/``entity_types``/``languages`` from ``metadata`` so it can
    never drift from canonical.

    Deterministic and pure: no clock/RNG, ordered field list (core fields in declaration order, then
    the ordered ``REGIMES`` appended last); the same metadata always yields the same JSON-LD.
    """
    md = dict(metadata) if metadata is not None else load_metadata()
    fields = [_field(name, dtype) for name, dtype in _CORE_FIELDS]
    fields += [_field(f"reg_{regime}", "sc:Text") for regime in REGIMES]
    return {
        "@context": _CROISSANT_CONTEXT,
        "@type": "sc:Dataset",
        "conformsTo": CROISSANT_CONFORMS_TO,
        "name": "pii-anon",
        "version": md["version"],
        "license": DATA_LICENSE,
        "description": _describe(md),
        "citeAs": render_bibtex(),
        "datePublished": CITATION_METADATA["date-released"],
        "distribution": [_file_object(parquet_filename, parquet_sha256)],
        "recordSet": [
            {
                "@type": "cr:RecordSet",
                "@id": _RECORD_SET_ID,
                "name": _RECORD_SET_ID,
                "field": fields,
            }
        ],
    }


REQUIRED_TOP_LEVEL: tuple[str, ...] = (
    "@context",
    "@type",
    "name",
    "description",
    "license",
    "distribution",
    "recordSet",
)


def validate_croissant(jsonld: Mapping[str, Any]) -> None:
    """Always-on Croissant 1.0 schema-SHAPE validation (pure-stdlib). Raise :class:`ValueError` on the
    first violation.

    Checks: every :data:`REQUIRED_TOP_LEVEL` key present; ``@type`` is Dataset/``sc:Dataset``;
    ``distribution`` non-empty and each entry is a FileObject/FileSet with ``name`` +
    ``contentUrl``/``encodingFormat``; ``recordSet`` non-empty and each field is a ``cr:Field`` with
    ``name`` + ``dataType``; AND every ``reg_<regime>`` (from :data:`REGIMES`) is declared as a field
    (gov-02 must survive — dropping any ``reg_*`` field is a validation failure).
    """
    for key in REQUIRED_TOP_LEVEL:
        if key not in jsonld:
            raise ValueError(f"Croissant missing required top-level key: {key!r}")

    if jsonld["@type"] not in ("Dataset", "sc:Dataset"):
        raise ValueError(f"Croissant @type must be Dataset/sc:Dataset, got {jsonld['@type']!r}")

    distribution = jsonld["distribution"]
    if not isinstance(distribution, list) or not distribution:
        raise ValueError("Croissant 'distribution' must be a non-empty list")
    for entry in distribution:
        if entry.get("@type") not in ("cr:FileObject", "cr:FileSet"):
            raise ValueError(f"distribution entry @type must be cr:FileObject/cr:FileSet, got {entry.get('@type')!r}")
        if not entry.get("name"):
            raise ValueError("distribution FileObject missing 'name'")
        if not entry.get("contentUrl") or not entry.get("encodingFormat"):
            raise ValueError("distribution FileObject missing 'contentUrl'/'encodingFormat'")

    record_sets = jsonld["recordSet"]
    if not isinstance(record_sets, list) or not record_sets:
        raise ValueError("Croissant 'recordSet' must be a non-empty list")

    declared_fields: set[str] = set()
    for record_set in record_sets:
        fields = record_set.get("field")
        if not isinstance(fields, list) or not fields:
            raise ValueError("recordSet 'field' must be a non-empty list")
        for field in fields:
            if field.get("@type") != "cr:Field":
                raise ValueError(f"recordSet field @type must be cr:Field, got {field.get('@type')!r}")
            name = field.get("name")
            if not name:
                raise ValueError("recordSet field missing 'name'")
            if not field.get("dataType"):
                raise ValueError(f"recordSet field {name!r} missing 'dataType'")
            declared_fields.add(name)

    # gov-02 (load-bearing): every legally-distinct regime field must survive into the description.
    for regime in REGIMES:
        reg_field = f"reg_{regime}"
        if reg_field not in declared_fields:
            raise ValueError(
                f"gov-02: Croissant recordSet must declare the regime field {reg_field!r}; "
                f"declared: {sorted(declared_fields)}"
            )


def validate_with_mlcroissant(jsonld: Mapping[str, Any]) -> Any:
    """Full Croissant spec validation via ``mlcroissant`` — behind the ``[croissant]`` extra
    (skip-if-absent). Raise :class:`RuntimeError` naming ``pip install pii-anon-datasets[croissant]``
    if ``mlcroissant`` is absent.

    The ``mlcroissant`` import lives ONLY here (never at module top) so the module + the
    ``distribution`` package import on a pure-stdlib box (NFR-004). Constructing the ``Dataset`` runs
    the full spec validation.
    """
    try:
        # The [croissant] extra is absent in the pure-stdlib default env — that absence IS the
        # condition this guard handles, so mypy --strict's unresolved-import is scope-suppressed here
        # (repo convention for an absent optional dep, cf. llm_adversary's anthropic import).
        import mlcroissant as mlc  # type: ignore[import-not-found]
    except ImportError as e:
        raise RuntimeError(
            "Full Croissant validation needs the 'croissant' extra: pip install pii-anon-datasets[croissant]"
        ) from e
    return mlc.Dataset(jsonld=dict(jsonld))  # constructing the Dataset runs spec validation
