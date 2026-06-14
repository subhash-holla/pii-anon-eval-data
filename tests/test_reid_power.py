"""S3-08 — the RE-ID-operating-point power ladder seam (NFR-018; sampling-design.md §5).

A PARALLEL ladder in ``stats/power.py`` for the anonymization/pseudonymization/RRS tracks,
whose denominator is paired personas / candidate-set ``|C|`` and whose operating point is
``p≈0.1–0.5`` — distinct from the detection-recall tiers (1522/753/200). It reuses the SAME
``required_n``/``_z`` closed form (one z-table) so design and measured share one statistic.

Load-bearing invariants pinned here:
  * the §5 numbers REID_HIGH(0.30, d=±3pp)→897 and REID_LOW(0.10)→385 (test 1; derived test 2);
  * ``ReidProvenance.track == "reidentification"`` with a non-strippable caveat (test 3) that
    attaches to ``MeasuredRRS`` and survives serialization (test 4);
  * the seam is CODE-ONLY: it does NOT mutate the FROZEN detection ``eval_lattice.json`` — its
    committed cell count is unchanged (test 5, the regression guard; pinned to the read value).
"""
import json
from pathlib import Path

import pytest
from pii_anon_datasets.scoring import ANTI_ANONYMITY_CAVEAT
from pii_anon_datasets.scoring.reidentification import (
    MeasuredRRS,
    score_reidentification,
)
from pii_anon_datasets.stats import power as pw
from pii_anon_datasets.stats.intervals import wilson_interval

# The committed detection lattice (FROZEN; built from the pinned lattice_freq_snapshot.json).
# This story's seam must NOT add a single cell to it. The count below was READ from the file
# at story time (cell_count field == len(cells) == 730) and is PINNED here as the guard.
_EVAL_LATTICE = Path(__file__).resolve().parents[1] / (
    "src/pii_anon_datasets/data/eval_lattice.json"
)
_FROZEN_LATTICE_CELL_COUNT = 730


# ── 1. the §5 operating-point numbers are pinned (idiom from test_power.py) ───────────────
def test_nfr_018_reid_required_n_pins_section5_numbers():
    # RE-ID operating point (paired personas / |C|), NOT detection recall:
    #   REID_HIGH p_ref=0.30, half-width d=±3pp → 897 pairs
    #   REID_LOW  p_ref=0.10, half-width d=±3pp → 385 pairs
    assert pw.reid_required_n(0.30, 0.030) == 897
    assert pw.reid_required_n(0.10, 0.030) == 385
    # same closed form as the detection-recall sizer (one z-table, two semantic entry points):
    assert pw.reid_required_n(0.30, 0.030) == pw.required_n(0.30, 0.030)
    assert pw.reid_required_n(0.10, 0.030) == pw.required_n(0.10, 0.030)


# ── 2. REID_TIER_SPECS targets are DERIVED from (p_ref, d), never hand-typed (anti-drift) ──
def test_nfr_018_reid_tier_specs_are_derived_not_typed():
    assert set(pw.REID_TIER_SPECS) == set(pw.ReidTier)
    for tier, spec in pw.REID_TIER_SPECS.items():
        assert spec.tier is tier
        # the target is the closed-form output, not a literal baked into the table
        assert spec.target_n_pairs == pw.reid_required_n(spec.p_ref, spec.half_width)
    # and the two named operating points land on the §5 figures
    assert pw.REID_TIER_SPECS[pw.ReidTier.REID_HIGH].target_n_pairs == 897
    assert pw.REID_TIER_SPECS[pw.ReidTier.REID_LOW].target_n_pairs == 385


# ── 3. ReidProvenance shape: reid track, |C|, powered, non-strippable caveat ──────────────
def test_nfr_018_reid_provenance_shape():
    prov = pw.ReidProvenance(
        target_n_pairs=897,
        observed_pairs=900,
        candidate_set_size=50,
        adversary_id="offline-deterministic-v1",
        reid_tier=pw.ReidTier.REID_HIGH.value,
    )
    # distinct from the DETECTION track — this is the re-id operating point
    assert prov.track == "reidentification"
    assert prov.candidate_set_size == 50
    assert prov.adversary_id == "offline-deterministic-v1"
    assert prov.target_n_pairs == 897 and prov.observed_pairs == 900
    # powered == (observed >= target)
    assert prov.powered is True
    assert pw.ReidProvenance(
        target_n_pairs=897, observed_pairs=896, candidate_set_size=50,
        adversary_id="offline-deterministic-v1",
    ).powered is False
    # the anti-anonymity caveat is the non-strippable default and is serialized
    assert prov.caveat == ANTI_ANONYMITY_CAVEAT
    d = prov.as_dict()
    assert d["track"] == "reidentification"
    assert d["candidate_set_size"] == 50
    assert d["caveat"] == ANTI_ANONYMITY_CAVEAT
    assert d["powered"] is True
    # __post_init__ rejects an empty caveat (cannot construct a caveat-less reid provenance)
    with pytest.raises(ValueError):
        pw.ReidProvenance(
            target_n_pairs=897, observed_pairs=900, candidate_set_size=50,
            adversary_id="offline-deterministic-v1", caveat="   ",
        )


# ── 4. ReidProvenance attaches to MeasuredRRS and survives as_dict() ──────────────────────
def test_nfr_018_reid_provenance_attaches_to_measured_rrs():
    prov = pw.ReidProvenance(
        target_n_pairs=385,
        observed_pairs=400,
        candidate_set_size=20,
        adversary_id="offline-deterministic-v1",
        reid_tier=pw.ReidTier.REID_LOW.value,
    )
    # a MeasuredRRS can be constructed carrying the ReidProvenance in its forward-seam field
    from pii_anon_datasets.scoring.reidentification import RRSResult

    measured = MeasuredRRS(
        rrs=RRSResult.from_attack(0.5, 0.5, 20, "offline-deterministic-v1", True),
        reid_recall_ci=wilson_interval(1, 2),
        reid_precision_ci=wilson_interval(1, 2),
        correct=1,
        n_targets=2,
        n_guesses=2,
        candidate_set_size=20,
        adversary_id="offline-deterministic-v1",
        deterministic=True,
        reid_provenance=prov,
    )
    assert measured.reid_provenance is prov
    out = measured.as_dict()
    assert "reid_provenance" in out
    assert out["reid_provenance"]["track"] == "reidentification"
    assert out["reid_provenance"]["target_n_pairs"] == 385
    assert out["reid_provenance"]["caveat"] == ANTI_ANONYMITY_CAVEAT
    # and it also rides through the score_reidentification entry point (provenance passthrough).
    # Empty (targets, candidates) → the n=0 sentinel CIs; provenance is threaded through verbatim.
    scored = score_reidentification(
        _NullAdversary(), [], [], 20, reid_provenance=prov,
    )
    assert scored.reid_provenance is prov
    assert scored.as_dict()["reid_provenance"]["track"] == "reidentification"


# ── 5. regression guard: the seam does NOT mutate the FROZEN detection lattice ────────────
def test_nfr_018_seam_does_not_mutate_frozen_lattice():
    data = json.loads(_EVAL_LATTICE.read_text(encoding="utf-8"))
    # the committed count is unchanged by this code-only seam (no cells added/removed)
    assert data["cell_count"] == _FROZEN_LATTICE_CELL_COUNT
    assert len(data["cells"]) == _FROZEN_LATTICE_CELL_COUNT
    assert data["cell_count"] == len(data["cells"])


# ── a trivial adversary that commits no guess (keeps test 4 self-contained, no I/O) ───────
class _NullAdversary:
    adversary_id = "offline-deterministic-v1"
    deterministic = True

    def attack(self, targets, candidates, candidate_set_size):  # noqa: ARG002
        return []
