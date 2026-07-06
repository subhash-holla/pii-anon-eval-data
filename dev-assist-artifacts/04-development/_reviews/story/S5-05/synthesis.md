# Story Gate Synthesis — S5-05 (`pii-anon` CLI: 5 thin dispatch verbs; FR-024 / DX-03)

**Gate:** story · **Scope:** S5-05 · **Aggregate verdict: APPROVE** · **Iterations:** 1 · **Date:** 2026-05-30

| Reviewer | Verdict | Findings |
|---|---|---|
| code-quality | ✅ APPROVE | 0 |
| security-sast | ✅ APPROVE | 0 (load-bearing — subprocess audited clean) |
| requirements-coverage | ✅ APPROVE | 0 |
| traceability | ✅ APPROVE | 0 |
| axiom-compliance | ✅ APPROVE | 0 |

**Aggregate: APPROVE** (zero findings across all five reviewers — fully clean gate).

## Joint signals

- **NFR-018 power-gate-on guardrail ENFORCED** (security-sast + axiom-compliance + requirements-coverage):
  `_cmd_validate` forwards `args.rest` verbatim and injects nothing; `--no-power-gate` appears ONLY in
  comments (cli.py:14/71/72), zero in executable code; the captured spawned argv for `main(["validate"])`
  is `[python, …/scripts/validate.py]` with `--no-power-gate` ABSENT, and `validate.py`'s own
  `store_true` default-False means the gate runs by default. Test `test_nfr_018_*` asserts the argv.
- **No-corpus-regeneration guardrail** (axiom-compliance): `_cmd_generate` injects no `--output`; the
  generator's own default is `*_generated.jsonl`, never the frozen `pii_anon.jsonl.gz` — test #5 asserts
  the spawned argv contains neither `--output` nor the corpus path.
- **Subprocess safety** (security-sast, load-bearing): one call site `subprocess.run([sys.executable,
  str(script), *args])` — list argv, **no `shell=True`**, hardcoded trusted script paths under
  `_repo_root()`, a line-scoped+justified `# noqa: S603`, clean exit-2 on a missing script.
- **Thin + pure-stdlib + lazy** (axiom + code-quality): AST shows top-level imports are stdlib only
  (`{__future__, argparse, collections, gzip, json, pathlib, subprocess, sys}`); `distribution` /
  `get_data_path` / `leaderboard` are lazy inside handlers; `import cli` works with pyarrow/spacy/
  mlcroissant blocked; no scoring/stats metric module at top level (no business logic); `main -> int`.

## Findings forwarded (sprint-gate signal)

- **requirements-coverage + traceability (FR-024 ROLL-UP)**: with S5-05 landing, **FR-024 is now fully
  implemented** across S5-02 (Parquet) + S5-03 (Croissant + dataset card) + S5-04 (spaCy + CoNLL) + S5-05
  (CLI), with JSONL pre-existing. FR-024 can be rolled up as **fully closed at the S5 sprint gate**.
- The `leaderboard` verb's backend is the named successor **S6** (graceful "ships in S6" stub now,
  exit 2 + clear message, no traceback) — an accepted deferral; S6 wires the verb to the real package.

## §8b deviations (all sound; verified by reviewers)

1. **`parse_known_args` instead of `nargs=argparse.REMAINDER`** for the passthrough verbs — a *correctness*
   improvement: `REMAINDER` empirically raises `SystemExit(2)` on a leading option like `validate
   --summary-only`, which would break the NFR-018 / FR-024 arg-forwarding (§7, test #4). Handler bodies
   unchanged (still read `args.rest`); the no-injection contract is preserved.
2. **strict-mypy refinements** — `_iter_jsonl -> Iterator[dict[str, object]]` + a scoped `# type:
   ignore[attr-defined]` on the absent-until-S6 `leaderboard` import (the `except ImportError` is the
   graceful contract). Same class as S5-04.
3. **Non-behavioral** `if __name__ == "__main__": raise SystemExit(main())` so `python -m
   pii_anon_datasets.cli` works.

## Outcome

S5-05 → **DONE**. The `pii-anon` console entry ships with five thin dispatch verbs
(`generate`/`score`/`export`/`validate`/`leaderboard`), zero business logic in `cli.py`, the NFR-018
power gate kept ON, the no-corpus-regeneration guardrail held, and a single copy-paste CI invocation
(`pii-anon validate`, DX-03). **FR-024 is now fully closed** (Parquet + Croissant/card + spaCy/CoNLL +
CLI + JSONL). Evidence: RED `c003174` → GREEN `ded2281` → REFACTOR `7efedbd` → docs `ec05e3f`; **250
passed / 1 skipped** (242 prior + 8 new, 0 regressions); ruff + mypy --strict clean; subprocess audited
clean (no `shell=True`); `scripts/` + `baselines/` + corpus / lattice / tags untouched.
