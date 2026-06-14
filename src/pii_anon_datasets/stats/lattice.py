"""Committed evaluation lattice generator (FR-029, NFR-018; sampling-design.md §2,§4,§5).

Deterministically builds the set of evaluation cells the benchmark COMMITS to powering —
main-effect marginals (forced estimability skeleton) + the three named 2-way interactions —
and freezes it to ``data/eval_lattice.json`` (the single source of truth read by the audit,
the enrichment fill, and ``validate.py --lattice``).

Construction (Broad, per the 2026-05-29 user decision): the curated 2-way commitments are the
**full balanced rectangles** (head-languages × frequent-types; detection-adversarial × critical;
domain × track) — NOT the Cartesian grid — so selection is a deterministic enumeration; the
``seed`` is recorded for provenance and reserved for an optional D-optimal trim (Lean mode).

``count_gated`` marks cells whose power is enforced by the detection-recall positive-count gate
(NFR-018). ``domain × eval-family`` cells are committed but ``count_gated=False`` — their power is
governed by the re-id-operating-point RRS/utility ladder (track-specific power seam, R10 #2),
filled when the S3/S4 anon/pseudo/RRS scorers land.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .. import taxonomy
from . import power

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_METADATA = _DATA_DIR / "pii_anon.metadata.json"
# PINNED design-time frequency snapshot — the lattice membership (head languages / frequent
# types) is frozen here so the committed lattice round-trips (NFR-018 anti-drift) even after
# enrichment changes the live corpus counts. The lattice reads THIS, never live metadata.
_FREQ_SNAPSHOT = _DATA_DIR / "lattice_freq_snapshot.json"
LATTICE_PATH = _DATA_DIR / "eval_lattice.json"

LATTICE_VERSION = "1.0.0"
DEFAULT_SEED = 42

DEFAULT_DOMAINS = ("general", "clinical", "financial", "legal", "technology")
DEFAULT_DIFFICULTIES = ("easy", "moderate", "hard", "challenging")
DEFAULT_DIMENSIONS = (
    "diverse_pii_types", "multilingual", "entity_tracking", "edge_cases",
    "context_preservation", "temporal_consistency", "format_variations",
)
DEFAULT_EVAL_FAMILIES = ("detection", "anonymization", "pseudonymization", "re_identification")
DEFAULT_ADV_TRACKS = ("clean", "adversarial")
# The committed *detection-obfuscation* adversarial types — restricted to those the enrichment
# generator can FAITHFULLY synthesize via a value-level transform (so every committed adv×type
# cell is a genuine attack, not a bare tag; R10 refinement #5). Kept in sync with
# scripts/lattice_targeting.ADVERSARIAL_TRANSFORMS (cross-checked by test). The ESRC/tier-3
# re-id attack types are governed by the RRS ladder, not this detection lattice.
# Restricted to the 3 transforms that RELIABLY perturb ANY value class (incl. digit-only
# SSN/CVV/PIN) so every committed adv×type cell is a genuine attack. Letter-targeting
# transforms (homoglyph/leetspeak/mixed_case) no-op on digit-only values and are therefore
# NOT committed (they remain available in lattice_targeting for value-classes that bear letters).
DEFAULT_DETECTION_ADVERSARIAL_TYPES = (
    "base64_encoding", "ocr_artifact", "zero_width_char",
)

NAMED_INTERACTIONS = ("language_x_entity_type", "domain_x_track", "adversarial_x_entity_type")


@dataclass(frozen=True)
class CommittedLattice:
    lattice_version: str
    seed: int
    source_metadata_version: str
    tier_specs: dict
    named_interactions: tuple
    cells: tuple            # tuple[dict] — each {id, dimensions, tier, target_n, committed, count_gated, interaction}

    def cell_count(self) -> int:
        return len(self.cells)

    def count_gated_cells(self) -> tuple:
        return tuple(c for c in self.cells if c["count_gated"])

    def to_json_obj(self) -> dict:
        return {
            "lattice_version": self.lattice_version,
            "seed": self.seed,
            "source_metadata_version": self.source_metadata_version,
            "tier_specs": self.tier_specs,
            "named_interactions": list(self.named_interactions),
            "cell_count": self.cell_count(),
            "cells": list(self.cells),
        }

    def to_json(self) -> str:
        # Deterministic bytes (NFR-004): sorted keys, fixed indent, trailing newline.
        return json.dumps(self.to_json_obj(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _load_metadata_freqs() -> tuple[Mapping[str, int], Mapping[str, int], str]:
    """Load the PINNED design-time frequency snapshot (falls back to live metadata only to
    bootstrap the snapshot on a fresh project). Reading the pin — not live metadata — is what
    keeps the frozen lattice stable across corpus enrichment (NFR-018 anti-drift)."""
    if _FREQ_SNAPSHOT.exists():
        s = json.loads(_FREQ_SNAPSHOT.read_text(encoding="utf-8"))
        return s["by_language"], s["by_entity_type"], s.get("source_version", "unknown")
    m = json.loads(_METADATA.read_text(encoding="utf-8"))
    dist = m["distributions"]
    return dist["by_language"], dist["by_entity_type"], m.get("version", "unknown")


def _cell(interaction: str, dims: dict, tier: power.Tier, *, count_gated: bool) -> dict:
    code = {
        "language_x_entity_type": "LxE", "adversarial_x_entity_type": "AxE",
        "domain_x_track": "DxT",
    }.get(interaction, "M")
    cid = f"{code}:" + "|".join(f"{k}={dims[k]}" for k in sorted(dims))
    return {
        "id": cid,
        "dimensions": dict(dims),
        "tier": tier.value,
        "target_n": power.target_for_tier(tier),
        "committed": True,
        "count_gated": count_gated,
        "interaction": interaction,
    }


def build_committed_lattice(
    *,
    entity_registry: Mapping[str, str] | None = None,
    lang_records: Mapping[str, int] | None = None,
    entity_positives: Mapping[str, int] | None = None,
    domains: tuple = DEFAULT_DOMAINS,
    difficulties: tuple = DEFAULT_DIFFICULTIES,
    dimensions: tuple = DEFAULT_DIMENSIONS,
    adversarial_types: tuple = DEFAULT_DETECTION_ADVERSARIAL_TYPES,
    eval_families: tuple = DEFAULT_EVAL_FAMILIES,
    adv_tracks: tuple = DEFAULT_ADV_TRACKS,
    head_language_threshold: int = 753,
    frequent_type_threshold: int = 753,
    adversarial_entity_tier_cap: power.Tier = power.Tier.STANDARD,
    seed: int = DEFAULT_SEED,
    lattice_version: str = LATTICE_VERSION,
    source_metadata_version: str | None = None,
) -> CommittedLattice:
    """Deterministically construct the committed lattice (sampling-design.md §4)."""
    registry = entity_registry if entity_registry is not None else taxonomy.ENTITY_REGISTRY
    if lang_records is None or entity_positives is None:
        _lang, _ent, _ver = _load_metadata_freqs()
        lang_records = lang_records or _lang
        entity_positives = entity_positives or _ent
        source_metadata_version = source_metadata_version or _ver
    source_metadata_version = source_metadata_version or "unknown"

    all_languages = sorted(lang_records)
    all_types = sorted(registry)
    head_languages = sorted(l for l in all_languages if lang_records.get(l, 0) >= head_language_threshold)
    frequent_types = sorted(t for t in all_types if entity_positives.get(t, 0) >= frequent_type_threshold)
    critical_types = sorted(t for t in all_types if taxonomy.risk_tier(t) == "critical")

    cells: list[dict] = []

    # ── T1 main-effect marginals (forced estimability skeleton) ──────────────────────────
    for t in all_types:
        cells.append(_cell("marginal:entity_type", {"entity_type": t},
                           power.Tier(taxonomy.risk_tier(t)), count_gated=True))
    for lang in all_languages:
        cells.append(_cell("marginal:language", {"language": lang}, power.Tier.STANDARD, count_gated=True))
    for d in domains:
        cells.append(_cell("marginal:domain", {"domain": d}, power.Tier.STANDARD, count_gated=True))
    for f in difficulties:
        cells.append(_cell("marginal:difficulty", {"difficulty": f}, power.Tier.STANDARD, count_gated=True))
    for a in adversarial_types:
        cells.append(_cell("marginal:adversarial", {"adversarial": a}, power.Tier.STANDARD, count_gated=True))
    for dim in dimensions:
        cells.append(_cell("marginal:dimension", {"dimension": dim}, power.Tier.STANDARD, count_gated=True))

    # ── T2a language × entity_type (the headline rectangle; max-of-members tier) ──────────
    for lang in head_languages:
        for t in frequent_types:
            cells.append(_cell("language_x_entity_type", {"language": lang, "entity_type": t},
                               power.Tier(taxonomy.risk_tier(t)), count_gated=True))

    # ── T2b adversarial × entity_type (detection robustness on critical types; capped) ────
    cap_target = power.target_for_tier(adversarial_entity_tier_cap)
    for a in adversarial_types:
        for t in critical_types:
            member = power.Tier(taxonomy.risk_tier(t))
            tier = member if power.target_for_tier(member) <= cap_target else adversarial_entity_tier_cap
            cells.append(_cell("adversarial_x_entity_type", {"adversarial": a, "entity_type": t},
                               tier, count_gated=True))

    # ── T2c domain × track (BOTH readings) ───────────────────────────────────────────────
    for d in domains:                              # domain × adversarial-track (count-gated)
        for tr in adv_tracks:
            cells.append(_cell("domain_x_track", {"domain": d, "adv_track": tr},
                               power.Tier.STANDARD, count_gated=True))
    for d in domains:                              # domain × evaluation-family (NOT count-gated — RRS seam)
        for fam in eval_families:
            cells.append(_cell("domain_x_track", {"domain": d, "eval_family": fam},
                               power.Tier.STANDARD, count_gated=False))

    cells.sort(key=lambda c: c["id"])              # deterministic ordering (NFR-004)

    tier_specs = {t.value: power.TIER_SPECS[t].as_dict() for t in power.Tier}
    return CommittedLattice(
        lattice_version=lattice_version, seed=seed,
        source_metadata_version=source_metadata_version, tier_specs=tier_specs,
        named_interactions=NAMED_INTERACTIONS, cells=tuple(cells),
    )


def load_lattice(path: Path = LATTICE_PATH) -> dict:
    """Load the frozen committed-lattice spec."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_lattice(path: Path = LATTICE_PATH, **kwargs) -> CommittedLattice:
    """Build + freeze the committed lattice to JSON (deterministic bytes)."""
    lat = build_committed_lattice(**kwargs)
    Path(path).write_text(lat.to_json(), encoding="utf-8")
    return lat


def _main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Build/freeze the committed evaluation lattice.")
    ap.add_argument("--out", type=Path, default=LATTICE_PATH)
    ap.add_argument("--check", action="store_true",
                    help="Verify the on-disk lattice matches a fresh build (anti-drift); exit 1 on drift.")
    args = ap.parse_args(argv)
    lat = build_committed_lattice()
    if args.check:
        on_disk = Path(args.out).read_text(encoding="utf-8") if Path(args.out).exists() else ""
        if on_disk != lat.to_json():
            print(f"DRIFT: {args.out} does not match a fresh build_committed_lattice()")
            return 1
        print(f"OK: {args.out} matches build_committed_lattice() — {lat.cell_count()} cells")
        return 0
    Path(args.out).write_text(lat.to_json(), encoding="utf-8")
    cg = len(lat.count_gated_cells())
    print(f"wrote {args.out} — {lat.cell_count()} committed cells ({cg} count-gated)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
