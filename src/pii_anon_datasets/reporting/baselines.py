"""Render the ``pii-anon baselines`` F2-ranked detector leaderboard as markdown (+ an optional chart).

Markdown rendering is PURE-STDLIB (no matplotlib) so BASELINES.md / README / DATASHEET can be regenerated
on a lib-less checkout; the chart lazily imports matplotlib (the ``[viz]`` extra), mirroring
:func:`pii_anon_datasets.reporting.viz._require_matplotlib`. Every rendered number is the AUDITED metric
(P/R/F1/F2 + Wilson CIs), and the four honesty disclosures ride along: the non-strippable synthetic-only
caveat (AX-001), the strict-vs-relaxed span-matching policy, per-detector label-map coverage (lossiness),
and precision shown beside recall (the false-positive tax of recall-weighted ranking).

Accepts either a ``BaselineResults`` or its ``as_dict()`` form (duck-typed — no import of the baselines
package, so reporting stays decoupled).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _as_data(results: Any) -> dict:
    return results.as_dict() if hasattr(results, "as_dict") else dict(results)


def _f(x: Any) -> str:
    return f"{float(x):.3f}"


def _scored(data: dict) -> list[str]:
    """Detector names that scored, in F2-ranked order."""
    return [row["detector"] for row in data.get("ranking", [])]


def render_leaderboard_table(data: dict) -> str:
    """The overall F2-ranked table: rank, detector, P, R, F1, F2, recall 95% CI, coverage."""
    out = [
        "| Rank | Detector | Precision | Recall | F1 | F2 | Recall 95% CI | Coverage |",
        "|---|---|---:|---:|---:|---:|---|---:|",
    ]
    for row in data.get("ranking", []):
        det = data["detectors"][row["detector"]]
        m = det["micro"]
        ci = m["recall_ci"]
        cov = det["coverage"]
        out.append(
            f"| {row['rank']} | {row['detector']} | {_f(m['precision'])} | {_f(m['recall'])} | "
            f"{_f(m['f1'])} | {_f(m['f2'])} | [{_f(ci['low'])}, {_f(ci['high'])}] | "
            f"{cov['reachable']}/{cov['of_total']} |"
        )
    return "\n".join(out) + "\n"


def render_breakdown_table(data: dict, dimension: str) -> str:
    """An F2 breakdown over one dimension (``by_domain`` / ``by_language`` / ``by_entity_type``):
    rows = scored detectors, columns = slice keys, cells = F2 (— where a detector has no spans)."""
    scored = _scored(data)
    keys = sorted({k for n in scored for k in data["detectors"][n].get(dimension, {})})
    out = ["| Detector | " + " | ".join(keys) + " |", "|---|" + "|".join("---:" for _ in keys) + "|"]
    for n in scored:
        cells = data["detectors"][n].get(dimension, {})
        values = " | ".join(_f(cells[k]["f2"]) if k in cells else "—" for k in keys)
        out.append(f"| {n} | {values} |")
    return "\n".join(out) + "\n"


def render_baseline_leaderboard(results: Any) -> str:
    """The full ``## Baseline Detector Performance`` section: intro + caveat + overall F2 table +
    per-domain (and per-language when multilingual) breakdowns + the honesty footnotes."""
    data = _as_data(results)
    ds = data.get("dataset", {})
    parts = [
        "## Baseline Detector Performance\n",
        (
            f"How widely-used PII detectors score on PII-Anon **{ds.get('dataset_version', '')}** "
            f"(`{ds.get('split', '?')}` split, language `{ds.get('language', 'all')}`; "
            f"{int(ds.get('n_records', 0)):,} records / {int(ds.get('n_gold', 0)):,} gold spans). "
            "Ranked by **F2** (β=2 — recall-weighted, because a missed PII is the costly error).\n"
        ),
        f"> {data.get('caveat', '')}\n",
        "### Overall (micro-averaged, F2-ranked)\n",
        render_leaderboard_table(data),
        "### F2 by domain\n",
        render_breakdown_table(data, "by_domain"),
    ]

    langs = sorted({k for n in _scored(data) for k in data["detectors"][n].get("by_language", {})})
    if len(langs) > 1:
        parts.append("### F2 by language\n")
        parts.append(render_breakdown_table(data, "by_language"))

    unavailable = sorted(n for n, det in data.get("detectors", {}).items() if det.get("status") != "scored")
    if unavailable:
        parts.append("_Not run (detector library or credentials unavailable): " + ", ".join(unavailable) + "._\n")

    parts.append(f"> {data.get('span_matching_disclosure', '')}\n")
    # Denominator tracks the corpus the run scored against (the canonical taxonomy has grown over time,
    # 63 -> 66), so read it from the data rather than hard-coding a stale literal.
    of_total = max((d.get("coverage", {}).get("of_total", 0)
                    for d in data.get("detectors", {}).values()), default=0)
    parts.append(
        f"Coverage = the count of canonical PII types reachable through a detector's native→{of_total}-type "
        f"label map (its projection ceiling). Matching policy: `{data.get('matching_policy', '')}`. Precision "
        "is shown beside recall so the false-positive tax of recall-weighted (F2) ranking stays visible.\n"
    )
    return "\n".join(parts)


def render_cost_table(data: dict, cost_per_detector: dict) -> str:
    """Cost-normalized companion: rank, detector, F2, $/1k records, cost per F2-point.

    Local detectors are 'free'; cloud detectors carry the June-2026 list-price estimate (×2 safety,
    CLOUD_DLP_COST.md). This is a SECOND lens beside the F2 ranking, not a re-ranking.
    """
    out = [
        "| Rank | Detector | F2 | $/1k records | Cost per F2-point |",
        "|---|---|---:|---:|---:|",
    ]
    for row in data.get("ranking", []):
        name = row["detector"]
        f2 = float(data["detectors"][name]["micro"]["f2"])
        info = cost_per_detector.get(name) or {}
        per_1k = info.get("usd_per_1k")
        if per_1k is None:
            cost_s, cpf = "n/a", "n/a"
        elif float(per_1k) == 0.0:
            # A cloud provider at $0 is FREE-TIER (under the provider's quota at this corpus size),
            # NOT free like an on-host local model — keep the distinction honest.
            cost_s = cpf = "free-tier*" if info.get("cloud") else "free"
        else:
            cost_s = f"${float(per_1k):.4f}"
            cpf = f"${float(per_1k) / f2:.4f}" if f2 > 0 else "n/a"
        out.append(f"| {row['rank']} | {name} | {f2:.3f} | {cost_s} | {cpf} |")
    return "\n".join(out) + "\n"


def _require_matplotlib() -> Any:
    """Lazily import matplotlib with the headless Agg backend (the optional ``[viz]`` extra)."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as e:  # pragma: no cover - exercised only on a viz-less checkout
        raise RuntimeError(
            "detector_performance_chart needs the optional 'viz' extra: pip install pii-anon-datasets[viz]"
        ) from e
    return plt


def detector_performance_chart(results: Any, path: str | Path) -> Path:
    """A bar chart of each scored detector's micro F2 (recall-weighted), written to ``path``."""
    data = _as_data(results)
    plt = _require_matplotlib()
    scored = _scored(data)
    f2s = [float(data["detectors"][n]["micro"]["f2"]) for n in scored]

    fig, ax = plt.subplots(figsize=(max(4.0, len(scored) * 0.9), 4.0))
    ax.bar(range(len(scored)), f2s, color="#3b6ea5")
    ax.set_xticks(range(len(scored)))
    ax.set_xticklabels(scored, rotation=30, ha="right")
    ax.set_ylabel("F2 (β=2, recall-weighted)")
    ax.set_ylim(0.0, 1.0)
    ax.set_title("PII detector F2 on PII-Anon — synthetic-only (AX-001)")
    fig.tight_layout()

    out = Path(path)
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out
