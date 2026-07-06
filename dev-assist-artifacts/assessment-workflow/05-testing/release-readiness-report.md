# CAP-02 Powered Assessment Workflow — Release-Readiness Report (Stage 5, RE-RULED)

**Date:** 2026-06-01 (v2-scoring-harness close-out re-rule) · **Verdict:** **SHIP-WITH-CAVEATS** ·
**provisional_status:** AGENT_SIMULATED (release-CI), but the synthetic-only ceiling is now **empirically
demonstrated on REAL detector systems**, not just synthetic placeholders.

> This re-rule supersedes the 2026-06-01 first verdict (`git` history). It re-measures the Stage-2 NFRs against
> the close-out code shipped this session (strict TDD, both repos), incorporates two real evidence runs (E1
> real-systems, E2 full-corpus census), and **classifies every caveat** as permanent-by-design / pending-external
> / closed-this-session. a11y = **N/A** (library + 2 CLIs, no web UI; inherited from cycle-1).

## 1. Verdict basis — what changed since the first rule
The academically-sound assessment spine is unchanged and still green; this session **closed every
code-achievable caveat** the first verdict carried as PARTIAL / DEFERRED / roadmap, and **upgraded the headline
INDICATIVE caveat to real-systems**:

- **Real detectors now RUN** (C1 + orchestrator integration): Presidio, GLiNER, and Piiranha adapters are
  pluggable systems verified end-to-end against the real libraries (already installed in the consumer venv).
  **E1 powered real-systems leaderboard** (`runs/real-systems-powered/`): 1822-record powered sample → **15,569
  gold positives**, presidio **0.616 [0.608, 0.624]** > gliner **0.558 [0.550, 0.566]** > piiranha **0.285
  [0.278, 0.292]** (Wilson CIs), both adjacent pairs **Holm-significant** (paired McNemar χ²-continuity), prereg
  verified, worst-language `ko`@0.429, non-strippable synthetic-only caveat. The bundled-synthetic INDICATIVE
  caveat is **retired** — the run is now **real-systems on SYNTHETIC data** (the AX-001 ceiling still holds).
- **Full-corpus citable census** (E2, `runs/full-corpus-census-synthetic/`): `--preset full-corpus` over **all
  575,604 records / 2,486,438 gold positives**, descriptive-census with **CI + p-values SUPPRESSED at full scale
  (NFR-025 verified: no CI keys, empty pair-verdicts)**, power verdict LARGE.
- A **real defect the real-systems run exposed** was fixed: `mcnemar_exact` overflowed at ~15k discordant pairs
  (`int too large to convert to float`); now a principled exact/χ² selector (`stats.paired.mcnemar`) — the
  synthetic fixtures never hit it; real detectors did.
- **Wave-7 adversarial review: honesty boundaries CLEAN**; AX-004 separation holds; the MAJOR (AUPRC degeneracy
  not flagged) + MINOR (guard coercion gap) + OBS (tracks unused) findings are all **resolved + tested**.

**No MUST-track failure → no DEFER.** The remaining caveats are the **irreducible synthetic-only invariant +
the genuinely external (DUA / reference-host / real-user) items** — minimized to exactly those.

## 2. NFR verification matrix (NFR-019 … NFR-055) — re-ruled
| NFR | Attribute | First rule | **Re-rule** | Evidence |
|---|---|---|---|---|
| NFR-019/020 | Stats-core integrity; fabrication ban; significance.py quarantined | PASS | **PASS** | `test_p1_runpath_guard`, `test_p1_closure` (import-closure intact after the new orchestrator imports — all AUDITED eval-data modules) |
| NFR-021 | Seeded LOCAL-RNG; byte-identical | PASS | **PASS** | cross-process tests; E1/E2 byte-repro |
| NFR-022 | Integer-guarded CI inputs | PASS | **PASS** | `stats/intervals._require_int_counts` |
| NFR-023/024 | CI on 100% of metrics + selection rule | PASS | **PASS** | E1 powered: Wilson CI on every row |
| NFR-025 | Full-corpus descriptive-census suppresses CI | **PARTIAL** | **PASS** | C2 enforcement; **E2 proved it at 575,604 records** (no CI keys, empty pairs) |
| NFR-026/027/028 | Paired test + Holm + family + tie-gating | PASS | **PASS** | E1 both pairs Holm-significant; χ²-selector for large-n |
| NFR-029 | RD convergence reported | PASS | **PASS** | RD-NOT-CONVERGED honestly flagged |
| NFR-030 | Byte-reproducible from manifest | PASS | **PASS** | E1/E2 byte-repro incl. provenance index |
| NFR-031/032 | Pre-registration + plan-hash | PASS | **PASS** | prereg verified in both runs; design_point recorded |
| NFR-033/034 | Run-type scope; smoke inert | **PARTIAL** | **PASS** | C2 `rigor_bar_for_run_type`; dev/smoke suppress, leaderboard-submission full |
| NFR-035/036/037/039 | Powered-tier / named shortfall / design point | PASS | **PASS** | sampler 4-state; E1 powered |
| NFR-038 | Sampler streaming, bounded memory | PASS | **PASS** | two bounded passes; E2 sampled 575,604 |
| NFR-040/041 | v2.0.0 seam + regression contract | PASS | **PASS** | `test_pii_anon_eval_v2_contract` |
| NFR-042/043 | Run-record + **file-level** provenance | **PARTIAL** (file-level) | **PASS** | C8 `assessment/provenance.py` sha256 index over all artifacts; tamper-detecting; in E1/E2 |
| NFR-044 | Non-strippable synthetic-only caveat | PASS | **PASS** | rides every run incl. real-systems |
| NFR-045/055 | Anon/pseudo separate families (never merged) | INHERITED-PASS | **PASS** | C10 `assessment/tracks.py` lifts AX-004 to the assessment layer; **wired into the live orchestrator** + mutation-tested (incl. `__int__`/`__index__` coercion) |
| NFR-046 | Operating-point Fβ / AUPRC | **DEFERRED** | **PASS** | C4 `build_operating_point_view` (rejects lone-F1 / post-hoc); **AUPRC degeneracy flagged** in the view + leaderboard †footnote; lazy figure |
| NFR-047 | Honesty-set closed | **PARTIAL** | **PASS** | C7 worst-language + rank-volatility (Kendall-τ; UNMEASURED < 3 seeds) — both in E1/E2 |
| NFR-048/049 | Contamination disclosure + held-out attestation | **DEFERRED** | **PASS** | C3 governance block on every page + contamination (`unknown` rejected) + HMAC-signed attestation + recusal + scoring-API oracle |
| NFR-050 | Pure-stdlib cores + lazy heavy-dep | PASS | **PASS** | new cores stdlib; detectors import torch/transformers only inside factories; matplotlib lazy |
| NFR-051 | pii-rate-elo gates green | PASS (mypy not re-run) | **PASS** | **mypy clean on full src (61 files, 0 issues)**; ruff clean; 296/1 |
| NFR-052 | Lattice frozen 730@47c3a8f | PASS | **PASS** | `lattice --check` green; git-verified untouched |
| NFR-053 | NFR-018 power gate ON | PASS | **PASS** | `validate.py` PASS on 575,604 / 0 errors |
| NFR-054 | Doc-drift = 0 | PASS | **PASS** | suite green |

**Tally:** **24 PASS (+1 inherited) · 0 PARTIAL · 0 DEFERRED · 0 FAIL** (was 18 PASS / 4 PARTIAL / 2 DEFERRED).
Plus DC-30 regulatory crosswalk (FR-053) and DC-31 citation packaging (FR-054, DOI=pending sentinel) **built**.

## 3. Caveats — MINIMIZED + classified (non-strippable; never fabricated)

### 3a. PERMANENT-BY-DESIGN (cannot be removed, only empirically BOUNDED)
1. **Synthetic-only external validity (AX-001).** Every per-cell metric is precision on the SYNTHETIC
   distribution, NOT external validity, and not a standalone real-world recall claim. This rides every metric
   and figure **forever**; the real-data correlation slice (§3b) can BOUND it but never remove it. Even the new
   real-systems leaderboard is **real-systems on synthetic data**.

### 3b. PENDING-EXTERNAL (needs a real resource not available this session; code seam + handoff shipped, sentinel held)
2. **Real-data correlation (FR-027).** Bounds caveat 1. `correlate()` / `correlate_from_path()` return
   `RealDataAbsent` until a DUA-holding collaborator drops derived i2b2-2014/TAB scores at
   `PII_ANON_REAL_DEID_PATH`. Handoff: `05-pass2/FR-027/path-activated-ingest.md`.
3. **Reference-host throughput (NFR-010b, inherited).** `INSUFFICIENT_EVIDENCE` until a declared 8-core host
   runs `scripts/run_throughput_benchmark.sh --reference-host "<spec>"`; the agent-env can never publish a pass.
   Handoff: `05-pass2/NFR-010/reference-host-runbook.md`.
4. **Real-user operating-point re-elicitation (DC-27).** β=2 / recall_target=0.90 are R10-to-confirm defaults;
   real P-priv-eng + P-dpo must confirm. Instrument: `05-testing/05-pass2/operating-point-reelicitation/`.
   (Also: design real-user trial + concept-value re-confirm, inherited cycle-1.)

### 3c. CLOSED-THIS-SESSION (code-achievable; strict TDD, committed)
INDICATIVE→real-systems (C1+E1) · run-type rigor enforcement (C2/E2) · governance + contamination + attestation
(C3) · operating-point Fβ/AUPRC/precision@recall + degeneracy flag (C4) · regulatory crosswalk 63→GDPR/HIPAA/
CCPA/GLBA (C5) · citation/claims packaging (C6) · honesty-set worst-language + rank-volatility (C7) · per-artifact
sha256 provenance index (C8) · OutcomeDTO port (C9) · anon/pseudo separate-family tracks (C10) · coref/qid
scoring (C11) · throughput reference-host gate + runner (C12) · mypy green (C13) · full-corpus census (E2) ·
McNemar-overflow fix.

## 4. Guardrails (held — git-verified)
lattice `--check` 730@`47c3a8f` · doc-drift NFR-013 0 · NFR-018 power gate PASS on 575,604 / 0 errors ·
`eval_lattice.json` + corpus untouched since `47c3a8f` · tags `v1.3.0` + `pre-lattice-enrichment` intact ·
four metric families never merged (AX-004; now enforced at the assessment layer too) · pure-stdlib cores + lazy
heavy-dep · both suites green (eval-data **502/7**, pii-rate-elo **296/1**, mypy 0 issues, ruff clean) ·
`analysis/significance.py` quarantined (import-closure intact after the new orchestrator imports).

## 5. Verdict
✅ **SHIP-WITH-CAVEATS** — caveat set **minimized to the irreducible synthetic-only invariant (§3a) + the
genuinely external DUA/reference-host/real-user items (§3b)**. Every code-achievable caveat is closed (§3c). The
capability is academically sound and now **demonstrated on real detector systems** and **over the full corpus**;
the residual caveats are permanent-by-design or human-only, with code seams + exact handoff commands shipped.
The only path to unconditional SHIP runs through the §3b external resources — see the HUMAN-ONLY TODO
(`HUMAN-ONLY-TODO.md`).
