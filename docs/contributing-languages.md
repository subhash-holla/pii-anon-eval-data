# Extending PII-Anon-Eval with a new language or dialect

No single team can cover every language and dialect. PII-Anon-Eval is built to **grow with the
community** — especially across the languages, dialects, and scripts of Asia and the Global South that
production PII pipelines must serve. This guide is the pathway for contributing that coverage.

It builds on the general rules in [CONTRIBUTING.md](../CONTRIBUTING.md) and the integrity invariant in
[CLAIMS_POLICY.md](../CLAIMS_POLICY.md). **Read the non-negotiables first:**

> 🔒 **100% synthetic, CC0, no real PII (AX-001).** Every contributed record must be *synthetic* — no
> scraped data, no "anonymized" real data, no personal data of real people, even your own. Contributions
> are dedicated to the public domain (CC0 1.0). If you suspect a record contains **real** PII, do **not**
> paste it in an issue — report it privately via [SECURITY.md](../SECURITY.md) with only the `record_id`.

The most-needed languages, dialects, scripts, and entity types are listed in
[wanted-languages.md](wanted-languages.md). Pick from there, or propose your own.

---

## How languages & dialects are represented

| Field | Standard | Examples |
|---|---|---|
| `language` | **BCP-47** language tag (dialects are first-class) | `vi`, `ta`, `zh-Hant`, `zh-Hans`, `pt-BR`, `ar-EG`, `en-IN`, `es-MX` |
| `script` | **ISO 15924** script code | `Latn`, `Hans`, `Jpan`, `Kore`, `Arab`, `Deva`, `Taml`, `Thai`, `Cyrl` |
| `language_family` | free text | `Dravidian`, `Sinitic`, `Indo-Aryan`, `Austronesian` |

**Dialects** are expressed via BCP-47 region/variant subtags — e.g. Brazilian vs European Portuguese
(`pt-BR` / `pt-PT`), Egyptian vs Modern Standard Arabic (`ar-EG` / `ar`), Traditional vs Simplified
Chinese (`zh-Hant` / `zh-Hans`), Indian English (`en-IN`). Use the most specific tag that is *true* of
your records; don't tag `pt-BR` if the text isn't actually Brazilian.

---

## Two ways to contribute

### Mode A — Language pack (preferred: regenerable)

A **generation recipe** the maintainers wire into the synthetic generator so records can be regenerated
deterministically at any scale and re-balanced across the 7 evaluation dimensions. A pack contributes
*recipes*, not raw records:

- **value generators / gazetteers** for the language: synthetic name lists, address formats, phone/ID
  formats, organization names, etc. (public-domain or original; never a real directory of real people);
- **document templates** in the target language (the carrier text PII is embedded in);
- a **`language-pack.yaml`** manifest (see `contrib/TEMPLATE-language-pack/`).

Use Mode A when you can describe *how to generate* the language. It scales and stays balanced.

### Mode B — Validated synthetic record batch (fastest to start)

A `.jsonl(.gz)` of synthetic records that already conform to the schema and pass the validator. Use Mode
B for a quick first contribution, a dialect probe, or when a recipe is impractical. Maintainers may later
back-port a Mode-B batch into a Mode-A pack.

Both modes ship in `contrib/<your-language>/` and are reviewed the same way.

---

## The record format (Mode B / pack samples)

Each line is one record matching `src/pii_anon_datasets/data/pii_anon.schema.json`. Minimum required:

```jsonc
{
  "record_id": "<UUID>",                 // uuid5; maintainers can re-mint — see README in the template
  "text": "…source text containing synthetic PII…",
  "version": "2.0.0",
  "language": "ta",                      // BCP-47 (use ta-IN, ta-LK for dialects)
  "script": "Taml",                      // ISO 15924
  "language_family": "Dravidian",
  "domain": "general",                   // general|clinical|financial|legal|technology|government|education|mixed
  "data_type": "unstructured_text",
  "primary_dimension": "multilingual",
  "dimensions": ["multilingual", "diverse_pii_types"],
  "difficulty_level": "moderate",
  "annotations": [
    { "entity_id": "e0", "entity_type": "PERSON_NAME", "start": 9, "end": 20,
      "text": "<must equal record.text[start:end]>",
      "category": "identity_demographics", "sensitivity_class": "direct_identifier" }
  ],
  "provenance": { "source_type": "synthetic", "license": "CC0-1.0",
                  "generation_seed": 12345, "native_speaker_reviewed": true }
}
```

**Hard invariants the validator enforces** (a single failure blocks merge):
- **Offset integrity:** `record.text[start:end] == annotation.text` for every span (the dataset's
  *0-offset-errors* promise). Offsets are **code-point** indices — mind combining marks in Indic/Arabic
  scripts.
- **Canonical enums:** `entity_type`, `category`, `sensitivity_class` from the schema (90+ entity types).
- **Synthetic provenance:** `provenance.source_type ∈ {synthetic, curated_public}` + a CC0-compatible
  `license`.
- No duplicate `record_id`s; no overlapping spans within a record; ≥1 annotation.

See a working two-record example in `contrib/TEMPLATE-language-pack/records.sample.jsonl`.

---

## Quality bar

- **Native-speaker review** is strongly encouraged — set `native_speaker_reviewed: true` and say who in
  the PR. Machine-translated carrier text without review is the most common rejection reason.
- **Powered coverage:** aim for **≥ 100 records per language** (and ideally ≥ 30 per
  language × evaluation-dimension cell) so per-language metrics carry usable confidence intervals.
  Smaller "coverage probes" are welcome too — they're merged as *underpowered* and flagged as such.
- **Entity & script realism:** names, IDs, addresses, and phone formats should match how PII actually
  appears in that locale (e.g. Aadhaar-shaped IDs for `en-IN`/`hi`, not SSN-shaped).
- **Diversity:** vary `domain`, `difficulty_level`, and `dimensions`; don't ship 200 copies of one
  template with the names swapped.

---

## Step-by-step

1. **Open an issue** with the *"Contribute a language or dialect"* template (`.github/ISSUE_TEMPLATE/
   language_contribution.yml`) — declares the BCP-47 tag, script, dialect, native-speaker availability,
   and mode. This avoids duplicate effort and lets maintainers point you at gazetteer/format conventions.
2. **Fork → branch → add** your records/pack under `contrib/<bcp47-tag>/`. Copy
   `contrib/TEMPLATE-language-pack/` as a starting point.
3. **Validate locally** (must pass):
   ```bash
   python scripts/validate_contribution.py contrib/<bcp47-tag>/records.jsonl
   ```
   Paste the validator's PASS output into your PR.
4. **Open a PR** with the project PR checklist (`.github/PULL_REQUEST_TEMPLATE.md`) — confirm CC0 +
   synthetic-only + provenance + native-speaker review.
5. **Review** runs the validator in CI and a maintainer checks linguistic realism + integrity
   ([GOVERNANCE.md](../GOVERNANCE.md)). On merge, maintainers integrate the pack, **regenerate** the
   affected splits, rerun `scripts/validate.py`, update the datasheet/changelog counts, and **version-bump**
   (a new language is a minor release).

Your contribution is credited in the changelog and the dataset card. Thank you for making the benchmark
*actually* global.

---

_This community-extension pathway is itself part of the dataset's long-term **maintenance plan** (NeurIPS
Datasets & Benchmarks / datasheet "Maintenance"): the benchmark is designed to grow its language and
dialect coverage through community contribution, under a fixed synthetic-only / CC0 integrity bar._
