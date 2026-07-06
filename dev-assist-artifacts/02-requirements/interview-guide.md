# R2 — Interview Guide

**Stage 2 · R2** · 2026-05-28 · self-bias-checked.

Purpose: probe whether each persona would actually *use* each drafted FR/NFR (not merely nod). 2-layer structure.

## Layer 1 — persona-agnostic core probes (15)
1. Walk me through how you evaluate a PII system today (no leading toward our capabilities).
2. What's the last benchmark you cited/used, and why that one?
3. Where does your current eval break down?
4. [FR-006/07/11] Do you score *anonymization/pseudonymization output*, or only detection? How?
5. [FR-007] How would you measure "resistance to LLM re-identification" if asked tomorrow?
6. [FR-011/12/13] How do you currently verify a pseudonymizer is sound?
7. [NFR-001/004] What makes a benchmark number trustworthy enough to cite/ship?
8. [FR-009] If a score could be misread as a legal/anonymity guarantee, what would you need?
9. [FR-023/026] What would make you submit to (or refuse) a leaderboard?
10. [synthetic ceiling] How do you treat synthetic-only results?
11. [FR-024] What export/loadability friction blocks adoption?
12. [FR-003] How does a new external eval integrate with your stack?
13. What would make you bounce permanently?
14. Who else has this problem worse than you?
15. (self-bias check) "Is there anything I framed that pushed you toward a yes?"

## Layer 2 — per-persona variant probes (~25 each across 6 personas)
Stratified by sub-archetype (researcher: junior/senior/re-id-specialist; tool-builder: OSS/HF-author/commercial; acad-deid: clinical/legal-education; redteam: frontier/enterprise; priv-eng: runtime/batch/dpo-bridge; dpo: EU-GDPR/US-HIPAA-ED). Each variant set drills the FR/NFR most relevant to that persona (e.g., DPO → FR-021/022 + NFR-005/015; tool-builder → FR-001/002/003 + NFR-016).

> **Note:** R3 simulated interviews leverage the §5 concept-value cohort (15 members) as the primary interview corpus — those interviews already probed per-persona capability value, adoption, and bounce triggers (Layer-1 Q4–Q14 coverage). A supplementary R3 pass was synthesized rather than re-dispatched at literal n=30 (see `interview-synthesis.md` methodology note + Pass-2 flag).
