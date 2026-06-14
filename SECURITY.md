# Security Policy

PII-Anon is a **100% synthetic** PII benchmark (no real personal data — AX-001) plus a pure-stdlib evaluation
harness. We take both code security and the synthetic-only invariant seriously.

## Supported versions
| Version | Supported |
|---|---|
| 2.0.x | ✅ |
| < 2.0 | ❌ (upgrade via `MIGRATION.md`) |

## Reporting a vulnerability
**Please report privately — do NOT open a public issue for a security problem.**

- **Preferred:** GitHub **Private Vulnerability Reporting** — the repository's *Security* tab → *Report a
  vulnerability*. (Maintainers: enable this under *Settings → Code security and analysis*.)
- **Fallback:** email the maintainer at **subhashholla23@gmail.com** with `[SECURITY]` in the subject.

Please include a description, reproduction steps, the affected version/commit, and the impact. We aim to
acknowledge within **5 business days** and to share a remediation timeline after triage. Please allow a
reasonable disclosure window before any public discussion.

## In scope
- Code-execution / injection / path-traversal / unsafe-deserialization issues in the harness, CLIs, exporters,
  or distribution tooling.
- Dependency vulnerabilities in the declared optional extras.
- **Real-PII contamination** — if any record is found to contain *real* personal data, treat it as a
  high-severity issue (it violates AX-001, the load-bearing legal/ethical invariant). Report privately with the
  `record_id`; do **not** post the suspected real data publicly.

## Out of scope
- The synthetic records are public-domain (CC0-1.0) and contain no real PII by design — they are not a
  confidentiality boundary.
- Findings that require a modified/poisoned local corpus or a non-default, untrusted input.

## Our commitments
- The scoring/stats/compliance core is **pure-stdlib** with **no outbound network calls** (data-flow-locality);
  the harness runs fully offline.
- Frozen evaluation assets (the committed lattice, the corpus, the version tags) are integrity-checked in CI and
  are never silently mutated.
