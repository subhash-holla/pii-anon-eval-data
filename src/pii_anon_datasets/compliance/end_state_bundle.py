"""DPIA-input end-state evidence bundle (DC-11; FR-021, supporting NFR-005/AX-004).

Assembles a **Data-Protection-Impact-Assessment INPUT** bundle for a transformation's output. It
keeps the **anonymization** evidence (DC-06 :class:`~pii_anon_datasets.scoring.anonymization.ParetoPoint`:
residual-risk ``MeasuredRRS`` + ``UtilityScore``, carrying the FR-009 anti-anonymity caveat) and the
**pseudonymization** evidence (DC-08
:class:`~pii_anon_datasets.scoring.pseudonymization.PseudonymizationReport`: reversal / collision /
referential / key-state integrity, carrying the EDPB Art 4(5) note) as **two SEPARATE sub-objects**.

LOAD-BEARING (NFR-005 / AX-004): there is DELIBERATELY no merged / combined de-id verdict, no
``__float__``, and no ``combined`` / ``overall`` / ``overall_score`` / ``deid`` /
``de_identification_score`` / ``score`` field anywhere on :class:`EndStateBundle` -- anonymity and
pseudonymity are different legal/technical properties and are never fused into one
de-identification number. The module-bottom ``assert`` enforces no forbidden name.

It surfaces the per-record regulatory crosswalk (S5-01, the N legally-distinct regime signals) and
carries a **mandatory non-strippable** :data:`DPIA_DISCLAIMER` labeling the bundle as an INPUT that
INFORMS but does NOT MAKE a determination (the same non-strippable pattern as the crosswalk: a module
constant + a non-defaulted-validated field + a ``__post_init__`` check). At least one evidence axis
must be present.

Pure-stdlib (NFR-004); deterministic (no RNG/clock -- AX-002). Imports the S5-01 crosswalk + the
DC-06/DC-08 result value objects READ-ONLY and composes them WITHOUT fusing.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields

from pii_anon_datasets.compliance.crosswalk import RegulatoryCrosswalk, crosswalk_record
from pii_anon_datasets.scoring.anonymization import ParetoPoint
from pii_anon_datasets.scoring.pseudonymization import PseudonymizationReport

# Non-strippable: the bundle is a DPIA INPUT, not a determination (FR-021).
DPIA_DISCLAIMER: str = (
    "This end-state bundle is an INPUT to a Data Protection Impact Assessment (DPIA). It INFORMS but "
    "does NOT MAKE a compliance or anonymity determination. The anonymization evidence (residual-risk "
    "+ utility) and the pseudonymization evidence (integrity) are kept SEPARATE and are never combined "
    "into a single de-identification verdict (FR-021 / NFR-005 / AX-004)."
)

# Names that would constitute a merged/fused de-id verdict -- DELIBERATELY absent (NFR-005 / AX-004).
_FORBIDDEN_MERGE_NAMES = frozenset(
    {
        "combined",
        "overall",
        "overall_score",
        "deid",
        "de_identification_score",
        "score",
    }
)


@dataclass(frozen=True)
class EndStateBundle:
    """DPIA-input bundle: anon + pseudo evidence kept SEPARATE; non-strippable disclaimer.

    DELIBERATELY exposes NO ``combined`` / ``overall`` / ``overall_score`` / ``deid`` /
    ``de_identification_score`` / ``score`` field and NO ``__float__``: the anonymization axis
    (``ParetoPoint``: residual-risk + utility, carrying the FR-009 caveat) and the pseudonymization
    axis (``PseudonymizationReport``: integrity, carrying the EDPB Art 4(5) note) are never fused
    (NFR-005 / AX-004). At least one evidence axis must be present. ``regulatory_crosswalk`` surfaces
    the N legally-distinct regime signals (S5-01).
    """

    regulatory_crosswalk: RegulatoryCrosswalk
    anonymization_evidence: ParetoPoint | None = None
    pseudonymization_evidence: PseudonymizationReport | None = None
    disclaimer: str = DPIA_DISCLAIMER

    def __post_init__(self) -> None:
        if not self.disclaimer.strip():
            raise ValueError("end-state bundle disclaimer required (FR-021 non-strippable)")
        if self.anonymization_evidence is None and self.pseudonymization_evidence is None:
            raise ValueError("end-state bundle needs at least one evidence axis (anonymization or pseudonymization)")

    def as_dict(self) -> dict[str, object]:
        """Two SEPARATE evidence sub-objects + the crosswalk + the disclaimer. No combined key.

        The anon sub-object's nested ``MeasuredRRS`` carries the FR-009 anti-anonymity caveat; the
        pseudo sub-object carries the EDPB Art 4(5) key-state note -- both travel unstripped.
        """
        return {
            "anonymization_evidence": (
                None if self.anonymization_evidence is None else self.anonymization_evidence.as_dict()
            ),
            "pseudonymization_evidence": (
                None if self.pseudonymization_evidence is None else self.pseudonymization_evidence.as_dict()
            ),
            "regulatory_crosswalk": self.regulatory_crosswalk.as_dict(),
            "disclaimer": self.disclaimer,
        }


def assemble_end_state_bundle(
    record: Mapping[str, object],
    *,
    anonymization: ParetoPoint | None = None,
    pseudonymization: PseudonymizationReport | None = None,
) -> EndStateBundle:
    """Assemble a DPIA-input bundle for ``record`` from optional anon/pseudo scorer outputs.

    The regulatory crosswalk is derived from the record's ``regulatory_domains`` tags (S5-01). At least
    one of ``anonymization`` / ``pseudonymization`` must be provided (else ``__post_init__`` raises).
    """
    return EndStateBundle(
        regulatory_crosswalk=crosswalk_record(record),
        anonymization_evidence=anonymization,
        pseudonymization_evidence=pseudonymization,
    )


# Structural invariant (NFR-005 / AX-004): the dataclass exposes none of the merged-verdict names.
assert _FORBIDDEN_MERGE_NAMES.isdisjoint({f.name for f in fields(EndStateBundle)})
