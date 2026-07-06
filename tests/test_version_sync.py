"""Smoke-test: the two-tier version-drift guard must exit 0 on the current working tree."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_version_sync_passes():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_version_sync.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
