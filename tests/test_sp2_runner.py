"""SP-II: the local lane is restart-safe at per-(detector,language) granularity."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SH = (ROOT / "scripts" / "run_full_leaderboard.sh").read_text()

def test_local_lane_iterates_languages_and_skips_per_lang():
    assert 'for lang in' in SH, "run_one_local must iterate languages"
    assert '$det_dir/$lang' in SH or '$det/$lang' in SH, "must nest output per language"
    assert re.search(r'\$lang_dir/baseline_results\.json.*done', SH), "must skip completed (det,lang) shards"
    assert '*/*/baseline_results.json' in SH, "final merge must glob two levels deep"
    # regression guard: `local det="$1" det_dir="$OUT_LOCAL/$det"` on ONE line expands $det from the
    # OUTER (empty) scope (bash gotcha) -> every detector collides into $OUT_LOCAL/<lang>. Must be split.
    assert not re.search(r'local det="\$1"\s+det_dir=', SH), \
        "det/det_dir must be separate `local` lines (single-line local a=$1 b=$a expands $a empty)"
