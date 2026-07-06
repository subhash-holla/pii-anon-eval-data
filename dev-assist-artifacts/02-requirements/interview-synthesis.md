# R3 — Simulated Interview Synthesis

**Stage 2 · R3** · 2026-05-28 · `provisional_status: AGENT_SIMULATED`

> **Methodology note (epistemic honesty + scale):** R3's interview corpus is the **15-member §5 concept-value cohort** (`01-discovery/06-concept-value-study-synthesis.md`), which already ran a 30-question protocol per member probing per-persona capability value, adoption likelihood, and bounce triggers — i.e., requirement-level signal. Rather than re-dispatch a separate literal-n=30 interview wave (single-session execution limit), that corpus is re-analyzed here through the FR/NFR lens. **This is a deviation from literal full-rigor R3** and is flagged for **real-user Pass-2**. Cross-persona prioritization is then independently re-tested in R6.

## Requirements personas CONFIRM (strong, multi-persona)
- **FR-011/012/013 (pseudonymization-integrity)** — *universally* confirmed; "empty quadrant, would adopt with no caveats" (tool-builder, clinical de-id, both DPOs, batch priv-eng). **Strongest signal in the study.**
- **FR-006/007 (anon output scoring + measured RRS)** — confirmed as the headline by researchers + acad-de-id; "the thing I currently can't write on a model card" (HF author).
- **FR-004 (per-slice CIs)** — confirmed by all 3 research/academic personas; solves the i2b2/TAB underpowering pain.
- **FR-003 (scorer I/O contract + Presidio adapter)** — confirmed make-or-break by tool-builders + priv-engs ("documentation promise, not a drop-in" without it).
- **FR-009 (non-strippable caveat)** — confirmed emphatically by both DPOs + acad-de-id ("an engineer will strip it and hand me 'certified: anonymized'").
- **FR-021/022 (end-state bundle + legally-distinct crosswalk)** — confirmed by DPOs ("first benchmark mapping to actual legal architecture"); the "inform not determine" framing is "the only usable epistemic posture."
- **FR-023/026 + NFR-014 (neutral leaderboard + governance)** — confirmed hard gate ("MLPerf not a company's responsible-AI page"; un-citable in a DPIA if vendor-captured).

## Requirements personas DON'T care about (OUT/COULD candidates, persona-dependent)
- **FR-014 (query-aware)** — irrelevant to researchers/tool-builders/acad-de-id; valued only by runtime priv-eng. → SHOULD, not MUST.
- **FR-011–013 (pseudonymization)** — *irrelevant to clinical acad-de-id* (de-id is irreversible removal) and to red-teamers — but MUST for others. Persona-stratified value, not OUT.
- **FR-017–020 (agentic)** — MEDIUM/low for researchers/academics/DPOs; useful only to red-teamers, and only as a bounded oracle. → SHOULD/COULD; FR-020 roadmap.
- **FR-019 (transcript residual)** — weakest item even for red-teamers. → COULD.

## Gaps personas surfaced that we hadn't drafted → became FR/NFR (validates N1–N9 capture)
- **Coreference + quasi-identifier-combination scoring** (legal/education de-id, strong) → FR-015/016, NFR (the dominant hard-case class; "if you score only spans you miss what IRBs worry about").
- **Eval cost + cheap-adversary mode** (HF author, gateway) → NFR-009.
- **Adversary pluggability** (senior researcher) → FR-010.
- **Runtime latency/throughput + streaming** (runtime gateway) → NFR-010.
- **Financial-sector PII coverage** (fintech) → NFR-011.
- **Per-language sample-size table** ("60 languages means nothing if 50 have <200 positives") → NFR-003.
- **Frictionless citation** (PhD "citation-giver") → FR-028.

## Priority DISAGREEMENTS (→ R6/R7 to adjudicate)
- Pseudonymization track: MUST for tool-builders/DPOs, irrelevant for clinical de-id/red-teamers → **persona-stratified MUST** (keep MUST; document audience).
- Agentic track: red-teamers want it (bounded), everyone else indifferent → **SHOULD**.
- Real-data slice (FR-027): "the unlock" for academics/researchers (would be MUST for headline citation) but explicitly v1.1 → **SHOULD now, MUST-for-v1.1**.

## Cross-cutting confirmations → NFRs
- Synthetic-only ceiling is universal → FR-027/NFR (real-data slice) is the dominant unlock; everything else carries the caveat.
- Version-pinning (NFR-007) + |C| param (FR-007) repeatedly demanded.
- Test/CI credibility (NFR-016) demanded ("an unverified scorer is disqualifying for a measurement artifact").

✅ R3 synthesis complete → feeds R4 (already folded into FR/NFR set) + R5 survey design.
