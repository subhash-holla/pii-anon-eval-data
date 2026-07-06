# Recruiting / Acquisition Checklist — FR-015 / FR-016

**Stage 5 · Wave T5 (Pass-2)** · 2026-05-31 · companion to [`protocol.md`](protocol.md).
Two legs: (1) **real annotated data** (shared i2b2/TAB track) + (2) a **small expert confirmation
cohort** (n = 5–8). Data acquisition is the shared track —
[`../_shared/real-data-acquisition-checklist.md`](../_shared/real-data-acquisition-checklist.md).
**No `outcome.md` until real annotated data + expert judgments land.**

## Data leg (shared i2b2/TAB)
- ☐ i2b2/n2c2 longitudinal notes with **coreference** annotations → FR-015 chains (clinical).
- ☐ TAB **quasi-identifier / indirect-identifier** annotations → FR-016 combinations (legal).
- ☐ Education/IRB de-id exemplars (where lawfully shareable) → the persona's named hard cases.
- ☐ Apply `coreference_slice` / `quasi_identifier_slice` logic to the **real** annotated corpora
  (chain-as-a-unit; ≥2-qid) → candidate detections (derived judgments only leave the DUA-host).

## Expert confirmation cohort (the human-judgment leg)
- ☐ **n = 5–8 expert de-id annotators**, spanning **clinical AND legal/education** de-id.
- ☐ Cohort criteria: publishes/practises PHI or legal de-id; **has annotated coreference or
  quasi-identifiers before**.
- ☐ **Exclusion:** general-NLP annotators without de-id/re-id experience (they would not reliably judge
  indirect-identification risk).
- ☐ Sample-size justification recorded: **inter-annotator-agreement saturation** (stable Krippendorff α
  at 5–8 for high-agreement expert judgment) — a *confirmation* cohort, not a discovery study.
- ☐ Channel: the de-id collaborator network (same as FR-027/§D); paid expert-annotation backfill
  (UserInterviews / Respondent) **screened HARD** to de-id-practitioner criteria; expert honorarium.

## Session (≈45 min, semi-structured + scored task)
- ☐ Framing (no real-PII; de-identified exemplars only).
- ☐ **Chain-as-a-unit task** — judge N real chains "detected as a unit / not"; compare to atomic-span scoring.
- ☐ **Qid-combination task** — flag which real ≥2-qid combinations carry re-identification risk; compare to the slice.
- ☐ Capture disagreements + rationales.

## Write-up
- ☐ Per-item/per-annotator: unit-vs-atomic agreement; qid-risk agreement; Krippendorff α; **n_real**
  (the low-power figure — likely small; report prominently).
- ☐ Write `outcome.md` (verdict per protocol §8; **low-power note retained**) + Status Change Log row;
  re-run `/dev-assist-testing` T6.

> Until then: status stays **PERSONA-CONDITIONAL**; the slices keep the non-strippable ~72%-formulaic
> low-power caveat; release stays **SHIP-WITH-CAVEATS**. No agent-generated coref/qid annotations
> substitute (REFUSED).
