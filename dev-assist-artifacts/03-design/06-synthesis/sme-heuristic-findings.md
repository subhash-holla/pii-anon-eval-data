# D6 — SME Heuristic Evaluation Findings

**Stage 3 · D6** · 2026-05-28 · 3 `sme-heuristic-evaluator` agents, framings substituted for a benchmark (methodology/reproducibility · developer-experience/API · governance/ethics/transparency). All verdicts **REQUEST_CHANGES → resolved** via design revisions (folded into `D-implementation-ready-design.md` §"D6 revisions"). Representative panel (3 of 5); real-SME Pass-2 flagged.

> These evaluators read the **actual v1.3.0 code** and caught defects that would have undermined the benchmark — high-value findings now elevated to Development requirements.

## Methodology / reproducibility
| ID | Sev | Finding | Resolution |
|---|---|---|---|
| reidx-01 | **CATASTROPHIC** | RRS headline routes through a *pluggable LLM adversary* → non-reproducible (temp/model-version drift); `llm_baseline.py` already asymmetric (OpenAI temp=0, Anthropic unset) | **Headline RRS = deterministic offline adversary + exposure-index; LLM-adversary = version-stamped SECONDARY.** Epsilon enforced as CI gate (DC-15); adversary version frozen in leaderboard record (DC-13) |
| reidx-02 | MAJOR | `evaluate.py` adds partial matches to BOTH `tp+fp` and `tp+fn` + fractional success → breaks Wilson/Clopper-Pearson (need integer Bernoulli k,n) | **DC-09 defines canonical integer (k,n) per metric on a frozen matching policy; partial-credit F1 reported separately, excluded from binomial CIs** |
| reidx-03 | MAJOR | `evaluate.py` greedy order-dependent matching → different TP/FP across adapters | **Deterministic optimal assignment (Hungarian on overlap + documented tie-break); versioned `matching_policy_version` in every score record** |
| reidx-04 | MAJOR | CI inflation: migration dedups exact-hash only → templated near-dups inflate effective n | **NFR-001 gate tests *effective* (near-dup-collapsed) positive counts, computed in `stats/`; dedup method recorded** |
| reidx-05 | MINOR | migration uses uuid/Counter → determinism leak | **Content-hash IDs + sorted iteration + byte-identical re-run test (DC-15)** |

## Developer-experience / API
| ID | Sev | Finding | Resolution |
|---|---|---|---|
| DX-01 | MAJOR | package rename `pii_anon_datasets`→`pii_anon` breaks published wheel + all imports | **Keep `pii_anon_datasets` as the package (nest `scoring/` under it) OR ship a `pii_anon_datasets` shim re-exporting for ≥1 minor; state chosen name** |
| DX-02 | MAJOR | crosswalk = hardcoded dict w/ silent passthrough `get(type,type)` → unmapped types become phantom FPs; recurring per-release tax | **Crosswalk = declared validated mapping FILE per adapter; fail-loud on unmapped + `--allow-unmapped` opt-out; versioned against schema** |
| DX-03 | MAJOR | no `cli.py`, no `[project.scripts]` → can't `pip install && pii-anon score`; 18 standalone scripts | **Add `[project.scripts] pii-anon = pii_anon...cli:main`; 5 verbs as thin dispatchers over existing `main()`s; one copy-paste CI invocation** |
| DX-04 | MINOR | migration name collision w/ existing `scripts/migrate_v1_to_v2.py` | **Reconcile/rename; reference exact canonical path in build sequence** |
| DX-05 | OBS | license: pyproject `Apache-2.0` vs design "CC0" | **Clarify the intended split: code Apache-2.0, data CC0 (per README); fix loose "CC0" phrasing + NFR-013 doc-currency** |

## Governance / ethics / transparency
| ID | Sev | Finding | Resolution |
|---|---|---|---|
| gov-01 | MAJOR | FR-009 caveat lives in `reporting/` → machine-readable scorer return + `distribution/` exports bypass it | **Caveat is a mandatory non-defaulted field on the RRS/residual-risk VALUE OBJECT in `scoring/core`; any serializer dropping it fails a schema test. The caveat travels with the NUMBER, not the renderer** |
| gov-02 | MAJOR | existing `export_parquet.py:54` flattens `regulatory_domains` into one JSON string → violates FR-022 legally-distinct | **`compliance/` emits N separate typed columns/keys (never merged); export test asserts each regime independently addressable; no "deidentified==anonymized" field; do NOT inherit the flattened column** |
| gov-03 | MAJOR | §0 neutrality reduced to file-presence; nothing structurally stops a `pii-anon-core`-affiliated submission seeing held-out labels | **Held-out append-only log records submitter affiliation + a no-pre-publication-access attestation; anti-gaming flags maintainer-affiliated submissions for recusal. Promote from switch-point to v1 for externally-published scores** |
| gov-04 | MINOR | NFR-005 check catches headline-merge but reporting/compliance could juxtapose into one visual "de-id" verdict | **Extend NFR-005 check to reporting/compliance layer: no shared axis, no combined "de-id" label** |
| gov-05 | OBS | AX-001 no-real-PII scan not named for migrated records + tagged v1.3.0 archive | **AX-001 scan runs on migrated records AND the tagged archive (a retained archive is a published surface)** |

## Cross-framing observations (logged)
- FR-003 advertises **type-relaxed** matching but `evaluate.py` has only strict+partial → add type-relaxed (traceability gap).
- Presidio adapter is **English-only** (`language="en"`) vs FR-001 multilingual → multilingual adapter config needed.
- Per-language slices likely **<200 positives** → NFR-003 power-transparency must label low-power language slices honestly.
- No `governance`/`coi` CLI verb → neutrality discoverable only via GOVERNANCE.md (minor discoverability).

**Net: 1 CATASTROPHIC + 9 MAJOR resolved into design revisions + elevated to Development requirements. Architecture (Modular + Hexagonal + Linear-batch + Info-Dense) survives; the fixes harden reproducibility, adoption, and governance enforcement at the structural layer.**
