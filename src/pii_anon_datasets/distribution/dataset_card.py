"""HF dataset card builder (FR-024 / NFR-013) — canonical counts that CANNOT drift + caveats.

Builds the Hugging Face dataset card (``README.md``: YAML frontmatter + Markdown body) for the CC0
corpus. ALL counts are read from the packaged ``pii_anon.metadata.json`` (via
:func:`pii_anon_datasets.distribution.croissant.load_metadata`, the SAME single source
``stats/lattice.py`` reads) so the card **cannot drift** from canonical (NFR-013). The
``entity_types`` count is cross-checked ``== taxonomy.ENTITY_TYPE_COUNT`` (the entity-registry SSOT),
so the three-way drift the taxonomy module fixed (48 / 65 / ~80) cannot recur through the card.

The card embeds four non-strippable, load-bearing caveats:

* :data:`TRAIN_VS_EVAL` — the 159,891 tier3_evaluation records are the ~27.8% EVALUATION substrate,
  NOT the whole 575,604-record corpus;
* :data:`ENRICHMENT_DISCLOSURE` — ~72% of records are synthetic_lattice_enrichment power-fill
  (synthetic power is not external validity);
* :data:`POWER_SENTENCE` — the §7 authoritative power statement (sampling-design.md §7), verbatim;
* the CC0-data / Apache-2.0-code license split (locked revision #11).

Pure-stdlib and deterministic — no clock/RNG, no network egress, no HF upload (NFR-004 / AX-002);
it returns a Markdown string only.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pii_anon_datasets import taxonomy
from pii_anon_datasets.distribution.croissant import load_metadata

# §7 authoritative power sentence (sampling-design.md §7) — embedded verbatim as a non-strippable claim.
POWER_SENTENCE: str = (
    "PII-Anon v2 is powered for all single-factor marginal recall claims (95% Wilson "
    "CIs; credential/financial-critical types to ±0.5pp at recall 0.99, standard to ±1pp at 0.98) and "
    "for three pre-registered 2-way interactions (language×entity-type on a 12×41 committed rectangle, "
    "domain×track, adversarial-type×entity-type). It is not powered for the full multilingual×entity-type "
    "grid or any ≥3-way interaction; those are reported as exploratory. Synthetic-distribution power is "
    "not external validity — see the real-data correlation slice."
)
ENRICHMENT_DISCLOSURE: str = (
    "~72% of records carry provenance.source_type="
    "'synthetic_lattice_enrichment' (the S-PWR power fill); synthetic power is not external validity."
)
TRAIN_VS_EVAL: str = (
    "The 159,891 tier3_evaluation records are the ~27.8% EVALUATION substrate of the "
    "575,604-record corpus (behavioral-signal / RRS scoring runs on this substrate), NOT the whole corpus."
)


def _size_category(total_records: int) -> str:
    """The HF ``size_categories`` bucket for ``total_records`` (e.g. ``100K<n<1M``).

    Deterministic, derived from the canonical record count — never hardcoded, so it tracks the
    metadata if the corpus size changes.
    """
    bounds = (
        (1_000, "n<1K"),
        (10_000, "1K<n<10K"),
        (100_000, "10K<n<100K"),
        (1_000_000, "100K<n<1M"),
        (10_000_000, "1M<n<10M"),
    )
    for upper, label in bounds:
        if total_records < upper:
            return label
    return "n>10M"


def _languages(md: Mapping[str, Any]) -> list[str]:
    """The corpus language codes, ordered — drawn from the canonical metadata distribution.

    Uses the ``by_language`` key order (descending by count in the packaged metadata) so the card's
    language list mirrors canonical; falls back to an empty list if the distribution is absent.
    """
    by_language = md.get("distributions", {}).get("by_language", {})
    return list(by_language.keys())


def _frontmatter(md: Mapping[str, Any]) -> str:
    """Render the YAML frontmatter block (license / size_categories / language / task / tags).

    All values derive from ``md`` (counts cannot drift); deterministic ordering.
    """
    languages = _languages(md)
    language_block = "".join(f"  - {code}\n" for code in languages)
    return (
        "---\n"
        "license: cc0-1.0\n"
        "pretty_name: PII-Anon\n"
        f"size_categories:\n  - {_size_category(int(md['total_records']))}\n"
        "task_categories:\n  - token-classification\n"
        "tags:\n  - pii\n  - privacy\n  - anonymization\n  - multilingual\n"
        f"language:\n{language_block}"
        "---\n"
    )


def _baseline_section(baseline_results: Mapping[str, Any]) -> str:
    """The compact ``## Baseline Detector Performance`` card section — the F2-ranked detector leaderboard
    wired into the card (only called when ``baseline_results`` is provided).

    Pure-stdlib f-string render of the overall F2 table fed by a ``baseline_results`` dict (the full
    per-type / per-domain / per-language tables, Wilson CIs, and provenance live in
    ``baseline_results.json`` / ``BASELINES.md``). The non-strippable synthetic-only caveat (AX-001) and
    each detector's native→63-type label-map coverage ride along. Ends with a blank line so the following
    ``## License`` section is cleanly separated.
    """
    data = baseline_results.as_dict() if hasattr(baseline_results, "as_dict") else dict(baseline_results)
    ds = data.get("dataset", {})
    lines = [
        "## Baseline Detector Performance",
        "",
        (
            f"How widely-used PII detectors score on this corpus (`{ds.get('split', '?')}` split, language "
            f"`{ds.get('language', 'all')}`; {int(ds.get('n_records', 0)):,} records), ranked by **F2** "
            "(recall-weighted — a missed PII is the costly error). Full per-type / per-domain / per-language "
            "tables, Wilson CIs, and provenance: `baseline_results.json` and `BASELINES.md`."
        ),
        "",
        f"> {data.get('caveat', '')}",
        "",
        "| Rank | Detector | Precision | Recall | F2 | Recall 95% CI | Coverage |",
        "|---|---|---:|---:|---:|---|---:|",
    ]
    for row in data.get("ranking", []):
        det = data["detectors"][row["detector"]]
        m = det["micro"]
        ci = m["recall_ci"]
        cov = det["coverage"]
        lines.append(
            f"| {row['rank']} | {row['detector']} | {m['precision']:.3f} | {m['recall']:.3f} | "
            f"{m['f2']:.3f} | [{ci['low']:.3f}, {ci['high']:.3f}] | {cov['reachable']}/{cov['of_total']} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def build_dataset_card(
    metadata: Mapping[str, Any] | None = None,
    baseline_results: Mapping[str, Any] | None = None,
) -> str:
    """HF dataset card (``README.md``: YAML frontmatter + Markdown body). ALL counts from
    ``metadata`` (default: packaged) so they cannot drift.

    Frontmatter: ``license: cc0-1.0``, ``size_categories`` (derived from ``total_records``), a
    ``language`` list, ``task_categories`` (token-classification), ``pretty_name``, ``tags``.
    Body: a description with the canonical ``total_records`` / ``total_annotations`` / ``entity_types``
    (== :data:`taxonomy.ENTITY_TYPE_COUNT`) / ``languages`` / ``evaluation_dimensions``;
    :data:`TRAIN_VS_EVAL`; :data:`ENRICHMENT_DISCLOSURE`; :data:`POWER_SENTENCE`; the CC0-data /
    Apache-2.0-code split.

    ``baseline_results`` (optional): a ``baselines`` leaderboard dict (or ``BaselineResults``). When given,
    a compact F2-ranked ``## Baseline Detector Performance`` section is inserted before ``## License``;
    when ``None`` the card is byte-identical to the corpus-only card (the leaderboard is wired in, never
    forced). The section carries the non-strippable synthetic-only caveat (AX-001).

    Deterministic and pure (no clock/RNG/network): the same metadata always yields the same card.
    """
    md = dict(metadata) if metadata is not None else load_metadata()
    assert md["entity_types"] == taxonomy.ENTITY_TYPE_COUNT  # counts cannot drift

    total_records = int(md["total_records"])
    total_annotations = int(md["total_annotations"])
    entity_types = int(md["entity_types"])
    languages = int(md["languages"])
    dimensions = int(md.get("evaluation_dimensions", len(taxonomy.SENSITIVITY_CLASSES)))

    body = (
        "# PII-Anon\n\n"
        f"A CC0 multilingual PII benchmark corpus of **{total_records:,}** records carrying "
        f"**{total_annotations:,}** entity annotations across **{entity_types}** entity types and "
        f"**{languages}** languages, spanning {dimensions} evaluation dimensions. Each record exposes "
        "the five legally-distinct regulatory regime signals (gov-02 / FR-022) as separate `reg_*` "
        "columns — no merged compliance verdict.\n\n"
        "## Train vs. evaluation substrate\n\n"
        f"{TRAIN_VS_EVAL}\n\n"
        "## Synthetic-enrichment disclosure\n\n"
        f"{ENRICHMENT_DISCLOSURE}\n\n"
        "## Statistical power\n\n"
        f"{POWER_SENTENCE}\n\n"
        f"{_baseline_section(baseline_results) if baseline_results else ''}"
        "## License\n\n"
        "The **data** is released under **CC0-1.0** (public-domain dedication); the accompanying "
        "**code** (loaders, scorers, exporters) is licensed **Apache-2.0**. The two licenses are "
        "distinct — using the data does not subject you to the code license, and vice versa.\n"
    )
    return _frontmatter(md) + "\n" + body
