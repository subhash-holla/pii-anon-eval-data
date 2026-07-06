# FR-027 real-data correlation — path-activated ingest (HUMAN-ONLY: DUA + data drop)

**Status:** `RealDataAbsent` (permanent until a DUA-holding collaborator drops real derived scores).
**Why human-only:** the i2b2-2014 / n2c2 and TAB corpora require a signed Data Use Agreement; raw PHI must
never enter this repo. The agent cannot sign a DUA or acquire the data, and the protocol REFUSES a fabricated
correlation. This session wired the *activation seam* so the moment a collaborator drops a **derived** score
file, the audited correlation runs with no further code change.

## What shipped this session (closes the code side)
- `src/pii_anon_datasets/validation/real_data_ingest.py` — `correlate_from_path()` returns the
  `RealDataAbsent` sentinel **unless** a real-data score file exists at the configured path; then it runs the
  audited `validation/correlation.py::correlate` (Kendall τ-b + Spearman ρ + seeded bootstrap CI + Bland-Altman).
  Malformed / unequal-length / under-length payloads **raise** — never padded or fabricated.
  (test: `tests/test_real_data_ingest.py`.)

## The drop protocol (for the DUA-holding collaborator, out-of-band)
1. Sign the i2b2-2014 / n2c2 DUA and/or obtain TAB; see `copublication-terms.md` + `recruiting-checklist.md`.
2. On the secure host where the real data lives, run BOTH systems (the synthetic-trained detector and the same
   detector on the real corpus) and export ONLY the **derived per-cell scores** — never spans, never text.
3. Write a JSON file with equal-length paired arrays (no raw PHI):
   ```json
   { "synthetic": [0.91, 0.62, ...], "real": [0.88, 0.59, ...] }
   ```
4. Drop it at a path on the maintainer's machine and point the harness at it:
   ```bash
   export PII_ANON_REAL_DEID_PATH=/secure/derived/i2b2_2014_scorepairs.json
   PYTHONPATH=src python -c "from pii_anon_datasets.validation import real_data_ingest as R; \
     r = R.correlate_from_path(seed=20260531); \
     print(type(r).__name__, getattr(r, 'kendall_tau', None), getattr(r, 'tau_ci', None))"
   # RealDataAbsent  -> still absent; CorrelationResult <tau> <ci> -> the real correlation ran
   ```
5. Compare τ-b CI lower bound to the pre-registered floor in `preregistration.md §verdict`; record the outcome
   in `05-pass2/FR-027/outcome.md`; re-run `/dev-assist-testing` T6.

## Honesty boundary (permanent AX-001 interaction)
The real-data correlation **bounds** the synthetic-only external-validity gap empirically; it does NOT remove
the AX-001 synthetic-only invariant (every per-cell metric still carries the non-strippable caveat). A high τ-b
tightens the citation ceiling; it never makes the synthetic corpus "real". `correlate()` returns
`RealDataAbsent` until step 4 lands — no simulated cohort, no agent-env number, ever (CATASTROPHIC if violated).
