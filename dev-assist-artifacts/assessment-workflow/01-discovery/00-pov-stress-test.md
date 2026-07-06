# Assessment-Workflow Discovery §0 — POV Stress Test (CAP-02)

**Capability**: CAP-02 — second PDLC cycle of `pii-anon-eval-data` (the *assessment workflow*)
**Stage**: assessment-workflow / 01-Discovery · Section 0
**Date**: 2026-06-01
**Method**: 3 independent stress-test critics in parallel — **Critic A (Adjacent-Product Skeptic)** · **Critic B (Persona Realist)** · **Critic C (OSS / Methodology Strategist)** — each citing live web evidence + repo evidence read 2026-06-01.
**Verdict (all three)**: **REFINE** (no SHOWSTOPPER on the *concept*; one SHOWSTOPPER + one CATASTROPHIC on the *as-wired implementation*, addressed as hard preconditions below).

> **Scope note.** This is the POV for **CAP-02** — the *workflow* that runs the existing `pii-rate-elo` tournament against PII-Anon v2.0.0 over a powered/representative/smoke sample with observability + reporting at every stage. It is distinct from, and downstream of, the cycle-1 dataset POV (`../../01-discovery/00-pov-stress-test.md`), which adopted re-identification-resistance + pseudonymization-integrity + multilingual breadth as the *dataset's* value prop under arms-length-neutral governance. CAP-02 inherits those commitments and adds the *assessment* layer.

---

## Original POV (under test)

> "CAP-02 is an **academically-sound, repeatable, reportable assessment workflow** that runs the EXISTING `pii-rate-elo` tournament against the PII-Anon v2.0.0 dataset over a **POWERED REPRESENTATIVE SAMPLE (default)** or the FULL corpus (opt-in) or a SMOKE preset (fast) — with **comprehensive observability + reporting integrated at EVERY stage** (load → sample → run systems → score → rate → report)."

The *spirit* survives: a powered, instrumented, reproducible assessment layer that consumes the mature engine is real, needed, and net-new. But three load-bearing clauses are over-claimed, mis-assigned, or asserted in the present tense as if already earned. All three critics returned **REFINE**.

---

## Critic A — Adjacent-Product Skeptic

**Verdict: REFINE.** The strongest objection lands but on a narrow target: read literally, the *tournament/scoring/significance* layer **is** re-running an adjacent product. `pii-rate-elo/cli.py` already ships `run → load → evaluate → tournament → analyze → export` with Glicko convergence (`tournament/convergence.py`), bootstrap + McNemar + Bonferroni (`analysis/significance.py`), and paper-ready LaTeX (`analysis/paper_metrics.py`). The MEMORY itself concedes this ("pii-rate-elo is MATURE — extend it, do NOT rebuild"). So if the POV were "an academically-sound tournament harness," it would be **REJECT-as-duplicate**. It is not — the locked architecture says eval-data **OWNS** sampling + observability + reporting and pii-rate-elo merely **CONSUMES**. The POV survives only where those three are genuinely absent upstream. They are:

- **Finding A — the powered sampler is a category gap, not a feature gap.** pii-rate-elo has *no concept of statistical power*. Its only subsetting knob is `max_samples`, implemented as naive head-truncation in three places (`cli.py`, `loader.py`, and `converters/pii_anon_eval.py` — verified: `if max_samples is not None and count >= max_samples: break`). That takes the *first N rows in file order* — it cannot hit a per-cell target, cannot stratify by (language × entity_type × domain), and cannot report a shortfall. eval-data's `stats/power.py` is a different species: NIST proportion sizing, frozen risk tiers (CRITICAL 1522 / STANDARD 753 / LONG_TAIL 200, *derived* not hand-typed), a parallel re-id ladder, and `audit_crossing()` → `PowerMatrix` with per-cell `PowerClass` and a SMALL/ADEQUATE/LARGE verdict. None of this is reachable through pii-rate-elo's seam. **This is the load-bearing differentiator and it holds.**
- **Finding B — "observability" is the weaker claim and must be reframed.** pii-rate-elo is *not* unobservable: `cross_dataset.py` has a `progress_hook`, checkpointing with dataset-hash validation, `[i/total]` logging; `cli.py` has Rich spinners. What it lacks is *statistical* observability — per-metric Wilson/Clopper-Pearson CIs (`stats/intervals.py`), the under-powered shortfall named per cell, the non-strippable synthetic-only caveat (`scoring/detection.py` `DesignProvenance`). Reframe as **epistemic instrumentation**, or a skeptic calls it a feature already present.
- **Finding C — the v1.3.0→v2.0.0 seam drift is itself a reason to exist.** `converters/pii_anon_eval.py` self-reports `num_records=159891` and a stale language list (verified) against the live v2.0.0 / 575,604 / `annotations` reality. pii-rate-elo *cannot today read the current corpus correctly* — a positioning **and correctness** gap, not plumbing.

**Five named alternatives (the framing demands them):** (1) **pii-rate-elo itself** — closest adjacent; lacks power/CIs/v2 seam. (2) **eval-data's own `baselines/evaluate.py`** — scores Presidio/regex/LLM in-repo, but per-baseline, no tournament, no powered sample. (3) **HELM / lm-eval-harness** — generic powered/CI harnesses, but no PII span F-beta, no re-id/pseudonymization tracks, no 63-type taxonomy. (4) **PIIBench / RAT-Bench** — score *systems*, but neither exposes a reusable powered sampler over *this* corpus. (5) **StratPPI (arXiv 2406.04291)** — proves stratified powered inference is a known *method*. This last is the fairest hit: **powered stratified subsetting is not novel as a technique.** CAP-02's novelty is the **integration** — a frozen 730-cell lattice bound to this 575k synthetic corpus, feeding a mature Elo engine, with non-strippable provenance.

**Severity:** MAJOR (over-claim risk on the tournament/significance layer + on powered sampling as method; both fixable by re-scoping to *consumed-vs-contributed*).

---

## Critic B — Persona Realist

**Verdict: REFINE.** CAP-02 conflates two value props, and the weaker one is doing the marketing.

- **The "powered SAMPLE (default)" mis-assigns the hero feature.** The personas (`../../01-discovery/personas.md`, `workflow-maps.md`) demand *per-slice power + per-metric CIs* — `PGO-acaddeid-01` is explicit: "publishable per-slice F1/F2 with CIs (infeasible on n≈1.3K real corpora)." For the corpus you **own** (575,604, CC0, local), the academic does not need you to sample *down* — they need each lattice cell to clear its NIST target. Sampling 575k down can only *lose* power in the long-tail cells the full corpus would have covered. So "powered sample" is the wrong hero for the academic; **"powered, per-slice-audited run" is the right one.**
- **Who actually needs the sample is the cost-bearing consumer.** `scripts/benchmark_throughput.py` reveals the true motivation (`CANONICAL_RECORDS = 575604`, full-scan wall-clock extrapolation, "above ~N rows, sample to stay within budget"). A full-corpus *detection* pass is cheap CPU. But the headline novelties — **LLM re-identification scoring** (`reid_required_n`, REID tiers, version-pinned `adversary_id`) — call a paid LLM adversary *per record*. *That* is where 575k is financially impossible. **Bind "sample" to the LLM-cost-bound tracks (re-id, pseudonymization integrity); let detection default to full-corpus-audited.**
- **Per-metric CIs: essential, cheapest credibility you can buy. Keep.** Every HIGH persona's outcome names CIs. The 2026 leaderboard consensus is "read the CI column, not the rank"; overlapping top-of-leaderboard CIs are a named failure mode. For a benchmark whose entire POV is *distrust of single-score vendor claims*, shipping a number without a CI reproduces the exact pathology it attacks.
- **Pre-registration: right instinct, oversold as table-stakes.** The academic-soundness bar lists pre-registration, but **zero of 18 PGO triples ask for it**; web evidence shows it is *advocated-but-not-default* in NLP (2026, contested). What the personas actually surfaced is *reproducibility-from-manifest* (`PGO-researcher-02` "reviewer-reproducible"), which CAP-02 already delivers (frozen `eval_lattice.json` @ 47c3a8f, deterministic bytes). **Demote pre-registration to opt-in rigor for the citation-chasing `P-acad-deid`, not a universal gate** — the `P-tool-builder` CI-gate persona will route around the friction.
- **Reachability passes.** Post-Papers-with-Code shutdown (Jul 2025), HF leaderboards are the canonical discovery surface; a CC0 HF-distributed harness reaches all three HIGH personas at zero cost. WTP ≈ $0; the "payment" is attention + citation, and CIs/per-slice-power are what convert attention into citation.

**Severity:** MAJOR (mis-assigned "sample-as-default" hero + over-weighted pre-registration; fixable by re-casting the *powered per-slice-audited run* as hero and the sample as a cost mode).

---

## Critic C — OSS / Methodology Strategist

**Verdict: REFINE.** The academic-soundness bar is the right *list*; the fatal weakness is a **bifurcated implementation** — two parallel statistics stacks of opposite quality, and the one currently wired into the run path is the fabricated one. Reviewers run the CLI and inspect what produced the numbers.

- **SHOWSTOPPER — the "paired test" and "every metric carries a CI" claims are satisfied by fabricated statistics in the consumer.** `cli.py:242` instantiates `SignificanceTester()` (verified). Its bootstrap does **not resample data** — it adds Gaussian noise to a point estimate: `se = metric_value*(1-metric_value)/100; noise = np.random.normal(0, se)` (verified, ~line 205-208), with `100` a hardcoded constant, not n. Its McNemar "test" never sees a confusion matrix: `n_approx = 100`, `pooled_sd = 0.1`, `z_stat = difference*sqrt(n_approx)/0.05` (verified, ~line 271-281) — a CI-overlap heuristic dressed as a paired test, the exact anti-pattern `eval-data/stats/paired.py` warns against. **A reviewer who diffs the two files rejects the methodology outright.**
- **CATASTROPHIC — reproducibility seam broken.** `converters/pii_anon_eval.py` self-reports `num_records=159891` (verified) and v1.3.0 / CC-BY-4.0 provenance against the v2.0.0 / 575,604 / `annotations` / CC0 artifact. "Pre-registered + reproducible from the manifest" cannot hold while the loader's provenance contradicts the dataset card.
- **What is genuinely rigorous and is being bypassed.** `eval-data/stats/paired.py` is correct (exact two-sided binomial McNemar, Edwards continuity-corrected χ² via `erfc`, a *real* paired bootstrap that resamples **pair indices** with a local seeded `random.Random(seed)`). `stats/power.py` derives tier targets from the NIST/SEMATECH §7.2.4.2 closed form (1522/753/200 re-derived). The `wilson-projected` method tag prevents a design-time projection being read as a measured CI. **The architecture decision is sound; the consumer is just not yet calling the owner's statistics — the seam is the unbuilt part of the capability.**
- **MAJOR — "powered sample meets lattice tiers" needs a named mode.** `PowerMatrix.verdict()` returns LARGE only at ≥99.9% well-powered cells; with 730 cells and CRITICAL=1522 positives/cell, the *representative default* will be honestly labeled SMALL/ADEQUATE, not LARGE. **State which mode (FULL opt-in vs representative) backs the published/citable leaderboard.**
- **MAJOR — RD-convergence under-specified.** `convergence.py` hardcodes `rd_threshold=100.0` undefined (verified, line 49) and presents heuristic round-count extrapolation as guidance (verified: "decreases by roughly 5-10% per round" line 158; `return 100 # Fallback estimate` line 199). Per Glickman, RD is a posterior SD where ±2RD is the 95% interval (cap 350, floor ~30). **Report achieved max-RD with its ±2RD interpretation; drop the extrapolated round predictions from any academic claim.**
- **OBSERVATION — the non-strippable caveat is the strongest-built guarantee.** `ReidProvenance.__post_init__` raises if `caveat` is empty; `as_dict()` always serializes it. External evidence makes this non-optional: synthetic benchmarks demonstrably *overestimate* de-identification performance (SPY, NAACL SRW 2025; Tonic.ai / Security Boulevard 2026). Keep leaning on it.

**Severity:** SHOWSTOPPER + CATASTROPHIC on the *as-wired* state — but this is a **wiring/provenance defect, not a conceptual one.** The methodology *design* survives peer review; the *as-wired implementation* does not, because the POV states in the present tense what the seam will eventually deliver.

---

## What Survives (cross-critic consensus)

1. **The powered, lattice-stratified sampler is unambiguously net-new** (Critic A, Finding A) — a category gap pii-rate-elo's `max_samples` head-truncation cannot fill. This is the load-bearing differentiator.
2. **Per-slice / per-metric confidence intervals are essential and persona-universal** (Critic B) — the cheapest credibility a distrust-of-single-scores benchmark can buy; non-negotiable for all three HIGH personas.
3. **The v1.3.0→v2.0.0 seam reconciliation is net-new *correctness* value** (Critic A Finding C, Critic C CATASTROPHIC) — the sister tool literally cannot read the current corpus today; this is a reason to exist, not plumbing.
4. **The non-strippable synthetic-only / anti-anonymity caveat is the strongest-built guarantee** (Critic C) — enforced by construction (`ReidProvenance.__post_init__`), corroborated as a peer-review precondition by external evidence.
5. **The honest UNDER-POWERED shortfall path** (`PowerClass.UNDER_POWERED`, `shortfall`, `verdict()`) is exactly the behavior `P-acad-deid` needs to defend subgroup gaps in review — surface it as a first-class report artifact, not an internal audit.
6. **The architecture (eval-data OWNS sampling + epistemic instrumentation + reporting; pii-rate-elo CONSUMES) is sound** — all three critics endorse the boundary; the work is wiring + provenance, not new statistics.

## What Does NOT Survive (must be re-scoped or fixed)

- **Any implicit claim that the tournament / scoring / significance layer is new** — it belongs to pii-rate-elo and must be explicitly *credited as consumed* (Critic A).
- **Any claim that powered stratified sampling is novel *as a method*** — it is prior art (StratPPI; "With Little Power"); claim **integration novelty**, not method novelty (Critic A, Finding 5).
- **"Comprehensive observability at every stage" as generic instrumentation** — collides with pii-rate-elo's existing `progress_hook`/checkpoint/Rich logging; reframe as *statistical/epistemic* observability (Critic A, Finding B).
- **"Powered representative SAMPLE (default)" as the universal hero** — re-cast the *powered per-slice-audited run* as hero; the sample is a *cost mode* for the LLM-bound tracks; detection defaults to full-corpus (Critic B).
- **Pre-registration as a universal academic-soundness gate** — demote to opt-in rigor for the one citation-chasing persona; the validated requirement is *manifest-reproducibility* (Critic B).
- **The present-tense framing of the academic-soundness bar** — as wired, the two headline guarantees (paired test, bootstrap CI) are computed by fabricated arithmetic; the POV must split **earned vs committed** (Critic C).

---

## REFINED POV (synthesis)

> "**CAP-02** is a seeded, byte-reproducible assessment **workflow** that **delegates** tournament ranking, Glicko convergence, and paired-significance testing to the mature **pii-rate-elo** engine — it does **not** re-implement them. Its net-new contributions are three: (1) a **NIST-powered, lattice-stratified sampler** over the **v2.0.0 / 575,604-record** corpus (pii-rate-elo's only knob is naive `max_samples` head-truncation, with no concept of power); (2) **per-cell epistemic instrumentation** — Wilson/Clopper-Pearson CIs on every rating/metric, a WELL/UNDER/EMPTY power class with the named shortfall, and a non-strippable synthetic-only / anti-anonymity caveat; and (3) **reconciliation of the drifted dataset seam** (pii-rate-elo is pinned to v1.3.0 / 159,891 / `labels`; the live corpus is v2.0.0 / 575,604 / `annotations` / CC0).
>
> All statistical claims are computed by a **single audited statistics core** (`eval-data/stats`) — the consuming tournament calls it directly, with **no approximated statistics on the run path**. **Detection runs the FULL corpus by default** (it is compute-cheap and the corpus is owned); the **LLM-adversary-bound tracks (re-identification, pseudonymization integrity) default to a POWERED, lattice-stratified SAMPLE** sized to the RRS/re-id tiers, with FULL opt-in and a fast SMOKE preset for CI gating. The **published/citable leaderboard is the FULL-corpus run**; the representative default is a fast pre-screen, always labeled with its power verdict (SMALL/ADEQUATE/LARGE) and named shortfall. **RD convergence is reported as achieved max-RD with its ±2RD (95%) interval**, never as an extrapolated round count. Powered stratified sampling is an established method (StratPPI; 'With Little Power'); the contribution is its **integration** with a frozen 730-cell risk lattice and this specific synthetic corpus — not the statistics themselves. **Pre-registration is offered as opt-in rigor** for first-class-citation use, not a universal gate; the universal commitment is **manifest-reproducibility**."

### What changed and why

| Original clause | Problem (critic) | Refinement |
|---|---|---|
| "academically-sound … assessment workflow" | Reads as a duplicate of pii-rate-elo (A) | Explicit **consumed-vs-contributed** boundary: delegates tournament/convergence/significance; contributes sampler + instrumentation + seam |
| "POWERED REPRESENTATIVE SAMPLE (default)" | Mis-assigned hero; sampling owned-corpus *loses* power (B) | Detection = **FULL by default**; sample = **cost mode** for LLM-bound tracks; **FULL = citable** mode |
| "comprehensive observability at EVERY stage" | Collides with existing progress/checkpoint logging (A) | Reframed as **epistemic instrumentation** (per-cell CIs + power class + non-strippable caveats) |
| "statistically-powered / stated confidence" (implied as-built) | Wired path uses **fabricated** bootstrap + McNemar (C) | Split **earned vs committed**; route the run path to the **single audited `eval-data/stats` core** |
| "repeatable / reproducible" | Loader provenance contradicts the artifact (C) | Reconcile `converters/pii_anon_eval.py` to **v2.0.0 / 575,604 / `annotations` / CC0** |
| (pre-registration in the bar) | Over-weighted vs persona demand (B) | **Opt-in rigor**; universal commitment is **manifest-reproducibility** |
| (RD convergence "reported") | Heuristic round extrapolation presented as derived (C) | Report **achieved max-RD + ±2RD interval**; drop round predictions from claims |
| (powered sampling as novelty) | Prior art — StratPPI / "With Little Power" (A) | Claim **integration novelty**, not method novelty |

### Hard preconditions the refined POV now *commits the project to*

1. **Route the run path to the audited core.** Delete or quarantine `pii-rate-elo/analysis/significance.py` and wire `cli.py` to `eval-data/stats/paired.py` + `intervals.py` (kills the SHOWSTOPPER). *Until then, the "paired test" / "stated confidence" clauses are false.*
2. **Reconcile the dataset seam.** Update `converters/pii_anon_eval.py` to v2.0.0 / 575,604 / `annotations` / CC0 so the manifest reproduces the stated artifact (clears the CATASTROPHIC).
3. **Declare FULL-corpus as the citable mode** and bind the powered SAMPLE to the LLM-adversary tracks (re-id, pseudonymization integrity); make detection default to full-corpus-audited.
4. **Report RD as a CI** (achieved max-RD + ±2RD); drop heuristic round extrapolation from any academic claim.
5. **Surface the power verdict + named shortfall** (`PowerMatrix.verdict()` SMALL/ADEQUATE/LARGE, `PowerClass.UNDER_POWERED.shortfall`) as a first-class report artifact.
6. **Demote pre-registration to opt-in**; keep seeded/byte-reproducible-from-manifest as the universal gate.

---

## Residual Risks

- **R1 (HIGH) — wiring debt is the whole capability.** The refined POV is only *true* once preconditions 1–2 land. Stated in the present tense before then, a single reviewer file-diff sinks the submission (Critic C SHOWSTOPPER/CATASTROPHIC). *Mitigation: track 1–2 as blocking gates; until closed, label all stated-confidence outputs PROVISIONAL.*
- **R2 (MED) — long-tail cells stay under-powered even at FULL corpus.** With CRITICAL=1522 positives/cell across 730 cells, rare entity×language cells may never clear tier even on all 575,604 records. *Mitigation: this is the honest-shortfall path working as designed — report SMALL/ADEQUATE/LARGE + named shortfall; do not over-claim LARGE.*
- **R3 (MED) — "representative" implies population inference the synthetic corpus cannot support.** The lattice is a committed estimability skeleton, not a natural-population sample. *Mitigation: say **"lattice-stratified,"** not "representative of population" (Critic B minor).*
- **R4 (MED) — LLM-adversary cost is the real sampling driver and is version-sensitive.** Re-id/pseudonymization tracks are bounded by a paid, version-pinned `adversary_id`; cost and behavior drift with model version. *Mitigation: pin `adversary_id` in the manifest; treat adversary version as a first-class reproducibility field.*
- **R5 (LOW) — Bonferroni in the consumer is the wrong correction family** for paired-on-same-gold comparisons (over-conservative). *Mitigation: moot once the rigorous paired stack is wired (precondition 1); note it so it is not reintroduced.*
- **R6 (LOW, inherited) — synthetic-only citation ceiling + host-neutrality CoI** carry over from the cycle-1 dataset POV. *Mitigation: the non-strippable caveat + arms-length-neutral governance decision already on record (`../../01-discovery/00-pov-stress-test.md` user decision (b)); CAP-02 inherits, does not relitigate.*
- **R7 (LOW) — preset/persona routing ambiguity.** `P-tool-builder` wants SMOKE/CI; `P-acad-deid` wants FULL power; `P-priv-eng` wants a shortlist sample. *Mitigation: document the default preset per persona in Requirements; one "default" cannot serve all three.*

---

## Methodology & Epistemic Honesty

- The three critics are **agent-simulated** (independent stress-test dispatches) and conducted live web search. Per project framing, agent-simulated research is **NOT a substitute for real users** — this artifact carries `provisional_status: AGENT_SIMULATED`. Real-user validation of this POV is a **Pass-2 follow-up**, not performed here.
- Repo claims in this artifact were **verified by direct read on 2026-06-01**: the fabricated bootstrap (`/100`, Gaussian-noise) and McNemar (`n_approx=100`, `pooled_sd=0.1`) in `pii-rate-elo/analysis/significance.py`; the `SignificanceTester()` instantiation at `cli.py:242`; `num_records=159891` in `converters/pii_anon_eval.py`; `rd_threshold=100.0`, the "5-10% per round" heuristic, and `return 100 # Fallback estimate` in `tournament/convergence.py`; and the existence of the rigorous counterparts (`eval-data/stats/{paired,power,intervals,lattice}.py`, `scoring/detection.py`, `scripts/benchmark_throughput.py`).
- **Sources (retrieved 2026-06-01):** StratPPI — arXiv 2406.04291 (stratified powered inference is a known method); "With Little Power Comes Great Responsibility" — arXiv 2010.06595 (power under-attended in NLP, but prior art); bootstrap-CI / difference-reporting hygiene — arXiv 2205.11134; per-slice CI norm in multilingual eval — arXiv 2509.22612; pre-registration contested/advocated not default — arXiv 2302.10086 + ReproNLP'26 (repronlp.github.io); REFORMS subgroup-size + CI reporting — PMC11092361; 2026 leaderboard "read-the-CI-column" norm — digitalapplied.com LLM-benchmark-methodology-2026; synthetic-overestimation — SPY NAACL SRW 2025 (aclanthology.org/2025.naacl-srw.23/) + Tonic.ai / Security Boulevard 2026; Glicko RD = posterior SD, ±2RD = 95%, cap 350 / floor ~30 — glicko.net/glicko/glicko.pdf + Wikipedia Glicko_rating_system.

**Section gate (assessment-workflow §0):** REFINED POV proposed above; **awaiting user adoption** + decision on whether preconditions 1–2 (run-path rewire + seam reconciliation) are in-scope for CAP-02 or tracked as blocking dependencies.

⏳ **Section 0 DRAFTED (2026-06-01) — pending user sign-off.**
