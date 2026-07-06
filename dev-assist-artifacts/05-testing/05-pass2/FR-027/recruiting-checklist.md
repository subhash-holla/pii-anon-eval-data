# Recruiting / Acquisition Checklist — FR-027

**Stage 5 · Wave T5 (Pass-2)** · 2026-05-31 · filled 2026-06-17 · companion to [`protocol.md`](protocol.md).
FR-027 needs a **real-data-holding collaborator**, not a paid user panel.  Data acquisition is the
**shared** i2b2/TAB track — see [`../_shared/real-data-acquisition-checklist.md`](../_shared/real-data-acquisition-checklist.md).
**No `outcome.md` until real, derived results land.**

> **No agent-simulated cohort substitutes for this protocol.**  Substituting agent-generated
> correlation scores for the licensed real-data run is a CATASTROPHIC methodology violation and is
> REFUSED.  The v1 harness returns the `RealDataAbsent` sentinel until a real run is executed.

---

## Collaborator contacts and engagement tracking

### i2b2 / n2c2 track (clinical English, Harvard DBMI)

| Contact point | Details | Status |
|---|---|---|
| **n2c2 Data Portal** | https://n2c2.dbmi.hms.harvard.edu/ — the primary portal for requesting the i2b2-2014 de-identification dataset (1,304 annotated clinical notes). The DUA is administered through the Harvard DBMI portal. | Not yet submitted |
| **DBMI contact** | Contact via the n2c2 portal request form; for collaboration enquiries, the n2c2 mailing list and shared-task organiser contact addresses are the entry point. | Not yet contacted |
| **Potential collaborating groups** | NLP groups with published n2c2/i2b2 shared-task participation (e.g. 2014 de-id track participants listed in the Stubbs & Uzuner 2015 overview paper); clinical NLP labs at Stanford BMIR, MIT Clinical NLP, UMass BioNLP, i2b2-affiliated institutions. | Candidates identified; not yet approached |
| **DUA status** | Requires a named-PI Data Use Agreement; IRB or IRB-exempt determination from the collaborator's institution. | Not executed |

### TAB track (legal English, ECHR annotations)

| Contact point | Details | Status |
|---|---|---|
| **TAB dataset** | Pilan et al. (2022) "The Text Anonymization Benchmark (TAB)" — freely available for research use. Official release at the NLPLab Oslo GitHub / ACL Anthology. | License confirmed as research-use; not yet acquired locally |
| **TAB authors** | University of Oslo NLP Group (Lilja Øvrelid, Ildikó Pilán, et al.); contact via the ACL Anthology paper contact or the NLPLab Oslo institutional email. | Not yet contacted |
| **License compatibility** | TAB derived-score publication: confirm explicitly that publishing K × entity-type aggregate recall matrices (no ECHR case text) is within the research-use terms. | Not yet confirmed with authors |

### Overlap with leaderboard detector communities

The following communities overlap with the FR-027 run and may have both detector expertise and
real-data access, making them natural co-collaboration candidates:

| Community | Relevance | Status |
|---|---|---|
| Presidio maintainers (Microsoft OSS) | Presidio is detector #5 in the K-list; the team has clinical NLP connections | Not yet contacted |
| GLiNER maintainers (urchade) | GLiNER is detector #2; co-authorship would add NER expertise | Not yet contacted |
| Piiranha maintainers (iiiorg) | Piiranha is detector #7; smaller lab, potentially open to collaboration | Not yet contacted |
| ACL/EMNLP de-id paper authors (2022–2025) | Clinical and legal NLP authors with real-data experience | Survey planned; not started |

---

## Engagement tracking

| Collaborator / group | First contact date | Response | DUA status | Go/No-go |
|---|---|---|---|---|
| _[to be filled at outreach]_ | — | — | — | — |

---

## Pre-run gates (must all be checked before the real run)

- [ ] Shared real-data acquisition checklist A–E complete:
  - [ ] A. i2b2/n2c2 2014 DUA executed (named PI, Harvard DBMI portal)
  - [ ] B. IRB or IRB-exempt determination from collaborator's institution
  - [ ] C. TAB license compatibility confirmed for derived-aggregate publication
  - [ ] D. DUA-host compute environment established (access-controlled; real PHI never leaves)
  - [ ] E. Derived-aggregate export pipeline tested on synthetic data (no raw text egress)
- [ ] [`copublication-terms.md`](copublication-terms.md) filled with named collaborator + signed (or confirmed via email chain archived in `outcome.md`)
- [ ] [`preregistration.md`](preregistration.md) frozen — committed to git with content hash recorded — **BEFORE any real score is computed**
- [ ] K-list confirmed unchanged from v2.1.0 tag (no new detectors added post-freeze)

---

## Run and write-up

- [ ] Score the K=11 systems on the PII-Anon synthetic domain-matched English slice (in-repo, reproducible via `results/baselines/tier1-en-all/baseline_results.json` + the domain-match slice query from `preregistration.md §3`).
- [ ] Score the same K=11 on i2b2-2014 + TAB on the DUA-host; export only the derived aggregate score matrix (TP/FP/FN per (system, entity-type) cell; no note text, no span values).
- [ ] Run `correlate(synthetic_scores, real_scores, seed=20260603)` → capture `CorrelationResult` verbatim (τ-b, ρ, seeded bootstrap CIs, Bland-Altman; run i2b2, TAB, and pooled as pre-registered).
- [ ] Confirm results reproduce byte-identically (AX-002) by re-running with the same seed on a clean environment.
- [ ] Write `outcome.md` (τ-b/ρ + CIs per corpus and pooled, Bland-Altman mean diff + limits, verdict per protocol §8) and append the traceability Status Change Log row to `02-requirements/traceability-matrix.md`.
- [ ] Re-run `/dev-assist-testing` T6 to update the release-readiness report.

---

## Current status

Status stays **PERSONA-CONDITIONAL**; `RealDataAbsent` remains the shipped truth; release stays
**SHIP-WITH-CAVEATS** (Caveat AX-001 + pending FR-027).  No agent-simulated cohort substitutes
(REFUSED — see protocol §2 and the harness enforcement in
`src/pii_anon_datasets/validation/correlation.py`).
