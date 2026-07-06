# R10 — NFR Threshold Validation Findings

**Stage 2 · R10** · 2026-05-28 · 6-persona representative validator panel (researcher, tool-builder, acad-deid, priv-eng-runtime, priv-eng-batch, dpo) × 5 quantified-threshold NFRs.

> **Scale note:** literal protocol = 10 personas/NFR; ran a representative 6-persona panel (single-session limit). Aggregate outcomes below; **real-user Pass-2 required** for the agent-extrapolated numbers (esp. NFR-010 5k/10k). DPO INSUFFICIENT_EVIDENCE on ops-NFRs is honest out-of-scope, not divergence.

## Aggregate outcomes (6-bucket ontology)
| NFR | Verdicts (6) | Aggregate | Action |
|---|---|---|---|
| **NFR-001** power ≥753/1,522 | 6 ACCEPTED | **VALIDATED** | Lock. Refine: enrichment-flag **downgrades to "low-power, CI-reported" (does NOT fail)**; published score names the CI method (Wilson/Clopper-Pearson) + assumed recall+half-width inline (reconstructable by a regulator). Math independently verified (Wilson half-width). |
| **NFR-008** ECE ≤0.05 (reported) | 4 ACCEPTED, 2 PERSONA_CONDITIONAL | **ACCEPTED-WITH-CAVEATS** | Keep ≤0.05 as a **reported reference target (not pass/fail, not a compliance claim)**. Add: pin ECE bin-count + variant (equal-width vs adaptive); add a **low-confidence-band reliability curve** (runtime routing lives in the 0.3–0.7 band); co-report per-class n. |
| **NFR-009** cheap-adversary $0 + <10min/1CPU | 5 ACCEPTED, 1 INSUFFICIENT | **VALIDATED** | Lock. Refine: **pin the reference CPU/clock** so the 10-min budget is portable; the audit-grade RRS figure must name which adversary mode produced it. |
| **NFR-010** throughput ≥1,000 rec/sec/8-core | 2 PERSONA_CONDITIONAL, 2 REVISE_TIGHTER, 1 REVISE_LOOSER, 1 INSUFFICIENT | **PERSONA-STRATIFIED** | The single gate was wrong (NER detectors ~100 rec/sec/core can't hit it; runtime/batch want far more). **Split** → see NFR-010a/b/c below. |
| **NFR-016** ≥85% line + CI green | 4 ACCEPTED, 1 REVISE_TIGHTER, 1 PERSONA_CONDITIONAL | **ACCEPTED-WITH-CAVEATS** | Keep ≥85% line. **Add ≥70% branch coverage on scorer/statistical-computation modules** (where reproducibility bugs hide — tool-builder + acad-deid both flagged). Record coverage in a versioned auditable artifact (per NFR-017). |

## NFR-010 stratification (the DIVERGED-avoiding resolution)
- **NFR-010a — Reported throughput, PER detector-class (no gate):** every scored run reports rec/sec by detector class (regex / spaCy-NER / transformer / LLM); **transformer/LLM detectors are exempt from any throughput floor** (CPU transformer inference is legitimately slow). *Measure:* per-class rec/sec in the run-record.
- **NFR-010b — Runtime-consumer target (lightweight detection path):** **≥5,000 rec/sec on 8-core AND report p50/p95/p99 per-record latency** + streaming/chunked input. *(agent-extrapolated from prod-gateway evidence; Pass-2 the number.)*
- **NFR-010c — Batch full-scan guidance:** document expected wall-clock for warehouse-scale full scans + record-size disclosure; recommend sampling fallback above a stated row count. *(Pass-2 the ~10k figure.)*

## Status changes (→ traceability matrix Status Change Log)
- NFR-010 → **PERSONA-STRATIFIED** (split into 010a/b/c); 010b/010c numbers `provisional_status: AGENT_SIMULATED, real_user_needed: true`.
- NFR-008, NFR-016 → ACCEPTED-WITH-CAVEATS (Pass-2 priority).
- NFR-001, NFR-009 → VALIDATED.
- Boolean/auditable NFRs (002, 005, 006, 011, 012, 013, 014, 015, 017) — validated by audit/scan, not 10-persona stress-test (documented; not DIVERGED).

**Net: 0 DIVERGED, 2 VALIDATED, 2 ACCEPTED-WITH-CAVEATS, 1 PERSONA-STRATIFIED** across the 5 quantified-threshold NFRs.

---

**Amendment 2026-05-29 (S-PWR work-stream):** **NFR-018** (committed-lattice per-cell power) added and validated via a literal **10-persona** panel → **ACCEPTED-WITH-CAVEATS** (tier numbers 1,522/753/200 **locked**, 0 REVISE; 6 mechanism/framing refinements). **NFR-001** (extended to crossed cells) co-validated (identical constants). Full detail: [`findings-nfr-018-2026-05-29.md`](findings-nfr-018-2026-05-29.md).
