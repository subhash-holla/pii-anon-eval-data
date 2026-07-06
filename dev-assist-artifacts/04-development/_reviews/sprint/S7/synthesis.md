# Sprint Gate Synthesis — S7 (Extension seams; DC-10 / DC-14 / DC-01, v1.1)

**Gate:** sprint · **Scope:** S7 (5 stories) · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-31

| Reviewer | Verdict | Findings |
|---|---|---|
| requirements-coverage | ✅ APPROVE | 1 OBS (multilingual-carrier test — v1.1 nicety) |
| performance-benchmark | ✅ APPROVE | 1 OBS (Kendall-τ bootstrap O(n²·n_boot) for large n — v1.x sub-sample) |
| axiom-compliance | ✅ APPROVE | 2 OBS (DRY the synthetic≠external-validity caveat constant; guardrail-evidence note) |
| code-quality · traceability · security-sast | ✅ carried forward | APPROVE on all S7 story gates (S7-01, S7-02, combined S7-03-04) — unanimous |

**Aggregate: APPROVE** (zero MAJOR+). The new S7 modules needed **no coverage-hardening** (oracle 94%,
payloads 98%, slices 97%, correlation 94% — all ≥85%); the deferred coverage-source edits landed
(`pii_anon_datasets.validation` + `.subsets` added).

## Story roster (5/5 DONE, every story gate APPROVE)

| Story | Module / doc | Closes | Notes |
|---|---|---|---|
| S7-01 | `scoring/adversary/oracle.py` | FR-017 | PII-recognition oracle; non-strippable "never agent-leakage scoring" guard; recognition-only |
| S7-02 | `scoring/adversary/payloads.py` | FR-017 | injection payloads (base64/ocr/zero-width faithful transforms); INERT synthetic fixtures |
| S7-03 | `validation/correlation.py` | FR-027 | Kendall/Spearman bootstrap + Bland-Altman; **non-bypassable RealDataAbsent never-fabricate sentinel** |
| S7-04 | `subsets/slices.py` | FR-015/016 | coreference + quasi-id slice loaders; non-strippable ~72%-formulaic v1.1 low-power caveat |
| S7-05 | `ROADMAP.md` | FR-018/019/020 | roadmap stub — documented as v1.x, NOT shipped (honest framing) |

## MUST/SHOULD-coverage snapshot (sprint)

- **FR-017 FULLY covered** (oracle S7-01 + payloads S7-02) — both halves of the bipartite FR ship; the
  scope guard is type-enforced + stress-verified non-droppable.
- **FR-015 / FR-016 / FR-027** — v1 SEAMS verified (slice loaders + correlation harness + honesty guards);
  the actual coreference/qid SCORING + the real-data correlation are SHOULD / v1.1 / PERSONA-CONDITIONAL
  → carried to the **Stage-5 release-gate Pass-2 roster** (the traceability-matrix rows keep them
  PERSONA-CONDITIONAL/Pass-2 — no later row prematurely marks them verified).
- **FR-018 / FR-019 / FR-020** — documented as **roadmap** (S7-05 ROADMAP.md), NOT shipped. No orphans.
- Full suite **346 passed / 1 skipped**; the config-driven coverage gate now measures `validation` +
  `subsets`.

## Cross-cutting verification

- **5/5 scope-honesty disclaimers non-strippable** (axiom-compliance, verified at ground truth): oracle
  "never agent-leakage scoring"; payloads INERT "not weaponized"; correlation "synthetic ≠ external
  validity" + the RealDataAbsent never-fabricate sentinel; slices "~72% formulaic … LIMITED external
  validity"; ROADMAP "not implemented in v1" — each a non-defaulted-validated field or a doc-pinned string.
- **AX-001 INERT / synthetic** — an independent weaponization regex over all S7 artifacts returned ZERO
  matches; carriers are benign multilingual templates; no real PII.
- **NFR-004 pure-stdlib** — AST re-derived: zero banned imports across all 4 modules; correlation's only
  `random` use is a LOCAL `random.Random(seed)` (no module-global), mirroring `stats/paired.py`.
- **AX-002 determinism** — correlation bootstrap seed-deterministic (byte-identical CIs; immune to
  module-global RNG perturbation); oracle/payloads/slices clock/RNG-free.
- **Performance (advisory)** — slices/oracle/payloads O(n)/O(1); the Kendall-τ bootstrap is O(n²·n_boot)
  (sub-second to a few seconds at the intended dozens–hundreds validation-slice scale; no 575K corpus
  hot-path leakage). A faster τ / sub-sampling is a v1.x hardening.
- **Guardrails** — the full S7 diff is NEW/additive only; corpus / `eval_lattice.json` / tags (`v1.3.0`,
  `pre-lattice-enrichment`) NOT in the diff; `scoring/adversary/__init__` exports additive (existing
  base/offline/llm retained).

## Forwarded to Stage 5 / v1.x

- **Stage-5 Pass-2 roster (binding)**: FR-027 synthetic→real transfer delta (real i2b2/TAB correlation);
  FR-015/016 coreference/qid full scoring — the v1 seams ship; the real-data/full-feature work is Pass-2.
- v1.x niceties (non-blocking): multilingual-carrier test; faster τ for large-n bootstrap; a single-source
  constant for the synthetic≠external-validity caveat.

## Outcome

Sprint S7 → **APPROVE / DONE**. The extension seams ship: the agentic recognition oracle + inert payload
library (FR-017 fully closed), the never-fabricate real-data correlation harness (FR-027 seam), the
coreference/quasi-id slice loaders (FR-015/016 seam), and the FR-018/019/020 roadmap — all with
non-strippable honesty guards. Proceed to `/dev-assist-signoff SO-06-s7`, then Stage 5 Testing.
