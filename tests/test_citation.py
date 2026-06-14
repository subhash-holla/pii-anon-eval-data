"""C6 — DOI / citation release packaging + claims policy (FR-054 / DC-31; cycle-1 FR-028).

Guards the HONESTY invariant: a fabricated ``10.x`` DOI may never be smuggled in
(``validate_no_fake_doi``). The Zenodo DOI was minted by a human on deposit, so the doi field now
carries the real ``10.5281/zenodo.<digits>`` value (it was the explicit ``PENDING`` sentinel before
minting). Also pins the canonical v2.0.0 / CC0 facts and the synthetic-only (AX-001/003) ceiling
caveat into the emitted CITATION.cff + CITATION.bib + CLAIMS_POLICY.md.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from pii_anon_datasets.release.citation import (
    CITATION_METADATA,
    CLAIMS_POLICY,
    DOI_PENDING,
    render_bibtex,
    render_citation_cff,
    validate_no_fake_doi,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# The real Zenodo DOI minted for v2.0.0 (replaced the PENDING sentinel on deposit).
MINTED_DOI = "10.5281/zenodo.20690979"


def test_doi_is_minted_real_doi_off_the_sentinel() -> None:
    # the sentinel constant is unchanged and still does NOT look like a minted DOI
    assert DOI_PENDING == "PENDING-ZENODO-MINT"
    assert not DOI_PENDING.startswith("10.")
    # DOI now MINTED: metadata carries the real Zenodo DOI, no longer the sentinel
    assert CITATION_METADATA["doi"] == MINTED_DOI
    assert CITATION_METADATA["doi"] != DOI_PENDING
    # and the real DOI still passes the anti-fabrication guard
    assert validate_no_fake_doi(CITATION_METADATA) is None


def test_metadata_pins_canonical_version_and_license() -> None:
    assert CITATION_METADATA["version"] == "2.0.0"
    assert CITATION_METADATA["license"] == "CC0-1.0"
    # author + repo provenance present
    assert "Holla" in str(CITATION_METADATA["authors"])
    assert "github.com/subhash-holla/pii-anon-eval-data" in CITATION_METADATA["repo"]


def test_render_citation_cff_is_valid_cff_text_with_pinned_facts() -> None:
    cff = render_citation_cff()
    assert "cff-version: 1.2.0" in cff
    assert 'version: "2.0.0"' in cff or "version: 2.0.0" in cff
    assert "CC0-1.0" in cff
    # the DOI line must carry the real minted DOI, the sentinel must be gone, no fabricated 10.x
    assert MINTED_DOI in cff
    assert DOI_PENDING not in cff
    assert "10.1234" not in cff
    assert "Holla" in cff


def test_render_bibtex_misc_entry_carries_minted_doi() -> None:
    bib = render_bibtex()
    assert bib.lstrip().startswith("@misc")
    assert "2.0.0" in bib
    assert "CC0" in bib
    # DOI is minted — the note must carry the real DOI, the sentinel must be gone, no fake DOI
    assert MINTED_DOI in bib
    assert DOI_PENDING not in bib
    assert "10.1234" not in bib


def test_claims_policy_states_synthetic_ceiling_and_what_it_does_not_support() -> None:
    assert "synthetic" in CLAIMS_POLICY.lower()
    assert "AX-001" in CLAIMS_POLICY
    # must explicitly bound the claim: not external validity / not a standalone recall claim
    low = CLAIMS_POLICY.lower()
    assert "external validity" in low
    assert "does not" in low or "not a" in low


def test_validate_no_fake_doi_passes_for_minted_default() -> None:
    # default state (now the real minted DOI) must be accepted, returns None
    assert validate_no_fake_doi() is None
    assert validate_no_fake_doi(CITATION_METADATA) is None


def test_validate_no_fake_doi_raises_on_fabricated_doi() -> None:
    forged = {**CITATION_METADATA, "doi": "10.1234/fake"}
    with pytest.raises(ValueError):
        validate_no_fake_doi(forged)


def test_repo_root_artifacts_exist_and_are_nonempty() -> None:
    for name in ("CITATION.cff", "CLAIMS_POLICY.md", "CITATION.bib"):
        p = REPO_ROOT / name
        assert p.is_file(), f"{name} missing at repo root"
        assert p.read_text(encoding="utf-8").strip(), f"{name} is empty"


def test_repo_root_artifacts_match_generators() -> None:
    cff = (REPO_ROOT / "CITATION.cff").read_text(encoding="utf-8")
    bib = (REPO_ROOT / "CITATION.bib").read_text(encoding="utf-8")
    claims = (REPO_ROOT / "CLAIMS_POLICY.md").read_text(encoding="utf-8")
    assert cff == render_citation_cff()
    assert bib == render_bibtex()
    # claims file embeds the policy text (plus a heading)
    assert CLAIMS_POLICY in claims
    # honesty: no fabricated DOI leaked into any committed artifact
    assert "10.1234" not in cff and "10.1234" not in bib and "10.1234" not in claims
    # the real minted DOI is now wired into the committed citation artifacts; sentinel is gone
    assert MINTED_DOI in cff and MINTED_DOI in bib
    assert DOI_PENDING not in cff and DOI_PENDING not in bib
