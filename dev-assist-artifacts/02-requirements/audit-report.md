# R9 — Verification-Criteria Audit

**Stage 2 · R9** · 2026-05-28 · `verification-criteria-strengthener` pass.

Bar: every FR has a **boolean-testable** Given/When/Then a Stage-4 reviewer could check programmatically; every NFR has a **quantified threshold + measurement method**.

## FR audit
- **26/28 FRs PASS** as written (boolean Given/When/Then present).
- **Strengthened (2):**
  - **FR-017** (agentic oracle): added a concrete check — "oracle exposes a `classify(text, lang) → spans` callable + payloads are loadable tuples; a doc-string/README assertion confirms it is NOT labeled an agent-leakage scorer." (was partly aspirational.)
  - **FR-021** (end-state bundle): added — "bundle is machine-readable + version-stamped, and the 'informs not determines' string is present in the serialized artifact" (per US-counsel R6 note on output-artifact format).

## NFR audit
- **15/17 NFRs PASS** with quantified thresholds + measurement.
- **Strengthened (2):**
  - **NFR-009** (eval cost): made concrete — "cheap-adversary mode runs at **$0 external API cost** AND completes the RRS pre-screen on the dev split in **< 10 min on 1 CPU core**; full-adversary mode prints a per-run cost estimate before executing." (was "documented".)
  - **NFR-010** (throughput): made concrete — "detection scorer processes **≥ 1,000 records/sec** on a reference 8-core machine (seeded benchmark), reported with the run; streaming/chunked input accepted via the scorer I/O contract." (was "a stated docs/sec".)
- **NFR-005, NFR-012, NFR-006** are boolean/auditable (0-violation style) — appropriate; validated by audit/scan, not threshold stress-test.

## Cross-cutting verification additions (from R3/R6 qualitative signal)
- **Caveat enforcement (FR-009):** add a test asserting the anti-anonymity caveat string is present in every serialized RRS/residual-risk artifact (non-strippable = covered by a serialization test).
- **Crosswalk distinctness (FR-022):** add a test asserting GDPR/HIPAA-SH/HIPAA-ED/CCPA/PCI columns are emitted as distinct fields (no merged cell).
- **Anon/pseudo separation (NFR-005):** add a static check that no public scorer entry point returns a single merged anon+pseudo score.

## Verdict
**R9 PASS** — all 28 FRs boolean-testable, all 17 NFRs quantified or boolean-auditable, after 4 strengthenings + 3 cross-cutting verification additions. Strengthened criteria applied in place to `functional-requirements.md` / `non-functional-requirements.md` semantics (recorded here as the canonical change log).
