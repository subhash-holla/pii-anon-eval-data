"""The partial-overlap counter must stay byte-identical to its greedy definition AND scale to the pooled,
record-namespaced span sets the baselines orchestrator builds for a full multilingual run (115k records →
~1M+ pooled spans). The original O(FP×FN) scan is correct but quadratic; this pins the EXACT semantics with
an independent brute-force reference (so any optimization cannot change a single count — the matching policy
stays ``strict-v1``) and exercises a large disjoint-band pool so a quadratic regression would time out.
"""

from __future__ import annotations

import random
import time

from pii_anon_datasets.scoring.core import Span, _count_partial, match_strict


def _ref_count_partial(gold_left, pred_left) -> int:
    """Independent brute-force reference: the greedy definition, scanning all gold for every pred."""
    gold_sorted = sorted(gold_left, key=lambda s: (s.start, s.end, s.entity_type))
    used = [False] * len(gold_sorted)
    partial = 0
    for ps in sorted(pred_left, key=lambda s: (s.start, s.end, s.entity_type)):
        for i, gs in enumerate(gold_sorted):
            if not used[i] and gs.entity_type == ps.entity_type and gs.overlaps(ps):
                used[i] = True
                partial += 1
                break
    return partial


def _rand_spans(rng: random.Random, n: int, span_max: int, types: list[str]) -> list[Span]:
    out = []
    for _ in range(n):
        start = rng.randint(0, span_max)
        end = start + rng.randint(1, 6)  # non-empty
        out.append(Span(start, end, rng.choice(types)))
    return out


def test_count_partial_is_identical_to_the_bruteforce_reference_over_random_cases() -> None:
    rng = random.Random(20260614)
    types = ["A", "B", "C"]
    for _ in range(300):
        gold = _rand_spans(rng, rng.randint(0, 25), 40, types)
        pred = _rand_spans(rng, rng.randint(0, 25), 40, types)
        assert _count_partial(gold, pred) == _ref_count_partial(gold, pred)


def test_match_strict_partial_matches_reference_after_strict_removal() -> None:
    # match_strict feeds _count_partial the multiset leftovers (g - inter, p - inter); confirm the whole
    # pipeline still equals the reference applied to those same leftovers.
    rng = random.Random(99)
    types = ["X", "Y"]
    for _ in range(200):
        gold = _rand_spans(rng, rng.randint(0, 30), 25, types)
        pred = _rand_spans(rng, rng.randint(0, 30), 25, types)
        from collections import Counter

        g, p = Counter(gold), Counter(pred)
        inter = g & p
        expected = _ref_count_partial(list((g - inter).elements()), list((p - inter).elements()))
        assert match_strict(gold, pred).partial == expected


def test_partial_count_scales_on_a_record_namespaced_pool() -> None:
    # The real worst case from the orchestrator: many same-type FP predictions that match NO gold (e.g. a
    # high-FP detector on the multilingual split). Each such pred scans the WHOLE gold pool — O(FP×FN) — so
    # at 115k records this is the multi-minute step the smoke surfaced. Here N same-type FP preds sit in the
    # GAP after their band's gold (overlap nothing). The pointer-optimized scan skips the permanently-dead
    # gold (end ≤ pred.start) and stops at the band boundary, making it ~O(N).
    n = 15_000
    gold, pred = [], []
    base = 0
    for _ in range(n):
        gold.append(Span(base, base + 5, "T"))         # gold occupies [base, base+5)
        pred.append(Span(base + 10, base + 15, "T"))   # same-type FP in the gap — overlaps no gold anywhere
        base += 100
    t0 = time.perf_counter()
    counts = match_strict(gold, pred)
    elapsed = time.perf_counter() - t0
    assert counts.tp == 0 and counts.fp == n and counts.fn == n
    assert counts.partial == 0  # nothing overlaps — every pred is a clean FP
    assert elapsed < 5.0, f"partial counting took {elapsed:.1f}s on {n} bands — quadratic regression"
