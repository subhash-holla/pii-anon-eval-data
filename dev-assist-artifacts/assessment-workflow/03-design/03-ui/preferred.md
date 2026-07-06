# CAP-02 — D3 CONVERGE: Preferred Surface (Minimalist-CLI + Info-Dense-Reports)

**Capability**: CAP-02 — academically-sound, repeatable, reportable assessment **workflow** that runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 / CC0 / `annotations`** over a **powered-representative sample (CLI default)** / **full corpus (opt-in, citable)** / **smoke (fast CI)**, with statistical/epistemic observability + reporting at every spine stage `load → sample → run → score → rate → report`.
**Stage**: assessment-workflow / 03-Design · **Diamond 3 (UI / Surface) — CONVERGE**
**Date**: 2026-06-01
**provisional_status**: AGENT_SIMULATED — the surface metaphor is selected by agent-simulated Pugh scoring against the requirements + the D2-locked workflow (Linear-batch, two-CLI, manifest seam, no per-stage consent). The one high-stakes UI commitment inherited from D2 — *"non-interactive by default; the single human decision (preset + run-type) is upfront; no interactive per-stage consent"* (SP-W4) — remains flagged for Pass-2 cognitive-walkthrough with a real single-operator research user.

> **Vocabulary remap.** DC = **Benchmark Component**; FR = Assessment Capability; UC = Evaluation Scenario; NFR = Quality Attribute; AX = binding axiom.

> **Locked architecture this diamond honors.** eval-data **OWNS** sampling + observability + reporting; `pii-rate-elo` **CONSUMES** (extend, do **NOT** rebuild the engine / metrics / convergence). **Two CLI entrypoints (L3):** (a) eval-data `python -m pii_anon_datasets.assessment.sample`; (b) `pii-rate-elo assessment`. The **sample-manifest is the L1 SEAM** (the only cross-process coupling). a11y is **N/A** (library + two CLIs, no web UI) per the brief + cycle-1 precedent. Cycle-1 surface precedent for this diamond = **Minimalist-CLI + Info-Dense-reports**.

---

## 1. The three surface-metaphor proposals (DIVERGE recap)

| Frame | Metaphor | CLI register | Report register | Signature move |
|---|---|---|---|---|
| **A** | **Minimalist-CLI + Info-Dense-Reports** | terse: only the upfront decision is exposed; everything else defaulted | Info-Dense LaTeX/CSV (the deliverable) | **Two registers, one frame** — the CLI shows only preset + run-type + verdict banner; the *report* is the only data-per-pixel surface. Complexity (audited stats, Holm, lattice) stays behind sane defaults. |
| **B** | **Information-Dense (both surfaces)** | dense per-cell stderr tables at every stage | Info-Dense LaTeX/CSV | The operator must *read* dense provenance at every spine boundary; every number labelled, nothing inferred; stdout = manifest path only (pipeable), stderr = the dense draw/stage tables. |
| **C** | **Conversational (transcript-as-deliverable)** | turn-card per stage; gate = verdict-card | Info-Dense LaTeX/CSV (deliberately *not* chat) | Reframes the chained run-record set as a conversation *transcript*; each spine stage = one machine-authored turn-card; the transcript IS the audit deliverable. (Read-only projection — not interactive, to honor SP-W4.) |

All three: ride the **same** two-CLI L1 manifest seam; expose the **same** upfront `--preset / --seed / --run-type / --sample / --config / --out` controls; render the **same** PowerMatrix verdict banner + fail-red gate vocabulary + non-strippable synthetic-only caveat; treat the **LaTeX tabular + CSV** as the primary citable register (FR-047); and emit one run-record per stage (L5/NFR-042) as a first-class audit deliverable (SP-W5).

---

## 2. Pugh comparison (the brief's five named criteria)

**Datum** = Frame A (Minimalist-CLI + Info-Dense-Reports) — the **cycle-1 surface precedent** (named in the locked hybrid) and the conservative baseline the brief names. Scores: **+1** better than datum / **0** equal / **−1** worse.

Weights are the brief's five D3 criteria, normalized to sum 1.00. **Honest-verdict legibility** carries the highest weight: the entire capability exists to emit *honest* power-labelled / tie-gated / caveat-bearing verdicts (G3, AX-003, NFR-047), and a surface that lets a verdict be misread as stronger than it is, is a requirements failure, not a preference. **Reproducibility-from-CLI** is weighted next (AX-002 byte-identity is reachable only if the operator can re-issue the exact command — the CLI *is* the reproduction interface). **Artifact-first reporting** is third (the LaTeX/CSV register is the actual deliverable — FR-047/050). **Researcher ergonomics** and **simplicity** are real but secondary — and, decisively, the D2 winner already locked **non-interactive batch with one upfront decision** (SP-W4), which bounds how much ergonomics any frame can add at the CLI.

| Criterion | Weight | A (Minimalist+Dense) = datum | B (Info-Dense both) | C (Conversational) |
|---|---:|:---:|:---:|:---:|
| **Honest-verdict legibility** (G3 never silently LARGE; AX-003 stated power; NFR-047 closed honesty set; FR-037 smoke suppression) | 0.30 | **0 (datum)** | +1 | 0 |
| **Reproducibility-from-CLI** (AX-002; NFR-030 byte-identity; the command IS the repro surface; seed/run-type echoed) | 0.26 | **0 (datum)** | 0 | −1 |
| **Artifact-first reporting** (FR-047 LaTeX/CSV primary; FR-050 self-verifying; forbidden-token lint) | 0.22 | **0 (datum)** | 0 | 0 |
| **Researcher ergonomics** (low cognitive load on the hot path; progressive disclosure; one upfront decision per SP-W4) | 0.14 | **0 (datum)** | −1 | −1 |
| **Simplicity / reproduce-from-CLI build cost** (fewest render surfaces; reuse-not-rebuild; cycle-1 consistency) | 0.08 | **0 (datum)** | −1 | −1 |
| **Weighted total** | 1.00 | **0.00** | **+0.08** | **−0.40** |

### Score rationale (per criterion)

- **Honest-verdict legibility — A datum; B +1; C 0.** This is **B's genuine strength.** Honest verdicts depend on *labelled, closed-set, non-inferred* presentation: every cell's `power_class ∈ {WELL_POWERED, UNDER_SAMPLED, CORPUS_LIMITED, EMPTY}` against **realized positives**, the corpus `PowerMatrix.verdict() ∈ {SMALL, ADEQUATE, LARGE}` (LARGE only at well-powered fraction ≥ 0.999, ADEQUATE ≥ 0.80 — never silently LARGE, G3/NFR-035), and the full NFR-047 honesty set surfaced inline. **B** maximizes this *at the CLI too* — its dense per-cell stderr draw table (`cell-id · tier · target_n · realized-pos · power_class · shortfall`) makes the under-tier story visible at the boundary, before any inference is computed (AX-003). **A** is equal-to-datum, not worse: it renders the identical closed-set verdict banner + worst-3 named shortfalls at the CLI and the *full* dense honesty bundle in the report — A simply moves the *per-cell exhaustive* table off the terminal hot path into the report/manifest (where NFR-047 actually requires it to live non-strippably). **C** is equal: the verdict-card carries the same closed-set tokens, and C's one real risk (a "conversation" implying a product recommendation) is neutralized because the forbidden-token lint (FR-047, `{SHIP-WITH-CAVEATS, SHIP, DEFER, GO/NO-GO}`) bites the artifact regardless of surface metaphor. So legibility is a wash between A and C; B's edge is real but bounded — see ergonomics.

- **Reproducibility-from-CLI — A datum; B 0; C −1.** The CLI *is* the reproduction interface: NFR-030 byte-identity is only useful if a consumer can re-issue the exact invocation, so the surface must make `{preset, seed, run-type}` legible and the command copy-pasteable. **A** realizes this cleanly — the terse command IS the reproduction unit; the run-type contract line (`run-type=X → rigor=… prereg=… sample_mode=…`, FR-038) and the sealed manifest sha256 are stamped on exit, so "what produced this" is one echoed line. **B** is equal — same command surface; the dense stderr is *additional* output, not a different reproduction contract (and B routes machine output to stdout = manifest path only, which is actually *better* for piping, offsetting the heavier stderr). **C** is **−1**: a transcript interleaves machine turn-cards into the primary surface, so the reproduction question shifts from "re-run this one command" toward "replay this transcript" — a strictly larger artifact to point at, even when (as here) the transcript is a read-only projection of the run-records. The D2 Pugh already penalized C's replay surface (−1 on determinism); the same liability re-appears at the surface layer.

- **Artifact-first reporting — A datum; B 0; C 0.** All three treat the **LaTeX tabular + CSV as the primary citable register** (FR-047) with CI + provenance-hash + synthetic-only caveat inline per cell, tie-greyed ranks (NFR-028), anon/pseudo never merged (AX-004), the self-verifying header embedding pre-reg hash + run id (FR-050), and the forbidden product-verdict tokens linted out. This is a **requirements-fixed** surface — none of the three metaphors changes the deliverable's shape, so all score equal. (C explicitly keeps the report *non*-conversational, which is the correct call and why it does not lose here.)

- **Researcher ergonomics — A datum; B −1; C −1.** With SP-W4 locking *one upfront decision + non-interactive batch*, ergonomics reduces to "how little must the operator read/parse on the hot path." **A** wins by construction: `--help` shows 3 common flags, advanced levers (alpha, span-match-mode, cutoffs) are disclosed behind `--help-advanced` because they live in pre-reg/config, not the hot path. **B** is **−1**: forcing a dense per-cell table to stderr at *every* stage is high cognitive load for the common case (the operator usually wants the verdict banner, not 730 cell rows) — B's density is right for the *report*, over-applied to the *CLI*. **C** is **−1**: a turn-card-per-stage stream is more to read than a terse progress line + banner, and (its inherent risk) the non-conversational power flows (`--block-on-underpower`, `full-corpus` opt-in, run-type profiles) are flags, not chat-discoverable — so C pays the conversational reading cost without the conversational discovery benefit.

- **Simplicity / build cost — A datum; B −1; C −1.** A's render surfaces: a terse progress/banner printer + the Info-Dense report renderer (LaTeX/CSV) + a run-record writer. **B** adds a dense per-stage table renderer with closed-set enum columns and a quiet/`--json-only` mode toggle for CI — real machinery duplicating, on the terminal, what the report already renders. **C** adds a turn-card renderer-per-stage + a transcript serializer (`transcript.jsonl`) as a *view* over the run-records — extra surface for a projection the run-record set already is. The locked architecture says **consume, do not rebuild**; A adds the least new surface around the reused engine/stats/report.

**Pugh verdict: the totals are within noise (A 0.00, B +0.08, C −0.40); the preferred surface is Frame A (Minimalist-CLI + Info-Dense-Reports) — the cycle-1-consistent datum — enriched with B's one winning idea as a named switch-point.** B edges A by +0.08 on a single criterion (honest-verdict legibility) at the cost of −1 on *both* ergonomics and simplicity; that is not a frame win, it is **one good idea (dense, closed-set, machine-readable per-cell power output) attached to the wrong primary surface.** We adopt that idea precisely where it belongs — see SP-U1 (dense per-cell power table available on demand / to stderr / always in the manifest+report, never forced onto the default hot path). The result is A's two-register frame, not a fourth metaphor. C's keepable insight (the run-record trail *is* the audit deliverable) was already absorbed at D2 (SP-W5) and is retained here as the run-record sidecar, not as a conversational primary surface.

---

## 3. Switch-points (named, per the brief)

| # | Switch-point | Frames in tension | Resolution (locked for D4–D5) |
|---|---|---|---|
| **SP-U1** | **Per-cell power detail placement**: dense per-cell table forced to stderr at every stage (B) vs verdict-banner-only on the hot path (A) | A vs B | **ADOPT B's CONTENT, A's PLACEMENT.** The dense, closed-set per-cell power table (`cell-id · tier · target_n · realized-pos · power_class · shortfall`) is **always written to the manifest + report** (where NFR-035/047 require it non-strippably) and is **available at the CLI on demand** via `--show-cells` (and to stderr under `--verbose`), but the **default hot path prints only the verdict banner + worst-3 named shortfalls** (B's density, A's restraint). This captures B's +1 legibility edge without B's −1 ergonomics/simplicity cost. |
| **SP-U2** | **Machine vs human stdout split**: stdout = manifest path only / dense tables to stderr (B) vs human-readable stdout (A) | A vs B | **ADOPT B's STREAM DISCIPLINE.** The sampler CLI writes the **manifest path (and only the path) to stdout** so the one-command chain pipes cleanly (`A --out … | …`); all human-readable progress, the verdict banner, and any dense table go to **stderr**. `--json-only` / `--quiet` (CI) suppress stderr entirely. This is B's genuinely better idea for the seam, kept verbatim. |
| **SP-U3** | **Advanced-flag disclosure**: flat `--help` listing every lever (B-leaning) vs progressive disclosure (A) | A vs B | **PROGRESSIVE DISCLOSURE (A).** `--help` shows the common flags (`--preset / --seed / --run-type / --out` for ENTRY-A; `--sample / --config / --run-type / --out` for ENTRY-B); `--help-advanced` discloses `--alpha`, `--lattice`, `--small-n-cutoff`, `--span-match-mode`, `--seeds`. Advanced levers live in pre-reg/config (the audited contract), not the hot path. |
| **SP-U4** | **`--block-on-underpower`** present (converts default's non-fatal power flag → hard halt) | inherited from D2 SP-W2 | **PRESENT on BOTH CLIs.** On the `powered-representative` default, `UNDER_SAMPLED`/`CORPUS_LIMITED` is a non-fatal honesty flag that **continues** (DF-1/NFR-035/037); `--block-on-underpower` flips that boundary to fail-closed (non-zero exit) for stricter callers. On `full-corpus`/leaderboard, the power gate already exits non-zero on shortfall (NFR-053) — the flag is then a no-op-equivalent (already fatal). |
| **SP-U5** | **No `--from-stage`** resume flag | inherited from D2 SP-W3 | **ABSENT.** There is no resume requirement; NFR-030 makes re-run byte-identical. Recovery = re-invoke the failed CLI stage, which re-consumes the prior sealed artifact. No `--from-stage` flag is surfaced (descoped over-build). |
| **SP-U6** | **Non-interactive default** (no per-stage consent) | inherited from D2 SP-W4 | **NON-INTERACTIVE BY DEFAULT.** Default + smoke run unattended in CI (NFR-019/033/034); the default invocation **is** the onboarding path. No prompts, no `--yes` escape hatch needed. **This is the high-stakes commitment flagged for Pass-2.** |
| **SP-U7** | **Color signalling**: color-coded gates (all frames) vs color-only risk | (all 3 agree) | **TEXT TOKEN + COLOR; `--no-color` honored.** Every gate carries a text token (`FAIL` / `FLAG` / `OK`) so no signal is color-only (a11y-of-text discipline even though web-a11y is N/A); `--no-color` and a non-TTY stdout both drop ANSI. |

---

## 4. The preferred surface — Minimalist-CLI + Info-Dense-Reports (LOCKED)

Two terse CLI entrypoints over the L1 manifest seam; the citable deliverable is an Info-Dense LaTeX/CSV register. The CLI exposes **only the one upfront decision** (preset + run-type) plus the seam/output paths; all statistical complexity stays behind audited defaults. Two registers, one frame: **terse CLI, dense report.**

### 4.1 The two CLI command signatures (L3)

#### ENTRY-A — eval-data sampler (emits the L1 sample-manifest)

```
python -m pii_anon_datasets.assessment.sample \
    [--preset {powered-representative|full-corpus|smoke}]   # DEFAULT: powered-representative (FR-035)
    [--seed INT]                                            # required for non-default reproducibility (NFR-021)
    [--run-type {smoke|dev|leaderboard-submission|filing-grade}]  # designation; stamped into the manifest (FR-038)
    --out PATH                                              # sample-manifest.json (L1 seam, sha256-sealed)
    [--block-on-underpower]                                 # SP-U4: non-fatal power flag -> hard halt
    [--show-cells]                                          # SP-U1: print full per-cell power table to stderr
    [--quiet | --json-only]                                 # SP-U2: stdout=manifest path only; suppress stderr (CI)
    [--no-color]                                            # SP-U7
    [--help | --help-advanced]                              # SP-U3: advanced = --alpha --lattice --small-n-cutoff --seeds
```

- **stdout (SP-U2):** the **manifest path only** (one line), so `--out` can be piped straight into ENTRY-B's `--sample`.
- **stderr:** per-stage progress (`LOAD`, `SAMPLE`); the **PowerMatrix verdict banner** (`VERDICT: SMALL|ADEQUATE|LARGE (well-powered <frac>, N/730 cells)`) + worst-3 named shortfalls in **realized positive counts**; on `--show-cells`, the full dense per-cell table. **Never silently LARGE** (G3/FR-035).
- **Gates:** **GATE-P2** (NFR-041) 5-tuple `{version, record-count, 63-type count, schema-fingerprint, content-hash}` mismatch ⇒ fail-red, non-zero exit, no manifest. **GATE-P3** (NFR-053) run-type-scoped (SP-U4/SP-W2).
- **States:** empty (no corpus / no positives ⇒ fail-red) / drawing (streaming counter) / sealed (prints manifest sha256 + non-strippable caveat to stderr, path to stdout) / halted (red `FAIL` reason line, non-zero exit).
- **Serves:** DC-16/17/18/19 · FR-032/033/034/035/036/037.

#### ENTRY-B — pii-rate-elo assessment (thin orchestrator → eval-data report)

```
pii-rate-elo assessment \
    --sample PATH                                          # sample-manifest.json (L1 seam, required)
    [--config configs/assessment.yaml]                     # pins run_significance_tests:false (P1)
    [--run-type {smoke|dev|leaderboard-submission|filing-grade}]  # rigor bar + prereg gate + backing sample mode (FR-038)
    [--systems ...]                                         # systems under test
    --out DIR/                                             # results/ (LaTeX + CSV + run-records + figures)
    [--block-on-underpower]                                # SP-U4: parity with ENTRY-A
    [--no-color] [--quiet]                                 # SP-U7 / CI
    [--help | --help-advanced]                             # SP-U3: advanced = --span-match-mode --alpha --seeds
```

- **No `--from-stage`** (SP-U5/SP-W3): recovery is re-invoke-the-stage (byte-identical, NFR-030).
- **stdout/stderr:** per-stage progress `PREREG → RUN → SCORE → RATE → REPORT`; the **run-type contract line** stamped at launch (`run-type=X → rigor={full-AX005|suppressed}, prereg={enforced|opt-in|off}, sample_mode={full|sample}`, FR-038) so the operator sees the rigor contract *before* scoring; gate lines in the closed vocabulary — **GATE-P1** (showstopper: `run_significance_tests=false` + `significance.py UNREACHABLE` import-graph guard + fab-regex lint), **GATE-AX5** (prereg, run-type-scoped), **GATE-CONV** (NOT-CONVERGED ⇒ blocking honesty flag, not a crash) — each rendered as a `FAIL` / `FLAG` / `OK` line (NFR-047). Terminal **report pointers** (absolute paths to the LaTeX / CSV / JSON deliverables).
- **Serves:** DC-21/22/23/24/26/27/28/29/30/31 · FR-039/044/047/049/050.

#### The one-command chain (onboarding default path)

```
python -m pii_anon_datasets.assessment.sample --preset powered-representative --seed 7 --out sample-manifest.json \
  && pii-rate-elo assessment --sample sample-manifest.json --config configs/assessment.yaml --out results/
```

Bare `python -m pii_anon_datasets.assessment.sample --out m.json` (no `--preset`) IS onboarding: it draws the `powered-representative` sample and labels it with its PowerMatrix verdict (DF-1/FR-035). `smoke` is the fast-CI on-ramp (every CI/p-value field suppressed, banner reads `NOT STATISTICALLY VALID`, FR-037).

### 4.2 Report layout — Info-Dense register (`results/`)

The deliverable is **artifact-first**: LaTeX `tabular` + CSV are primary; the JSON run-records are the reproduction substrate (necessary-but-insufficient as the *filed* artifact, INT-05/FR-050).

```
results/
├── leaderboard.tex            # PRIMARY citable register (FR-047)
├── leaderboard.csv            # machine register (same content, same gating)
├── report.{tex,pdf}           # full info-dense report (header + tables + figures + honesty bundle)
├── figures/                   # AUPRC / Fβ-asymmetry / per-language-recall (matplotlib, lazy-imported)
├── run-records/               # 6 chained records {load,sample,run,score,rate,report}, shared run_id (L5/NFR-042)
│   └── run-<run_id>.jsonl     # one record per spine stage (audit deliverable, SP-W5)
├── prereg.json                # pre-registration {hash, commit_sha} (FR-044), embedded into the report header
└── manifest.copy.json         # the consumed L1 manifest (provenance closure)
```

**Self-verifying report header (FR-050):** embeds `pre_registration.hash` + `commit_sha` + `run_id` so any consumer reproduces the result from the manifest end-to-end, plus the run-lineage count, the `run-type` contract triple, the seed + RNG fingerprint, and the corpus `PowerMatrix.verdict()`.

**Leaderboard `tabular` layout (the Info-Dense core):**

| column | content | requirement |
|---|---|---|
| system | system id + `contamination_status ∈ {disclosed-unseen, disclosed-trained-on-corpus, undisclosed}` (`unknown` ⇒ flagged) | NFR-048 |
| family | **anon** \| **pseudo** rendered as **separate metric families — never merged** into one "redaction quality" number | AX-004 / FR-047 |
| metric (per family) | recall / precision / Fβ / AUPRC, each **with its CI** + the `method ∈ {wilson, clopper-pearson, paired-bootstrap}` named inline + `scope: conditional-on-this-sample` | FR-040 / NFR-024 |
| rank | **gated by the paired-test verdict** — pairs not significant after **Holm–Bonferroni** (family size stated) are **greyed / grouped as statistical ties** (no rank out-runs the paired evidence) | FR-041 / FR-047 / NFR-028 |
| power | per-cell `power_class` roll-up + corpus verdict; under-tier carries **named shortfall in realized positives** | FR-033 / NFR-035/037 |
| caveat | the **non-strippable synthetic-only / anti-anonymity caveat**, inline per metric (cannot be stripped to a removable footer) | AX-001/003 / NFR-044 |

**Honesty bundle (NFR-047 closed set — rendered inline, non-strippably; stripping any one invalidates the artifact):**
`RD-NOT-CONVERGED` (achieved max-RD ± 2RD + Glicko rounds + stopping rule — never an extrapolated round count) · per-cell `UNDER-POWERED / UNDER-SAMPLED / CORPUS-LIMITED` · `contamination-uncontrolled` (per non-`disclosed-unseen` system) · `rank-volatility: UNMEASURED` (if single-seed; else Kendall-τ over ≥3 seeds) · **worst-language recall** = `argmin` over languages in the coverage envelope **with the language label** · **low-resource recall** = recall over the committed set of languages with realized positives `< 200` · `correlation-study: named-and-pending` · `NOT_ASSESSED` for critical types outside the coverage envelope.

**Forbidden-token lint (FR-047 / C7):** a scan of the LaTeX + CSV registers finds **none** of `{"SHIP-WITH-CAVEATS", "SHIP", "DEFER", "GO/NO-GO"}` (extensible). A register containing any listed token ⇒ invalid. Academic vocabulary only — no product-verdict language.

**Smoke register (FR-037):** every CI field and every p-value field is **suppressed / null**; the artifact carries `not_statistically_valid: true`; the banner reads `NOT STATISTICALLY VALID`. A smoke result can neither be mistaken for, nor surface numbers that look like, a powered result.

### 4.3 Interaction patterns

- **Primary:** the one-command chain (ENTRY-A `--out` → ENTRY-B `--sample`); fully unattended in CI (SP-U6).
- **Error:** fail-closed, non-zero exit, single red `FAIL` reason line; recovery = re-invoke the stage (byte-identical, NFR-030) — no resume (SP-U5).
- **Help / onboarding:** the default invocation IS onboarding; `--help` minimal, `--help-advanced` discloses the audited levers (SP-U3).
- **Run-type surface:** echoed once as a stamped contract line before scoring (FR-038), and re-stamped into every run-record and the report header.

### 4.4 Discoverability & accessibility

- **Discoverability: medium-high.** The 3 common flags + verdict banner are docs-free findable; the one-command chain is documented inline; run-type profiles + `--block-on-underpower` need `--help`. Weakness (carried): advanced levers (alpha, span-match-mode, cutoffs) hidden — acceptable because they live in pre-reg/config (the audited contract), not the hot path.
- **Accessibility: N/A (text/two-CLI, no web UI).** But: gates carry a text token (`FAIL`/`FLAG`/`OK`) so no signal is color-only; `--no-color` and non-TTY both drop ANSI (SP-U7); run-records + transcript-equivalent are plain JSON/JSONL (screen-reader-trivial by default).

---

## 5. Axiom considerations (surface layer)

- **AX-001 (synthetic-only):** the non-strippable caveat is printed at manifest-seal (stderr) and rendered inline-per-metric in every register (NFR-044) — never a removable footer.
- **AX-002 (deterministic/seeded/byte-reproducible):** the CLI **is** the reproduction interface — the terse copy-pasteable command + the echoed `{seed, run-type, manifest sha256}` make re-run byte-identical (NFR-030); SP-U2's machine-stdout keeps the seam scriptable.
- **AX-003 (stated power):** the PowerMatrix verdict banner is printed **before any inference is computed** (Stage-1 output) and re-rendered in the report header; never silently LARGE (G3).
- **AX-004 (separate families):** the leaderboard renders **anon** and **pseudo** as separate metric-family columns — the surface contains no merge affordance.
- **AX-005 (pre-registered/reproducible):** the run-type contract line surfaces the rigor bar **before** scoring (FR-038); the self-verifying header embeds the pre-reg hash + run id (FR-050); smoke/dev suppress inferential output rather than emit an un-rigorous number (FR-037).

---

## 6. Constraints on downstream diamonds

- **D4 (System):** a **stage sequencer** emits per-stage stderr progress + one run-record per boundary (L5); a **banner renderer** reads the PowerMatrix verdict off the manifest (no recompute); **closed-set enum tokens** for `power_class` / verdict / honesty-flags / `contamination_status` are the render contract; `--block-on-underpower` toggles GATE-P3 fatality (SP-U4); `--show-cells`/`--verbose` gate the dense per-cell table (SP-U1); stdout = manifest path only on ENTRY-A (SP-U2); **pure-stdlib CLI cores + lazy heavy-dep guards** (numpy/matplotlib lazy-imported **only** in figure code, NFR-050).
- **D5 (Architecture):** the CLI is a **thin adapter** over `pii_anon_datasets.assessment` (sampler + report); the **report renderer (LaTeX/CSV) owns the Info-Dense register**; the **sample-manifest schema is the seam contract** (L1, the only cross-process coupling); the forbidden-token + honesty-set + tie-gating linters are report-side functions (eval-data owns reporting, L2).

---

## 7. What feeds the next diamond (D4 System)

D4 inherits a **two-register surface**: a terse non-interactive two-CLI front (one upfront decision: preset + run-type) and an Info-Dense LaTeX/CSV deliverable. The load-bearing UI affordances are: the **PowerMatrix verdict banner** (closed-set, never silently LARGE), the **fail-red gate vocabulary** (P1 showstopper / P2 / P3 / prereg / NOT-CONVERGED as `FAIL`/`FLAG`/`OK`), the **run-type contract line** (FR-038), the **machine-stdout seam** (SP-U2), and the **inline non-strippable honesty bundle** (NFR-047). The two named UI switch-points carried forward are **`--block-on-underpower` present** (SP-U4) and **no `--from-stage`** (SP-U5). `provisional_status: AGENT_SIMULATED`; the **non-interactive-default** commitment (SP-U6) is flagged for Pass-2 real-operator cognitive walkthrough.

---

✅ **D3 CONVERGE complete (2026-06-01).** Pugh-compared 3 surface metaphors (A Minimalist-CLI+Info-Dense-Reports / B Info-Dense-both / C Conversational) against the brief's five criteria; **Frame A preferred (datum; totals within noise A 0.00 / B +0.08 / C −0.40)** — cycle-1-consistent and a clean fit to the D2-locked non-interactive two-CLI batch. Enriched with **B's one winning idea** (dense, closed-set, machine-readable per-cell power output) as named switch-points: per-cell detail placed in manifest+report + on-demand at the CLI, not forced onto the hot path (SP-U1), and machine-stdout stream discipline at the seam (SP-U2). Seven switch-points named + resolved (SP-U1…U7). Concrete **two CLI signatures + Info-Dense report layout** written. High-stakes commitment flagged for Pass-2: **non-interactive default, no per-stage consent** (SP-U6). `provisional_status: AGENT_SIMULATED`. Ready for D4 (System).
