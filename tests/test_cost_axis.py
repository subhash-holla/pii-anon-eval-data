from pii_anon_datasets.reporting.baselines import render_cost_table


def _data():
    return {
        "ranking": [{"rank": 1, "detector": "aws"}, {"rank": 2, "detector": "gliner"}],
        "detectors": {
            "aws": {"micro": {"f2": 0.7367}},
            "gliner": {"micro": {"f2": 0.7354}},
        },
    }


def test_render_cost_table_free_and_priced():
    cost = {"aws": {"usd_per_1k": 1.7032}, "gliner": {"usd_per_1k": 0.0}}
    md = render_cost_table(_data(), cost)
    assert "$/1k records" in md
    assert "free" in md  # gliner local
    assert "$1.7032" in md  # aws priced
