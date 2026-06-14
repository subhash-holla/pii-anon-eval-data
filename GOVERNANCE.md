# Governance

This document is the governance charter for **PII-Anon** — a CC0 synthetic-PII benchmark dataset and
pure-stdlib evaluation harness. It exists so that the benchmark's neutrality is auditable: anyone can see
how decisions are made, who maintains the project, where the conflicts of interest are, and what controls
keep the leaderboard honest.

> **Honesty note.** Parts of this charter describe an *intended* governance structure that is not yet
> staffed by real people. Those parts are explicitly flagged **AGENT_SIMULATED / aspirational** below. We
> would rather state the project's real (small) size plainly than imply an organization that does not yet
> exist.

## Charter & mission

**Mission.** Provide a credible, statistically-grounded, fully-synthetic benchmark for PII **detection**,
**anonymization**, **pseudonymization-integrity**, and **measured re-identification** — one that no single
vendor's tool is privileged by, and whose every published number carries its uncertainty and its
synthetic-distribution caveat.

**Scope.** The project maintains: the CC0 corpus + slices; the v2.0.0 schema + migration; the scoring /
statistics / reporting harness; the compliance crosswalk + DPIA-input bundle; the distribution exports
(Parquet / Croissant / spaCy / CoNLL + dataset card); and the leaderboard + governance seam. The data is
**CC0**; the code is **Apache-2.0**.

## Decision-making process

- **Routine changes** (bug fixes, new scorers, doc updates) are decided by the maintainer(s) via the
  normal pull-request review described in [CONTRIBUTING.md](CONTRIBUTING.md), with the automated
  story/sprint review gates as the quality bar.
- **Substantive changes** (corpus regeneration, schema breaks, power-ladder changes, metric-family
  semantics, leaderboard policy) require: a written proposal, a deprecation/erratum entry where relevant,
  and — once the advisory body below is real — advisory review. Until then they are decided by the
  maintainer in the open (public PR + rationale), and are reversible via the pinned `v1.3.0` /
  `pre-lattice-enrichment` tags.
- **Releases** are semantically versioned and dated (see [CONTRIBUTING.md](CONTRIBUTING.md#versioning)).

## Advisory body

> **Status: ASPIRATIONAL / AGENT_SIMULATED.** The project does **not** yet have a staffed advisory board.
> This section lists the *roles* the project intends to fill, not real members. No advisory member is
> named here because none exists yet — naming fictitious advisors would itself be a governance failure.

The intended advisory roster (to be filled as the project grows) covers these independent perspectives:

| Seat | Perspective it represents |
|---|---|
| Academic de-identification researcher | external-validity, methodology rigour |
| Enterprise privacy engineer | real-world deployment realism |
| Legal / DPO reviewer | regulatory-crosswalk soundness (no over-claiming) |
| ML/NLP evaluation methodologist | statistical-power + leaderboard integrity |
| Community / OSS representative | contributor fairness, license hygiene |

Advisory seats, once filled, are explicitly **not** held by `pii-anon-core` (see Conflict of interest).

## Conflict of interest

The project is currently maintained under the **`pii-anon-core`** affiliation. This is the project's
central conflict of interest and it is stated plainly:

- **Leaderboard recusal.** A submitter who is a project **maintainer** or is **`pii-anon-core`-affiliated**
  is flagged for **recusal** — they cannot self-adjudicate or privilege their own leaderboard entry. This
  is enforced in code by `pii_anon_datasets.leaderboard.CoIRecord.requires_recusal` (which flags
  maintainer / `pii-anon-core` affiliations) together with the append-only, hash-chained held-out store
  (`pii_anon_datasets.leaderboard.LeaderboardStore`, `verify_chain`).
- **No pre-publication access.** Every submission carries a **non-strippable attestation** of no
  pre-publication access to the held-out evaluation set (`CoIRecord` / `NO_PREPUB_ATTESTATION`); the
  held-out gold labels are **never distributed** and are structurally excluded from the store.
- **Advisory independence.** Advisory seats (once real) are held by people **not** affiliated with
  `pii-anon-core`.

## Bus factor & succession

**Bus factor = 1.** This is an honest statement: the project currently has a **single maintainer**. That
is a real risk, and we do not hide it behind an org chart.

Succession is protected structurally rather than organizationally: the **data is CC0** and the **code is
Apache-2.0**, every release is **tagged and dated**, the corpus + lattice are **content-addressed and
frozen** (`v1.3.0`, `pre-lattice-enrichment` tags), and the evaluation harness is **pure-stdlib** with no
hosted-service dependency. If the maintainer disappears, anyone can fork the repository, reproduce the
corpus from the pinned snapshot, and continue the project without permission. Standing up the advisory
body above is the intended path to a bus factor greater than 1.

## Neutrality controls (the leaderboard governance seam)

The leaderboard is a **governance seam**, not a hosted service in v1. Its neutrality rests on auditable,
pure-stdlib controls:

- **Held-out store** — append-only, content-hash-chained event log; `verify_chain()` makes tampering
  evident; the held-out **gold is never stored** (forbidden-key reject).
- **Opt-in publish + anti-gaming** — a submission is published only on explicit opt-in; rate-limiting,
  held-out **rotation epochs**, and a contamination/duplicate check are enforced
  (`pii_anon_datasets.leaderboard.policy`).
- **Conflict-of-interest recusal** — as above.

All of these are inspectable in the open-source code and pinned by the test suite, so the governance
claims in this document are continuously verified, not merely asserted.
