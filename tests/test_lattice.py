"""Tests for stats.lattice (FR-029, NFR-018; committed-lattice single source of truth).

Pins: deterministic build; the frozen eval_lattice.json round-trips against the generator
(anti-drift); every target_n is derived (== required_n); forced estimability skeleton covers
every main-effect level; count-gating excludes the domain×eval-family RRS seam.
"""
import json
from pathlib import Path

import pytest

from pii_anon_datasets import taxonomy as tx
from pii_anon_datasets.stats import lattice as L
from pii_anon_datasets.stats import power as pw

FROZEN = Path(__file__).resolve().parent.parent / "src" / "pii_anon_datasets" / "data" / "eval_lattice.json"


def test_build_is_deterministic():
    assert L.build_committed_lattice().to_json() == L.build_committed_lattice().to_json()


def test_frozen_lattice_matches_generator_antidrift():
    # The shipped artifact MUST equal a fresh build (NFR-018 anti-drift round-trip).
    assert FROZEN.read_text(encoding="utf-8") == L.build_committed_lattice().to_json()


def test_targets_are_derived_not_hand_typed():
    lat = json.loads(L.build_committed_lattice().to_json())
    for tier, spec in lat["tier_specs"].items():
        assert spec["target_n"] == pw.required_n(spec["p_ref"], spec["half_width"])
    for c in lat["cells"]:
        assert c["target_n"] == pw.target_for_tier(c["tier"])


def test_forced_skeleton_covers_every_main_effect_level():
    lat = L.build_committed_lattice()
    cells = lat.cells
    type_marginals = {c["dimensions"]["entity_type"] for c in cells
                      if c["interaction"] == "marginal:entity_type"}
    assert type_marginals == set(tx.CANONICAL_ENTITY_TYPES)        # all 66 types
    lang_marginals = {c["dimensions"]["language"] for c in cells
                      if c["interaction"] == "marginal:language"}
    assert len(lang_marginals) == 60                                # all 60 languages
    dom_marginals = {c["dimensions"]["domain"] for c in cells if c["interaction"] == "marginal:domain"}
    assert dom_marginals == set(L.DEFAULT_DOMAINS)


def test_interaction_breakdown():
    from collections import Counter
    lat = L.build_committed_lattice()
    by_int = Counter(c["interaction"] for c in lat.cells)
    assert by_int["language_x_entity_type"] == 697    # 17 head langs × 41 frequent types (2C powered rectangle)
    assert by_int["adversarial_x_entity_type"] == 66   # 3 faithful adv × 22 critical
    assert by_int["domain_x_track"] == 30              # 5×2 adv-track + 5×4 eval-family
    assert lat.cell_count() == 938                      # 733 + (697−492) = +205 new LxE cells (2C)


def test_named_interactions_declared():
    lat = L.build_committed_lattice()
    assert lat.named_interactions == (
        "language_x_entity_type", "domain_x_track", "adversarial_x_entity_type",
    )


def test_domain_eval_family_is_the_only_non_count_gated():
    lat = L.build_committed_lattice()
    seam = [c for c in lat.cells if not c["count_gated"]]
    assert len(seam) == 20                              # 5 domains × 4 eval families
    for c in seam:
        assert c["interaction"] == "domain_x_track"
        assert "eval_family" in c["dimensions"]
    # everything else (incl. domain×adv_track) IS count-gated
    gated = lat.count_gated_cells()
    assert len(gated) == 918                            # 938 total − 20 eval-family seam
    assert all("eval_family" not in c["dimensions"] for c in gated)


def test_lang_x_entity_uses_head_langs_and_frequent_types():
    lat = L.build_committed_lattice()
    lxe = [c for c in lat.cells if c["interaction"] == "language_x_entity_type"]
    langs = {c["dimensions"]["language"] for c in lxe}
    types = {c["dimensions"]["entity_type"] for c in lxe}
    # 2C powered rectangle: the 5 new langs (ru/th/el/bn/he) are now head languages.
    assert {"en", "nl", "ru", "th", "el", "bn", "he"} <= langs and len(langs) == 17  # 17 head langs (≥753)
    assert "PERSON_NAME" in types and len(types) == 41               # frequent types (≥753 positives)
    # a critical type in this rectangle keeps the critical (1522) target (max-of-members)
    iban = next(c for c in lxe if c["dimensions"]["entity_type"] == "IBAN")
    assert iban["tier"] == "critical" and iban["target_n"] == 1522


def test_adv_x_entity_capped_at_standard():
    lat = L.build_committed_lattice()
    axe = [c for c in lat.cells if c["interaction"] == "adversarial_x_entity_type"]
    # all over critical entity types, but the adversarial-robustness target is capped at standard
    assert {c["dimensions"]["entity_type"] for c in axe} == set(tx.types_in_tier("critical"))
    assert all(c["target_n"] == 753 for c in axe)
    assert all(c["dimensions"]["adversarial"] in L.DEFAULT_DETECTION_ADVERSARIAL_TYPES for c in axe)


def test_cell_ids_unique_and_load_roundtrips():
    lat = L.build_committed_lattice()
    ids = [c["id"] for c in lat.cells]
    assert len(ids) == len(set(ids))                    # unique
    on_disk = L.load_lattice(FROZEN)
    assert on_disk["cell_count"] == lat.cell_count()


def test_write_lattice_writes_matching_json(tmp_path):
    out = tmp_path / "lat.json"
    lat = L.write_lattice(out)
    assert out.read_text(encoding="utf-8") == lat.to_json()
    assert L.load_lattice(out)["cell_count"] == lat.cell_count()


def test_main_check_matches_frozen():
    # the shipped eval_lattice.json must match a fresh build (anti-drift CLI used by CI)
    assert L._main(["--check", "--out", str(FROZEN)]) == 0


def test_main_check_detects_drift(tmp_path):
    drifted = tmp_path / "drift.json"
    drifted.write_text('{"cells": []}\n', encoding="utf-8")
    assert L._main(["--check", "--out", str(drifted)]) == 1


def test_main_writes(tmp_path, capsys):
    out = tmp_path / "lat.json"
    assert L._main(["--out", str(out)]) == 0
    assert out.exists()
    assert "committed cells" in capsys.readouterr().out
