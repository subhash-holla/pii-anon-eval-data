# D6 — Implementation-Ready Design (canonical)

**Stage 3 · 5-Diamond Cascade synthesis** · 2026-05-28 · Ready for Stage 4 Development.
Input: `02-requirements/` (28 FR + 17 NFR). Vocabulary: DC = Benchmark Component · UI = consumer surface.

> **Methodology/scale note:** the D1–D5 DIVERGE/CONVERGE/VALIDATE were authored directly (3-frame exploration + Pugh + switch-points documented per diamond) from the 50-agent Discovery+Requirements base — the design is strongly determined by the M6 "scorer-with-adapters" problem. A **representative D6 SME heuristic panel** (substituted framings) independently critiqued the synthesis (see `06-synthesis/sme-heuristic-findings.md`). Representative-scale per single-session limit; real-user/real-SME Pass-2 flagged. Full epistemic block at end.

---

## D0 — Prep: tensions + axioms
**Tensions resolved:** (1) *synthetic-vs-real-validity* → synthetic core + real-data correlation slice as a v1.1 extension seam (FR-027), caveats non-strippable; (2) *restructure-vs-additive* → **v2.0.0 schema unification** is in scope, gated by a migration script + v1.3.0 git tag + tagged archive (never delete); (3) *headline-vs-moat* → both ship (RRS headline + pseudonymization-integrity moat). **Axioms locked:** AX-001 no-real-PII, AX-002 determinism, AX-003 statistical-power, AX-004 anon/pseudo-separation (from `00-axioms/`).

## D1 — Design Cases (15 DCs locked)
Decomposition (JTBD lens preferred over Persona/Workflow-arc per Pugh — the benchmark's components map cleanest to *jobs*). DC↔FR map in `requirements-to-design` audit below.

| DC | Component | Primary FRs | Priority |
|---|---|---|---|
| **DC-01** | Corpus & slices (v2.0.0 records; financial-PII, per-language power, **committed-lattice enrichment — S-PWR**, coreference/quasi-id slices) | FR-024, NFR-001/003/011/018 | MUST |
| **DC-02** | Schema & annotation model (v2.0.0 unified) + **v1.3.0→v2.0.0 migration** | (schema) NFR-013, AX-002 | MUST |
| **DC-03** | Generation pipeline (deterministic, seeded, provenanced; LLM-gen w/ provenance) | NFR-004/006, AX-001/002 | MUST |
| **DC-04** | **Scoring harness core** — I/O contract + adapter framework (the M6 centerpiece) | FR-003 | MUST |
| **DC-05** | Detection scorer (P/R/F1/F2 + per-slice CIs + calibration) | FR-001/002/004/005 | MUST |
| **DC-06** | Anonymization scorer (residual re-id + utility Pareto) | FR-006 | MUST |
| **DC-07** | Re-identification scorer (measured-attack RRS + exposure index + pluggable adversary) | FR-007/008/009/010 | MUST |
| **DC-08** | Pseudonymization-integrity scorer (reversal/collision/referential/key-separation) | FR-011/012/013 | MUST (moat) |
| **DC-09** | Statistical-power & reporting engine (Wilson/Clopper-Pearson, paired stats, calibration, per-language table, **committed-lattice power audit + per-cell design provenance**, viz) | FR-004/029, NFR-001/002/003/008/018 | MUST |
| **DC-10** | Agentic oracle + payload library (bounded) | FR-017/018/019/020 | COULD |
| **DC-11** | Compliance/end-state bundle + regulatory crosswalk | FR-021/022 | MUST |
| **DC-12** | Distribution & exports (Parquet/Croissant/spaCy/CoNLL/HF card) | FR-024/028, NFR-012 | MUST |
| **DC-13** | Leaderboard & governance (held-out, opt-in, anti-gaming, GOVERNANCE.md, contribution pipeline) | FR-023/025/026, NFR-014 | MUST |
| **DC-14** | Real-data validation harness (correlation vs i2b2/TAB) | FR-027 | SHOULD (v1.1) |
| **DC-15** | Test suite & CI (pytest, line+branch coverage, gates) | NFR-016 | MUST |

**Switch-point:** DC-10/DC-14 carry `PERSONA-CONDITIONAL`/v1.1; built as extension seams, not v1-blocking.

## D2 — Workflow shape → **Linear batch + on-demand callable scorer** (Pugh-preferred)
3 frames: Linear / Event-Driven / Agent-Conversation. **Pugh-preferred: Linear** — data-prep is a deterministic linear pipeline (generate→annotate→validate→split→export); scoring is an **on-demand request/response** call (library/CLI). **Switch-point:** an append-only event log for *leaderboard submissions* (light event-sourced seam, governance/audit) — adopt when the hosted leaderboard ships (v1.x). Agent-Conversation rejected (no conversational workflow).

## D3 — Consumer surfaces → **Minimalist CLI + Information-Dense reports** (Pugh-preferred)
3 frames: Minimalist / Information-Dense / Conversational (adapted to surfaces, not screens). **Pugh-preferred hybrid:** Minimalist **CLI/Python API** (few clear verbs: `generate`, `score`, `export`, `validate`, `leaderboard`) + **Information-Dense report layer** (per-slice tables with CIs, reliability diagrams, privacy-utility **Pareto plots**, **slice heatmaps**, agent-leakage Sankey — the eval-doc recommended visualizations) + HF dataset card + Croissant. **Accessibility de-scoped** (markdown/static, no interactive web app) — kept doc-clarity only. **Switch-point:** Conversational (LLM-queryable results) = v2 delighter.

## D4 — System archetype → **Modular** (Pugh-preferred)
3 frames: Monolith / Modular / Event-Sourced. **Pugh-preferred: Modular** — decisive: the requirements demand **extension seams** (new slices, new metrics, new baselines, new adversaries, new export formats). Module boundaries = corpus · schema · generation · scoring-core · per-track scorers · stats/reporting · distribution · leaderboard · validation · tests. **Switch-point:** the leaderboard submission store is append-only (partial event-sourced seam for audit/anti-gaming). Monolith rejected (kills extensibility); full Event-Sourced rejected (overkill for a batch benchmark).

## D5 — Code pattern → **Hexagonal (ports & adapters)** for the scoring core (Pugh-preferred)
3 frames: Hexagonal / Clean / Capability-based. **Pugh-preferred: Hexagonal** — *the M6 problem IS a ports-and-adapters problem*: the **scoring domain** (detection/anon/pseudo/re-id metrics + stats) is the hexagon core; **inbound ports** = "a system's output" via the documented I/O contract (entity-type crosswalk + span-matching policy), with a **Presidio reference adapter** (FR-003); the **LLM adversary** is a pluggable outbound port (FR-010, cheap/offline adapter for NFR-009); **outbound ports** = exports/leaderboard/report adapters. This directly satisfies FR-003 (adapter), FR-010 (pluggable adversary), NFR-009 (offline adapter). **Switch-point:** **Clean architecture** for the stats/reporting subsystem (DC-09) — its dependency-rule discipline suits the math core; adopt Clean *within* DC-09, Hexagonal at the harness boundary. Capability-based rejected (no capability-security need for a CC0 benchmark).

---

## D6 — Synthesis: the implementation-ready hybrid

**Shape:** **Modular system** · **Hexagonal scoring core** (Clean inside DC-09 stats) · **Linear batch data-prep + callable scorer** · **Minimalist CLI + Information-Dense reports**.

### Module/package layout (target, Python; v2.0.0)
```
src/pii_anon/
  schema/        # DC-02: v2.0.0 record dataclasses + validators + migration (v1_3_0_to_v2_0_0.py)
  corpus/        # DC-01: slice definitions, loaders, splits, enrichment, financial-PII, coreference/quasi-id slices
  generation/    # DC-03: seeded generators + LLM-gen provenance (model+prompt+seed)
  scoring/
    core/        # DC-04: ScoringHarness, IO-contract, span-matching policy, adapter registry  ← hexagon core
    adapters/    # DC-04: presidio_adapter.py (reference), generic_jsonl_adapter.py            ← inbound ports
    detection.py        # DC-05
    anonymization.py    # DC-06 (residual-risk + utility Pareto)
    reidentification.py # DC-07 (measured RRS + exposure_index; adversary port)
    pseudonymization.py # DC-08 (threat-model; collision-type-separated; key/state separation)
    adversary/   # DC-07: pluggable adversary port — llm_adversary.py + offline_adversary.py (NFR-009)
  stats/         # DC-09: wilson/clopper-pearson CIs, paired (mcnemar/bootstrap), calibration (ECE/Brier), per-language power table  ← Clean core
  reporting/     # DC-09: reliability diagrams, privacy-utility Pareto, slice heatmaps, leakage Sankey, non-strippable caveat embedder (FR-009)
  compliance/    # DC-11: end-state bundle + legally-distinct regulatory crosswalk
  distribution/  # DC-12: parquet/croissant/spacy/conll exporters + HF card + dataset card
  leaderboard/   # DC-13: held-out store (append-only), submission policy, anti-gaming, governance metadata
  validation/    # DC-14: real-data correlation harness (i2b2/TAB) — v1.1 seam
  cli.py         # DC-03/12: minimalist verbs
tests/           # DC-15: pytest (line≥85% + branch≥70% on scoring/stats), fixtures, CI
```
Existing `scripts/` + `baselines/` are **wrapped** as adapters/migrated into this layout (brownfield: don't rebuild — `evaluate.py` becomes `scoring/detection.py` + reference adapter; `enrich_*.py` become `corpus/`/`generation/`; `conll_format.py` → `distribution/`).

### v2.0.0 schema + migration (DC-02) — the consequential change
- Unify the record schema (single source of truth for counts/version → fixes NFR-013 drift); add fields the new scorers need (system-output ingestion targets; per-slice power metadata; legally-distinct regulatory columns).
- **Guardrails (load-bearing):** `git tag v1.3.0` before any change; `migration/v1_3_0_to_v2_0_0.py` is deterministic + reversible-documented; v1.3.0 corpus archived (tagged); update DATASHEET/MIGRATION/CHANGELOG; **no record deleted without a tagged archive** (AX-002 + plan guardrail).

### Three audits
1. **Persona-service audit:** every persona served by ≥1 MUST DC — researcher (DC-05/06/07/09), tool-builder (DC-04/05/08/13/15), acad-deid (DC-05/06/07/09/14), red-teamer (DC-10), priv-eng (DC-05/09/11/12), dpo (DC-08/11). ✔ No persona unserved.
2. **Axiom-saturation audit:** AX-001 → DC-03 (generation) + DC-15 (no-real-PII test) + security scan; AX-002 → DC-02/03 (determinism tests); AX-003 → DC-09 (stats engine) + committed-lattice gate NFR-018 (`03-design/sampling-design.md`); AX-004 → DC-06/DC-08 separate modules + NFR-005 static check. ✔ All 4 axioms saturate the touched layers.
3. **Requirements-to-design traceability:** all 17 MUST FRs → a MUST DC (table in D1; **FR-029 → DC-09/DC-01** per the 2026-05-29 S-PWR amendment); 0 orphan FRs; 0 DC without an FR source. DIVERGED/PERSONA-CONDITIONAL (FR-015/016/027) → DC-01/DC-14 extension seams. ✔

### Build sequence (→ Development sprints)
1. **Foundations:** DC-15 (pytest+CI baseline) + DC-04 (scoring core + I/O contract + Presidio adapter) — unblocks everything (closes C1 + M6 spine).
2. **v2.0.0 schema + migration** (DC-02) — tag v1.3.0 first.
3. **Scorers:** DC-05 detection → DC-06 anon → DC-08 pseudonymization (moat) → DC-07 RRS (headline) — each TDD, each behind the core's ports.
4. **Stats/reporting** (DC-09) — Wilson/paired/calibration/per-language + viz + caveat embedder.
5. **Compliance** (DC-11) + **distribution** (DC-12: Croissant/Parquet/HF card) + **doc-drift fix** (NFR-013).
6. **Leaderboard/governance** (DC-13: GOVERNANCE.md, held-out, anti-gaming).
7. **Extension seams:** DC-10 agentic oracle (bounded), DC-14 real-data harness (v1.1), DC-01 coreference/quasi-id slices (v1.1).

### D6 revisions (post-SME panel — LOCKED into the design)
The 3-SME heuristic panel (`sme-heuristic-findings.md`) caught 1 CATASTROPHIC + 9 MAJOR, several from reading the real v1.3.0 code. Resolutions are now binding design constraints + Development requirements:
1. **RRS headline is the DETERMINISTIC offline adversary + exposure-index** (DC-07); the LLM adversary is a *version-stamped secondary* figure. Epsilon enforced as a CI gate; adversary version frozen in the leaderboard record. *(reidx-01 — protects reproducibility/comparability.)*
2. **Canonical integer (k,n) per metric on a frozen, versioned matching policy** (DC-04/09); partial-credit F1 reported separately and **excluded from binomial CIs**. The wrapped `evaluate.py` double-counting bug (partial added to both denominators) is **fixed, not inherited**. *(reidx-02.)*
3. **Deterministic optimal span assignment** (Hungarian-on-overlap + documented tie-break); `matching_policy_version` stamped on every score. *(reidx-03.)*
4. **NFR-001 power gate tests *effective* (near-duplicate-collapsed) positive counts** computed in `stats/` (not exact-hash dedup). *(reidx-04.)*
5. **Caveat is a mandatory non-defaulted field on the RRS/residual-risk VALUE OBJECT in `scoring/core`** — every serializer (report, Parquet, JSON, leaderboard) that drops it **fails a schema test**. Caveat travels with the number, not the renderer. *(gov-01 — FR-009 made structural.)*
6. **Regulatory crosswalk = N separate typed columns** in `compliance/` + `distribution/`; the existing `export_parquet.py` regime-flattening is **fixed, not inherited**; export test asserts each regime independently addressable, no equivalence field. *(gov-02 — FR-022 made structural.)*
7. **Held-out store records submitter affiliation + a no-pre-publication-access attestation; maintainer/`pii-anon-core`-affiliated submissions are flagged for recusal** — promoted from switch-point to **v1** for externally-published scores. *(gov-03 — §0 neutrality made structural.)*
8. **Package name continuity:** keep `pii_anon_datasets` (nest `scoring/` under it) OR ship a re-export shim ≥1 minor — **do not break the published wheel**. *(DX-01.)*
9. **Entity-type crosswalk = declared validated mapping FILE per adapter**, fail-loud on unmapped types (+ `--allow-unmapped`), versioned against the schema. *(DX-02 — kills the silent phantom-FP tax.)*
10. **CLI entry point** (`[project.scripts] pii-anon=…cli:main`) with 5 verbs as thin dispatchers; one copy-paste CI invocation. *(DX-03.)*
11. **Add type-relaxed matching** (FR-003 was unimplemented); **multilingual Presidio adapter** (not English-only); **NFR-005 check extends to reporting/compliance** (no combined "de-id" verdict); **AX-001 scan covers migrated records + the tagged v1.3.0 archive**; **reconcile** `scripts/migrate_v1_to_v2.py` vs new migration; **license clarity** (code Apache-2.0 / data CC0). *(cross-framing + gov-04/05 + DX-04/05.)*

### Epistemic honesty
- D1–D5 authored (3-frame + Pugh documented) not multi-agent-dispatched — economical given single-session budget; architecture strongly determined by the M6 problem. D6 critiqued by a **representative SME heuristic panel** (`sme-heuristic-findings.md`); **real-SME design review is a Pass-2 follow-up.**
- The v2.0.0 schema change is the consequential, repo-mutating step — Development gates it behind the v1.3.0 tag + migration + archive guardrails.
- All design inherits `provisional_status: AGENT_SIMULATED`.
