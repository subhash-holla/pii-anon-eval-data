"""Per-ENTITY-TYPE regulatory taxonomy crosswalk (FR-053 / DC-30).

C5 — extends the cycle-1 record-tag crosswalk (``compliance.crosswalk``, FR-022 / gov-02) DOWN
to the per-entity-type level and ADDS GLBA. Each of the canonical **63** entity types
(``taxonomy.ENTITY_REGISTRY`` — derived, never a stale hand-list so it cannot drift; DC-02/M1)
maps to a record of FIVE SEPARATE, legally-distinct regime fields:

* ``gdpr`` — EU GDPR material scope (the type is, on its face, personal data),
* ``gdpr_art9_special_category`` — GDPR Art-9 "special category" (health / biometric / genetic /
  racial-or-ethnic / political / religious-or-philosophical / sex-life),
* ``hipaa_phi`` — HIPAA Protected Health Information (a health-context identifier),
* ``ccpa`` — CCPA/CPRA "personal information",
* ``glba_nonpublic_personal_info`` — GLBA nonpublic personal information (financial).

**No merged verdict (mirrors AX-004 separation + gov-02, load-bearing).** There is DELIBERATELY
no ``overall`` / ``deidentified`` / ``compliant`` / ``equivalent`` roll-up — the five regimes are
legally distinct and NO cross-regime equivalence is implied. A flag is an IN-SCOPE / special-
category **SIGNAL** about the type's subject-matter, NOT a per-record compliance *determination*;
the non-strippable :data:`CROSSWALK_DISCLAIMER` says exactly that (and :class:`EntityCrosswalkBundle`
cannot be constructed with an empty disclaimer — mirrors ``scoring.detection.DesignProvenance`` /
``assessment.manifest.ASSESSMENT_CAVEAT``).

Versioned (:data:`ENTITY_REGULATORY_CROSSWALK_VERSION`) + provenance-stamped with an INJECTABLE
``generated_at`` (default fixed string) so :func:`build_entity_crosswalk` is byte-reproducible
(AX-002). Pure-stdlib (NFR-004); deterministic (no RNG / clock).
"""
from __future__ import annotations

from dataclasses import dataclass

from ..taxonomy import CANONICAL_ENTITY_TYPES, ENTITY_REGISTRY

SCHEMA = "pii-anon-entity-regulatory-crosswalk/v1"
ENTITY_REGULATORY_CROSSWALK_VERSION = "1.0.0"

# Fixed default so byte-output is reproducible absent an explicit injection (AX-002).
DEFAULT_GENERATED_AT = "1970-01-01T00:00:00Z"

# The five legally-distinct, independently-addressable regime keys (FR-053 / DC-30). ORDERED;
# the single source of truth behind every entry's keyset. DELIBERATELY contains no merged /
# roll-up verdict key (legally distinct — no cross-regime equivalence).
REGIME_KEYS: tuple[str, ...] = (
    "gdpr",
    "gdpr_art9_special_category",
    "hipaa_phi",
    "ccpa",
    "glba_nonpublic_personal_info",
)

# Non-strippable proof that each flag is a SIGNAL about subject-matter, not a determination.
CROSSWALK_DISCLAIMER: str = (
    "This per-entity-type regulatory crosswalk maps each of the 63 canonical entity types to a "
    "per-regime IN-SCOPE / special-category SIGNAL about the type's subject-matter (GDPR, GDPR "
    "Art-9, HIPAA PHI, CCPA, GLBA). It INFORMS but does NOT MAKE a compliance determination; the "
    "regimes are kept legally distinct with NO cross-regime equivalence (FR-053 / DC-30)."
)

# ── Conservative per-type legal signals (subject-matter level) ──────────────────────────────
# These are deliberately conservative subject-matter SIGNALS, not determinations.

# GDPR Art-9 "special category" data: health / genetic / biometric-for-unique-id / racial-ethnic
# / political opinions / religious-or-philosophical beliefs / sex life. (Trade-union membership is
# not a corpus type.) DERIVED set, asserted ⊆ registry below.
_ART9_SPECIAL_CATEGORY: frozenset[str] = frozenset({
    # health (medical_biological category — health-context content)
    "HEALTH_CONDITION", "HEALTH_INSURANCE_ID", "MEDICAL_RECORD_NUMBER", "MEDICATION_NAME",
    "PRESCRIPTION_NUMBER", "PROCEDURE_NAME",
    # biometric-for-unique-identification + genetic
    "BIOMETRIC_ID",
    # racial / ethnic origin
    "ETHNICITY",
    # political opinions / religious-or-philosophical beliefs
    "POLITICAL_OPINION", "RELIGIOUS_BELIEF",
})

# HIPAA PHI: health-context identifiers — the medical/biological category plus its insurance id.
# (Provider identifiers DEA/NPI identify a *provider*, not a patient, so they are NOT PHI here.)
_HIPAA_PHI: frozenset[str] = frozenset({
    "HEALTH_CONDITION", "HEALTH_INSURANCE_ID", "MEDICAL_RECORD_NUMBER", "MEDICATION_NAME",
    "PRESCRIPTION_NUMBER", "PROCEDURE_NAME",
})

# GLBA nonpublic personal information: the financial category PLUS the strong financial gov-ids
# (SSN / tax id) that a financial institution holds. Insurance-policy + invoice are financial.
_GLBA_NPI: frozenset[str] = frozenset(set(
    t for t, cat in ENTITY_REGISTRY.items() if cat == "financial"
) | {"SOCIAL_SECURITY_NUMBER", "TAX_ID"})

# GDPR / CCPA material scope: a type is, on its face, personal data EXCEPT a handful that are not
# inherently about an identified person. Conservative OUT-of-material-scope set (everything else
# is treated as IN material scope — the conservative default for an eval SIGNAL).
_NON_PERSONAL: frozenset[str] = frozenset({
    "ORGANIZATION_NAME",  # an org is not a natural person
    "URL", "INVOICE_NUMBER", "VEHICLE_MODEL", "TIMESTAMP",  # metadata, not person-identifying
})

# Validate the curated sets against the registry so a taxonomy rename fails loud (DC-02 / M1).
assert _ART9_SPECIAL_CATEGORY <= CANONICAL_ENTITY_TYPES, "Art-9 set drifted from taxonomy"
assert _HIPAA_PHI <= CANONICAL_ENTITY_TYPES, "HIPAA PHI set drifted from taxonomy"
assert _GLBA_NPI <= CANONICAL_ENTITY_TYPES, "GLBA NPI set drifted from taxonomy"
assert _NON_PERSONAL <= CANONICAL_ENTITY_TYPES, "non-personal set drifted from taxonomy"


def _entry_for(entity_type: str) -> dict[str, bool]:
    """The 5 legally-distinct regime SIGNALS for one entity type — ORDERED per REGIME_KEYS.

    Conservative subject-matter mapping (a signal, not a determination): personal-on-its-face
    types are GDPR + CCPA in-scope; Art-9 / HIPAA / GLBA fire from the curated sets above.
    """
    personal = entity_type not in _NON_PERSONAL
    return {
        "gdpr": personal,
        "gdpr_art9_special_category": entity_type in _ART9_SPECIAL_CATEGORY,
        "hipaa_phi": entity_type in _HIPAA_PHI,
        "ccpa": personal,
        "glba_nonpublic_personal_info": entity_type in _GLBA_NPI,
    }


@dataclass(frozen=True)
class EntityCrosswalkBundle:
    """The assembled crosswalk — versioned, provenance-stamped, non-strippable disclaimer.

    Carries the disclaimer so a built crosswalk cannot lose its "signal not determination"
    status (cannot be constructed with an empty disclaimer). Frozen → an immutable reporting
    value. DELIBERATELY no merged-verdict field (FR-053 / DC-30)."""

    version: str
    provenance: dict[str, str]
    entries: dict[str, dict[str, bool]]
    disclaimer: str = CROSSWALK_DISCLAIMER

    def __post_init__(self) -> None:
        if not self.disclaimer or not self.disclaimer.strip():
            raise ValueError(
                "EntityCrosswalkBundle requires a non-empty signal-not-determination "
                "disclaimer (FR-053 / DC-30)."
            )

    def as_dict(self) -> dict[str, object]:
        """Serialise to a plain dict; the five regime keys stay separate, no merged-verdict key."""
        return {
            "schema": SCHEMA,
            "version": self.version,
            "disclaimer": self.disclaimer,
            "provenance": dict(self.provenance),
            "entries": {t: dict(e) for t, e in self.entries.items()},
        }


def build_entity_crosswalk(*, generated_at: str = DEFAULT_GENERATED_AT) -> dict[str, object]:
    """Build the per-entity-type crosswalk over EXACTLY the canonical 63 taxonomy types.

    Returns ``{schema, version, disclaimer, provenance, entries:{type: {<5 regime keys>}}}``. The
    entries are derived from ``taxonomy.ENTITY_REGISTRY`` (never a stale list); ``generated_at`` is
    injectable (default fixed) so the serialised output is byte-reproducible (AX-002). No merged
    cross-regime verdict is ever produced (FR-053 / DC-30)."""
    entries = {etype: _entry_for(etype) for etype in sorted(CANONICAL_ENTITY_TYPES)}
    provenance = {
        "version": ENTITY_REGULATORY_CROSSWALK_VERSION,
        "source": "taxonomy.ENTITY_REGISTRY (63 canonical types) + FR-053/DC-30 legal mapping",
        "generated_at": generated_at,
    }
    bundle = EntityCrosswalkBundle(
        version=ENTITY_REGULATORY_CROSSWALK_VERSION,
        provenance=provenance,
        entries=entries,
    )
    return bundle.as_dict()


# Structural invariant: the entry keyset is EXACTLY the five legally-distinct regimes, and nothing
# that would constitute a merged / flattened cross-regime verdict (FR-053 / DC-30).
assert tuple(_entry_for(next(iter(CANONICAL_ENTITY_TYPES)))) == REGIME_KEYS
