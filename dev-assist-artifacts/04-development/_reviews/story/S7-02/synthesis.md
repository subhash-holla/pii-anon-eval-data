# Story Gate Synthesis — S7-02 (Injection payload library; FR-017 / DC-10 bounded)

**Gate:** story · **Scope:** S7-02 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-31

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 2 MINOR (`__post_init__`/`as_dict` lack docstrings — internal helpers) |
| security-sast | ✅ APPROVE | 0 (load-bearing — INERT confirmed: zero weaponized markers; base64 encode-only) |
| axiom-compliance | ✅ APPROVE | 1 OBS (test #6 docstring names `unicodedata`, not imported — cosmetic) |
| requirements-coverage | ✅ APPROVE | 1 OBS (6 multilingual carriers shipped but `build_payloads` defaults to English — untested) |
| traceability | ✅ APPROVE | 1 MINOR + 1 OBS (matrix row pending; partition watch) |

**Aggregate: APPROVE** (zero SHOWSTOPPER / CATASTROPHIC / MAJOR; MINOR/OBSERVATIONs only).

## Joint signals

- **AX-001 INERT (the crux)** — security-sast + axiom-compliance verified the payloads are benign: a broad
  weaponization / dynamic-execution / network / unsafe-deserialization scan returned ZERO matches (the only
  hits are the inert-marker literals inside the AX-001 audit test that asserts their absence). `render()`
  is a plain `str.format`; base64 is encode-only (no decode-then-run); the non-strippable
  `INERT_DISCLAIMER` (empty AND whitespace -> ValueError) states inert / never / agent-leakage. No real
  PII, no bidi/trojan-source codepoints (only the declared U+200B + benign CJK/Arabic carrier prefixes).
- **FR-017 tuple + 3 committed faithful transforms** — `build_payloads(span)` yields exactly 3 payloads
  (base64/ocr/zero_width); transforms are deterministic + recoverable (base64 round-trips; zero_width
  strips U+200B back; ocr is a genuine fixed homoglyph map — `Robin Vale -> R0b1n V@13`, not identity).
- **Pure-stdlib + deterministic** — imports `{__future__, base64, dataclasses}`; AST guard green; no
  clock/RNG; 6/6 tests pass.

## Findings forwarded (non-blocking)

- **requirements-coverage (OBS)**: the 6 multilingual `CARRIER_TEMPLATES` are shipped but `build_payloads`
  defaults to the English carrier — a multilingual-carrier test is a cheap v1.1 nicety (the "multilingual"
  FR-017 qualifier is implemented, just not exercised in tests).
- **code-quality (MINOR)**: add docstrings to `__post_init__`/`as_dict` (internal helpers).
- **traceability (MINOR)**: FR-017 matrix Status Change Log row at the S7 sprint close.

## Outcome

S7-02 -> **DONE**. The injection payload library ships: `InjectionPayload = (obfuscated_span,
carrier_template, intent_tag)` with the 3 committed faithful transforms (base64 / ocr-homoglyph /
zero-width); INERT synthetic fixtures (benign carriers, non-strippable inertness disclaimer, no weaponized
content); validated; pure-stdlib; deterministic. **FR-017 now FULLY covered** (S7-01 oracle + S7-02
payloads) — markable verified at the S7 sprint gate. Evidence: RED `fe9630b` -> GREEN `fb83f6b` ->
REFACTOR `b8ad21f` -> docs `861e719`; **335 passed / 1 skipped** (329 prior + 6 new, 0 regressions); ruff
+ mypy --strict clean; oracle/base/offline/llm + corpus / lattice / tags untouched.
