"""PII-Anon Evaluation Dataset

Comprehensive multilingual benchmark for PII detection and de-identification
evaluation. 150K+ records across 60 languages, 65 entity types, 20+ document
formats, and 7 evaluation dimensions.

Usage:
    from pii_anon_datasets import load_dataset, get_data_path

    # Load the full canonical dataset
    records = load_dataset()

    # Load a specific dimension subset
    records = load_dataset(subset="entity_tracking")

    # Load a domain subset
    records = load_dataset(domain="clinical")

    # Load train/dev/test splits
    train = load_dataset(split="train")
    dev = load_dataset(split="dev")
    test = load_dataset(split="test")

    # Load adversarial test set
    adv = load_dataset(split="test_adversarial")
"""

import gzip
import json
from pathlib import Path

def _get_version() -> str:
    """Read version from pyproject.toml (single source of truth)."""
    pyproject = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    if pyproject.exists():
        for line in pyproject.read_text().splitlines():
            if line.startswith("version"):
                return line.split("=")[1].strip().strip('"')
    # Fallback for installed packages where pyproject.toml isn't alongside source
    from importlib.metadata import version
    return version(__name__)

__version__ = _get_version()
__all__ = ["load_dataset", "get_data_path"]

_PACKAGE_DIR = Path(__file__).parent


def get_data_path() -> Path:
    """Return the path to the data directory."""
    return _PACKAGE_DIR / "data"


def load_dataset(
    *,
    subset: str | None = None,
    domain: str | None = None,
    split: str | None = None,
    language: str | None = None,
    dimension: str | None = None,
) -> list[dict]:
    """Load records from the PII-Anon dataset.

    Args:
        subset: Load a dimension subset (e.g., "entity_tracking", "multilingual").
        domain: Load a domain subset (e.g., "clinical", "financial").
        split: Load a split ("train", "dev", "test", "test_adversarial", or cross-domain like "test_clinical").
        language: Filter to a specific BCP 47 language code.
        dimension: Filter by primary_dimension value.

    Returns:
        List of record dictionaries.
    """
    if split:
        path = _PACKAGE_DIR / "splits" / f"{split}.jsonl.gz"
    elif domain:
        path = _PACKAGE_DIR / "subsets" / "by_domain" / f"{domain}.jsonl.gz"
    elif subset:
        path = _PACKAGE_DIR / "subsets" / "by_dimension" / f"{subset}.jsonl.gz"
    else:
        path = _PACKAGE_DIR / "data" / "pii_anon.jsonl.gz"

    if not path.exists():
        # Try uncompressed
        uncompressed = path.with_suffix("").with_suffix(".jsonl")
        if uncompressed.exists():
            path = uncompressed
        else:
            raise FileNotFoundError(f"Dataset file not found: {path}")

    records = []
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if language and rec.get("language") != language:
                continue
            if dimension and rec.get("primary_dimension") != dimension:
                continue
            records.append(rec)

    return records
