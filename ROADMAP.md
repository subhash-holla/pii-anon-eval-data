# Roadmap

This roadmap records the agentic-leakage and validation directions that PII-Anon **intends** to add in a
future **v1.x** — and, just as importantly, what is **NOT** implemented in v1. PII-Anon v1 ships a
*PII-recognition oracle* (`pii_anon_datasets.scoring.adversary.oracle`) and an *injection-payload library*
(`pii_anon_datasets.scoring.adversary.payloads`), both of which are **never marketed as agent-leakage
scoring**. The items below build on those v1 seams but are deliberately out of v1 scope.

## v1.x — agentic-leakage roadmap (NOT implemented in v1)

These are **roadmap / future** items. They are documented here for transparency; **none of them is shipped
or measured in v1**.

### FR-018 — Cross-turn fragmented-leakage payloads

**Status: roadmap (v1.x), not implemented.** Multi-turn agent scenarios where an identity is *fragmented
across turns* (e.g. a partial name in turn 1 + a partial date-of-birth in turn 4) and reassembled. v1 ships
only single-span obfuscated payloads (the S7-02 `InjectionPayload` library); the cross-turn fragmentation
seeding is future work.

### FR-019 — Transcript residual-leakage estimate

**Status: roadmap (v1.x), not implemented.** A per-channel / per-turn behavioral-signal-residual estimate
over agent transcripts, emitted **with a transcript-distribution caveat** (a final-output-only "low risk"
verdict is explicitly out of scope). v1 measures re-identification resistance on static records, not
transcripts.

### FR-020 — Live-harness adapter

**Status: roadmap (v1.x), not implemented.** An adapter integrating the recognition oracle into live agent
harnesses (AgentDojo / InjecAgent), invoking the oracle at each of AgentLeak's 7 channel boundaries. v1
ships the callable oracle (the seam); the live-harness integration is future work.

## Other deferred items (v1.1 / Pass-2)

The following ship their **v1 seam** now, with the full feature deferred to a v1.1 / real-data Pass-2:

- **FR-015 / FR-016 — Coreference-chain & quasi-identifier-combination scoring.** v1 ships the slice
  loaders (`pii_anon_datasets.subsets.slices`) with a non-strippable 79.2%-formulaic low-power caveat; the
  actual chain-as-a-unit / quasi-identifier-combination *scoring* is v1.1.
- **FR-027 — Real-data validation correlation.** v1 ships the correlation harness
  (`pii_anon_datasets.validation.correlation`) with Kendall-τ / Spearman + seeded bootstrap + Bland-Altman;
  but the real i2b2-2014 / TAB data is not present, so the harness returns a `RealDataAbsent` sentinel and
  **never fabricates** a correlation. The synthetic→real transfer delta is a real-data Pass-2 deliverable.
  See the public [External-Validity Protocol (FR-027)](docs/external-validity-protocol.md) for the
  pre-registered statistical plan (τ\*=0.60, seed 20260603), verdict mapping, and activation flow.

## Honesty note

Nothing in this roadmap is implemented in v1. The agentic-leakage direction is anchored by the v1
recognition oracle + payload seams, which are recognition / fixture tools — **never agent-leakage
scoring**. Synthetic-distribution coverage is not external validity; see the real-data correlation slice.
