# Language-pack template

Copy this folder to `contrib/<bcp47-tag>/` (e.g. `contrib/ta-IN/`) and use it as the starting point for a
new-language/dialect contribution. Full instructions: [`docs/contributing-languages.md`](../../docs/contributing-languages.md).

```
contrib/<bcp47-tag>/
├── language-pack.yaml        # manifest (who/what/license/coverage)  — fill this in
├── records.sample.jsonl      # your synthetic records (rename/extend; .jsonl or .jsonl.gz)
└── README.md                 # (optional) notes on your locale's PII realities
```

## Quick start

1. Fill in `language-pack.yaml` (BCP-47 tag, script, contributor, synthetic-only + CC0 attestation, coverage).
2. Put your synthetic records in `records.sample.jsonl` — one JSON record per line, matching
   `src/pii_anon_datasets/data/pii_anon.schema.json`. The two-line sample shipped here is a valid example.
3. Validate (must PASS — paste the output into your PR):
   ```bash
   python scripts/validate_contribution.py contrib/<bcp47-tag>/records.sample.jsonl
   ```

## The one rule that trips people up

**Offsets are code-point indices and `text[start:end]` must equal `annotation.text` exactly.** In
Indic/Arabic/Thai scripts, combining marks count as separate code points — if you author by hand, the
validator will catch a mismatch. The easiest way to get offsets right is to build records
programmatically (find the substring → its start/end), as the maintainers do.

## record_id

Each `record_id` is a UUIDv5. If you don't mint one, the maintainers will re-mint deterministically on
integration — but a placeholder UUID must still be a valid `8-4-4-4-12` hex string for the validator to
pass (the sample uses one).

🔒 Synthetic-only, CC0, no real PII — see [`docs/contributing-languages.md`](../../docs/contributing-languages.md).
