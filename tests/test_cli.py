"""S5-05 — `pii-anon` CLI: 5 thin dispatch verbs (FR-024 / DX-03 / NFR-018 / NFR-004).

The CLI is a THIN argparse dispatcher: every verb delegates to its owning subsystem
(``export`` → ``pii_anon_datasets.distribution``; ``validate``/``generate``/``score`` →
a repo script via ``subprocess``; ``leaderboard`` → the S6 seam, graceful until built).
``cli.py`` holds NO business logic.

These tests patch ``subprocess.run`` and the ``distribution`` exporters to assert DISPATCH —
they never actually run ``validate.py``/``generate_records.py`` over the real corpus, nor write a
real Parquet/CoNLL/DocBin. Test names carry ``fr_024``/``nfr_018``/``dx_03``/``nfr004`` tokens so
``pytest -k`` selects.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import sys
from pathlib import Path

import pytest
from pii_anon_datasets import cli

# Source path of the module under test — used by the pure-stdlib AST guard (#8).
_CLI_SOURCE = Path(cli.__file__)


class _FakeCompleted:
    """Stand-in for ``subprocess.CompletedProcess`` (we only need ``.returncode``)."""

    def __init__(self, returncode: int = 0) -> None:
        self.returncode = returncode


# 1. [UNIT-TEST] — the parser registers exactly the five verbs and --help names them.
def test_fr_024_cli_exposes_five_verbs(capsys: pytest.CaptureFixture[str]) -> None:
    parser = cli.build_parser()
    # The subparsers action carries the registered verb names.
    sub_actions = [
        a
        for a in parser._actions
        if isinstance(a, argparse._SubParsersAction)  # type: ignore[attr-defined]
    ]
    assert sub_actions, "build_parser() must register subcommands"
    verbs = set(sub_actions[0].choices)
    assert verbs == {"generate", "score", "export", "validate", "leaderboard", "baselines"}

    with pytest.raises(SystemExit) as exc:
        cli.main(["--help"])
    assert exc.value.code == 0
    help_text = capsys.readouterr().out
    for verb in ("generate", "score", "export", "validate", "leaderboard", "baselines"):
        assert verb in help_text


# 2. [INTEGRATION-TEST] — `export --format parquet` dispatches to distribution.export_parquet.
def test_fr_024_cli_export_dispatches_to_distribution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import pii_anon_datasets.distribution as dist

    captured: dict[str, object] = {}

    def _fake_export_parquet(records, output):  # noqa: ANN001, ANN202 - test double
        captured["records"] = records
        captured["output"] = output
        # Drain a couple of records to prove the CLI hands over a real iterator (it computes nothing).
        captured["first_two"] = [next(iter(records), None)]

    monkeypatch.setattr(dist, "export_parquet", _fake_export_parquet)

    # Point the record source at a tiny synthetic .jsonl so the CLI never reads the frozen corpus.
    src = tmp_path / "mini.jsonl"
    src.write_text('{"record_id": "r1", "text": "x", "annotations": []}\n', encoding="utf-8")
    out = tmp_path / "out.parquet"

    rc = cli.main(["export", "--format", "parquet", "--input", str(src), "--output", str(out)])

    assert rc == 0
    assert captured["output"] == str(out)
    # The CLI passed an ITERATOR/generator (a streaming record source), not a materialised list.
    assert hasattr(captured["records"], "__iter__")
    assert not isinstance(captured["records"], (list, tuple))


# 3. [CONTRACT-TEST] — GUARDRAIL: `validate` keeps the NFR-018 power gate ON.
def test_nfr_018_cli_validate_keeps_power_gate_on(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, list[str]] = {}

    def _fake_run(argv, *args, **kwargs):  # noqa: ANN001, ANN202 - capture the spawned argv
        seen["argv"] = list(argv)
        return _FakeCompleted(0)

    monkeypatch.setattr(cli.subprocess, "run", _fake_run)

    rc = cli.main(["validate"])

    assert rc == 0
    argv = seen["argv"]
    # The delegate IS validate.py …
    assert any(str(a).endswith("validate.py") for a in argv)
    # … and the CLI NEVER injects --no-power-gate (the gate runs by default — NFR-018).
    assert "--no-power-gate" not in argv


# 4. [UNIT-TEST] — `validate --summary-only` forwards the user's arg verbatim (still gate-on).
def test_fr_024_cli_validate_forwards_user_args(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, list[str]] = {}

    def _fake_run(argv, *args, **kwargs):  # noqa: ANN001, ANN202 - capture the spawned argv
        seen["argv"] = list(argv)
        return _FakeCompleted(0)

    monkeypatch.setattr(cli.subprocess, "run", _fake_run)

    rc = cli.main(["validate", "--summary-only"])

    assert rc == 0
    argv = seen["argv"]
    assert any(str(a).endswith("validate.py") for a in argv)
    assert "--summary-only" in argv
    # Forwarding the user's flags must not smuggle in the gate-disabling flag.
    assert "--no-power-gate" not in argv


# 5. [CONTRACT-TEST] — `generate` dispatches to the seeded generator and NEVER targets the frozen corpus.
def test_nfr004_cli_generate_never_targets_frozen_corpus(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, list[str]] = {}

    def _fake_run(argv, *args, **kwargs):  # noqa: ANN001, ANN202 - capture the spawned argv
        seen["argv"] = list(argv)
        return _FakeCompleted(0)

    monkeypatch.setattr(cli.subprocess, "run", _fake_run)

    rc = cli.main(["generate"])

    assert rc == 0
    argv = seen["argv"]
    assert any(str(a).endswith("generate_records.py") for a in argv)
    # No-corpus-regeneration guardrail: the CLI injects NO output path at all, so it can never
    # point the generator at the shipped, frozen corpus. (The script's own default is *_generated.jsonl.)
    joined = " ".join(str(a) for a in argv)
    assert "pii_anon.jsonl.gz" not in joined
    # The CLI passes only the script + interpreter (no injected --output).
    assert "--output" not in argv


# 6. [CONTRACT-TEST] — `leaderboard` is wired to the S6 governance seam (S6-01 landed the package).
def test_fr_024_cli_leaderboard_wired_to_s6_seam(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # S6-01 landed the leaderboard package; the verb now routes to the real `leaderboard.main`.
    # (Pre-S6 this asserted graceful degradation `is None`; S6-01 is the named successor — see
    # tests/test_leaderboard_store.py::test_fr_023_leaderboard_cli_verify for the verb's own contract.)
    assert importlib.util.find_spec("pii_anon_datasets.leaderboard") is not None

    rc = cli.main(["leaderboard"])  # no sub-verb -> the delegate's usage path

    assert rc == 2  # clean non-crash exit code (usage), not an uncaught traceback
    err = capsys.readouterr().err
    assert "usage" in err.lower() and "verify" in err
    # No traceback leaked to the user.
    assert "Traceback" not in err


# 7. [UNIT-TEST] — the console entry point is declared and `main` returns an int.
def test_dx_03_console_entry_point_declared() -> None:
    repo_root = Path(cli._repo_root())
    pyproject = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    assert "[project.scripts]" in pyproject
    assert 'pii-anon = "pii_anon_datasets.cli:main"' in pyproject

    assert callable(cli.main)
    rc = cli.main([])  # no verb → prints help, returns a non-zero int (the console_scripts contract)
    assert isinstance(rc, int)


# 8. [PROPERTY-TEST] — the CLI is thin + pure-stdlib: import works with heavy deps absent,
#    and it imports no clock/RNG/identifier module nor any scoring/stats metric module at top level.
def test_nfr004_cli_thin_pure_stdlib(monkeypatch: pytest.MonkeyPatch) -> None:
    # (a) Importing the CLI must not require pyarrow / spacy / mlcroissant (distribution is lazy).
    import builtins

    real_import = builtins.__import__
    banned_runtime = {"pyarrow", "spacy", "mlcroissant"}

    def _guarded_import(name, *args, **kwargs):  # noqa: ANN001, ANN202 - import hook for the guard
        root = name.split(".")[0]
        if root in banned_runtime:
            raise ImportError(f"{root} is blocked for this test (must be a lazy import)")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _guarded_import)
    for mod in list(sys.modules):
        if mod.split(".")[0] in banned_runtime:
            monkeypatch.delitem(sys.modules, mod, raising=False)
    monkeypatch.delitem(sys.modules, "pii_anon_datasets.cli", raising=False)

    import importlib

    importlib.import_module("pii_anon_datasets.cli")  # must succeed with heavy deps blocked

    # (b) AST guard: cli.py imports none of the non-deterministic stdlib modules at top level …
    tree = ast.parse(_CLI_SOURCE.read_text(encoding="utf-8"))
    top_level_imports: set[str] = set()
    for node in tree.body:  # MODULE TOP LEVEL ONLY — lazy imports inside functions are allowed.
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_level_imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            top_level_imports.add(node.module.split(".")[0])

    banned_nondeterministic = {"random", "time", "uuid", "datetime", "secrets"}
    assert not (top_level_imports & banned_nondeterministic), (
        f"cli.py must be deterministic: forbidden top-level imports {top_level_imports & banned_nondeterministic}"
    )

    # … and no scoring / stats metric module at top level (no business logic in the CLI).
    # Catch both `import pii_anon_datasets.scoring` and `from pii_anon_datasets.scoring import …`.
    banned_business = {"scoring", "stats", "baselines"}
    for node in tree.body:  # MODULE TOP LEVEL ONLY.
        mods: list[str] = []
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods = [node.module]
        for m in mods:
            assert not (set(m.split(".")) & banned_business), (
                f"cli.py must hold no business logic: forbidden top-level import {m!r}"
            )


# --- S5-close coverage hardening: missing-script exit 2, `score` dispatch, the export-format branches ---
# Lift cli.py to >=85% line coverage by exercising the _run_script not-found path, the `score` verb,
# and the conll/spacy/croissant/card export branches (the parquet branch is covered above).


def test_fr_024_run_script_returns_2_when_script_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """[UNIT-TEST] ``_run_script`` returns exit code 2 (and never spawns a subprocess) when the repo
    script is absent — point ``_repo_root`` at an empty tmp dir with no ``scripts/`` (lines 44-46)."""
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)

    # Guard: it must NOT reach subprocess.run when the script is missing.
    def _boom(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202 - must not be called
        raise AssertionError("subprocess.run must not run when the script is missing")

    monkeypatch.setattr(cli.subprocess, "run", _boom)

    rc = cli._run_script("scripts/validate.py", [])

    assert rc == 2
    err = capsys.readouterr().err
    assert "not found" in err and "scripts/validate.py" in err


def test_fr_024_cli_score_dispatches_to_evaluate(monkeypatch: pytest.MonkeyPatch) -> None:
    """[CONTRACT-TEST] ``main(["score", ...])`` dispatches to ``baselines/evaluate.py`` via subprocess
    and forwards the user's arg tail verbatim (line 67 / ``_cmd_score``)."""
    seen: dict[str, list[str]] = {}

    def _fake_run(argv, *args, **kwargs):  # noqa: ANN001, ANN202 - capture the spawned argv
        seen["argv"] = list(argv)
        return _FakeCompleted(0)

    monkeypatch.setattr(cli.subprocess, "run", _fake_run)

    rc = cli.main(["score", "--pred", "preds.jsonl"])

    assert rc == 0
    argv = seen["argv"]
    assert any(str(a).endswith("baselines/evaluate.py") or str(a).endswith("evaluate.py") for a in argv)
    # The user's verbatim tail is forwarded (thin dispatch — no logic, no injected flags).
    assert "--pred" in argv and "preds.jsonl" in argv


def _mini_input(tmp_path: Path) -> Path:
    """A tiny synthetic .jsonl record source so the CLI never reads the frozen corpus."""
    src = tmp_path / "mini.jsonl"
    src.write_text(
        '{"record_id": "r1", "text": "John here", "language": "en", '
        '"annotations": [{"start": 0, "end": 4, "entity_type": "PERSON"}]}\n',
        encoding="utf-8",
    )
    return src


def test_fr_024_cli_export_conll_dispatches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """[INTEGRATION-TEST] ``export --format conll`` dispatches to ``distribution.export_conll`` and
    forwards the ``--conll-format`` choice (lines 88-91)."""
    import pii_anon_datasets.distribution as dist

    captured: dict[str, object] = {}

    def _fake_export_conll(records, output, *, fmt="bio"):  # noqa: ANN001, ANN202 - test double
        captured["output"] = output
        captured["fmt"] = fmt
        next(iter(records), None)  # prove a real iterator is handed over

    monkeypatch.setattr(dist, "export_conll", _fake_export_conll)

    src = _mini_input(tmp_path)
    out = tmp_path / "out.conll"
    rc = cli.main(
        ["export", "--format", "conll", "--input", str(src), "--output", str(out), "--conll-format", "bilou"]
    )

    assert rc == 0
    assert captured["output"] == str(out)
    assert captured["fmt"] == "bilou"


def test_fr_024_cli_export_spacy_dispatches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """[INTEGRATION-TEST] ``export --format spacy`` dispatches to ``distribution.export_spacy_docbin``
    (lines 92-95)."""
    import pii_anon_datasets.distribution as dist

    captured: dict[str, object] = {}

    def _fake_export_spacy(records, output):  # noqa: ANN001, ANN202 - test double
        captured["output"] = output
        next(iter(records), None)

    monkeypatch.setattr(dist, "export_spacy_docbin", _fake_export_spacy)

    src = _mini_input(tmp_path)
    out = tmp_path / "out.spacy"
    rc = cli.main(["export", "--format", "spacy", "--input", str(src), "--output", str(out)])

    assert rc == 0
    assert captured["output"] == str(out)


def test_fr_024_cli_export_croissant_dispatches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """[INTEGRATION-TEST] ``export --format croissant`` calls ``distribution.build_croissant`` and
    writes the JSON-LD to ``--output`` (lines 96-99)."""
    import pii_anon_datasets.distribution as dist

    sentinel = {"@type": "sc:Dataset", "name": "pii-anon-test"}
    monkeypatch.setattr(dist, "build_croissant", lambda **_kw: sentinel)  # tolerate parquet_sha256 kwarg

    out = tmp_path / "croissant.json"
    rc = cli.main(["export", "--format", "croissant", "--output", str(out)])

    assert rc == 0
    written = out.read_text(encoding="utf-8")
    assert '"pii-anon-test"' in written and '"@type"' in written


def test_fr_024_cli_export_croissant_injects_parquet_sha256(tmp_path: Path) -> None:
    """[INTEGRATION-TEST] ``export --format croissant --parquet-sha256 <hex>`` threads the hash into
    ``build_croissant`` so the emitted FileObject carries it — the Croissant spec / mlcroissant require
    a FileObject content hash, and the release step injects the real Parquet sha256. Uses the real
    exporter (build_croissant is pure-stdlib — no pyarrow/mlcroissant needed)."""
    out = tmp_path / "croissant.json"
    sha = "b" * 64
    rc = cli.main(["export", "--format", "croissant", "--output", str(out), "--parquet-sha256", sha])

    assert rc == 0
    written = out.read_text(encoding="utf-8")
    assert f'"sha256": "{sha}"' in written, "CLI must thread --parquet-sha256 into the FileObject"


def test_fr_024_cli_export_card_dispatches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """[INTEGRATION-TEST] ``export --format card`` calls ``distribution.build_dataset_card`` and writes
    the markdown to ``--output`` (lines 100-103)."""
    import pii_anon_datasets.distribution as dist

    monkeypatch.setattr(dist, "build_dataset_card", lambda: "# PII-Anon Dataset Card\n")

    out = tmp_path / "CARD.md"
    rc = cli.main(["export", "--format", "card", "--output", str(out)])

    assert rc == 0
    assert out.read_text(encoding="utf-8") == "# PII-Anon Dataset Card\n"


def test_fr_024_cli_export_card_embeds_baselines(tmp_path: Path) -> None:
    """[INTEGRATION-TEST] ``export --format card --baselines <results.json>`` embeds the F2 leaderboard
    section into the shipped card (the leaderboard wired INTO the dataset card)."""
    import json as _json

    results = {
        "caveat": "real detectors on SYNTHETIC data. Synthetic-only (AX-001).",
        "matching_policy": "strict-v1",
        "dataset": {"split": "test", "language": "en", "n_records": 2000},
        "ranking": [{"rank": 1, "detector": "gliner", "f2_micro": 0.71, "f2_macro": 0.5}],
        "detectors": {
            "gliner": {
                "status": "scored",
                "micro": {"precision": 0.79, "recall": 0.69, "f2": 0.71, "recall_ci": {"low": 0.68, "high": 0.70}},
                "coverage": {"reachable": 23, "of_total": 63},
            }
        },
    }
    bl = tmp_path / "baseline_results.json"
    bl.write_text(_json.dumps(results), encoding="utf-8")
    out = tmp_path / "CARD.md"

    rc = cli.main(["export", "--format", "card", "--baselines", str(bl), "--output", str(out)])

    assert rc == 0
    card = out.read_text(encoding="utf-8")
    assert "## Baseline Detector Performance" in card
    assert "gliner" in card
    assert "Synthetic-only (AX-001)" in card


# --- the `baselines` verb (the detector leaderboard pipeline) ---


def test_fr_024_cli_baselines_list_reports_available(capsys: pytest.CaptureFixture[str]) -> None:
    """[INTEGRATION-TEST] ``baselines --list`` reports the available detectors (regex is always there)
    and never touches the corpus."""
    rc = cli.main(["baselines", "--list"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "regex" in out


def test_fr_024_cli_baselines_runs_offline_detector_end_to_end(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """[INTEGRATION-TEST] ``baselines --detectors regex --input <tiny.jsonl>`` runs end-to-end against an
    injected record source (never the frozen corpus), writes baseline_results.json, and returns 0."""
    src = tmp_path / "mini.jsonl"
    src.write_text(
        '{"record_id": "r1", "text": "Email a@b.com now", "language": "en", "domain": "technology", '
        '"annotations": [{"start": 6, "end": 13, "entity_type": "EMAIL_ADDRESS"}]}\n',
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"
    rc = cli.main(
        ["baselines", "--detectors", "regex", "--input", str(src), "--out", str(out_dir), "--split", "test"]
    )
    assert rc == 0
    results_path = out_dir / "baseline_results.json"
    assert results_path.exists()
    import json as _json

    parsed = _json.loads(results_path.read_text(encoding="utf-8"))
    assert parsed["detectors"]["regex"]["status"] == "scored"


def test_fr_024_cli_baselines_merge_combines_per_detector_runs(tmp_path: Path) -> None:
    """[INTEGRATION-TEST] ``baselines --merge a.json b.json`` unions per-detector run JSONs into one
    F2-ranked leaderboard (the restart-safe census pattern)."""
    import json as _json

    def _mk(name: str, f2: float) -> dict:
        return {
            "matching_policy": "strict-v1",
            "span_matching_disclosure": "strict-v1 … partial …",
            "caveat": "Synthetic-only (AX-001).",
            "confidence": 0.95,
            "dataset": {"split": "test", "language": "en", "dataset_version": "2.0.0", "n_records": 10, "n_gold": 50},
            "ranking": [{"rank": 1, "detector": name, "f2_micro": f2, "f2_macro": f2}],
            "detectors": {
                name: {"status": "scored", "model_id": "", "record_errors": 0,
                       "micro": {"precision": 1.0, "recall": f2, "f1": f2, "f2": f2,
                                 "recall_ci": {"low": 0.0, "high": 1.0}},
                       "coverage": {"reachable": 1, "of_total": 63}}
            },
        }

    a = tmp_path / "a.json"
    a.write_text(_json.dumps(_mk("alpha", 0.9)), encoding="utf-8")
    b = tmp_path / "b.json"
    b.write_text(_json.dumps(_mk("beta", 0.4)), encoding="utf-8")
    out = tmp_path / "merged"

    rc = cli.main(["baselines", "--merge", str(a), str(b), "--out", str(out)])

    assert rc == 0
    merged = _json.loads((out / "baseline_results.json").read_text(encoding="utf-8"))
    assert set(merged["detectors"]) == {"alpha", "beta"}
    assert [r["detector"] for r in merged["ranking"]] == ["alpha", "beta"]  # F2-descending


def test_nfr_cli_baselines_cloud_requires_optin(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """[CONTRACT-TEST] A cloud detector is NOT run without --cloud (budget guard): requesting only `aws`
    without --cloud runs nothing and warns."""
    src = tmp_path / "mini.jsonl"
    src.write_text('{"record_id": "r1", "text": "hi", "language": "en", "annotations": []}\n', encoding="utf-8")
    rc = cli.main(["baselines", "--detectors", "aws", "--input", str(src), "--out", str(tmp_path / "o")])
    err = capsys.readouterr().err
    assert "cloud" in err.lower() and "aws" in err.lower()
    assert rc == 0  # graceful (ran nothing), not a crash
