"""Tests for reporting.viz (S4-05 visualization layer — DC-09 D3 Information-Dense reports).

The five report visualizations behind the optional ``[viz]`` extra (matplotlib): the
**reliability diagram** (FR-005 calibration), the **privacy-utility Pareto plot** (FR-006), the
**slice heatmap** (NFR-003, delegating to ``PowerMatrix.heatmap``), the **agent-leakage Sankey**,
and the **abstention coverage-risk curve** (FR-005 selective-prediction facet — flagged at the
S4-03 gate, closed here).

matplotlib lives behind the ``[viz]`` extra, so this module pins it with
``pytest.importorskip("matplotlib")`` + ``matplotlib.use("Agg")`` (headless; no display). In THIS
env matplotlib IS installed, so the PNG-writing tests RUN (they do not skip). All PNGs are written
to ``tmp_path`` (no real-FS writes outside the tempdir — AX-002 determinism).

LOAD-BEARING:
* **NFR-005 / AX-004** — ``pareto_plot`` takes thin ``(residual_risk, utility, label)`` tuples
  (two axes), NEVER a merged scalar; ``reporting/viz.py`` must NOT hard-import ``scoring`` (it
  duck-types its inputs). The Pareto plot puts privacy on one axis and utility on the other.
* **NFR-004 lazy import** — ``import matplotlib`` lives ONLY inside ``_require_matplotlib``; the
  ``reporting`` package (and ``reporting.viz`` module) import cleanly WITHOUT matplotlib at module
  load. ``test_nfr004_reporting_core_imports_without_matplotlib`` proves the package import path;
  ``test_nfr004_viz_no_toplevel_matplotlib_import`` is an AST guard pinning that ``viz.py`` has no
  module-level ``import matplotlib``.

Each test name carries an ``fr_005`` / ``fr_006`` / ``nfr_003`` / ``nfr004`` / ``fr005`` token.
PNG byte-equality is NOT asserted (matplotlib embeds timestamps) — tests assert the file is
written, non-empty, and (where checked) carries the PNG magic header.
"""
from __future__ import annotations

import ast
import importlib
import pathlib

import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")  # headless backend — no display, deterministic-enough for "PNG written"

from pii_anon_datasets.reporting import viz  # noqa: E402  (after importorskip — intentional)

# PNG 8-byte file signature (\x89PNG\r\n\x1a\n) — a render fn must produce a real PNG.
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


# ── thin fixtures (duck-typed; viz never imports scoring/stats concrete types) ──────────────
class _Bin:
    """A CalibrationResult.reliability bin (duck-typed): only .conf_mean / .acc / .count read."""

    def __init__(self, conf_mean: float, acc: float, count: int) -> None:
        self.conf_mean = conf_mean
        self.acc = acc
        self.count = count


class _Calib:
    """A CalibrationResult-shaped object (duck-typed): only .reliability is consumed by viz."""

    def __init__(self, reliability: tuple[_Bin, ...]) -> None:
        self.reliability = reliability


class _FakePowerMatrix:
    """Records that slice_heatmap delegated to .heatmap(path) and writes a real PNG itself."""

    def __init__(self) -> None:
        self.heatmap_called_with: str | None = None

    def heatmap(self, path: str) -> None:
        self.heatmap_called_with = path
        pathlib.Path(path).write_bytes(_PNG_MAGIC + b"delegated")


def _calib() -> _Calib:
    return _Calib(
        reliability=(
            _Bin(0.05, 0.00, 3),
            _Bin(0.25, 0.20, 5),
            _Bin(0.55, 0.60, 8),
            _Bin(0.85, 0.90, 10),
            _Bin(0.95, 1.00, 4),
        )
    )


def _assert_nonempty_png(path: str) -> None:
    p = pathlib.Path(path)
    assert p.exists(), f"render fn did not write {path}"
    data = p.read_bytes()
    assert len(data) > 0, "render fn wrote an empty file"
    assert data[:8] == _PNG_MAGIC, "written file is not a PNG (missing magic header)"


# ── 1. reliability diagram (FR-005) ─────────────────────────────────────────────────────────
def test_fr_005_reliability_diagram_writes_png(tmp_path: pathlib.Path) -> None:
    out = str(tmp_path / "reliability.png")
    returned = viz.reliability_diagram(_calib(), out)
    assert returned == out
    _assert_nonempty_png(out)


# ── 2. privacy-utility Pareto plot (FR-006) — TWO-AXIS thin tuples (NFR-005) ─────────────────
def test_fr_006_pareto_plot_writes_png(tmp_path: pathlib.Path) -> None:
    # thin (residual_risk, utility, label) points — NOT a merged scalar; viz never imports scoring.
    points = [
        (0.12, 0.91, "presidio"),
        (0.04, 0.78, "llm-redactor"),
        (0.30, 0.97, "regex-baseline"),
    ]
    out = str(tmp_path / "pareto.png")
    returned = viz.pareto_plot(points, out)
    assert returned == out
    _assert_nonempty_png(out)


# ── 3. slice heatmap (NFR-003) — delegates to PowerMatrix.heatmap ───────────────────────────
def test_nfr_003_slice_heatmap_writes_png(tmp_path: pathlib.Path) -> None:
    pm = _FakePowerMatrix()
    out = str(tmp_path / "heatmap.png")
    returned = viz.slice_heatmap(pm, out)
    assert returned == out
    assert pm.heatmap_called_with == out, "slice_heatmap must delegate to power_matrix.heatmap(path)"
    _assert_nonempty_png(out)


# ── 4. abstention coverage-risk curve (FR-005 selective-prediction facet) ───────────────────
def test_fr_005_coverage_risk_curve_writes_png(tmp_path: pathlib.Path) -> None:
    # selective prediction: as low-confidence predictions are abstained, coverage drops, accuracy rises.
    confidences = [0.95, 0.90, 0.80, 0.70, 0.60, 0.55, 0.40, 0.30, 0.20, 0.10]
    correct = [1, 1, 1, 1, 0, 1, 0, 0, 1, 0]
    out = str(tmp_path / "coverage_risk.png")
    returned = viz.coverage_risk_curve(confidences, correct, out)
    assert returned == out
    _assert_nonempty_png(out)


# ── 5. agent-leakage Sankey — thin LeakageEdge tuples ───────────────────────────────────────
def test_fr_005_agent_leakage_sankey_writes_png(tmp_path: pathlib.Path) -> None:
    edges = [
        viz.LeakageEdge("user_prompt", "tool_call", 12.0),
        viz.LeakageEdge("tool_call", "log_sink", 7.0),
        viz.LeakageEdge("tool_call", "model_output", 5.0),
    ]
    out = str(tmp_path / "sankey.png")
    returned = viz.agent_leakage_sankey(edges, out)
    assert returned == out
    _assert_nonempty_png(out)


# ── 6. import-guard message names the [viz] extra (NFR-004) ──────────────────────────────────
def test_nfr004_viz_behind_extra_import_guards(monkeypatch: pytest.MonkeyPatch) -> None:
    # simulate matplotlib being ABSENT: _require_matplotlib must raise a clear RuntimeError that
    # names the install command, NOT a bare ImportError.
    import builtins

    real_import = builtins.__import__

    def _blocked(name: str, *args: object, **kwargs: object) -> object:
        if name == "matplotlib" or name.startswith("matplotlib."):
            raise ImportError("No module named 'matplotlib'")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", _blocked)
    with pytest.raises(RuntimeError) as exc:
        viz._require_matplotlib()
    msg = str(exc.value)
    assert "pip install pii-anon-datasets[viz]" in msg, "guard must name the install command"


# ── 7. reporting package imports without matplotlib at module load (NFR-004 lazy) ───────────
def test_nfr004_reporting_core_imports_without_matplotlib() -> None:
    # importing the package (and viz module) must NOT have triggered a matplotlib import; sys.modules
    # may already hold matplotlib (it's installed) — so we prove laziness structurally: re-importing
    # reporting with matplotlib import sabotaged still succeeds.
    import builtins
    import sys

    real_import = builtins.__import__

    def _blocked(name: str, *args: object, **kwargs: object) -> object:
        if name == "matplotlib" or name.startswith("matplotlib."):
            raise ImportError("blocked: proving reporting import is matplotlib-free")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    saved = {k: v for k, v in sys.modules.items() if k.startswith("matplotlib")}
    for k in list(saved):
        del sys.modules[k]
    for mod in ("pii_anon_datasets.reporting", "pii_anon_datasets.reporting.viz"):
        sys.modules.pop(mod, None)
    builtins.__import__ = _blocked
    try:
        pkg = importlib.import_module("pii_anon_datasets.reporting")
        assert hasattr(pkg, "reliability_diagram"), "viz fns must be re-exported by reporting"
        assert hasattr(pkg, "pareto_plot")
    finally:
        builtins.__import__ = real_import
        sys.modules.update(saved)
        importlib.import_module("pii_anon_datasets.reporting.viz")  # restore a clean module


def test_nfr004_viz_no_toplevel_matplotlib_import() -> None:
    # AST guard: viz.py must have NO module-level `import matplotlib` / `from matplotlib import ...`.
    # matplotlib may ONLY be imported inside a function body (the lazy _require_matplotlib).
    src = pathlib.Path(viz.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    offenders: list[int] = []
    for node in tree.body:  # MODULE-LEVEL statements only
        if isinstance(node, ast.Import):
            if any(a.name == "matplotlib" or a.name.startswith("matplotlib.") for a in node.names):
                offenders.append(node.lineno)
        elif isinstance(node, ast.ImportFrom):
            if node.module and (node.module == "matplotlib" or node.module.startswith("matplotlib.")):
                offenders.append(node.lineno)
    assert not offenders, f"viz.py has top-level matplotlib import(s) at line(s) {offenders} (must be lazy)"


# ── 8. pyproject declares the [viz] extra (so power.py::heatmap's install hint resolves) ────
def test_fr_005_pyproject_declares_viz_extra() -> None:
    try:
        import tomllib  # py3.11+
    except ModuleNotFoundError:  # pragma: no cover - py3.10 fallback
        import tomli as tomllib  # type: ignore[no-redef]
    root = pathlib.Path(__file__).resolve().parents[1]
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    extras = data["project"]["optional-dependencies"]
    assert "viz" in extras, "pyproject must declare a [viz] optional-dependency group"
    assert any("matplotlib" in dep for dep in extras["viz"]), "the viz extra must include matplotlib"
