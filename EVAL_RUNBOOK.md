# Full 11-Detector Leaderboard — Run Runbook

How to score **all 11 baseline detectors** (8 local + 3 cloud DLP) over the **full multilingual `test`
split** (115,618 records, 60 languages) in a reproducible, isolated environment, and regenerate the
multilingual card section. Everything is **budget-gated**: no cloud money is spent without an explicit
confirmation.

> The English **all-11 headline** (`results/baselines/tier1-en-all/`, wired into [BASELINES.md](BASELINES.md)
> and [README.md](README.md)) is already complete and is **not** changed by this run. This run *adds* the
> full-multilingual section.

---

## 0. What runs where, and what it costs

| Tier | Detectors | Scope | Where | Cost |
|---|---|---|---|---|
| Local | regex, presidio, spacy, gliner, piiranha, scrubadub, stanza, flair | all 60 languages | Docker (GPU VM) | $0 |
| Cloud | aws | English only (Comprehend PII is EN-only) | HTTPS API | ~$26 |
| Cloud | gcp | 12 major languages | HTTPS API | ~$0 (< 1 GB free tier) |
| Cloud | azure | English + as many supported langs as the budget allows | HTTPS API | **capped** (see below) |

**Azure is the only real budget risk.** Per-document 1,000-char rounding makes Azure ~70% of cloud spend.
Run the preflight to see the exact projection and the budget-capped plan:

```bash
python scripts/cloud_cost_preflight.py --split test --max-azure-usd 90
```

Today that prints (×2 safety ceiling): **AWS $25.58 · GCP $0.00 · Azure full $196.33**, and with a **$90
Azure cap** Azure covers **en + nl ≈ $78.74** (English alone is ~$63). So within a ~$100 Azure credit you
realistically get **English + 1–2 more languages on Azure**, **all 12 majors free on GCP**, and **English
on AWS**. Local detectors cover **all 60 languages for free**.

> **Combined Azure budget:** the GPU VM *also* draws on your Azure credits, but a spot T4 for a few
> GPU-hours is only ~$2–8 — small next to Azure DLP. If you want to preserve credits for DLP, run the GPU
> VM on AWS/GCP instead (the container is identical) and keep Azure for the DLP calls only.

---

## 1. Credentials

Put provider creds in `~/.pii-anon-cloud.env` (never committed; the scripts source it):

```bash
# AWS (or rely on ~/.aws/credentials / AWS_PROFILE)
export AWS_ACCESS_KEY_ID=...           ; export AWS_SECRET_ACCESS_KEY=... ; export AWS_REGION=us-east-1
# Azure AI Language
export AZURE_LANGUAGE_ENDPOINT=https://<resource>.cognitiveservices.azure.com/ ; export AZURE_LANGUAGE_KEY=...
# GCP DLP
export GOOGLE_APPLICATION_CREDENTIALS=/path/key.json ; export GCP_PROJECT=<project-id>
```

---

## 2. Dry run first (spends nothing)

```bash
scripts/run_full_leaderboard.sh --dry-run --max-azure-usd 90
```

Prints the per-provider/per-language cost table and the JSON run plan. Always start here.

---

## 3a. Local on this Mac (no Docker) — simplest, $0, slower

```bash
pip install -e ".[baselines,engines]" && python -m spacy download en_core_web_lg
LIMIT=200 scripts/run_full_leaderboard.sh --no-cloud --no-report   # smoke first (first 200 records)
scripts/run_full_leaderboard.sh --no-cloud                          # full local, all 60 languages
```

## 3b. Reproducible Docker image (local or any VM)

```bash
docker build -t pii-anon-eval .
# local (CPU), preflight only:
docker run --rm -v "$PWD/results:/app/results" pii-anon-eval scripts/run_full_leaderboard.sh --dry-run
# GPU + cloud (mounts results + the card back, sources creds):
docker run --rm --gpus all --env-file ~/.pii-anon-cloud.env \
  -v "$PWD/results:/app/results" -v "$PWD/BASELINES.md:/app/BASELINES.md" \
  pii-anon-eval scripts/run_full_leaderboard.sh --max-azure-usd 90 --yes
```

## 3c. Azure GPU VM (fastest; uses credits) — one command up + auto-teardown

```bash
az login
export PII_ANON_CLOUD_ENV=~/.pii-anon-cloud.env
MAX_AZURE_USD=90 scripts/provision_azure_gpu.sh up     # spot T4 VM → build → run → fetch results → delete RG
# (teardown also runs on EXIT; force it any time with: scripts/provision_azure_gpu.sh down)
```

This stands up a spot `Standard_NC4as_T4_v3`, installs the NVIDIA driver + Docker, builds the image, runs
`run_full_leaderboard.sh` with the GPU, copies `results/` and the updated `BASELINES.md` back, then deletes
the resource group. Set `KEEP_VM=1` to leave the VM running for debugging.

---

## 4. What you get

```
results/baselines/fulltest-local/                # 8 local detectors, all 60 langs (merged + per-detector)
  baseline_results.json  leaderboard.md  <detector>/...
results/baselines/fulltest-cloud/<provider>/<lang>/   # one restart-safe shard per (provider, language)
  baseline_results.json  run.log
BASELINES.md  → BEGIN/END-LEADERBOARD-MULTILINGUAL block populated with the by-language F2 matrix
```

The run is **restart-safe**: re-run the same command to resume — a finished detector or `(provider,language)`
shard is skipped, so a spot-VM eviction or an Azure-credit cutoff only loses the in-flight shard.

---

## 5. Regenerate the card by hand (if you ran with `--no-report`)

```bash
python scripts/sync_cards.py matrix \
  --local results/baselines/fulltest-local/baseline_results.json \
  --cloud-glob 'results/baselines/fulltest-cloud/*/*/baseline_results.json' \
  --file BASELINES.md --marker LEADERBOARD-MULTILINGUAL --dry-run   # drop --dry-run to write
git diff BASELINES.md     # only the bytes between the markers change
```

---

## 6. Honesty notes (carried into the card)

- Multilingual numbers for **English-tuned local detectors** (spaCy `en_core_web_lg`, Presidio `en`,
  Stanza/Flair English models) will be **low on non-English** — expected, and shown, not hidden. GLiNER and
  Piiranha are multilingual.
- A cloud provider that doesn't support a language shows `—` in the matrix (an `unsupported-language`
  status), never a faked/garbage `en`-on-that-language score.
- All scores remain **synthetic-only (AX-001)** — statistical precision on PII-Anon's synthetic
  distribution, not an external-validity claim. Cloud numbers are a **single run** of non-deterministic
  managed services.
