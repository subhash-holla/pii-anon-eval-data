"""NFR-050 regression guard: importing the pure-stdlib baselines CORE must NOT import any detector
library (presidio / spacy / gliner / torch / transformers / stanza / flair / scrubadub). Heavy libs
load only inside an adapter's ``build()``. Mirrors tests/test_cli.py's thin-import guard.

Run in a CLEAN subprocess so a detector lib already imported by the parent pytest session (the eval venv
now has them all installed) cannot mask an accidental eager import in the baselines package.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

import pii_anon_datasets

_HEAVY = ("torch", "presidio_analyzer", "spacy", "transformers", "gliner", "stanza", "flair", "scrubadub")


def test_nfr050_baselines_core_imports_no_detector_lib() -> None:
    src_dir = str(pathlib.Path(pii_anon_datasets.__file__).resolve().parents[1])
    code = (
        "import sys\n"
        "import pii_anon_datasets.baselines.orchestrator\n"
        "import pii_anon_datasets.baselines.provenance\n"
        "import pii_anon_datasets.baselines.contract\n"
        "import pii_anon_datasets.baselines.results\n"
        f"heavy=[m for m in {_HEAVY!r} if m in sys.modules]\n"
        "assert not heavy, 'NFR-050 violation: baselines core eagerly imported '+repr(heavy)\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": src_dir},
    )
    assert proc.returncode == 0, proc.stderr
