"""S3-08 — NFR-005 / AX-004 cross-module separation audit ([AUDIT]).

Now that BOTH families exist (anonymization.py = DC-06, pseudonymization.py = DC-08), pin the
headline guarantee ACROSS modules: the anon and pseudo metric families are distinct and are
NEVER fused into a single "de-identification" / "combined" / "overall" score. Pseudonymity and
anonymity are different legal/technical properties (EDPB Art 4(5) vs GDPR anonymisation) and the
benchmark deliberately refuses to collapse them into one number.

These are AUDIT tests: a forbidden name appearing in a DISCLAIMER docstring ("there is
deliberately no ``combined`` field") is fine — what is forbidden is a forbidden name *defined*
as a public symbol (a top-level def/class/assignment, a dataclass field, or a public ``__all__``
export) that fuses the two families. So the check is structural (AST + live introspection),
never a naive substring grep — and it still includes a definition-anchored source grep as the
§6 test-#6 requires.
"""
import ast
import inspect
from pathlib import Path

import pii_anon_datasets.scoring as scoring
from pii_anon_datasets.scoring import anonymization as anon
from pii_anon_datasets.scoring import pseudonymization as pseudo

# Names that would signal a MERGED de-identification score fusing the anon + pseudo families.
_FORBIDDEN_MERGED_NAMES = frozenset({
    "combined",
    "deid",
    "de_identification_score",
    "overall_score",
    "total_collisions",
})

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src/pii_anon_datasets/scoring"
_ANON_SRC = _SRC_ROOT / "anonymization.py"
_PSEUDO_SRC = _SRC_ROOT / "pseudonymization.py"


def _defined_names(source: str) -> set[str]:
    """All names a module DEFINES — top-level def/class/assignment + every class attribute
    (dataclass field annotations and assignments). Crucially this ignores names that appear
    only inside docstrings / comments / string literals (the disclaimer prose)."""
    tree = ast.parse(source)
    names: set[str] = set()

    def add_target(t: ast.expr) -> None:
        if isinstance(t, ast.Name):
            names.add(t.id)
        elif isinstance(t, (ast.Tuple, ast.List)):
            for e in t.elts:
                add_target(e)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                add_target(tgt)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            # dataclass field: ``combined: float`` etc.
            names.add(node.target.id)
    return names


# ── 6. anon and pseudo are SEPARATE modules with no merged-metric symbol in EITHER ────────
def test_nfr_005_anon_and_pseudo_are_separate_modules():
    # they are genuinely distinct modules
    assert anon.__name__ != pseudo.__name__
    assert Path(anon.__file__).name == "anonymization.py"
    assert Path(pseudo.__file__).name == "pseudonymization.py"

    # neither imports the other's public result type into a combined verdict: the anon module
    # does not reference PseudonymizationReport, and the pseudo module does not reference
    # ParetoPoint (i.e. no module pulls the other family's result type in to fuse them).
    assert not hasattr(anon, "PseudonymizationReport")
    assert not hasattr(pseudo, "ParetoPoint")

    # a DEFINITION-anchored grep of BOTH module sources finds no forbidden merged name defined
    # as a public symbol (disclaimer prose mentioning the names is allowed and present).
    for src_path in (_ANON_SRC, _PSEUDO_SRC):
        defined = _defined_names(src_path.read_text(encoding="utf-8"))
        public_defined = {n for n in defined if not n.startswith("_")}
        offenders = public_defined & _FORBIDDEN_MERGED_NAMES
        assert not offenders, f"{src_path.name} defines merged-metric symbol(s): {offenders}"

    # cross-check against the LIVE module namespaces (catches a re-export, not just a def):
    for mod in (anon, pseudo):
        public = {n for n in vars(mod) if not n.startswith("_")}
        assert not (public & _FORBIDDEN_MERGED_NAMES), (
            f"{mod.__name__} exposes a merged-metric symbol"
        )

    # the two result types never expose a fused scalar: no __float__, and none of the
    # forbidden axis-merging attributes on the ParetoPoint / PseudonymizationReport classes.
    for cls in (anon.ParetoPoint, pseudo.PseudonymizationReport):
        assert not hasattr(cls, "__float__"), f"{cls.__name__} must not be float-coercible"
        for name in _FORBIDDEN_MERGED_NAMES:
            assert not hasattr(cls, name), f"{cls.__name__} must not expose '{name}'"
    # ParetoPoint's two axes are objects of DIFFERENT types — structurally unmergeable.
    anon_fields = {f for f in anon.ParetoPoint.__dataclass_fields__}
    assert {"residual_risk", "utility"} <= anon_fields
    # pseudo report keeps the two collision integers SEPARATE (never a summed total).
    pseudo_fields = set(pseudo.PseudonymizationReport.__dataclass_fields__)
    assert {"intended_linkage_collisions", "unintended_crypto_collisions"} <= pseudo_fields
    assert "total_collisions" not in pseudo_fields


# ── 7. no combined de-id callable in the scoring PUBLIC api (__all__) ─────────────────────
def test_nfr_005_no_combined_deid_callable_in_scoring_public_api():
    public_api = set(scoring.__all__)

    # no public export's name itself advertises a fused de-id / combined / overall score
    fused_tokens = ("combined", "deid", "de_identification", "overall", "total_collisions")
    for name in public_api:
        low = name.lower()
        assert not any(tok in low for tok in fused_tokens), (
            f"scoring.__all__ exports a fused-de-id-named symbol: {name}"
        )

    # the two family entry points exist and return DISTINCT, non-fused result types
    assert "score_anonymization" in public_api
    assert "score_pseudonymization" in public_api
    anon_ret = inspect.signature(scoring.score_anonymization).return_annotation
    pseudo_ret = inspect.signature(scoring.score_pseudonymization).return_annotation
    # they return different types (Pareto point vs pseudonymization report) — never one merged score
    assert anon_ret != pseudo_ret

    # and no public callable returns a bare float/int "de-id score" fusing the families:
    # every public scorer either returns a structured result object or is a non-fusing helper.
    for name in public_api:
        obj = getattr(scoring, name)
        if not callable(obj) or inspect.isclass(obj):
            continue
        try:
            ret = inspect.signature(obj).return_annotation
        except (ValueError, TypeError):
            continue
        # a fused de-id score would be a scalar return; the scorers return rich result objects.
        assert ret not in (float, int, "float", "int"), (
            f"public callable {name} returns a scalar — risk of a fused de-id score"
        )
