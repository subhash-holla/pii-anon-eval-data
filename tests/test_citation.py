"""C6 — DOI / citation release packaging + claims policy (FR-054 / DC-31; cycle-1 FR-028).

Guards the HONESTY invariant: the Zenodo DOI is minted by a human LATER, so the doi field is
an explicit ``PENDING`` sentinel and ``validate_no_fake_doi`` forbids a fabricated ``10.x`` DOI.
Also pins the canonical v2.0.0 / CC0 facts and the synthetic-only (AX-001/003) ceiling caveat
into the emitted CITATION.cff + CITATION.bib + CLAIMS_POLICY.md.
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


def test_doi_pending_is_explicit_sentinel_not_a_real_doi() -> None:
    assert DOI_PENDING == "PENDING-ZENODO-MINT"
    # the sentinel must NOT look like a minted DOI
    assert not DOI_PENDING.startswith("10.")
    assert CITATION_METADATA["doi"] == DOI_PENDING


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
    # the DOI line must carry the PENDING sentinel, never a fabricated 10.x DOI
    assert DOI_PENDING in cff
    assert "10.1234" not in cff
    assert "Holla" in cff


def test_render_bibtex_misc_entry_carries_pending_doi() -> None:
    bib = render_bibtex()
    assert bib.lstrip().startswith("@misc")
    assert "2.0.0" in bib
    assert "CC0" in bib
    # DOI is pending — the note must say so, and no fake DOI may appear
    assert DOI_PENDING in bib
    assert "10.1234" not in bib


def test_claims_policy_states_synthetic_ceiling_and_what_it_does_not_support() -> None:
    assert "synthetic" in CLAIMS_POLICY.lower()
    assert "AX-001" in CLAIMS_POLICY
    # must explicitly bound the claim: not external validity / not a standalone recall claim
    low = CLAIMS_POLICY.lower()
    assert "external validity" in low
    assert "does not" in low or "not a" in low


def test_validate_no_fake_doi_passes_for_pending_default() -> None:
    # default state (pending) must be accepted, returns None
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
    assert DOI_PENDING in cff and DOI_PENDING in bib
