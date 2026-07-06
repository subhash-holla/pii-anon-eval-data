# Co-Publication Governance Terms — FR-027

**Stage 5 · Wave T5 (Pass-2) · governance terms** · 2026-05-31 · filled 2026-06-17
**Status: TEMPLATE FILLED — awaiting named collaborator.** FR-027 explicitly requires these terms
be **recorded** before the real run (protocol §5).  Fill the collaborator-specific fields when a
de-id group confirms participation; reference this document from `outcome.md`.  The incentive is
**reputational** (co-authorship / citation), not cash (WTP ≈ $0 across personas).

---

## 1. Parties

- **PII-Anon maintainer:** Subhash Holla (maintainer, corresponding author for the PII-Anon-Eval
  dataset and paper).
- **De-id collaborator / DUA holder:** _[To be filled at time of engagement — must be a recognized
  clinical or legal de-identification group with an existing i2b2/n2c2 DUA or TAB affiliation.
  Candidate groups include: n2c2/DBMI collaborators (Harvard DBMI), TAB-affiliated NLP labs
  (University of Oslo / ECHR dataset authors), and NLP groups with published clinical de-id systems
  (ACL/EMNLP/JAMIA de-id track authors, Presidio/GLiNER maintainers who also hold real-data
  access).]_

---

## 2. Data-handling responsibilities

- **Who runs the real leg on the DUA-host:** the de-id collaborator (the DUA holder), on a
  compute environment that has executed the i2b2/n2c2 Data Use Agreement and any required IRB
  or IRB-exempt determination.  The PII-Anon maintainer does **not** access real PHI or raw
  ECHR case text.
- **What leaves the DUA-host:** ONLY the derived aggregate score matrix — K × entity-type
  recall/precision cells (integer counts: TP, FP, FN per cell), no note text, no span values,
  no individual patient/case records.  Row-level granularity is **not exported**; only
  corpus-level aggregates per (system, entity-type) cell.
- **Two-person export review:** the derived score matrix export requires sign-off by two named
  individuals (one from the collaborator institution, one from the PII-Anon team) confirming that
  no raw PHI or span text is included.  Names to be recorded in `outcome.md`.
- **AX-pii-anon-001 confirmation:** real PHI never enters the PII-Anon repository.  The
  `src/pii_anon_datasets/validation/correlation.py::correlate()` function accepts only the
  aggregate score matrix; it never ingests raw text.
  - [ ] Confirmed by collaborator at export time (record date and names in `outcome.md`)

---

## 3. Authorship and credit

- **Authorship:** the de-id collaborator group is listed as co-author(s) on any publication that
  includes the real-data correlation results.  Specific author order is negotiated at engagement
  time and documented in the version of this file that corresponds to the `outcome.md` hash.
- **CRediT contributorship statement:**
  - PII-Anon maintainer: Conceptualization, Data curation (synthetic corpus), Software, Formal
    analysis, Writing – original draft.
  - De-id collaborator: Data curation (real corpus, DUA-host), Investigation (real-data scoring),
    Validation, Writing – review & editing.
- **Acknowledgement of corpora per their citation requirements:**
  - i2b2/n2c2 2014 de-identification dataset: cite per Harvard DBMI / n2c2 portal requirements
    (specific citation to be confirmed at DUA execution; typically the 2014 Shared Task overview
    paper by Stubbs & Uzuner).
  - TAB — Text Anonymization Benchmark: cite Pilan et al. (2022) per the TAB release terms.

---

## 4. Embargo and publication

- **Embargo window:** derived results (the aggregate score matrix and the `CorrelationResult`
  object) are embargoed until the associated paper is **accepted** at the target venue.  No
  pre-publication disclosure of numeric correlation results outside the collaboration.
- **Target venue(s):** a peer-reviewed NLP or medical informatics venue where PII/de-identification
  benchmark work is recognized — e.g., ACL, EMNLP, NAACL, PETS, JAMIA, or the NeurIPS Datasets
  and Benchmarks track.  Final venue selection is a joint decision; the pre-registration
  (§6) commits the statistical plan regardless of venue.
- **Preprint policy:** a preprint (e.g. arXiv) may be posted at submission; both parties must
  approve the preprint text and the phrasing of the external-validity claim before posting.

---

## 5. Non-strippable framing (mandatory)

All published materials that include FR-027 correlation results **must** carry the following
framing.  This is not negotiable and is a condition of co-publication.

1. The paper **must state explicitly** that PII-Anon remains a **synthetic** benchmark; the
   correlation measures whether synthetic-distribution detector rankings track real-corpus
   rankings on the domain-matched English slice — it does **not** make PII-Anon records real
   data, does not constitute a GDPR/HIPAA certification, and does not generalize beyond the
   paired entity-type set and the English clinical/legal domains tested.

2. Every figure, table, or inline number that reports the FR-027 correlation result **must**
   carry the `CORRELATION_CAVEAT` text that `correlate()` self-attaches to the
   `CorrelationResult` object.  This caveat may not be truncated or omitted from any published
   display.

3. The per-cell leaderboard numbers (detection F2, recall, precision) continue to carry the
   AX-001 synthetic-only caveat regardless of the FR-027 verdict.  A REAL_USER_VALIDATED
   verdict lifts the synthetic-only **citation ceiling** for the correlated types and domains
   only; it does not change the per-cell label from "synthetic" to "real".

---

## 6. Conflict-of-interest

- Any maintainer or collaborator who is also an author or contributor of a system in the
  K-list (e.g. Presidio, GLiNER, scrubadub, cloud DLP APIs) must declare that CoI in the
  paper's author contribution and conflict-of-interest statement.
- The relevant recusal recorded here: the scoring of the CoI'd system(s) is conducted by a
  collaborator who has no authorship interest in those systems (mirroring the `gov-03
  CoIRecord` discipline).  Specific declarations to be filled at engagement time and
  recorded in the version of this file referenced from `outcome.md`.
