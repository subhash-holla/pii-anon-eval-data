# Contributing to PII-Anon

Thank you for helping improve PII-Anon. This is a CC0 synthetic-PII benchmark with a pure-stdlib
evaluation harness; contributions are welcome under the rules below. Governance and conflict-of-interest
policy live in [GOVERNANCE.md](GOVERNANCE.md).

How to contribute: **fork** → create a **branch** → open a **pull request** against `main`. Every PR is
reviewed against the project's automated story/sprint review gates.

### 🌏 Extending language & dialect coverage (most-wanted)

No team can cover every language and dialect — the benchmark is designed to grow with the community.
If you want to add a new language or dialect (especially across Asia and the Global South), start here:

- **Guide:** [docs/contributing-languages.md](docs/contributing-languages.md) — the two contribution
  modes (language pack vs validated record batch), the BCP-47 dialect convention, and the quality bar.
- **What's most needed:** [docs/wanted-languages.md](docs/wanted-languages.md).
- **Propose one:** open the *Contribute a language or dialect* issue
  (`.github/ISSUE_TEMPLATE/language_contribution.yml`).
- **Self-check before a PR:** `python scripts/validate_contribution.py contrib/<bcp47-tag>/records.jsonl`
  (offset integrity, canonical enums, synthetic-only provenance, per-language coverage report).
- **Scaffold:** copy `contrib/TEMPLATE-language-pack/` to `contrib/<bcp47-tag>/`.

All language contributions follow the same non-negotiables below (CC0, 100% synthetic, declared provenance).

## Pull-request template

Open a PR using this template (also mirrored in `.github/PULL_REQUEST_TEMPLATE.md` when present). A PR
must check off:

- [ ] **What changed & why** — a clear summary; link any issue.
- [ ] **Traced requirement** — the FR/NFR (or roadmap item) this advances.
- [ ] **Tests added** — new/changed behavior is covered by tests; `python3 -m pytest` is green.
- [ ] **Provenance** — for any data: generator + seed + `source_type` declared (see below).
- [ ] **License compatibility** — confirmed CC0-compatible data / Apache-2.0 code (see below).
- [ ] **Docs** — README / TAXONOMY / DATASHEET / CHANGELOG updated if counts or behavior changed (the
      `tests/test_doc_drift.py` pins must stay green).

## License compatibility (CC0)

PII-Anon's **data is released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)** and
its **code under Apache-2.0**. Contributions must preserve this split:

- **Data contributions** must be **CC0-compatible**: original or public-domain-dedicated, *fully
  synthetic*, with no incompatible upstream license and no scraped or real personal data. If you cannot
  dedicate a data contribution to the public domain (CC0), it cannot be merged.
- **Code contributions** are accepted under **Apache-2.0**; do not add dependencies with incompatible
  licenses, and keep the scoring/stats/compliance core **pure-stdlib** (heavy deps stay behind extras).

## Provenance & synthetic-only

Every contributed record MUST be **synthetic** and carry declared **provenance** — the generator, the
seed, and a `provenance.source_type` (e.g. `synthetic_lattice_enrichment`, `template_expansion`). **No
real PII** may be contributed (AX-001): real personal information — even "anonymized" real data — is
out of scope and will be rejected. The benchmark's credibility depends on a 100%-synthetic, provenanced
corpus.

## Deprecation & erratum policy

We correct mistakes in the open rather than rewriting history:

- **Erratum.** A flawed record, metric, or published claim gets an **erratum** entry in `CHANGELOG.md`
  describing the error, its scope, and the correction. Prior version entries are preserved (they record
  what each release claimed).
- **Deprecation.** A field, metric, or API being removed is first marked **deprecated** for at least one
  minor release (with a migration note in `MIGRATION.md`) before removal, so downstream consumers have a
  window to adapt. Corpus or schema changes are reversible via the pinned `v1.3.0` /
  `pre-lattice-enrichment` tags.

## Versioning & releases

Releases follow **semantic versioning** and are **dated**:

- **MAJOR** — breaking schema / corpus / metric-semantics changes (carry a `MIGRATION.md` section).
- **MINOR** — backward-compatible additions (new scorers, exports, slices).
- **PATCH** — fixes, doc corrections, errata.

Each release is tagged and dated in `CHANGELOG.md`. Statistical-power and metric-family-separation
guarantees are part of the public contract — changing them is at least a MINOR (often MAJOR) release with
an explicit rationale.
