"""S5-03 — HF dataset card (FR-024 / NFR-013): canonical counts that CANNOT drift + caveats.

Pins the dataset-card builder that ships the CC0 corpus with a HF README:

* YAML frontmatter (``license: cc0-1.0`` + ``size_categories`` + ``language`` list) (``fr_024``);
* body counts pulled from the packaged ``pii_anon.metadata.json`` so they cannot drift — the
  ``entity_types`` count equals BOTH ``metadata["entity_types"]`` AND ``taxonomy.ENTITY_TYPE_COUNT``,
  and the stale v1.x strings ``"150K"`` / ``"65 "`` / ``"57 "`` are forbidden (``nfr_013``);
* the load-bearing caveats: the train-vs-eval substrate note (the frozen 159,891 tier3 EVALUATION
  records against the LIVE corpus total, no stale ratio), the 79.2% ``synthetic_lattice_enrichment``
  disclosure, the §7 authoritative power sentence, and the CC0-data / Apache-2.0-code split (``fr_024``);
* pure-stdlib (AST guard banning {random, time, uuid, datetime, secrets} — ``nfr004``).
"""

from __future__ import annotations

import ast
import pathlib

from pii_anon_datasets import taxonomy
from pii_anon_datasets.distribution import dataset_card as dataset_card_mod
from pii_anon_datasets.distribution.croissant import load_metadata
from pii_anon_datasets.distribution.dataset_card import build_dataset_card

_BANNED_NONDETERMINISTIC = {"random", "time", "uuid", "datetime", "secrets"}


def test_fr_024_dataset_card_has_yaml_frontmatter() -> None:
    """[UNIT-TEST] ``build_dataset_card()`` output starts with a ``---`` YAML frontmatter block
    declaring ``license: cc0-1.0``, a ``size_categories`` and a ``language:`` list."""
    card = build_dataset_card()

    assert card.startswith("---\n"), "card must open with a YAML frontmatter fence"
    # The frontmatter is the text between the first two '---' fences.
    end = card.index("\n---", 4)
    frontmatter = card[4:end]

    assert "license: cc0-1.0" in frontmatter, "frontmatter must declare license: cc0-1.0"
    assert "size_categories:" in frontmatter, "frontmatter must declare a size_categories"
    assert "language:" in frontmatter, "frontmatter must declare a language list"


def test_nfr_013_dataset_card_counts_match_metadata() -> None:
    """[PROPERTY-TEST] Counts cannot drift: the card body contains the canonical ``total_records``
    (782,677) and ``total_annotations`` (3,107,240) and the ``entity_types`` count, which equals
    BOTH ``metadata["entity_types"]`` AND ``taxonomy.ENTITY_TYPE_COUNT``; it contains NONE of the
    stale strings ``"150K"`` / ``"65 "`` / ``"57 "``."""
    md = load_metadata()
    card = build_dataset_card(md)

    # Canonical record / annotation totals (grouped with thousands separators) appear verbatim.
    assert f"{md['total_records']:,}" in card, "canonical total_records must appear in the card body"
    assert f"{md['total_annotations']:,}" in card, "canonical total_annotations must appear"

    # entity_types is consistent across the three sources and present in the card.
    assert md["entity_types"] == taxonomy.ENTITY_TYPE_COUNT, "metadata vs taxonomy entity-count drift"
    assert str(md["entity_types"]) in card, "entity_types count must appear in the card body"

    # No stale v1.x counts may survive (the drift the card exists to prevent).
    for stale in ("150K", "65 ", "57 "):
        assert stale not in card, f"stale count {stale!r} must not appear in the generated card"


def test_fr_024_dataset_card_embeds_caveats() -> None:
    """[UNIT-TEST] The card embeds (a) the train-vs-eval note (the frozen 159,891 tier3 EVALUATION
    records against the LIVE corpus total, no stale ratio/denominator), (b) the 79.2%
    ``synthetic_lattice_enrichment`` disclosure, (c) the §7 authoritative power sentence, and (d) the
    CC0-data / Apache-2.0-code split."""
    md = load_metadata()
    card = build_dataset_card()

    # (a) train-vs-eval substrate: the frozen 159,891 tier3 EVALUATION records stated against the LIVE
    #     corpus total (no hardcoded fraction/denominator, so the pre-2.2.0 575,604 total must be absent).
    assert "159,891" in card, "card must state the 159,891 tier3 EVALUATION substrate size"
    assert f"{md['total_records']:,}-record corpus" in card, "substrate note must use the live corpus total"
    assert "575,604" not in card, "card must not carry the stale pre-2.2.0 corpus total"
    assert "EVALUATION" in card, "card must distinguish the EVALUATION substrate from the whole corpus"

    # (b) the 79.2% synthetic_lattice_enrichment disclosure.
    assert "79.2%" in card, "card must disclose the 79.2% enrichment fraction"
    assert "synthetic_lattice_enrichment" in card, "card must name synthetic_lattice_enrichment"

    # (c) the §7 authoritative power sentence (embedded verbatim, non-strippable).
    assert "powered for all single-factor marginal recall claims" in card, "power sentence missing"
    assert "Synthetic-distribution power is not external validity" in card, "power-validity caveat missing"

    # (d) the CC0-data / Apache-2.0-code split.
    assert "CC0" in card and "Apache-2.0" in card, "card must state the CC0-data / Apache-2.0-code split"


def test_nfr004_dataset_card_pure_stdlib() -> None:
    """[PROPERTY-TEST] NFR-004: AST guard — ``dataset_card.py`` imports NONE of
    {random, time, uuid, datetime, secrets} (deterministic, pure-stdlib emit; AX-002)."""
    src = pathlib.Path(dataset_card_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert _BANNED_NONDETERMINISTIC.isdisjoint(imported), (
        f"dataset_card.py imports nondeterministic modules: {sorted(_BANNED_NONDETERMINISTIC & imported)}"
    )


def _baseline_results_fixture() -> dict:
    """A minimal but schema-faithful baseline_results dict (one F2-ranked detector)."""
    return {
        "caveat": "Power on a committed cell is statistical precision on the SYNTHETIC distribution. Synthetic-only (AX-001).",
        "matching_policy": "strict-v1",
        "dataset": {"split": "test", "language": "en", "dataset_version": "2.0.0", "n_records": 1500, "n_gold": 9000},
        "ranking": [{"rank": 1, "detector": "gliner", "f2_micro": 0.76, "f2_macro": 0.51}],
        "detectors": {
            "gliner": {
                "status": "scored",
                "micro": {
                    "precision": 0.71,
                    "recall": 0.78,
                    "f1": 0.74,
                    "f2": 0.76,
                    "recall_ci": {"low": 0.77, "high": 0.79},
                },
                "coverage": {"reachable": 31, "of_total": 63},
            }
        },
    }


def test_nfr_013_baseline_results_none_is_byte_identical() -> None:
    """[PROPERTY-TEST] Adding the ``baseline_results`` param must not change the default card by a single
    byte: it defaults to ``None`` and only APPENDS a section when provided."""
    assert build_dataset_card(baseline_results=None) == build_dataset_card()
    md = load_metadata()
    assert build_dataset_card(md, baseline_results=None) == build_dataset_card(md)


def test_fr_024_baseline_section_inserted_before_license() -> None:
    """[UNIT-TEST] With ``baseline_results`` provided, a '## Baseline Detector Performance' section appears
    — F2-ranked, carrying the synthetic-only caveat and the per-detector coverage — positioned BEFORE the
    License section (and the default caveats are all still present)."""
    card = build_dataset_card(baseline_results=_baseline_results_fixture())

    assert "## Baseline Detector Performance" in card
    assert "gliner" in card, "the F2-ranked detector must appear in the card"
    assert "Synthetic-only (AX-001)" in card, "the synthetic-only caveat must ride on the card numbers"
    assert "31/63" in card, "per-detector label-map coverage must be disclosed"
    assert card.index("## Baseline Detector Performance") < card.index("## License"), "section before License"
    # the pre-existing caveats are untouched
    assert "synthetic_lattice_enrichment" in card and "159,891" in card
