"""Injection payload library (FR-017; DC-10, bounded).

An :class:`InjectionPayload` is the FR-017 tuple — ``(obfuscated_span, carrier_template,
intent_tag)`` — where ``obfuscated_span`` is a PII span rendered through one of the **3
committed faithful obfuscation transforms** (``base64`` / ``ocr`` homoglyph-confusable /
``zero_width`` insertion), ``carrier_template`` is a benign multilingual template with a
``{span}`` placeholder, and ``intent_tag`` names the obfuscation technique. :func:`build_payloads`
emits one payload per committed transform. The transforms are **faithful** (deterministic +
recoverable): ``base64`` decodes back to the span, ``zero_width`` strips (remove U+200B) back to
the span, and ``ocr`` is a fixed deterministic homoglyph map.

**INERT synthetic fixtures (AX-001).** These payloads exist to test whether a PII detector still
catches *obfuscated* PII; they are **NOT weaponized prompt injections** — the carriers carry no
active/executable content. Each payload carries a non-strippable :data:`INERT_DISCLAIMER` (a module
constant + a validated dataclass field whose ``__post_init__`` rejects an empty value): the payloads
are **NEVER marketed as agent-leakage scoring** (FR-017 / AX-001).

Pure-stdlib (NFR-004): ``base64`` + ``dataclasses`` (the OCR-confusable map is a fixed literal — no
``unicodedata`` lookup needed); deterministic — no clock / RNG (AX-002).
"""

from __future__ import annotations

import base64
from dataclasses import dataclass

INTENT_TAGS: tuple[str, ...] = ("base64", "ocr", "zero_width")  # the 3 committed faithful transforms
_ZERO_WIDTH: str = "​"
# A fixed, deterministic homoglyph/OCR-confusable map (faithful: reversible via the inverse).
_OCR_MAP: dict[str, str] = {
    "o": "0",
    "O": "0",
    "l": "1",
    "I": "1",
    "i": "1",
    "s": "5",
    "S": "5",
    "e": "3",
    "a": "@",
    "B": "8",
    "g": "9",
    "t": "7",
    "z": "2",
}

# Benign multilingual carriers (each has a {span} placeholder). INERT — no weaponized directive.
CARRIER_TEMPLATES: tuple[str, ...] = (
    "Please note: {span}",
    "Nota: {span}",
    "Remarque : {span}",
    "Hinweis: {span}",
    "注意: {span}",
    "ملاحظة: {span}",
)

# Non-strippable (FR-017 / AX-001): these are inert synthetic fixtures, not weaponized injections.
INERT_DISCLAIMER: str = (
    "Inert synthetic obfuscated-PII fixture for detector-robustness testing. NOT a weaponized prompt "
    "injection (no active/executable content); NEVER marketed as agent-leakage scoring (FR-017 / AX-001)."
)


def base64_transform(span: str) -> str:
    """Faithful: base64 of the UTF-8 bytes (decodes back to the span)."""
    return base64.b64encode(span.encode("utf-8")).decode("ascii")


def ocr_transform(span: str) -> str:
    """Faithful: deterministic homoglyph/OCR-confusable substitution per the fixed _OCR_MAP."""
    return "".join(_OCR_MAP.get(ch, ch) for ch in span)


def zero_width_transform(span: str) -> str:
    """Faithful: insert a zero-width space between characters (strip U+200B to recover)."""
    return _ZERO_WIDTH.join(span)


_TRANSFORMS = {"base64": base64_transform, "ocr": ocr_transform, "zero_width": zero_width_transform}


@dataclass(frozen=True)
class InjectionPayload:
    """The FR-017 tuple: (obfuscated_span, carrier_template, intent_tag) + non-strippable inertness note."""

    obfuscated_span: str
    carrier_template: str
    intent_tag: str
    disclaimer: str = INERT_DISCLAIMER

    def __post_init__(self) -> None:
        if self.intent_tag not in INTENT_TAGS:
            raise ValueError(f"intent_tag must be one of {INTENT_TAGS}, got {self.intent_tag!r}")
        if "{span}" not in self.carrier_template:
            raise ValueError("carrier_template must contain a {span} placeholder")
        if not self.disclaimer.strip():
            raise ValueError("payload inertness disclaimer required (FR-017 / AX-001 non-strippable)")

    def render(self) -> str:
        """The inert carrier with the obfuscated span substituted (a plain string)."""
        return self.carrier_template.format(span=self.obfuscated_span)

    def as_dict(self) -> dict[str, object]:
        return {
            "obfuscated_span": self.obfuscated_span,
            "carrier_template": self.carrier_template,
            "intent_tag": self.intent_tag,
            "disclaimer": self.disclaimer,
        }


def build_payloads(span: str, *, carrier: str = CARRIER_TEMPLATES[0]) -> list[InjectionPayload]:
    """One InjectionPayload per committed transform (base64/ocr/zero_width) for `span`."""
    return [InjectionPayload(_TRANSFORMS[tag](span), carrier, tag) for tag in INTENT_TAGS]
