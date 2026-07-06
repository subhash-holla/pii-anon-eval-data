"""Data integrity manifest (P5; closes assessment gap M2; AX-002 / NFR-004).

Writes ``data/MANIFEST.sha256`` — a deterministic sha256 (stdlib hashlib; no heavy deps) of the
canonical corpus + metadata + schema + lattice spec + every split and subset. This makes
"byte-identical re-run OR hash-pinned delta" machine-checkable and is the archival receipt the
CHANGELOG cites. Also asserts the immutable ``v1.3.0`` archive tag is untouched.

The frozen paper substrate (EX00) is a SEPARATE manifest checked INDEPENDENTLY of the live corpus.
It hashes only Paper 1's immutable inputs (label_maps_63.json, the committed v2.0.0 leaderboard run,
and the results/tier-a + results/per-record evidence). A v2.x corpus regeneration must NOT redden
it — that is the whole point of the split (see ``results/tier-a/EX00_MANIFEST.sha256``).

CLI:
  python scripts/write_manifest.py                 # (re)write the live-corpus manifest
  python scripts/write_manifest.py --check          # recompute + compare corpus; exit 1 on drift
  python scripts/write_manifest.py --frozen         # (re)write the frozen paper-substrate manifest (EX00)
  python scripts/write_manifest.py --frozen-check    # verify the frozen substrate; exit 1 on drift (corpus-independent)
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PKG = REPO_ROOT / "src" / "pii_anon_datasets"
DATA_DIR = PKG / "data"
MANIFEST = DATA_DIR / "MANIFEST.sha256"

# --- Frozen paper substrate (EX00) — decoupled from the live corpus on purpose. ---
RESULTS = REPO_ROOT / "results"
FROZEN_MANIFEST = RESULTS / "tier-a" / "EX00_MANIFEST.sha256"
# The committed v2.0.0 leaderboard run the headline numbers derive from (results/tier-a/SUMMARY.md
# cites this as the source; "zero detector re-runs").
LEADERBOARD = RESULTS / "baselines" / "tier1-en-all" / "baseline_results.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _tracked_files() -> list[Path]:
    files: list[Path] = []
    for name in ("pii_anon.jsonl.gz", "pii_anon.metadata.json", "pii_anon.schema.json",
                 "eval_lattice.json", "lattice_freq_snapshot.json", "label_maps_63.json"):
        p = DATA_DIR / name
        if p.exists():
            files.append(p)
    for sub in ("splits", "subsets"):
        d = PKG / sub
        if d.exists():
            files.extend(sorted(d.rglob("*.jsonl.gz")))
    return sorted(set(files), key=lambda p: str(p.relative_to(REPO_ROOT)))


def compute_manifest() -> str:
    lines = []
    for p in _tracked_files():
        lines.append(f"{_sha256(p)}  {p.relative_to(REPO_ROOT)}")
    tag = v1_3_0_commit()
    header = [f"# pii-anon data manifest (sha256) — {len(lines)} files",
              f"# v1.3.0_tag_commit: {tag or 'UNAVAILABLE'}"]
    return "\n".join(header + lines) + "\n"


def _frozen_files() -> list[Path]:
    """Paper 1's IMMUTABLE substrate — deliberately disjoint from the mutable corpus.

    A v2.2.0 (63->66) corpus regeneration changes pii_anon.jsonl.gz / splits / subsets and so
    reddens ``_tracked_files()``; NONE of those paths appear here, so ``--frozen-check`` stays green
    across a corpus re-baseline. label_maps_63.json is dual-listed (it is also in the live-corpus
    manifest) — that is intentional defense-in-depth, not a conflation.
    """
    files: list[Path] = []
    lm = DATA_DIR / "label_maps_63.json"
    if lm.exists():
        files.append(lm)
    if LEADERBOARD.exists():
        files.append(LEADERBOARD)
    # results/tier-a/** (the paper's numbers + figures) and results/per-record/** (evidence dumps).
    # Exclude the EX00 manifest itself (no self-reference), volatile *.log run logs, dotfiles, and any
    # underscore-prefixed scratch/backup dir (e.g. results/per-record/_v200stale/ — the moved-aside v2.0.0
    # dumps; the `_`-prefix scratch convention also covers results/baselines/_smoke-*, _partial-*, ...).
    for root in (RESULTS / "tier-a", RESULTS / "per-record"):
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.name.startswith(".") or p == FROZEN_MANIFEST or p.suffix == ".log":
                continue
            if any(part.startswith("_") for part in p.relative_to(root).parts):
                continue  # skip underscore-prefixed scratch/backup subtrees
            files.append(p)
    return sorted(set(files), key=lambda p: str(p.relative_to(REPO_ROOT)))


def compute_frozen_manifest() -> str:
    lines = [f"{_sha256(p)}  {p.relative_to(REPO_ROOT)}" for p in _frozen_files()]
    header = [
        f"# pii-anon FROZEN paper substrate (sha256) — {len(lines)} files",
        "# EX00: Paper 1 (PII-Anon-Eval) immutable inputs. Checked INDEPENDENTLY of the live-corpus",
        "#       data/MANIFEST.sha256 — a v2.x corpus regeneration must NOT redden this guard.",
        "#       Re-baseline ONLY on a disclosed change to the frozen substrate itself.",
        f"# leaderboard_source: {LEADERBOARD.relative_to(REPO_ROOT)}",
    ]
    return "\n".join(header + lines) + "\n"


def v1_3_0_commit() -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "v1.3.0^{commit}"],
                             capture_output=True, text=True, timeout=15)
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write/verify the data sha256 manifest (M2).")
    ap.add_argument("--check", action="store_true", help="recompute + compare corpus; exit 1 on drift")
    ap.add_argument("--frozen", action="store_true", help="(re)write the frozen paper-substrate manifest (EX00)")
    ap.add_argument("--frozen-check", action="store_true",
                    help="verify the frozen substrate; exit 1 on drift (independent of the live corpus)")
    args = ap.parse_args(argv)

    # Frozen-substrate path is fully independent: it never touches the corpus or the v1.3.0 tag logic,
    # so a dirty/regenerated corpus cannot affect its verdict.
    if args.frozen or args.frozen_check:
        current = compute_frozen_manifest()
        if args.frozen_check:
            on_disk = FROZEN_MANIFEST.read_text(encoding="utf-8") if FROZEN_MANIFEST.exists() else ""
            if on_disk != current:
                print(f"ERROR: frozen substrate drift — {FROZEN_MANIFEST.relative_to(REPO_ROOT)} "
                      f"does not match recomputed hashes", file=sys.stderr)
                return 1
            print(f"OK: {FROZEN_MANIFEST.relative_to(REPO_ROOT)} matches ({len(_frozen_files())} frozen files)")
            return 0
        FROZEN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        FROZEN_MANIFEST.write_text(current, encoding="utf-8")
        print(f"wrote {FROZEN_MANIFEST.relative_to(REPO_ROOT)} — {len(_frozen_files())} frozen files hashed")
        return 0

    # v1.3.0 tag integrity: if a prior manifest pins a commit, the tag must not have moved.
    tag = v1_3_0_commit()
    if MANIFEST.exists():
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            if line.startswith("# v1.3.0_tag_commit:"):
                pinned = line.split(":", 1)[1].strip()
                if tag and pinned not in ("UNAVAILABLE", tag):
                    print(f"ERROR: v1.3.0 tag moved — manifest pins {pinned}, git has {tag}", file=sys.stderr)
                    return 1

    current = compute_manifest()
    if args.check:
        on_disk = MANIFEST.read_text(encoding="utf-8") if MANIFEST.exists() else ""
        if on_disk != current:
            print(f"ERROR: data manifest drift — {MANIFEST.relative_to(REPO_ROOT)} does not match recomputed hashes", file=sys.stderr)
            return 1
        print(f"OK: {MANIFEST.relative_to(REPO_ROOT)} matches ({len(_tracked_files())} files); v1.3.0 tag intact")
        return 0

    MANIFEST.write_text(current, encoding="utf-8")
    print(f"wrote {MANIFEST.relative_to(REPO_ROOT)} — {len(_tracked_files())} files hashed; "
          f"v1.3.0 tag commit {tag or 'UNAVAILABLE'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
