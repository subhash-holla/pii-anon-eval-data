# CAP-02 operating-point re-elicitation — pre-registered real-user instrument (HUMAN-ONLY)

**Status:** `AGENT_SIMULATED` (permanent until real P-priv-eng + P-dpo participants run this).
**Why human-only:** DC-27 / FR-048 committed β=2 and recall_target=0.90 as *R10-to-confirm* defaults; the
MEDIUM personas that own this bundle (P-priv-eng, P-dpo) were unseated at the R6 survey. The numbers are
defensible from INT-04 ("34k FPs / 10k entities", 3× license cost) but rest on a SIMULATED panel. This is the
highest-priority Pass-2 re-elicitation (Design D5). **Do NOT write `outcome.md` from a simulated cohort** — that
is a CATASTROPHIC methodology violation the protocol refuses.

## What shipped this session (closes the code side)
The operating-point machinery is built + verified end-to-end on real detectors (C4): recall-priority Fβ (β
recorded, ≥2), threshold-free AUPRC, precision-at-fixed-recall, and the op-point == pre-registered-threshold
gate (`report.build_operating_point_view`; `stats/operating_point.py`). β and recall_target are **parameters**
(`run_assessment(beta=…, recall_target=…)` / prereg `design_point`), so a re-elicited value is a config change,
not a rebuild.

## Recruitment (n = 8–12; 2–3 per sub-archetype)
- **P-priv-eng** (runtime privacy engineers who own the false-positive tax): in-house de-id pipeline owners,
  CISO-adjacent.
- **P-dpo** (data protection officers / compliance): GDPR/HIPAA accountable owners.
- Screen out anyone with a system in any leaderboard (governance recusal, FR-052).

## Pre-registered protocol (fix BEFORE recruiting; no post-hoc re-analysis)
1. **Artifact walkthrough** — show the real-systems operating-point table (Presidio/GLiNER/Piiranha
   precision/recall/Fβ/AUPRC from the C4 run) WITHOUT a recommended β.
2. **Cost elicitation** — elicit each participant's de-id FN:FP cost asymmetry as a stated integer ratio
   ("a missed SSN costs N times a false redaction"); record N per participant.
3. **Recall-target elicitation** — "at what recall do you operate / would you accept a vendor at?" (free
   response, then a 0.80–0.99 slider).
4. **β confirmation** — derive β from the elicited FN:FP ratio (β ≈ √ratio) and ask the participant to confirm
   or adjust the resulting Fβ weighting against examples.

## Pre-registered analysis + verdict mapping
- Aggregate the elicited (FN:FP ratio, recall_target) per persona; report median + range.
- **CONFIRMED** — committed defaults (β=2, recall_target=0.90) fall within the elicited inter-quartile range for
  both personas → keep; mark DC-27 REAL_USER_VALIDATED.
- **REVISE** — defaults outside the IQR → adopt the elicited median, update `configs/assessment.yaml`
  `operating_point`, re-run the assessment (it is parameterized), record the change.
- **PERSONA-STRATIFIED** — P-priv-eng and P-dpo diverge materially → report BOTH operating points (the families
  are already separate; never average them).
- **INSUFFICIENT_EVIDENCE** — < 8 real participants recruited within the window → stays AGENT_SIMULATED.

Record the outcome in `outcome.md`; re-run `/dev-assist-testing` to re-rule DC-27 / NFR-046.
