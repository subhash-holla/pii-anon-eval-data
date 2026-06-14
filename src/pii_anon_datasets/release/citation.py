"""Frictionless citation + honest claims policy (FR-054 / DC-31; closes cycle-1 FR-028).

Single source of truth = :data:`CITATION_METADATA` (a plain dict). From it we EMIT a CFF 1.2.0
file (as YAML *text* — there is no YAML library; NFR-050) and a BibTeX ``@misc`` entry. The
canonical facts (v2.0.0 / CC0-1.0 data license / 575,604 records / author Subhash Holla) are
confirmed against README.md + pyproject.toml.

HONESTY (the load-bearing invariant): the Zenodo DOI is minted by a HUMAN later. The doi field is
the explicit sentinel :data:`DOI_PENDING` — NEVER a fabricated DOI. :func:`validate_no_fake_doi`
forbids a ``10.x``-shaped value unless a genuine minted DOI is deliberately passed in.

The claims policy reuses the synthetic-only AX-001/003 ceiling caveat (mirrors
``scoring.detection.DESIGN_CAVEAT`` / ``assessment.manifest.ASSESSMENT_CAVEAT``): it states what a
result on this corpus DOES and does NOT support.
"""
from __future__ import annotations

# Explicit "not yet minted" sentinel. A real Zenodo DOI is a human deposit step performed LATER;
# until then NO 10.x string may appear anywhere in a committed citation artifact.
DOI_PENDING = "PENDING-ZENODO-MINT"

# Canonical, version-pinned citation metadata (single source). Confirmed: README.md v2.0.0 / 575,604
# records / data license CC0-1.0; pyproject.toml author "Subhash Holla" + repo URL.
CITATION_METADATA: dict = {
    "message": "If you use this dataset, please cite it using these metadata.",
    "title": (
        "PII Anonymization Evaluation Dataset: Three-Tier Synthetic Benchmark "
        "with Behavioral-Signal Annotations"
    ),
    "authors": [{"family-names": "Holla", "given-names": "Subhash"}],
    "version": "2.0.0",
    "license": "CC0-1.0",  # DATA-release license (code is Apache-2.0); this packages the corpus
    "doi": DOI_PENDING,
    "year": 2026,
    "date-released": "2026-05-28",
    "repo": "https://github.com/subhash-holla/pii-anon-eval-data",
    "url": "https://github.com/subhash-holla/pii-anon-eval-data",
    "record_count": 575604,
    "keywords": [
        "PII", "de-identification", "anonymization", "synthetic-data", "benchmark", "evaluation",
    ],
    "abstract": (
        "575,604 fully synthetic records (60 languages, 63 entity types) for evaluating PII "
        "detection, anonymization quality, and resistance to LLM-based re-identification. "
        "100% synthetic — contains NO real personal information (AX-001)."
    ),
}

# Synthetic-only / external-validity ceiling, reused from scoring.detection.DESIGN_CAVEAT. Kept as a
# literal (not imported) so the release module stays a leaf and importing it pulls in no scorer code.
_AX_CEILING_CAVEAT = (
    "Synthetic-only (AX-001): every record contains ONLY synthetic PII. A score on this corpus is "
    "statistical precision on the SYNTHETIC distribution, NOT external validity, and NOT a standalone "
    "recall claim absent the real-data correlation slice (FR-027). AX-003."
)

CLAIMS_POLICY = (
    "This dataset is a CC0 SYNTHETIC eval substrate. The following bounds what a published result "
    "computed on it may and may not claim.\n\n"
    "WHAT A RESULT DOES SUPPORT: a reproducible, version-pinned (v2.0.0) measurement of a system's "
    "PII-detection / de-identification / re-identification-resistance behaviour on a controlled "
    "synthetic distribution, with stated confidence intervals on integer-count metrics. Cell-level "
    "power is statistical precision on THAT synthetic distribution.\n\n"
    "WHAT A RESULT DOES NOT SUPPORT: " + _AX_CEILING_CAVEAT + " A number here is therefore NOT a "
    "claim of real-world recall, NOT a claim of external validity, and NOT a compliance "
    "certification. Any real-world or regulatory claim requires the separate real-data correlation "
    "slice (FR-027), which is out of scope for this release.\n\n"
    "DOI / PROVENANCE HONESTY: the archival DOI is minted by a human on deposit and is published "
    "here as the explicit sentinel '" + DOI_PENDING + "' until then; no fabricated DOI is asserted. "
    "Cite the repository URL and version until the DOI is minted."
)


def _cff_str(value: str) -> str:
    """Double-quote a scalar for YAML emission, escaping backslashes and quotes (CFF-safe)."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_citation_cff(meta: dict = CITATION_METADATA) -> str:
    """Emit a valid Citation File Format 1.2.0 document as YAML *text* from ``meta`` (no YAML lib)."""
    lines: list[str] = [
        "cff-version: 1.2.0",
        "message: " + _cff_str(meta["message"]),
        "title: " + _cff_str(meta["title"]),
        "type: dataset",
        'version: "' + str(meta["version"]) + '"',
        "date-released: " + _cff_str(meta["date-released"]),
        "license: " + _cff_str(meta["license"]),
        # DOI is the PENDING sentinel until a human mints it — never a fabricated 10.x value.
        "doi: " + _cff_str(meta["doi"]),
        "url: " + _cff_str(meta["url"]),
        "repository-code: " + _cff_str(meta["repo"]),
        "abstract: " + _cff_str(meta["abstract"]),
        "authors:",
    ]
    for author in meta["authors"]:
        lines.append("  - family-names: " + _cff_str(author["family-names"]))
        lines.append("    given-names: " + _cff_str(author["given-names"]))
    lines.append("keywords:")
    for kw in meta["keywords"]:
        lines.append("  - " + _cff_str(kw))
    return "\n".join(lines) + "\n"


def render_bibtex(meta: dict = CITATION_METADATA) -> str:
    """Emit a BibTeX ``@misc`` entry from ``meta``. The note records that the DOI is pending."""
    authors = " and ".join(
        f"{a['family-names']}, {a['given-names']}" for a in meta["authors"]
    )
    doi = meta["doi"]
    doi_note = (
        "DOI pending Zenodo mint (" + DOI_PENDING + ")"
        if doi == DOI_PENDING
        else "doi: " + doi
    )
    note = (
        f"{meta['record_count']:,} synthetic records; license {meta['license']}; "
        f"100% synthetic (AX-001); {doi_note}"
    )
    return (
        "@misc{holla2026pii_anon_eval,\n"
        f"  title        = {{{meta['title']}}},\n"
        f"  author       = {{{authors}}},\n"
        f"  year         = {{{meta['year']}}},\n"
        f"  version      = {{{meta['version']}}},\n"
        "  publisher    = {GitHub},\n"
        f"  howpublished = {{\\url{{{meta['url']}}}}},\n"
        f"  license      = {{{meta['license']}}},\n"
        f"  note         = {{{note}}}\n"
        "}\n"
    )


def validate_no_fake_doi(meta: dict = CITATION_METADATA) -> None:
    """Forbid a FABRICATED DOI. Accept the PENDING sentinel or a deliberately-supplied real DOI.

    The default release state is PENDING. A genuine minted DOI is a human action recorded by
    *replacing* the sentinel with a real ``10.x`` value AND clearing this guard at deposit time; this
    function exists so a ``10.x``-shaped string can never be smuggled in while the deposit hasn't
    happened. We cannot prove a DOI resolves offline, so the contract is conservative: the only
    ``10.``-prefixed value this function tolerates is one explicitly passed by a human via ``meta``,
    and even that must be syntactically DOI-shaped — anything else raises.
    """
    doi = meta.get("doi")
    if doi == DOI_PENDING:
        return None
    if not isinstance(doi, str) or not doi.strip():
        raise ValueError("citation doi must be the DOI_PENDING sentinel or a real minted DOI.")
    if doi.startswith("10."):
        # A real Zenodo DOI is shaped "10.5281/zenodo.<digits>". The placeholder examples we guard
        # against (e.g. "10.1234/fake") are not registered — reject any obviously fabricated value.
        rest = doi[3:]
        registrant, sep, suffix = rest.partition("/")
        looks_fabricated = (
            not sep
            or not suffix.strip()
            or not registrant.isdigit()
            or "fake" in doi.lower()
            or "example" in doi.lower()
            or "1234" in registrant
        )
        if looks_fabricated:
            raise ValueError(
                f"refusing fabricated DOI {doi!r}; the DOI is minted by a human — use DOI_PENDING "
                "until deposit."
            )
        return None
    raise ValueError(
        f"citation doi {doi!r} is neither the DOI_PENDING sentinel nor a 10.x-shaped DOI."
    )
