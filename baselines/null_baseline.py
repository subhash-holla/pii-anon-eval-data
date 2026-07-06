"""Negative-control detector: predicts nothing (recall lower bound; expect F2 ~ 0)."""
from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

LABEL_MAP: dict[str, str | None] = {}


class _NullAdapter:
    name = "null"
    model_id = ""
    label_map = LABEL_MAP
    deterministic = True

    def available(self) -> bool:
        return True

    def map_label(self, native: str) -> str | None:
        return None

    def build(self) -> object:
        return None

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        return []

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _NullAdapter()
