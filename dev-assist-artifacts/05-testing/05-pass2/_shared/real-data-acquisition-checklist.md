# Shared Real-Data Acquisition Checklist — i2b2/n2c2 + TAB (the de-id collaborator track)

**Stage 5 · Wave T5 (Pass-2) · SHARED acquisition checklist** · 2026-05-31
**Co-locates three Pass-2 items** that all depend on the SAME real-corpus acquisition + de-id
collaborator: **FR-027** (synthetic→real correlation), **FR-015/016** (real coreference/quasi-id
annotations), and **formulaic-distribution-shift** (real reference distributions). Acquire once; serve
all three.

> **NON-NEGOTIABLE (carried from every protocol preamble).** **No real PHI/PII ever enters this repo.**
> Only **derived, de-identified aggregates** (paired score matrices, feature histograms, chain/qid-level
> judgments — no note text, no spans, no values) leave the DUA-controlled host. Substituting an
> agent-simulated cohort or a synthetic "real" reference for any leg is a **CATASTROPHIC methodology
> violation** and is **REFUSED** (axiom AX-pii-anon-001 / AX-001). This checklist acquires the **real**
> licensed corpora; outcomes land **out-of-band** and only then is each item's `outcome.md` written.

This is a checklist, **not** evidence. Nothing here changes the SHIP-WITH-CAVEATS verdict. The verdict
moves only when real, derived results land in the per-item `outcome.md`.

---

## A. Corpora to acquire

| Corpus | Serves | License / gate | Status |
|---|---|---|---|
| **i2b2 / n2c2 2014 de-id** (1,304 clinical notes; PHI spans; longitudinal coreference) | FR-027 (clinical leg), FR-015 (coref), formulaic (clinical type-mix) | Harvard DBMI Data Portal **DUA**; named-PI; IRB or IRB-exempt determination | ☐ not started |
| **TAB — Text Anonymization Benchmark** (1,268 ECHR legal cases; quasi-/indirect-identifier annotations) | FR-027 (legal leg), FR-016 (quasi-id), formulaic (legal mix) | Open research license — **confirm derived-artifact publication compatibility** | ☐ not started |
| **Published PII/PHI distribution statistics** (i2b2/n2c2/OpenDeID papers, public frequency tables) | formulaic (reference prior where raw data is gated) | public, cite | ☐ not started |

## B. DUA / legal checklist (i2b2/n2c2)

- ☐ Identify the **named PI** who will hold the DUA (the de-id collaborator — see §D).
- ☐ Register at the Harvard DBMI Data Portal (`https://www.i2b2.org` / n2c2) and request the **2014 de-id** track.
- ☐ Execute the **Data Use Agreement** (institutional signature authority required).
- ☐ Obtain **IRB approval or IRB-exempt determination** (synthetic-benchmark correlation is typically
  exempt, but the determination must be on file before any real note is touched).
- ☐ Provision an **access-controlled host** for the real data (the "DUA-host"); real PHI **never** leaves it.
- ☐ Record the executed DUA + IRB determination references in the per-item `outcome.md` provenance (IDs only).

## C. TAB checklist

- ☐ Acquire TAB from the official release.
- ☐ **Confirm the license permits publishing derived artifacts** (feature histograms / aggregate score
  matrices / chain-level judgments). Record the license + the compatibility determination.
- ☐ Stage TAB on the same access-controlled host as i2b2 for a single derived-export pipeline.

## D. De-id collaborator (the channel — NOT a paid user panel)

The unlock the personas name is **"co-published with a recognized de-id group"** (reputational, WTP ≈ $0).

- ☐ Approach **ACL / EMNLP / PETS / JAMIA** de-id authors; the **n2c2** participant community; a
  **TAB-affiliated** lab; **Presidio / GLiNER-PII** maintainers (overlaps the design-real-user-trial channel).
- ☐ Secure a collaborator who **already holds (or can obtain) the i2b2/n2c2 DUA** and can run the real
  leg on the DUA-host.
- ☐ Agree the division of labor: who scores on the DUA-host, who exports the derived aggregates, who
  co-authors. Capture co-publication governance in [`../FR-027/copublication-terms.md`](../FR-027/copublication-terms.md).

## E. Derived-export discipline (what may leave the DUA-host — and nothing else)

| Item | Permitted derived export | FORBIDDEN |
|---|---|---|
| FR-027 | K-system × entity-type **aggregate score matrix** (recall@type) | note text, spans, values |
| FR-015/016 | **chain-level / qid-level judgments** (detected-as-unit y/n; risk y/n) + Krippendorff α | note text, the chains/qids themselves |
| formulaic | **feature histograms** (format-class counts, length bins, co-occurrence rates) | note text, raw values |

- ☐ Implement the derived-export as a script that runs **on the DUA-host** and emits only the table(s) above.
- ☐ Two-person review of every export before it leaves the host (no record-level data slips through).

## F. Hand-off to per-item execution

Once B–E are green, execute each item against its own plan and write its `outcome.md`:

- **FR-027** → freeze [`../FR-027/preregistration.md`](../FR-027/preregistration.md) (commit its hash
  **before** any real score), run `correlate(...)`, write `../FR-027/outcome.md`.
- **FR-015/016** → recruit the n=5–8 expert confirmation cohort
  ([`../FR-015-016/recruiting-checklist.md`](../FR-015-016/recruiting-checklist.md)), run the chain/qid
  tasks, write `../FR-015-016/outcome.md`.
- **formulaic** → freeze
  [`../formulaic-distribution-shift/analysis-plan.md`](../formulaic-distribution-shift/analysis-plan.md),
  compute divergence, write `../formulaic-distribution-shift/outcome.md`.

Then re-run `/dev-assist-testing` T6 to re-rule the release verdict toward SHIP.
