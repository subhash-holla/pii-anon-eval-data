# Cloud DLP detector cost estimate (×2 safety factor)

The cloud DLP adapters (AWS Comprehend, GCP Sensitive Data Protection, Azure AI Language PII) are **built
behind credentials but NOT run**. This note is the budget go/no-go: a grounded estimate from **verified
June 2026 list pricing** × **actual PII-Anon character counts**, with a **×2 safety factor** (retries,
request overhead, the 3-unit / 1-KB / 1-record minimums on short documents, and price drift).

## Verified list pricing (June 2026)

| Provider | Billing unit | List price | Free tier / month | Min per request |
|---|---|---|---|---|
| AWS Comprehend `DetectPiiEntities` | 100 characters = 1 unit | **$0.0001 / unit** | 50,000 units (5M chars) | 3 units (300 chars) |
| GCP Sensitive Data Protection `content.inspect` | bytes inspected | **$3.00 / GB** (>1 GB; $2 >1 TB) | 1 GB | 1 KB |
| Azure AI Language PII | 1,000 characters = 1 text record | **$1.00 / 1,000 records** (0–500K; $0.75 to 2.5M; $0.30 to 10M) | 5,000 records | rounds **per document** |

The **per-document rounding** is decisive: PII-Anon documents average ~295 chars (English test), so each is
billed as a *whole* Azure text record (1,000 chars) and as the AWS 3-unit floor — short docs cost far more
than a naive chars/unit calc. Azure therefore dominates total cost.

## Actual billable volume (computed from the corpus)

| Scope | Docs | Chars | AWS units (100c, 3-min) | Azure text-records (1000c, per-doc) | GCP GB |
|---|---:|---:|---:|---:|---:|
| **English test** | 30,995 | 9,143,672 | 127,919 | 31,419 | 0.0091 |
| **Full test (60 lang)** | 115,618 | 19,527,236 | 384,476 | 116,157 | 0.0195 |
| **Full corpus (60 lang)** | 575,604 | ~97,000,000 | ~1,500,000 | ~600,000 | ~0.10–0.19 |

## Estimated cost — gross list price × 2 (free tiers ignored = conservative ceiling)

| Scope | AWS ×2 | GCP ×2 | Azure ×2 | **All three ×2** |
|---|---:|---:|---:|---:|
| **English test** | $26 | ~$0 (under 1 GB free) | $63 | **≈ $88** |
| **Full test (60 lang)** | $77 | ~$0 | $232 | **≈ $309** |
| **Full corpus (60 lang)** | ~$300 | ~$0 | ~$1,150 | **≈ $1,450** |

Notes: GCP DLP is GB-priced and the entire corpus is **< 1 GB**, so it falls inside the 1 GB/month free
tier — effectively **free** at every scope. AWS is moderate. **Azure is ~70% of total** at every scope
because of per-document text-record rounding. With free tiers applied, English-test AWS drops to ~$16 and
Azure to ~$62; the ×2 factor already absorbs that, so the table above is the safe upper bound.

## Recommendation

- **Scope cloud to English (and, if wanted, the 10 other major languages).** Tier-4 full-60-language cloud
  is ~$1,450 and almost entirely Azure — defer it.
- **Cheapest meaningful cloud comparison:** AWS + GCP on the English test ≈ **$26 ×2** (GCP ≈ free). Adding
  Azure on the English test brings it to **≈ $88 ×2**.
- **No cloud detector runs until this budget is confirmed.** When approved, run:
  `pii-anon baselines --cloud --detectors aws,gcp[,azure] --split test --languages en --out results/baselines/tier1-en-cloud`
  with the provider credentials in the environment.

VERIFY pricing again at run time (per-region rates and tiers change): AWS Comprehend, GCP Sensitive Data
Protection, and Azure AI Language pricing pages.
