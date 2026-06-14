"""Report visualizations (S4-05; DC-09 D3 Information-Dense reports) — behind the ``[viz]`` extra.

Five static PNG report artifacts:

* :func:`reliability_diagram` — calibration reliability curve vs the perfect-calibration diagonal
  (FR-005). Consumes a ``CalibrationResult``-shaped object **by duck-typing** ``.reliability`` bins
  (each bin exposes ``.conf_mean`` / ``.acc`` / ``.count``) — it does NOT import
  :class:`~pii_anon_datasets.stats.calibration.CalibrationResult`.
* :func:`pareto_plot` — the privacy-utility **two-axis** Pareto plot (FR-006). It takes THIN
  ``(residual_risk, utility, label)`` tuples and plots residual-risk on x against utility on y; it
  **never** imports ``scoring`` and **never** fuses the two axes into one scalar (NFR-005 / AX-004).
  The caller unpacks a ``ParetoPoint`` into its two axis values + a label.
* :func:`slice_heatmap` — delegates to :meth:`PowerMatrix.heatmap` (NFR-003).
* :func:`agent_leakage_sankey` — agent-leakage flow diagram from thin :class:`LeakageEdge` tuples.
* :func:`coverage_risk_curve` — the abstention **selective-prediction** curve (FR-005): accuracy as a
  function of coverage as the lowest-confidence predictions are progressively abstained. This closes
  the FR-005 abstention/coverage-risk facet flagged at the S4-03 gate.

**NFR-004 (core stays pure-stdlib):** matplotlib is imported LAZILY — only inside
:func:`_require_matplotlib`, never at module top. So ``import pii_anon_datasets.reporting`` (which
re-exports these functions) succeeds with matplotlib absent; only *calling* a render function needs
the ``[viz]`` extra, and a missing extra raises a clear :class:`RuntimeError` naming the install
command.

**Determinism:** the ``Agg`` backend is selected inside the lazy guard; each function writes a PNG
and closes the figure. PNG byte-equality is not a contract (matplotlib embeds a timestamp); the
contract is "a non-empty PNG file is written".
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

__all__ = [
    "LeakageEdge",
    "reliability_diagram",
    "pareto_plot",
    "slice_heatmap",
    "agent_leakage_sankey",
    "coverage_risk_curve",
    "operating_point_curve",
]


def _require_matplotlib() -> Any:
    """Lazily import matplotlib, select the headless ``Agg`` backend, and return ``pyplot``.

    matplotlib is an OPTIONAL dependency (the ``[viz]`` extra) so the core stays pure-stdlib
    (NFR-004); this is the ONLY place it is imported. If it is absent, raise a clear
    :class:`RuntimeError` naming the install command rather than letting a bare ``ImportError``
    surface from deep inside a render call.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")  # headless: no display required for static report PNGs
        import matplotlib.pyplot as plt
    except ImportError as e:  # pragma: no cover - exercised via monkeypatched import in tests
        raise RuntimeError(
            "viz needs the optional 'viz' extra: pip install pii-anon-datasets[viz]"
        ) from e
    return plt


@dataclass(frozen=True)
class LeakageEdge:
    """One agent-leakage flow ``source -> target`` carrying magnitude ``value`` (e.g. leak count).

    A thin transport tuple so :func:`agent_leakage_sankey` needs no concrete agent-graph type.
    """

    source: str
    target: str
    value: float


def reliability_diagram(result: Any, path: str) -> str:
    """Draw a calibration reliability diagram from a ``CalibrationResult``-shaped ``result``.

    Duck-typed: only ``result.reliability`` (an iterable of bins with ``.conf_mean`` / ``.acc`` /
    ``.count``) is read — :class:`CalibrationResult` is NOT imported. Empty bins (``count == 0``) are
    dropped so the curve reflects only populated buckets. Plots the perfect-calibration diagonal for
    reference, then the per-bin accuracy-vs-confidence curve. Writes a PNG to ``path`` and returns it.
    """
    plt = _require_matplotlib()
    bins = [b for b in result.reliability if getattr(b, "count", 0) > 0]
    confs = [float(b.conf_mean) for b in bins]
    accs = [float(b.acc) for b in bins]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0.0, 1.0], [0.0, 1.0], linestyle="--", color="gray", label="perfect calibration")
    if confs:
        ax.plot(confs, accs, marker="o", color="tab:blue", label="observed")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_xlabel("mean predicted confidence")
    ax.set_ylabel("empirical accuracy")
    ax.set_title("Reliability diagram (calibration)")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def pareto_plot(points: Sequence[tuple[float, float, str]], path: str) -> str:
    """Draw the privacy-utility **two-axis** Pareto plot (FR-006; NFR-005 / AX-004).

    ``points`` is a sequence of thin ``(residual_risk, utility, label)`` tuples. Residual-risk is
    plotted on the x-axis and utility on the y-axis — the two axes are NEVER fused into a single
    scalar, and ``scoring`` is never imported (the caller unpacks a ``ParetoPoint`` into these two
    axis values + a label). Each point is scattered and annotated with its label. Returns ``path``.
    """
    plt = _require_matplotlib()
    fig, ax = plt.subplots(figsize=(6, 5))
    for residual_risk, utility, label in points:
        x = float(residual_risk)
        y = float(utility)
        ax.scatter([x], [y], s=40)
        ax.annotate(str(label), (x, y), textcoords="offset points", xytext=(5, 5), fontsize=8)
    ax.set_xlabel("residual re-identification risk (privacy axis)")
    ax.set_ylabel("downstream utility (utility axis)")
    ax.set_title("Privacy-utility Pareto (two axes — never a merged scalar)")
    ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def slice_heatmap(power_matrix: Any, path: str) -> str:
    """Render the power slice heatmap by delegating to ``power_matrix.heatmap(path)`` (NFR-003).

    The grid construction + colour mapping live on :meth:`PowerMatrix.heatmap`; this is the
    ``reporting`` façade that exposes it alongside the other report visualizations. Returns ``path``.
    """
    power_matrix.heatmap(path)
    return path


def agent_leakage_sankey(edges: Sequence[LeakageEdge], path: str) -> str:
    """Draw an agent-leakage flow diagram from thin :class:`LeakageEdge` tuples.

    Each ``source -> target`` flow is drawn as a horizontal bar whose length is proportional to its
    ``value`` (a leakage magnitude), grouped and labelled by ``"source -> target"`` and ordered by
    descending value so the dominant leakage paths read top-first. A flow-conservation Sankey would
    require balanced in/out flows, which arbitrary leakage edges need not satisfy; this magnitude-bar
    rendering is robust for any edge set while still surfacing where agent data leaks. Returns ``path``.
    """
    plt = _require_matplotlib()
    ordered = sorted(edges, key=lambda e: float(e.value), reverse=True)
    labels = [f"{e.source} → {e.target}" for e in ordered]
    values = [float(e.value) for e in ordered]
    fig, ax = plt.subplots(figsize=(7, max(3, 0.5 * len(ordered) + 1)))
    ypos = list(range(len(ordered)))
    ax.barh(ypos, values, color="tab:red", alpha=0.7)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()  # largest flow on top
    ax.set_xlabel("leakage magnitude")
    ax.set_title("Agent-leakage flows (source → target)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def coverage_risk_curve(
    confidences: Sequence[float], correct: Sequence[int], path: str
) -> str:
    """Draw the abstention selective-prediction **coverage-risk curve** (FR-005).

    Selective prediction: rank predictions by confidence (highest first) and sweep a confidence
    threshold downward; at each step the model *answers* the predictions at or above the threshold
    (coverage = answered/total) and *abstains* on the rest. The curve plots accuracy-on-answered
    against coverage, so accuracy is typically highest at low coverage (only the most-confident,
    usually-correct predictions are kept) and decays toward the full-coverage accuracy. This is the
    FR-005 abstention facet flagged at the S4-03 gate. ``len(confidences) != len(correct)`` raises
    :class:`ValueError`. Writes a PNG to ``path`` and returns it.
    """
    if len(confidences) != len(correct):
        raise ValueError(
            f"coverage_risk_curve: len(confidences) ({len(confidences)}) "
            f"!= len(correct) ({len(correct)})"
        )
    plt = _require_matplotlib()
    n = len(confidences)
    # sort by confidence descending — answer the most-confident predictions first.
    order = sorted(range(n), key=lambda i: float(confidences[i]), reverse=True)
    coverage: list[float] = []
    accuracy: list[float] = []
    cum_correct = 0
    for rank, i in enumerate(order, start=1):
        cum_correct += int(correct[i])
        coverage.append(rank / n)
        accuracy.append(cum_correct / rank)
    fig, ax = plt.subplots(figsize=(6, 5))
    if coverage:
        ax.plot(coverage, accuracy, marker="o", color="tab:green")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_xlabel("coverage (fraction answered; low-confidence predictions abstained)")
    ax.set_ylabel("accuracy on answered predictions")
    ax.set_title("Abstention coverage-risk (selective prediction)")
    ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def operating_point_curve(
    curve: Sequence[tuple[float, float]], path: str, *, operating_point: tuple[float, float] | None = None
) -> str:
    """Draw the precision-recall curve with the pre-registered operating point marked (DC-27 / FR-048).

    ``curve`` is a sequence of ``(recall, precision)`` points — a SINGLE point for a hit-only system (the
    degenerate case), many for a scored detector. ``operating_point`` ``(recall, precision)``, if given, is
    highlighted: the point the recall-priority Fβ / precision-at-recall readout is taken at. This renders the
    false-positive-tax view (recall on x, precision on y) so a high recall bought with collapsing precision is
    visible, not hidden behind a lone F1. Writes a PNG to ``path`` and returns it.
    """
    plt = _require_matplotlib()
    pts = sorted(((float(r), float(p)) for r, p in curve), key=lambda rp: rp[0])
    xs = [r for r, _ in pts]
    ys = [p for _, p in pts]
    fig, ax = plt.subplots(figsize=(6, 5))
    if len(pts) == 1:
        ax.scatter(xs, ys, color="tab:blue", s=70, label="operating point (hit-only / degenerate)")
    else:
        ax.plot(xs, ys, marker="o", color="tab:blue", label="precision-recall curve")
    if operating_point is not None:
        ax.scatter([operating_point[0]], [operating_point[1]], color="tab:red", s=110, zorder=5,
                   marker="*", label="pre-registered operating point")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_xlabel("recall")
    ax.set_ylabel("precision")
    ax.set_title("Detection operating point (recall-priority; FR-048)")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.legend(loc="lower left", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path
