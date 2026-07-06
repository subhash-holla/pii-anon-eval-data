from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SH = (ROOT / "scripts" / "provision_azure_gpu.sh").read_text()

def test_teardown_assertion_present():
    assert "az group exists" in SH, "must verify the resource group is deleted post-run"
    assert "MANUAL ACTION REQUIRED" in SH, "must print a manual-delete hint"
