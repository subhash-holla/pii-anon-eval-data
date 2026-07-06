---
capability_id: CAP-02
canonical_manifest: ../MANIFEST.md
schema_version: 2
---

# CAP-02 — Powered Assessment Workflow (convenience mirror)

> ⚠️ The **canonical** status tracker is the root `dev-assist-artifacts/MANIFEST.md` → "Capability 2" section.
> This file is a convenience mirror for working inside the subtree. Keep both in sync; on conflict the root wins.

## Capability

An academically-sound, repeatable, reportable assessment workflow that runs the existing **pii-rate-elo**
tournament against PII-Anon **v2.0.0** over a **powered representative sample (default)** / **full corpus
(opt-in)** / **smoke (fast)** — with observability + reporting integrated at **every** stage of working with
the dataset (load → sample → run systems → score → rate → report).

**Architecture (locked):** eval-data OWNS sampling + observability + reporting; `pii-rate-elo` CONSUMES.

## ID offsets (global, never renumber/reuse)

| Artifact | Cycle-1 max | CAP-02 start |
|---|---|---|
| UC (Evaluation Scenario) | UC-15 | **UC-16** |
| FR (Benchmark Capability) | FR-029 | **FR-030** |
| NFR (Quality Attribute) | NFR-018 | **NFR-019** |
| DC (Benchmark Component) | DC-15 | **DC-16** |
| Sprint | S7 / S-PWR | **S8** |
| Sign-off | SO-06 | **SO-07** |
| Axiom | AX-pii-anon-004 | **AX-pii-anon-005** (if confirmed) |

## Inherited axioms (still binding)
- **AX-pii-anon-001** synthetic-only / no-real-PII
- **AX-pii-anon-002** deterministic-reproducible generation + scoring (seeded, byte-reproducible)
- **AX-pii-anon-003** stated statistical power (every reported metric declares n + CI; tiered targets)
- **AX-pii-anon-004** anonymization / pseudonymization scored by SEPARATE metric families

## Frozen guardrails (must stay green — do NOT regress)
- `python -m pii_anon_datasets.stats.lattice --check` → 730 cells @ `47c3a8f`
- `scripts/validate.py --lattice` → NFR-018 power gate ON
- `pytest -k nfr_013` → doc-drift 0; tags `v1.3.0` + `pre-lattice-enrichment` intact; NO corpus regeneration
- NFR-005 four metric families never merged; pure-stdlib cores + lazy heavy-dep guards
- eval-data full suite green (363/1 + new); pii-rate-elo `pytest`+`ruff`+`mypy` green

## Stage status (mirror)
| Stage | Status |
|-------|--------|
| 01-Discovery | COMPLETE (UC-16..23; 8 UCs) |
| 02-Requirements | COMPLETE (FR-030..054; NFR-019..055; AX-005 confirmed) |
| 03-Design | COMPLETE (DC-16..31; build seq S8-S12; L4/P1 resolved) |
| 04-Development | COMPLETE (S8-S12; real-data E2E proven; eval-data 394/6, pii-rate-elo 268/1) |
| 05-Testing | COMPLETE (SHIP-WITH-CAVEATS; NFR-018 gate PASS on 575,604) |
| 04-Development | NOT_STARTED |
| 05-Testing | NOT_STARTED |
