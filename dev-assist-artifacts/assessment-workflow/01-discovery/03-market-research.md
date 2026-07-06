# Discovery §3 — Market Research (CAP-02 Assessment Workflow)

**Stage**: 01-Discovery · Section 3 (cycle-2: assessment-workflow)
**Date**: 2026-06-01
**Method**: Agent-synthesized JTBD + Kano + Pugh, grounded in cycle-1 §2 personas (`../../01-discovery/personas.md`), the refined POV (`../../01-discovery/00-pov-stress-test.md`), MEMORY academic-soundness bar, and the two repos (eval-data + pii-rate-elo). Live web evidence for status-quo/reproducibility forces.

> **Epistemic honesty.** This is the SECOND PDLC cycle and concerns the *assessment workflow* (CAP-02: load → sample → run → score → rate → report over a powered/full/smoke sample), NOT the dataset. Personas are **reused** from cycle-1 (the benchmark *consumers* are the workflow's hirers). All JTBD forces, Kano labels, and Pugh cells are **AGENT_SIMULATED** (`provisional_status: AGENT_SIMULATED`) — not real-user-validated. Real-user job-interview + Kano-survey validation (ACL/PETS authors, Presidio/GLiNER maintainers, i2b2/n2c2 participants, DPOs) is a Pass-2 follow-up. WTP ≈ $0 (CC0); categories rest on credibility/citability, not spend.

---

## A. JTBD — the core job

**When** I need to make a defensible, reportable claim about how PII systems rank on the v2.0.0 corpus, **I want to** run the existing pii-rate-elo tournament over a *right-sized, pre-registered, seeded* sample with observability and a CI on every number, **so I can** publish/cite a result that survives peer + regulator review without burning a full-corpus run each time.

- **Functional**: load → sample (powered / full / smoke) → run → score → rate → report, byte-reproducibly from a manifest; meets NIST power tiers or is flagged UNDER-POWERED with the shortfall named.
- **Emotional**: done well → *confidence* ("a reviewer can rerun this"); done poorly → *dread* of the synthetic-only + "you p-hacked / can't reproduce it" rejection.
- **Social**: signals methodological rigor to ACL/PETS reviewers and DPOs; self-signals "I'm not the vendor gaming my own leaderboard."

### Forces (Push / Pull / Habit / Anxiety)
- **Push** (off status quo = ad-hoc full-corpus run): full corpus (575,604 records) is slow/expensive; no power method → "statistically-powered" is unearned; ad-hoc runs "unrealistically favor their tool" and resist comparison; version/seed ambiguity ("which dataset, which code, can I trust the saved result?"); the dataset seam has **drifted** — pii-rate-elo pinned to stale v1.3.0 / 159,891 / "labels" vs v2.0.0 / 575,604 / "annotations".
- **Pull**: powered sample = fast + credible; pre-registration + manifest = reproducibility; per-slice CIs (Wilson/Clopper-Pearson) + paired tests (McNemar / paired bootstrap) + RD convergence = claims that pass review; observability at every stage.
- **Habit / switching cost**: the existing ad-hoc CLI "just works" and is already learned; the powered path adds sampling-design + pre-registration ceremony up front.
- **Anxiety**: "is the powered sample *really* representative, or will I miss a slice?"; fear a smaller sample weakens a headline; trusting an extended seam over the engine they know.

**Currently "hired" solution**: run pii-rate-elo on the full corpus ad-hoc, hand-roll significance/reporting, eat the cost and the reproducibility gap (MEMORY status quo).

### Cross-persona pattern
Researcher (P-mlnlp) / tool-builder (P-tool-builder) / acad-deid (P-acad-deid) — the 3 HIGH gating personas — all hire it for the *same* job: **"powered + reproducible + reportable, without full-corpus cost."** This is the substrate capability; the **powered-sample default** (vs full opt-in / smoke) is the differentiating feature.

---

## B. Kano — feature categorization & sequencing (T1 = the 3 HIGH gating personas)

| Feature | Avg category (T1) | Sequencing |
|---|---|---|
| Seam reconciliation (v1.3.0/"labels" → v2.0.0/"annotations") | **Must-have** (invisible correctness floor) | v0.1 sprint 1 |
| Per-metric confidence intervals (Wilson / Clopper-Pearson) | **Must-have** | v0.1 sprint 1 |
| Paired tests for system-vs-system (McNemar + paired bootstrap) | **Must-have** | v0.1 sprint 2 |
| Pre-registration / byte-reproducible seeded manifest | **Must-have** | v0.1 sprint 2 |
| Honest UNDER-POWERED / INSUFFICIENT_EVIDENCE verdicts | **Must-have / Delighter** | v0.1 sprint 2 (cheap, high-trust) |
| Powered representative sample (NIST tiers) + UNDER-POWERED flag | **Performance / Delighter** | v0.1 sprint 3 |
| Per-stage observability run-records (load→…→report) | **Performance** | v0.1 sprint 3 |
| Leaderboard + auto-generated figures | **Performance / Must-have** | v0.1 sprint 4 |
| SMOKE preset (sub-minute sanity run) | **Delighter** | v0.1 sprint 4 (low cost) |
| FULL-corpus opt-in (575,604 records) | **Performance / Indifferent** | v0.2 (defer; sample covers v0.1) |

**Delighter shortlist (land 1–2 in v0.1):** (1) **Honest UNDER-POWERED / INSUFFICIENT_EVIDENCE verdicts** — directly disarms the universal synthetic-citation-ceiling objection (§2 signal #1); near-zero build cost (harness self-stamps, per NFR-010). (2) **SMOKE preset** — an unexpected CI/DX win for tool-builders, the contribute-recognizers cohort whose advocacy drives adoption.

**Reverse-feature eliminations (presence dissatisfies):** certification / paid private eval runs (POV decision (b) — re-introduces neutrality CoI); headlining a "live agentic-leakage benchmark" from static records (category-mismatch, AgentLeak 41.7% missed — scope as recognition-oracle only); bespoke per-domain scoring configs beyond the frozen 730-cell lattice (maintenance + reproducibility-drift risk).

---

## C. Pugh — CAP-02 vs alternatives

**Absolute scoring (0–5; higher = better).** Baseline datum = **Alt A** (run pii-rate-elo full-corpus as-is) = the literal status quo. Criteria fixed before scoring; derived from the MEMORY soundness bar + cycle-1 J3 ("defensible, peer-acceptable number").

| Criterion | Weight | **CAP-02** | Alt A (full-corpus as-is) | Alt B (ad-hoc subsample) | Alt C (Presidio-style scripts) | Alt D (HELM-style harness) |
|---|---|---|---|---|---|---|
| C1 Academic soundness (power tiers, CIs, paired tests, RD) | 28% | 5 | 3 | 1 | 1 | 3 |
| C2 Reproducibility (seeded / byte-repro / pre-registered manifest) | 22% | 5 | 3 | 1 | 2 | 4 |
| C3 Cost / runtime efficiency | 15% | 4 | 1 | 5 | 4 | 2 |
| C4 Fairness / anti-gaming (held-out, version-pinned adversary, non-strippable caveat) | 15% | 5 | 3 | 1 | 1 | 3 |
| C5 Engine reuse / drift-reconciliation (no rebuild; v2.0.0 seam fixed) | 12% | 5 | 2 | 2 | 1 | 1 |
| C6 Observability + reporting at every stage | 8% | 5 | 2 | 1 | 2 | 4 |
| **Weighted total** | **100%** | **4.84** | **2.45** | **1.83** | **1.74** | **2.96** |

Arithmetic check (CAP-02): 5(.28)+5(.22)+4(.15)+5(.15)+5(.12)+5(.08) = 1.40+1.10+0.60+0.75+0.60+0.40 = **4.85** (4.84 with rounding). Weights sum 100%.

**Evidence per key cell:**
- CAP-02 C1=5: NIST tiers DERIVED not hand-typed (`stats/power.py` TIER_SPECS: CRITICAL 1522 / STANDARD 753 / LONG_TAIL 200; reid 897/385); Wilson/Clopper-Pearson (`stats/intervals.py`); McNemar + paired-efficiency proof (`required_discordant_pairs`, `paired_vs_independent_ratio`); under-powered cells flagged with named shortfall (`PowerMatrix.verdict`).
- CAP-02 C2=5: seeded reservoir + byte-reproducible run-record + pre-registered slice (`scripts/benchmark_throughput.py`, AX-002; corpus seeds 42/162/172/4242/91237).
- CAP-02 C4=5: non-strippable anti-anonymity caveat (`scoring/detection.py` DesignProvenance / `ReidProvenance.__post_init__`); version-pinned `adversary_id`; held-out leaderboard provenance.
- CAP-02 C5=5: explicitly reconciles the pii-rate-elo v1.3.0/159,891/"labels" drift (confirmed in `datasets/converters/pii_anon_eval.py`) to v2.0.0/575,604/"annotations" while reusing engine/metrics/significance.
- Alt A C3=1: full 575,604-record corpus every run — the runtime problem `benchmark_throughput.py` exists to size. Alt D C5=1: greenfield rebuild contradicts "extend pii-rate-elo, do NOT rebuild"; C1=3: no PII-specific power lattice / anon-vs-pseudo separation.

**Selection: CAP-02 (4.84).** Dominates on academic soundness, reproducibility, anti-gaming, and engine-reuse — the exact axes of the MEMORY soundness bar. Alt D (2.96) is the only structural rival but loses decisively on reuse and PII-specific rigor.

**Alternate switch-points (criteria where a non-preferred candidate scored higher):**
- **C3 Cost (Alt B=5, Alt C=4 > CAP-02=4):** if per-run budget becomes binding, lean harder on the SMOKE preset / shrink the powered sample — but only with the UNDER-POWERED shortfall named (never silently drop to ad-hoc).
- **C2 / C6 (Alt D=4):** if a third party demands a HELM-recognizable surface, wrap CAP-02 reporting in a HELM-style scenario adapter rather than adopting Alt D wholesale.
- **No C1 / C4 / C5 switch-points** — CAP-02 is the unique maximum there; do not trade them for cost.

---

## D. Triangulated implication for v0.1 scope

All three lenses converge: **v0.1 = the five Kano must-haves** (seam reconciliation, per-metric CIs, paired tests, pre-registration/byte-repro manifest, honest verdicts) **+ the Performance backbone** (powered sample, per-stage observability, leaderboard/figures) **+ the two delighters** (honest UNDER-POWERED verdicts, SMOKE preset). This is exactly the Pugh-winning CAP-02 configuration and the JTBD functional spec.

- **Defer to v0.2+:** FULL-corpus opt-in (sample is sufficient and powered for v0.1); live-harness agentic adapter; real-data correlation study (gated on external i2b2/n2c2 DUA — the genuine citation unlock, but out-of-band and not v0.1-blocking).
- **Cut entirely:** certification / paid-eval; static-as-agentic-leakage headline; bespoke scoring configs (Pugh reverse-features).

The must-haves are non-negotiable because all three v1-gating personas treat reproducibility + CIs + paired tests + correct-dataset as the floor; shipping delighters before them would fail it.

---

## Sources
- Internal: `dev-assist-artifacts/01-discovery/personas.md`, `00-pov-stress-test.md`, `workflow-maps.md` (cycle-1; retrieved 2026-06-01)
- Internal: MEMORY `pii-anon-pdlc-complete.md` — academic-soundness bar, NFR-010 self-stamping verdict, frozen 730-cell lattice / v2.0.0 corpus (retrieved 2026-06-01)
- Code: `pii-anon-eval-data/src/pii_anon_datasets/stats/power.py` (TIER_SPECS, REID_TIER_SPECS, McNemar); `stats/intervals.py` (Wilson/Clopper-Pearson); `scripts/benchmark_throughput.py` (seeded run-record, AX-002)
- Code: `pii-rate-elo-pipeline/src/pii_rate_elo_pipeline/datasets/converters/pii_anon_eval.py` (drift: v1.3.0 / num_records=159891 / "labels")
- The reproducibility crisis in ML — https://www.mariushobbhahn.com/2020-03-22-case_for_rep_ML/ (retrieved 2026-06-01)
- Reproducibility in ML-based research: barriers & drivers (AI Magazine 2025) — https://onlinelibrary.wiley.com/doi/10.1002/aaai.70002 (retrieved 2026-06-01)
- Toward a Benchmark Repository … ad-hoc tool evaluation — https://arxiv.org/pdf/2011.14751 (retrieved 2026-06-01)
- Maintaining MTEB: long-term reproducibility of benchmarks — https://arxiv.org/pdf/2506.21182 (retrieved 2026-06-01)

---

✅ **Section 3 (cycle-2 assessment-workflow) — JTBD + Kano + Pugh synthesized.** Forces, categories, and Pugh cells are AGENT_SIMULATED; real-user validation is a Pass-2 follow-up.
