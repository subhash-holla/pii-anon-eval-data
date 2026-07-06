# Discovery §1 — Motivation & Background (CAP-02)

**Capability**: CAP-02 — Powered Assessment Workflow
**Stage**: 01-Discovery · Section 1
**Date**: 2026-06-01
**Method**: direct reading of both repos (eval-data + pii-rate-elo) at HEAD + three POV critiques (Adjacent-Product Skeptic / Persona Realist / OSS-Methodology Strategist). Every version/count/field/line claim below is cited to the file and line it was read from on 2026-06-01. Agent-synthesized framing is marked as such.
**provisional_status**: AGENT_SIMULATED (POV critics + reasoning are agent-simulated; the *code/version evidence* is direct file reads, not simulated).

> **Cycle-2 framing.** This is the second PDLC cycle of `pii-anon-eval-data`. Cycle-1 built the **dataset + scoring/stats cores** (Stage 5 verdict: SHIP-WITH-CAVEATS). CAP-02 builds the **assessment *workflow*** that runs the mature `pii-rate-elo` tournament against the v2.0.0 corpus over a powered, lattice-stratified sample — with epistemic instrumentation at every stage. Vocabulary remap (per project framing): Persona = assessment consumer; UC = Evaluation Scenario; FR = Assessment Capability; NFR = Quality Attribute; DC = Benchmark Component.

> **Scope honesty up front (the load-bearing distinction).** CAP-02 **delegates** tournament ranking, Glicko-RD convergence, and paired-significance *machinery* to `pii-rate-elo` — it does **not** re-implement them. CAP-02 **contributes** (a) a NIST-powered, lattice-stratified **sampler**, (b) **epistemic instrumentation** (per-cell Wilson/Clopper-Pearson CIs, WELL/UNDER/EMPTY power class with a *named shortfall*, non-strippable synthetic-only/anti-anonymity caveats), and (c) **reconciliation of the drifted dataset seam**. Powered stratified sampling is an established *method* (StratPPI; "With Little Power"); the contribution is its **integration** with a frozen 730-cell risk lattice and this specific 575,604-record synthetic corpus, not the statistics themselves.

---

## 1. Why this capability NOW

Cycle-1 produced two things that do not yet meet: a **v2.0.0 corpus** (575,604 records / 2,486,438 annotations / 63 entity types / 60 languages / `annotations` field; `DATASHEET.md:1,22,32`, `README.md:1,16,34`) and a **mature ranking engine** in the sister repo (`pii-rate-elo`) with a real Glicko tournament, bootstrap/McNemar/Bonferroni significance scaffolding, and paper-ready export. The gap CAP-02 closes is the **wiring between them, done to an academic-soundness bar** — and right now that wiring is not merely *missing*, it is **actively wrong** in three independent ways. Each is verified against the code, not asserted.

### 1.1 The drift problem — `pii-rate-elo` cannot honestly read the current corpus

The sister tool's dataset seam is **pinned to a stale dataset generation**. Read on 2026-06-01:

- **`pii-rate-elo/.../schema.py`** declares the record class for **v1.3.0**: module docstring `"EvalBenchmarkRecord: Evaluation benchmark record schema (v1.3.0)"` (`schema.py:8`); class docstring `"PII Anonymization Eval v1.3.0"` (`schema.py:95`); the default field `version: str = "1.3.0"` (`schema.py:137`); and `summarize_eval_dataset()` hardcodes `"version": "1.3.0"` (`schema.py:752`).
- **`pii-rate-elo/.../datasets/converters/pii_anon_eval.py`** hard-pins the **declared provenance** the converter reports to the rest of the pipeline:
  - module docstring: *"…159,891 records across 60 languages, 63 entity types…"* (`pii_anon_eval.py:5`),
  - `info()` returns **`num_records=159891`** (`pii_anon_eval.py:93`),
  - **`license="CC-BY-4.0"`** (`pii_anon_eval.py:221`),
  - **`citation="PII-Anon Evaluation Dataset v1.3.0"`** (`pii_anon_eval.py:222`),
  - description repeats *"159,891 records across 60 languages"* (`pii_anon_eval.py:224`).

The live artifact is **v2.0.0 / 575,604 records / CC0 (data) / `annotations` field** (`DATASHEET.md:1,22`; `README.md:1,16,34,371`). So a consumer reproducing from `pii-rate-elo`'s self-reported metadata gets the **wrong version, ~3.6× the wrong record count, the wrong license, and a stale citation**. A pre-registered, reproducible manifest is only credible if the loader's provenance matches the artifact; today it contradicts the dataset card.

> **Precision (so the POV is not over-claimed).** The *row parser* `_normalize_eval_row` already reads the v2-era `annotations` key with a `labels` fallback — `labels_raw = list(row.get("annotations", row.get("labels", [])))` (`schema.py:349`) — so the field-name drift is *partial* (the parser tolerates both). The hard, uncaveated drift is in the **declared provenance** (version / count / license / citation) the converter advertises, and in the **schema's self-identification as v1.3.0**. Reconciling that declared seam to v2.0.0 / 575,604 / CC0 is part of CAP-02. (Adjacent-Product Skeptic finding A2; Strategist CATASTROPHIC.)

### 1.2 No powered / pre-registered / reproducible assessment *path*

`pii-rate-elo` has **no concept of statistical power**, and its only subsetting knob is **naive head-truncation**:

- the converter yields rows until a count is hit — `if max_samples is not None and count >= max_samples: break` (`pii_anon_eval.py:82-84`);
- the loader does the same — `break` after `max_samples` (`datasets/loader.py:73`);
- the CLI threads `max_samples=ds_cfg.max_samples` straight through (`cli.py:145,624`).

Head-truncation returns the **first N rows in file order**. It cannot hit a per-cell target, cannot stratify by (language × entity_type × domain), and cannot *report a shortfall*. That is categorically different from what cycle-1 already built in **`eval-data/stats/power.py`** (read 2026-06-01):

- NIST/SEMATECH §7.2.4.2 proportion sizing `required_n()` (`power.py:67-78`), with tier targets **DERIVED, not hand-typed**: `Tier.CRITICAL`→**1522**, `STANDARD`→**753**, `LONG_TAIL`→**200** (`power.py:54-58,95-99`);
- a **parallel re-id ladder** at the re-identification operating point (`reid_required_n`, `REID_TIER_SPECS` → **897 / 385** pairs; `power.py:120-157`);
- `audit_crossing()` → a deterministic **`PowerMatrix`** with per-cell `PowerClass` (WELL / UNDER / EMPTY), a per-cell **`shortfall`**, and a corpus-level **SMALL / ADEQUATE / LARGE `verdict()`** (`power.py:235-240,288-465`).

**None of this is reachable through `pii-rate-elo`'s `max_samples` seam.** This is the **category gap** that justifies the capability: not "a better sampler" but "the first powered sampler over this corpus, with a power verdict the engine cannot emit." (Skeptic finding A1; Realist OBSERVATION on surfacing the verdict; Strategist OBSERVATION.) The frozen 730-cell lattice that the sample targets is committed at `47c3a8f` (the S-PWR commit; verified in `git log` for `stats/power.py`).

### 1.3 The academic-soundness gap — the two headline guarantees are computed by *fabricated* arithmetic in the consuming repo

This is the sharpest "why now." The academic-soundness bar requires that *every metric carries a CI* and *system-vs-system claims use a paired test*. As wired today, `pii-rate-elo` produces **both** from constants, not data. Read 2026-06-01 in **`pii-rate-elo/.../analysis/significance.py`**, which `cli.py:242` instantiates (`sig_tester = SignificanceTester()`, gated by `config.analysis.run_significance_tests`, `cli.py:240`):

- the **"bootstrap" CI** adds Gaussian noise to a point estimate instead of resampling: `se = metric_value * (1 - metric_value) / 100` with a hardcoded `100` (not n), then `noise = np.random.normal(0, se)` (`significance.py:204-207`);
- the **"McNemar" test** never sees a discordant-pair count: `n_approx = 100`, `z_stat = difference * np.sqrt(n_approx) / 0.05`, `pooled_sd = 0.1` (`significance.py:271-281`).

Meanwhile cycle-1's **`eval-data/stats/paired.py`** already implements the *correct* paired stack (exact binomial McNemar tail, Edwards continuity-corrected χ², and a real paired bootstrap that resamples pair indices with a seeded RNG for byte-reproducibility), and **`stats/intervals.py`** the integer-guarded Wilson/Clopper-Pearson CIs. The rigorous code exists **one repo over and is bypassed**. A single reviewer who diffs `significance.py` against `stats/paired.py` rejects the methodology outright. (Strategist SHOWSTOPPER.)

So CAP-02 is **not** "re-run `pii-rate-elo`." The honest statement of the present tense is: the engine is mature, but the path that produces its *statistical* claims is fabricated, its dataset seam advertises a stale/smaller/wrong-licensed corpus, and there is no powered sampler at all. CAP-02 routes the run path through the audited `eval-data/stats` core, reconciles the seam, and adds the sampler — and only *then* are the guarantees earned.

## 2. The macro context (why the bar is non-negotiable)

Agent-synthesized framing, grounded in cycle-1 §1 motivation and the 2026 sources the critics retrieved:

1. **Single-score vendor claims are the pathology this benchmark attacks.** The 2026 leaderboard-methodology consensus is "read the CI column, not the rank"; overlapping top-of-leaderboard CIs are a named failure mode. A benchmark whose entire thesis is *distrust of single numbers* cannot itself ship a number without a CI — which is exactly what `significance.py` does today.
2. **Synthetic benchmarks demonstrably *over*-estimate de-identification.** Peer-reviewed/industry evidence (SPY, NAACL SRW 2025; Tonic.ai 2026 — *"where PII detection still needs real data"*) makes the **non-strippable synthetic-only / anti-anonymity caveat** a precondition for peer-review survival, not decoration. Cycle-1 already enforces this *by construction*: `ReidProvenance.__post_init__` raises if the caveat is empty and `as_dict()` always serializes it (`power.py:181,187-202`). CAP-02 must carry that caveat through the report unchanged. This corresponds to the inherited axioms **AX-pii-anon-001 / -003** (`MANIFEST-capability.md:34,36`).
3. **Reproducibility — not pre-registration — is the active NLP norm (2026).** ReproNLP'26 (ACL) and REFORMS advocate *reproducibility from a manifest* and *per-subgroup sample sizes + CIs*; pre-registration is advocated-but-contested and *not* a default reviewer gate. CAP-02 therefore treats **seeded/byte-reproducible-from-manifest** as the table-stakes requirement (cycle-1 already delivers deterministic bytes + the lattice frozen at `47c3a8f`) and **pre-registration as opt-in rigor** for the one citation-chasing persona — not a universal gate. (Realist MAJOR.)

## 3. What CAP-02 must NOT claim (carry to Requirements as guardrails)

The three critics converge on the same failure modes; recording them here keeps the POV honest:

| # | Over-claim to avoid | Correct framing | Source |
|---|---|---|---|
| G1 | "An academically-sound assessment workflow" (reads as a *new tournament*) | Delegates ranking/convergence/significance *machinery* to `pii-rate-elo`; contributes sampler + instrumentation + seam fix | Skeptic A1; MANIFEST `Architecture (locked)` |
| G2 | "Powered representative **sample** (default)" as the hero for *all* tracks | Detection is compute-cheap → **full-corpus-audited by default**; the **LLM-adversary-bound tracks (re-id / pseudonymization)** are where a sample is load-bearing (cost), sized to the re-id tiers 897/385 | Realist MAJOR; `benchmark_throughput.py` `CANONICAL_RECORDS=575604` |
| G3 | "Powered sample **meets** lattice tiers" | `verdict()` needs ≥99.9% of 730 cells well-powered for LARGE; the *default* representative mode will honestly read ADEQUATE/SMALL with a **named shortfall**. State which mode (FULL opt-in vs representative) backs the *citable* leaderboard | Strategist MAJOR; `power.py:351-361` |
| G4 | "RD convergence" as a derived round-count | Report **achieved max-RD with its ±2RD (95%) interval**; do *not* publish heuristic round extrapolation as derived | Strategist MAJOR |
| G5 | "Comprehensive observability at every stage" (collides with existing progress logging) | Reframe as **statistical/epistemic** observability: per-cell CIs + power class + non-strippable caveats — the actual delta | Skeptic A3 |
| G6 | "Powered stratified sampling is novel" | It is an established **method** (StratPPI; "With Little Power"). Novelty is the **integration** (frozen 730-cell lattice ↔ this 575k corpus ↔ mature engine) | Skeptic A4 |
| G7 | "REPRESENTATIVE" (implies population inference) | Say **"lattice-stratified"** — the lattice is a committed estimability skeleton, not a natural-population sample of a synthetic corpus | Realist MINOR |

## 4. Hard preconditions CAP-02 commits to (all currently open)

Synthesized from the critiques; these become the spine of Requirements:

1. **Route the run path through the audited statistics core** — `pii-rate-elo` must call `eval-data/stats/paired.py` + `stats/intervals.py`; quarantine `analysis/significance.py` so no approximated statistic reaches a published number. *(Closes §1.3 / G4.)*
2. **Reconcile the dataset seam** — converter `info()` + `schema.py` self-identification → v2.0.0 / 575,604 / CC0 / `annotations`, so the manifest reproduces the stated artifact. *(Closes §1.1.)*
3. **Add the powered, lattice-stratified sampler** as a first-class stage, emitting the `PowerMatrix` verdict + per-cell shortfall as a *report artifact*, not an internal audit. *(Closes §1.2 / G3.)*
4. **Bind "sample" to the cost-bound tracks**; detection defaults to full-corpus-audited; declare the FULL-corpus run as the **citable** mode. *(G2.)*

## 5. Methodology & Epistemic Honesty

- **Direct evidence vs simulation.** Every version / count / field / line-number claim in §1 is a **direct file read** at HEAD on 2026-06-01 (paths + lines inline). The POV *critiques* and their prioritization are **AGENT_SIMULATED** — three simulated critics, not real reviewers — and are tagged accordingly per project framing. Their *web sources* (StratPPI 2406.04291; "With Little Power" 2010.06595; SPY NAACL 2025; ReproNLP'26; REFORMS; Glicko spec) were cited by the critics with 2026-06-01 retrieval; no independent re-crawl was performed in this section.
- **No corpus regeneration** is implied by this capability (frozen-guardrail discipline; `MANIFEST-capability.md:42`). The lattice stays frozen at `47c3a8f`.
- **Single-session limit.** Representative-scale methodology; agent-simulated research is not a substitute for real users — real-user validation of the CAP-02 personas/scenarios is a Pass-2 follow-up.

---
✅ **Section 1 DRAFTED (2026-06-01)** — ready for §2 (Personas & Workflows, CAP-02). Carry guardrails G1–G7 and preconditions 1–4 forward.
