# Accessibility Audit — N/A (no UI surface)

**Wave:** T4 (Accessibility) · **Verdict: NOT APPLICABLE** · **Date:** 2026-05-31

## Determination

PII-Anon is a **CC0 synthetic-PII benchmark dataset + a pure-stdlib Python evaluation library + a thin
console CLI** (`pii-anon`). It has **no interactive web/GUI surface** — no rendered pages, forms, widgets,
focus order, color contrast, ARIA, or assistive-technology surface to audit. WCAG 2.2 AA conformance
testing (axe-core / Pa11y / Lighthouse / NVDA / VoiceOver) is therefore **not applicable**.

This was anticipated throughout the PDLC: the Requirements/Design vocabulary remap (MANIFEST §"Benchmark-
dataset adaptation") explicitly **de-scoped accessibility/WCAG** ("no interactive web UI; documentation
clarity only"), and the MANIFEST Testing-phase roster carries "Accessibility test plan — n/a, no UI
surface".

## The consumer surfaces (and how they stay usable)

The project's "UI" is its **documentation + machine-readable metadata + CLI**, addressed by other waves:

| Surface | How usability/clarity is verified |
|---|---|
| README / DATASHEET / TAXONOMY / COMPARISON / MIGRATION / CHANGELOG / GOVERNANCE / CONTRIBUTING / ROADMAP | NFR-013 doc-drift gate (`tests/test_doc_drift.py`) keeps counts canonical; the governance/contribution docs are pinned by `test_governance.py` / `test_contributing.py` / `test_roadmap.py`. |
| HF dataset card + Croissant 1.0 JSON-LD | NFR-012 (validates + loads via HF `datasets`); counts derive from `metadata.json` (cannot drift). |
| `pii-anon` CLI | 5 thin verbs with `--help`; DX-03 one copy-paste CI invocation (`pii-anon validate`). |

## Outcome

**Accessibility audit: N/A.** Recorded as an explicit "not applicable — no UI surface" finding (not a
skipped obligation). If a future release adds an interactive web leaderboard or viewer, a WCAG 2.2 AA
audit re-enters scope at that point.
