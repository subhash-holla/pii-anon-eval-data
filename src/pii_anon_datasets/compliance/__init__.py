"""Compliance surface (DC-11): the legally-distinct regulatory crosswalk (FR-022 / gov-02).

This package is the single source of truth for mapping a record's ``regulatory_domains`` tags to
**N separate, legally-distinct, typed regime columns** — there is NO merged / equivalence /
flattened ``compliant`` verdict (the v1.3.0 ``export_parquet.py`` regime-flattening is fixed here,
not inherited). Both the Parquet exporter (S5-02) and the end-state bundle (S5-06) import from
:mod:`pii_anon_datasets.compliance.crosswalk`.

It also hosts the DPIA-input :mod:`~pii_anon_datasets.compliance.end_state_bundle` (S5-06 / FR-021):
an :class:`EndStateBundle` that keeps the anonymization evidence (DC-06 ``ParetoPoint``) and the
pseudonymization evidence (DC-08 ``PseudonymizationReport``) as **two SEPARATE sub-objects** — never
fused into one de-id score (NFR-005 / AX-004) — and carries the non-strippable
:data:`DPIA_DISCLAIMER`.

Pure-stdlib (NFR-004); deterministic (no RNG/clock — AX-002).
"""

from __future__ import annotations

from pii_anon_datasets.compliance.crosswalk import (
    CROSSWALK_DISCLAIMER,
    REGIMES,
    RegimeStatus,
    RegulatoryCrosswalk,
    as_columns,
    crosswalk_record,
)
from pii_anon_datasets.compliance.end_state_bundle import (
    DPIA_DISCLAIMER,
    EndStateBundle,
    assemble_end_state_bundle,
)

__all__ = [
    "CROSSWALK_DISCLAIMER",
    "DPIA_DISCLAIMER",
    "REGIMES",
    "EndStateBundle",
    "RegimeStatus",
    "RegulatoryCrosswalk",
    "as_columns",
    "assemble_end_state_bundle",
    "crosswalk_record",
]
