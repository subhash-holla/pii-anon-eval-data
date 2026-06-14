"""Legally-distinct regulatory crosswalk (FR-022 / gov-02).

Given a record's ``regulatory_domains`` tags, emit **N separate, legally-distinct, typed regime
columns**. Five regimes are named and independently addressable:

* ``reg_gdpr`` — EU General Data Protection Regulation,
* ``reg_hipaa_safe_harbor`` — HIPAA de-identification §164.514(b)(2) (Safe-Harbor: the 18
  identifier categories removed),
* ``reg_hipaa_expert_determination`` — HIPAA de-identification §164.514(b)(1) (Expert
  Determination: statistical), and
* ``reg_ccpa_deidentified`` — CCPA/CPRA "deidentified" criteria,
* ``reg_pci_dss`` — PCI-DSS cardholder-data scope.

**No merged verdict (gov-02, load-bearing).** HIPAA is TWO columns because §164.514(b)(2) and
§164.514(b)(1) are two *different legal standards*; they are never collapsed into one HIPAA cell.
There is DELIBERATELY no merged-verdict field or column — neither a cross-regime roll-up, an
"is-this-record-OK" boolean, nor a bare de-identification flag — and no cross-regime equivalence
is implied. The v1.3.0 ``scripts/export_parquet.py:54`` behaviour — flattening
``regulatory_domains`` into a single JSON blob column — is REJECTED, not inherited.

**Tag presence is a SIGNAL, not a determination.** A regime column is :attr:`RegimeStatus.IN_SCOPE`
iff a mapping tag is present on the record (its subject-matter applies); otherwise it is
:attr:`RegimeStatus.OUT_OF_SCOPE` (``"out_of_scope_of_dataset"`` — explicitly NOT a pass/fail
adequacy verdict). The :data:`CROSSWALK_DISCLAIMER` states the crosswalk *informs but does not
make* a compliance determination.

Real corpus tags are lowercase ``{gdpr, ccpa, hipaa, pci_dss, sox, lgpd, pipa}``. ``hipaa`` fans
out to BOTH HIPAA columns. ``sox`` / ``lgpd`` / ``pipa`` are NOT FR-022-named regimes — they are
surfaced via :attr:`RegulatoryCrosswalk.other_regimes`, NEVER folded into a named regime column.

Pure-stdlib (NFR-004); deterministic (no RNG/clock — AX-002).
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, fields
from enum import Enum

# FR-022's five named regimes — ordered, independently addressable. Each backs one typed column
# ``reg_<regime>``. HIPAA's two legal de-identification methods are two SEPARATE regimes.
REGIMES: tuple[str, ...] = (
    "gdpr",
    "hipaa_safe_harbor",
    "hipaa_expert_determination",
    "ccpa_deidentified",
    "pci_dss",
)

# The disclaimer is non-strippable proof that a regime column is a SIGNAL, not a determination.
CROSSWALK_DISCLAIMER: str = (
    "This regulatory crosswalk maps dataset regulatory-domain tags to a per-record regime "
    "IN-SCOPE signal. It INFORMS but does NOT MAKE a compliance determination, and regimes are "
    "kept legally distinct — no cross-regime equivalence (gov-02 / FR-022)."
)


class RegimeStatus(str, Enum):
    """Per-record, per-regime scope SIGNAL — deliberately NOT a compliance verdict.

    :attr:`IN_SCOPE` means the regime's subject-matter applies to this record (a mapping tag is
    present); :attr:`OUT_OF_SCOPE` (``"out_of_scope_of_dataset"``) means the dataset carries no
    such tag — it is explicitly NOT a pass/fail adequacy or "determined" verdict.
    """

    IN_SCOPE = "in_scope"
    OUT_OF_SCOPE = "out_of_scope_of_dataset"


# Corpus tag -> the FR-022 regime column(s) it puts IN_SCOPE. ``hipaa`` maps to BOTH HIPAA legal
# methods. Tags absent here (sox / lgpd / pipa) are surfaced via ``other_regimes``, never folded.
_TAG_TO_REGIMES: dict[str, tuple[str, ...]] = {
    "gdpr": ("gdpr",),
    "hipaa": ("hipaa_safe_harbor", "hipaa_expert_determination"),
    "ccpa": ("ccpa_deidentified",),
    "pci_dss": ("pci_dss",),
}


@dataclass(frozen=True)
class RegulatoryCrosswalk:
    """A record's per-regime scope signals — five legally-distinct fields, no merged verdict.

    The five ``RegimeStatus`` fields are kept legally distinct (gov-02): there is DELIBERATELY no
    merged / equivalence / flattened verdict field. ``other_regimes`` surfaces non-FR-022 corpus
    tags (sox / lgpd / pipa) WITHOUT folding them into a named regime. Frozen → an immutable,
    hashable reporting value the exporter (S5-02) and bundle (S5-06) can safely share.
    """

    gdpr: RegimeStatus
    hipaa_safe_harbor: RegimeStatus
    hipaa_expert_determination: RegimeStatus
    ccpa_deidentified: RegimeStatus
    pci_dss: RegimeStatus
    other_regimes: tuple[str, ...]
    disclaimer: str = CROSSWALK_DISCLAIMER
    # DELIBERATELY no merged-verdict field (gov-02 / FR-022).

    def __post_init__(self) -> None:
        if not self.disclaimer.strip():
            raise ValueError("crosswalk disclaimer required")

    def as_dict(self) -> dict[str, object]:
        """Serialise to a plain dict — regime statuses as their string values, plus metadata.

        The five regimes stay separate keys; ``other_regimes`` and ``disclaimer`` round out the
        record. No merged-verdict key is ever produced.
        """
        out: dict[str, object] = {regime: getattr(self, regime).value for regime in REGIMES}
        out["other_regimes"] = list(self.other_regimes)
        out["disclaimer"] = self.disclaimer
        return out


def _record_tags(record: Mapping[str, object]) -> tuple[str, ...]:
    """Normalised, order-preserving, de-duplicated regulatory-domain tags from a record."""
    raw = record.get("regulatory_domains") or []
    if not isinstance(raw, Iterable) or isinstance(raw, (str, bytes)):
        return ()
    seen: dict[str, None] = {}
    for tag in raw:
        key = str(tag).strip().lower()
        if key:
            seen.setdefault(key, None)
    return tuple(seen)


def crosswalk_record(record: Mapping[str, object]) -> RegulatoryCrosswalk:
    """Crosswalk one record's tags to per-regime scope signals.

    Each FR-022 regime is :attr:`RegimeStatus.IN_SCOPE` iff a tag mapping to it
    (:data:`_TAG_TO_REGIMES`) is present; otherwise :attr:`RegimeStatus.OUT_OF_SCOPE`. Non-FR-022
    tags (sox / lgpd / pipa) are surfaced in ``other_regimes`` — never folded into a named regime.
    """
    tags = _record_tags(record)

    in_scope: set[str] = set()
    other: list[str] = []
    for tag in tags:
        mapped = _TAG_TO_REGIMES.get(tag)
        if mapped is None:
            other.append(tag)  # non-FR-022 tag: surfaced, not folded
        else:
            in_scope.update(mapped)

    def status(regime: str) -> RegimeStatus:
        return RegimeStatus.IN_SCOPE if regime in in_scope else RegimeStatus.OUT_OF_SCOPE

    return RegulatoryCrosswalk(
        gdpr=status("gdpr"),
        hipaa_safe_harbor=status("hipaa_safe_harbor"),
        hipaa_expert_determination=status("hipaa_expert_determination"),
        ccpa_deidentified=status("ccpa_deidentified"),
        pci_dss=status("pci_dss"),
        other_regimes=tuple(other),
    )


def as_columns(record: Mapping[str, object]) -> dict[str, str]:
    """The five typed Parquet columns ``{"reg_<regime>": <status value>}`` for a record.

    Exactly five keys, ordered per :data:`REGIMES`, each value a :class:`RegimeStatus` string —
    legally distinct, no merged column (gov-02). This is the surface the exporter (S5-02) writes.
    """
    xwalk = crosswalk_record(record)
    return {f"reg_{regime}": getattr(xwalk, regime).value for regime in REGIMES}


# Structural invariant: the dataclass exposes exactly the five named regimes + other_regimes +
# disclaimer, and nothing that would constitute a merged / flattened verdict field.
assert tuple(f.name for f in fields(RegulatoryCrosswalk))[:5] == REGIMES
