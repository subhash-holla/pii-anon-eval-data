#!/usr/bin/env python3
"""Two-tier version-drift guard (v2.1.0).

Tier 1 (content) must equal pyproject.toml's version. Tier 2 (publication metadata + DOI) must
carry the last ARCHIVED version (no Zenodo re-mint this phase). Exit 1 on any drift.

The Tier-2 check is FIELD-LEVEL, not a whole-file substring scan:
- CITATION.cff:  the ``version:`` field line
- CITATION.bib:  the ``version = {...}`` field line
- .zenodo.json:  the ``"version":`` JSON key
- release/citation.py: the CITATION_METADATA ``"version"`` key (it GENERATES the cff/bib/croissant, so it
  tracks the archived release, not the working content version)

This means a prose note like "v2.1.0 is a working/unarchived version" in those files does NOT
trip the guard, because we assert only that the version FIELD equals the archived version.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVED_VERSION = "2.2.0"  # last Zenodo-archived release; bump only when a new DOI is minted

TIER1_FILES = (
    "README.md",
    "DATASHEET.md",
    "BASELINES.md",
    "RELEASE_CHECKLIST.md",
    "scripts/validate.py",  # validator's expected per-record schema_version must track the content version
)


def _pyproject_version() -> str:
    for line in (ROOT / "pyproject.toml").read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("version") and "=" in stripped:
            val = stripped.split("=", 1)[1].strip().strip('"').strip("'")
            # Exclude lines that are not the [project] version (e.g. requires-python = ">=3.10")
            if re.fullmatch(r"\d+\.\d+\.\d+", val):
                return val
    raise SystemExit("pyproject.toml has no version line matching X.Y.Z")


def _cff_version(text: str) -> str | None:
    """Extract the ``version:`` field value from CITATION.cff content."""
    for line in text.splitlines():
        m = re.match(r'^version:\s*["\']?(\d+\.\d+\.\d+)["\']?', line.strip())
        if m:
            return m.group(1)
    return None


def _bib_version(text: str) -> str | None:
    """Extract the ``version = {...}`` field value from CITATION.bib content."""
    m = re.search(r'version\s*=\s*\{([^}]+)\}', text)
    if m:
        return m.group(1).strip()
    return None


def _zenodo_version(text: str) -> str | None:
    """Extract the ``"version"`` key value from .zenodo.json content."""
    try:
        data = json.loads(text)
        val = data.get("version")
        return str(val) if val is not None else None
    except json.JSONDecodeError:
        return None


def _pycitation_version(text: str) -> str | None:
    """Extract the CITATION_METADATA ``"version"`` value from release/citation.py."""
    m = re.search(r'"version":\s*"(\d+\.\d+\.\d+)"', text)
    return m.group(1) if m else None


_TIER2_EXTRACTORS = {
    "CITATION.cff": _cff_version,
    "CITATION.bib": _bib_version,
    ".zenodo.json": _zenodo_version,
    "src/pii_anon_datasets/release/citation.py": _pycitation_version,
}


def main() -> int:
    content = _pyproject_version()
    errs: list[str] = []

    # Tier-1: content version must appear somewhere in the file
    for rel in TIER1_FILES:
        text = (ROOT / rel).read_text()
        if content not in text:
            errs.append(f"TIER1 {rel}: missing content version {content!r}")

    # Tier-2: version FIELD must equal the archived version (field-level, not whole-file substring)
    for rel, extractor in _TIER2_EXTRACTORS.items():
        text = (ROOT / rel).read_text()
        found = extractor(text)
        if found is None:
            errs.append(f"TIER2 {rel}: could not locate version field")
        elif found != ARCHIVED_VERSION:
            errs.append(
                f"TIER2 {rel}: version field is {found!r}, expected archived {ARCHIVED_VERSION!r}"
                " (no DOI re-mint this phase)"
            )

    if errs:
        print("\n".join(errs), file=sys.stderr)
        return 1

    print(f"version sync OK: content={content}, archived={ARCHIVED_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
