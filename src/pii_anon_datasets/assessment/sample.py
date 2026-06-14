"""Powered, lattice-stratified, seeded sampler (CAP-02 DC-17 / FR-032; the §7 algorithm).

For each committed count-gated lattice cell, draw a seeded per-cell reservoir of ``record_id`` s targeting the
cell's NIST-derived ``target_n``; the sample = the union of those reservoirs. REUSES the audited machinery —
``stats/lattice.py::load_lattice`` and ``scripts/lattice_audit.py::{committed_index, record_increments}`` (the
SAME cell-matching the NFR-018 gate uses, so "what we sample" lines up with "what we enforce") — and never
reinvents it. Two bounded streaming passes (combined full-positive count + reservoir-fill, then realized-positive
count over the selected union); ``O(#committed-cells)``-bounded working set; the corpus is never materialized
(NFR-038).

Determinism (AX-002 / NFR-021, repro-01): each cell gets an INDEPENDENT, **string-seeded** child RNG
``random.Random(f"{seed}\\x1f{cell_id}")`` — NOT one shared RNG fanned across cells (Algorithm-R is
order-dependent), and NOT a tuple seed (a tuple falls back to Python's hash-salted ``hash()`` →
non-reproducible across processes; a str seed uses the stable sha512 path). Two draws with the same
``{corpus content_hash, lattice_version, seed}`` are byte-identical.

Presets: ``powered-representative`` (DEFAULT, FR-035 — never silently full, never silently LARGE),
``full-corpus`` (opt-in; descriptive-census, FR-036), ``smoke`` (fast fixed slice, statistically inert, FR-037).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import random
import subprocess
import sys
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path

from pii_anon_datasets.stats import lattice as _lattice

from .manifest import build_manifest, write_manifest
from .verdicts import POWER_OPERATING_POINT, PowerClass, classify_cell, corpus_verdict, shortfall

_REPO_ROOT = Path(__file__).resolve().parents[3]
# scripts/ is not a package; put it on the path to reuse the SAME audit module validate.py + the fill use.
_SCRIPTS = str(_REPO_ROOT / "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import lattice_audit as _audit  # noqa: E402  (scripts/lattice_audit.py)

DEFAULT_CORPUS = _REPO_ROOT / "src" / "pii_anon_datasets" / "data" / "pii_anon.jsonl.gz"
SMOKE_N = 64
PRESETS = ("powered-representative", "full-corpus", "smoke")


@dataclass(frozen=True)
class CellDraw:
    cell_id: str
    tier: str
    target_n: int
    realized_positive_count: int
    full_positive_count: int
    power_class: PowerClass
    power_operating_point: str
    realized_positive_shortfall: int
    dimensions: Mapping[str, object]


@dataclass(frozen=True)
class SampleResult:
    record_ids: tuple[str, ...]
    per_cell: tuple[CellDraw, ...]
    verdict: str
    preset: str
    run_type: str
    seed: int
    inferential_target: str
    repro: dict


class _Reservoir:
    """Incremental Algorithm-R reservoir over record_ids with a LOCAL seeded RNG (single streaming pass)."""

    __slots__ = ("k", "rng", "seen", "items")

    def __init__(self, k: int, rng: random.Random) -> None:
        self.k = max(0, int(k))
        self.rng = rng
        self.seen = 0
        self.items: list[str] = []

    def offer(self, rid: str) -> None:
        self.seen += 1
        if len(self.items) < self.k:
            self.items.append(rid)
        else:
            j = self.rng.randint(0, self.seen - 1)
            if j < self.k:
                self.items[j] = rid


def _iter_corpus(path: Path) -> Iterator[dict]:
    """Stream records from a (gzipped or plain) JSONL corpus — never materializes it (NFR-038)."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def _cell_rng(seed: int, cell_id: str) -> random.Random:
    """Per-cell child RNG via a STRING seed (stable sha512 path; NOT a hash-salted tuple) — repro-01."""
    return random.Random(f"{seed}\x1f{cell_id}")


def draw_sample(
    *,
    corpus_path: str | Path | None = None,
    lattice: dict | None = None,
    preset: str = "powered-representative",
    seed: int,
    run_type: str = "dev",
) -> SampleResult:
    """Draw a sample per ``preset`` and return a :class:`SampleResult` (records + per-cell power + verdict)."""
    if preset not in PRESETS:
        raise ValueError(f"unknown preset {preset!r}; use one of {PRESETS}")
    corpus = Path(corpus_path) if corpus_path is not None else DEFAULT_CORPUS
    lat = lattice if lattice is not None else _lattice.load_lattice()
    cells = [c for c in lat["cells"] if c.get("count_gated")]
    index = _audit.committed_index(lat)
    lattice_version = str(lat.get("lattice_version", "unknown"))
    inferential_target = "descriptive-census" if preset == "full-corpus" else "super-population"

    full_counts: dict[str, int] = {c["id"]: 0 for c in cells}
    reservoirs: dict[str, _Reservoir] = {}
    if preset == "powered-representative":
        reservoirs = {c["id"]: _Reservoir(int(c["target_n"]), _cell_rng(seed, c["id"])) for c in cells}
    selected: set[str] = set()
    smoke_ids: list[str] = []

    # ---- pass 1: full-corpus realized positives (always) + per-cell reservoir / selection ----
    for rec in _iter_corpus(corpus):
        rid = str(rec.get("record_id", ""))
        inc = _audit.record_increments(rec, index)
        for cid, n in inc.items():
            full_counts[cid] += n
        if preset == "full-corpus":
            selected.add(rid)
        elif preset == "smoke":
            if len(smoke_ids) < SMOKE_N:
                smoke_ids.append(rid)
        else:  # powered-representative
            for cid in inc:
                reservoirs[cid].offer(rid)
    if preset == "powered-representative":
        for res in reservoirs.values():
            selected.update(res.items)
    elif preset == "smoke":
        selected = set(smoke_ids)

    # ---- pass 2: realized positives in the SELECTED union (bounded; skipped for full-corpus) ----
    if preset == "full-corpus":
        sample_counts = dict(full_counts)
    else:
        sample_counts = {c["id"]: 0 for c in cells}
        for rec in _iter_corpus(corpus):
            if str(rec.get("record_id", "")) not in selected:
                continue
            for cid, n in _audit.record_increments(rec, index).items():
                sample_counts[cid] += n

    # ---- per-cell 4-state classification against realized positives ----
    per_cell: list[CellDraw] = []
    for c in cells:
        cid = c["id"]
        target = int(c["target_n"])
        ns = int(sample_counts.get(cid, 0))
        nf = int(full_counts.get(cid, 0))
        pc = classify_cell(ns, nf, target, in_envelope=True)
        per_cell.append(
            CellDraw(
                cell_id=cid,
                tier=str(c.get("tier", "")),
                target_n=target,
                realized_positive_count=ns,
                full_positive_count=nf,
                power_class=pc,
                power_operating_point=POWER_OPERATING_POINT,
                realized_positive_shortfall=shortfall(ns, target),
                dimensions=dict(c["dimensions"]),
            )
        )
    per_cell.sort(key=lambda d: d.cell_id)

    verdict = corpus_verdict([d.power_class for d in per_cell])
    repro = {
        "seed": seed,
        "rng_fingerprint": "random.Random(f'{seed}\\x1f{cell_id}') per cell (sha512-stable)",
        "lattice_version": lattice_version,
        "preset": preset,
    }
    return SampleResult(
        record_ids=tuple(sorted(selected)),
        per_cell=tuple(per_cell),
        verdict=verdict,
        preset=preset,
        run_type=run_type,
        seed=seed,
        inferential_target=inferential_target,
        repro=repro,
    )


# --------------------------------------------------------------------------- ENTRY-A CLI (DC-20)
def _corpus_sha256(path: Path) -> str:
    """sha256 of the raw corpus file bytes — pins the content for the manifest repro block (guards swaps)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit() -> str:
    """Best-effort git SHA of the producing tree; 'unknown' if unavailable (never raises)."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(_REPO_ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return proc.stdout.strip() if proc.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def main(argv: list[str] | None = None) -> int:
    """ENTRY-A: draw a sample → write the manifest; stdout = manifest path, stderr = verdict + shortfalls."""
    parser = argparse.ArgumentParser(
        prog="python -m pii_anon_datasets.assessment.sample",
        description="Draw a powered, lattice-stratified, seeded sample of the PII-Anon v2.0.0 corpus "
        "→ a reproducible sample manifest (the L1 seam consumed by `pii-rate-elo assessment`).",
    )
    parser.add_argument("--preset", choices=PRESETS, default="powered-representative",
                        help="powered-representative (default) / full-corpus (opt-in, citable) / smoke (fast CI)")
    parser.add_argument("--seed", type=int, required=True, help="RNG seed (byte-reproducible draw)")
    parser.add_argument("--run-type", default="dev",
                        choices=("smoke", "dev", "leaderboard-submission", "filing-grade"))
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS), help="corpus JSONL(.gz) path")
    parser.add_argument("--lattice", default=None, help="lattice JSON path (default: the frozen committed lattice)")
    parser.add_argument("--out", required=True, help="output manifest path")
    parser.add_argument("--block-on-underpower", action="store_true",
                        help="promote any under-tier cell to a hard halt (GATE-P3)")
    parser.add_argument("--show-cells", action="store_true", help="print every cell's power class to stderr")
    parser.add_argument("--quiet", action="store_true", help="suppress the stderr verdict banner")
    args = parser.parse_args(argv)

    corpus = Path(args.corpus)
    lat = json.loads(Path(args.lattice).read_text(encoding="utf-8")) if args.lattice else None

    result = draw_sample(
        corpus_path=corpus, lattice=lat, preset=args.preset, seed=args.seed, run_type=args.run_type
    )
    manifest = build_manifest(result, corpus_content_hash=_corpus_sha256(corpus), code_commit=_git_commit())
    out = write_manifest(manifest, args.out)

    print(str(out))  # stdout: the machine channel — manifest path only (pipeable; SP-U2)

    shortfalls = [
        c for c in result.per_cell
        if c.realized_positive_shortfall > 0
        and c.power_class in (PowerClass.UNDER_SAMPLED, PowerClass.CORPUS_LIMITED)
    ]
    if not args.quiet:
        print(
            f"[assessment.sample] preset={result.preset} run_type={result.run_type} "
            f"power_verdict={result.verdict} · conditional-on-this-sample · synthetic-only | "
            f"records={len(result.record_ids)} | under-tier cells={len(shortfalls)}",
            file=sys.stderr,
        )
        for c in sorted(shortfalls, key=lambda d: d.realized_positive_shortfall, reverse=True)[:3]:
            remedy = (
                "draw more (raise the sample size)"
                if c.power_class is PowerClass.UNDER_SAMPLED
                else f"IRREDUCIBLE: corpus has only {c.full_positive_count} positives for this cell"
            )
            print(
                f"  - {c.cell_id} [{c.power_class.value}] shortfall={c.realized_positive_shortfall} → {remedy}",
                file=sys.stderr,
            )
        if args.show_cells:
            for c in result.per_cell:
                print(
                    f"    {c.cell_id} {c.power_class.value} "
                    f"n={c.realized_positive_count}/{c.target_n}",
                    file=sys.stderr,
                )

    # GATE-P3 (SP-W2): full-corpus/leaderboard or --block-on-underpower → non-zero exit on any shortfall.
    if shortfalls and (args.preset == "full-corpus" or args.block_on_underpower):
        print("[assessment.sample] GATE-P3 FAIL: under-powered committed cells (see above).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
