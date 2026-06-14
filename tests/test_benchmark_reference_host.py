"""NFR-010 — the canonical-verdict gate for the throughput benchmark (Pass-2 reference-host seam).

The agent sandbox (and any unverified host) is NEVER the declared 8-core reference host, so the canonical
NFR-010b verdict stays INSUFFICIENT_EVIDENCE — never a pass — regardless of the measured rec/sec. Only an
OPERATOR explicitly declaring the reference host (via --reference-host on the real machine) lets the floor
verdict (PASS/FAIL vs >=5000 rec/sec) stand. This pins that gate so an agent-env number can never be published
as a pass.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "benchmark_throughput",
    Path(__file__).resolve().parents[1] / "scripts" / "benchmark_throughput.py",
)
BT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(BT)  # type: ignore[union-attr]


def test_no_reference_host_is_insufficient_evidence_even_above_floor() -> None:
    v = BT._canonical_verdict(None, 99999.0)
    assert v["canonical_verdict"] == "INSUFFICIENT_EVIDENCE"
    assert v["is_reference_host"] is False


def test_empty_reference_host_treated_as_absent() -> None:
    v = BT._canonical_verdict("   ", 99999.0)
    assert v["canonical_verdict"] == "INSUFFICIENT_EVIDENCE"
    assert v["is_reference_host"] is False


def test_declared_reference_host_above_floor_passes() -> None:
    v = BT._canonical_verdict("8-core x86_64 reference host, 32GB, isolated", 9000.0)
    assert v["canonical_verdict"] == "PASS"
    assert v["is_reference_host"] is True
    assert "8-core" in v["environment"]


def test_declared_reference_host_below_floor_fails() -> None:
    v = BT._canonical_verdict("8-core reference host", 3000.0)
    assert v["canonical_verdict"] == "FAIL"
    assert v["is_reference_host"] is True


def test_floor_is_nfr_010b_5000() -> None:
    assert BT.NFR_010B_FLOOR == 5000
    assert BT._canonical_verdict("ref", 5000.0)["canonical_verdict"] == "PASS"   # >= floor
    assert BT._canonical_verdict("ref", 4999.0)["canonical_verdict"] == "FAIL"


def test_cli_exposes_reference_host_flag() -> None:
    import argparse
    # the flag must exist so an operator can declare the host; agent runs omit it (stays INSUFFICIENT_EVIDENCE)
    src = (Path(__file__).resolve().parents[1] / "scripts" / "benchmark_throughput.py").read_text()
    assert "--reference-host" in src
    assert isinstance(argparse.ArgumentParser(), argparse.ArgumentParser)
