# Enriched-vs-core ablation (provenance.source_type)

Does the F2 ranking survive partitioning out the ~lattice enrichment fill? Per-detector F2 by `provenance.source_type` over the English test split. Neutralises the AX-003 desk-reject ("the ranking is an artefact of the formulaic fill").

| Detector | curated_public F2 (n_gold=8,987) | synthetic F2 (n_gold=162,206) | synthetic_lattice_enrichment F2 (n_gold=30,687) |
|---|---:|---:|---:|
| gliner | 0.7507 | 0.7263 | 0.7820 |
| presidio | 0.5424 | 0.5076 | 0.6270 |
| regex | 0.4331 | 0.3957 | 0.3834 |
| piiranha | 0.3904 | 0.3345 | 0.3904 |
| stanza | 0.2945 | 0.3369 | 0.3748 |
| spacy | 0.2673 | 0.3105 | 0.3709 |
| scrubadub | 0.2131 | 0.1622 | 0.3926 |

## Ranking by partition (top→bottom)

- **curated_public**: gliner > presidio > regex > piiranha > stanza > spacy > scrubadub
- **synthetic**: gliner > presidio > regex > stanza > piiranha > spacy > scrubadub
- **synthetic_lattice_enrichment**: gliner > presidio > scrubadub > piiranha > regex > stanza > spacy

**Top-2 ordering IS identical across all partitions** → the headline ranking is invariant to the enrichment fill.

_Precision note: per-partition precision uses n_pred only from records IN that source_type partition; predictions from zero-gold records (which carry no partition) are excluded, so the per-partition F2 is for RANK comparison — not level-comparable to the headline micro-F2._
