"""``pii-anon`` CLI — five THIN dispatch verbs (FR-024 / DX-03).

A console entry point with five verbs, each a pure dispatcher that parses args and delegates to the
owning subsystem — **zero business logic here** (no metric math, no scoring, no file parsing beyond
argparse + a streaming line reader for ``export``):

* ``generate`` → ``scripts/generate_records.py`` (deterministic seeded generator; its own default
  output is ``*_generated.jsonl`` — NEVER the frozen corpus) — subprocess passthrough.
* ``score`` → ``baselines/evaluate.py`` (the span evaluator) — subprocess passthrough.
* ``export`` → :mod:`pii_anon_datasets.distribution` (S5-02/03/04 — parquet / croissant / conll /
  spacy / card) — a LAZY import inside :func:`_cmd_export` so ``import pii_anon_datasets.cli`` works
  with pyarrow/spacy/mlcroissant absent.
* ``validate`` → ``scripts/validate.py`` (the **NFR-018 committed-cell power gate**) — subprocess
  passthrough; forwards the user's args verbatim and **never injects** ``--no-power-gate``.
* ``leaderboard`` → :mod:`pii_anon_datasets.leaderboard` (the S6 governance seam) — lazy import;
  reports "ships in S6" gracefully until the package is built.

``main(argv) -> int`` returns an exit code (the ``console_scripts`` contract). Pure-stdlib
(argparse / subprocess / sys / pathlib / json / gzip); heavy deps stay lazy.
"""

from __future__ import annotations

import argparse
import gzip
import json
import subprocess
import sys
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path


def _repo_root() -> Path:
    """Walk up to the repo root (the dir holding pyproject.toml)."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path(__file__).resolve().parents[2]  # <root>/src/pii_anon_datasets/cli.py -> <root>


def _run_script(rel_path: str, args: Sequence[str]) -> int:
    """Spawn a repo script as a subprocess; return its exit code. Thin — no logic, no arg injection."""
    script = _repo_root() / rel_path
    if not script.exists():
        print(f"pii-anon: {rel_path} not found (run from a source checkout)", file=sys.stderr)
        return 2
    # Trusted invocation: fixed repo-script path under _repo_root(), no shell=True, no untrusted
    # interpolation (args are the user's verbatim CLI tail, forwarded to a known repo script).
    return subprocess.run([sys.executable, str(script), *args]).returncode  # noqa: S603


def _iter_jsonl(path: Path) -> Iterator[dict[str, object]]:
    """Stream records from a .jsonl(.gz) file (plumbing — not business logic)."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


# ---- thin verb handlers: parse -> delegate ----
def _cmd_generate(args: argparse.Namespace) -> int:
    return _run_script("scripts/generate_records.py", args.rest)  # default output is *_generated.jsonl


def _cmd_score(args: argparse.Namespace) -> int:
    return _run_script("baselines/evaluate.py", args.rest)


def _cmd_validate(args: argparse.Namespace) -> int:
    # GUARDRAIL (NFR-018): forward the user's args verbatim; NEVER inject --no-power-gate. The gate
    # runs by default; only the user may opt out by passing --no-power-gate through `rest`.
    return _run_script("scripts/validate.py", args.rest)


_EXPORTERS = ("parquet", "conll", "spacy", "croissant", "card")


def _cmd_export(args: argparse.Namespace) -> int:
    from pii_anon_datasets import get_data_path  # lazy

    src = Path(args.input) if args.input else (get_data_path() / "pii_anon.jsonl.gz")
    fmt = args.format
    if fmt == "parquet":
        from pii_anon_datasets.distribution import export_parquet
        from pii_anon_datasets.distribution.parquet_export import infer_union_schema

        # First pass builds the FULL union schema (so a column appearing only in later records is not
        # dropped); the second pass streams the rows conformed to it. Two passes over the file — bounded
        # memory — keep every split/subset export on one shared, complete schema.
        schema = infer_union_schema(_iter_jsonl(src))
        export_parquet(_iter_jsonl(src), args.output, schema=schema)
    elif fmt == "conll":
        from pii_anon_datasets.distribution import export_conll

        export_conll(_iter_jsonl(src), args.output, fmt=args.conll_format)
    elif fmt == "spacy":
        from pii_anon_datasets.distribution import export_spacy_docbin

        export_spacy_docbin(_iter_jsonl(src), args.output)
    elif fmt == "croissant":
        from pii_anon_datasets.distribution import build_croissant

        jsonld = build_croissant(parquet_sha256=args.parquet_sha256)
        Path(args.output).write_text(json.dumps(jsonld, indent=2, ensure_ascii=False), "utf-8")
    elif fmt == "card":
        from pii_anon_datasets.distribution import build_dataset_card

        if args.baselines:
            baseline_results = json.loads(Path(args.baselines).read_text(encoding="utf-8"))
            card = build_dataset_card(baseline_results=baseline_results)
        else:
            card = build_dataset_card()
        Path(args.output).write_text(card, encoding="utf-8")
    print(f"pii-anon: wrote {fmt} -> {args.output}")
    return 0


def _cmd_leaderboard(args: argparse.Namespace) -> int:
    try:
        # `leaderboard` is built in S6 and is genuinely absent now; the ImportError below is the
        # graceful-degradation contract (test #6). `# type: ignore[attr-defined]` because mypy --strict
        # resolves the package and (correctly) sees no `leaderboard` attribute until S6 lands it.
        from pii_anon_datasets import leaderboard  # type: ignore[attr-defined]  # built in S6
    except ImportError:
        print(
            "pii-anon leaderboard: ships in the S6 governance seam — not yet available",
            file=sys.stderr,
        )
        return 2
    return int(leaderboard.main(args.rest))  # wired in S6


def _sha256_path(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _records_content_hash(records: Iterable[dict[str, object]]) -> str:
    """A deterministic sha256 over each record's id + text — identifies the exact scored slice."""
    import hashlib

    h = hashlib.sha256()
    for r in records:
        h.update(str(r.get("record_id", "")).encode("utf-8"))
        h.update(b"\x1f")
        h.update(str(r.get("text", "")).encode("utf-8"))
        h.update(b"\x1e")
    return h.hexdigest()


def _git_commit() -> str:
    try:
        proc = subprocess.run(  # noqa: S603 - fixed argv, no shell, no untrusted input
            ["git", "rev-parse", "--short", "HEAD"], cwd=str(_repo_root()), capture_output=True, text=True
        )
        return proc.stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001 - provenance must degrade gracefully, never crash the run
        return "unknown"


def _dataset_version() -> str:
    try:
        from importlib.metadata import version

        return version("pii-anon-datasets")
    except Exception:  # noqa: BLE001
        return ""


def _baselines_progress_printer():  # noqa: ANN202 - returns an event-sink closure
    """A stderr progress sink for ``pii-anon baselines`` — stamps wall-clock onto the orchestrator's
    clock-free events and renders %, rec/s, and ETA so a long census is transparent (not a black box)."""
    import time

    started: dict[str, float] = {}

    def cb(ev: dict) -> None:
        e = ev.get("event")
        det = str(ev.get("detector", "?"))
        now = time.monotonic()
        if e == "detector_start":
            started[det] = now
            print(f"[baselines] ▶ {det}: starting ({ev.get('total', '?')} records)…", file=sys.stderr, flush=True)
        elif e == "built":
            print(f"[baselines]   {det}: model loaded ({now - started.get(det, now):.0f}s)", file=sys.stderr, flush=True)
        elif e == "records":
            el = max(now - started.get(det, now), 1e-9)
            done, total = int(ev["done"]), int(ev["total"])
            rate = done / el
            eta_m = ((total - done) / rate) / 60 if rate > 0 else 0.0
            print(
                f"[baselines]   {det}: {done}/{total} ({100 * done / total:.0f}%)  {rate:.1f} rec/s  ETA {eta_m:.0f}m",
                file=sys.stderr,
                flush=True,
            )
        elif e == "detector_done":
            el_m = (now - started.get(det, now)) / 60
            print(
                f"[baselines] ✓ {det}: done in {el_m:.1f}m  F2={float(ev.get('f2', 0.0)):.3f}  "
                f"({ev.get('record_errors', 0)} record-errors)",
                file=sys.stderr,
                flush=True,
            )
        elif e == "detector_skipped":
            print(f"[baselines] – {det}: skipped ({ev.get('reason')})", file=sys.stderr, flush=True)
        elif e == "detector_error":
            print(f"[baselines] ✗ {det}: errored ({ev.get('error')})", file=sys.stderr, flush=True)

    return cb


def _cmd_baselines_merge(args: argparse.Namespace) -> int:
    """`--merge`: combine per-detector/per-group run JSONs (the restart-safe census pattern) into one
    F2-ranked leaderboard + emit the canonical artifacts."""
    import glob as _glob
    from datetime import datetime, timezone

    from pii_anon_datasets.baselines import orchestrator
    from pii_anon_datasets.baselines.provenance import emit_baseline_artifacts
    from pii_anon_datasets.baselines.results import BaselineResults
    from pii_anon_datasets.reporting.baselines import render_baseline_leaderboard

    paths: list[str] = []
    for pattern in args.merge:
        paths.extend(sorted(_glob.glob(pattern)) or ([pattern] if Path(pattern).exists() else []))
    if not paths:
        print("pii-anon baselines --merge: no result files matched", file=sys.stderr)
        return 2
    loaded = [BaselineResults.from_dict(json.loads(Path(p).read_text(encoding="utf-8"))) for p in paths]
    merged = orchestrator.merge_results(loaded)
    ts = datetime.now(timezone.utc).isoformat()
    out_paths = emit_baseline_artifacts(
        merged, args.out, run_id=f"baselines-merge-{args.seed}", seed=args.seed,
        code_commit=_git_commit(), content_hash="merged", timestamp=ts, generated_at=ts,
    )
    print(render_baseline_leaderboard(merged))
    print(f"pii-anon baselines: merged {len(paths)} runs -> {out_paths['results']}")
    return 0


def _cmd_baselines(args: argparse.Namespace) -> int:
    # Lazy imports keep `import pii_anon_datasets.cli` pure-stdlib (no scoring/stats/baselines/clock at top
    # level — NFR-004 AST guard + the thin-CLI contract). The orchestrator owns all metric logic.
    from datetime import datetime, timezone

    from pii_anon_datasets.baselines import registry, run

    if args.merge:
        return _cmd_baselines_merge(args)

    if args.list:
        avail = registry.available_detectors(include_cloud=args.cloud)
        print("available detectors: " + (", ".join(avail) if avail else "(none)"))
        return 0

    if args.detectors:
        names = [n.strip() for n in args.detectors.split(",") if n.strip()]
    else:
        names = list(registry.available_detectors(include_cloud=False))

    # GUARDRAIL: cloud DLP detectors NEVER run without explicit --cloud opt-in (budget-gated).
    cloud_requested = [n for n in names if n in registry.CLOUD_DETECTORS]
    if cloud_requested and not args.cloud:
        print(
            f"pii-anon baselines: cloud detectors {cloud_requested} require --cloud (budget-gated) — skipping",
            file=sys.stderr,
        )
        names = [n for n in names if n not in registry.CLOUD_DETECTORS]

    if args.input:
        records = list(_iter_jsonl(Path(args.input)))
        content_hash = _sha256_path(Path(args.input))
    else:
        from pii_anon_datasets import load_dataset

        language = None if args.languages in ("", "all") else args.languages
        records = load_dataset(split=args.split, language=language)
        content_hash = _records_content_hash(records)
    if args.limit:
        records = records[: args.limit]

    if not names:
        print("pii-anon baselines: no detectors to run", file=sys.stderr)
        return 0

    ts = datetime.now(timezone.utc).isoformat()
    progress = None if args.quiet else _baselines_progress_printer()
    out = run.run_baselines(
        records,
        names,
        out_dir=args.out,
        dataset_info={"split": args.split, "language": args.languages, "dataset_version": _dataset_version()},
        run_id=f"baselines-{args.split}-{args.languages}-{args.seed}",
        seed=args.seed,
        code_commit=_git_commit(),
        content_hash=content_hash,
        timestamp=ts,
        generated_at=ts,
        progress=progress,
    )
    from pii_anon_datasets.reporting.baselines import render_baseline_leaderboard

    print(render_baseline_leaderboard(out["results"]))
    print(f"pii-anon baselines: wrote {out['paths']['results']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pii-anon", description="PII-Anon benchmark CLI")
    sub = parser.add_subparsers(dest="verb")
    # Passthrough verbs declare NO options of their own: their entire CLI tail is forwarded verbatim
    # to the delegate (captured via `parse_known_args` in `main`, including a leading `--flag`). Using
    # `parse_known_args` rather than a `nargs=REMAINDER` positional is the §8b deviation — REMAINDER
    # drops a leading option-like token (e.g. `validate --summary-only`), which would break NFR-018
    # arg-forwarding; see story §12. The handlers still read the forwarded tail off `args.rest`.
    for verb, fn in (
        ("generate", _cmd_generate),
        ("score", _cmd_score),
        ("validate", _cmd_validate),
        ("leaderboard", _cmd_leaderboard),
    ):
        sp = sub.add_parser(verb)
        sp.set_defaults(func=fn)
    ex = sub.add_parser("export")
    ex.add_argument("--format", choices=_EXPORTERS, default="parquet")
    ex.add_argument("--output", required=True)
    ex.add_argument("--input", default=None)
    ex.add_argument("--conll-format", dest="conll_format", choices=("bio", "bilou"), default="bio")
    ex.add_argument("--baselines", default=None, help="baseline_results.json to embed in the --format card output")
    ex.add_argument("--parquet-sha256", default=None, help="sha256 of the built Parquet, embedded in the --format croissant FileObject (the spec requires md5/sha256)")
    ex.set_defaults(func=_cmd_export)
    # `baselines` owns its options (like `export`): runs the detector leaderboard pipeline. Cloud DLP
    # detectors stay behind --cloud (budget-gated); the heavy logic lives in pii_anon_datasets.baselines.
    bl = sub.add_parser("baselines")
    bl.add_argument("--detectors", default=None, help="comma-separated names (default: available local detectors)")
    bl.add_argument("--split", default="test")
    bl.add_argument("--languages", default="en", help="single BCP-47 code, or 'all' for no language filter")
    bl.add_argument("--limit", type=int, default=None)
    bl.add_argument("--out", default="results/baselines")
    bl.add_argument("--seed", type=int, default=20260603)
    bl.add_argument("--input", default=None, help="optional .jsonl record source (bypasses the packaged split)")
    bl.add_argument("--cloud", action="store_true", help="opt in to the budget-gated cloud DLP detectors")
    bl.add_argument("--list", action="store_true", help="list available detectors and exit")
    bl.add_argument("--quiet", action="store_true", help="suppress the live per-detector progress (stderr)")
    bl.add_argument(
        "--merge", nargs="*", default=None,
        help="merge per-detector run JSONs (paths/globs) into one F2 leaderboard at --out, then exit",
    )
    bl.set_defaults(func=_cmd_baselines)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    # `parse_known_args` forwards the verbatim CLI tail (incl. a leading `--flag`) to passthrough
    # delegates; the export verb still validates its OWN declared options (e.g. required --output).
    args, rest = parser.parse_known_args(argv)
    args.rest = rest  # the delegate's verbatim arg tail (never mutated — NFR-018: no injected flags)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 1
    return int(func(args))


if __name__ == "__main__":
    raise SystemExit(main())
