"""Positive-control detector: returns the record's gold spans (upper bound; expect F2 = 1.0).

Reads the record via the orchestrator's ``wants_record`` seam — the only adapter that needs the record.
"""
from pii_anon_datasets import taxonomy
from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

LABEL_MAP: dict[str, str | None] = {t: t for t in taxonomy.CANONICAL_ENTITY_TYPES}


class _OraclePerfectAdapter:
    name = "oracle"
    model_id = "gold"
    label_map = LABEL_MAP
    deterministic = True
    wants_record = True

    def available(self) -> bool:
        return True

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get(native)

    def build(self) -> object:
        return None

    def detect(self, text: str, model: object, record: dict | None = None) -> list[AdapterSpan]:
        anns = (record or {}).get("annotations", []) or []
        t = text or ""
        return [
            AdapterSpan(int(a["start"]), int(a["end"]), str(a["entity_type"]), t[int(a["start"]):int(a["end"])])
            for a in anns
        ]

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _OraclePerfectAdapter()
