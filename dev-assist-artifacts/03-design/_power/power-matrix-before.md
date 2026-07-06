# Committed-Lattice Power Matrix — BEFORE enrichment

Corpus: pii_anon v2.0.0, 159,891 records (pre-S-PWR-enrichment). `pre-lattice-enrichment` tag.

- committed count-gated cells: **710** · well-powered **251** · under-powered **200** · empty **259**
- total positive shortfall: **424,144** · overall verdict: **SMALL**

## By named interaction
| interaction | cells | well | under | empty | shortfall | verdict |
|---|---:|---:|---:|---:|---:|---|
| adversarial_x_entity_type | 66 | 2 | 1 | 63 | 47,592 | SMALL |
| domain_x_track | 10 | 8 | 1 | 1 | 1,174 | ADEQUATE |
| language_x_entity_type | 492 | 119 | 178 | 195 | 364,473 | SMALL |
| marginal:adversarial | 3 | 3 | 0 | 0 | 0 | LARGE |
| marginal:difficulty | 4 | 4 | 0 | 0 | 0 | LARGE |
| marginal:dimension | 7 | 7 | 0 | 0 | 0 | LARGE |
| marginal:domain | 5 | 5 | 0 | 0 | 0 | LARGE |
| marginal:entity_type | 63 | 43 | 20 | 0 | 10,905 | SMALL |
| marginal:language | 60 | 60 | 0 | 0 | 0 | LARGE |

## By risk tier
| tier | cells | well | under | empty | shortfall | verdict |
|---|---:|---:|---:|---:|---:|---|
| critical | 214 | 35 | 90 | 89 | 243,465 | SMALL |
| long_tail | 10 | 4 | 6 | 0 | 117 | SMALL |
| standard | 486 | 212 | 104 | 170 | 180,562 | SMALL |

## Claim ladder (sampling-design.md §7)
- **Marginals** (per language/type/domain/difficulty/adversarial/dimension): single-factor recall claims with 95% Wilson CIs.
- **Named 2-ways** (language×entity-type rectangle, domain×track, adversarial-type×entity-type): estimable on committed cells only.
- **Unnamed 2-way / ≥3-way / full grid**: NOT estimable — exploratory only.

_Power on a synthetic cell is precision on the synthetic distribution, not external validity (cf. FR-027 real-data correlation slice)._
