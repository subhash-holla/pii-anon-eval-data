"""Tests for compliance.crosswalk (FR-022 / gov-02: legally-distinct regulatory crosswalk).

S5-01 — the gov-02 structural fix. v1.3.0 ``scripts/export_parquet.py:54`` flattened
``regulatory_domains`` into ONE JSON blob; that is REJECTED here. The crosswalk emits **N
SEPARATE typed columns, legally distinct, with NO merged / equivalence / flattened verdict**.

LOAD-BEARING (gov-02 / FR-022):
* exactly 5 named, independently-addressable regime columns (``reg_gdpr``,
  ``reg_hipaa_safe_harbor``, ``reg_hipaa_expert_determination``, ``reg_ccpa_deidentified``,
  ``reg_pci_dss``);
* HIPAA is EXACTLY two columns — Safe-Harbor (§164.514(b)(2)) and Expert-Determination
  (§164.514(b)(1)) are different legal standards, NEVER collapsed to one HIPAA verdict;
* there is NO ``compliant`` / ``deidentified`` / ``overall`` / ``equivalent`` /
  ``regulatory_domains`` merged column, and a source grep (test #3) confirms no merged-verdict
  symbol survives in the module;
* a tag is an IN-SCOPE *signal*, never a compliance *determination* — the (non-empty)
  disclaimer states the crosswalk "informs, does not make, a determination";
* real corpus tags are lowercase ``{gdpr, ccpa, hipaa, pci_dss, sox, lgpd, pipa}``; ``hipaa``
  fans out to BOTH HIPAA columns; ``sox`` / ``lgpd`` / ``pipa`` are surfaced via
  ``other_regimes`` and NEVER folded into a named FR-022 column.

Pure-stdlib (NFR-004): test #6 is an AST guard pinning out {random, time, uuid, datetime,
secrets}. Every test fn carries an ``fr_022`` token.
"""
import ast
import pathlib
import re

import pytest
from pii_anon_datasets.compliance import crosswalk as crosswalk_mod
from pii_anon_datasets.compliance.crosswalk import (
    CROSSWALK_DISCLAIMER,
    REGIMES,
    RegimeStatus,
    RegulatoryCrosswalk,
    as_columns,
    crosswalk_record,
)

# The 5 typed Parquet columns FR-022 requires (ordered, independently addressable).
EXPECTED_COLUMNS = (
    "reg_gdpr",
    "reg_hipaa_safe_harbor",
    "reg_hipaa_expert_determination",
    "reg_ccpa_deidentified",
    "reg_pci_dss",
)


def test_fr_022_five_legally_distinct_columns() -> None:
    """``as_columns(record)`` yields EXACTLY the 5 typed regime columns — [UNIT-TEST].

    No more, no fewer: each regime is its own addressable column (gov-02), so an exporter or a
    bundle can reference ``reg_pci_dss`` without touching ``reg_gdpr``.
    """
    record = {"regulatory_domains": ["gdpr", "hipaa", "ccpa", "pci_dss"]}
    cols = as_columns(record)
    assert tuple(cols.keys()) == EXPECTED_COLUMNS
    assert len(cols) == 5
    # The 5 REGIMES constant is the single ordered source of truth behind the columns.
    assert REGIMES == (
        "gdpr",
        "hipaa_safe_harbor",
        "hipaa_expert_determination",
        "ccpa_deidentified",
        "pci_dss",
    )
    assert tuple(f"reg_{r}" for r in REGIMES) == EXPECTED_COLUMNS
    # Each value is a RegimeStatus string value, never a bool/merged verdict.
    assert set(cols.values()) <= {s.value for s in RegimeStatus}


def test_fr_022_hipaa_is_two_distinct_columns() -> None:
    """HIPAA is EXACTLY two columns — Safe-Harbor vs Expert-Determination — [AUDIT].

    §164.514(b)(2) (Safe-Harbor: 18 identifiers removed) and §164.514(b)(1) (Expert-Determination:
    statistical) are DIFFERENT legal standards. They must never be collapsed into one ``reg_hipaa``
    verdict — both appear, addressable independently.
    """
    hipaa_cols = [c for c in EXPECTED_COLUMNS if c.startswith("reg_hipaa")]
    assert hipaa_cols == ["reg_hipaa_safe_harbor", "reg_hipaa_expert_determination"]
    # Never a single collapsed HIPAA column.
    cols = as_columns({"regulatory_domains": ["hipaa"]})
    assert "reg_hipaa" not in cols
    assert "reg_hipaa_safe_harbor" in cols and "reg_hipaa_expert_determination" in cols
    # The two HIPAA regimes are distinct names in the REGIMES tuple.
    assert "hipaa_safe_harbor" in REGIMES and "hipaa_expert_determination" in REGIMES
    assert REGIMES.count("hipaa_safe_harbor") == 1
    assert REGIMES.count("hipaa_expert_determination") == 1


def test_fr_022_no_merged_or_equivalence_column() -> None:
    """NO merged / equivalence / flattened column exists anywhere — [AUDIT].

    Neither the column set, the dataclass fields, nor the module source may carry a
    ``compliant`` / ``deidentified`` / ``overall`` / ``equivalent`` / ``regulatory_domains`` (the
    v1.3.0 flattened blob) merged-verdict symbol. A source grep is the structural backstop.
    """
    cols = as_columns({"regulatory_domains": ["gdpr", "hipaa", "ccpa", "pci_dss"]})
    forbidden_cols = {"compliant", "deidentified", "overall", "equivalent", "regulatory_domains"}
    assert forbidden_cols.isdisjoint(cols.keys())
    # No column name (other than the regime-scoped ccpa_deidentified) is a bare merged verdict.
    for name in cols:
        assert name != "reg_deidentified"
        assert name != "reg_compliant"

    # Dataclass carries no merged-verdict field.
    xwalk = crosswalk_record({"regulatory_domains": ["gdpr"]})
    field_names = set(xwalk.as_dict().keys())
    assert forbidden_cols.isdisjoint(field_names)
    assert not any(f in {"compliant", "overall", "equivalent"} for f in vars(xwalk))

    # Source grep: no merged-verdict symbol survives as an identifier/assignment in the module.
    src = pathlib.Path(crosswalk_mod.__file__).read_text(encoding="utf-8")
    for symbol in ("compliant", "overall", "equivalent"):
        assert not re.search(rf"\b{symbol}\b", src), (
            f"crosswalk.py must carry no merged-verdict symbol; found '{symbol}'"
        )
    # The flattened ``regulatory_domains`` column name must not be emitted as a crosswalk column.
    assert "reg_regulatory_domains" not in src


def test_fr_022_presence_to_status_conservative() -> None:
    """Tag presence → conservative IN_SCOPE *signal*, never a determination — [UNIT-TEST].

    A record tagged ``hipaa`` puts BOTH HIPAA columns ``in_scope``; an untagged regime is
    ``out_of_scope_of_dataset`` (NOT "compliant"/"non-compliant"). The crosswalk carries a
    non-empty "informs, does not make, a determination" disclaimer and yields no ``True`` verdict.
    """
    xwalk = crosswalk_record({"regulatory_domains": ["hipaa"]})
    assert isinstance(xwalk, RegulatoryCrosswalk)
    assert xwalk.hipaa_safe_harbor is RegimeStatus.IN_SCOPE
    assert xwalk.hipaa_expert_determination is RegimeStatus.IN_SCOPE
    # Untagged regimes are out-of-scope-of-dataset, not a compliance verdict.
    assert xwalk.gdpr is RegimeStatus.OUT_OF_SCOPE
    assert xwalk.ccpa_deidentified is RegimeStatus.OUT_OF_SCOPE
    assert xwalk.pci_dss is RegimeStatus.OUT_OF_SCOPE
    assert RegimeStatus.OUT_OF_SCOPE.value == "out_of_scope_of_dataset"

    # Status values are signals, not booleans.
    cols = as_columns({"regulatory_domains": ["hipaa"]})
    assert cols["reg_hipaa_safe_harbor"] == "in_scope"
    assert cols["reg_gdpr"] == "out_of_scope_of_dataset"
    assert True not in cols.values() and "true" not in cols.values()

    # The disclaimer is non-empty and states it informs but does not determine.
    assert xwalk.disclaimer.strip()
    assert CROSSWALK_DISCLAIMER.strip()
    # __post_init__ rejects an empty/whitespace disclaimer (the disclaimer is non-strippable).
    with pytest.raises(ValueError):
        RegulatoryCrosswalk(
            gdpr=RegimeStatus.OUT_OF_SCOPE,
            hipaa_safe_harbor=RegimeStatus.OUT_OF_SCOPE,
            hipaa_expert_determination=RegimeStatus.OUT_OF_SCOPE,
            ccpa_deidentified=RegimeStatus.OUT_OF_SCOPE,
            pci_dss=RegimeStatus.OUT_OF_SCOPE,
            other_regimes=(),
            disclaimer="   ",
        )
    low = CROSSWALK_DISCLAIMER.lower()
    assert "inform" in low
    assert ("does not make" in low) or ("not make" in low and "determination" in low)
    assert "determination" in low

    # Empty regulatory_domains → all out-of-scope, still no determination raised.
    empty = crosswalk_record({"regulatory_domains": []})
    assert all(getattr(empty, r) is RegimeStatus.OUT_OF_SCOPE for r in REGIMES)
    missing = crosswalk_record({})  # absent key behaves as no tags
    assert all(getattr(missing, r) is RegimeStatus.OUT_OF_SCOPE for r in REGIMES)


def test_fr_022_corpus_tag_mapping() -> None:
    """Real corpus tags map correctly; non-FR-022 tags are surfaced, not folded — [UNIT-TEST].

    ``gdpr``→``reg_gdpr``; ``hipaa``→BOTH HIPAA columns; ``ccpa``→``reg_ccpa_deidentified``;
    ``pci_dss``→``reg_pci_dss``. ``sox`` / ``lgpd`` / ``pipa`` are NOT FR-022-named regimes — they
    appear in ``other_regimes`` and NEVER silently become a named FR-022 column.
    """
    assert as_columns({"regulatory_domains": ["gdpr"]})["reg_gdpr"] == "in_scope"

    hip = as_columns({"regulatory_domains": ["hipaa"]})
    assert hip["reg_hipaa_safe_harbor"] == "in_scope"
    assert hip["reg_hipaa_expert_determination"] == "in_scope"

    assert as_columns({"regulatory_domains": ["ccpa"]})["reg_ccpa_deidentified"] == "in_scope"
    assert as_columns({"regulatory_domains": ["pci_dss"]})["reg_pci_dss"] == "in_scope"

    # Non-FR-022 corpus tags: surfaced via other_regimes, never folded into a named regime.
    for tag in ("sox", "lgpd", "pipa"):
        xwalk = crosswalk_record({"regulatory_domains": [tag]})
        assert tag in xwalk.other_regimes
        # None of the 5 named columns flipped on from a non-FR-022 tag.
        assert all(getattr(xwalk, r) is RegimeStatus.OUT_OF_SCOPE for r in REGIMES)
        # And no smuggled-in named column for the non-FR-022 tag.
        assert f"reg_{tag}" not in as_columns({"regulatory_domains": [tag]})

    # Mixed: a real multi-regime record keeps each regime independent + surfaces sox.
    mixed = crosswalk_record({"regulatory_domains": ["gdpr", "hipaa", "pci_dss", "sox"]})
    assert mixed.gdpr is RegimeStatus.IN_SCOPE
    assert mixed.hipaa_safe_harbor is RegimeStatus.IN_SCOPE
    assert mixed.hipaa_expert_determination is RegimeStatus.IN_SCOPE
    assert mixed.pci_dss is RegimeStatus.IN_SCOPE
    assert mixed.ccpa_deidentified is RegimeStatus.OUT_OF_SCOPE
    assert "sox" in mixed.other_regimes
    # other_regimes never contains an FR-022-named tag.
    assert not any(t in {"gdpr", "hipaa", "ccpa", "pci_dss"} for t in mixed.other_regimes)


def test_fr_022_nfr004_crosswalk_pure_stdlib() -> None:
    """AST guard (NFR-004 / AX-002): crosswalk.py imports no nondeterminism — [PROPERTY-TEST].

    The module imports none of {random, time, uuid, datetime, secrets} — pure-stdlib.
    """
    src = pathlib.Path(crosswalk_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)

    banned = {"random", "time", "uuid", "datetime", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), (
        f"crosswalk.py imports nondeterministic modules: {sorted(banned & imported)}"
    )
