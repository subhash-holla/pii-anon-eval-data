# PII-Anon — HUMAN-ONLY TODO to reach unconditional SHIP (both cycles)

Every CODE-achievable caveat is closed (strict TDD, committed). What remains needs a real external resource an
agent cannot obtain or simulate. Each item below is **scaffolded in code + has an exact command/artifact**; the
honesty sentinels (`RealDataAbsent` / `INSUFFICIENT_EVIDENCE` / `AGENT_SIMULATED`) are held until a human runs it.
**Never** substitute a simulated cohort, an agent-env number, or a fabricated DOI — the protocols REFUSE it.

Caveat legend: 🔒 **permanent-by-design** (cannot be removed, only bounded) · ⏳ **pending-external** (closes on
the human step) · ✅ **closed this session**.

---

## 🔒 1. Synthetic-only external validity (AX-001) — PERMANENT
Cannot be removed. It rides every per-cell metric and figure forever. It can only be **empirically BOUNDED** by
item 2. Even the real-detector leaderboard is "real-systems on SYNTHETIC data." Nothing to do — keep the caveat.

## ⏳ 2. Real-data correlation slice (FR-027) — bounds caveat 1
**Resource:** a signed i2b2-2014 / n2c2 (and/or TAB) Data Use Agreement + a de-id collaborator. Raw PHI never
enters the repo — only DERIVED paired scores.
**Steps:**
1. Sign the DUA (see `05-pass2/FR-027/copublication-terms.md` + `recruiting-checklist.md`).
2. On the secure host, run the synthetic-trained detector AND the same detector on the real corpus; export the
   DERIVED paired per-cell scores as `{"synthetic": [...], "real": [...]}` (equal length).
3. ```bash
   export PII_ANON_REAL_DEID_PATH=/secure/derived/i2b2_2014_scorepairs.json
   PYTHONPATH=src python -c "from pii_anon_datasets.validation import real_data_ingest as R; \
     print(R.correlate_from_path(seed=20260531))"   # RealDataAbsent -> CorrelationResult when present
   ```
4. Record τ-b + CI vs the pre-registered floor (`05-pass2/FR-027/preregistration.md`) → `outcome.md`; re-run T6.
**Closes:** bounds AX-001; retires the "not citable as a standalone recall claim" ceiling.

## ⏳ 3. Reference-host throughput (NFR-010b)
**Resource:** a declared **8-core** reference host (8 physical cores ≥3.0GHz, 32GB, isolated).
**Step (on that host, from the eval-data repo root):**
```bash
./scripts/run_throughput_benchmark.sh nfr010-refhost.json \
  --reference-host "8-core x86_64 @ ≥3.0GHz, 32GB, isolated, single NUMA node"
# prints canonical_verdict = PASS (iff regex lightweight path ≥5000 rec/sec) | FAIL
```
The agent never passes `--reference-host` → stays `INSUFFICIENT_EVIDENCE`. Spec + protocol:
`05-pass2/NFR-010/reference-host-runbook.md`. **Closes:** NFR-010b PROVISIONAL → PASS.

## ⏳ 4. Real-user validation
**Resource:** real participants (NOT a simulated cohort — a simulated `outcome.md` is a CATASTROPHIC violation).
- **Operating-point re-elicitation** (DC-27; n=8–12 real P-priv-eng + P-dpo): confirm β=2 / recall_target=0.90.
  Pre-registered instrument: `05-testing/05-pass2/operating-point-reelicitation/instrument.md`. If revised, it is
  a config change (`configs/assessment.yaml operating_point`) — the assessment is parameterized; just re-run.
- **Design real-user trial + concept-value re-confirm** (cycle-1; n=12–18 real consumers):
  `05-testing/05-pass2/design-real-user-trial/`.
**Closes:** the AGENT_SIMULATED design/threshold provenance.

## ⏳ 5. Real-CI clean-checkout run (release-CI)
**Resource:** a clean external CI image with the full optional surface
(`.[dev,baselines,llm,distribution,croissant,viz]`).
**Step:** run both suites on a clean checkout → drops `AGENT_SIMULATED`, converts the NFR-012 `importorskip`
skips to executed passes. **Closes:** the methodology-provenance caveat.

## ⏳ 6. Mint the DOI (DC-31 / FR-054)
**Resource:** a Zenodo (or equivalent) account.
**Step:** deposit the release on Zenodo, then replace the `PENDING-ZENODO-MINT` sentinel in `CITATION.cff` /
`CITATION.bib` / `release/citation.py CITATION_METADATA["doi"]` with the minted DOI. `validate_no_fake_doi`
forbids a fabricated one; a genuinely-minted `10.x` is accepted. **Closes:** the FR-054 persistent-identifier bar.

## ⏳ 7. Full-corpus REAL-detector run (optional, for a citable real-systems census)
**Resource:** a host willing to run real detectors over 575,604 records (≈hours on GPU; the powered 1822-record
real-systems run took ~7 min).
**Step:** `pii-rate-elo assessment --sample <full-corpus-manifest> --corpus <full corpus> --systems
presidio,gliner,piiranha --run-type filing-grade --out results-real-census`. This session ran the full-corpus
census with the bundled synthetic systems (E2) + the real-systems powered run (E1); the real-systems full census
is the only remaining scale point. **Closes:** a citable real-systems descriptive census (still synthetic data —
🔒 AX-001 holds).

---

## ✅ Closed this session (no human action) — see `release-readiness-report.md §3c`
All of C1–C13 + the McNemar-overflow fix + E1 real-systems (INDICATIVE→real-systems) + E2 full-corpus census.
Both repos green; mypy clean; lattice/corpus/tags untouched; Wave-7 honesty review CLEAN.

> **Reaching unconditional SHIP** requires items 2–6 (item 1 is permanent). None is code-achievable in this
> environment; each is a single human step with the exact command above.
