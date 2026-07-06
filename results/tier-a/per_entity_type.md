# Per-entity-type & micro→macro collapse

Macro (unweighted mean over the 66 types) collapses relative to micro: detectors succeed on a few frequent types and fail the long tail. The ratio macro/micro is a *coverage-ceiling* diagnostic.

| Detector | Micro F2 | Macro F2 | Macro/Micro | Micro recall | Macro recall |
|---|---:|---:|---:|---:|---:|
| aws | 0.7360 | 0.2726 | 0.37 | 0.728 | 0.288 |
| gliner | 0.7337 | 0.2424 | 0.33 | 0.716 | 0.264 |
| gcp | 0.7040 | 0.1456 | 0.21 | 0.700 | 0.151 |
| azure | 0.6962 | 0.1334 | 0.19 | 0.688 | 0.141 |
| presidio | 0.5262 | 0.0914 | 0.17 | 0.562 | 0.105 |
| regex | 0.3956 | 0.1214 | 0.31 | 0.349 | 0.124 |
| piiranha | 0.3452 | 0.1084 | 0.31 | 0.327 | 0.133 |
| stanza | 0.3402 | 0.0211 | 0.06 | 0.308 | 0.030 |
| flair | 0.3264 | 0.0207 | 0.06 | 0.295 | 0.026 |
| spacy | 0.3170 | 0.0181 | 0.06 | 0.294 | 0.026 |
| scrubadub | 0.2006 | 0.0406 | 0.20 | 0.169 | 0.047 |

## Types reachable by NO detector (structural blind spots)

30 of 66 gold types are outside *every* detector's label map:

`AUTHENTICATION_TOKEN, BAR_NUMBER, BIOMETRIC_ID, COURT_CASE_NUMBER, CREDIT_CARD_FRAGMENT, DEVICE_IDENTIFIER, DOCKET_NUMBER, EDUCATION_LEVEL, EMPLOYEE_ID, ETHNICITY, GENDER, GENETIC_DATA, HOUSEHOLD_SIZE, INSURANCE_POLICY_NUMBER, INVOICE_NUMBER, JOB_TITLE, LATITUDE_LONGITUDE, MARITAL_STATUS, MEDICAL_RECORD_NUMBER, NATIONALITY, NPI_NUMBER, POLITICAL_OPINION, PRESCRIPTION_NUMBER, PROCEDURE_NAME, RELIGIOUS_BELIEF, SALARY, SEXUAL_ORIENTATION, TRADE_UNION_MEMBERSHIP, VEHICLE_MODEL, VISA_NUMBER`


## High-severity types: recall of the top-2 detectors + best-of-any

| Type | aws | gliner | best recall (any detector) | best detector |
|---|---:|---:|---:|---|
| SOCIAL_SECURITY_NUMBER | 0.913 | 0.854 | 0.970 | regex |
| CREDIT_CARD_NUMBER | 0.818 | 0.816 | 0.818 | aws |
| PASSPORT_NUMBER | 0.909 | 0.860 | 0.909 | aws |
| MEDICAL_RECORD_NUMBER | 0.000 | 0.000 | 0.000 (all miss) | — |
| BANK_ACCOUNT_NUMBER | 0.861 | 0.495 | 0.887 | presidio |
| DRIVER_LICENSE_NUMBER | 0.938 | 0.863 | 0.938 | aws |
| AGE | 0.139 | 0.000 | 0.139 | aws |
| HEALTH_CONDITION | 0.000 | 0.973 | 0.973 | gliner |
| NATIONAL_ID_NUMBER | 0.000 | 0.515 | 0.515 | gliner |
| DATE_OF_BIRTH | 0.971 | 0.955 | 0.971 | aws |
| AUTHENTICATION_TOKEN | 0.000 | 0.000 | 0.000 (all miss) | — |
| API_KEY | 0.117 | 0.000 | 0.117 | aws |
