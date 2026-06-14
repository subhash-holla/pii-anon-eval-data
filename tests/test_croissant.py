"""S5-03 — Croissant 1.0 JSON-LD (FR-024 / NFR-012): validate-AND-load + gov-02 reg_* fields.

Pins the behaviour that makes the CC0 corpus machine-discoverable and LOADABLE (not merely
present). Two load-bearing contracts close NFR-012:

* **Always-on schema-shape validation** — :func:`validate_croissant` is pure-stdlib (no
  ``mlcroissant``) and asserts the Croissant 1.0 shape, INCLUDING the five gov-02 ``reg_*`` fields
  from :data:`pii_anon_datasets.compliance.crosswalk.REGIMES` (``nfr_012`` / gov-02).
* **Loads via HF datasets** — the Croissant describes the Parquet that
  :func:`pii_anon_datasets.distribution.parquet_export.export_parquet` (S5-02) writes; the round-trip
  test exports a tiny Parquet, builds the Croissant, validates the shape, then
  ``datasets.load_dataset('parquet', ...)`` loads it back with the ``reg_*`` columns intact
  (``nfr_012``).

Counts come from the packaged ``pii_anon.metadata.json`` so they cannot drift (``fr_024``).
``mlcroissant`` is ABSENT in this env -> full spec-validation is skip-if-absent; ``pyarrow`` +
``datasets`` ARE installed, so the load round-trip RUNS. ``mlcroissant`` is a LAZY import so the
module imports pure-stdlib (``nfr004`` / NFR-004).
"""

from __future__ import annotations

import ast
import builtins
import importlib
import pathlib

import pytest
from pii_anon_datasets.compliance.crosswalk import REGIMES
from pii_anon_datasets.distribution import croissant as croissant_mod
from pii_anon_datasets.distribution.croissant import (
    build_croissant,
    load_metadata,
    validate_croissant,
    validate_with_mlcroissant,
)

# The five typed regime fields the Croissant recordSet MUST declare (gov-02), from the SSOT.
EXPECTED_REGIME_FIELDS = tuple(f"reg_{regime}" for regime in REGIMES)

_BANNED_NONDETERMINISTIC = {"random", "time", "uuid", "datetime", "secrets"}


def _synthetic_records() -> list[dict]:
    """A tiny, varied in-memory record list — no real corpus, no PII, deterministic.

    Mirrors the S5-02 fixture shape so the Croissant description matches a Parquet the exporter
    actually produces: a gdpr record, a hipaa+pci_dss record (HIPAA fans out to both columns), a
    non-FR-022-tag record (sox -> other_regimes), and an untagged record.
    """
    return [
        {
            "record_id": "rec-0001",
            "text": "Synthetic alpha.",
            "language": "en",
            "domain": "clinical",
            "primary_dimension": "context_preservation",
            "regulatory_domains": ["gdpr"],
            "annotations": [{"category": "identity", "span": [0, 9]}],
        },
        {
            "record_id": "rec-0002",
            "text": "Synthetic beta.",
            "language": "de",
            "domain": "financial",
            "primary_dimension": "diverse_pii_types",
            "regulatory_domains": ["hipaa", "pci_dss"],
            "annotations": [],
        },
        {
            "record_id": "rec-0003",
            "text": "Synthetic gamma.",
            "language": "fr",
            "domain": "legal",
            "primary_dimension": "diverse_pii_types",
            "regulatory_domains": ["sox"],  # non-FR-022 -> never a named reg_* field
            "annotations": [],
        },
        {
            "record_id": "rec-0004",
            "text": "Synthetic delta.",
            "language": "es",
            "domain": "general",
            "primary_dimension": "diverse_pii_types",
            "regulatory_domains": [],
            "annotations": [],
        },
    ]


def test_fr_024_croissant_has_required_jsonld_shape() -> None:
    """[UNIT-TEST] ``build_croissant()`` returns a Croissant 1.0 JSON-LD dict with ``@context``,
    ``@type`` Dataset, ``name``/``description``/``license``, ``conformsTo`` (croissant 1.0), a
    non-empty ``distribution`` and a non-empty ``recordSet``; ``validate_croissant`` passes."""
    jsonld = build_croissant()

    assert "@context" in jsonld and jsonld["@context"], "missing @context"
    assert jsonld["@type"] in ("Dataset", "sc:Dataset"), f"bad @type: {jsonld.get('@type')!r}"
    assert jsonld["name"], "missing name"
    assert jsonld["description"], "missing description"
    assert jsonld["license"], "missing license"
    assert "1.0" in str(jsonld["conformsTo"]), f"conformsTo must be croissant 1.0: {jsonld.get('conformsTo')!r}"
    assert jsonld["distribution"], "distribution must be non-empty"
    assert jsonld["recordSet"], "recordSet must be non-empty"

    # The always-on, pure-stdlib schema-shape validator passes on a well-formed Croissant.
    validate_croissant(jsonld)  # must not raise


def test_nfr_012_croissant_declares_reg_columns() -> None:
    """[UNIT-TEST] gov-02 survives into the description: the ``recordSet`` declares one ``Field`` per
    :data:`crosswalk.REGIMES` (the five ``reg_*`` fields), each typed — and there is NO flattened
    ``regulatory_domains`` field."""
    jsonld = build_croissant()

    # Collect the declared field names across every recordSet.
    field_names: set[str] = set()
    for record_set in jsonld["recordSet"]:
        for field in record_set["field"]:
            field_names.add(field["name"])
            assert field.get("dataType"), f"field {field['name']!r} has no dataType"

    for reg_field in EXPECTED_REGIME_FIELDS:
        assert reg_field in field_names, (
            f"gov-02 regime field {reg_field!r} not declared in recordSet; have {sorted(field_names)}"
        )
    assert len(EXPECTED_REGIME_FIELDS) == 5

    # The gov-02 bug being superseded: there must be NO flattened blob field.
    assert "regulatory_domains" not in field_names, (
        "found flattened 'regulatory_domains' field — gov-02 requires N separate typed reg_* fields"
    )

    # validate_croissant FAILS if a reg_* field is dropped (gov-02 is enforced, not incidental).
    broken = {
        **jsonld,
        "recordSet": [
            {
                **jsonld["recordSet"][0],
                "field": [f for f in jsonld["recordSet"][0]["field"] if f["name"] != EXPECTED_REGIME_FIELDS[0]],
            }
        ],
    }
    with pytest.raises(ValueError, match=EXPECTED_REGIME_FIELDS[0]):
        validate_croissant(broken)


def test_fr_024_croissant_counts_from_metadata_cannot_drift() -> None:
    """[PROPERTY-TEST] ``build_croissant(metadata)`` DERIVES its counts from ``metadata`` — passing a
    perturbed mapping changes the emitted JSON-LD accordingly (counts are not hardcoded)."""
    canonical = load_metadata()
    base = build_croissant(canonical)
    assert base["version"] == canonical["version"]
    assert str(canonical["total_records"]) in base["description"]

    perturbed = {**canonical, "version": "9.9.9-test", "total_records": 4242}
    out = build_croissant(perturbed)
    assert out["version"] == "9.9.9-test", "version must be derived from metadata, not hardcoded"
    assert "4242" in out["description"], "total_records must be derived from metadata, not hardcoded"
    # The canonical count must NOT appear when a perturbed metadata is supplied (proves derivation).
    assert str(canonical["total_records"]) not in out["description"]


def test_nfr_012_croissant_describes_loadable_parquet(tmp_path: pathlib.Path) -> None:
    """[INTEGRATION-TEST] NFR-012 validate-AND-load round-trip: export a tiny Parquet via
    ``parquet_export.export_parquet``, build the Croissant for it, assert ``validate_croissant``
    passes AND ``datasets.load_dataset('parquet', ...)`` loads it back with the ``reg_*`` columns
    intact — the literal NFR-012 threshold (validates AND loads)."""
    pytest.importorskip("pyarrow")
    datasets = pytest.importorskip("datasets")
    from pii_anon_datasets.distribution.parquet_export import export_parquet

    out = tmp_path / "pii_anon.parquet"
    export_parquet(_synthetic_records(), str(out))

    jsonld = build_croissant(parquet_filename=out.name)
    validate_croissant(jsonld)  # always-on shape check passes

    # The Croissant's distribution points at the Parquet we just wrote.
    content_urls = [fo.get("contentUrl") for fo in jsonld["distribution"]]
    assert out.name in content_urls, f"distribution must reference {out.name!r}; have {content_urls}"

    # ...and that Parquet loads via HF datasets with the reg_* columns intact (loadability).
    ds = datasets.load_dataset("parquet", data_files=str(out), split="train")
    assert ds.num_rows == 4
    for reg_col in EXPECTED_REGIME_FIELDS:
        assert reg_col in ds.column_names, f"regime column {reg_col!r} did not survive datasets load"
    by_id = {row["record_id"]: row for row in ds}
    assert by_id["rec-0001"]["reg_gdpr"] == "in_scope"


def test_nfr_012_croissant_declares_citeas_and_datepublished() -> None:
    """[INTEGRATION-TEST] nfr_012: the Croissant carries the recommended ``citeAs`` + ``datePublished``
    metadata (mlcroissant warns when they are absent). Both derive from the canonical
    ``CITATION_METADATA`` (single source of truth) so they can never drift from CITATION.cff / bibtex."""
    from pii_anon_datasets.release.citation import CITATION_METADATA, render_bibtex

    jsonld = build_croissant(parquet_sha256="c" * 64)
    assert jsonld["datePublished"] == CITATION_METADATA["date-released"]
    assert jsonld["citeAs"] == render_bibtex()
    # Still spec-valid with the recommended fields present.
    pytest.importorskip("mlcroissant")
    validate_with_mlcroissant(jsonld)


def test_nfr_012_croissant_fileobject_carries_injected_parquet_sha256() -> None:
    """[INTEGRATION-TEST] nfr_012: the Parquet FileObject must advertise a content hash — the
    Croissant spec requires ``md5`` or ``sha256``, and mlcroissant rejects a FileObject without one
    (``At least one of these properties should be defined: ['md5', 'sha256']``). ``build_croissant``
    accepts an injected ``parquet_sha256`` (mirroring the ``parquet_filename`` injection) and emits it
    on the FileObject so the shipped metadata passes full mlcroissant validation."""
    sha = "a" * 64  # a well-formed 64-hex sha256 — the value the release step injects
    jsonld = build_croissant(parquet_sha256=sha)

    fobj = jsonld["distribution"][0]
    assert fobj.get("sha256") == sha, "FileObject must carry the injected parquet sha256"

    # Full mlcroissant spec validation accepts the hash-bearing FileObject (was a ValidationError).
    pytest.importorskip("mlcroissant")
    validate_with_mlcroissant(jsonld)  # must not raise


def test_nfr_012_full_validation_skips_without_mlcroissant() -> None:
    """[CONTRACT-TEST] Full Croissant spec-validation is skip-if-absent, both directions:

    * ``mlcroissant`` absent (this env) -> ``validate_with_mlcroissant`` raises a clear
      ``RuntimeError`` naming ``pip install pii-anon-datasets[croissant]``;
    * ``mlcroissant`` present (``importorskip``) -> it validates a well-formed JSON-LD w/o error."""
    # A spec-valid FileObject must carry a content hash, so inject one (the release step computes the
    # real Parquet sha256); without it mlcroissant rejects the FileObject (md5/sha256 required).
    jsonld = build_croissant(parquet_sha256="0" * 64)

    try:
        import mlcroissant  # noqa: F401  (presence probe only)
    except ImportError:
        # Absent path (this env): must raise the clear install RuntimeError.
        with pytest.raises(RuntimeError) as excinfo:
            validate_with_mlcroissant(jsonld)
        assert "pip install pii-anon-datasets[croissant]" in str(excinfo.value), (
            f"RuntimeError must name the install command; got: {str(excinfo.value)!r}"
        )
    else:
        # Present path: full validation accepts a well-formed Croissant without error.
        pytest.importorskip("mlcroissant")
        validate_with_mlcroissant(jsonld)  # must not raise


def test_nfr004_croissant_pure_stdlib_imports_without_mlcroissant(monkeypatch: pytest.MonkeyPatch) -> None:
    """[PROPERTY-TEST] NFR-004: ``import pii_anon_datasets.distribution.croissant`` succeeds with
    ``mlcroissant`` blocked (lazy import); AST guard: the module imports NONE of
    {random, time, uuid, datetime, secrets} (deterministic, pure-stdlib)."""
    # (a) Lazy import: the module imports even when mlcroissant cannot be imported.
    real_import = builtins.__import__

    def _block_mlcroissant(name: str, *args: object, **kwargs: object) -> object:
        if name == "mlcroissant" or name.startswith("mlcroissant."):
            raise ImportError(f"No module named {name!r}")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", _block_mlcroissant)
    reloaded = importlib.reload(importlib.import_module("pii_anon_datasets.distribution.croissant"))
    assert reloaded is not None
    assert hasattr(reloaded, "build_croissant")

    # (b) AST guard: no nondeterministic imports anywhere in the module source.
    src = pathlib.Path(croissant_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert _BANNED_NONDETERMINISTIC.isdisjoint(imported), (
        f"croissant.py imports nondeterministic modules: {sorted(_BANNED_NONDETERMINISTIC & imported)}"
    )


# --- S5-close coverage hardening: every validate_croissant FAILURE branch (lines 218-250) ---
# build_croissant() once, then mutate deep copies so each malformed variant trips exactly one guard.
# This lifts distribution/croissant.py to >=85% line coverage.
import copy  # noqa: E402


def _valid() -> dict:
    """A freshly-built, well-formed Croissant (deep-copyable for per-branch mutation)."""
    return build_croissant()


def test_validate_croissant_rejects_missing_top_level_key() -> None:
    """[UNIT-TEST] A dropped required top-level key (here ``recordSet``) -> ValueError (line 216-218)."""
    bad = _valid()
    del bad["recordSet"]
    with pytest.raises(ValueError, match="missing required top-level key"):
        validate_croissant(bad)


def test_validate_croissant_rejects_wrong_at_type() -> None:
    """[UNIT-TEST] ``@type`` that is not Dataset/sc:Dataset -> ValueError (line 220-221)."""
    bad = _valid()
    bad["@type"] = "sc:CreativeWork"
    with pytest.raises(ValueError, match="@type must be Dataset"):
        validate_croissant(bad)


def test_validate_croissant_rejects_empty_distribution() -> None:
    """[UNIT-TEST] An empty (or non-list) ``distribution`` -> ValueError (line 223-225)."""
    bad = _valid()
    bad["distribution"] = []
    with pytest.raises(ValueError, match="'distribution' must be a non-empty list"):
        validate_croissant(bad)


def test_validate_croissant_rejects_distribution_entry_wrong_type() -> None:
    """[UNIT-TEST] A distribution entry whose ``@type`` is not FileObject/FileSet -> ValueError
    (line 227-228)."""
    bad = copy.deepcopy(_valid())
    bad["distribution"][0]["@type"] = "cr:NotAFileObject"
    with pytest.raises(ValueError, match="distribution entry @type"):
        validate_croissant(bad)


def test_validate_croissant_rejects_distribution_missing_name() -> None:
    """[UNIT-TEST] A distribution FileObject with no ``name`` -> ValueError (line 229-230)."""
    bad = copy.deepcopy(_valid())
    del bad["distribution"][0]["name"]
    with pytest.raises(ValueError, match="distribution FileObject missing 'name'"):
        validate_croissant(bad)


def test_validate_croissant_rejects_distribution_missing_contenturl_or_encoding() -> None:
    """[UNIT-TEST] A distribution FileObject missing ``contentUrl``/``encodingFormat`` -> ValueError
    (line 231-232)."""
    bad = copy.deepcopy(_valid())
    del bad["distribution"][0]["contentUrl"]
    with pytest.raises(ValueError, match="contentUrl"):
        validate_croissant(bad)

    bad2 = copy.deepcopy(_valid())
    del bad2["distribution"][0]["encodingFormat"]
    with pytest.raises(ValueError, match="contentUrl"):
        validate_croissant(bad2)


def test_validate_croissant_rejects_empty_recordset() -> None:
    """[UNIT-TEST] An empty (or non-list) ``recordSet`` -> ValueError (line 234-236)."""
    bad = _valid()
    bad["recordSet"] = []
    with pytest.raises(ValueError, match="'recordSet' must be a non-empty list"):
        validate_croissant(bad)


def test_validate_croissant_rejects_empty_field_list() -> None:
    """[UNIT-TEST] A recordSet whose ``field`` is empty/non-list -> ValueError (line 241-242)."""
    bad = copy.deepcopy(_valid())
    bad["recordSet"][0]["field"] = []
    with pytest.raises(ValueError, match="'field' must be a non-empty list"):
        validate_croissant(bad)


def test_validate_croissant_rejects_field_wrong_type() -> None:
    """[UNIT-TEST] A field whose ``@type`` is not ``cr:Field`` -> ValueError (line 244-245)."""
    bad = copy.deepcopy(_valid())
    bad["recordSet"][0]["field"][0]["@type"] = "cr:NotAField"
    with pytest.raises(ValueError, match="field @type must be cr:Field"):
        validate_croissant(bad)


def test_validate_croissant_rejects_field_missing_name() -> None:
    """[UNIT-TEST] A field with no ``name`` -> ValueError (line 246-248)."""
    bad = copy.deepcopy(_valid())
    del bad["recordSet"][0]["field"][0]["name"]
    with pytest.raises(ValueError, match="field missing 'name'"):
        validate_croissant(bad)


def test_validate_croissant_rejects_field_missing_datatype() -> None:
    """[UNIT-TEST] A field with no ``dataType`` -> ValueError (line 249-250)."""
    bad = copy.deepcopy(_valid())
    del bad["recordSet"][0]["field"][0]["dataType"]
    with pytest.raises(ValueError, match="missing 'dataType'"):
        validate_croissant(bad)


def test_validate_croissant_rejects_dropped_reg_field() -> None:
    """[UNIT-TEST] gov-02: dropping ANY ``reg_*`` field fails validation (line 253-260) — the regime
    signals must survive into the description."""
    dropped = EXPECTED_REGIME_FIELDS[-1]  # e.g. reg_pci_dss
    bad = copy.deepcopy(_valid())
    bad["recordSet"][0]["field"] = [
        f for f in bad["recordSet"][0]["field"] if f.get("name") != dropped
    ]
    with pytest.raises(ValueError, match=dropped):
        validate_croissant(bad)
