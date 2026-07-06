# CAP-02 Requirements Methodology & Epistemic Honesty

**Capability**: CAP-02 — Powered, repeatable, reportable assessment workflow (runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 / CC0 / `annotations`** over a powered, lattice-stratified sample (default) / full corpus (opt-in, citable) / smoke (fast), with observability + reporting at every spine stage).
**Stage**: assessment-workflow / 02-Requirements · **R8 (methodology record)** · 2026-06-01.
**provisional_status**: AGENT_SIMULATED — all critics, personas, interviewees, survey respondents, and SME panels are agent-simulated single-session research; the **code / version / line evidence** the requirements bind to is **direct file-read at HEAD on 2026-06-01** in `pii-anon-eval-data` (the cited `pii-rate-elo` lines are from the Discovery file-reads at HEAD — that repo is not checked out on this machine). **Agent-simulated research is NOT a substitute for real users.**

> **Project framing (vocabulary remap).** This is a **synthetic** PII benchmark assessed at **representative scale** in a **single session**. UC = Evaluation Scenario · FR = Benchmark/Assessment Capability · NFR = Quality Attribute · DC = Benchmark Component · Persona = assessment consumer. The representative-scale / single-session limit is **documented, not hidden** (this file).

---

## 1. R0–R10 execution record

| Phase | What ran | Agents / mode | Output |
|---|---|---|---|
| **R0** | UC↔PGO bridge + orphan scan (≈0%) | authored (mechanical) from Discovery | `_bridge/uc-pgo-map.md` |
| **R1** | Low-fi FR/NFR | folded into R4 (authored from Discovery) | (folded) |
| **R2** | Interview guide (18 persona-agnostic core probes + per-persona Layer-2 + sub-archetype probes + self-bias check) | authored | `interview-guide.md` |
| **R3** | Simulated-interview synthesis | **6 `simulated-interviewee` agents** (1/persona: INT-01…06), incl. the P-complreviewer sub-archetype (closing the R2 un-sampled-DPO gap) + the P-tool-vendor gaming angle | `interview-synthesis.md` |
| **R4** | Hi-fi FR/NFR authoring | authored from Discovery + R0 bridge + R3 | `functional-requirements.md` (FR-030…054), `non-functional-requirements.md` (NFR-019…055) |
| **R5** | Survey instrument (3-tier, 18 bundles + 2 baseline gates + coverage table) | authored | `survey-instrument.md` |
| **R6** | Prioritization survey | **6 `simulated-survey-respondent` agents** (all HIGH-cohort/sub-archetype seats) | `survey-analysis.md` |
| **R7** | Prioritization analysis + boundary adjudication (D1–D12) | authored from R6 + R3-fallback | `prioritization-decisions.md` |
| **R8** | Canonical artifacts | authored | `requirements-document.md`, `traceability-matrix.md`, this file |
| **R9** | Verification-criteria strengthening | (next) | (audit / strengthened acceptance criteria) |
| **R10** | NFR threshold validation | (next) — threshold-validator panel on the quantified NFRs | `_threshold-validation/` |

---

## 2. Agent counts (this stage)

- **R3:** 6 simulated interviewees (INT-01…06), one per persona (3 HIGH / 3 MEDIUM), 27–30 probes each.
- **R6:** 6 simulated survey respondents — **all HIGH-cohort or its folded sub-archetypes** (3× P-mlnlp-researcher, 1× P-acad-deid, 1× P-tool-builder/OSS, 1× P-tool-builder/`P-tool-vendor`).
- **Discovery (inherited context):** 3 POV critics + 6 persona researchers + JTBD/Kano/Pugh market synthesis + 5-SME UC panel + 6-member concept-value cohort (5 completed, 1 refused).
- **Structural/synthesis phases (R0/R1/R4/R5/R7/R8)** were **authored directly** from the rich Discovery + R3 signal (the dedicated author agents would have read the identical inputs); authoring did not reduce the rigor of the resulting requirements, which carry full Given/When/Then (FRs) + quantified-or-boolean-auditable thresholds + measurement methods (NFRs).

---

## 3. Representative-scale + single-session limit (the dominant methodological caveat)

This is a synthetic benchmark assessed by **small simulated cohorts in one session** — directional, **not** confirmatory or saturated. The user elected full literal rigor; a genuine **single-session execution limit** (context budget for processing many agent transcripts) forced representative-scale substitutions, each documented and flagged for real-user Pass-2:

1. **R3 (literal ~30 interviews) → n=6** (one per persona). Captured the convergent gating signal (C-1…C-10), resolved DF-1…DF-5, and surfaced 15 net-new candidates (N-01…N-15) — including **3 net-new capabilities that came ONLY from the MEDIUM personas** (operating-point reporting, filing-grade artifact format, oracle throughput SLA), which would have been missed without the DPO sampling-gap closure + the red-team + priv-eng sections.
2. **R6 (literal ~60 responses) → n=6**, and **all 6 seats are HIGH-cohort/sub-archetype**. The **3 MEDIUM personas (P-priv-eng, P-dpo/P-complreviewer, P-agentic-redteam) were NOT seated.** Inter-respondent variance on the consensus MUSTs (B1/B2/B3/B6/B8/B13/B16) was very low (mostly 6–0), so those are well-supported; the **MEDIUM-owned bundles (B12/B14/B17 + throughput) are systematically under-weighted** by the all-HIGH cohort.
3. **R10 (literal 10 personas × N NFRs):** representative validator panel on the quantified-threshold NFRs — to be recorded in `_threshold-validation/`.

**Adjudication method that the sampling gap forced (R7 §0):** MEDIUM-owned bundles are **NOT de-scoped by the absent-seat vote** — they fall back to the R3-elicited MEDIUM priority + the R4 UC-mandated FR priority. A 6× COULD from HIGH seats on a P-priv-eng-core bundle (B14/FR-048) is read as a **missing-seat artifact**, not a verdict (D5). Every such adjudication carries `real_user_needed: true` to Pass-2.

---

## 4. Confirmation-bias controls (disconfirmation worked)

- The R2 guide embedded **mandatory rejection probes**; they elicited rejection signal, not just assent. They surfaced **three walk-away triggers** named by multiple personas — fabricated statistics (`significance.py`), an unpinned dataset seam, and a missing power verdict — and the **mandatory-pre-reg avoidance risk** (4 personas independently warned mandatory-for-all-runs would cause teams to route around the harness or file development outputs).
- The **DF-1 default-mode fork was kept genuinely open**: it produced the study's one real disagreement (powered-sample-default vs INT-05's full-corpus-for-filing), resolved **split-by-use** (locked default holds + run-type designation), with INT-05's pushback carried forward rather than smoothed.
- **No interviewee challenged the core spine, the OWNS/CONSUMES boundary, or the engine-reuse posture** — INT-01 (the G1/G6 probe) said reuse "makes me substantially more likely to trust and cite it." The disagreements were all at the scoping/priority layer, not the architecture layer.

---

## 5. Epistemic honesty — what is firsthand vs simulated

- **Firsthand (direct file-read at HEAD, 2026-06-01):** the code/version/line evidence the requirements bind to — `stats/power.py` (`TIER_SPECS` 1522/753/200 derived via `required_n`; `REID_TIER_SPECS` 897/385 *pairs*; `PowerClass` WELL/UNDER/EMPTY; `PowerMatrix.verdict` LARGE≥0.999 / ADEQUATE≥0.80 at L357-361), `stats/intervals.py` (integer-guarded Wilson/Clopper-Pearson), `stats/paired.py` (McNemar exact/χ² + seeded LOCAL-RNG paired bootstrap), `stats/lattice.py --check` (730 cells @ `47c3a8f`), `scripts/lattice_audit.py` (single-pass realized-positive streaming), `scripts/benchmark_throughput.py` (seeded run-record + Algorithm-R reservoir), `scripts/write_manifest.py` (content hash), `scoring/detection.py::DesignProvenance` + `subsets/slices.py` (non-strippable caveats), `tests/test_doc_drift.py` (`CANONICAL_RECORDS="575,604"`, entity count = `tx.ENTITY_TYPE_COUNT` = 63 derived). The cited `pii-rate-elo` lines (`significance.py` L205-206/L271-281 fabrication; `pii_anon_eval.py` L93/L221/L222 + `schema.py` L137/L349 drift) are from the Discovery file-reads — that repo is not checked out on this machine.
- **Simulated (AGENT_SIMULATED):** every persona, PGO, UC, interview, and survey signal, and **every quantified threshold embedded in FR/NFR text** (e.g. <10 min smoke, <30 min powered, ≤50 ms p95 / ≥500 rps oracle SLA, 3-seed Kendall-τ minimum, the 34k-FP false-positive-tax figure, the 0.80/0.999 verdict cuts). These are **directional**, not committed — the R9 verification-criteria pass + the R10 threshold-validator pressure-test them.
- **AX-pii-anon-005 is CONFIRMED at R7 (6/6, one adopted sharpening) but remains a candidate pending PO sign-off**; it is recorded in `requirements-document.md` for confirmation, and the NFRs are its testable operationalization.

---

## 6. Named Pass-2 gaps (real-user validation required — do NOT treat as closed)

1. **Real-user validation across the whole roster** — interview ACL/PETS authors, Presidio/GLiNER/Piiranha maintainers, i2b2/n2c2 participants, privacy/platform-security engineers running bake-offs, and DPO-adjacent assessors. None of the agent-simulated signal substitutes for this.
2. **The P-dpo / assurance lens is FIRST-CONTACT** (INT-05), **not** re-confirmation of the cycle-1 P-dpo priority — a clean INT-05 result does not validate that priority. The compliance FRs/NFRs (FR-045/046/050/052/053; NFR-042/043) trace to a single un-re-confirmed lens. Real-user DPO interviews remain a Pass-2 **must**.
3. **The 3 MEDIUM personas were UNSEATED at R6.** The single highest-priority re-elicitation is a real **P-priv-eng** seat for the operating-point view (FR-048/NFR-046 — the bundle most distorted by the sampling gap, D5). A real-user Pass-2 with the MEDIUM personas is expected to **lengthen the SHOULD/COULD tail** beyond the current MUST-heavy shape.
4. **The DF-1 filing-grade pushback** (INT-05 wants full-corpus as the default for filing-grade evidence) is carried as the FR-038 `filing-grade` backing-mode profile, **pending real-user DPO verification** of whether regulators accept a well-labelled powered-sample artifact (INT-05's own hedge).
5. **The real-data correlation slice** (cycle-1 UC-13, vs i2b2-2014 / TAB) is the single highest-leverage credibility unlock and the **strongest convergent missing-capability signal of R6** (4 of 6 named it). It is **out-of-band / gated on external DUA / explicitly NOT v0.1-blocking** (DF-4, unanimous), carried as a named COULD-scope roadmap stub + the FR-049 "named-and-pending" report flag (D11). Real-data acquisition + the correlation study are Pass-2 / Testing follow-ups.
6. **Directional thresholds** (§5) require real-user verification in Pass-2; each interviewee flagged its own numbers as needing it. R10 records the threshold-validation outcomes in `_threshold-validation/`.

The dev-assist-testing pass2-coordinator will **refuse substitution** of agent-simulated research for real users on these gaps.

---

## 7. Distribution shape — the MUST-heavy result is structural, not a prioritization failure

**Combined 62 requirements: 48 MUST (77.4%) · 12 SHOULD (19.4%) · 2 COULD (3.2%)** — MUST-heavy versus the natural ~30/55/15 shape. The deviation is **structural and documented** (R7 §6), for three converging reasons:
1. **The requirement set entered R6 pre-concentrated** — the UCs were SME-pre-filtered (3 CATASTROPHIC + 15 MAJOR resolved in place, 0 new IDs); the R4 FRs were authored 19-MUST / 6-SHOULD / 0-COULD. The academic-soundness spine *is* the capability — there is little legitimate SHOULD/COULD tail to find.
2. **3 of the 4 precondition bundles + the AX-005 enforcement spine are floor-locked MUST** by the locked brief — they cannot populate a SHOULD/COULD tail no matter how respondents vote.
3. **The round is all-HIGH-cohort** — the seats that would have pushed B12/B14/B17 down (the 3 MEDIUM personas) were unseated, so the tail is under-populated this round. The R3-fallback adjudications (D4/D5/D8) recover *some* tail (FR-048→COULD, FR-043/045→SHOULD, B17 split), but a real-user Pass-2 with the MEDIUM personas is expected to lengthen it further.

**No bundle scored majority-WON'T → 0 OUT items.** The MUST-skew is the honest shape of a precondition-heavy, all-gating-cohort round, **flagged here rather than smoothed by artificially demoting preconditions.**

---

## 8. No-regression discipline (carried as binding CAP-02 NFRs)

The cycle-1 frozen guardrails are encoded as MUST-grade NFRs and verified-locatable at HEAD this session:
- **Lattice 730 cells @ `47c3a8f`** (`stats/lattice.py --check`) → NFR-052.
- **NFR-018 committed-lattice power gate stays ON** (`scripts/validate.py --lattice`) → NFR-053.
- **Doc-drift = 0** (`tests/test_doc_drift.py`; 575,604 / 2,486,438 / 63-derived / v2.0.0; NFR-013 inherited) → NFR-054.
- **Four metric families never merged** (NFR-005 inherited invariant) → NFR-055.
- **No corpus regeneration**; pure-stdlib statistical cores + lazy heavy-dep guards (NFR-050); `pii-rate-elo` own gates (pytest/ruff/mypy) stay green (NFR-051).

CAP-02 **consumes** the `pii-rate-elo` engine/metrics/significance machinery (does not rebuild it) and **owns** the sampler + observability + reporting. The one net-new statistical primitive (Holm-Bonferroni, FR-041) is added to the **audited** `stats/paired.py` (or a sibling in `stats/`), **never** to the quarantined `significance.py`.

---

## 9. Source artifacts

- **CAP-02 Requirements (this stage):** `_bridge/uc-pgo-map.md` (R0), `interview-guide.md` (R2), `interview-synthesis.md` (R3), `functional-requirements.md` + `non-functional-requirements.md` (R4), `survey-instrument.md` (R5), `survey-analysis.md` (R6), `prioritization-decisions.md` (R7).
- **Canonical Discovery:** `01-discovery/discovery-report.md` (§8 Open Items 1–13, G1–G7 anti-over-claim rails, C1–C10), `01-discovery/04-use-cases.md` (UC-16…23 + acceptance signals), `01-discovery/personas.md` (6 personas + 2 sub-archetypes).
- **Capability manifest / offsets:** `assessment-workflow/MANIFEST-capability.md` (UC→16, FR→030, NFR→019, DC→16; inherited axioms; frozen guardrails).
- **Cycle-1 (format + inherited IDs):** `02-requirements/requirements-document.md`, `traceability-matrix.md`, `methodology.md` (R8 format convention); inherited NFR-001…018, FR-001…029, UC-01…15, AX-001…004.
- **Code (direct file-read at HEAD, 2026-06-01):** both repos for threshold grounding (paths enumerated in §5 + the R4 FR/NFR docs).

✅ **R8 Methodology complete (2026-06-01).** Records the R0–R10 execution path, agent counts, the **representative-scale + AGENT_SIMULATED + single-session limit**, the confirmation-bias controls, the firsthand-vs-simulated split, the **named Pass-2 gaps** (real-user roster validation; P-dpo first-contact; 3 MEDIUM personas unseated; DF-1 filing-grade pushback; real-data correlation slice; directional thresholds), the structural MUST-heavy distribution, and the no-regression discipline. `provisional_status: AGENT_SIMULATED`; real-user validation is Pass-2.
