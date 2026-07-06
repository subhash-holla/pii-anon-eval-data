"""Multilingual cloud-detector support — the seam that lets the budget-gated cloud DLP detectors run over
the full multilingual ``test`` split instead of English only.

Three things are under test, all offline (the cloud SDKs are FAKED — never called for real, mirroring the
build-behind-keys / budget-gated contract):

1. A per-provider **supported-language allowlist** (the honesty guard + the cost bound — AWS Comprehend PII
   is English-only; Azure supports a documented subset; GCP DLP covers the major languages). A provider is
   never asked to score a language it can't, which would both burn budget and emit garbage.
2. The cloud adapters **thread the run language** (a settable ``language`` attribute) into the API call,
   mapping the dataset's BCP-47 code to the provider's own locale string (e.g. dataset ``pt`` -> Azure
   ``pt-PT``; ``zh`` -> ``zh-hans``). GCP DLP ``inspect_content`` takes no language argument, so it only
   participates in the allowlist.
3. The **orchestrator** sets ``adapter.language`` from the run's ``dataset_info`` and records a new
   ``unsupported-language`` status (never crashes, never silently runs en-on-Hindi) for an unsupported
   (provider, language) pair — via an OPTIONAL ``supports_language`` hook, so local adapters are untouched.
"""

from __future__ import annotations

import importlib
import pathlib
import sys
import types

import pytest

# Repo-root holds the namespace-package `baselines/` adapter modules (mirrors the registry at run time).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from pii_anon_datasets.baselines import cloud_languages as cl
from pii_anon_datasets.baselines.contract import AdapterSpan
from pii_anon_datasets.baselines.orchestrator import score_detectors


# --------------------------------------------------------------------------------------------------------
# 1. per-provider supported-language allowlist
# --------------------------------------------------------------------------------------------------------
def test_aws_pii_supports_english_only() -> None:
    # AWS Comprehend DetectPiiEntities is documented English-only — scoping it elsewhere is a forgery.
    assert cl.is_supported("aws", "en") is True
    assert cl.is_supported("aws", "fr") is False
    assert cl.is_supported("aws", "hi") is False


def test_azure_supports_its_documented_subset_not_all_60() -> None:
    assert cl.is_supported("azure", "fr") is True
    assert cl.is_supported("azure", "pt") is True
    assert cl.is_supported("azure", "hi") is False  # not a documented Azure PII language


def test_gcp_supports_the_major_languages_but_not_the_50_record_tail() -> None:
    assert cl.is_supported("gcp", "en") is True
    assert cl.is_supported("gcp", "hi") is True
    assert cl.is_supported("gcp", "cy") is False  # a 48-record tail language is out of comparison scope


def test_every_provider_supports_english_and_returns_a_frozenset() -> None:
    for provider in ("aws", "azure", "gcp"):
        langs = cl.supported(provider)
        assert isinstance(langs, frozenset)
        assert "en" in langs


def test_unknown_provider_supports_nothing() -> None:
    assert cl.is_supported("nope", "en") is False
    assert cl.supported("nope") == frozenset()


# --------------------------------------------------------------------------------------------------------
# 2. dataset BCP-47 code -> provider locale string
# --------------------------------------------------------------------------------------------------------
def test_azure_api_code_maps_dataset_codes_to_azure_locales() -> None:
    assert cl.api_code("azure", "pt") == "pt-PT"
    assert cl.api_code("azure", "zh") == "zh-hans"
    assert cl.api_code("azure", "en") == "en"  # identity where the codes already agree


def test_aws_api_code_is_identity() -> None:
    assert cl.api_code("aws", "en") == "en"


# --------------------------------------------------------------------------------------------------------
# 3. the cloud adapters thread the run language into the API call
# --------------------------------------------------------------------------------------------------------
def _azure_adapter():
    return importlib.import_module("baselines.azure_baseline").ADAPTER


def _aws_adapter():
    return importlib.import_module("baselines.aws_comprehend_baseline").ADAPTER


def test_azure_detect_sends_the_mapped_run_language(monkeypatch) -> None:
    a = _azure_adapter()
    captured: dict[str, object] = {}

    def recognize_pii_entities(docs, language, string_index_type):  # noqa: ARG001
        captured["language"] = language
        return [types.SimpleNamespace(is_error=False, entities=[])]

    monkeypatch.setattr(a, "language", "pt", raising=False)
    a.detect("Olá", types.SimpleNamespace(recognize_pii_entities=recognize_pii_entities))
    assert captured["language"] == "pt-PT"  # dataset 'pt' -> Azure locale (proves the attr is read + mapped)


def test_azure_detect_defaults_to_english(monkeypatch) -> None:
    a = _azure_adapter()
    captured: dict[str, object] = {}

    def recognize_pii_entities(docs, language, string_index_type):  # noqa: ARG001
        captured["language"] = language
        return [types.SimpleNamespace(is_error=False, entities=[])]

    monkeypatch.setattr(a, "language", "en", raising=False)
    a.detect("hi", types.SimpleNamespace(recognize_pii_entities=recognize_pii_entities))
    assert captured["language"] == "en"


def test_aws_detect_sends_the_run_language(monkeypatch) -> None:
    a = _aws_adapter()
    captured: dict[str, object] = {}

    def detect_pii_entities(Text, LanguageCode):  # noqa: ARG001, N803 - mirrors the boto3 kwarg name
        captured["lang"] = LanguageCode
        return {"Entities": []}

    monkeypatch.setattr(a, "language", "en", raising=False)
    a.detect("x", types.SimpleNamespace(detect_pii_entities=detect_pii_entities))
    assert captured["lang"] == "en"


def test_cloud_adapters_expose_a_supports_language_hook() -> None:
    azure = _azure_adapter()
    assert azure.supports_language("fr") is True
    assert azure.supports_language("hi") is False
    assert _aws_adapter().supports_language("fr") is False  # AWS PII is English-only


# --------------------------------------------------------------------------------------------------------
# 4. orchestrator: an unsupported (provider, language) is RECORDED, never run
# --------------------------------------------------------------------------------------------------------
def _rec(rid: str, lang: str, text: str = "John Smith") -> dict:
    return {
        "record_id": rid,
        "text": text,
        "language": lang,
        "domain": "general",
        "annotations": [{"start": 0, "end": 10, "entity_type": "PERSON_NAME"}],
    }


class _FakeCloudAdapter:
    """A cloud-shaped adapter (has ``language`` + ``supports_language``) that records whether it was run."""

    name = "azure"
    model_id = "fake-azure"
    label_map = {"PERSON": "PERSON_NAME"}
    deterministic = False
    language = "en"

    def __init__(self, supported: set[str]) -> None:
        self._supported = supported
        self.built = False
        self.detect_calls = 0

    def available(self) -> bool:
        return True

    def supports_language(self, lang: str) -> bool:
        return lang in self._supported

    def build(self) -> object:
        self.built = True
        return object()

    def detect(self, text: str, model: object) -> list[AdapterSpan]:  # noqa: ARG002
        self.detect_calls += 1
        return [AdapterSpan(0, 10, "PERSON_NAME", text[0:10])]

    def coverage(self) -> int:
        return 1


def test_orchestrator_skips_unsupported_language_without_building_or_detecting() -> None:
    adapter = _FakeCloudAdapter(supported={"en"})
    results = score_detectors([_rec("r1", "hi")], [adapter], dataset_info={"language": "hi"})
    block = results.detectors["azure"]
    assert block["status"] == "unsupported-language"
    assert adapter.built is False  # checked BEFORE the expensive build()
    assert adapter.detect_calls == 0
    assert "azure" not in {row["detector"] for row in results.ranking}  # excluded from the leaderboard


def test_orchestrator_runs_supported_language_and_threads_it_onto_the_adapter() -> None:
    adapter = _FakeCloudAdapter(supported={"en", "fr"})
    results = score_detectors([_rec("r1", "fr")], [adapter], dataset_info={"language": "fr"})
    assert results.detectors["azure"]["status"] == "scored"
    assert adapter.language == "fr"  # orchestrator threaded the run language onto the adapter pre-build
    assert adapter.detect_calls == 1


def test_orchestrator_leaves_local_adapters_untouched_when_no_language_hooks() -> None:
    # A local-shaped adapter (no `language`, no `supports_language`) must score exactly as before, even on a
    # non-English record — the multilingual cloud plumbing is invisible to it.
    class _LocalAdapter:
        name = "regexish"
        model_id = "local"
        label_map = {"X": "PERSON_NAME"}

        def available(self) -> bool:
            return True

        def build(self) -> object:
            return object()

        def detect(self, text: str, model: object) -> list[AdapterSpan]:  # noqa: ARG002
            return [AdapterSpan(0, 10, "PERSON_NAME", text[0:10])]

        def coverage(self) -> int:
            return 1

    results = score_detectors([_rec("r1", "hi")], [_LocalAdapter()], dataset_info={"language": "hi"})
    assert results.detectors["regexish"]["status"] == "scored"
