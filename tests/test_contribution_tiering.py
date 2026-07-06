from scripts.contribution_tiering import render_markdown


def test_render_markdown_has_three_tiers():
    md = render_markdown()
    assert "C1" in md and "C2" in md and "C3" in md
    assert "delivered" in md.lower()
    assert "AX-001" in md  # synthetic-only honesty rides along
