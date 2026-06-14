"""Targeted synthetic-record generation for committed-lattice enrichment (P3; AX-001/AX-002).

The one new generation primitive the power work-stream needs: emit ONE record GUARANTEED to
contain exactly one positive annotation of a requested ``entity_type`` in a requested
(language, domain, difficulty, adversarial-type) cell — so ``records_to_generate(cell) ==
deficit(cell)`` (no generate-and-pray).

``EMITTERS`` covers ALL 63 canonical types (reusing ``PIIFactory`` for the 35 it already
emits; local emitters for the 28 gaps), validated complete against the canonical registry at
import (fail-loud — AX-001: never scrape real data to fill a gap). Adversarial cells apply a
FAITHFUL value-level obfuscation (the target value is genuinely transformed, offsets stay
valid), so an enrichment adversarial record is a real attack, not a bare tag.

Synthetic-only (AX-001); seeded/deterministic (AX-002). Records are returned v1-shaped and are
normalized to v2.0.0 by the fill script via ``migration.migrate_record``.
"""
from __future__ import annotations

import base64
import random
import string
import sys
import urllib.parse
from pathlib import Path
from typing import Callable

_HERE = Path(__file__).resolve().parent
for _p in (str(_HERE), str(_HERE.parent), str(_HERE.parent / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from generate_records import PIIFactory, PIIValue, build_record  # noqa: E402
from pii_anon_datasets import taxonomy  # noqa: E402


# ── faithful value-level adversarial transforms (the committed detection-attack set) ─────
_HOMOGLYPHS = {
    "a": "а", "c": "с", "e": "е", "i": "і", "j": "ј", "o": "о", "p": "р",
    "s": "ѕ", "x": "х", "y": "у", "A": "А", "B": "В", "C": "С", "E": "Е",
    "H": "Н", "K": "К", "M": "М", "O": "О", "P": "Р", "T": "Т", "X": "Х",
}
# Broad enough that every digit 0-9 (so every numeric identifier) has a confusion — lets
# ocr_artifact reliably perturb any committed value, including digit-only SSN/CVV/PIN.
_OCR_CONFUSIONS = {
    "0": "O", "1": "I", "2": "Z", "3": "E", "4": "A", "5": "S", "6": "G", "7": "T",
    "8": "B", "9": "g", "O": "0", "I": "1", "Z": "2", "E": "3", "A": "4", "S": "5",
    "G": "6", "T": "7", "B": "8", "l": "1", "o": "0", "g": "9", "s": "5", "b": "6",
}
_LEET = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"}


def _t_homoglyph(s: str, rng: random.Random, rate: float = 0.3) -> str:
    return "".join(_HOMOGLYPHS[c] if (c in _HOMOGLYPHS and rng.random() < rate) else c for c in s)


def _t_zero_width(s: str, rng: random.Random, count: int = 2) -> str:
    if len(s) < 2:
        return s + "​"
    chars = list(s)
    for _ in range(count):
        chars.insert(rng.randint(1, len(chars) - 1), "​")
    return "".join(chars)


def _t_ocr(s: str, rng: random.Random, rate: float = 0.3) -> str:
    eligible = [i for i, c in enumerate(s) if c in _OCR_CONFUSIONS]
    if not eligible:
        return s
    forced = rng.choice(eligible)   # guarantee ≥1 substitution so the attack is never a no-op
    return "".join(
        _OCR_CONFUSIONS[c] if (i in eligible and (i == forced or rng.random() < rate)) else c
        for i, c in enumerate(s)
    )


def _t_leetspeak(s: str, rng: random.Random) -> str:
    return "".join(_LEET.get(c.lower(), c) for c in s)


def _t_mixed_case(s: str, rng: random.Random) -> str:
    return "".join(c.upper() if (c.isalpha() and rng.random() < 0.5) else c.lower() for c in s)


def _t_base64(s: str, rng: random.Random) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


def _t_url_encoding(s: str, rng: random.Random) -> str:
    return urllib.parse.quote(s, safe="")


# entity_type marginal "adversarial" set + adv×entity_type committed set (faithful transforms only).
ADVERSARIAL_TRANSFORMS: dict[str, Callable[[str, random.Random], str]] = {
    "unicode_homoglyph": _t_homoglyph,
    "zero_width_char": _t_zero_width,
    "ocr_artifact": _t_ocr,
    "leetspeak": _t_leetspeak,
    "mixed_case": _t_mixed_case,
    "base64_encoding": _t_base64,
    "url_encoding": _t_url_encoding,
}
COMMITTED_ADVERSARIAL_TYPES: tuple[str, ...] = tuple(sorted(ADVERSARIAL_TRANSFORMS))


# ── local emitters for the 28 canonical types PIIFactory does not cover ──────────────────
def _pv(t: str, value: str, sensitivity: str) -> PIIValue:
    return PIIValue(t, value, taxonomy.category_of(t), sensitivity)


_ETHNICITIES = ["Hispanic", "Asian", "Black", "White", "Native American", "Pacific Islander", "Mixed"]
_GENDERS = ["Male", "Female", "Non-binary", "Transgender", "Prefer not to say"]
_NATIONALITIES = ["American", "British", "German", "French", "Japanese", "Indian", "Brazilian", "Nigerian"]
_EDUCATION = ["High School Diploma", "Associate Degree", "Bachelor's Degree", "Master's Degree", "PhD"]
_MARITAL = ["Single", "Married", "Divorced", "Widowed", "Separated"]
_POLITICAL = ["Democrat", "Republican", "Independent", "Green Party", "Libertarian"]
_RELIGION = ["Christian", "Muslim", "Jewish", "Hindu", "Buddhist", "Atheist", "Agnostic"]
_VEHICLES = ["Toyota Camry", "Honda Civic", "Ford F-150", "Tesla Model 3", "BMW X5", "Subaru Outback"]
_TLDS = ["com", "org", "net", "io", "co.uk"]
_VIN_CHARS = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"  # no I,O,Q per VIN spec


def _h(rng: random.Random, n: int) -> str:
    return "".join(rng.choice("0123456789abcdef") for _ in range(n))


_LOCAL_EMITTERS: dict[str, Callable[[PIIFactory], PIIValue]] = {
    # digital_online
    "AUTHENTICATION_TOKEN": lambda f: _pv("AUTHENTICATION_TOKEN", "Bearer " + _h(f.rng, 40), "direct_identifier"),
    "BIOMETRIC_ID": lambda f: _pv("BIOMETRIC_ID", "BIO-" + _h(f.rng, 16).upper(), "direct_identifier"),
    "DEVICE_IDENTIFIER": lambda f: _pv("DEVICE_IDENTIFIER", "".join(str(f.rng.randint(0, 9)) for _ in range(15)), "direct_identifier"),
    "SOCIAL_MEDIA_HANDLE": lambda f: _pv("SOCIAL_MEDIA_HANDLE", "@" + f.rng.choice(["alex", "sam", "jo", "kai", "max"]) + str(f.rng.randint(1, 9999)), "direct_identifier"),
    "URL": lambda f: _pv("URL", f"https://{f.rng.choice(['site','app','portal','my'])}{f.rng.randint(1,999)}.{f.rng.choice(_TLDS)}/u/{f.rng.randint(1000,999999)}", "direct_identifier"),
    # employment
    "EDUCATION_LEVEL": lambda f: _pv("EDUCATION_LEVEL", f.rng.choice(_EDUCATION), "quasi_identifier"),
    # financial
    "CREDIT_CARD_FRAGMENT": lambda f: _pv("CREDIT_CARD_FRAGMENT", "****-****-****-" + "".join(str(f.rng.randint(0, 9)) for _ in range(4)), "direct_identifier"),
    "CRYPTOCURRENCY_ADDRESS": lambda f: _pv("CRYPTOCURRENCY_ADDRESS", "0x" + _h(f.rng, 40), "direct_identifier"),
    "CVV": lambda f: _pv("CVV", "".join(str(f.rng.randint(0, 9)) for _ in range(3)), "direct_identifier"),
    "PIN": lambda f: _pv("PIN", "".join(str(f.rng.randint(0, 9)) for _ in range(4)), "direct_identifier"),
    # government_legal
    "BAR_NUMBER": lambda f: _pv("BAR_NUMBER", "BAR-" + "".join(str(f.rng.randint(0, 9)) for _ in range(6)), "direct_identifier"),
    "DOCKET_NUMBER": lambda f: _pv("DOCKET_NUMBER", f"{f.rng.randint(2020,2026)}-{f.rng.randint(1000,9999)}-{f.rng.choice(string.ascii_uppercase)}{f.rng.choice(string.ascii_uppercase)}", "direct_identifier"),
    "VEHICLE_IDENTIFICATION_NUMBER": lambda f: _pv("VEHICLE_IDENTIFICATION_NUMBER", "".join(f.rng.choice(_VIN_CHARS) for _ in range(17)), "direct_identifier"),
    # identity_demographics
    "AGE": lambda f: _pv("AGE", str(f.rng.randint(18, 95)), "quasi_identifier"),
    "ETHNICITY": lambda f: _pv("ETHNICITY", f.rng.choice(_ETHNICITIES), "sensitive_attribute"),
    "GENDER": lambda f: _pv("GENDER", f.rng.choice(_GENDERS), "quasi_identifier"),
    "NATIONALITY": lambda f: _pv("NATIONALITY", f.rng.choice(_NATIONALITIES), "quasi_identifier"),
    # location_temporal
    "LATITUDE_LONGITUDE": lambda f: _pv("LATITUDE_LONGITUDE", f"{f.rng.uniform(-90,90):.4f}, {f.rng.uniform(-180,180):.4f}", "quasi_identifier"),
    "LOCATION_NAME": lambda f: _pv("LOCATION_NAME", f.rng.choice(["Springfield", "Riverside", "Franklin", "Greenville", "Bristol", "Clinton"]), "quasi_identifier"),
    "POSTAL_CODE": lambda f: _pv("POSTAL_CODE", "".join(str(f.rng.randint(0, 9)) for _ in range(5)), "quasi_identifier"),
    # medical_biological
    "DEA_NUMBER": lambda f: _pv("DEA_NUMBER", f"{f.rng.choice(string.ascii_uppercase)}{f.rng.choice(string.ascii_uppercase)}" + "".join(str(f.rng.randint(0, 9)) for _ in range(7)), "direct_identifier"),
    "NPI_NUMBER": lambda f: _pv("NPI_NUMBER", "".join(str(f.rng.randint(0, 9)) for _ in range(10)), "direct_identifier"),
    "PRESCRIPTION_NUMBER": lambda f: _pv("PRESCRIPTION_NUMBER", "RX-" + "".join(str(f.rng.randint(0, 9)) for _ in range(8)), "direct_identifier"),
    # special_category
    "HOUSEHOLD_SIZE": lambda f: _pv("HOUSEHOLD_SIZE", str(f.rng.randint(1, 8)), "sensitive_attribute"),
    "MARITAL_STATUS": lambda f: _pv("MARITAL_STATUS", f.rng.choice(_MARITAL), "sensitive_attribute"),
    "POLITICAL_OPINION": lambda f: _pv("POLITICAL_OPINION", f.rng.choice(_POLITICAL), "sensitive_attribute"),
    "RELIGIOUS_BELIEF": lambda f: _pv("RELIGIOUS_BELIEF", f.rng.choice(_RELIGION), "sensitive_attribute"),
    "VEHICLE_MODEL": lambda f: _pv("VEHICLE_MODEL", f.rng.choice(_VEHICLES), "quasi_identifier"),
}

# entity_type -> PIIFactory method name (the 35 the factory already emits).
_FACTORY_METHOD: dict[str, str] = {
    "PERSON_NAME": "person_name", "EMAIL_ADDRESS": "email", "PHONE_NUMBER": "phone",
    "SOCIAL_SECURITY_NUMBER": "ssn", "STREET_ADDRESS": "address", "DATE_OF_BIRTH": "dob",
    "ORGANIZATION_NAME": "org", "CREDIT_CARD_NUMBER": "credit_card", "IBAN": "iban",
    "IP_ADDRESS": "ip_address", "MAC_ADDRESS": "mac_address", "MEDICAL_RECORD_NUMBER": "mrn",
    "PASSPORT_NUMBER": "passport", "NATIONAL_ID_NUMBER": "national_id",
    "DRIVER_LICENSE_NUMBER": "driver_license", "USERNAME": "username", "API_KEY": "api_key",
    "EMPLOYEE_ID": "employee_id", "JOB_TITLE": "job_title", "SALARY": "salary",
    "LICENSE_PLATE": "license_plate", "HEALTH_CONDITION": "diagnosis",
    "MEDICATION_NAME": "medication", "PROCEDURE_NAME": "procedure",
    "HEALTH_INSURANCE_ID": "insurance_id", "TAX_ID": "tax_id",
    "BANK_ACCOUNT_NUMBER": "bank_account", "BANK_ROUTING_NUMBER": "routing_number",
    "SWIFT_BIC_CODE": "swift_code", "VISA_NUMBER": "visa_number", "TIMESTAMP": "timestamp",
    "PASSWORD": "password", "COURT_CASE_NUMBER": "court_case_number",
    "INVOICE_NUMBER": "invoice_number", "INSURANCE_POLICY_NUMBER": "insurance_policy",
}


def _factory_emitter(method: str) -> Callable[[PIIFactory], PIIValue]:
    return lambda f: getattr(f, method)()


EMITTERS: dict[str, Callable[[PIIFactory], PIIValue]] = {
    **{t: _factory_emitter(m) for t, m in _FACTORY_METHOD.items()},
    **_LOCAL_EMITTERS,
}


def _validate_emitters_complete() -> None:
    missing = taxonomy.CANONICAL_ENTITY_TYPES - set(EMITTERS)
    extra = set(EMITTERS) - taxonomy.CANONICAL_ENTITY_TYPES
    if missing or extra:
        raise RuntimeError(
            f"EMITTERS must cover EXACTLY the 63 canonical types (AX-001 fail-loud). "
            f"missing={sorted(missing)} extra={sorted(extra)}"
        )


_validate_emitters_complete()


def _validate_adversarial_coverage() -> None:
    """Every adversarial type the lattice commits to must have a faithful transform here."""
    from pii_anon_datasets.stats.lattice import DEFAULT_DETECTION_ADVERSARIAL_TYPES
    missing = set(DEFAULT_DETECTION_ADVERSARIAL_TYPES) - set(ADVERSARIAL_TRANSFORMS)
    if missing:
        raise RuntimeError(
            f"committed adversarial types lack a faithful transform (AX-001 fail-loud): {sorted(missing)}"
        )


_validate_adversarial_coverage()


_LABELS = {
    "SOCIAL_SECURITY_NUMBER": "SSN", "DATE_OF_BIRTH": "DOB", "IBAN": "IBAN",
    "IP_ADDRESS": "IP", "MAC_ADDRESS": "MAC", "API_KEY": "API key", "CVV": "CVV",
    "PIN": "PIN", "URL": "URL", "DEA_NUMBER": "DEA", "NPI_NUMBER": "NPI",
}


def _human_label(entity_type: str) -> str:
    return _LABELS.get(entity_type, entity_type.replace("_", " ").title())


def gen_targeted_record(
    factory: PIIFactory,
    *,
    entity_type: str,
    language: str,
    domain: str,
    difficulty: str,
    adversarial_type: str | None,
    rng: random.Random,
    nonce: str | None = None,
) -> dict:
    """Emit ONE v1-shaped record GUARANTEED to contain exactly one positive of ``entity_type``
    in the requested cell. Adversarial cells faithfully obfuscate the target value. ``nonce`` adds a
    non-PII uniqueness marker so records on small value-pools never collide into a content-dedup
    drop (which would also collide content-addressed record_ids). The fill script normalizes the
    result to v2.0.0 via ``migration.migrate_record``."""
    if entity_type not in EMITTERS:
        raise KeyError(f"no synthetic emitter for committed type {entity_type!r} (AX-001 fail-loud)")
    target = EMITTERS[entity_type](factory)

    if adversarial_type is not None:
        transform = ADVERSARIAL_TRANSFORMS.get(adversarial_type)
        if transform is None:
            raise KeyError(
                f"no faithful transform for adversarial type {adversarial_type!r}; "
                f"committed set is {COMMITTED_ADVERSARIAL_TYPES}"
            )
        # Guarantee the attack is genuine: re-draw the value until the transform perturbs it
        # (a random value may have no transform-eligible char, e.g. ocr × an all-letter PASSWORD).
        obf = transform(target.value, rng)
        for _ in range(8):
            if obf != target.value:
                break
            target = EMITTERS[entity_type](factory)
            obf = transform(target.value, rng)
        if obf == target.value:
            raise ValueError(
                f"adversarial transform {adversarial_type!r} could not perturb a {entity_type} value"
            )
        target = PIIValue(target.entity_type, obf, target.category, target.sensitivity_class)

    slots: dict[str, PIIValue] = {"target": target}
    segs: list[str] = []
    if entity_type != "PERSON_NAME":
        slots["name"] = factory.person_name()
        segs.append("Record for {name}")
    segs.append(f"{_human_label(entity_type)}: {{target}}")
    if entity_type != "EMAIL_ADDRESS":
        name_for_email = slots["name"].value if "name" in slots else None
        slots["email"] = factory.email(name_for_email)
        segs.append("contact {email}")
    template = ", ".join(segs) + "."
    if nonce is not None:
        template += f" [#{nonce}]"   # non-PII record marker → guarantees distinct text/record_id

    return build_record(
        template, slots,
        language=language,
        primary_dimension=("edge_cases" if adversarial_type else "diverse_pii_types"),
        domain=domain, difficulty=difficulty,
        adversarial_type=adversarial_type,
        adversarial_difficulty=("clean" if adversarial_type is None else "moderate"),
        adversarial_techniques=([adversarial_type] if adversarial_type else []),
        rng=rng,
    )
