"""Read dataset version from pyproject.toml (single source of truth)."""

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent


def get_version() -> str:
    """Return the version string from pyproject.toml."""
    pyproject = _REPO_ROOT / "pyproject.toml"
    for line in pyproject.read_text().splitlines():
        if line.startswith("version"):
            return line.split("=", 1)[1].strip().strip('"')
    raise RuntimeError("Could not find version in pyproject.toml")


DATASET_VERSION = get_version()
