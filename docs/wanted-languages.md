# Wanted: languages, dialects, scripts & entity types

Where community contribution helps most. Grounded in the v2.0.0 test-split coverage measurement
(see `results/tier-a/multilingual_*` once the multilingual run lands). Pick something here, or propose
your own via the [*Contribute a language or dialect*](../.github/ISSUE_TEMPLATE/language_contribution.yml)
issue. How-to: [contributing-languages.md](contributing-languages.md).

Legend: **🅰** powered (≥1000 recs, stable CIs) · **🅱** coverage probe (~50 recs, underpowered) · **❌** absent.

## 1. Highest priority — underpowered Asian & Global-South languages

These exist only as ~50-record probes (wide CIs) or are absent. Bringing any to **≥100 records**
(ideally ≥30 per language×dimension cell) makes its per-language metrics citable.

| Language | BCP-47 | Script | Status | Notes |
|---|---|---|---|---|
| Tamil | `ta` (`ta-IN`,`ta-LK`,`ta-SG`) | Taml | 🅱 | also currently **mislabeled `Latn`** — see §4 |
| Telugu | `te` | Telu | 🅱 | mislabeled `Latn` |
| Urdu | `ur` (`ur-PK`,`ur-IN`) | Arab | 🅱 | RTL; Nastaʼliq |
| Persian | `fa` (`fa-IR`,`fa-AF`=Dari) | Arab | 🅱 | RTL |
| Nepali | `ne` | Deva | 🅱 | |
| Sinhala | `si` | Sinh | 🅱 | |
| Khmer | `km` | Khmr | 🅱 | no inter-word spaces — tokenization-hard |
| Lao | `lo` | Laoo | 🅱 | |
| Malay | `ms` | Latn | 🅱 | |
| Pashto | `ps` | Arab | 🅱 | |
| Bengali | `bn` (`bn-BD`,`bn-IN`) | Beng | 🅱/❌ | |
| Kannada | `kn` | Knda | ❌ | |
| Malayalam | `ml` | Mlym | ❌ | |
| Gujarati | `gu` | Gujr | ❌ | |
| Punjabi | `pa` | Guru | ❌ | |
| Odia | `or` | Orya | ❌ | |
| Burmese | `my` | Mymr | ❌ | |
| Tagalog/Filipino | `tl`/`fil` | Latn | ❌ | |
| Javanese | `jv` | Latn/Java | ❌ | |
| Cebuano | `ceb` | Latn | ❌ | |

## 2. Dialects of already-covered languages

Dialects change names, ID schemes, address/phone formats, and honorifics — a production pipeline must
handle them. We have the base language but want the regional variants:

- **Chinese:** `zh-Hant` (Traditional) vs `zh-Hans` (Simplified) — distinct scripts.
- **Arabic:** `ar-EG`, `ar-SA`, `ar-MA`, `ar-LV` vs Modern Standard `ar`.
- **Portuguese:** `pt-BR` vs `pt-PT`. **Spanish:** `es-MX`, `es-AR`, `es-CO` vs `es-ES`.
- **English:** `en-IN`, `en-SG`, `en-PH`, `en-NG` (very different PII: Aadhaar, NRIC, etc.) vs `en-US`.
- **Korean** regional, **Hindi** vs other Indic registers, **French** `fr-CA` vs `fr-FR`.

## 3. Locale-specific & under-covered entity types

The taxonomy has 90+ canonical types, but some are thin or locale-specific. Records that exercise these
are wanted (often paired with the languages above):

- **National ID schemes:** Aadhaar (`en-IN`/`hi`), MyNumber (`ja`), Resident Registration Number (`ko`),
  Emirates ID (`ar`), NRIC (`en-SG`), CURP (`es-MX`) — all map to `NATIONAL_ID_NUMBER` but need realistic
  formats per locale.
- **GDPR Art.9 special categories** (under-represented per the dataset fitness review): `SEXUAL_ORIENTATION`,
  `UNION_MEMBERSHIP`, `GENETIC_MARKER`, plus more `POLITICAL_OPINION` / `RELIGIOUS_BELIEF` / `ETHNICITY`
  at scoreable support (≥~400 spans each).
- **Secrets/credentials** in agentic contexts: broaden beyond `API_KEY` (Bearer/JWT, cloud keys, PEM,
  `CVV`/`PIN`) — propose a new `CONNECTION_STRING`/DSN type via an issue if needed.

## 4. Data-quality fixes the community can help with

- **Script-code canonicalization:** the `script` field mixes ISO-15924 codes and full names
  (`Latn`/`Latin`, `Cyrl`/`Cyrillic`, `Hebr`/`Hebrew`, `Deva`/`Devanagari`) **and mislabels Tamil/Telugu
  records as `Latn`.** A normalization pass (data-quality issue + PR) is welcome.
- **Mislabel reports:** wrong entity type / span boundary → the
  [data-quality issue template](../.github/ISSUE_TEMPLATE/data_quality.yml).

---

_Coverage status updates as the multilingual benchmark (`results/tier-a/multilingual_leaderboard.md`)
is refreshed. Counts are from the v2.0.0 test split; the full corpus may carry more of a given language._
