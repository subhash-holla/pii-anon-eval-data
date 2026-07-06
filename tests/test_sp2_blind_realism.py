import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import gold_spotcheck_aggregate as agg  # noqa: E402
import gold_spotcheck_sample as smp  # noqa: E402


def test_blind_realism_rate_over_blind_rows():
    # anchoring-resistant realism = realism rated on the BLIND rows (entity_type withheld)
    rows = [
        {"blind": "1", "realistic": "1", "p_incl": "0.5"},
        {"blind": "1", "realistic": "0", "p_incl": "0.5"},
        {"blind": "0", "realistic": "1", "p_incl": "0.5"},  # non-blind -> not the anchoring-resistant set
    ]
    res = agg.blind_realism_rate(rows)
    assert res["n"] == 2 and abs(res["rate"] - 0.5) < 1e-9


def test_sampler_has_no_misconceived_blind_realism_column():
    # the separate blind_realism subset was removed; blind rows carry the realism anchor
    assert "blind_realism" not in smp.FIELDS
    assert "blind" in smp.FIELDS and "realistic" in smp.FIELDS
