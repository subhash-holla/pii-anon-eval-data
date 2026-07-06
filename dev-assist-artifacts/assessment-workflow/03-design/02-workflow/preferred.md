# CAP-02 — D2 CONVERGE: Preferred Workflow archetype

**Capability**: CAP-02 — academically-sound, repeatable, reportable assessment **workflow** that runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 / CC0 / `annotations`** over a **powered-representative sample (CLI default)** / **full corpus (opt-in, citable)** / **smoke (fast CI)**, with statistical/epistemic observability + reporting at every spine stage `load → sample → run → score → rate → report`.
**Stage**: assessment-workflow / 03-Design · **Diamond 2 (Workflow) — CONVERGE**
**Date**: 2026-06-01
**provisional_status**: AGENT_SIMULATED — the workflow archetype is selected by agent-simulated Pugh scoring against the requirements + the verified code seams (read at HEAD 2026-06-01). The one high-stakes commitment — *"every assessment run is a fail-closed linear batch across the two-CLI manifest seam, with no interactive per-stage consent"* — is flagged for Pass-2 cognitive-walkthrough validation with a real single-operator research user.

> **Vocabulary remap.** DC = **Benchmark Component**; FR = Assessment Capability; UC = Evaluation Scenario; NFR = Quality Attribute; AX = binding axiom.

> **Locked architecture this diamond honors.** eval-data **OWNS** sampling + observability + reporting; `pii-rate-elo` **CONSUMES** (extend, do **NOT** rebuild the engine / metrics / convergence). Two CLI entrypoints (L3): (a) eval-data `python -m pii_anon_datasets.assessment.sample --preset … --seed … --out sample-manifest.json`; (b) `pii-rate-elo assessment --sample sample-manifest.json --config configs/assessment.yaml --out results/`. The **sample-manifest is the L1 SEAM** (the only cross-process coupling). Cycle-1 precedent for this diamond = **Linear-batch-data-prep**.

---

## 1. The three archetype proposals (DIVERGE recap)

| Frame | Archetype | Surface shape | Navigation | Signature move |
|---|---|---|---|---|
| **A** | **Linear-batch-pipeline** | non-interactive batch (upfront choices only) | linear, checkpoint-resume | Spine ordering IS the control flow; each stage boundary is a durable hashed checkpoint with a fail-closed gate; observability + governance are a **sidecar**, not stages |
| **B** | **Event-Driven** | event/stage status surface + gate-verdict cards | spoke-and-hub (run-record bus = hub) | The artifact-on-disk **is the event**; gates are **event-consumers** (`proceed`/`halt`) not inline steps; resume = re-fire last unconsumed event |
| **C** | **Agent-Conversation** | conversation (transcript = audit trail) | conversational, turn-per-stage | Each spine stage = one operator turn; each gate = a **blocking card** the operator must clear; transcript IS the provenance deliverable |

All three: map onto the same `load→…→report` spine + the same two-CLI L1 manifest seam; emit one run-record per stage (L5); carry the non-strippable synthetic-only caveat; honor P1/P2/P3 as gates and the no-regression rails.

---

## 2. Pugh comparison (the brief's five named criteria)

**Datum** = Frame A (Linear-batch) — the **cycle-1 precedent** (`Linear-batch-data-prep` in the locked hybrid) and the conservative baseline the brief names. Scores: **+1** better than datum / **0** equal / **−1** worse.

Weights are the brief's five criteria, normalized to sum 1.00. **Fit to the linear spine** and **determinism/reproducibility** carry the highest weight: the capability *is literally* the `load→…→report` pipeline (D1 chose the Workflow-arc lens for exactly this reason), and AX-002 byte-reproducibility (NFR-030/021/038/042) is a binding axiom, not a nicety. **Observability-gate placement** is weighted next because the three precondition gates (P1/P2/P3) are the spine's load-bearing integrity surfaces. Simplicity and resume/failure handling are real but secondary (and, as §3 shows, the requirements set contains **no resume requirement** — only an honest-halt + byte-identical-re-run contract).

| Criterion | Weight | A (Linear) = datum | B (Event-Driven) | C (Agent-Conversation) |
|---|---:|:---:|:---:|:---:|
| **Fit to the linear spine** (the capability IS `load→…→report`) | 0.28 | **0 (datum)** | −1 | −1 |
| **Determinism / reproducibility** (AX-002; NFR-030/021/038/042; same-seed byte-identity) | 0.24 | **0 (datum)** | 0 | −1 |
| **Observability-gate placement** (P1/P2/P3 fire as CI-blocking boundary predicates; NFR-019 "green requires no human") | 0.22 | **0 (datum)** | +1 | −1 |
| **Simplicity** (fewest moving parts; reuse-not-rebuild; cycle-1 consistency) | 0.16 | **0 (datum)** | −1 | −1 |
| **Resume / failure handling** (halt-closed + re-run from sealed artifact; NFR-030 makes re-run byte-identical) | 0.10 | **0 (datum)** | +1 | 0 |
| **Weighted total** | 1.00 | **0.00** | **−0.10** | **−0.84** |

### Score rationale (per criterion)

- **Fit to the linear spine — A datum; B −1; C −1.** The capability is a six-stage pipeline whose ordering is fixed and total; D1 already locked the **Workflow-arc** lens *because* "the capability IS the pipeline" and the DC set is "already the spine." A Linear-batch archetype is a 1:1 structural match — stage *N* consumes stage *N−1*'s sealed artifact, no more. **B** re-expresses the same fixed total order as a pub/sub event graph: this is *expressive* but adds an event vocabulary (`*.emitted/consumed`, a bus, handler subscriptions) for a control flow that never actually branches or fans out at runtime except at the single manifest seam — accidental complexity over a linear reality. **C** actively fights the spine: turning a fixed pipeline into a turn-by-turn conversation imposes a navigation model (operator turns) the pipeline does not need; the spine has exactly one human decision point (preset + run-type, upfront — DF-1/NFR-033), not six.

- **Determinism / reproducibility — A datum; B 0; C −1.** AX-002 + NFR-030 make manifest + run byte-reproducible from `{seed, RNG fingerprint, sampler version}`; NFR-021 pins seeded LOCAL RNG; NFR-042 emits one provenance-complete record per stage under a shared run id. **A** realizes this cleanly: each checkpoint is a pure function of the prior sealed artifact + seed, so re-running from any boundary is byte-identical by construction — determinism is a property of the linear data dependency. **B** is equal: idempotent content-hash-keyed handlers also reproduce byte-identically, but the event bus adds no reproducibility A lacks (the manifest seam already carries the seed + fingerprint). **C** is **−1**: a conversation interleaves operator turns with computation, so reproducibility now depends on faithfully replaying a *transcript* (operator decisions + tool returns), a strictly larger and more fragile replay surface than "re-run the batch with the recorded seed." The conversation adds a human-decision dimension to a contract that NFR-030 defines as a pure function of the manifest.

- **Observability-gate placement — A datum; B +1; C −1.** This is **B's genuine strength and C's fatal mismatch.** The three gates are, by requirement, **CI-blocking machine predicates**: NFR-019 says the P1 quarantine gate is an "import-graph / call-graph static check … these two CI predicates ARE the gate (green requires no human)"; NFR-041 (P2) is a regression test that "fails red"; NFR-053 (P3) is `validate.py --lattice` exiting non-zero on shortfall. **B** models gates as first-class event-consumers that inspect a run-record and emit `proceed`/`halt(reason)` — a slightly cleaner separation of "gate logic" from "stage logic," and it makes the non-fatal `UNDER_SAMPLED` path a natural event the report consumer must render. **A** is equal-to-datum, not worse: it places the identical predicates as fail-closed boundary checks between stages (P1 import-graph guard, P2 5-tuple, P3 power gate) — same predicates, same fail-closed semantics, just inlined at the boundary rather than dispatched on a bus. **C** is **−1**: it renders gates as *interactive operator cards* requiring acknowledgement (`{proceed-with-caveat | re-sample | abort | lock}`). That directly contradicts NFR-019's "green requires no human" and NFR-033's table-driven CI gate — the gates are designed to be human-free and CI-runnable (the default + smoke presets must run unattended in CI), so a human-in-the-loop gate model is a requirements mismatch, not a preference.

- **Simplicity — A datum; B −1; C −1.** A's parts: a stage sequencer + hashed-artifact checkpoints + a run-record sidecar writer + fail-closed boundary predicates. **B** adds an event/artifact contract per boundary, a subscription/dispatch mechanism, a `PENDING→…→CONSUMED|HALTED` state machine, and idempotency keys — real machinery for a flow with one true branch point. **C** adds a card-renderer-per-DC, interactive gate affordances, a transcript/audit model, and `--yes`/`--block-on-underpower` non-interactive escape hatches *just to recover CI-runnability* — i.e. C must re-introduce the batch path to satisfy CI, which is evidence the conversation is the wrong primary surface. The locked architecture says **consume, do not rebuild**; A adds the least new orchestration around the reused engine/stats.

- **Resume / failure handling — A datum; B +1; C 0.** **Decisive finding: the FR/NFR set contains NO resume / checkpoint / `--from-stage` requirement** (grep over both requirement docs returns zero hits). What the requirements *do* mandate is honest-halt (gates fail-closed / "rejected, not merely warned" — NFR-026) plus **byte-identical re-run from the sealed manifest** (NFR-030). So the criterion reduces to: halt cleanly, then re-run reproducibly. **B** earns **+1** because "re-fire the last EMITTED-but-unconsumed event" is the lightest, most precise resume mapping, and it falls out of the event model for free. **A** is the datum: it halts fail-closed at the failing boundary and re-runs from the prior sealed artifact (byte-identical per NFR-030) — fully adequate, and A's frame *also* proposes a `--from-stage` resume, but that is **over-build beyond requirements** (noted as a switch-point, SP-W3, to be trimmed). **C** is equal: transcript-replay-to-last-good-card is a heavier resume surface than B's event re-fire but no worse than A's re-run.

**Pugh verdict: Frame A (Linear-batch-pipeline) is preferred (datum; the only non-negative total).** It is the cycle-1-consistent choice and a 1:1 structural match to the spine. It is **not** unanimous — **B wins observability-gate placement (+1) and resume (+1)** — so the preferred workflow **is Linear-batch enriched with B's two best ideas as named switch-points**: (i) gates expressed as *named, inspectable boundary predicates over the run-record* (B's "gate consumer" discipline, realized inline — no bus), and (ii) the *honest-halt + re-run-from-sealed-artifact* resume model (B's event re-fire, realized as "re-run from the last sealed checkpoint" — no `--from-stage` engine). The result is A's spine, not a fourth archetype.

---

## 3. Switch-points (named, per the brief)

| # | Switch-point | Frames in tension | Resolution (locked for D3–D5) |
|---|---|---|---|
| **SP-W1** | **Gate mechanism**: inline fail-closed boundary checks (A) vs gate-as-event-consumer on a bus (B) | A vs B | **ADOPT B's DISCIPLINE, A's MECHANISM.** Each gate (P1/P2/P3 + prereg + NOT-CONVERGED) is a **named predicate over the stage's run-record** that returns `proceed` / `halt(reason)` — B's clean gate/stage separation — but evaluated **inline at the boundary**, not dispatched on an event bus (no bus to build; the manifest-on-disk is the only seam). This keeps NFR-019's "green requires no human" CI-predicate semantics while gaining B's testability (gates unit-testable in isolation from stages). |
| **SP-W2** | **Under-powered path**: hard halt vs non-fatal flag that the report must render | (all 3 agree it is non-fatal) | **NON-FATAL FLAG, carried on the manifest → report.** Per DF-1 + NFR-035/037, `UNDER_SAMPLED` / `CORPUS_LIMITED` on the **default** preset **continues** (the study's "strongest delight" — the honest under-powered run) and surfaces as a blocking *honesty flag* (NFR-047), never a crash and never a silent `LARGE`. On the **`full` / leaderboard** preset, NFR-053's power gate **exits non-zero** on shortfall (fail-closed). The gate's behavior is thus **run-type-scoped** (DC-20). |
| **SP-W3** | **Resume model**: stateful `--from-stage` checkpoint executor (A's frame) vs re-run-from-sealed-artifact (B's re-fire) | A vs B | **TRIM TO RE-RUN-FROM-SEALED-ARTIFACT.** There is **no resume requirement** in the FR/NFR set; NFR-030 guarantees re-run byte-identity. So failure → fail-closed halt → re-invoke the failed CLI stage, which re-consumes the prior **sealed** artifact (the manifest, or the prior run-record's referenced inputs) and reproduces byte-identically. A's `--from-stage` executor is **descoped as over-build** (revisitable in D4 only if a real operator in Pass-2 demands sub-run resume of the long `run` stage). |
| **SP-W4** | **Primary surface**: batch CLI (A) vs interactive conversation with per-stage consent (C) | A vs C | **BATCH CLI; NO PER-STAGE CONSENT.** NFR-019/033/034 require the default + smoke presets to run **unattended in CI**; an operator-consent-per-stage model (C) is a requirements mismatch and forces C to re-add `--yes` escape hatches. The single human decision (preset + run-type) is **upfront** (DC-20, the L3 surface). C's one keepable insight — *the run-record trail is itself the audit deliverable* — is absorbed as SP-W5. **This is the high-stakes commitment flagged for Pass-2.** |
| **SP-W5** | **Audit-trail framing**: run-records as a passive sidecar (A) vs the transcript IS the deliverable (C) | A vs C | **SIDECAR THAT IS ALSO A FIRST-CLASS DELIVERABLE.** A's sidecar framing (observability writes at every boundary, never gates flow) is kept, but C's insight is adopted: the **chained run-record set (one per stage, shared run id — NFR-042) is an explicit audit artifact**, not debug output — it is what makes the run reproducible-from-manifest end-to-end and feeds the self-verifying report (NFR-047). |
| **SP-W6** | **Pre-registration position**: structural Stage-2 (upstream of scoring) in all three | (all 3 agree) | **STRUCTURAL: PREREG IS UPSTREAM OF THE FIRST SCORE.** The linear order *physically enforces* "pre-register BEFORE scoring" (FR-044; AX-005 element 4) — DC-24 sits between SAMPLE and the DC-22 score stage. This is the one place all three frames agree; the linear archetype makes it a property of stage order, not a convention. Enforcement strength is run-type-scoped (NFR-033). |

---

## 4. The preferred workflow — Linear-batch-pipeline (LOCKED)

A **resumable-by-re-run batch pipeline with fail-closed boundary gates**, split across the two L3 CLI entrypoints at the L1 manifest seam. Six spine stages; two cross-cutting sidecars (observability, governance) that write at every boundary and **never gate flow**.

```
                ┌─ run-type (DC-20) selects rigor bar + sample mode + prereg gate ─┐
                ▼  (the ONE upfront human decision; everything after is unattended)  │
[ENTRY-A: eval-data CLI]  python -m pii_anon_datasets.assessment.sample --preset --seed --out
                                                                                     │
  STAGE 0  LOAD ──── DC-16 reconcile v2.0.0 + regression-contract 5-tuple            │
       │             ╠═ GATE-P2 (NFR-041): {version,count,63-type,fingerprint,hash}  │
       │             ║   mismatch ⇒ fail RED, non-zero exit, no downstream           │
       ▼                                                                             │
  STAGE 1  SAMPLE ── DC-17 seeded lattice sampler → DC-18 PowerMatrix → DC-19 manifest│
       │             ╠═ GATE-P3 (NFR-053): power gate — run-type-scoped (SP-W2):      │
       │             ║   default ⇒ UNDER_SAMPLED/CORPUS_LIMITED continue as FLAG;     │
       │             ║   full/leaderboard ⇒ shortfall exits non-zero                  │
       │             ╚═> emits sample-manifest.json  [L1 SEAM, sha256-sealed,         │
       │                 non-strippable caveat, seed + RNG fingerprint]              │
       · · · · · · · · · · · · seam boundary (process split) · · · · · · · · · · · · ·
[ENTRY-B: pii-rate-elo CLI]  pii-rate-elo assessment --sample manifest.json --config --out
       │
  STAGE 2  PREREG ── DC-24 pre-register BEFORE first score (git-anchored, hash-chained)
       │             ╠═ GATE-AX5 (NFR-031, run-type-scoped): leaderboard/filing ⇒
       │             ║   prereg MUST exist + commit-on-remote; else opt-in
       ▼
  STAGE 3  RUN ───── DC-21 thin orchestrator: PIIRateEloEngine + ConvergenceChecker (Glicko RD)
       │             ╠═ GATE-P1 (NFR-019/020) [SHOWSTOPPER]: run_significance_tests:false
       │             ║   + import-graph guard (significance.py UNREACHABLE) + fab-regex lint
       ▼
  STAGE 4  SCORE ─── DC-22 audited CIs (Wilson/Clopper-Pearson) · DC-23 family-separation
       │                 (AX-004) + contamination + seed-variance scope
       ▼
  STAGE 5  RATE ──── DC-22 paired McNemar/bootstrap + Holm-Bonferroni; convergence verdict
       │             ╠═ GATE-CONV (NFR-029): NOT-CONVERGED ⇒ blocking honesty flag (not crash)
       ▼
  STAGE 6  REPORT ── DC-26 tie-gated leaderboard → DC-27 operating-point → DC-28 honesty
       │                 bundle + self-verifying header → DC-30 crosswalk → DC-31 DOI/citation
       ▼
  [DELIVERABLE: results/]  +  per-page governance block (DC-29)

  SIDECARS (write at every boundary; NEVER gate flow):
    • Observability (L5/DC-25): one run-record per stage {load,sample,run,score,rate,report},
      shared run_id, each {dataset_version, record_count, schema_fingerprint, seed, stage,
      code_commit} + toolchain; file-level provenance on every artifact (NFR-042/043).
      ↳ SP-W5: this chained record set IS a first-class audit deliverable, not debug output.
    • Governance (DC-29): submission-provenance + recusal/neutrality block, stamped per report page.

  GATE SEMANTICS (SP-W1): every gate = a NAMED PREDICATE over the stage run-record returning
    proceed / halt(reason), evaluated INLINE at the boundary (no event bus). All gates are
    CI-blocking machine predicates (NFR-019 "green requires no human"). Fail-closed by default;
    the power gate is the one run-type-scoped non-fatal-on-default exception (SP-W2).

  FAILURE / RESUME (SP-W3): a gate halt is fail-closed (non-zero exit, downstream does not run).
    Recovery = re-invoke the failed CLI stage; it re-consumes the prior SEALED artifact and
    reproduces byte-identically (NFR-030). No stateful --from-stage executor (descoped over-build).

  PREREG ORDERING (SP-W6): STAGE 2 is structurally upstream of STAGE 4/5 — the linear order
    PHYSICALLY enforces "pre-register before scoring" (AX-005 element 4), not by convention.
```

### Stage → DC → trigger → gate → run-record mapping

| Stage | DC(s) | Entry | Trigger | Boundary gate (predicate) | Run-record (L5) |
|---|---|---|---|---|---|
| 0 LOAD | DC-16 | A | sample CLI invoked | **GATE-P2** 5-tuple (NFR-041), fail-red | `load` |
| 1 SAMPLE | DC-17/18/19 | A | LOAD gate green | **GATE-P3** power (NFR-053), run-type-scoped (SP-W2) | `sample` |
| — (seam) | DC-19 | A→B | manifest sealed (sha256) | manifest non-strippable-caveat invariant (NFR-044) | (carried on `sample`) |
| 2 PREREG | DC-24 | B | manifest loaded | **GATE-AX5** prereg (NFR-031), run-type-scoped | (chained into `run`) |
| 3 RUN | DC-21 | B | prereg ok | **GATE-P1** quarantine (NFR-019/020) **[SHOWSTOPPER]** | `run` |
| 4 SCORE | DC-22/23 | B | outcomes handed off | family-separation static check (NFR-045/055) | `score` |
| 5 RATE | DC-22 | B | scores computed | **GATE-CONV** NOT-CONVERGED honesty flag (NFR-029) | `rate` |
| 6 REPORT | DC-26/27/28/29/30/31 | B | rate complete | report linter: CIs+ties+honesty-set+self-verify (NFR-028/047) | `report` |

---

## 5. Cross-workflow concerns

- **Onboarding / default path.** The default invocation (no preset ⇒ `powered-representative`, DF-1) runs the full spine **unattended** to a power-labelled deliverable — the linear default *is* the onboarding path. The **one-command chain** wires ENTRY-A → ENTRY-B by feeding `--out sample-manifest.json` into `--sample`. `smoke` is the fast-CI on-ramp: it exercises all six stages with CI + p-value fields **suppressed** (NFR-034), so it can never look inferential.

- **Error / recovery flow.** Three halt classes: **(1) hard halt** — P1 fabrication-path reachable (GATE-P1) or P2 contract mismatch (GATE-P2) ⇒ non-zero exit, nothing downstream runs; **(2) run-type-scoped halt** — P3 power shortfall on `full`/leaderboard (NFR-053); **(3) non-fatal flag** — `UNDER_SAMPLED` / `CORPUS_LIMITED` on default, `NOT-CONVERGED`, `contamination-uncontrolled` ⇒ carried on the artifact, the report MUST render it (NFR-047). **Recovery is re-run, not resume** (SP-W3): re-invoke the failed stage; NFR-030 guarantees byte-identical reproduction from the sealed manifest.

- **Multi-DC interactions.** The **manifest (DC-19) is the only cross-process coupling** (L1). The **run-type selector (DC-20) fans out** to GATE-P3 strength (DC-18), GATE-AX5 strength (DC-24), and the rigor bar (DC-22) — one mechanism, three scoped behaviors (NFR-033). The **observability sidecar (DC-25) threads the shared `run_id`** through all six stages and surfaces the DC-16 5-tuple as run-record fields. **Report DCs (26/27/28) fan in on the single audited-stats output** so leaderboard, operating-point, and honesty bundle share one statistical source of truth (no recompute, no AX-004 merge).

---

## 6. Axiom considerations

- **AX-001 (synthetic-only):** the non-strippable caveat is seeded at DC-19 (manifest) and carried by `DesignProvenance` through every downstream stage to DC-28/31. The linear data dependency guarantees it cannot be dropped between stages (NFR-044).
- **AX-002 (deterministic/seeded/byte-reproducible):** each stage boundary is a sealed, hashed checkpoint; re-running from any boundary re-derives byte-identical artifacts (seed + RNG fingerprint pinned in the manifest and every run-record — NFR-030/021/042).
- **AX-003 (stated power):** DC-18's PowerMatrix verdict is a Stage-1 gate output, surfaced **before any inference is computed** (GATE-P3); re-asserted as a blocking honesty flag at DC-28.
- **AX-004 (separate families):** DC-23 family-separation is enforced at SCORE (static check, NFR-045/055) **before** DC-26 renders — the linear path contains no merge point.
- **AX-005 (pre-registered/reproducible, 6 elements + scope):** the linear order **physically enforces** prereg (Stage 2) upstream of scoring (Stages 4–5) — DC-24 is structurally before DC-22 (SP-W6). Run-type (DC-20) sets the gate strength at the PREREG and power boundaries (NFR-033).

---

## 7. Constraints on downstream diamonds

- **D3 (UI):** Minimalist-CLI, no web UI (a11y N/A). Needs: (a) **two entrypoints** with upfront `--preset / --seed / --run-type / --sample / --config / --out`; (b) per-stage **progress** + the **PowerMatrix verdict banner** + **fail-red gate messages**; (c) info-dense terminal **report pointers**; (d) **non-interactive by default** (default + smoke run in CI with no prompts — SP-W4); (e) a `--block-on-underpower` flag to convert the default's non-fatal power flag into a hard halt for stricter callers (SP-W2). **No `--from-stage` resume flag** (SP-W3 descope) — recovery is re-invoke-the-stage.

- **D4 (System):** a **linear stage sequencer** (not an event bus, not a conversation state machine) with: **hashed, sealed stage artifacts**; the **sample-manifest as the inter-process seam contract** (the load-bearing schema — L1); **gate predicates as named, unit-testable functions over the run-record** (SP-W1) evaluated fail-closed at each boundary — P1 import-graph/call-graph guard (NFR-019), P2 5-tuple regression test (NFR-041), P3 power gate (NFR-053, run-type-scoped); a **run-record sidecar writer** keyed on shared `run_id`, one record per stage (NFR-042), emitted as a first-class audit artifact (SP-W5); **pure-stdlib cores + lazy heavy-dep guards** (NFR-050). State persisted per boundary = `{stage, artifact_hash, run_id, seed, code_commit}` enabling crash-recovery via **re-run** (no stateful resume engine — SP-W3). **L4 loader strategy remains deferred to D4/D5** (prefer fixing the bundled parser + regression contract; reserve `load_dataset` import for the sampler side).

---

## 8. What feeds the next diamond (D3 UI)

D3 inherits a **non-interactive two-CLI batch surface** with one upfront decision (preset + run-type), per-stage progress + verdict banners + fail-red gate messages, info-dense report pointers, and an explicit **no-interactive-consent** commitment (SP-W4, flagged for Pass-2). The gate-message vocabulary (P1/P2/P3 + prereg + NOT-CONVERGED) and the PowerMatrix verdict banner are the load-bearing UI affordances. The `--block-on-underpower` flag and the absence of a `--from-stage` flag are the two named UI-surface switch-points carried forward.

---

✅ **D2 CONVERGE complete (2026-06-01).** Pugh-compared 3 workflow archetypes (A Linear-batch / B Event-Driven / C Agent-Conversation) against the brief's five criteria; **Frame A (Linear-batch-pipeline) preferred (datum; the only non-negative total)** — cycle-1-consistent and a 1:1 match to the `load→…→report` spine. Enriched with **B's two winning ideas** as switch-points: gate-as-named-predicate discipline (SP-W1) + honest-halt-and-re-run resume model (SP-W3, trimming A's own `--from-stage` over-build). Six switch-points named + resolved (SP-W1…W6). Decisive finding: **no resume requirement exists** — recovery is byte-identical re-run from the sealed manifest (NFR-030). High-stakes commitment flagged for Pass-2: **no interactive per-stage consent** (SP-W4). `provisional_status: AGENT_SIMULATED`. Ready for D3 (UI).
