"""Release packaging — frictionless citation + an honest claims policy (FR-054 / DC-31).

Closes cycle-1 FR-028 (frictionless citation): emits CITATION.cff (CFF 1.2.0) + a BibTeX
``@misc`` entry from a single Python dict (NFR-050 — no YAML library; the CFF is emitted as
YAML *text*). HONESTY invariant: the Zenodo DOI is minted by a HUMAN later, so the doi field is
an explicit ``PENDING`` sentinel and :func:`citation.validate_no_fake_doi` forbids a fabricated DOI.
The claims policy reuses the synthetic-only AX-001/003 ceiling caveat (see
``scoring.detection.DESIGN_CAVEAT``).
"""
from __future__ import annotations

__all__: list[str] = []
