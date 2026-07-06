# Story Gate Synthesis — S5-03 (Croissant 1.0 JSON-LD + HF dataset card; NFR-012 loadability)

**Gate:** story · **Scope:** S5-03 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-30

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 1 OBS (`validate_with_mlcroissant` not re-exported — by design per §8 export list) |
| security-sast | ✅ APPROVE | 1 OBS (mlcroissant CVE scan deferred — opt-in, uninstalled `[croissant]` extra) |
| requirements-coverage | ✅ APPROVE | 2 OBS (full mlcroissant validate → Pass-2 CI; NFR-013 cross-doc sweep → S5-07) |
| traceability | ✅ APPROVE | 0 (all 6 declared IDs resolve; 4 tokens `-k`-selectable above threshold) |
| axiom-compliance | ✅ APPROVE | 0 (1 prose-shorthand note on regime enumeration) |

**Aggregate: APPROVE** (zero SHOWSTOPPER / CATASTROPHIC / MAJOR; OBSERVATIONs only).

## Joint signals

- **NFR-012 validate-AND-load VERIFIED** (requirements-coverage + traceability + axiom): the binding
  `test_nfr_012_croissant_describes_loadable_parquet` genuinely RAN (pyarrow + datasets 4.8.3 present) —
  it exports a real Parquet via S5-02's `export_parquet`, `validate_croissant()` passes the always-on
  schema-shape check, AND `datasets.load_dataset("parquet", …)` round-trips with the five `reg_*` columns
  intact (`load_dataset` not monkeypatched). The literal Croissant validate-AND-load threshold is met.
- **gov-02 survives into the Croissant description** (traceability + axiom): the `recordSet` declares one
  `reg_<regime>` Field per the `crosswalk.REGIMES` SSOT; no flattened `regulatory_domains` field, no
  merged/equivalence field; `validate_croissant` raises naming `reg_gdpr` if a `reg_*` field is dropped.
- **Counts cannot drift** (axiom + requirements-coverage): every count read from `metadata.json`;
  `entity_types`(63) `== taxonomy.ENTITY_TYPE_COUNT`(63) asserted at runtime; the perturbation test proves
  counts are derived not hardcoded; the card test forbids stale `150K`/`65`/`57`.
- **Pure-stdlib + lazy** (code-quality + axiom + security): `import mlcroissant` only inside
  `validate_with_mlcroissant`; both modules import on a pure-stdlib box; AST guards ban
  `{random,time,uuid,datetime,secrets}`. **No egress** (security: grep+AST — only docstring
  assertions-of-absence + JSON-LD `@context`/license URI literals; writes no file, makes no remote call).
  **AX-002 determinism** (byte-identical across two builds; fixed context + ordered structures).

## Findings forwarded (non-blocking)

- **requirements-coverage**: full `mlcroissant` spec-conformance is deferred (skip-if-absent — the extra
  is not installed); successor = the scheduled Pass-2 CI image with `[croissant]` installed. The always-on
  stdlib shape check + the real `datasets` round-trip are the executable NFR-012 evidence in this env, and
  the skip-if-absent contract is itself pinned by a passing test naming the install command.
- **requirements-coverage / NFR-013**: the full cross-doc consistency sweep (README/DATASHEET/COMPARISON/
  TAXONOMY/…) is the explicit successor **S5-07**; the *generated* card already pulls canonical counts.
- **security-sast**: run the `mlcroissant` CVE scan at the epic/sprint gate once the opt-in extra is
  installed; keep any HF publish/upload an explicit opt-in verb, never wired into the emitters.
- **code-quality (OBS)**: `validate_with_mlcroissant` is intentionally NOT re-exported from
  `distribution/__init__` (the §8 export list is `build_croissant` / `validate_croissant` /
  `build_dataset_card`) — accessible via the full module path; acceptable.

## Outcome

S5-03 → **DONE**. The Croissant 1.0 JSON-LD emitter + HF dataset card ship; **NFR-012 closed** (Croissant
validates against the always-on schema-shape check AND the described Parquet loads via HF `datasets` with
the `reg_*` regime columns intact); FR-024's Croissant + dataset-card sub-clauses closed; gov-02 survives
into the machine-readable description; counts cannot drift (derived from `metadata.json`,
`== taxonomy.ENTITY_TYPE_COUNT`). Evidence: RED `bd1de34` → GREEN `0268642` → REFACTOR `c5d2234` → docs
`0d112c0`; **233 passed / 1 skipped** (223 prior + 10 new, 0 regressions); ruff + mypy --strict clean;
lazy `mlcroissant` (package imports without it); no network egress; frozen lattice / corpus / `v1.3.0` +
`pre-lattice-enrichment` tags untouched.
