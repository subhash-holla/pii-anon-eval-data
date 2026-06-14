"""Per-artifact sha256 provenance index (CAP-02 NFR-043; file-level provenance for AX-005 element 4).

Pins each released assessment artifact to the sha256 of its raw file bytes, so a published bundle can be
re-verified file-by-file (a swap or silent edit changes that file's hash — never the whole-bundle hash only).
Mirrors ``sample.py::_corpus_sha256`` (the chunked sha256-of-file-bytes helper) and the runrecord schema/
``harness_version``/INJECTABLE-timestamp pattern: ``generated_at`` is injected for byte-reproducible fixtures,
artifacts are sorted by ``path`` for determinism, and a missing file raises ``FileNotFoundError`` rather than
emitting a fabricated hash. Pure-stdlib (hashlib).
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path

PROVENANCE_SCHEMA = "pii-anon-assessment-provenance-index/v1"
HARNESS_VERSION = "1.0.0"


def sha256_file(path: str | Path) -> str:
    """sha256 of the raw file bytes (chunked; mirrors ``sample.py::_corpus_sha256``). Never fakes a hash:
    a missing file lets ``open`` raise ``FileNotFoundError``."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_provenance_index(
    paths: Iterable[str | Path],
    *,
    harness_version: str = HARNESS_VERSION,
    generated_at: str,
) -> dict:
    """Build the file-level provenance index over ``paths``.

    Returns ``{schema, harness_version, generated_at, artifacts:[{path, sha256, bytes}]}``. Each ``path`` is the
    file's basename; ``artifacts`` are sorted by ``path`` for byte-reproducible output. ``generated_at`` is
    INJECTABLE (same value → identical index). A missing file raises ``FileNotFoundError`` (never a fake hash).
    """
    artifacts: list[dict[str, object]] = []
    for raw in paths:
        p = Path(raw)
        if not p.is_file():  # explicit pre-check → FileNotFoundError even before stat/read races
            raise FileNotFoundError(str(p))
        artifacts.append({"path": p.name, "sha256": sha256_file(p), "bytes": p.stat().st_size})
    artifacts.sort(key=lambda a: a["path"])
    return {
        "schema": PROVENANCE_SCHEMA,
        "harness_version": harness_version,
        "generated_at": generated_at,
        "artifacts": artifacts,
    }


def write_provenance_index(index: dict, out_path: str | Path) -> Path:
    """Write ``index`` as canonical JSON (sorted keys, trailing newline) — byte-reproducible on disk."""
    out = Path(out_path)
    out.write_text(json.dumps(index, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
