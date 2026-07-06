# Thai native-names migration report (v2.2.0 SP-I, approach γ′)

- sources migrated: 24
- records scanned: 3,226,744
- Thai records: 164,524
- records changed: 164,136
- spans changed (PERSON_NAME + EMAIL): 328,756
- edge-case flags (unmapped name/email left unchanged): 0

## Per-source

| source | records | th | changed | spans |
|---|---|---|---|---|
| src/pii_anon_datasets/data/pii_anon.jsonl.gz | 782,677 | 41,122 | 41,025 | 82,162 |
| src/pii_anon_datasets/splits/dev.jsonl.gz | 78,046 | 4,108 | 4,099 | 8,205 |
| src/pii_anon_datasets/splits/test.jsonl.gz | 157,045 | 8,234 | 8,213 | 16,454 |
| src/pii_anon_datasets/splits/test_adversarial.jsonl.gz | 11,254 | 0 | 0 | 0 |
| src/pii_anon_datasets/splits/test_clinical.jsonl.gz | 4,630 | 0 | 0 | 0 |
| src/pii_anon_datasets/splits/test_financial.jsonl.gz | 5,100 | 0 | 0 | 0 |
| src/pii_anon_datasets/splits/test_legal.jsonl.gz | 2,122 | 0 | 0 | 0 |
| src/pii_anon_datasets/splits/test_technology.jsonl.gz | 2,301 | 6 | 6 | 18 |
| src/pii_anon_datasets/splits/train.jsonl.gz | 547,586 | 28,780 | 28,713 | 57,503 |
| src/pii_anon_datasets/subsets/by_difficulty/challenging.jsonl.gz | 190,683 | 10,258 | 10,258 | 20,516 |
| src/pii_anon_datasets/subsets/by_difficulty/easy.jsonl.gz | 190,170 | 10,372 | 10,275 | 20,544 |
| src/pii_anon_datasets/subsets/by_difficulty/hard.jsonl.gz | 207,270 | 10,375 | 10,375 | 20,822 |
| src/pii_anon_datasets/subsets/by_difficulty/moderate.jsonl.gz | 194,554 | 10,117 | 10,117 | 20,280 |
| src/pii_anon_datasets/subsets/by_dimension/context_preservation.jsonl.gz | 13,288 | 30 | 30 | 93 |
| src/pii_anon_datasets/subsets/by_dimension/diverse_pii_types.jsonl.gz | 634,187 | 40,875 | 40,875 | 81,739 |
| src/pii_anon_datasets/subsets/by_dimension/edge_cases.jsonl.gz | 72,362 | 30 | 30 | 60 |
| src/pii_anon_datasets/subsets/by_dimension/entity_tracking.jsonl.gz | 25,207 | 30 | 30 | 120 |
| src/pii_anon_datasets/subsets/by_dimension/format_variations.jsonl.gz | 7,567 | 30 | 30 | 60 |
| src/pii_anon_datasets/subsets/by_dimension/multilingual.jsonl.gz | 22,716 | 97 | 0 | 0 |
| src/pii_anon_datasets/subsets/by_dimension/temporal_consistency.jsonl.gz | 7,350 | 30 | 30 | 90 |
| src/pii_anon_datasets/subsets/by_domain/clinical.jsonl.gz | 23,449 | 0 | 0 | 0 |
| src/pii_anon_datasets/subsets/by_domain/financial.jsonl.gz | 25,165 | 0 | 0 | 0 |
| src/pii_anon_datasets/subsets/by_domain/legal.jsonl.gz | 10,742 | 0 | 0 | 0 |
| src/pii_anon_datasets/subsets/by_domain/technology.jsonl.gz | 11,273 | 30 | 30 | 90 |

_Untouched name-bearing types (by design): USERNAME (not name-derived), ORGANIZATION_NAME / LOCATION_NAME / MEDICATION_NAME / PROCEDURE_NAME (non-person pools)._
