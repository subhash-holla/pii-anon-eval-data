"""Data integrity manifest (P5; closes assessment gap M2; AX-002 / NFR-004).

Writes ``data/MANIFEST.sha256`` — a deterministic sha256 (stdlib hashlib; no heavy deps) of the
canonical corpus + metadata + schema + lattice spec + every split and subset. This makes
"byte-identical re-run OR hash-pinned delta" machine-checkable and is the archival receipt the
CHANGELOG cites. Also asserts the immutable ``v1.3.0`` archive tag is untouched.

CLI:
  python scripts/write_manifest.py            # (re)write the manifest
  python scripts/write_manifest.py --check     # recompute + compare; exit 1 on drift
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


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _tracked_files() -> list[Path]:
    files: list[Path] = []
    for name in ("pii_anon.jsonl.gz", "pii_anon.metadata.json", "pii_anon.schema.json",
                 "eval_lattice.json", "lattice_freq_snapshot.json"):
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


def v1_3_0_commit() -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "v1.3.0^{commit}"],
                             capture_output=True, text=True, timeout=15)
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write/verify the data sha256 manifest (M2).")
    ap.add_argument("--check", action="store_true", help="recompute + compare; exit 1 on drift")
    args = ap.parse_args(argv)

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
