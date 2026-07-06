# Gold-validity spot-check (single-pass author corroboration)

> **AX-002 / AX-001 framing.** This is a SINGLE-PASS gold-validity corroboration by ONE rater (the author) against the programmatic gold — it is **NOT** inter-annotator agreement, **NOT** Cohen's kappa, **NOT** a multi-annotator panel, and **NOT** external validity. Self-adjudication is a named limitation: the type-correctness rate is an upper bound; the **blind type-recovery rate** is its anchoring-resistant complement. Realism is the author's synthetic-plausibility judgment (AX-001). Logged as a disclosed post-hoc AMEND to the preregistration (commissioned by MAJOR-3).

**Adjudicated:** 500 spans (Horvitz–Thompson inverse-`p_incl` weighted to the corpus marginal; the per-type coverage floor over-samples the long tail, so the weighted rate — not the raw pooled mean — is the corpus estimand).

## Powered claims — gold-validity corroboration rate per axis (the only reportable rates)

| Axis | weighted rate | Wilson 95% CI | eff. n | pooled (sample-level) |
|---|---:|---|---:|---:|
| type-correctness | 1.000 | [0.984, 1.000] | 239 | 1.000 |
| realism | 1.000 | [0.988, 1.000] | 321 | 1.000 |

**Blind type-recovery** (author named the type before the label was revealed, 124 blind spans): 0.927 [CI 0.868, 0.961].
**Blind-realism rate** (author rated realism with the type label withheld, 125 spans): 1.000 [CI 0.970, 1.000].

## Powered per-script cells (priority scripts, n≥24)

| Script | rate | Wilson 95% CI | n | status |
|---|---:|---|---:|---|
| Cyrl | 1.000 | [0.862, 1.000] | 24 | POWERED |
| Thai | 1.000 | [0.862, 1.000] | 24 | POWERED |
| Grek | 1.000 | [0.862, 1.000] | 24 | POWERED |
| Beng | 1.000 | [0.862, 1.000] | 24 | POWERED |
| Hebr | 1.000 | [0.862, 1.000] | 24 | POWERED |
| Latn | 1.000 | [0.983, 1.000] | 226 | POWERED |

## Descriptive coverage — per entity type (NOT powered claims; wide CIs)

| Entity type | rate | Wilson 95% CI | n | status |
|---|---:|---|---:|---|
| AGE | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| API_KEY | 1.000 | [0.566, 1.000] | 5 | UNDERPOWERED |
| AUTHENTICATION_TOKEN | 1.000 | [0.207, 1.000] | 1 | UNDERPOWERED |
| BANK_ACCOUNT_NUMBER | 1.000 | [0.646, 1.000] | 7 | UNDERPOWERED |
| BANK_ROUTING_NUMBER | 1.000 | [0.676, 1.000] | 8 | UNDERPOWERED |
| BAR_NUMBER | 1.000 | [0.610, 1.000] | 6 | UNDERPOWERED |
| BIOMETRIC_ID | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| COURT_CASE_NUMBER | 1.000 | [0.510, 1.000] | 4 | UNDERPOWERED |
| CREDIT_CARD_FRAGMENT | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| CREDIT_CARD_NUMBER | 1.000 | [0.676, 1.000] | 8 | UNDERPOWERED |
| CRYPTOCURRENCY_ADDRESS | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| CVV | 1.000 | [0.676, 1.000] | 8 | UNDERPOWERED |
| DATE_OF_BIRTH | 1.000 | [0.676, 1.000] | 8 | UNDERPOWERED |
| DEA_NUMBER | 1.000 | [0.566, 1.000] | 5 | UNDERPOWERED |
| DEVICE_IDENTIFIER | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| DOCKET_NUMBER | 1.000 | [0.610, 1.000] | 6 | UNDERPOWERED |
| DRIVER_LICENSE_NUMBER | 1.000 | [0.510, 1.000] | 4 | UNDERPOWERED |
| EDUCATION_LEVEL | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| EMAIL_ADDRESS | 1.000 | [0.937, 1.000] | 57 | POWERED |
| EMPLOYEE_ID | 1.000 | [0.646, 1.000] | 7 | UNDERPOWERED |
| ETHNICITY | 1.000 | [0.207, 1.000] | 1 | UNDERPOWERED |
| GENDER | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| GENETIC_DATA | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| HEALTH_CONDITION | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| HEALTH_INSURANCE_ID | 1.000 | [0.439, 1.000] | 3 | UNDERPOWERED |
| IBAN | 1.000 | [0.646, 1.000] | 7 | UNDERPOWERED |
| INSURANCE_POLICY_NUMBER | 1.000 | [0.646, 1.000] | 7 | UNDERPOWERED |
| INVOICE_NUMBER | 1.000 | [0.646, 1.000] | 7 | UNDERPOWERED |
| IP_ADDRESS | 1.000 | [0.439, 1.000] | 3 | UNDERPOWERED |
| JOB_TITLE | 1.000 | [0.439, 1.000] | 3 | UNDERPOWERED |
| LATITUDE_LONGITUDE | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| LICENSE_PLATE | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| LOCATION_NAME | 1.000 | [0.439, 1.000] | 3 | UNDERPOWERED |
| MAC_ADDRESS | 1.000 | [0.439, 1.000] | 3 | UNDERPOWERED |
| MARITAL_STATUS | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| MEDICAL_RECORD_NUMBER | 1.000 | [0.439, 1.000] | 3 | UNDERPOWERED |
| MEDICATION_NAME | 1.000 | [0.510, 1.000] | 4 | UNDERPOWERED |
| NATIONALITY | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| NATIONAL_ID_NUMBER | 1.000 | [0.676, 1.000] | 8 | UNDERPOWERED |
| NPI_NUMBER | 1.000 | [0.207, 1.000] | 1 | UNDERPOWERED |
| ORGANIZATION_NAME | 1.000 | [0.610, 1.000] | 6 | UNDERPOWERED |
| PASSPORT_NUMBER | 1.000 | [0.676, 1.000] | 8 | UNDERPOWERED |
| PASSWORD | 1.000 | [0.646, 1.000] | 7 | UNDERPOWERED |
| PERSON_NAME | 1.000 | [0.947, 1.000] | 68 | POWERED |
| PHONE_NUMBER | 1.000 | [0.758, 1.000] | 12 | UNDERPOWERED |
| PIN | 1.000 | [0.566, 1.000] | 5 | UNDERPOWERED |
| POLITICAL_OPINION | 1.000 | [0.207, 1.000] | 1 | UNDERPOWERED |
| POSTAL_CODE | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| PROCEDURE_NAME | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| RELIGIOUS_BELIEF | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| SALARY | 1.000 | [0.439, 1.000] | 3 | UNDERPOWERED |
| SEXUAL_ORIENTATION | 1.000 | [0.207, 1.000] | 1 | UNDERPOWERED |
| SOCIAL_MEDIA_HANDLE | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| SOCIAL_SECURITY_NUMBER | 1.000 | [0.701, 1.000] | 9 | UNDERPOWERED |
| STREET_ADDRESS | 1.000 | [0.646, 1.000] | 7 | UNDERPOWERED |
| SWIFT_BIC_CODE | 1.000 | [0.566, 1.000] | 5 | UNDERPOWERED |
| TAX_ID | 1.000 | [0.701, 1.000] | 9 | UNDERPOWERED |
| TIMESTAMP | 1.000 | [0.566, 1.000] | 5 | UNDERPOWERED |
| TRADE_UNION_MEMBERSHIP | 1.000 | [0.207, 1.000] | 1 | UNDERPOWERED |
| URL | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| USERNAME | 1.000 | [0.342, 1.000] | 2 | UNDERPOWERED |
| VEHICLE_IDENTIFICATION_NUMBER | 1.000 | [0.207, 1.000] | 1 | UNDERPOWERED |
| VEHICLE_MODEL | 1.000 | [0.207, 1.000] | 1 | UNDERPOWERED |
| VISA_NUMBER | 1.000 | [0.207, 1.000] | 1 | UNDERPOWERED |

## Disagreements (0)


_Datasheet line:_ single-pass author gold-validity corroboration on n=500 stratified spans — type-correctness 1.000 (Wilson 95% [0.984,1.000]), realism 1.000; NOT inter-annotator agreement / kappa (AX-002); synthetic-only (AX-001).
