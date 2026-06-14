"""Per-language + language×entity_type power transparency (DC-09; NFR-003, FR-029, AX-003).

NFR-003 forbids shipping an aggregate "60-language" or "type-across-languages" claim without the
underlying per-language positive-count table AND the per-(language×entity_type) power matrix, with
every below-tier-target cell flagged low-power. This is a THIN reporter over the FROZEN committed
``eval_lattice.json`` + the existing :mod:`reporting.power_table`: it reuses ``power_table``'s
``_power_class`` cell classifier so a language / type / language×type row carries exactly the same
``power_class`` label as the published per-cell power table.

Like :mod:`reporting.power_table`, it takes ``observed_counts`` (computed by the audit —
``scripts/validate.py`` / ``lattice_audit.py``) as an ARGUMENT and never reads the corpus, keeping
this src-layer pure + deterministic (NFR-004). It also never rebuilds or mutates the frozen lattice:
the lattice arrives as an argument.
"""
from __future__ import annotations

import csv
import io
from typing import Any

from .power_table import _power_class

# Interaction tags + id prefixes are the contract frozen into eval_lattice.json (stats/lattice.py):
# language marginals carry interaction "marginal:language" (id "M:language=<lang>"); the headline
# rectangle carries "language_x_entity_type" (id "LxE:entity_type=<t>|language=<l>").
_MARGINAL_LANGUAGE = "marginal:language"
_LANGUAGE_X_TYPE = "language_x_entity_type"


def _cell_row(cell: dict[str, Any], observed_counts: dict[str, int]) -> tuple[int, str]:
    """Observed positives (default 0, mirroring ``power_table``) + the reused power class."""
    positives = int(observed_counts.get(cell["id"], 0))
    return positives, _power_class(positives, cell["target_n"])


def per_language_table(lattice: dict[str, Any], observed_counts: dict[str, int]) -> list[dict[str, Any]]:
    """One row per LANGUAGE marginal cell, sorted by language (NFR-003 per-language table).

    Filters the frozen lattice to ``interaction == "marginal:language"`` cells; each row is
    ``{language, positives, target_n, tier, power_class}`` with ``positives`` pulled from
    ``observed_counts`` (keyed by cell id) and ``power_class`` reusing ``power_table``'s classifier.
    A below-target language is therefore labelled ``under_powered`` (or ``empty`` at zero).
    """
    rows: list[dict[str, Any]] = []
    for cell in lattice["cells"]:
        if cell["interaction"] != _MARGINAL_LANGUAGE:
            continue
        positives, power_class = _cell_row(cell, observed_counts)
        rows.append({
            "language": cell["dimensions"]["language"],
            "positives": positives,
            "target_n": cell["target_n"],
            "tier": cell["tier"],
            "power_class": power_class,
        })
    rows.sort(key=lambda r: r["language"])
    return rows


def language_x_type_matrix(lattice: dict[str, Any], observed_counts: dict[str, int]) -> list[dict[str, Any]]:
    """The language×entity_type committed cells, grouped by language (NFR-003 power matrix).

    Filters to ``interaction == "language_x_entity_type"`` cells; each row is
    ``{language, entity_type, positives, target_n, tier, power_class}``. Sorted by
    ``(language, entity_type)`` so the matrix is contiguous per language (forward-navigable) and
    still reverse-navigable by entity_type. ``power_class`` reuses ``power_table``'s classifier, so
    any below-target language×type cell is labelled low-power (``under_powered`` / ``empty``).
    """
    rows: list[dict[str, Any]] = []
    for cell in lattice["cells"]:
        if cell["interaction"] != _LANGUAGE_X_TYPE:
            continue
        positives, power_class = _cell_row(cell, observed_counts)
        dims = cell["dimensions"]
        rows.append({
            "language": dims["language"],
            "entity_type": dims["entity_type"],
            "positives": positives,
            "target_n": cell["target_n"],
            "tier": cell["tier"],
            "power_class": power_class,
        })
    rows.sort(key=lambda r: (r["language"], r["entity_type"]))
    return rows


# Deterministic column order for BOTH row shapes (NFR-004). ``entity_type`` is present only for
# the matrix rows; it is emitted when (and only when) every row carries it.
_BASE_COLUMNS = ("language", "entity_type", "positives", "target_n", "tier", "power_class")


def _columns(rows: list[dict[str, Any]]) -> list[str]:
    if rows and all("entity_type" in r for r in rows):
        return list(_BASE_COLUMNS)
    return [c for c in _BASE_COLUMNS if c != "entity_type"]


def render_markdown(rows: list[dict[str, Any]]) -> str:
    """Markdown table: header + one row per cell; below-target cells flagged in a ``low_power``
    column (NFR-003 low-power labelling)."""
    cols = _columns(rows)
    header = "| " + " | ".join(cols) + " | low_power |"
    sep = "|" + "|".join("---" for _ in cols) + "|---|"
    out = [header, sep]
    for r in rows:
        flag = "" if r["power_class"] == "well_powered" else "⚠ LOW"
        out.append("| " + " | ".join(str(r[c]) for c in cols) + f" | {flag} |")
    return "\n".join(out) + "\n"


def render_csv(rows: list[dict[str, Any]]) -> str:
    """CSV with a deterministic column order (NFR-004); a ``low_power`` boolean column flags every
    below-target cell. Round-trips via :mod:`csv` to the same row count."""
    cols = _columns(rows)
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow([*cols, "low_power"])
    for r in rows:
        low_power = r["power_class"] != "well_powered"
        writer.writerow([*(r[c] for c in cols), low_power])
    return buf.getvalue()
