"""Per-cloud-provider supported-language allowlist + dataset-code -> provider-locale mapping.

This is the honesty guard AND the cost bound for the multilingual cloud baseline run. PII-Anon's ``test``
split spans 60 BCP-47 languages, but the three cloud DLP services each support PII detection for only a
SUBSET — and forcing an unsupported language (e.g. ``recognize_pii_entities(..., language="en")`` on
Hindi text) both burns budget and emits garbage that would silently deflate that language's scores. So the
orchestrator runs each provider only over the languages it officially supports; everything else is
RECORDED as ``unsupported-language`` (never run).

Pure-stdlib (NFR-004): just frozensets + a dict. Imported at adapter module-load — no heavy library.

Sources (verify at run time — provider language coverage changes):
  * AWS Comprehend ``DetectPiiEntities`` — English-only (the real-time PII API).
  * Azure AI Language PII (``recognize_pii_entities``) — a documented GA subset; here the ones that overlap
    PII-Anon's major languages. Azure uses locale strings (``pt-PT``, ``zh-hans``) where the dataset uses a
    bare ISO-639-1 code, so :func:`api_code` maps them.
  * GCP Sensitive Data Protection ``inspect_content`` — broad infoType coverage; scoped here to PII-Anon's
    12 major languages (each >6k records) for a meaningful, comparable table (the 48-language tail is
    ~50 records each). DLP takes no language argument, so only the allowlist matters for GCP.
"""

from __future__ import annotations

# PII-Anon's 12 "major" languages (each holds >6k of the 115,618 test records; ~96% of the split).
_MAJOR: frozenset[str] = frozenset(
    {"en", "nl", "hi", "ko", "pt", "it", "es", "ar", "zh", "fr", "ja", "de"}
)

# provider -> the dataset BCP-47 codes it officially supports for PII detection.
SUPPORTED: dict[str, frozenset[str]] = {
    "aws": frozenset({"en"}),
    "azure": frozenset({"en", "es", "fr", "de", "it", "pt", "nl", "zh", "ja", "ko"}),
    "gcp": _MAJOR,
}

# provider -> {dataset code: provider locale string}, where the provider's API code differs from the
# dataset's bare ISO-639-1 code. Anything not listed is passed through unchanged (identity).
_API_CODE: dict[str, dict[str, str]] = {
    "aws": {},  # AWS uses the bare ISO-639-1 code (and only ever 'en' here).
    "azure": {"pt": "pt-PT", "zh": "zh-hans"},
    "gcp": {},  # DLP takes no language argument.
}


def supported(provider: str) -> frozenset[str]:
    """The set of dataset language codes ``provider`` can score PII on (empty for an unknown provider)."""
    return SUPPORTED.get(provider, frozenset())


def is_supported(provider: str, language: str) -> bool:
    """True iff ``provider`` officially supports PII detection for the dataset ``language`` code."""
    return language in SUPPORTED.get(provider, frozenset())


def api_code(provider: str, language: str) -> str:
    """Map the dataset's BCP-47 ``language`` code to ``provider``'s own locale string (identity by default)."""
    return _API_CODE.get(provider, {}).get(language, language)
