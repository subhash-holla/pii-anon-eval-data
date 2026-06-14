"""Detector adapters conform to the uniform contract.

Pure label-map / coverage / availability assertions run with NO heavy library. The offline detectors
(regex, scrubadub) get a live ``detect()`` smoke. Model-backed detectors (gliner / piiranha / spacy /
stanza / flair) get a live smoke ONLY when ``PII_ANON_RUN_LIVE_DETECTORS=1`` (off in normal CI — they
pull multi-GB models / network); their pure logic (label map, coverage, contract conformance) is always
tested. Label maps for presidio / gliner / piiranha MIRROR the audited sister-repo maps (re-implemented,
never imported — the forbidden edge); spacy / scrubadub / stanza / flair maps are designed here.
"""

from __future__ import annotations

import importlib
import os
import pathlib
import sys
import types

import pytest
from pii_anon_datasets import taxonomy
from pii_anon_datasets.baselines import contract
from pii_anon_datasets.baselines.contract import AdapterSpan, DetectorAdapter

# Repo-root holds the (namespace-package) `baselines/` adapter modules — put it on the path so
# `import baselines.<name>_baseline` resolves (mirrors what the registry does at run time).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

# (detector name, repo-root module). The 8 local + the key-gated LLM.
_ALL = [
    ("regex", "baselines.regex_baseline"),
    ("presidio", "baselines.presidio_baseline"),
    ("spacy", "baselines.spacy_baseline"),
    ("gliner", "baselines.gliner_baseline"),
    ("piiranha", "baselines.piiranha_baseline"),
    ("scrubadub", "baselines.scrubadub_baseline"),
    ("stanza", "baselines.stanza_baseline"),
    ("flair", "baselines.flair_baseline"),
    ("llm", "baselines.llm_baseline"),
]
_MODEL_BACKED = ["gliner", "piiranha", "spacy", "stanza", "flair"]
_CLOUD = [
    ("aws", "baselines.aws_comprehend_baseline"),
    ("gcp", "baselines.gcp_dlp_baseline"),
    ("azure", "baselines.azure_baseline"),
]
_RUN_LIVE = os.environ.get("PII_ANON_RUN_LIVE_DETECTORS") == "1"


def _adapter(module_name: str):
    return importlib.import_module(module_name).ADAPTER


@pytest.mark.parametrize(("name", "module"), _ALL)
def test_adapter_conforms_to_contract(name: str, module: str) -> None:
    a = _adapter(module)
    assert isinstance(a, DetectorAdapter), f"{name} must satisfy the DetectorAdapter contract"
    assert a.name == name
    assert isinstance(a.available(), bool)  # a pure probe — must not raise / import the heavy lib


@pytest.mark.parametrize(("name", "module"), _ALL)
def test_adapter_label_map_targets_are_canonical_and_coverage_matches(name: str, module: str) -> None:
    a = _adapter(module)
    targets = {v for v in a.label_map.values() if v is not None}
    assert targets <= taxonomy.CANONICAL_ENTITY_TYPES, f"{name} maps to an off-taxonomy type: {targets}"
    assert a.coverage() == contract.coverage_of(a.label_map) > 0
    assert contract.lossiness(a.label_map)["of_total"] == taxonomy.ENTITY_TYPE_COUNT


def test_mirrored_and_designed_label_maps_spot_checks() -> None:
    gliner = _adapter("baselines.gliner_baseline")
    assert gliner.map_label("Person") == "PERSON_NAME"  # case-insensitive prompt label
    assert gliner.map_label("not a pii label") is None

    piiranha = _adapter("baselines.piiranha_baseline")
    assert piiranha.map_label("B-GIVENNAME") == "PERSON_NAME"  # BIO prefix tolerated
    assert piiranha.map_label("TITLE") is None  # honorific intentionally dropped

    presidio = _adapter("baselines.presidio_baseline")
    assert presidio.map_label("LOCATION") == "LOCATION_NAME"  # reconciled (was STREET_ADDRESS)
    assert presidio.map_label("DATE_TIME") == "DATE_OF_BIRTH"  # reconciled (was TIMESTAMP)
    assert presidio.map_label("NRP") is None  # too coarse — dropped
    assert presidio.map_label("US_BANK_NUMBER") == "BANK_ACCOUNT_NUMBER"  # correct Presidio label

    spacy = _adapter("baselines.spacy_baseline")
    assert spacy.map_label("PERSON") == "PERSON_NAME"
    assert spacy.map_label("DATE") is None  # generic date dropped (no FP inflation)

    flair = _adapter("baselines.flair_baseline")
    assert flair.map_label("PER") == "PERSON_NAME"
    assert flair.map_label("MISC") is None


def test_llm_has_open_vocabulary_no_projection_ceiling() -> None:
    llm = _adapter("baselines.llm_baseline")
    assert llm.coverage() == taxonomy.ENTITY_TYPE_COUNT  # identity over all 63 — no label-map ceiling
    assert llm.map_label("NAME") == "PERSON_NAME"  # a free-text alias
    assert llm.available() in (True, False)  # key-gated; default env has no key → False


# ---- offline live smokes (no model download) ----
def test_regex_live_detect_finds_email_and_ssn() -> None:
    a = _adapter("baselines.regex_baseline")
    found = {s.entity_type for s in a.detect("Reach jane@example.com, SSN 123-45-6789.", a.build())}
    assert {"EMAIL_ADDRESS", "SOCIAL_SECURITY_NUMBER"} <= found


def test_scrubadub_live_detect_finds_email() -> None:
    pytest.importorskip("scrubadub")
    a = _adapter("baselines.scrubadub_baseline")
    spans = a.detect("Please contact me at jane.doe@example.com today.", a.build())
    assert any(s.entity_type == "EMAIL_ADDRESS" for s in spans)
    assert all(isinstance(s, AdapterSpan) for s in spans)


# ---- model-backed live smokes (gated; off in normal CI) ----
@pytest.mark.skipif(not _RUN_LIVE, reason="set PII_ANON_RUN_LIVE_DETECTORS=1 to run model-backed detectors")
@pytest.mark.parametrize("name", _MODEL_BACKED)
def test_model_backed_live_detect(name: str) -> None:
    module = dict(_ALL)[name]
    a = _adapter(module)
    if not a.available():
        pytest.skip(f"{name} library not importable")
    spans = a.detect("My name is John Smith and I work at Acme Corp in Paris.", a.build())
    assert all(s.entity_type in taxonomy.CANONICAL_ENTITY_TYPES for s in spans)
    assert all(isinstance(s, AdapterSpan) for s in spans)


# ---- cloud adapters: built behind keys, NEVER run here (pure conformance only) ----
@pytest.mark.parametrize(("name", "module"), _CLOUD)
def test_cloud_adapter_conforms_without_running(name: str, module: str) -> None:
    a = _adapter(module)
    assert isinstance(a, DetectorAdapter) and a.name == name
    assert isinstance(a.available(), bool)  # a key+lib probe; must never raise
    assert a.deterministic is False  # cloud model versions can change server-side -> INDICATIVE only
    targets = {v for v in a.label_map.values() if v is not None}
    assert targets <= taxonomy.CANONICAL_ENTITY_TYPES
    assert a.coverage() == contract.coverage_of(a.label_map) > 0


def test_cloud_label_map_spot_checks() -> None:
    assert _adapter("baselines.aws_comprehend_baseline").map_label("SSN") == "SOCIAL_SECURITY_NUMBER"
    assert _adapter("baselines.gcp_dlp_baseline").map_label("EMAIL_ADDRESS") == "EMAIL_ADDRESS"
    # Azure normalizes case / spaces / underscores before lookup.
    assert _adapter("baselines.azure_baseline").map_label("PhoneNumber") == "PHONE_NUMBER"


# ---- GCP DLP per-minute quota (429) retry/backoff ----
# DLP `content.inspect` enforces a per-minute request quota; a full-corpus run sustains a rate above it and
# gets RESOURCE_EXHAUSTED (429) on a fraction of records. Unretried, each becomes a permanent record-error
# whose gold spans are forced to false-negatives — silently deflating recall. detect() must retry 429s.
def _fake_finding(info_type: str, start: int, end: int):
    return types.SimpleNamespace(
        info_type=types.SimpleNamespace(name=info_type),
        location=types.SimpleNamespace(codepoint_range=types.SimpleNamespace(start=start, end=end)),
    )


def _fake_inspect_response(findings):
    return types.SimpleNamespace(result=types.SimpleNamespace(findings=findings))


def test_gcp_detect_retries_resource_exhausted_then_succeeds(monkeypatch) -> None:
    """A 429 ResourceExhausted on a record is retried with backoff and recovered — not counted as an error."""
    a = _adapter("baselines.gcp_dlp_baseline")

    class ResourceExhausted(Exception):
        """Stands in for google.api_core.exceptions.ResourceExhausted (matched by class name, import-free)."""

    text = "Mail jane@acme.com now"
    s = text.index("jane@acme.com")
    e = s + len("jane@acme.com")
    resp = _fake_inspect_response([_fake_finding("EMAIL_ADDRESS", s, e)])

    calls = {"n": 0}

    def inspect_content(request):  # noqa: ARG001 - fake ignores the request
        calls["n"] += 1
        if calls["n"] < 3:
            raise ResourceExhausted("429 Quota exceeded ... requests per minute of service 'dlp.googleapis.com'")
        return resp

    monkeypatch.setattr(a, "backoff_base_s", 0, raising=False)  # don't actually sleep between retries
    spans = a.detect(text, types.SimpleNamespace(inspect_content=inspect_content))

    assert calls["n"] == 3  # failed twice, retried, succeeded on the third attempt
    assert [(sp.entity_type, sp.start, sp.end) for sp in spans] == [("EMAIL_ADDRESS", s, e)]


def test_gcp_detect_reraises_after_exhausting_retry_budget(monkeypatch) -> None:
    """If 429s never clear, detect() retries then re-raises — the orchestrator still records a real
    record-error. We retry transient throttling; we never silently swallow."""
    a = _adapter("baselines.gcp_dlp_baseline")

    class ResourceExhausted(Exception): ...

    calls = {"n": 0}

    def inspect_content(request):  # noqa: ARG001
        calls["n"] += 1
        raise ResourceExhausted("429 Quota exceeded")

    monkeypatch.setattr(a, "backoff_base_s", 0, raising=False)
    with pytest.raises(ResourceExhausted):
        a.detect("Mail jane@acme.com", types.SimpleNamespace(inspect_content=inspect_content))
    assert calls["n"] >= 2  # retried before giving up, then re-raised


def test_gcp_detect_does_not_retry_non_rate_limit_errors(monkeypatch) -> None:
    """Retry is scoped to 429/ResourceExhausted only — any other error propagates immediately, unmasked."""
    a = _adapter("baselines.gcp_dlp_baseline")

    class InvalidArgument(Exception): ...

    calls = {"n": 0}

    def inspect_content(request):  # noqa: ARG001
        calls["n"] += 1
        raise InvalidArgument("malformed request")

    monkeypatch.setattr(a, "backoff_base_s", 0, raising=False)
    with pytest.raises(InvalidArgument):
        a.detect("x", types.SimpleNamespace(inspect_content=inspect_content))
    assert calls["n"] == 1  # not retried — only throttle errors are


def test_aws_available_resolves_env_or_shared_credentials_file(monkeypatch) -> None:
    """AWS is usable via env keys, AWS_PROFILE, OR the shared ~/.aws/credentials file (boto3's default
    chain) — available() must recognize the shared file, not only env vars."""
    mod = importlib.import_module("baselines.aws_comprehend_baseline")
    a = mod.ADAPTER
    real_exists = os.path.exists
    # No env creds + no shared file -> unavailable.
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.setattr(mod.os.path, "exists", lambda p: False if str(p).endswith(".aws/credentials") else real_exists(p))
    assert a.available() is False
    # Shared credentials file present -> available (boto3 will resolve it).
    monkeypatch.setattr(mod.os.path, "exists", lambda p: True if str(p).endswith(".aws/credentials") else real_exists(p))
    assert a.available() is True
    # Env key present -> available regardless of file.
    monkeypatch.setattr(mod.os.path, "exists", lambda p: False if str(p).endswith(".aws/credentials") else real_exists(p))
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIA-test")
    assert a.available() is True
