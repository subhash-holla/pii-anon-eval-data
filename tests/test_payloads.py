"""Injection payload library tests (S7-02; FR-017, AX-001, NFR-004).

An ``InjectionPayload`` is the FR-017 tuple — ``(obfuscated_span, carrier_template,
intent_tag)`` — where ``obfuscated_span`` is a PII span rendered through one of the **3
committed faithful obfuscation transforms** (``base64`` / ``ocr`` homoglyph-confusable /
``zero_width`` insertion), ``carrier_template`` is a benign multilingual template with a
``{span}`` placeholder, and ``intent_tag`` names the technique. ``build_payloads(span)``
emits one payload per committed transform. The transforms are **faithful** (deterministic +
recoverable). The payloads are **INERT synthetic fixtures** (AX-001) — they test whether a
PII detector still catches obfuscated PII; they are **NOT weaponized prompt injections** and
carry a non-strippable inertness/scope disclaimer (NEVER agent-leakage scoring — FR-017).

Pure-stdlib + deterministic (NFR-004 / AX-002).
"""

from __future__ import annotations

import ast
import base64
import pathlib

import pytest
from pii_anon_datasets.scoring.adversary import (
    INERT_DISCLAIMER,
    INTENT_TAGS,
    InjectionPayload,
    build_payloads,
)
from pii_anon_datasets.scoring.adversary import payloads as payloads_mod

# A synthetic PII-shaped span (AX-001: fabricated, no real PII). Carries lowercase letters
# that the deterministic _OCR_MAP rewrites, so obfuscated != raw is observable.
_SPAN = "Robin Vale"


# 1. ::test_fr_017_payload_is_obfuscated_carrier_intent_tuple  [UNIT-TEST]
def test_fr_017_payload_is_obfuscated_carrier_intent_tuple() -> None:
    """``InjectionPayload`` exposes the FR-017 tuple — ``obfuscated_span`` +
    ``carrier_template`` (with a ``{span}`` placeholder) + ``intent_tag`` — and ``render()``
    substitutes the obfuscated span into the carrier (FR-017)."""
    payload = InjectionPayload(
        obfuscated_span="0BFU5C8TED",
        carrier_template="Please note: {span}",
        intent_tag="base64",
    )

    assert payload.obfuscated_span == "0BFU5C8TED"
    assert payload.intent_tag == "base64"
    assert "{span}" in payload.carrier_template

    rendered = payload.render()
    assert rendered == "Please note: 0BFU5C8TED"
    assert "0BFU5C8TED" in rendered


# 2. ::test_fr_017_three_committed_transforms  [UNIT-TEST]
def test_fr_017_three_committed_transforms() -> None:
    """``build_payloads(span)`` yields EXACTLY 3 payloads — one per committed transform
    ``("base64", "ocr", "zero_width")`` — and each ``obfuscated_span`` differs from the raw
    span (FR-017)."""
    payloads = build_payloads(_SPAN)

    assert len(payloads) == 3
    assert tuple(p.intent_tag for p in payloads) == ("base64", "ocr", "zero_width")
    assert tuple(p.intent_tag for p in payloads) == INTENT_TAGS

    for p in payloads:
        assert isinstance(p, InjectionPayload)
        assert p.obfuscated_span != _SPAN  # the span IS obfuscated


# 3. ::test_fr_017_transforms_are_faithful  [PROPERTY-TEST]
def test_fr_017_transforms_are_faithful() -> None:
    """The transforms are faithful — deterministic + recoverable: ``base64`` decodes back to
    the span; ``zero_width`` strips back (remove U+200B) to the span; ``ocr`` is a fixed
    deterministic homoglyph map (same input -> same output) (FR-017)."""
    by_tag = {p.intent_tag: p.obfuscated_span for p in build_payloads(_SPAN)}

    # base64 is faithful: decodes back to the original UTF-8 span
    decoded = base64.b64decode(by_tag["base64"].encode("ascii")).decode("utf-8")
    assert decoded == _SPAN

    # zero_width is faithful: stripping U+200B recovers the original span
    stripped = by_tag["zero_width"].replace("​", "")
    assert stripped == _SPAN
    assert "​" in by_tag["zero_width"]  # the zero-width char was actually inserted

    # ocr is faithful in the deterministic sense: same input -> same output, every run
    again = {p.intent_tag: p.obfuscated_span for p in build_payloads(_SPAN)}
    assert again["ocr"] == by_tag["ocr"]
    # and the fixed map is applied (Robin Vale -> homoglyphs of o/i/a/e ...)
    assert by_tag["ocr"] == payloads_mod.ocr_transform(_SPAN)


# 4. ::test_fr_017_payloads_are_inert  [AUDIT]
def test_fr_017_payloads_are_inert() -> None:
    """AX-001 inertness: ``render()`` returns a plain string; no payload/carrier contains
    active/executable markers (no ``<script``, no weaponized "ignore previous instructions"
    directive); ``INERT_DISCLAIMER`` is present + non-strippable (empty disclaimer ->
    ``ValueError``) and states "inert" + "never" + "agent-leakage" (FR-017 / AX-001)."""
    weaponized_markers = ("<script", "ignore previous instructions", "ignore all previous")

    for p in build_payloads(_SPAN):
        rendered = p.render()
        assert isinstance(rendered, str)  # a plain string, not a callable / code object
        haystack = (rendered + " " + p.carrier_template + " " + p.obfuscated_span).lower()
        for marker in weaponized_markers:
            assert marker not in haystack

    # the inertness disclaimer is non-strippable: an empty disclaimer is rejected
    with pytest.raises(ValueError):
        InjectionPayload(obfuscated_span="x", carrier_template="{span}", intent_tag="base64", disclaimer="")

    lowered = INERT_DISCLAIMER.lower()
    assert "inert" in lowered
    assert "never" in lowered
    assert ("agent-leakage" in lowered) or ("agent leakage" in lowered)


# 5. ::test_fr_017_invalid_payload_rejected  [UNIT-TEST]
def test_fr_017_invalid_payload_rejected() -> None:
    """An unknown ``intent_tag`` raises ``ValueError``; a ``carrier_template`` missing the
    ``{span}`` placeholder raises ``ValueError`` (FR-017 negative path)."""
    with pytest.raises(ValueError):
        InjectionPayload(obfuscated_span="x", carrier_template="Please note: {span}", intent_tag="bogus")

    with pytest.raises(ValueError):
        InjectionPayload(obfuscated_span="x", carrier_template="no placeholder here", intent_tag="base64")


# 6. ::test_nfr004_payloads_pure_stdlib  [PROPERTY-TEST]
def test_nfr004_payloads_pure_stdlib() -> None:
    """NFR-004 / AX-002: statically prove ``payloads.py`` imports none of
    {random, time, uuid, datetime, secrets} — the payload library has no clock/RNG
    (only ``base64`` + ``unicodedata`` + stdlib)."""
    src = pathlib.Path(payloads_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned = {"random", "time", "uuid", "datetime", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert banned.isdisjoint(imported), f"payloads.py imports nondeterministic modules: {sorted(banned & imported)}"
