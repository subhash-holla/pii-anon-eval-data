# Security Checklist — pii-anon-eval-data

This benchmark publishes a PII dataset. The load-bearing security/ethics control is **axiom [AX-pii-anon-001](../00-axioms/project-axioms.yaml): synthetic-only, no real PII**. No domain pack is active; this checklist is the manual baseline until an automated real-PII pattern set is authored in Stage 4 Development.

## Release-blocking invariants

- [ ] **No real PII.** Every entity value traces to a synthetic generator or surrogate pool. No real natural person is identifiable from any record.
- [ ] **No accidental valid identifiers.** Structurally-valid SSNs (area/group/serial), Luhn-valid card numbers, real IBANs, real API keys/tokens appear ONLY as synthetic-generator output — never copied from real sources.
- [ ] **No secrets in the repo.** No real API keys, tokens, or credentials in code, configs, fixtures, or docs (use `sk-ant-test-…` / `XXXX` placeholders).
- [ ] **License preserved.** `LICENSE` intact; dataset license + intended-use documented in DATASHEET.

## Distinguishing synthetic PII (allowed) from real-PII leakage (blocked)

The corpus is *supposed* to contain PII-shaped strings. A naive scanner that flags all PII-shaped strings would flag the entire dataset. The Stage 4 scanner must instead detect **leakage** signals:
- Identifiers that pass real-world checksums AND were not emitted by a declared generator.
- Real public-figure names co-occurring with real contact details.
- Real-looking corporate email domains tied to named individuals outside the synthetic org pool.

## Provenance

- [ ] Every entity value is reproducible from a seeded generator or a documented surrogate pool (axiom [AX-pii-anon-002](../00-axioms/project-axioms.yaml)).
- [ ] LLM-generated/sanitized content records model + prompt + params + seed.

_Scan exceptions (if any) are tracked in [exceptions.yaml](exceptions.yaml) with sign-off citations._
