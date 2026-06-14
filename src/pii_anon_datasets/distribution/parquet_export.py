"""Streaming Parquet exporter (FR-024) — gov-02 N typed regime columns, no flattened blob.

Supersedes ``scripts/export_parquet.py`` (v1.3.0). Two load-bearing contracts:

1. **gov-02** — each FR-022 regime is its OWN typed column. The regime columns come from
   :func:`pii_anon_datasets.compliance.crosswalk.as_columns` (the five ``reg_*`` keys); the old
   single ``json.dumps(regulatory_domains)`` blob column (``export_parquet.py:54``) is DROPPED, not
   inherited. ``regulatory_domains`` is consumed to PRODUCE the typed columns and never written
   back as a flattened blob.
2. **Streaming** — :func:`export_parquet` consumes ``records`` as an iterator and writes via a
   single-pass ``pyarrow.parquet.ParquetWriter`` in batches of ``batch_size``. It NEVER calls
   ``list(records)`` / ``len(records)`` / indexes the input, so the full 575K corpus is never held
   in memory (the old script's blowup).

``pyarrow`` is a LAZY import (only inside :func:`_require_pyarrow`) so this module — and the
``pii_anon_datasets.distribution`` package — import on a pure-stdlib box (NFR-004). The exporter
writes a LOCAL file only: no network egress, no HF upload (AX-001).
"""
from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from typing import Any

from pii_anon_datasets.compliance.crosswalk import as_columns

# pyarrow has no type stubs / py.typed marker, so its objects surface as ``Any``; it is imported
# ONLY inside :func:`_require_pyarrow` (never at module top) so this module imports pure-stdlib
# (NFR-004). The ``Any`` annotations below name pyarrow handles without a runtime/type-check import.

# Scalar (non-nested) record fields are written as-is; everything else that is a list/dict is
# JSON-encoded into a string column. ``regulatory_domains`` is DELIBERATELY excluded from the row
# (it is replaced by the N typed reg_* columns — the gov-02 fix); writing it back as a blob would
# reintroduce the v1.3.0 bug.
_DROP_FIELDS: frozenset[str] = frozenset({"regulatory_domains"})


def _require_pyarrow() -> tuple[Any, Any]:
    """Lazily import pyarrow, or raise a clear install error (NFR-004 / [distribution] extra).

    Imported here (not at module top) so ``import pii_anon_datasets.distribution`` works without
    pyarrow. If the extra is missing, the ``RuntimeError`` names the exact install command.
    """
    try:
        # pyarrow ships no py.typed marker -> mypy --strict reports import-untyped; scope-suppress it
        # (consistent with the repo's lazy optional-dep convention, e.g. llm_adversary's anthropic).
        import pyarrow as pa  # type: ignore[import-untyped]
        import pyarrow.parquet as pq  # type: ignore[import-untyped]
    except ImportError as e:
        raise RuntimeError(
            "Parquet export needs the 'distribution' extra: "
            "pip install pii-anon-datasets[distribution]"
        ) from e
    return pa, pq


def _json_or_none(value: object) -> str | None:
    """Deterministically JSON-encode a nested block to a string (``None`` stays ``None``).

    ``sort_keys=True`` makes the encoding insensitive to dict ordering, so the same logical record
    always yields byte-identical column values (supports the deterministic-export contract).
    ``ensure_ascii=False`` preserves multilingual text without escaping.
    """
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _row(record: Mapping[str, object]) -> dict[str, object]:
    """Flatten one record to a Parquet row (gov-02): scalars + JSON nested blocks + reg_* columns.

    * scalar fields (``record_id``, ``text``, ``language``, ``domain``, ...) pass through;
    * nested ``list``/``dict`` blocks (``annotations``, ``entity_tracking``, ``provenance``, ...)
      are JSON-encoded into string columns;
    * ``regulatory_domains`` is DROPPED from the row and replaced by the five typed regime columns
      from :func:`as_columns` (the gov-02 fix — NO flattened blob column);
    * the regime columns are written LAST so they are unambiguously addressable.

    Deterministic and pure (no clock/RNG): the same record always yields the same row.
    """
    row: dict[str, object] = {}
    for key, value in record.items():
        if key in _DROP_FIELDS:
            continue  # replaced by typed reg_* columns below (gov-02)
        if isinstance(value, (list, dict)):
            row[key] = _json_or_none(value)
        else:
            row[key] = value  # scalar / None passes through unchanged

    # The N separate, legally-distinct typed regime columns (gov-02). Overwrite-safe: these keys are
    # the reg_* namespace, distinct from any scalar field above.
    row.update(as_columns(record))
    return row


def infer_union_schema(records: Iterable[Mapping[str, object]]) -> Any:
    """Compute the FULL union schema across all ``records`` (one pass) for a complete, stable export.

    ``export_parquet`` otherwise fixes its schema from the FIRST batch, which silently drops any column
    absent from that batch (the real corpus lost ``context_preservation``, present in 27.8% of records
    but not in the first 10k). Passing this union schema makes every batch — and every separately
    exported split/subset file — conform to the same complete column set, so no field is lost and
    multi-file HuggingFace dataset configs share one schema.

    Types: the first non-null value fixes a column's type (``bool``->bool, ``int``->int64,
    ``float``->float64, otherwise string — matching ``_row``'s scalar / JSON-string / reg_* output); a
    column null in every record defaults to string. Column order is sorted (deterministic).
    """
    pa, _ = _require_pyarrow()
    types: dict[str, Any] = {}
    for record in records:
        for name, value in _row(record).items():
            if name in types and not pa.types.is_null(types[name]):
                continue  # already have a concrete (non-null) type for this column
            if isinstance(value, bool):  # before int — bool is an int subclass
                types[name] = pa.bool_()
            elif isinstance(value, int):
                types[name] = pa.int64()
            elif isinstance(value, float):
                types[name] = pa.float64()
            elif value is None:
                types.setdefault(name, pa.null())
            else:
                types[name] = pa.string()
    return pa.schema([(n, pa.string() if pa.types.is_null(t) else t) for n, t in sorted(types.items())])


def export_parquet(
    records: Iterable[Mapping[str, object]],
    out_path: str,
    *,
    schema: Any = None,
    batch_size: int = 10_000,
) -> str:
    """Stream ``records`` to a Parquet file at ``out_path``; return ``out_path`` (FR-024).

    Streaming (load-bearing): ``records`` is consumed as a ONE-PASS iterator and written through a
    single :class:`pyarrow.parquet.ParquetWriter`, accumulating rows into batches of ``batch_size``.
    The input is NEVER ``list()``-ed / ``len()``-ed / indexed, so the full corpus is not held in
    memory. The writer's schema is fixed from the first batch — pyarrow infers its columns + types,
    which are pinned in a deterministic (sorted) column order; every subsequent row is then
    *conformed* to that schema (a missing key becomes null, an unexpected key is ignored), so records
    that carry the same fields in a different native key order — or omit an optional field — still
    write cleanly instead of raising a per-batch schema mismatch. The same records always produce
    identical table contents (the nested blocks are deterministically JSON-encoded with ``sort_keys``).

    gov-02: each FR-022 regime is its own typed ``reg_*`` column (via :func:`_row` / ``as_columns``);
    there is no flattened ``regulatory_domains`` blob column.

    AX-001: writes a LOCAL file only — no network egress, no HF upload.

    Raises:
        RuntimeError: if the ``[distribution]`` extra (pyarrow) is not installed — message names the
            install command.
        ValueError: if ``batch_size`` is not positive.
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size must be positive, got {batch_size}")

    pa, pq = _require_pyarrow()

    writer: Any = None
    batch: list[dict[str, object]] = []

    def _flush(rows: list[dict[str, object]]) -> None:
        """Write one accumulated batch against a STABLE, deterministically-ordered schema.

        Every row in every batch is conformed to ONE schema — a column absent from a record becomes
        null, an unexpected column is ignored — so records that list fields in a different order, or
        omit optional ones, all write cleanly instead of raising a per-batch schema mismatch. The
        schema is either the caller-supplied union schema (``infer_union_schema``, preferred — it
        carries EVERY column the corpus uses, so none is ever dropped) or, as a fallback, inferred from
        the first batch (representative only when the first batch happens to see every column).
        """
        nonlocal writer, schema
        if not rows:
            return
        if schema is None:
            # Fallback: infer names + types from the first batch, pinned in deterministic sorted order.
            inferred = pa.Table.from_pylist(rows).schema
            schema = pa.schema(sorted(inferred, key=lambda field: field.name))
        if writer is None:
            writer = pq.ParquetWriter(out_path, schema)
        names = schema.names
        conformed = [{name: row.get(name) for name in names} for row in rows]
        writer.write_table(pa.Table.from_pylist(conformed, schema=schema))

    try:
        for record in records:  # one-pass iteration — no list()/len()/indexing (streaming)
            batch.append(_row(record))
            if len(batch) >= batch_size:
                _flush(batch)
                batch = []  # drop the materialised batch so memory stays bounded
        _flush(batch)  # final partial batch

        if writer is None:
            # No records at all: still emit a valid (empty) Parquet file with the regime schema, so
            # downstream loaders/consumers always see a file with the gov-02 columns present.
            empty_schema = pa.Table.from_pylist(
                [], schema=_empty_schema(pa)
            ).schema
            writer = pq.ParquetWriter(out_path, empty_schema)
    finally:
        if writer is not None:
            writer.close()

    return out_path


def _empty_schema(pa: Any) -> Any:
    """Minimal schema for the zero-record case — the five typed regime columns (gov-02).

    Used only when ``export_parquet`` receives no records, so the emitted file still advertises the
    legally-distinct ``reg_*`` columns (and, deliberately, no flattened ``regulatory_domains`` blob).
    """
    return pa.schema([(col, pa.string()) for col in as_columns({})])
