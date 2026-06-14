"""Documentation-drift enforcement (NFR-013; S5-07).

Pins the doc-currency invariant so the record-count / annotation-count /
entity-type-count / version cannot drift across the 7 project docs again.

The canonical entity-type count is derived from ``taxonomy.ENTITY_TYPE_COUNT``
(the single source of truth, DC-02 / M1) — NOT a hardcoded 63 — wherever the
registry can supply it. The record/annotation/version constants mirror
``data/pii_anon.metadata.json``.

All six tests carry the ``nfr_013`` token so ``pytest -k nfr_013`` selects them.
[PROPERTY-TEST]
"""
from __future__ import annotations

import re
from pathlib import Path

from pii_anon_datasets import taxonomy as tx

# Repo root: tests/ -> repo root (two parents up from this file's directory).
_REPO_ROOT = Path(__file__).resolve().parent.parent

# Canonical constants (record/annotation/version come from metadata.json;
# the entity count is the registry's single source of truth).
CANONICAL_ENTITY_COUNT = tx.ENTITY_TYPE_COUNT  # == 63, derived — never hardcoded here
CANONICAL_RECORDS = "575,604"
CANONICAL_ANNOTATIONS = "2,486,438"
CANONICAL_VERSION = "2.0.0"
# License is part of the public contract: the corpus is public-domain CC0-1.0 (CITATION.cff / metadata.json /
# CONTRIBUTING), the code Apache-2.0. A CC-BY claim wrongly requires attribution and contradicts CC0 — pin it.
CANONICAL_DATA_LICENSE = "CC0"
CANONICAL_CODE_LICENSE = "Apache"


def _read(name: str) -> str:
    """Read a repo doc by path relative to the repo root."""
    return (_REPO_ROOT / name).read_text(encoding="utf-8")


# Entity-type-shaped token: an all-caps (A-Z, optionally with digits/underscores)
# identifier of length >= 2. This matches both multi-segment names (PERSON_NAME)
# and single-word canonical types (AGE, URL, CVV, PIN, IBAN). The taxonomy test
# restricts these to backticked occurrences (the type column) before comparing to
# the registry, so common English words elsewhere in the prose are not over-matched.
_UPPER_SNAKE = re.compile(r"\b[A-Z][A-Z0-9_]{1,}\b")


def test_nfr_013_docs_use_canonical_record_count() -> None:
    """README/DATASHEET/COMPARISON carry the canonical 575,604 and no stale count."""
    stale = ["117,752", "919,000", "150K+ records", "~1.24M", "1.24M"]
    for doc in ("README.md", "DATASHEET.md", "COMPARISON.md"):
        text = _read(doc)
        assert CANONICAL_RECORDS in text, f"{doc} missing canonical record count {CANONICAL_RECORDS}"
        for needle in stale:
            assert needle not in text, f"{doc} still contains stale record-count string {needle!r}"


def test_nfr_013_docs_use_canonical_entity_count() -> None:
    """README/DATASHEET/COMPARISON/__init__ reflect the registry count; no stale 65/57."""
    count = str(CANONICAL_ENTITY_COUNT)  # derived from taxonomy.ENTITY_TYPE_COUNT
    stale = ["65 entity types", "65 types", "57 entity types", "57 types"]
    for doc in (
        "README.md",
        "DATASHEET.md",
        "COMPARISON.md",
        "src/pii_anon_datasets/__init__.py",
    ):
        text = _read(doc)
        assert count in text, f"{doc} missing canonical entity-type count {count}"
        for needle in stale:
            assert needle not in text, f"{doc} still contains stale entity-count string {needle!r}"


def test_nfr_013_doc_titles_are_v2() -> None:
    """DATASHEET/COMPARISON titles/headers declare v2.0.0, not v1.1.0 / v1.3.0."""
    for doc in ("DATASHEET.md", "COMPARISON.md"):
        text = _read(doc)
        assert CANONICAL_VERSION in text, f"{doc} does not declare canonical version {CANONICAL_VERSION}"
        # The header/title line must not advertise a stale dataset version.
        first_lines = "\n".join(text.splitlines()[:12])
        assert "v1.1.0" not in first_lines, f"{doc} header still declares v1.1.0"
        assert "v1.3.0" not in first_lines, f"{doc} header still declares v1.3.0"
        assert "v1.3 " not in first_lines and not first_lines.rstrip().endswith("v1.3"), (
            f"{doc} header still declares v1.3"
        )


def test_nfr_013_taxonomy_body_matches_registry() -> None:
    """TAXONOMY.md's canonical table is EXACTLY the 63 registry types (no orphan/extra rows)."""
    text = _read("TAXONOMY.md")
    # Entity-type tokens that appear in `backtick` code spans are the table's type column.
    tokens = {m.group(0) for m in _UPPER_SNAKE.finditer(text)}
    registry = set(tx.CANONICAL_ENTITY_TYPES)
    # Restrict to entity-type-shaped tokens that name a row in the type column (backticked).
    backticked = {t for t in tokens if f"`{t}`" in text}
    extra = backticked - registry
    missing = registry - backticked
    assert not extra, f"TAXONOMY.md lists non-canonical entity rows: {sorted(extra)}"
    assert not missing, f"TAXONOMY.md is missing canonical registry types: {sorted(missing)}"


def test_nfr_013_migration_has_v2_section() -> None:
    """MIGRATION.md has a v1.3.0 -> v2.0.0 section mentioning the key v2 schema moves."""
    text = _read("MIGRATION.md")
    has_section = bool(
        re.search(r"v?1\.3\.0\s*(?:→|->|to)\s*v?2\.0\.0", text)
        or re.search(r"v?1\.3\.0\s*(?:→|->|to)\s*2\.0\.0", text)
    )
    assert has_section, "MIGRATION.md has no 'v1.3.0 -> v2.0.0' section"
    assert "tier3_evaluation" in text, "MIGRATION v2 section must mention tier3_evaluation"
    assert "record_id" in text, "MIGRATION v2 section must mention content-addressed record_id"
    assert "compat.to_v1_record" in text, "MIGRATION v2 section must mention compat.to_v1_record"


def test_nfr_013_changelog_has_spwr_entry() -> None:
    """CHANGELOG.md has an S-PWR / power-enrichment entry under 2.0.0."""
    text = _read("CHANGELOG.md")
    # Scope to the 2.0.0 section (from its heading to the next version heading).
    after = text.split("## [2.0.0]", 1)
    assert len(after) == 2, "CHANGELOG.md has no [2.0.0] section"
    body = after[1].split("## [1.3.0]", 1)[0]
    assert CANONICAL_RECORDS in body, "CHANGELOG 2.0.0 section must mention canonical 575,604"
    assert "synthetic_lattice_enrichment" in body, (
        "CHANGELOG 2.0.0 section must mention synthetic_lattice_enrichment (S-PWR)"
    )


def test_nfr_013_docs_declare_canonical_license() -> None:
    """README + DATASHEET declare data=CC0 + code=Apache with NO ambiguating CC-BY claim.

    The corpus is public-domain CC0-1.0 (CITATION.cff / metadata.json / CONTRIBUTING all agree); a
    "CC0 / CC-BY-4.0" claim is self-contradictory (CC-BY requires attribution, CC0 does not) and must not
    appear in PII-Anon's own docs. (COMPARISON.md is excluded — its CC-BY entries are COMPETITORS' licenses.)
    """
    for doc in ("README.md", "DATASHEET.md"):
        text = _read(doc)
        assert CANONICAL_DATA_LICENSE in text, f"{doc} must declare the data license {CANONICAL_DATA_LICENSE}-1.0"
        assert CANONICAL_CODE_LICENSE in text, f"{doc} must declare the code license {CANONICAL_CODE_LICENSE}-2.0"
        for needle in ("CC-BY", "CC BY"):
            assert needle not in text, (
                f"{doc} contains an ambiguating {needle} license claim; the data is CC0-1.0 (public domain, "
                "no attribution required) — see CITATION.cff / pii_anon.metadata.json"
            )


def test_nfr_013_baselines_doc_carries_synthetic_only_honesty() -> None:
    """The baseline leaderboard docs cannot shed their honesty: BASELINES.md carries the non-strippable
    synthetic-only caveat (AX-001), discloses external-validity as the limit, uses the canonical 63-type
    taxonomy count + the recall-weighted F2 rationale, and introduces no ambiguating CC-BY claim. README +
    DATASHEET link to it and keep the synthetic-only framing."""
    bl = _read("BASELINES.md")
    assert "AX-001" in bl and "synthetic" in bl.lower(), "BASELINES.md must carry the synthetic-only caveat"
    assert "external validity" in bl.lower(), "BASELINES.md must disclose external-validity as the limit"
    assert str(CANONICAL_ENTITY_COUNT) in bl, "BASELINES.md must use the canonical 63-type taxonomy count"
    assert "F2" in bl, "BASELINES.md must state the recall-weighted F2 rationale"
    for needle in ("CC-BY", "CC BY"):
        assert needle not in bl, f"BASELINES.md contains an ambiguating {needle} claim"
    for doc in ("README.md", "DATASHEET.md"):
        text = _read(doc)
        assert "BASELINES.md" in text, f"{doc} must link to the canonical baseline leaderboard"
        assert "synthetic" in text.lower(), f"{doc} baseline section must carry the synthetic-only framing"
