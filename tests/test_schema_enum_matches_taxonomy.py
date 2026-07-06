"""The shipped JSON-schema entity_type enum must equal the canonical taxonomy (no drift)."""
import json
from pathlib import Path

from pii_anon_datasets import taxonomy

SCHEMA = Path(__file__).resolve().parent.parent / "src" / "pii_anon_datasets" / "data" / "pii_anon.schema.json"


def _entity_enum(obj):
    if isinstance(obj, dict):
        if obj.get("enum") and "PERSON_NAME" in obj["enum"] and "EMAIL_ADDRESS" in obj["enum"]:
            return obj["enum"]
        for v in obj.values():
            r = _entity_enum(v)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _entity_enum(v)
            if r is not None:
                return r
    return None


def test_schema_entity_enum_equals_canonical():
    enum = _entity_enum(json.loads(SCHEMA.read_text()))
    assert enum is not None, "entity_type enum not found in schema"
    assert set(enum) == set(taxonomy.CANONICAL_ENTITY_TYPES), (
        f"schema-only={sorted(set(enum)-set(taxonomy.CANONICAL_ENTITY_TYPES))} "
        f"taxonomy-only={sorted(set(taxonomy.CANONICAL_ENTITY_TYPES)-set(enum))}"
    )
