# Brownfield Assessment — pii-anon-eval-data

**Date**: 2026-05-28
**Assessment by**: developer-assistant v0.1.0, `dev-assist-brownfield-assessment` skill
**Project root**: /Users/subhashholla/Development/pii_anonymize_pseudonymize/pii-anon-core/pii-anon-eval-data

> **Framing note.** This project is a **synthetic PII benchmark dataset + Python evaluation harness**, not a product with an end-user UI. The PDLC rubric is applied with the benchmark-dataset vocabulary remap recorded in `developer-assistant.yaml` and `MANIFEST.md`. "Personas" = benchmark consumers; "UI metaphor" = consumer surface (Python API / CLI / dataset card); accessibility is N/A by design. Ratings call the *methodology rigor* of the existing artifacts — not the quality of the data, which is substantial.

---

## 1. Project Profile

### Identity

| Field | Value |
|---|---|
| Name | pii-anon-eval-data (`pii-anon-datasets`) |
| Description | Multilingual 3-tier benchmark for PII detection, anonymization quality, and LLM re-identification resistance |
| Primary language | Python (`requires-python >=3.10`, `pyproject.toml:14`) |
| Framework | None (data package + scripts) |
| Runtime category | library + dataset + evaluation harness |

### Scope

| Field | Value |
|---|---|
| File count | ~30 source/doc files + 24 `.jsonl.gz` data files |
| Top-level dirs | `src/`, `scripts/`, `baselines/`, `integrations/`, `docs/` |
| Data scale | 159,891 records, ~1.24M annotations (`README.md:14-16`) |
| Scope class | **single-user / solo-maintainer** (1 git author; self-funded, `DATASHEET.md:14`) |

### Maturity

| Field | Value |
|---|---|
| Git commits | 8 (`git rev-list --count`) |
| Unique contributors | 1 (solo) |
| Version | 1.3.0 (`pyproject.toml:6`, README/CHANGELOG) |
| Last commit | `19ce769 v1.3.0: Tier 3 evaluation infrastructure` |
| Dependency-lock style | none (no lockfile; no declared deps) |
| History note | a `v2.0.0` commit already exists out-of-sequence in history (`70fa172`, between v1.0.0 and v1.1.0) — a prior aborted/renamed v2.0.0. **Relevant because this effort also targets v2.0.0; reconcile the version narrative.** |

### Tooling

| Capability | Status |
|---|---|
| Linter | **none** (no ruff/flake8 config) |
| Formatter | **none** (no black/ruff-format config) |
| Type-checker | **none** (no mypy config) |
| Test framework | **none** (no `tests/`, no `test_*.py`, no `conftest.py`, no pytest config) |
| CI | **none** (no `.github/workflows`, no pre-commit) |

> Single-user scope override is **active and documented**: cohort/tiering steps in downstream stages may be run at the user's chosen depth (the user elected **full rigor**, so the simulated cohorts will run rather than collapse). The accountability matrix reflects a solo maintainer.

---

## 2. Per-Stage Signal Extraction

| Stage | Signal dimension | Rating | Top evidence |
|---|---|---|---|
| Discovery | Personas (benchmark consumers) | WEAK | Implied by `DATASHEET.md:104-110` ("Uses": NER, multilingual NER, coreference, adversarial robustness, privacy-risk research) and `README.md:5-8`; no named persona docs |
| Discovery | Use cases (eval scenarios) | PARTIAL | `DATASHEET.md:104-110` + `README.md:243-277` enumerate consumer tasks; not in UC-NN situation/intent/outcome form |
| Discovery | Workflow maps | WEAK | Consumer flow visible in `README.md:42-67` (Quick Start) + `:297-333` (Scripts); no P/G/O-annotated maps |
| Discovery | Market context | **STRONG** | `COMPARISON.md` (head-to-head vs 9 benchmarks, full feature matrix) + `docs/PUGH_CHART_ANALYSIS.md` (8 weighted criteria) |
| Discovery | Concept value | MISSING | No user study, NPS, or cohort feedback anywhere |
| Requirements | Functional reqs (capabilities) | PARTIAL | Capabilities richly described (`README.md:69-197`, `CHANGELOG.md`); `scripts/validate.py` 8 checks ≈ acceptance criteria; no FR-NN with Given/When/Then |
| Requirements | Quantified NFRs (quality attrs) | WEAK | DATASHEET claims "0 errors" + coverage guarantee (`DATASHEET.md:49-50`); no NFR doc with thresholds/measurement/percentiles; **no statistical-power methodology** |
| Requirements | Traceability | MISSING | No UC↔FR↔test matrix |
| Requirements | Prioritization | MISSING | CHANGELOG records what shipped, not prioritized MUST/SHOULD/OUT |
| Requirements | Threshold validation | MISSING | No R10-style validation |
| Design | Design cases (components) | WEAK | Module/`scripts/` boundaries imply components; no DC-NN with FR→DC mapping |
| Design | Workflow shape | PARTIAL | Clear linear batch pipeline: generate→enrich→merge→validate→split→export (`README.md:297-333`, `DATASHEET.md:66-71`) |
| Design | UI metaphor | N/A | No UI; consumer surface is Python API + CLI + files |
| Design | System archetype | PARTIAL | Implicit modular batch system (generators / enrichers / baselines / integrations); undocumented as an archetype |
| Design | Architecture pattern | WEAK | `scripts/` import from `src/`; loose coupling, undocumented dependency direction |
| Design | Cross-cutting axioms | MISSING | No determinism / no-real-PII / privacy axiom checklist existed (now seeded at `00-axioms/project-axioms.yaml`) |
| Development | TDD discipline | MISSING | 0 tests; commits are version bumps, no RED→GREEN pattern |
| Development | Story discipline | WEAK | Coarse version-bump commits ("v1.3.0: …"); no stories/epics/DoD |
| Development | Review gates | MISSING | Solo; no CODEOWNERS, branch protection, or PR process |
| Development | Reviewer specialization | MISSING | None |
| Development | CI quality | MISSING | No CI, linter, formatter, or type-checker |
| Testing | Test type coverage | WEAK | `scripts/validate.py` (8 schema checks) + `baselines/evaluate.py` (eval harness) exist; **no unit/integration test suite** |
| Testing | Benchmark harness | PARTIAL | `baselines/evaluate.py` computes strict/partial/F2 + per-type/domain (`README.md:286`); only **regex** scored on **500** records (`baselines/results/regex_test.json`); Presidio/LLM unrun |
| Testing | Accessibility tests | N/A | No UI surface |
| Testing | Examples + tests pairs | WEAK | README examples exist; no example↔test pairing |

### Aggregate per-stage rating

| Stage | Rating | Strongest dimension | Weakest dimension |
|---|---|---|---|
| Discovery | **PARTIAL** | Market context (STRONG) | Concept value (MISSING) |
| Requirements | **PARTIAL** | Functional capabilities | Traceability / prioritization / threshold-validation (MISSING) |
| Design | **WEAK** | Workflow shape (PARTIAL) | Cross-cutting axioms (MISSING) |
| Development | **WEAK** | (functional code exists & runs) | TDD / CI / review gates (MISSING) |
| Testing | **WEAK→PARTIAL** | Benchmark harness (PARTIAL) | Test-type coverage (WEAK) |

**Headline:** the *content/data* is mature and differentiated; the *engineering and verification discipline* is the gap. This is a strong dataset wrapped in an unverified, undocumented-as-requirements pipeline.

---

## 3. Findings (5-Severity Taxonomy)

| Severity | Count |
|---|---|
| SHOWSTOPPER | 0 |
| CATASTROPHIC | 1 |
| MAJOR | 6 |
| MINOR | 5 |
| OBSERVATION | 5 |

### SHOWSTOPPER
- (none) — working source, rich README, real data and harness present.

### CATASTROPHIC
- **C1 — Zero automated tests; the scoring harness itself is unverified.** No `tests/`, no `test_*.py`, no CI (`find` + CI scan returned nothing). Every headline claim (annotation correctness, F1/F2 math, k-anonymity/RRS scoring) rests on `baselines/evaluate.py` + `scripts/enrich_*.py` that have no regression protection. For a benchmark whose *value is measurement correctness*, this is the critical gap. **Resolution:** Stage 4 builds a pytest suite (strict TDD) around the eval harness, validators, and a sample of generators before any v2.0.0 schema change.

### MAJOR
- **M1 — Documentation/data version drift undermines credibility.** Record count, entity-type count, and version disagree across docs: `DATASHEET.md:1,22` (v1.1.0 / 117,752 / 57 types), `TAXONOMY.md:1` (v1.2.0, lists ~80 type rows but claims 65), `README.md:3,18` (v1.3.0 / 159,891 / 65), `COMPARISON.md` (mixes v1.2/v1.3, "117K/151K/150K"). README's own schema example still shows `"version": "1.2.0"` (`README.md:205`). **Resolution:** single source of truth for counts/version; regenerate docs from data.
- **M2 — No quantified NFRs and no statistical-power methodology.** Both research briefs make per-slice statistical power the difference between "a big dataset" and "a credible benchmark" (`pii_eval_may26.md` §"Recommended evaluation program": ≥753 positives for recall≈0.98 ±1pp; stratified enrichment for rare classes). The project has coverage prose but no sample-size-per-slice, per-metric CIs, or calibration. **Resolution:** Stage 2 NFRs quantify these; encoded as axiom AX-pii-anon-003.
- **M3 — No traceability** between claimed capabilities and any verification artifact. **Resolution:** Stage 2 traceability matrix; Stage 4 ties tests to FR/NFR IDs.
- **M4 — Benchmark is largely unrun: only one partial baseline.** `baselines/results/` contains only `regex_test.json` (500 records; strict F1 0.5335, recall 0.3846). Presidio + LLM baselines are coded but unscored; there is no leaderboard. A benchmark with one partial baseline cannot yet substantiate comparative claims. **Resolution:** run/score Presidio + Claude on the full test set; publish a leaderboard surface (HF).
- **M5 — Reproducibility/installability gaps in `pyproject.toml`.** No `[project.dependencies]`; baselines import `presidio`, `openai`, `anthropic` (`README.md:284-286`) with nothing declaring them; no dev-deps (pytest); no entry points; classifier asserts `Development Status :: 5 - Production/Stable` (`pyproject.toml:11`) despite 0 tests/CI. **Resolution:** declare runtime + optional `[baselines]`/`[dev]` extras; downgrade status until tests land.
- **M6 — Anonymization and pseudonymization are not actually *scored*.** `evaluate.py` scores detection (span F1) only. Tier-2/Tier-3 fields are **precomputed annotations on records**, not a harness that ingests a *system's* anonymized/pseudonymized output and scores residual re-id risk, utility, reversal integrity, or collision. This is the core thesis of the effort and is currently absent as scoring capability. **Resolution:** Stage 3 designs separate anon/pseudo scoring APIs (axiom AX-pii-anon-004); Stage 4 builds them.

### MINOR
- **m1 — Personas implicit, not formalized** (`DATASHEET.md:104-110`). Formalize 6 consumer personas in Discovery.
- **m2 — Use cases described as prose "uses," not UC-NN** form. Convert in Discovery §4.
- **m3 — Partial-overlap scoring may be inert.** `regex_test.json` shows `partial_f1 == strict_f1 == 0.5335` and `partial_matches: 0` overall — partial-credit path looks unexercised/untested. Verify in Stage 4.
- **m4 — Version-history confusion.** Stale `v2.0.0` commit (`70fa172`) predates v1.1.0. Document the version narrative before re-using v2.0.0.
- **m5 — No design artifacts** (DC roster, architecture pattern, axioms) — system shape is implicit only.

### OBSERVATION
- **o1 — `COMPARISON.md` + `docs/PUGH_CHART_ANALYSIS.md` are near-methodology-grade market research** → extract directly into Discovery §3 (KEEP_AS_IS / MERGE), refresh competitor data with 2025-26 web research.
- **o2 — `DATASHEET.md` (Gebru framework) is a strong base** → extract into Requirements + distribution; refresh to v2.0.0 and resolve the training-vs-evaluation contradiction below.
- **o3 — `TAXONOMY.md` is a strong entity spec** → extract into Requirements; reconcile the 57/65/~80 type-count discrepancy first.
- **o4 — The `scripts/` pipeline (15 scripts) + `baselines/` + `integrations/` are reusable** → WRAP, don't rebuild; layer tests + new metrics on top.
- **o5 — Intended-use contradiction.** `DATASHEET.md:116` says "should not be used for training," yet the project ships 70/10/20 **train** splits (`README.md:55-57`) and a CoNLL exporter that emits `label2id.json` for HF **training** (`integrations/conll_format.py`). Resolve the dataset's intended-use statement.

---

## 4. Bring-Forward Plan (Impact × Effort)

### High impact / Low effort (do first)
1. **Reconcile version/count drift** (M1) — one source of truth; regenerate docs. Effort: S.
2. **Declare deps + dev/baseline extras; fix status classifier** (M5) — installable + reproducible. Effort: S.
3. **Add a minimal CI workflow** (lint + validate + pytest) so every later change is gated. Effort: S.
4. **Run + score Presidio + Claude baselines on the full test set** (M4) — first real leaderboard rows. Effort: M.

### High impact / High effort (plan into Development)
1. **pytest suite around the eval/enrich/validate code** (C1), strict TDD. Effort: M-L.
2. **Separate anonymization & pseudonymization scoring harnesses** (M6) — residual re-id + utility; reversal/collision/referential-integrity. Effort: L.
3. **Statistical-power layer** (M2) — stratified enrichment + sample-size planner + per-slice CIs. Effort: L.
4. **Calibration (ECE/Brier) + reliability + abstention**, and **agentic-leakage scored suite**. Effort: M-L each.

### Low impact / Low effort (polish)
1. Formalize personas (m1) + UCs (m2); tag examples↔tests.
2. Verify/repair partial-overlap scoring (m3).

### Low impact / High effort (defer)
1. **Real-user Pass-2 study** with benchmark consumers — defer to a post-v2.0.0 follow-up (cannot be agent-simulated; see §6).

---

## 5. Retroactive Artifact Proposals

### Discovery (retroactive)
| Artifact | Extractable | Gaps to fill |
|---|---|---|
| `personas.md` | ~6 consumer personas inferable from DATASHEET Uses | tier-of-care, sub-archetypes, adoption signal |
| `use-cases.md` | ~8-12 eval scenarios from DATASHEET Uses + README dimensions | situation/intent/outcome, acceptance, anti-cases |
| `market-research.md` | **STRONG** from COMPARISON + PUGH_CHART_ANALYSIS | refresh 2025-26 competitors (PIIBench, PrivaCI-Bench, AgentDojo, WebPII); JTBD + Kano |
| `discovery-report.md` | synthesize after above | synthesis pass |

### Requirements (retroactive)
| Artifact | Extractable | Gaps to fill |
|---|---|---|
| `functional-requirements.md` | capabilities from README/CHANGELOG/TAXONOMY | Given/When/Then; boolean-testable verification |
| `non-functional-requirements.md` | coverage/validation guarantees from DATASHEET | quantified thresholds, **statistical power**, calibration, determinism, ethics |
| `traceability-matrix.md` | (after R8) | full UC↔FR/NFR↔DC↔Task↔Test |
| threshold-validation | (R10) | per-NFR threshold stress-test |

### Design (retroactive)
| Artifact | Extractable | Gaps to fill |
|---|---|---|
| design-cases | components from `src/`+`scripts/` boundaries | DC roster + FR→DC map (corpus/schema/generation/eval/scoring/distribution) |
| system/architecture | apparent linear-batch + modular shape | documented archetype + the **v2.0.0 schema + migration** decision |
| `D-implementation-ready-design.md` | synthesis | anon/pseudo scoring APIs, calibration, statistical-power, agentic-leakage models |

### Development / Testing (retroactive)
| Artifact | Extractable | Gaps to fill |
|---|---|---|
| test suite | validate.py checks convertible to assertions | full pytest suite + fixtures + CI |
| NFR verification matrix | regex baseline row | all baselines × slices, per-slice CIs, calibration |
| examples+tests catalog | README examples | 1:1 example↔test pairs per component |

---

## 6. Pass-2 Recommendations (real-user/SME — not agent-simulable)

| Recommendation | Reason | Suggested protocol |
|---|---|---|
| Benchmark-consumer interviews | Personas inferred, not validated | 5-8 real researchers/privacy engineers |
| Real-detector leaderboard submissions | Only synthetic/own baselines exist | invite external systems to score on the test set |
| SME review of anon/pseudo scoring design | New, high-stakes scoring semantics | 1-2 privacy-eval SMEs review the metric definitions |

---

## 7. Methodology Block (Epistemic Honesty)

**What this assessment is:** a structural, citation-backed pattern-match of existing project state against PDLC rigor rubrics, adapted for a benchmark-dataset project.

**What it is not:** a code review (data/annotation *correctness* is out of scope — flagged for Stage 4 testing), nor a verdict on dataset quality (the data is substantial and differentiated).

**What it can't see:** the maintainer's implicit design intent, unwritten priorities, and any real-user signal held outside the repo. The single-user override means several "MISSING process" findings (review gates, story discipline) reflect a solo workflow, not negligence — they become relevant precisely because the goal is now a *publishable, world-class* benchmark with external consumers.

---

## 8. Next Steps

Per the approved master plan, proceed to **CHECKPOINT 1** (this report) → **Stage 1 Discovery** in brownfield mode:
`/dev-assist-discovery` — extracts the STRONG market-research + entity-spec signal, formalizes the 6 consumer personas and eval-scenario use cases, and refreshes competitor data with 2025-26 web research. Discovery will surface MISSING/WEAK signals as explicit open items rather than silently filling them.
