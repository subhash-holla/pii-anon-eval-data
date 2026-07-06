"""Negative-control detector: labels every whitespace token PERSON_NAME (precision floor)."""
import re

from pii_anon_datasets.baselines.contract import AdapterSpan, coverage_of

LABEL_MAP: dict[str, str | None] = {"PERSON_NAME": "PERSON_NAME"}
_TOKEN = re.compile(r"\S+")


class _AlwaysPersonNameAdapter:
    name = "always_person_name"
    model_id = ""
    label_map = LABEL_MAP
    deterministic = True

    def available(self) -> bool:
        return True

    def map_label(self, native: str) -> str | None:
        return LABEL_MAP.get(native)

    def build(self) -> object:
        return None

    def detect(self, text: str, model: object) -> list[AdapterSpan]:
        return [AdapterSpan(m.start(), m.end(), "PERSON_NAME", m.group()) for m in _TOKEN.finditer(text or "")]

    def coverage(self) -> int:
        return coverage_of(LABEL_MAP)


ADAPTER = _AlwaysPersonNameAdapter()
