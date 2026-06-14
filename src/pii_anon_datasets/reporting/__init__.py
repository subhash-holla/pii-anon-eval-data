"""Reporting layer (DC-09): per-cell power tables + power matrices for published metrics."""
from .language_power import (
    language_x_type_matrix,
    per_language_table,
)
from .language_power import render_csv as render_language_csv
from .language_power import render_markdown as render_language_markdown
from .power_table import power_report, power_table, render_csv, render_markdown

# S4-05 visualization layer (DC-09 D3 reports). Re-exported here, but DEFINING these functions
# imports NO matplotlib — matplotlib is imported lazily inside reporting.viz._require_matplotlib,
# so `import pii_anon_datasets.reporting` stays pure-stdlib at module load (NFR-004); only CALLING
# a render function needs the optional [viz] extra.
from .viz import (
    LeakageEdge,
    agent_leakage_sankey,
    coverage_risk_curve,
    pareto_plot,
    reliability_diagram,
    slice_heatmap,
)

__all__ = [
    "power_table",
    "power_report",
    "render_markdown",
    "render_csv",
    # S4-04 per-language + language×type power transparency (NFR-003)
    "per_language_table",
    "language_x_type_matrix",
    "render_language_markdown",
    "render_language_csv",
    # S4-05 visualization layer (DC-09 D3 reports) — matplotlib behind the [viz] extra (lazy).
    "LeakageEdge",
    "reliability_diagram",
    "pareto_plot",
    "slice_heatmap",
    "agent_leakage_sankey",
    "coverage_risk_curve",
]
