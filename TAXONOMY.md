# PII Entity Type Taxonomy v2.0.0

This document defines the entity types used in the PII-Anon Evaluation Dataset, organized into 9 categories. Each entry includes a definition, sensitivity classification, and regulatory relevance.

> **Canonical set (v2.2-dev): 66 entity types across 9 categories.** The authoritative, machine-readable source is `pii_anon_datasets.taxonomy` (derived directly from the corpus); `validate.py` accepts exactly those 66. This reconciles the prior three-way drift (48 in the old validator / "65" in the README / ~80 rows here), and adds 3 GDPR Art-9 special-category types in v2.2-dev (63→66). The tables below now list **exactly** those 66 types — one row per canonical type, in 1:1 correspondence with `taxonomy.ENTITY_REGISTRY` (enforced by `tests/test_doc_drift.py::test_nfr_013_taxonomy_body_matches_registry`).

## Sensitivity Classes

| Class | Definition | Example |
|-------|-----------|---------|
| **direct_identifier** | Uniquely identifies an individual on its own | Name, SSN, email |
| **quasi_identifier** | Identifying only in combination with other attributes | Age, postal code, job title |
| **sensitive_attribute** | Protected category data (GDPR Art. 9, HIPAA) | Health condition, political opinion |

## Category 1: Identity & Demographics (6 types)

| Entity Type | Sensitivity | Definition | Example |
|-------------|------------|------------|---------|
| `PERSON_NAME` | direct | Full name, first name, last name, or formal address | "John Smith", "Dr. Johnson" |
| `ORGANIZATION_NAME` | quasi | Company, institution, or organization name | "Acme Corp", "MIT" |
| `NATIONALITY` | quasi | National origin or citizenship | "German", "Brazilian" |
| `GENDER` | quasi | Gender identity | "Male", "Non-binary" |
| `AGE` | quasi | Numeric age or age range | "42", "30-35" |
| `ETHNICITY` | sensitive | Ethnic or racial identity | "Hispanic", "East Asian" |

## Category 2: Contact (2 types)

| Entity Type | Sensitivity | Definition | Example |
|-------------|------------|------------|---------|
| `EMAIL_ADDRESS` | direct | Email address | "user@example.com" |
| `PHONE_NUMBER` | direct | Phone number (any format) | "+1 (555) 123-4567" |

## Category 3: Financial (12 types)

| Entity Type | Sensitivity | Definition | Example |
|-------------|------------|------------|---------|
| `CREDIT_CARD_NUMBER` | direct | Payment card number | "4111 1111 1111 1111" |
| `CREDIT_CARD_FRAGMENT` | direct | Partial card number (last 4, first 6) | "****1234" |
| `BANK_ACCOUNT_NUMBER` | direct | Bank account number | "1234567890" |
| `BANK_ROUTING_NUMBER` | quasi | Bank routing/sort code | "021000021" |
| `IBAN` | direct | International Bank Account Number | "DE89370400440532013000" |
| `SWIFT_BIC_CODE` | quasi | SWIFT/BIC bank identifier | "DEUTDEFF" |
| `CRYPTOCURRENCY_ADDRESS` | direct | Blockchain wallet address | "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" |
| `TAX_ID` | direct | Tax identification number (EIN, TIN) | "12-3456789" |
| `INVOICE_NUMBER` | direct | Commercial invoice identifier | "INV-123456" |
| `INSURANCE_POLICY_NUMBER` | direct | Insurance policy identifier | "POL-7654321" |
| `CVV` | direct | Card verification value (3-4 digits) | "123" |
| `PIN` | direct | Personal identification number | "4521" |

## Category 4: Digital & Online (10 types)

| Entity Type | Sensitivity | Definition | Example |
|-------------|------------|------------|---------|
| `USERNAME` | direct | Account username or handle | "admin_42" |
| `PASSWORD` | direct | Password or passphrase | "P@ssw0rd123!" |
| `API_KEY` | direct | API key or secret token | "sk-abc123def456..." |
| `AUTHENTICATION_TOKEN` | direct | Session or auth token | "Bearer eyJhbGci..." |
| `SOCIAL_MEDIA_HANDLE` | direct | Social media username | "@johndoe" |
| `URL` | quasi | Web address containing PII | "example.com/users/john" |
| `IP_ADDRESS` | direct | IP address (IPv4 or IPv6) | "192.168.1.1", "2001:0db8:85a3::8a2e" |
| `MAC_ADDRESS` | direct | Network hardware address | "00:1B:44:11:3A:B7" |
| `DEVICE_IDENTIFIER` | direct | Hardware device ID | "UDID-ABC123" |
| `BIOMETRIC_ID` | direct | Biometric identifier reference | "BIO-FP-001234" |

## Category 5: Government & Legal (10 types)

| Entity Type | Sensitivity | Definition | Example |
|-------------|------------|------------|---------|
| `PASSPORT_NUMBER` | direct | Passport document number | "A12345678" |
| `DRIVER_LICENSE_NUMBER` | direct | Driver's license number | "DL-123456" |
| `SOCIAL_SECURITY_NUMBER` | direct | Social Security Number (US) | "123-45-6789" |
| `NATIONAL_ID_NUMBER` | direct | National identity card number | "NID-123456789" |
| `VISA_NUMBER` | direct | Visa document number | "V12345678" |
| `LICENSE_PLATE` | direct | Vehicle license plate | "ABC-1234" |
| `VEHICLE_IDENTIFICATION_NUMBER` | direct | Vehicle VIN | "1HGBH41JXMN109186" |
| `COURT_CASE_NUMBER` | direct | Court case file number | "2024-CV-1234" |
| `BAR_NUMBER` | direct | Bar association number | "CA-123456" |
| `DOCKET_NUMBER` | direct | Court docket number (PACER format) | "1:24-cv-01234-ABC" |

## Category 6: Medical & Biological (8 types)

| Entity Type | Sensitivity | Definition | Example |
|-------------|------------|------------|---------|
| `MEDICAL_RECORD_NUMBER` | direct | Hospital/clinic MRN | "MRN-1234567" |
| `HEALTH_CONDITION` | sensitive | Medical diagnosis or condition | "Type 2 Diabetes" |
| `HEALTH_INSURANCE_ID` | direct | Health insurance member ID | "INS-123456789" |
| `MEDICATION_NAME` | sensitive | Prescribed medication | "Metformin 500mg" |
| `PROCEDURE_NAME` | sensitive | Medical procedure | "Colonoscopy" |
| `PRESCRIPTION_NUMBER` | direct | Pharmacy prescription ID | "RX-7654321" |
| `NPI_NUMBER` | direct | National Provider Identifier (10-digit) | "1234567890" |
| `DEA_NUMBER` | direct | DEA registration number (prescriber ID) | "AB1234563" |

## Category 7: Location & Temporal (6 types)

| Entity Type | Sensitivity | Definition | Example |
|-------------|------------|------------|---------|
| `STREET_ADDRESS` | quasi | Physical street address | "123 Main St, Springfield, IL 62704" |
| `LOCATION_NAME` | quasi | Named geographic location (city, country, region) | "Berlin", "California" |
| `POSTAL_CODE` | quasi | ZIP or postal code | "62704", "SW1A 1AA" |
| `LATITUDE_LONGITUDE` | quasi | Geographic coordinates | "40.7128, -74.0060" |
| `TIMESTAMP` | quasi | Date-time value in document | "2024-03-15T14:30:00Z" |
| `DATE_OF_BIRTH` | quasi | Birth date | "1990-05-15" |

## Category 8: Employment (4 types)

| Entity Type | Sensitivity | Definition | Example |
|-------------|------------|------------|---------|
| `JOB_TITLE` | quasi | Professional role or position | "Senior Data Analyst" |
| `SALARY` | quasi | Compensation amount | "$85,000" |
| `EMPLOYEE_ID` | direct | Employer-assigned identifier | "EMP-12345" |
| `EDUCATION_LEVEL` | quasi | Highest education attained | "Master's degree" |

## Category 9: Special Category Data (8 types)

These are GDPR Article 9 "special categories" requiring explicit consent for processing.

| Entity Type | Sensitivity | Definition | Example | Regulatory Relevance |
|-------------|------------|------------|---------|---------------------|
| `POLITICAL_OPINION` | sensitive | Political affiliation or view | "registered Democrat" | GDPR Art. 9 |
| `RELIGIOUS_BELIEF` | sensitive | Religious affiliation | "Buddhist" | GDPR Art. 9 |
| `SEXUAL_ORIENTATION` | sensitive | Sexual orientation or sex life | "bisexual" | GDPR Art. 9 |
| `TRADE_UNION_MEMBERSHIP` | sensitive | Trade union affiliation | "Unite the Union member" | GDPR Art. 9 (Art. 9(2)(d)) |
| `GENETIC_DATA` | sensitive | Genetic markers or sequencing data | "BRCA1 c.68_69delAG pathogenic variant" | GDPR Art. 9 |
| `MARITAL_STATUS` | quasi | Relationship status | "married", "divorced" | Context-dependent |
| `HOUSEHOLD_SIZE` | quasi | Number of household members | "4-person household" | Re-identification risk |
| `VEHICLE_MODEL` | quasi | Vehicle make/model | "2022 Tesla Model 3" | Insurance/legal contexts |

## Regulatory Framework Mapping

| Framework | Key Entity Types |
|-----------|-----------------|
| **GDPR** (EU) | All PII types; special attention to Art. 9 sensitive categories |
| **HIPAA** (US Healthcare) | MEDICAL_RECORD_NUMBER, HEALTH_CONDITION, MEDICATION_NAME, HEALTH_INSURANCE_ID, DATE_OF_BIRTH, STREET_ADDRESS |
| **CCPA** (California) | PERSON_NAME, SOCIAL_SECURITY_NUMBER, DRIVER_LICENSE_NUMBER, CREDIT_CARD_NUMBER, BIOMETRIC_ID |
| **PCI-DSS** (Payment) | CREDIT_CARD_NUMBER, CREDIT_CARD_FRAGMENT, BANK_ACCOUNT_NUMBER |
| **SOX** (Financial) | TAX_ID, BANK_ACCOUNT_NUMBER, SALARY, EMPLOYEE_ID |

## Re-identification Risk

Quasi-identifiers create re-identification risk when combined:

| Combination | Estimated k-anonymity | Risk Level |
|-------------|----------------------|------------|
| 1 quasi-identifier | ~100 | Low |
| 2 quasi-identifiers | ~20 | Moderate |
| 3 quasi-identifiers | ~5 | High |
| 4+ quasi-identifiers | ~2 | Critical |

The dataset includes per-record `privacy_risk.k_anonymity_estimate` values based on the quasi-identifier count in each record's annotations.
