# PII-Anon v2.2.0 — Release Checklist

A step-by-step runbook to take PII-Anon from "feature-complete" to **fully evaluated and publicly released** so
others can find, load, cite, and reproduce it: HuggingFace dataset (data + card + Parquet/Croissant +
leaderboard) → public GitHub code repo → tagged v2.0.0 Release → Zenodo DOI.

**Legend:** 🤖 automatable (CLI/script) · 👤 human-only (accounts, billing, legal, real people) · ⏱️
long-running (background) · ⛔ phase blocker.

> All commands run from the repo root in the project venv. Tests use `PYTHONPATH=src python -m pytest`.
> Every published detector number carries the non-strippable **synthetic-only caveat (AX-001)** — real
> detectors on synthetic data are *not* an external-validity claim. See `BASELINES.md` and `CLOUD_DLP_COST.md`.

---

## Phase 0 — Finish the evaluation (all 4 tiers)

Detectors: regex, scrubadub, spaCy, Stanza, Flair, GLiNER, Piiranha, Presidio (8 local) + LLM (API key) +
AWS/GCP/Azure (cloud, behind keys). Every run emits `baseline_results.json` + run-record + sha256 provenance.

### Tier 1 — English test headline (local) 🤖⏱️
- [ ] Run the 8 local detectors on the English test (headline = a seeded representative sample; the full
  30,995-record census is ~15 h — optional, label `n`):
  ```bash
  pii-anon baselines --detectors regex,scrubadub,spacy,stanza,gliner,presidio,flair,piiranha \
    --input /tmp/en_test_2000.jsonl --split test --languages en --out results/baselines/tier1-en
  ```
- [ ] Confirm the leaderboard prints (GLiNER should lead, ~F2 0.71) and the three artifacts exist in `--out`.

### Tier 2 — per-domain (clinical / financial / legal / technology) 🤖
- [ ] Per-domain F2 is **already emitted** in the Tier-1 run's `by_domain` block — no separate run needed.
  Optionally cross-check by running the per-domain splits (`--split test_clinical`, etc.).

### Tier 3 — representative multilingual slice (local) 🤖⏱️
- [ ] Seeded multilingual sample across the major languages, full local roster:
  ```bash
  pii-anon baselines --detectors regex,scrubadub,spacy,stanza,gliner,presidio,flair,piiranha \
    --split test --languages all --limit 3000 --out results/baselines/tier3-multilingual
  ```
  (English-only detectors show low non-English recall — the honest, disclosed result.)

### Tier 4 — full 60 languages, multilingual detectors only 🤖⏱️⏱️
- [ ] Run only the multilingual-capable detectors over the full multilingual test split. **English-only
  detectors are flagged N/A; no cloud at Tier 4.** Long run — background it:
  ```bash
  pii-anon baselines --detectors gliner,piiranha --split test --languages all --out results/baselines/tier4-60lang
  ```

### Cloud DLP — AWS + GCP + Azure on the full English test 👤⛔ then 🤖⏱️⏱️
- [ ] 👤 Unblock credentials (the cloud run does nothing until these resolve):
  - **AWS** — attach the `comprehend:DetectPiiEntities` IAM permission (creds already resolve via `~/.aws/credentials`).
  - **GCP** — `gcloud services enable dlp.googleapis.com`; `gcloud auth application-default login`; `export GCP_PROJECT=<id>`.
  - **Azure** — create an *Azure AI Language* resource; `export AZURE_LANGUAGE_ENDPOINT=…` + `AZURE_LANGUAGE_KEY=…`.
- [ ] 🤖 Verify: `pii-anon baselines --list --cloud` (all three appear).
- [ ] 🤖⏱️ Run (full English test ≈ 93k sequential calls, ~hours, ~$44–88 ×2 — see `CLOUD_DLP_COST.md`):
  ```bash
  pii-anon baselines --cloud --detectors aws,gcp,azure --split test --languages en --out results/baselines/tier1-en-cloud
  ```

### Wire the numbers into the docs + card 🤖
- [ ] Replace the `<!-- BEGIN-LEADERBOARD -->` placeholder in **BASELINES.md** with the rendered leaderboard
  (`reporting.baselines.render_baseline_leaderboard`), and the README `<!-- BEGIN-LEADERBOARD-SUMMARY -->` with a top-3 summary.
- [ ] Generate the populated card:
  `pii-anon export --format card --baselines results/baselines/tier1-en/baseline_results.json --output dist/README.md`
- [ ] Commit `results/baselines/**` + the doc edits; keep doc-drift green.

---

## Phase 1 — Quality & consistency gates (all must pass) 🤖

- [ ] Full suite: `PYTHONPATH=src python -m pytest -q`
- [ ] Doc-drift = 0 (NFR-013): `pytest -k nfr_013`
- [ ] Power gate (NFR-018): `pii-anon validate --lattice` (exit 0)
- [ ] Lattice frozen: `python -m pii_anon_datasets.stats.lattice --check` (730 cells @47c3a8f)
- [ ] ruff-clean: `python -m ruff check baselines/ src/pii_anon_datasets/baselines/ src/pii_anon_datasets/reporting/baselines.py`
- [ ] `MANIFEST.sha256` unchanged (no corpus regen); four metric families stay separate (AX-004); `significance.py` quarantined.

---

## Phase 2 — Build the distribution artifacts (`dist/`) 🤖

All exporters are deterministic + streaming (the full corpus is never materialized).

- [ ] Card (with leaderboard): `pii-anon export --format card --baselines results/baselines/tier1-en/baseline_results.json --output dist/README.md`
- [ ] Parquet (gov-02 `reg_*` typed columns; needs `.[distribution]`): `pii-anon export --format parquet --output dist/pii_anon.parquet`
- [ ] Croissant 1.0: `pii-anon export --format croissant --output dist/croissant.json`
- [ ] (optional) CoNLL / spaCy DocBin for NER users: `pii-anon export --format conll|spacy …`
- [ ] HF `datasets` round-trip (NFR-012): `datasets.load_dataset("parquet", data_files="dist/pii_anon.parquet")`; confirm the `reg_*` columns + counts.
- [ ] Emit `sha256` of every `dist/*` for the release notes.

---

## Phase 3 — Publish the dataset to HuggingFace Hub 👤 (CLI is 🤖)

- [ ] 👤 Create an HF account/org + an empty **dataset** repo; record the namespace (e.g. `<you>/pii-anon`).
- [ ] 👤 `huggingface-cli login` (or `export HF_TOKEN=…`, write scope).
- [ ] 🤖 Upload the card + data (no in-repo automation today — explicit CLI step):
  ```bash
  huggingface-cli upload <ns>/pii-anon dist/README.md README.md --repo-type dataset
  huggingface-cli upload <ns>/pii-anon dist/pii_anon.parquet data/pii_anon.parquet --repo-type dataset
  # + dist/croissant.json (and optional CoNLL/spaCy)
  ```
- [ ] Confirm the dataset **page + viewer** render; `datasets.load_dataset("<ns>/pii-anon")` from a clean env.
- [ ] 🤖 Add the HF URL into README / CITATION.cff / DATASHEET; re-run `pytest -k nfr_013`. Optionally ship a
  tiny `scripts/upload_hf.py` (explicit opt-in verb — the security review asked any upload path be explicit).

---

## Phase 4 — Publish the code to GitHub (code-only branch) 👤 (procedure 🤖)

The full branch can't be pushed (corpus >100MB in history). Publish a **code-only snapshot** — the corpus lives
on HF, not git. (`.gitignore` ignores only uncompressed `.jsonl`; the `.jsonl.gz` are tracked and must be stripped.)

- [ ] 🤖 Orphan branch, strip every corpus blob, re-gitignore, force-push:
  ```bash
  git checkout --orphan feat/v2-scoring-harness-code
  git rm -r --cached src/pii_anon_datasets/data/*.jsonl.gz src/pii_anon_datasets/splits/*.jsonl.gz \
    'src/pii_anon_datasets/subsets/**/*.jsonl.gz'
  printf '\n# Corpus is distributed via HuggingFace, never git (>100MB)\n*.jsonl.gz\n' >> .gitignore
  git add -A && git commit -m "Code-only snapshot: v2.0.0 (corpus on HF, not git)"
  git push -u origin feat/v2-scoring-harness-code --force
  ```
- [ ] ⚠️ Data-dependent tests (`load_dataset`) need the corpus — on a clean code-only checkout, fetch it from HF
  (or those tests skip). Pure-logic tests run corpus-free.
- [ ] 👤 Set the published branch + protection.
- [ ] 🤖 GitHub Actions CI on a **clean image** (installs `.[dev,baselines,engines,distribution,croissant,viz]`,
  fetches the corpus from HF, runs the suite + `validate --lattice` + `lattice --check` + `pytest -k nfr_013`).
  This is the real-CI evidence that closes release Caveat #4.

---

## Phase 5 — Version, release, and DOI 👤 + 🤖

- [ ] 🤖 Confirm: CHANGELOG `[2.0.0]` ✓, CITATION.cff `version: 2.0.0` ✓, Phase-1 gates green, verdict = SHIP-WITH-CAVEATS.
- [ ] 🤖 Tag + push: `git tag -a v2.0.0 -m "PII-Anon v2.0.0 — SHIP-WITH-CAVEATS"` ; `git push origin v2.0.0`.
- [ ] 👤 Cut a **GitHub Release** off `v2.0.0`: link the HF dataset, the BASELINES.md leaderboard, the 5 caveats; attach `dist/` checksums.
- [ ] 👤 **Zenodo**: connect the repo (or deposit the release) → mint the DOI.
- [ ] 🤖 Replace `PENDING-ZENODO-MINT` with the real DOI in `CITATION.cff`, `CITATION.bib`, and
  `src/pii_anon_datasets/release/citation.py::CITATION_METADATA` (the `validate_no_fake_doi()` guard forbids a
  fabricated `10.x` — pass the real one). Re-run tests.
- [ ] 👤 (optional) PyPI: `python -m build` + `twine upload` so `pip install pii-anon-datasets` works (corpus still from HF).

---

## Phase 6 — Upgrade SHIP-WITH-CAVEATS → SHIP (external validity; post-share) 👤

These do **not** block sharing (every number already carries AX-001), but they remove the caveats. **Never
fabricate their outcomes** — the protocols refuse simulated substitutes.

- [ ] 👤 **Real-data correlation** (FR-027): signed i2b2-2014 / TAB DUA + secure host; export only the derived
  paired-score matrix (real PHI never enters the repo) → `validation.real_data_ingest.correlate_from_path()`.
- [ ] 👤 **Real-user design trial**: n=12–18 real consumers; semi-structured interview + artifact walkthrough.
- [ ] 👤 **Distribution-shift study**: synthetic vs real feature histograms; quantify the power discount.
- [ ] 👤 **NFR-010 throughput**: `./scripts/run_throughput_benchmark.sh nfr010-refhost.json --reference-host "8-core …"`.
- [ ] Re-run the Stage-5 testing synthesis to re-rule the release verdict once any of these land.

---

## Phase 7 — Announce & share 👤

- [ ] Shareable surface: HF dataset URL · GitHub repo + v2.0.0 release · Zenodo DOI · the BASELINES.md leaderboard.
- [ ] Lead with the honest framing: synthetic-only (AX-001), per-detector label-map coverage, precision shown beside recall.

---

## End-to-end smoke (before announcing)

1. Clean venv → `pip install pii-anon-datasets` (or code-only checkout + extras).
2. `datasets.load_dataset("<ns>/pii-anon")` returns the splits with `reg_*` columns.
3. `pii-anon baselines --list`; a `--limit 50` run reproduces a leaderboard.
4. HF card renders with the leaderboard + caveats; GitHub-release links + DOI resolve.
5. `pytest -k nfr_013` + `pii-anon validate --lattice` + `stats.lattice --check` green on the published code.
