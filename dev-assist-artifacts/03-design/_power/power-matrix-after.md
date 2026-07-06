# Committed-Lattice Power Matrix — AFTER enrichment

Corpus: pii_anon v2.0.0, 575,604 records (post-S-PWR Full-Broad enrichment, +415,713 synthetic). Every committed count-gated cell ≥ its tiered target.

- committed count-gated cells: **710** · well-powered **710** · under-powered **0** · empty **0**
- total positive shortfall: **0** · overall verdict: **LARGE**

## By named interaction
| interaction | cells | well | under | empty | shortfall | verdict |
|---|---:|---:|---:|---:|---:|---|
| adversarial_x_entity_type | 66 | 66 | 0 | 0 | 0 | LARGE |
| domain_x_track | 10 | 10 | 0 | 0 | 0 | LARGE |
| language_x_entity_type | 492 | 492 | 0 | 0 | 0 | LARGE |
| marginal:adversarial | 3 | 3 | 0 | 0 | 0 | LARGE |
| marginal:difficulty | 4 | 4 | 0 | 0 | 0 | LARGE |
| marginal:dimension | 7 | 7 | 0 | 0 | 0 | LARGE |
| marginal:domain | 5 | 5 | 0 | 0 | 0 | LARGE |
| marginal:entity_type | 63 | 63 | 0 | 0 | 0 | LARGE |
| marginal:language | 60 | 60 | 0 | 0 | 0 | LARGE |

## By risk tier
| tier | cells | well | under | empty | shortfall | verdict |
|---|---:|---:|---:|---:|---:|---|
| critical | 214 | 214 | 0 | 0 | 0 | LARGE |
| long_tail | 10 | 10 | 0 | 0 | 0 | LARGE |
| standard | 486 | 486 | 0 | 0 | 0 | LARGE |

## Claim ladder (sampling-design.md §7)
- **Marginals** (per language/type/domain/difficulty/adversarial/dimension): single-factor recall claims with 95% Wilson CIs.
- **Named 2-ways** (language×entity-type rectangle, domain×track, adversarial-type×entity-type): estimable on committed cells only.
- **Unnamed 2-way / ≥3-way / full grid**: NOT estimable — exploratory only.

_Power on a synthetic cell is precision on the synthetic distribution, not external validity (cf. FR-027 real-data correlation slice)._
