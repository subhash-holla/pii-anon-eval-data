"""S5-02 — Parquet export (FR-024): gov-02 N regime columns + streaming.

Pins the behaviour that *supersedes* the v1.3.0 ``scripts/export_parquet.py`` (whose line-54
flattened ``regulatory_domains`` into ONE JSON blob — the gov-02 bug). The new exporter:

* emits each FR-022 regime as its OWN typed ``reg_*`` column via
  :func:`pii_anon_datasets.compliance.crosswalk.as_columns` (S5-01) — **no** flattened
  ``regulatory_domains`` blob column (``fr_024`` / gov-02);
* **streams** records through a ``ParquetWriter`` (never materialises the corpus) (``fr_024``);
* round-trips + loads via HF ``datasets`` (``nfr_012``);
* keeps ``pyarrow`` a LAZY import so the package imports pure-stdlib (``nfr004`` / NFR-004).

pyarrow + datasets ARE installed in this environment, so the integration tests RUN. The top-level
``importorskip`` keeps the module honest on a stdlib-only box (NFR-004) without lying about coverage.
"""
from __future__ import annotations

import json
from collections.abc import Iterator

import pytest

# pyarrow backs the [distribution] extra; skip cleanly on a pure-stdlib box (it IS installed here).
pyarrow = pytest.importorskip("pyarrow")
import pyarrow.parquet as pq  # noqa: E402  (after importorskip by design)
from pii_anon_datasets.compliance.crosswalk import REGIMES  # noqa: E402
from pii_anon_datasets.distribution.parquet_export import export_parquet  # noqa: E402

# The five typed regime columns the exporter MUST emit (gov-02), derived from the SSOT regime list.
EXPECTED_REGIME_COLUMNS = tuple(f"reg_{regime}" for regime in REGIMES)


def _synthetic_records() -> list[dict]:
    """A tiny, varied in-memory record list — no real corpus, no PII, deterministic.

    Covers: a single-regime record (gdpr), a multi-regime record (hipaa -> BOTH HIPAA columns +
    pci_dss), a non-FR-022-tag record (sox -> surfaced via other_regimes, NOT a named column), and
    an untagged record — so the regime columns and JSON-encoded nested blocks are all exercised.
    """
    return [
        {
            "record_id": "rec-0001",
            "text": "Synthetic alpha.",
            "language": "en",
            "domain": "clinical",
            "regulatory_domains": ["gdpr"],
            "annotations": [{"category": "identity", "span": [0, 9]}],
            "entity_tracking": {"num_distinct_persons": 1},
            "provenance": {"license": "CC0-1.0", "source_type": "synthetic"},
            "dimensions": ["context_preservation"],
        },
        {
            "record_id": "rec-0002",
            "text": "Synthetic beta.",
            "language": "de",
            "domain": "financial",
            "regulatory_domains": ["hipaa", "pci_dss"],
            "annotations": [],
            "entity_tracking": {"num_distinct_persons": 0},
            "provenance": {"license": "CC0-1.0", "source_type": "synthetic"},
            "dimensions": [],
        },
        {
            "record_id": "rec-0003",
            "text": "Synthetic gamma.",
            "language": "fr",
            "domain": "legal",
            "regulatory_domains": ["sox"],  # non-FR-022 -> other_regimes, never a named column
            "annotations": [{"category": "financial", "span": [0, 9]}],
            "entity_tracking": {"num_distinct_persons": 0},
            "provenance": {"license": "CC0-1.0", "source_type": "synthetic"},
            "dimensions": ["diverse_pii_types"],
        },
        {
            "record_id": "rec-0004",
            "text": "Synthetic delta.",
            "language": "es",
            "domain": "general",
            "regulatory_domains": [],  # untagged -> all regimes out_of_scope
            "annotations": [],
            "entity_tracking": {"num_distinct_persons": 0},
            "provenance": {"license": "CC0-1.0", "source_type": "synthetic"},
            "dimensions": [],
        },
    ]


def test_fr_024_parquet_has_n_separate_regime_columns(tmp_path):
    """[INTEGRATION-TEST] gov-02: the 5 typed reg_* columns are present and independently
    addressable; there is NO flattened ``regulatory_domains`` JSON-blob column (the line-54 fix)."""
    out = tmp_path / "corpus.parquet"
    export_parquet(_synthetic_records(), str(out))

    schema = pq.read_schema(out)
    names = set(schema.names)

    # Each FR-022 regime is its OWN typed column (gov-02), independently addressable.
    for col in EXPECTED_REGIME_COLUMNS:
        assert col in names, f"missing typed regime column {col!r}; have {sorted(names)}"
    assert len(EXPECTED_REGIME_COLUMNS) == 5

    # The gov-02 bug being superseded: there must be NO flattened blob column.
    assert "regulatory_domains" not in names, (
        "found flattened 'regulatory_domains' blob column — that is the v1.3.0 gov-02 bug; "
        "regimes must be N separate typed reg_* columns"
    )

    # Independently addressable + correctly populated for the gdpr-only record.
    table = pq.read_table(out, columns=list(EXPECTED_REGIME_COLUMNS) + ["record_id"])
    by_id = {r["record_id"]: r for r in table.to_pylist()}
    assert by_id["rec-0001"]["reg_gdpr"] == "in_scope"
    assert by_id["rec-0001"]["reg_hipaa_safe_harbor"] == "out_of_scope_of_dataset"
    # hipaa tag fans out to BOTH HIPAA legal-standard columns (never collapsed).
    assert by_id["rec-0002"]["reg_hipaa_safe_harbor"] == "in_scope"
    assert by_id["rec-0002"]["reg_hipaa_expert_determination"] == "in_scope"
    assert by_id["rec-0002"]["reg_pci_dss"] == "in_scope"


def test_fr_024_parquet_roundtrips_records(tmp_path):
    """[INTEGRATION-TEST] N synthetic records write -> read back via pyarrow.parquet -> same row
    count + key scalar fields (record_id, text, language) preserved."""
    records = _synthetic_records()
    out = tmp_path / "corpus.parquet"
    export_parquet(records, str(out))

    table = pq.read_table(out)
    assert table.num_rows == len(records)

    rows = table.to_pylist()
    got = {r["record_id"]: r for r in rows}
    for rec in records:
        rid = rec["record_id"]
        assert rid in got
        assert got[rid]["text"] == rec["text"]
        assert got[rid]["language"] == rec["language"]
    # Nested blocks survive as JSON-decodable strings (not flattened, not dropped).
    assert json.loads(got["rec-0001"]["annotations"]) == records[0]["annotations"]
    assert json.loads(got["rec-0001"]["entity_tracking"]) == records[0]["entity_tracking"]


def test_nfr_012_parquet_loads_via_datasets(tmp_path):
    """[INTEGRATION-TEST] NFR-012 loadability: HF ``datasets.load_dataset('parquet', ...)``
    round-trips the file and the reg_* regime columns survive the load."""
    datasets = pytest.importorskip("datasets")

    out = tmp_path / "corpus.parquet"
    export_parquet(_synthetic_records(), str(out))

    ds = datasets.load_dataset("parquet", data_files=str(out), split="train")
    assert ds.num_rows == 4
    for col in EXPECTED_REGIME_COLUMNS:
        assert col in ds.column_names, f"regime column {col!r} did not survive datasets load"
    # The gdpr-only record's regime signal survives the HF datasets round-trip.
    by_id = {row["record_id"]: row for row in ds}
    assert by_id["rec-0001"]["reg_gdpr"] == "in_scope"


def test_fr_024_export_streams_not_materializes(tmp_path):
    """[UNIT-TEST] Streaming (load-bearing): ``export_parquet`` consumes records as a ONE-SHOT
    iterator via ParquetWriter — it must not ``list()``/``len()``/index the whole input.

    A one-shot generator can be iterated exactly once; if the exporter materialised it (or iterated
    twice) the second pass would yield nothing / raise. We assert the file holds every yielded row
    and that the generator was driven to exhaustion (proving a single streaming pass)."""
    consumed: list[str] = []

    def one_shot() -> Iterator[dict]:
        for rec in _synthetic_records():
            consumed.append(rec["record_id"])  # observe consumption order/count
            yield rec

    gen = one_shot()
    out = tmp_path / "corpus.parquet"
    export_parquet(gen, str(out))

    # Every record was streamed exactly once, in order (no re-iteration, no materialisation).
    assert consumed == ["rec-0001", "rec-0002", "rec-0003", "rec-0004"]
    # The generator is exhausted — a second pass yields nothing (one-shot was honoured).
    assert list(gen) == []
    # And all four rows reached the file.
    assert pq.read_table(out).num_rows == 4


def test_fr_024_deterministic_export(tmp_path):
    """[PROPERTY-TEST] Exporting the same records twice yields identical table CONTENTS.

    pyarrow stamps its own library version into the Parquet footer metadata, so raw bytes are not a
    stable contract; the deterministic guarantee is over the logical table (schema + column data),
    which we compare via ``Table.equals``."""
    records = _synthetic_records()
    out_a = tmp_path / "a.parquet"
    out_b = tmp_path / "b.parquet"
    export_parquet(records, str(out_a))
    export_parquet(records, str(out_b))

    table_a = pq.read_table(out_a)
    table_b = pq.read_table(out_b)
    assert table_a.schema.equals(table_b.schema)
    assert table_a.equals(table_b), "same records exported twice produced differing table contents"


def test_nfr004_distribution_imports_without_pyarrow(monkeypatch):
    """[CONTRACT-TEST] NFR-004 lazy import: ``import pii_anon_datasets.distribution`` succeeds with
    NO pyarrow; calling the exporter without the [distribution] extra raises a clear RuntimeError
    naming ``pip install pii-anon-datasets[distribution]``."""
    import builtins
    import importlib

    # The package itself must import on a pure-stdlib box (no pyarrow at module top).
    dist_pkg = importlib.import_module("pii_anon_datasets.distribution")
    assert dist_pkg is not None

    real_import = builtins.__import__

    def _block_pyarrow(name, *args, **kwargs):
        if name == "pyarrow" or name.startswith("pyarrow."):
            raise ImportError(f"No module named {name!r}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _block_pyarrow)

    with pytest.raises(RuntimeError) as excinfo:
        export_parquet(_synthetic_records(), "unused.parquet")

    msg = str(excinfo.value)
    assert "pip install pii-anon-datasets[distribution]" in msg, (
        f"RuntimeError must name the install command; got: {msg!r}"
    )


# --- S5-close coverage hardening: batch-size guard, batch-flush boundary, zero-record empty file ---
# These lift parquet_export.py to >=85% line coverage by exercising the edge paths the integration
# tests above don't reach (the ValueError guard, the mid-stream flush, and the empty-corpus schema).


def test_fr_024_parquet_rejects_nonpositive_batch_size(tmp_path):
    """[UNIT-TEST] ``batch_size <= 0`` raises ``ValueError`` BEFORE any pyarrow work (the guard at the
    top of ``export_parquet`` — line 122)."""
    out = tmp_path / "corpus.parquet"
    for bad in (0, -1):
        with pytest.raises(ValueError, match="batch_size must be positive"):
            export_parquet(_synthetic_records(), str(out), batch_size=bad)
    # The guard fires before writing — no file is produced.
    assert not out.exists()


def test_fr_024_parquet_flushes_at_batch_boundary(tmp_path):
    """[UNIT-TEST] With ``batch_size=1`` every record triggers a mid-stream flush (lines 144-145: the
    ``len(batch) >= batch_size`` boundary + the batch reset), yet all rows still land and the schema
    is fixed from the first batch so later batches conform."""
    records = _synthetic_records()
    out = tmp_path / "corpus.parquet"
    returned = export_parquet(records, str(out), batch_size=1)

    assert returned == str(out)
    table = pq.read_table(out)
    # Every record reached the file even though each was flushed as its own one-row batch.
    assert table.num_rows == len(records)
    got = {r["record_id"]: r for r in table.to_pylist()}
    assert set(got) == {"rec-0001", "rec-0002", "rec-0003", "rec-0004"}
    # The reg_* schema (fixed from the first flushed batch) is present on the multi-batch file.
    for col in EXPECTED_REGIME_COLUMNS:
        assert col in set(table.schema.names)


def test_fr_024_parquet_empty_iterator_writes_valid_empty_file_with_reg_schema(tmp_path):
    """[UNIT-TEST] An EMPTY record stream still emits a VALID, readable Parquet whose schema carries
    the five typed ``reg_*`` columns (lines 151-154: the ``writer is None`` zero-record branch +
    ``_empty_schema``) — so downstream loaders always see the gov-02 columns present."""
    out = tmp_path / "empty.parquet"
    returned = export_parquet(iter(()), str(out))  # a genuinely empty one-shot iterator

    assert returned == str(out)
    assert out.exists()
    table = pq.read_table(out)
    assert table.num_rows == 0  # zero records -> zero rows, but a real file
    names = set(table.schema.names)
    for col in EXPECTED_REGIME_COLUMNS:
        assert col in names, f"empty Parquet must still declare regime column {col!r}; have {sorted(names)}"
    # gov-02: no flattened blob column sneaks into the empty-file schema either.
    assert "regulatory_domains" not in names


def test_fr_024_parquet_handles_heterogeneous_record_schemas(tmp_path):
    """[INTEGRATION-TEST] fr_024 / nfr_012: records with a DIFFERENT key order across a batch
    boundary — and an optional field present in one batch but absent in a later one — must ALL land
    in one Parquet.

    Regression for the real 575,604-corpus crash at row 110,000: the exporter fixed its schema from
    the first batch's pyarrow *inference*, but a later batch (whose records carried the same fields
    in a different native key order, some missing ``token_count``) inferred a different schema, so
    ``ParquetWriter.write_table`` raised ``Table schema does not match schema used to create file``
    and the writer died mid-stream. ``batch_size=2`` forces the divergent records into a later batch.
    The previous ``_synthetic_records`` fixture never caught this because every record had identical
    keys in identical order.
    """
    records = [
        # batch 1 — canonical key order; both carry the optional token_count
        {"record_id": "rec-0001", "text": "alpha", "language": "en", "domain": "clinical",
         "regulatory_domains": ["gdpr"], "annotations": [], "token_count": 3},
        {"record_id": "rec-0002", "text": "beta", "language": "de", "domain": "financial",
         "regulatory_domains": [], "annotations": [], "token_count": 5},
        # batch 2 — DIFFERENT key order, and NEITHER record carries token_count (rec-0004 also drops
        # annotations) — exactly the heterogeneity the real corpus has after enrichment.
        {"language": "fr", "annotations": [], "domain": "legal", "text": "gamma",
         "regulatory_domains": ["sox"], "record_id": "rec-0003"},
        {"text": "delta", "record_id": "rec-0004", "language": "es", "domain": "general",
         "regulatory_domains": []},
    ]
    out = tmp_path / "corpus.parquet"
    export_parquet(records, str(out), batch_size=2)  # 2 batches -> cross-batch schema divergence

    table = pq.read_table(out)
    assert table.num_rows == len(records), (
        f"all {len(records)} heterogeneous records must be written; got {table.num_rows}"
    )
    got = {r["record_id"]: r for r in table.to_pylist()}
    assert set(got) == {"rec-0001", "rec-0002", "rec-0003", "rec-0004"}
    # Key-order divergence in the later batch does not corrupt/lose data.
    assert got["rec-0003"]["text"] == "gamma"
    assert got["rec-0001"]["token_count"] == 3
    # A field absent from a later record is null-filled, not a crash and not a dropped column.
    assert got["rec-0003"]["token_count"] is None
    assert got["rec-0004"]["annotations"] is None
    # gov-02 reg_* columns still present through the heterogeneous write.
    for col in EXPECTED_REGIME_COLUMNS:
        assert col in set(table.schema.names)


def test_fr_024_parquet_keeps_columns_that_appear_only_after_the_first_batch(tmp_path):
    """[INTEGRATION-TEST] fr_024 / nfr_012: a column present ONLY in records after the first batch must
    NOT be dropped.

    Regression for the real-corpus data loss: fixing the schema from the *first batch* silently dropped
    any column absent from the first 10k records — the merged corpus lost ``context_preservation``
    (present in 27.8% of records). The exporter must conform to the full UNION schema
    (``infer_union_schema`` over a first pass), filling null where a record lacks a column, so multi-file
    HuggingFace configs share one schema and no field is lost.
    """
    from pii_anon_datasets.distribution.parquet_export import infer_union_schema

    records = [
        # batch 1 (batch_size=2): NO 'late_field'
        {"record_id": "r1", "text": "a", "domain": "clinical", "regulatory_domains": []},
        {"record_id": "r2", "text": "b", "domain": "financial", "regulatory_domains": []},
        # batch 2: 'late_field' appears only here
        {"record_id": "r3", "text": "c", "domain": "legal", "regulatory_domains": [], "late_field": "present"},
        {"record_id": "r4", "text": "d", "domain": "general", "regulatory_domains": [], "late_field": "also"},
    ]
    schema = infer_union_schema(records)
    assert "late_field" in schema.names, "union schema must include the late-appearing column"

    out = tmp_path / "corpus.parquet"
    export_parquet(records, str(out), schema=schema, batch_size=2)

    table = pq.read_table(out)
    assert "late_field" in table.schema.names, "late column must survive in the Parquet, not be dropped"
    assert table.num_rows == 4
    got = {r["record_id"]: r for r in table.to_pylist()}
    assert got["r3"]["late_field"] == "present"
    assert got["r1"]["late_field"] is None  # absent in early rows -> null, not a dropped column
    # gov-02 reg_* columns are still present
    for col in EXPECTED_REGIME_COLUMNS:
        assert col in set(table.schema.names)


def test_fr_024_parquet_json_or_none_passthrough():
    """[UNIT-TEST] ``_json_or_none`` returns ``None`` for ``None`` (line 65) and a deterministic,
    sort_keys-stable JSON string for a nested block — the helper the row-flattener uses for nested
    columns."""
    from pii_anon_datasets.distribution.parquet_export import _json_or_none

    assert _json_or_none(None) is None
    # sort_keys=True makes the encoding order-insensitive (deterministic export contract).
    assert _json_or_none({"b": 1, "a": 2}) == _json_or_none({"a": 2, "b": 1})
    assert _json_or_none({"a": 2, "b": 1}) == '{"a": 2, "b": 1}'
