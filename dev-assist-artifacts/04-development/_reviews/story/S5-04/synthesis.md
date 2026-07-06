# Story Gate Synthesis — S5-04 (spaCy + CoNLL exporters; FR-024)

**Gate:** story · **Scope:** S5-04 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-30

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 1 OBS (2 necessary `type: ignore[call-overload]` on the `Mapping[str,object]` brownfield port) |
| security-sast | ✅ APPROVE | 0 (local file writes only; no egress; no new dep; synthetic data) |
| requirements-coverage | ✅ APPROVE | 1 OBS (FR-024 CLI sub-clause → successor S5-05; confirm authored before FR-024 rolled up) |
| traceability | ✅ APPROVE | 0 (all IDs resolve; `-k fr_024`→7, `-k nfr004`→2; no double-claim) |
| axiom-compliance | ✅ APPROVE | 1 OBS (stale "double blank line" comment; no axiom impact) |

**Aggregate: APPROVE** (zero SHOWSTOPPER / CATASTROPHIC / MAJOR; OBSERVATIONs only).

## Joint signals

- **spaCy DocBin round-trip VERIFIED** (code-quality + requirements-coverage + traceability): spaCy 3.8.3
  is present, so `test_fr_024_spacy_docbin_roundtrip` genuinely RAN (0 skipped) — `export_spacy_docbin`
  writes a DocBin that `DocBin().from_disk` reloads with `ents` (labels + char offsets) preserved;
  misaligned `char_span` (None) skipped and overlaps dropped via `spacy.util.filter_spans`.
- **CoNLL thin-wrap + streaming** (code-quality + axiom): `conll_export.export_conll` carries no
  tokenization/tagging logic (AST-confirmed) — it streams a one-pass iterator through the packaged
  `integrations.conll_format.record_to_conll` (pure functions ported verbatim from the brownfield CLI,
  which stays untouched). BIO + BILOU tags align to char offsets.
- **NFR-004 / lazy + pure-stdlib** (axiom + code-quality + security): CoNLL is pure-stdlib (AST guards);
  `import spacy` only inside `_require_spacy`; `spacy_export` imports with spaCy blocked; export without
  the `[baselines]` extra raises a clear `RuntimeError` naming the install command. No network egress.
- **AX-002 determinism** (axiom): both exporters byte-identical across a live double-export (stable
  whitespace tokenizer + offsets sorted by `(start, end)`; no clock/RNG).

## Findings forwarded (non-blocking)

- **requirements-coverage (sprint-gate-critical)**: FR-024 is a MUST spanning JSONL + Parquet + Croissant
  + spaCy + CoNLL + dataset-card + CLI. S5-04 closes the **spaCy + CoNLL** sub-clauses. The **CLI
  `export`-verb sub-clause is the named successor S5-05** — the sprint/epic gate must confirm S5-05 is
  authored + DONE before FR-024 is rolled up as fully closed (no silent orphan). *(Resolved by authoring
  S5-05 next.)*
- **code-quality (OBS)**: two `# type: ignore[call-overload]` at `integrations/conll_format.py:64-65` are
  genuinely required under `--strict` for the `Mapping[str, object]` brownfield port (verified by live
  mypy probe); narrowing to a TypedDict would remove them — defer, not blocking.
- **axiom-compliance (OBS)**: a stale "double blank line" comment in `conll_export.py` — cosmetic;
  the emitted separator is one blank line (matching the verbatim port), as documented in §12 deviation #1.

## Outcome

S5-04 → **DONE**. The spaCy + CoNLL exporters ship: CoNLL BIO/BILOU (thin-wrap over the packaged
`integrations.conll_format`, streaming, deterministic, pure-stdlib) + spaCy char-offset tuples
(`to_spacy_offsets`, pure) + a serialized `DocBin` (lazy spaCy behind `[baselines]`, round-trips
preserving `ents`, filters misaligned/overlapping spans). FR-024's spaCy + CoNLL sub-clauses closed.
Evidence: RED `589567f` → GREEN `dd71da6` → REFACTOR `99f58f1` → docs `574a30f`; **242 passed / 1
skipped** (233 prior + 9 new, 0 regressions); ruff + mypy --strict clean; brownfield CLI / scoring / stats
/ corpus / `v1.3.0` + `pre-lattice-enrichment` tags untouched; no pyproject change (spaCy already in
`[baselines]`).
