<!-- Thanks for contributing to PII-Anon! Please complete the checklist (see CONTRIBUTING.md). -->

## What changed & why


## Checklist
- [ ] **Traced requirement** — the FR/NFR (or roadmap item) this advances.
- [ ] **Tests added** — new/changed behavior is covered; `PYTHONPATH=src python -m pytest` is green.
- [ ] **Provenance** — for any data: generator + seed + `provenance.source_type` declared.
- [ ] **License** — CC0-compatible data / Apache-2.0 code; **no real PII** (AX-001) — fully synthetic only.
- [ ] **Docs** — README / TAXONOMY / DATASHEET / CHANGELOG updated if counts or behavior changed (the
      `tests/test_doc_drift.py` pins stay green).
- [ ] **Frozen assets** — I did NOT regenerate the corpus or mutate the committed lattice (730 cells @
      `47c3a8f`) or the `v1.3.0` / `pre-lattice-enrichment` tags.
- [ ] **Metric-family separation** — anonymization / pseudonymization / detection / re-id stay separate
      (AX-004); no fused "de-identification" score introduced.
