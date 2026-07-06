# Train/test contamination & near-duplicate leakage audit

Train: **402,634** records (402,634 distinct texts). Test: **115,618** records. Read-only over the published Parquet; no detector runs.

| Axis | Test records matched in train | % of test |
|---|---:|---:|
| **Exact-text overlap** (verbatim text in train) | 0 | **0.00%** |
| **Template-skeleton overlap** (PII-redacted structure in train) | 22,386 | **19.36%** |
| Intra-test exact duplicate texts | — | 0.00% |

## Interpretation (the honest framing)

- **Exact-text leakage is 0.00%** — negligible; test texts are not verbatim copies of train.
- **Template-skeleton overlap is 19.36%.** This is EXPECTED for a templated synthetic corpus and is **NOT label leakage**: the detection task is recovering the *unseen PII values*, which are regenerated per record even when the surrounding template is shared. The defensible claim is: "0.0% verbatim duplication; 19% shared template structure by design, disclosed" — never "0 contamination".
- A harder *novel-template* test slice (test skeletons NOT present in train) can be carved from this audit if a reviewer wants a leakage-free subset.

_Method: exact = sha1(text) set-membership train↔test; skeleton = sha1 of text with every gold span replaced by its entity-type tag (left-to-right, overlaps skipped). AX-001: synthetic-only — this measures internal corpus structure, not real-world generalization._
