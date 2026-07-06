# Story Gate Synthesis — S5-02 (Parquet export, gov-02 N regime columns + streaming)

**Gate:** story · **Scope:** S5-02 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-30

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 2 OBS |
| traceability | ✅ APPROVE | 2 OBS |
| requirements-coverage | ✅ APPROVE | 2 OBS (85.45% line; NFR-012 Croissant→S5-03) |
| security-sast | ✅ APPROVE | 1 OBS (unused huggingface_hub in extra) |
| axiom-compliance | ✅ APPROVE | 0 |

**Aggregate: APPROVE** (zero MAJOR+).

## Joint signals

- **gov-02 survives serialization** (axiom + traceability + requirements-coverage): `_row` drops `regulatory_domains` (the old `export_parquet.py:54` blob) and emits the 5 typed `reg_*` columns via S5-01's `as_columns`; `hipaa` fans out to both HIPAA columns; `sox` stays in `other_regimes` (no `reg_sox`). No flattened blob in the Parquet schema.
- **NFR-012 Parquet loadability VERIFIED** (genuinely ran, datasets 4.8.3): `datasets.load_dataset("parquet",...)` round-trips; `reg_*` columns survive.
- **Streams** (one-shot generator to exhaustion; no `list(records)`/`len`/indexing — AST-confirmed). **No egress** (security-sast grep+AST: no network/upload/`push_to_hub`; writes a local file only). **Lazy pyarrow** (package imports without it). **Determinism over contents** (`Table.equals`, not raw bytes — pyarrow footer false-determinism trap avoided).

## Findings forwarded (non-blocking)

- requirements-coverage (sprint-gate-critical): FR-024 is a MUST spanning JSONL+Parquet+Croissant+spaCy+CoNLL+card+CLI. **S5-02 closes the Parquet sub-clause + Parquet-loadability**; **NFR-012's literal threshold names the *Croissant* file → fully closed at S5-03.** Do NOT mark NFR-012 fully satisfied on S5-02 alone.
- security-sast OBS: `huggingface_hub` declared in `[distribution]` but unused — re-fire security-sast when a publish/upload path lands; keep any `push_to_hub` an explicit opt-in verb, never default in `export_parquet`.

## Outcome

S5-02 → **DONE**. The streaming Parquet exporter with gov-02 N regime columns ships (FR-024 Parquet; NFR-012 Parquet-loadability; gov-02 closed for the export surface). Evidence: RED `91e2266` → GREEN `e6176fa` → REFACTOR `4bf4ef8` → docs `b33de79`; 223 passed / 1 skipped (0 regressions); 85.45% line coverage; lazy pyarrow; no egress; frozen lattice/corpus/tags untouched.
