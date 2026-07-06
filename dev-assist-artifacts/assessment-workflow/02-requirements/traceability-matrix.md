# CAP-02 Traceability Matrix

**Capability**: CAP-02 — Powered, repeatable, reportable assessment workflow (runs the **existing** `pii-rate-elo` tournament against PII-Anon **v2.0.0 / 575,604 / CC0 / `annotations`** over a powered, lattice-stratified sample (default) / full corpus (opt-in, citable) / smoke (fast), with observability + reporting at every spine stage `load → sample → run → score → rate → report`).
**Stage**: assessment-workflow / 02-Requirements · **R8 (canonical traceability)** · 2026-06-01.
**Chain**: **Persona → PGO → UC → FR/NFR → (DC → Story → Test in later stages)** — fully navigable in both directions via this matrix + `_bridge/uc-pgo-map.md`.
**provisional_status**: AGENT_SIMULATED (every row) — the persona/PGO/UC chain is agent-simulated single-session research; the code/version/line evidence the requirements bind to is direct file-read at HEAD on 2026-06-01. Real-user validation is a Pass-2 follow-up.
**Vocabulary remap**: PGO = Benchmark Goal · UC = Evaluation Scenario · FR = Benchmark/Assessment Capability · NFR = Quality Attribute · AX = binding axiom.

> **ID discipline.** Global numbering continued, never renumbered/reused: UC-16…23, FR-030…054, NFR-019…055, AX-pii-anon-001…005 (005 candidate, CONFIRMED at R7). Cycle-1 IDs (UC-01…15, FR-001…029, NFR-001…018) are frozen and binding; this matrix references them only where a CAP-02 requirement inherits/extends one.

---

## 1. Forward: UC → FR / NFR → priority (UC-16 … UC-23)

The unit carried into Requirements is the UC. Each UC resolves to its serving FR/NFR set; priority is the **final R7-committed** class; `provisional_status` is per-UC (all AGENT_SIMULATED, with the load-bearing structural caveat named in the Notes).

| UC | Title (abbrev.) | FRs | NFRs | Priority | provisional_status |
|---|---|---|---|---|---|
| **UC-16** | Powered lattice-stratified sample meeting committed-lattice tiers (seeded; per-cell power class + NOT_ASSESSED) | FR-032, FR-033, FR-034 (+FR-035 default) | NFR-035, NFR-036, NFR-037, NFR-038, NFR-039, NFR-030 (repro), NFR-053 (power gate) | **MUST** | AGENT_SIMULATED |
| **UC-17** | Elo/Glicko run — per-metric CIs, paired tests, RD-convergence; scoring_family / contamination / seed-variance | FR-039, FR-040, FR-041, FR-042, FR-043 | NFR-019, NFR-020, NFR-021, NFR-022, NFR-023, NFR-024, NFR-026, NFR-027, NFR-029, NFR-045, NFR-048 | **MUST** | AGENT_SIMULATED |
| **UC-18** | Pre-register the run BEFORE any system is scored (git-anchored + hash-chained) | FR-044 (+FR-038 scoping, FR-050 embed) | NFR-031, NFR-032, NFR-033 | **MUST** | AGENT_SIMULATED · pre-reg enforcement opt-in (D3) |
| **UC-19** | Full-corpus opt-in run (descriptive census; count from version-pinned loader) | FR-036 (+FR-035, FR-038, FR-039, FR-044 parity) | NFR-025, NFR-032 | **SHOULD** | AGENT_SIMULATED · DF-1 filing-grade pushback → Pass-2 |
| **UC-20** | Smoke run for fast CI/dev iteration (suppress all CI + p-value fields) | FR-037 (+FR-035, FR-038) | NFR-034, NFR-033 | **SHOULD** | AGENT_SIMULATED |
| **UC-21** | Reconcile dataset seam to v2.0.0 + pin regression contract (5-tuple) | FR-030, FR-031 | NFR-040, NFR-041, NFR-054 (doc-drift) | **MUST** | AGENT_SIMULATED (code-evidence firsthand at HEAD) |
| **UC-22** | Observability run-record at every spine stage + file-level provenance | FR-045, FR-046 | NFR-042, NFR-043 | **MUST** | AGENT_SIMULATED · assurance lens FIRST-CONTACT (INT-05) → Pass-2 |
| **UC-23** | Reportable leaderboard + figures with HONEST verdicts | FR-047, FR-048, FR-049, FR-050, FR-053, FR-054 (+FR-033 power flags, FR-043 anon/pseudo, FR-051/052 governance) | NFR-028, NFR-044, NFR-046, NFR-047, NFR-049, NFR-029 (convergence), NFR-036 (shortfall surfaced) | **MUST** | AGENT_SIMULATED · operating-point (FR-048) MUST-for-P-priv-eng, unseated → Pass-2 |

**Every UC (UC-16…23) is served by ≥1 FR and ≥1 NFR → 0 orphan UCs.** Priority split: **6 MUST (UC-16/17/18/21/22/23) · 2 SHOULD (UC-19/20).**

---

## 2. Reverse: every FR → UC → PGO (forward-orphan check, all 25 FRs)

Every FR cites the UC it serves; the UC↔PGO bridge (`_bridge/uc-pgo-map.md`) resolves the UC to its PGO(s) → persona → goal. `[theme]` = the UC's `Trace:` names a workflow theme rather than a PGO ID, resolved through the UC's primary persona + intent (bridge §1).

| FR | UC | PGO(s) served | Priority |
|---|---|---|---|
| FR-030 | UC-21 | PGO-builder-02 [theme] (foundational to all researcher/builder/acaddeid PGOs) | MUST |
| FR-031 | UC-21 | PGO-builder-02 [theme] | MUST |
| FR-032 | UC-16 | PGO-researcher-03, PGO-acaddeid-01, PGO-priveng-03 [theme] | MUST |
| FR-033 | UC-16/23 | PGO-researcher-03, PGO-acaddeid-01 | MUST |
| FR-034 | UC-16 | PGO-acaddeid-03 | MUST |
| FR-035 | UC-16/19/20 | PGO-acaddeid-01/03, PGO-researcher-01, PGO-builder-01 | MUST |
| FR-036 | UC-19 | PGO-acaddeid-01/03, PGO-researcher-01 | SHOULD |
| FR-037 | UC-20 | PGO-builder-01 | SHOULD |
| FR-038 | UC-18/19/20 | PGO-acaddeid-03, PGO-builder-01 (run-type scoping) | MUST |
| FR-039 | UC-17/19 | PGO-researcher-01/03, PGO-builder-01, PGO-acaddeid-01 | MUST |
| FR-040 | UC-17/23 | PGO-researcher-03, PGO-acaddeid-01 | MUST |
| FR-041 | UC-17/23 | PGO-researcher-01, PGO-acaddeid-01, PGO-builder-01 | MUST |
| FR-042 | UC-17 | PGO-researcher-01/03 | MUST |
| FR-043 | UC-17/23 | PGO-researcher-01, PGO-builder-01/03 (separation), PGO-dpo-01 | SHOULD |
| FR-044 | UC-18/19 | PGO-acaddeid-03, PGO-complreviewer-01, PGO-tool-vendor-02 [theme] | MUST |
| FR-045 | UC-22 | PGO-priveng-02 [theme], PGO-complreviewer-01 | SHOULD |
| FR-046 | UC-22/23 | PGO-complreviewer-01, PGO-priveng-02 | SHOULD |
| FR-047 | UC-23 | PGO-researcher-01, PGO-builder-02, PGO-tool-vendor-01, PGO-priveng-01, PGO-dpo-01/02, PGO-complreviewer-02 | MUST |
| FR-048 | UC-23 | PGO-priveng-01, PGO-dpo-02 | COULD (MUST-for-P-priv-eng) |
| FR-049 | UC-23 | PGO-complreviewer-02, PGO-dpo-01 | MUST |
| FR-050 | UC-18/22/23 | PGO-complreviewer-01, PGO-acaddeid-03 | MUST |
| FR-051 | UC-17/23 | PGO-tool-vendor-01/02, PGO-builder-02, PGO-complreviewer-01 | MUST |
| FR-052 | UC-18/23 | PGO-complreviewer-01, PGO-priveng-01 | SHOULD |
| FR-053 | UC-23 | PGO-dpo-03, PGO-priveng-03 | SHOULD |
| FR-054 | UC-23 | PGO-acaddeid-03, PGO-tool-vendor-01 | SHOULD (MUST-for-P-acad-deid) |

**All 25 FRs trace to ≥1 UC → ≥1 PGO → 0 orphan FRs.**

---

## 3. Reverse: every NFR → axiom / precondition + UC (orphan check, all 37 NFRs)

Every NFR serves a binding axiom (AX-001…005) and/or a hard precondition (P1/P2/P3) and is exercised by ≥1 UC.

| NFR | Serves (axiom / precondition) | UC(s) | Priority |
|---|---|---|---|
| NFR-019 | P1; AX-005(1,2) | UC-17 | MUST |
| NFR-020 | P1; AX-005 | UC-17 | MUST |
| NFR-021 | P1; AX-002; AX-005 | UC-17 | MUST |
| NFR-022 | P1; AX-003 | UC-17 | MUST |
| NFR-023 | AX-003; AX-005(1) | UC-17/23 | MUST |
| NFR-024 | AX-003; AX-005 | UC-17/23 | MUST |
| NFR-025 | AX-003 | UC-19 | MUST |
| NFR-026 | AX-005(2) | UC-17/23 | MUST |
| NFR-027 | AX-005(2) | UC-17/23 | MUST |
| NFR-028 | AX-005(2) | UC-23 | MUST |
| NFR-029 | AX-005(3); G4 | UC-17/23 | MUST |
| NFR-030 | AX-002; AX-005(4) | UC-16 | MUST |
| NFR-031 | AX-005(4) | UC-18/19 | MUST |
| NFR-032 | AX-005(4) | UC-18/19 | MUST |
| NFR-033 | AX-005 (enforcement scope) | UC-18/19/20 | MUST |
| NFR-034 | AX-002; AX-005 (scope) | UC-20 | MUST |
| NFR-035 | P3; AX-003 | UC-16 | MUST |
| NFR-036 | P3; AX-003 | UC-16/23 | MUST |
| NFR-037 | P3; AX-003 | UC-16 | MUST |
| NFR-038 | P3; AX-002 | UC-16 | MUST |
| NFR-039 | P3; AX-003 | UC-16 | MUST |
| NFR-040 | P2 | UC-21 | MUST |
| NFR-041 | P2 | UC-21 | MUST |
| NFR-042 | AX-002; AX-005(4) | UC-22 | SHOULD (assurance-MUST sub-part, D4) |
| NFR-043 | AX-005(4) | UC-22 | SHOULD |
| NFR-044 | AX-001/003; AX-005(5) | UC-23 | MUST |
| NFR-045 | AX-004; AX-005 | UC-17 | SHOULD (NR-core MUST via NFR-055) |
| NFR-046 | AX-005 | UC-23 | COULD (MUST-for-P-priv-eng, D5) |
| NFR-047 | AX-005 | UC-23 | MUST |
| NFR-048 | AX-005(6) | UC-17/23 | MUST |
| NFR-049 | AX-005; inherits NFR-014 | UC-17/23 | MUST |
| NFR-050 | AX-002; engineering gate | (all — run-path import discipline) | MUST-grade gate (D10) |
| NFR-051 | OWNS/CONSUMES boundary | (all — consumer gates green) | MUST |
| NFR-052 | NFR-018 anti-drift (inherited); no corpus regen | UC-16 | MUST-grade gate (G-norg) |
| NFR-053 | NFR-018 (inherited hard gate); P3 | UC-16 | MUST-grade gate (G-norg) |
| NFR-054 | NFR-013 (inherited); doc-drift = 0 | UC-21 | MUST-grade gate (G-norg) |
| NFR-055 | AX-004; NFR-005 (inherited); four families never merged | UC-17/23 | SHOULD bundle / MUST-grade NR invariant (D6) |

**All 37 NFRs serve ≥1 axiom or precondition and are exercised by ≥1 UC → 0 orphan NFRs.**

---

## 4. Axiom → FR/NFR linkage (AX-001 … AX-005)

| Axiom | What it binds | FR(s) | NFR(s) |
|---|---|---|---|
| **AX-pii-anon-001** (synthetic-only / no real PII) | non-strippable synthetic-only / anti-anonymity caveat on every metric + figure | FR-034, FR-049, FR-054 (claims policy) | NFR-044 |
| **AX-pii-anon-002** (deterministic / seeded / byte-reproducible) | seeded LOCAL-RNG, byte-reproducibility from manifest, single-pass deterministic sampler | FR-032, FR-034, FR-044, FR-050 | NFR-021, NFR-030, NFR-034, NFR-038, NFR-042, NFR-050 |
| **AX-pii-anon-003** (stated power — every metric declares n + CI; tiered targets) | integer-guarded CIs; power class vs realized positives; named shortfall; design point in manifest | FR-033, FR-040 | NFR-022, NFR-023, NFR-024, NFR-025, NFR-035, NFR-036, NFR-037, NFR-039, NFR-044 |
| **AX-pii-anon-004** (anon vs pseudo, SEPARATE metric families) | scoring_family declared; pseudo never bare-F1; four families never merged; regulatory crosswalk legally distinct | FR-043, FR-047, FR-053 | NFR-045, NFR-055 |
| **AX-pii-anon-005** (pre-registered / reproducible assessment — CONFIRMED, candidate) | the 6-element bar, run-type-scoped enforcement, manifest-repro universal / pre-reg opt-in | FR-038, FR-040, FR-041, FR-044, FR-047, FR-049, FR-050, FR-051 | NFR-019, NFR-020, NFR-021, NFR-023, NFR-024, NFR-025, NFR-026, NFR-027, NFR-028, NFR-029, NFR-030, NFR-031, NFR-032, NFR-033, NFR-034, NFR-042, NFR-043, NFR-044, NFR-047, NFR-048, NFR-049 |

**AX-005 element → NFR map (the testable operationalization):**
| AX-005 element | NFR(s) |
|---|---|
| (1) CI with method named | NFR-023, NFR-024, NFR-025 |
| (2) Paired test + declared multiplicity family (Holm-Bonferroni, 2 families, family size in text) | NFR-026, NFR-027, NFR-028 |
| (3) Convergence as achieved max-RD ± 2RD + rounds | NFR-029 |
| (4) Provenance reproducible-from-manifest | NFR-030, NFR-031, NFR-032, NFR-042, NFR-043 |
| (5) Non-strippable synthetic-only caveat | NFR-044 |
| (6) Contamination disclosure + held-out non-exposure attestation | NFR-048, NFR-049 |
| Enforcement scope (run-type-bound) | NFR-033, NFR-034 |

**Precondition → NFR map (the 3 hard preconditions, fully covered):**
| Precondition | FR(s) | NFR(s) |
|---|---|---|
| **P1** — audited stats only; `significance.py` quarantined; zero approximated stats on run path | FR-042 (+FR-040/041) | NFR-019, NFR-020, NFR-021, NFR-022 |
| **P2** — seam → v2.0.0 via versioned crosswalk + regression contract | FR-030, FR-031 | NFR-040, NFR-041 |
| **P3** — powered lattice-stratified sampler + PowerMatrix verdict + per-cell named shortfall vs realized positives | FR-032, FR-033, FR-034 | NFR-035, NFR-036, NFR-037, NFR-038, NFR-039 (+ NFR-053 power gate) |

---

## 5. PGO → UC linkage + the 3 HIGH personas (MUST-cover coverage)

From `_bridge/uc-pgo-map.md` (R0). The 9 HIGH-persona PGOs are **MUST-cover**; the 9 MEDIUM + 4 sub-archetype-driver PGOs are **SHOULD-cover**.

**HIGH personas — MUST-cover PGOs (the acceptance + credibility cohort):**
| PGO | Persona | Served by UC | In-scope? |
|---|---|---|---|
| PGO-acaddeid-01 | P-acad-deid | UC-16, UC-17, UC-19 | ✅ covered |
| PGO-acaddeid-02 | P-acad-deid | — | **scoped-OUT** (re-id/RRS ladder; roadmap) |
| PGO-acaddeid-03 | P-acad-deid | UC-18, UC-19 | ✅ covered |
| PGO-researcher-01 | P-mlnlp-researcher | UC-17, UC-19, UC-23 | ✅ covered |
| PGO-researcher-02 | P-mlnlp-researcher | — | **scoped-OUT** (re-id/ESRC; roadmap) |
| PGO-researcher-03 | P-mlnlp-researcher | UC-16, UC-17 | ✅ covered |
| PGO-builder-01 | P-tool-builder | UC-17, UC-20 | ✅ covered |
| PGO-builder-02 | P-tool-builder | UC-21, UC-23 | ✅ covered |
| PGO-builder-03 | P-tool-builder | — | **scoped-OUT** (pseudonymizer RRS figure; roadmap) |

**MEDIUM personas + sub-archetype drivers — SHOULD-cover PGOs:**
- **Covered by a UC (9 of 13):** PGO-priveng-01 (UC-23), PGO-priveng-02 (UC-22), PGO-priveng-03 (UC-16/23, partial), PGO-dpo-01 (UC-23), PGO-dpo-02 (UC-23, detection-side), PGO-tool-vendor-01 (UC-23), PGO-tool-vendor-02 (UC-18/23), PGO-complreviewer-01 (UC-18/22/23), PGO-complreviewer-02 (UC-23).
- **Scoped-OUT (cycle-1 / roadmap, documented):** PGO-redteam-01/02/03 (agentic recognition-oracle / RRS-on-transcripts → cycle-1 UC-08/09 + live-harness-adapter roadmap).
- **Weak/partial → authored, not dropped:** PGO-priveng-03 + PGO-dpo-03 (regulatory crosswalk / 63-type checklist) → FR-053 **AUTHOR-not-defer** (D8), resolving Open Item 10.

---

## 6. Orphan check (0 orphans required — PASS)

Per the R0 contract, two directions plus a weak-coverage note.

### (A) UCs with no FR/NFR — **0 orphans**
All 8 UCs (UC-16…23) are served by ≥1 FR **and** ≥1 NFR (§1). No scenario is requirement-orphaned.

### (B) FRs / NFRs with no UC — **0 orphans**
All 25 FRs trace to ≥1 UC (§2); all 37 NFRs are exercised by ≥1 UC (§3). No requirement is scenario-orphaned.

### (C) UCs with no PGO / MUST-cover PGOs with no UC — **0 in-scope orphans**
- UC → PGO: every UC serves ≥1 PGO (bridge §2). **0 forward orphans.**
- MUST-cover (HIGH) PGO → UC: **6 of 9 covered**; the **3 uncovered (PGO-acaddeid-02, PGO-researcher-02, PGO-builder-03) are the re-identification / RRS family**, each closed by an **explicit, documented out-of-scope boundary** with a named roadmap reuse hook (`REID_TIER_SPECS`), per `04-use-cases.md` UC-23 §scope-boundary + Open Item 13 / MEI-06. **These are explicitly-scoped-OUT, not orphans.**

### (D) MUST UC served only by COULD requirements — **none**
Every MUST UC (UC-16/17/18/21/22/23) is served by ≥1 MUST FR and ≥1 MUST NFR. UC-23 (MUST) includes the COULD operating-point view (FR-048/NFR-046) **in addition to** its MUST report spine (FR-047/049/050; NFR-044/047) — the MUST deliverable does not depend on the COULD item.

### (E) Axiom coverage — **all 5 axioms wired**
AX-001…005 each link to ≥1 FR and ≥1 NFR (§4). No binding axiom is unimplemented.

**Orphan rate:**
- UC orphan rate (UCs with no requirement): **0 / 8 = 0.0%.**
- FR orphan rate (FRs with no UC): **0 / 25 = 0.0%.**
- NFR orphan rate (NFRs with no axiom/precondition+UC): **0 / 37 = 0.0%.**
- In-scope MUST-PGO orphan rate (HIGH PGOs with no UC, excluding the 3 explicitly-scoped-OUT re-id PGOs): **0 / 6 = 0.0%.**

**Matrix verdict: 0 orphans (honest rate 0.0%).** The only MUST PGOs without a UC are the three re-id/RRS goals, each closed by an explicit documented out-of-scope boundary with a named roadmap hook — the bound is honest, not silent. The two SHOULD PGOs flagged weak-coverage at R0 (priveng-03, dpo-03 — the regulatory crosswalk) are now served by FR-053 (AUTHOR-not-defer).

---

## 7. Brief-required coverage (every mandated (a)–(h) coverage point lands on ≥1 UC + FR + NFR)

| Required coverage | UC | FR(s) | NFR(s) |
|---|---|---|---|
| (a) powered representative sample meeting committed-lattice tiers, seeded/deterministic | UC-16 | FR-032/033/034 | NFR-035/036/037/038/039/030 |
| (b) Elo/Glicko assessment with per-metric CIs + paired tests + RD convergence | UC-17 | FR-039/040/041 | NFR-023/026/027/029 |
| (c) full-corpus opt-in run | UC-19 | FR-036 | NFR-025/032 |
| (d) smoke run | UC-20 | FR-037 | NFR-034 |
| (e) pre-register the run BEFORE scoring | UC-18 | FR-044 (+FR-038) | NFR-031/032/033 |
| (f) reconcile the `pii-rate-elo` dataset seam to v2.0.0 + regression contract | UC-21 | FR-030/031 | NFR-040/041 |
| (g) observability run-records at every dataset op | UC-22 | FR-045/046 | NFR-042/043 |
| (h) reportable leaderboard + figures + HONEST verdicts (RD-not-converged / under-powered / synthetic-only) | UC-23 | FR-047/049/050 | NFR-044/047/029 |

All eight brief-required coverage points map to exactly one MUST/SHOULD UC, each backed by ≥1 FR and ≥1 NFR.

---

## 8. Status change log (Requirements stage)

| Date | Req | From | To | Reason |
|---|---|---|---|---|
| 2026-06-01 | AX-pii-anon-005 | (candidate) | PROPOSED (R4) | 6-element axiom proposed + wired to FR-040/041/044/049/045/046/043/051/038 + NFRs |
| 2026-06-01 | AX-pii-anon-005 | PROPOSED | **CONFIRMED (pending PO sign-off)** | R7: 6/6 R6 respondents Yes (one Yes-with-change); SRV-04 sharpening adopted (element 6 binds leaderboard-submission AND filing-grade) |
| 2026-06-01 | FR-043 | MUST (R4) | SHOULD (R7) | B10 new anon/pseudo sub-parts; sampling gap (MEDIUM personas unseated). NR-core (four families never merged) stays MUST via NFR-055/G-norg. Reversible at Pass-2 (D6) |
| 2026-06-01 | FR-045 | MUST (R4) | SHOULD (R7) | B12 per-stage run-record SHOULD overall; the 6-stage provenance floor is the assurance-MUST sub-part. Reversible at Pass-2 (D4) |
| 2026-06-01 | FR-048 | MUST (R4) | **COULD-overall / MUST-for-P-priv-eng** (R7) | B14 operating-point; no P-priv-eng seat administered at R6. The bundle most distorted by the sampling gap; Pass-2 with a real P-priv-eng seat is the highest-priority re-elicitation (D5) |
| 2026-06-01 | FR-053 | (author-or-defer fork) | SHOULD, **AUTHOR-not-defer** (R7) | T7 tied 3–3 but R3 resolved AUTHOR via the two MEDIUM compliance personas (unseated); the R3 resolution governs the absent-seat tie. Honors Open Item 10 (D8) |
| 2026-06-01 | FR-054 | (persona-stratified) | SHOULD, **MUST-for-P-acad-deid** (R7) | Zenodo DOI is a HARD citation gate for the academic cohort, silent elsewhere (D9) |
| 2026-06-01 | NFR-010b (inherited) | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE (unchanged) | CAP-02 does not re-pin the cycle-1 lightweight-detection throughput floor; it inherits it unchanged (`real_user_needed: true`) |

---

## 9. Methodology & Epistemic Honesty (traceability-specific)

- **Trace chain fully navigable both directions:** Persona → PGO (`personas.md` / bridge §0) → UC (bridge §1/§2) → FR/NFR (§2/§3 here) → (DC → Story → Test downstream). The reverse is the orphan check (§6).
- **provisional_status: AGENT_SIMULATED** on every row. Two load-bearing structural caveats ride specific rows: (1) the **P-dpo / assurance lens is FIRST-CONTACT** (INT-05) — UC-22 and the compliance FRs/NFRs trace to a single un-re-confirmed lens; (2) the **3 MEDIUM personas were UNSEATED at R6** — UC-23's operating-point sub-part (FR-048) and the MEDIUM-owned bundles are adjudicated against the R3-elicited priority, with Pass-2 re-elicitation named.
- **The 3 explicitly-scoped-OUT re-id/RRS PGOs are documented boundaries, not orphans** — closed by `04-use-cases.md` §scope-boundary + Open Item 13 / MEI-06, with the `REID_TIER_SPECS` roadmap reuse hook. Counting them raw gives a 3/9 = 33% MUST-PGO figure, but all three are honest-bounded, so the **true orphan rate is 0.0%**.
- **No FR/NFR/UC IDs minted or renumbered** in this matrix; it indexes the existing UC-16…23 / FR-030…054 / NFR-019…055 set verbatim. Cycle-1 inherited IDs are referenced only where a CAP-02 requirement extends one (NFR-005/013/014/018).
- **Source artifacts:** `_bridge/uc-pgo-map.md` (R0), `functional-requirements.md` + `non-functional-requirements.md` (R4), `prioritization-decisions.md` (R7), `interview-synthesis.md` (R3), canonical Discovery (`01-discovery/`). Cycle-1 `02-requirements/traceability-matrix.md` provided the format convention.

✅ **R8 Traceability Matrix complete (2026-06-01).** UC→FR/NFR table for UC-16…23 with a `provisional_status` column; axiom linkage AX-001…005 (005 CONFIRMED candidate); PGO links (persona → PGO → UC → FR/NFR, both directions); precondition→NFR map; brief-coverage map. **Orphan check: 0 orphans** (0/8 UCs, 0/25 FRs, 0/37 NFRs; the 3 uncovered MUST PGOs are explicitly-scoped-OUT re-id/RRS goals with named roadmap hooks). `provisional_status: AGENT_SIMULATED`.
