#!/usr/bin/env python3
"""
Generate new PII-Anon v2 records using template expansion + synthetic PII injection.

This script generates records for all content expansion categories:
- Entity tracking (coreference across multi-turn contexts)
- Clinical domain (discharge summaries, progress notes, etc.)
- Financial domain (bank statements, KYC, wire transfers)
- Legal domain (court filings, contracts)
- Code domain (source code with embedded PII)
- Structured documents (forms, invoices, tables)
- Temporal consistency (time-series entity evolution)
- Edge cases / adversarial (obfuscation, misspellings, ambiguity)

Usage:
    python scripts/generate_records.py [--output-dir src/pii_anon_datasets/data]
    python scripts/generate_records.py --category clinical --count 5000
    python scripts/generate_records.py --all
"""

import argparse
import gzip
import json
import random
import string
import uuid
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "src" / "pii_anon_datasets" / "data" / "pii_anon_v2_generated.jsonl"

SEED = 42

# ─── PII Value Factories ────────────────────────────────────────────────────

FIRST_NAMES_EN = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Daniel", "Lisa", "Matthew", "Nancy",
    "Anthony", "Betty", "Mark", "Margaret", "Donald", "Sandra", "Steven", "Ashley",
    "Andrew", "Kimberly", "Paul", "Emily", "Joshua", "Donna", "Kenneth", "Michelle",
    "Kevin", "Carol", "Brian", "Amanda", "George", "Dorothy", "Timothy", "Melissa"]

LAST_NAMES_EN = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"]

FIRST_NAMES_DE = ["Hans", "Klaus", "Heike", "Petra", "Stefan", "Monika", "Andreas", "Sabine",
    "Wolfgang", "Ursula", "Jürgen", "Martina", "Dieter", "Brigitte", "Rainer", "Claudia"]

LAST_NAMES_DE = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner",
    "Becker", "Schulz", "Hoffmann", "Koch", "Richter", "Wolf", "Klein", "Braun"]

FIRST_NAMES_FR = ["Pierre", "Marie", "Jean", "Sophie", "François", "Isabelle", "Michel", "Catherine",
    "Philippe", "Nathalie", "Alain", "Sylvie", "Laurent", "Christine", "Nicolas", "Anne"]

LAST_NAMES_FR = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand",
    "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David"]

FIRST_NAMES_ES = ["Carlos", "María", "Miguel", "Ana", "José", "Carmen", "Antonio", "Laura",
    "Francisco", "Marta", "Pedro", "Cristina", "Luis", "Isabel", "Diego", "Patricia"]

LAST_NAMES_ES = ["García", "Rodríguez", "Martínez", "López", "González", "Hernández", "Pérez",
    "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Cruz", "Morales"]

FIRST_NAMES_JA = ["太郎", "花子", "健一", "美咲", "翔太", "愛子", "大輔", "由美",
    "拓也", "恵子", "直樹", "裕子", "誠", "明美", "隆", "幸子"]

LAST_NAMES_JA = ["田中", "鈴木", "高橋", "渡辺", "伊藤", "山本", "中村", "小林",
    "加藤", "吉田", "山田", "佐々木", "松本", "井上", "木村", "林"]

FIRST_NAMES_ZH = ["伟", "芳", "强", "秀英", "磊", "敏", "军", "丽",
    "勇", "静", "杰", "艳", "涛", "慧", "明", "洁"]

LAST_NAMES_ZH = ["王", "李", "张", "刘", "陈", "杨", "黄", "赵",
    "周", "吴", "徐", "孙", "马", "胡", "朱", "郭"]

FIRST_NAMES_AR = ["محمد", "فاطمة", "أحمد", "عائشة", "علي", "مريم", "خالد", "نور",
    "عمر", "سارة", "يوسف", "هدى", "حسن", "ليلى", "إبراهيم", "زينب"]

LAST_NAMES_AR = ["الأحمد", "المحمد", "العلي", "الحسن", "الخالد", "السعيد",
    "الشريف", "القاسم", "الرشيد", "المنصور", "الفهد", "النجار"]

ORGS = ["Acme Corp", "Globex Industries", "Initech Solutions", "Umbrella Corp",
    "Cyberdyne Systems", "Wayne Enterprises", "Stark Industries", "LexCorp",
    "Soylent Corp", "Weyland-Yutani", "Tyrell Corporation", "Oscorp Industries",
    "Massive Dynamic", "Hooli", "Pied Piper", "Aperture Science",
    "Black Mesa Research", "InGen", "Wonka Industries", "Dunder Mifflin",
    "Sterling Cooper", "Prestige Worldwide", "Vandelay Industries", "Bluth Company",
    "Consolidated Amalgamated", "Pacific Northwest Tech", "Atlantic Data Systems",
    "Nordic Analytics", "Meridian Healthcare", "Pinnacle Financial Group"]

STREETS = ["Main St", "Oak Ave", "Elm Dr", "Maple Ln", "Cedar Blvd", "Pine Rd",
    "Birch Way", "Walnut St", "Cherry Ln", "Spruce Ave", "Willow Dr",
    "Dogwood Ct", "Poplar Ave", "Sycamore Blvd", "Magnolia Way",
    "Hickory Ln", "Chestnut St", "Aspen Dr", "Redwood Ave", "Cypress Blvd"]

CITIES = ["Springfield", "Madison", "Franklin", "Clinton", "Georgetown",
    "Arlington", "Riverside", "Lakewood", "Fairview", "Salem",
    "Burlington", "Greenville", "Bristol", "Chester", "Portland"]

STATES = ["AL", "AK", "AZ", "CA", "CO", "CT", "FL", "GA", "IL", "IN",
    "KS", "KY", "LA", "MA", "MD", "MI", "MN", "MO", "NC", "NJ",
    "NM", "NY", "OH", "OK", "OR", "PA", "SC", "TN", "TX", "VA", "WA", "WI"]

DOMAINS_EMAIL = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com",
    "icloud.com", "mail.com", "fastmail.com", "zoho.com", "aol.com"]

JOB_TITLES = ["Software Engineer", "Data Analyst", "Project Manager", "Marketing Director",
    "Financial Advisor", "HR Specialist", "Operations Manager", "Research Scientist",
    "Product Designer", "Sales Representative", "Compliance Officer", "Risk Analyst",
    "Chief Technology Officer", "VP of Engineering", "Legal Counsel", "Medical Director",
    "Staff Accountant", "Network Administrator", "Security Analyst", "Database Administrator"]

DIAGNOSES = ["Type 2 Diabetes Mellitus", "Essential Hypertension", "Acute Bronchitis",
    "Chronic Obstructive Pulmonary Disease", "Major Depressive Disorder",
    "Generalized Anxiety Disorder", "Osteoarthritis", "Chronic Kidney Disease",
    "Atrial Fibrillation", "Congestive Heart Failure", "Asthma", "Migraine",
    "Hypothyroidism", "Rheumatoid Arthritis", "Gastroesophageal Reflux Disease"]

MEDICATIONS = ["Metformin 500mg", "Lisinopril 10mg", "Atorvastatin 20mg", "Amlodipine 5mg",
    "Omeprazole 20mg", "Sertraline 50mg", "Metoprolol 25mg", "Losartan 50mg",
    "Albuterol Inhaler", "Gabapentin 300mg", "Levothyroxine 75mcg", "Prednisone 10mg"]

PROCEDURES = ["Complete Blood Count", "Comprehensive Metabolic Panel", "Chest X-Ray",
    "Electrocardiogram", "CT Scan Abdomen", "MRI Brain", "Colonoscopy",
    "Echocardiogram", "Pulmonary Function Test", "Bone Density Scan"]

PROG_LANGS = ["python", "javascript", "java", "go", "rust", "typescript", "csharp",
    "ruby", "php", "sql", "bash", "yaml", "json_config"]


@dataclass
class PIIValue:
    """A generated PII value with its entity type and metadata."""
    entity_type: str
    value: str
    category: str
    sensitivity_class: str
    cluster_id: str | None = None
    mention_variant: str | None = None


class PIIFactory:
    """Generates realistic synthetic PII values with seeded randomness."""

    def __init__(self, rng: random.Random, language: str = "en"):
        self.rng = rng
        self.language = language
        self._person_counter = 0

    def _pick(self, lst: list) -> Any:
        return self.rng.choice(lst)

    def person_name(self, cluster_id: str | None = None, variant: str = "full_name") -> PIIValue:
        if self.language == "de":
            first, last = self._pick(FIRST_NAMES_DE), self._pick(LAST_NAMES_DE)
        elif self.language == "fr":
            first, last = self._pick(FIRST_NAMES_FR), self._pick(LAST_NAMES_FR)
        elif self.language == "es":
            first, last = self._pick(FIRST_NAMES_ES), self._pick(LAST_NAMES_ES)
        elif self.language == "ja":
            first, last = self._pick(FIRST_NAMES_JA), self._pick(LAST_NAMES_JA)
        elif self.language == "zh":
            first, last = self._pick(FIRST_NAMES_ZH), self._pick(LAST_NAMES_ZH)
        elif self.language == "ar":
            first, last = self._pick(FIRST_NAMES_AR), self._pick(LAST_NAMES_AR)
        else:
            first, last = self._pick(FIRST_NAMES_EN), self._pick(LAST_NAMES_EN)

        if variant == "first_name":
            name = first
        elif variant == "last_name":
            name = last
        elif variant == "formal":
            prefix = self._pick(["Mr.", "Mrs.", "Ms.", "Dr."])
            name = f"{prefix} {last}"
        elif variant == "first_last_initial":
            name = f"{first} {last[0]}."
        else:
            name = f"{first} {last}"

        return PIIValue("PERSON_NAME", name, "identity_demographics", "direct_identifier",
                        cluster_id=cluster_id, mention_variant=variant)

    def email(self, person_name: str | None = None) -> PIIValue:
        if person_name:
            parts = person_name.lower().split()
            user = f"{parts[0]}.{parts[-1]}{self.rng.randint(1, 99)}" if len(parts) > 1 else parts[0]
        else:
            user = f"user{self.rng.randint(100, 9999)}"
        domain = self._pick(DOMAINS_EMAIL)
        return PIIValue("EMAIL_ADDRESS", f"{user}@{domain}", "contact", "direct_identifier")

    def phone(self) -> PIIValue:
        area = self.rng.randint(200, 999)
        p1 = self.rng.randint(200, 999)
        p2 = self.rng.randint(1000, 9999)
        return PIIValue("PHONE_NUMBER", f"+1 ({area}) {p1}-{p2}", "contact", "direct_identifier")

    def ssn(self) -> PIIValue:
        a = self.rng.randint(100, 999)
        b = self.rng.randint(10, 99)
        c = self.rng.randint(1000, 9999)
        return PIIValue("SOCIAL_SECURITY_NUMBER", f"{a}-{b}-{c}", "government_legal", "direct_identifier")

    def address(self) -> PIIValue:
        num = self.rng.randint(100, 9999)
        street = self._pick(STREETS)
        city = self._pick(CITIES)
        state = self._pick(STATES)
        zipcode = self.rng.randint(10000, 99999)
        return PIIValue("STREET_ADDRESS", f"{num} {street}, {city}, {state} {zipcode}",
                        "location_temporal", "quasi_identifier")

    def dob(self) -> PIIValue:
        year = self.rng.randint(1940, 2005)
        month = self.rng.randint(1, 12)
        day = self.rng.randint(1, 28)
        return PIIValue("DATE_OF_BIRTH", f"{year}-{month:02d}-{day:02d}",
                        "location_temporal", "quasi_identifier")

    def org(self) -> PIIValue:
        return PIIValue("ORGANIZATION_NAME", self._pick(ORGS),
                        "identity_demographics", "quasi_identifier")

    def credit_card(self) -> PIIValue:
        prefix = self._pick(["4", "5", "37", "6011"])
        remaining = 16 - len(prefix)
        digits = prefix + "".join(str(self.rng.randint(0, 9)) for _ in range(remaining))
        formatted = " ".join(digits[i:i+4] for i in range(0, len(digits), 4))
        return PIIValue("CREDIT_CARD_NUMBER", formatted, "financial", "direct_identifier")

    def iban(self) -> PIIValue:
        country = self._pick(["DE", "FR", "GB", "NL", "ES", "IT"])
        check = self.rng.randint(10, 99)
        rest = "".join(str(self.rng.randint(0, 9)) for _ in range(18))
        return PIIValue("IBAN", f"{country}{check}{rest}", "financial", "direct_identifier")

    def ip_address(self) -> PIIValue:
        octets = [self.rng.randint(1, 254) for _ in range(4)]
        return PIIValue("IP_ADDRESS", ".".join(str(o) for o in octets),
                        "digital_online", "direct_identifier")

    def mac_address(self) -> PIIValue:
        octets = [f"{self.rng.randint(0, 255):02x}" for _ in range(6)]
        return PIIValue("MAC_ADDRESS", ":".join(octets), "digital_online", "direct_identifier")

    def mrn(self) -> PIIValue:
        return PIIValue("MEDICAL_RECORD_NUMBER", f"MRN-{self.rng.randint(1000000, 9999999)}",
                        "medical_biological", "direct_identifier")

    def passport(self) -> PIIValue:
        letter = self._pick(string.ascii_uppercase)
        num = self.rng.randint(10000000, 99999999)
        return PIIValue("PASSPORT_NUMBER", f"{letter}{num}", "government_legal", "direct_identifier")

    def national_id(self) -> PIIValue:
        return PIIValue("NATIONAL_ID_NUMBER", f"NID-{self.rng.randint(100000000, 999999999)}",
                        "government_legal", "direct_identifier")

    def driver_license(self) -> PIIValue:
        letters = "".join(self._pick(string.ascii_uppercase) for _ in range(2))
        num = self.rng.randint(100000, 999999)
        return PIIValue("DRIVER_LICENSE_NUMBER", f"{letters}-{num}",
                        "government_legal", "direct_identifier")

    def username(self) -> PIIValue:
        word = self._pick(["user", "admin", "dev", "test", "mgr", "ops", "sys"])
        num = self.rng.randint(100, 9999)
        return PIIValue("USERNAME", f"{word}_{num}", "digital_online", "direct_identifier")

    def api_key(self) -> PIIValue:
        key = "".join(self.rng.choices(string.ascii_letters + string.digits, k=32))
        return PIIValue("API_KEY", f"sk-{key}", "digital_online", "direct_identifier")

    def employee_id(self) -> PIIValue:
        return PIIValue("EMPLOYEE_ID", f"EMP-{self.rng.randint(10000, 99999)}",
                        "employment", "direct_identifier")

    def job_title(self) -> PIIValue:
        return PIIValue("JOB_TITLE", self._pick(JOB_TITLES), "employment", "quasi_identifier")

    def salary(self) -> PIIValue:
        amount = self.rng.randint(35, 250) * 1000
        return PIIValue("SALARY", f"${amount:,}", "employment", "quasi_identifier")

    def license_plate(self) -> PIIValue:
        letters = "".join(self._pick(string.ascii_uppercase) for _ in range(3))
        nums = self.rng.randint(1000, 9999)
        return PIIValue("LICENSE_PLATE", f"{letters}-{nums}", "government_legal", "direct_identifier")

    def diagnosis(self) -> PIIValue:
        return PIIValue("HEALTH_CONDITION", self._pick(DIAGNOSES),
                        "medical_biological", "sensitive_attribute")

    def medication(self) -> PIIValue:
        return PIIValue("MEDICATION_NAME", self._pick(MEDICATIONS),
                        "medical_biological", "sensitive_attribute")

    def procedure(self) -> PIIValue:
        return PIIValue("PROCEDURE_NAME", self._pick(PROCEDURES),
                        "medical_biological", "sensitive_attribute")

    def insurance_id(self) -> PIIValue:
        return PIIValue("HEALTH_INSURANCE_ID", f"INS-{self.rng.randint(100000000, 999999999)}",
                        "medical_biological", "direct_identifier")

    def tax_id(self) -> PIIValue:
        a = self.rng.randint(10, 99)
        b = self.rng.randint(1000000, 9999999)
        return PIIValue("TAX_ID", f"{a}-{b}", "financial", "direct_identifier")

    def bank_account(self) -> PIIValue:
        num = "".join(str(self.rng.randint(0, 9)) for _ in range(10))
        return PIIValue("BANK_ACCOUNT_NUMBER", num, "financial", "direct_identifier")

    def routing_number(self) -> PIIValue:
        num = "".join(str(self.rng.randint(0, 9)) for _ in range(9))
        return PIIValue("BANK_ROUTING_NUMBER", num, "financial", "quasi_identifier")

    def swift_code(self) -> PIIValue:
        bank = "".join(self._pick(string.ascii_uppercase) for _ in range(4))
        country = self._pick(["US", "DE", "GB", "FR", "JP", "CH"])
        loc = "".join(self._pick(string.ascii_uppercase + string.digits) for _ in range(2))
        return PIIValue("SWIFT_BIC_CODE", f"{bank}{country}{loc}", "financial", "quasi_identifier")

    def visa_number(self) -> PIIValue:
        return PIIValue("VISA_NUMBER", f"V{self.rng.randint(10000000, 99999999)}",
                        "government_legal", "direct_identifier")

    def timestamp(self) -> PIIValue:
        y = self.rng.randint(2020, 2026)
        m = self.rng.randint(1, 12)
        d = self.rng.randint(1, 28)
        h = self.rng.randint(0, 23)
        mi = self.rng.randint(0, 59)
        return PIIValue("TIMESTAMP", f"{y}-{m:02d}-{d:02d}T{h:02d}:{mi:02d}:00Z",
                        "location_temporal", "quasi_identifier")

    def password(self) -> PIIValue:
        chars = string.ascii_letters + string.digits + "!@#$%"
        pwd = "".join(self.rng.choices(chars, k=self.rng.randint(8, 16)))
        return PIIValue("PASSWORD", pwd, "digital_online", "direct_identifier")

    def court_case_number(self) -> PIIValue:
        year = self.rng.randint(2020, 2026)
        num = self.rng.randint(1000, 9999)
        court = self._pick(["CV", "CR", "CIV", "CRIM", "FAM"])
        return PIIValue("COURT_CASE_NUMBER", f"{year}-{court}-{num}",
                        "government_legal", "direct_identifier")

    def invoice_number(self) -> PIIValue:
        return PIIValue("INVOICE_NUMBER", f"INV-{self.rng.randint(100000, 999999)}",
                        "financial", "direct_identifier")

    def vehicle_reg(self) -> PIIValue:
        letters = "".join(self._pick(string.ascii_uppercase) for _ in range(3))
        nums = self.rng.randint(100, 999)
        return PIIValue("VEHICLE_REGISTRATION", f"{letters} {nums}",
                        "government_legal", "direct_identifier")

    def insurance_policy(self) -> PIIValue:
        return PIIValue("INSURANCE_POLICY_NUMBER", f"POL-{self.rng.randint(1000000, 9999999)}",
                        "financial", "direct_identifier")

    def session_id(self) -> PIIValue:
        sid = "".join(self.rng.choices(string.hexdigits.lower(), k=32))
        return PIIValue("SESSION_ID", sid, "digital_online", "direct_identifier")


# ─── Record Builder ──────────────────────────────────────────────────────────

@dataclass
class AnnotationSlot:
    """A placeholder in a template to be filled with a PII value."""
    placeholder: str
    pii_value: PIIValue | None = None


def build_record(
    text_template: str,
    slots: dict[str, PIIValue],
    *,
    language: str = "en",
    primary_dimension: str = "diverse_pii_types",
    data_type: str = "unstructured_text",
    domain: str = "general",
    difficulty: str = "moderate",
    document_type: str | None = None,
    rng: random.Random | None = None,
    extra_dimensions: list[str] | None = None,
    regulatory_domains: list[str] | None = None,
    adversarial_type: str | None = None,
    adversarial_difficulty: str = "clean",
    adversarial_techniques: list[str] | None = None,
) -> dict[str, Any]:
    """Build a v2 record from a template string and PII value slots.

    The template uses {slot_name} placeholders. Each slot maps to a PIIValue.
    Offsets are computed after all replacements.
    """
    if rng is None:
        rng = random.Random(SEED)

    # Step 1: Find ALL placeholder positions for ALL slots
    slot_positions = []
    for name, pii in slots.items():
        placeholder = "{" + name + "}"
        start = 0
        while True:
            idx = text_template.find(placeholder, start)
            if idx == -1:
                break
            slot_positions.append((idx, placeholder, pii))
            start = idx + len(placeholder)

    # Step 2: Replace from end to preserve earlier positions, tracking annotations
    slot_positions.sort(key=lambda x: x[0], reverse=True)
    # Store (template_offset, pii) pairs for annotation building
    annotation_specs = []
    result_text = text_template
    for idx, placeholder, pii in slot_positions:
        result_text = result_text[:idx] + pii.value + result_text[idx + len(placeholder):]
        annotation_specs.append((idx, pii))

    # Step 3: Recalculate offsets in the final text
    # Since we replaced from end to start, earlier positions are still valid
    # but we need to account for length changes from earlier replacements
    # Easier: just re-scan from scratch using the sorted replacement order
    annotations = []
    # Re-sort by position (ascending) and compute final offsets
    # Actually, since replacements were done right-to-left, the positions
    # for earlier slots are correct in the final text. Let's just find each
    # PII value at its expected position.

    # Rebuild: track all replacements in order (left to right)
    slot_positions_asc = sorted(slot_positions, key=lambda x: x[0])
    offset_shift = 0
    for orig_idx, placeholder, pii in slot_positions_asc:
        final_idx = orig_idx + offset_shift
        annotations.append({
            "entity_type": pii.entity_type,
            "start": final_idx,
            "end": final_idx + len(pii.value),
            "text": pii.value,
            "category": pii.category,
            "sensitivity_class": pii.sensitivity_class,
            "cluster_id": pii.cluster_id,
            "mention_variant": pii.mention_variant,
        })
        offset_shift += len(pii.value) - len(placeholder)

    # Step 4: Remove overlapping annotations (keep the longer span)
    annotations.sort(key=lambda a: (a["start"], -a["end"]))
    filtered = []
    for ann in annotations:
        if filtered and ann["start"] < filtered[-1]["end"]:
            # Overlap — keep the one already in filtered (it's longer due to sort)
            continue
        filtered.append(ann)
    annotations = filtered

    # Assign entity_ids and verify offsets
    for i, ann in enumerate(annotations):
        ann["entity_id"] = f"e{i}"
        actual = result_text[ann["start"]:ann["end"]]
        if actual != ann["text"]:
            raise ValueError(f"Offset mismatch: expected {ann['text']!r} at [{ann['start']}:{ann['end']}], got {actual!r}")

    from scripts.migrate_v1_to_v2 import (
        LANGUAGE_FAMILY_MAP, SCRIPT_MAP, RESOURCE_LEVEL_MAP,
    )

    dimensions = [primary_dimension]
    if extra_dimensions:
        dimensions.extend(extra_dimensions)
    if language != "en" and "multilingual" not in dimensions:
        dimensions.append("multilingual")
    dimensions = sorted(set(dimensions))

    token_count = max(1, len(result_text.split()))

    if regulatory_domains is None:
        regulatory_domains = ["gdpr"]
        entity_types = {a["entity_type"] for a in annotations}
        if entity_types & {"MEDICAL_RECORD_NUMBER", "HEALTH_CONDITION", "MEDICATION_NAME",
                           "PROCEDURE_NAME", "HEALTH_INSURANCE_ID", "PRESCRIPTION_NUMBER"}:
            regulatory_domains.append("hipaa")
        if entity_types & {"SOCIAL_SECURITY_NUMBER", "DRIVER_LICENSE_NUMBER"}:
            regulatory_domains.append("ccpa")

    quasi_ids = sorted({a["entity_type"] for a in annotations if a["sensitivity_class"] == "quasi_identifier"})
    reident_risk = "low"
    if len(quasi_ids) >= 3:
        reident_risk = "high"
    elif len(quasi_ids) >= 2:
        reident_risk = "moderate"

    record_id = str(uuid.uuid4())

    return {
        "record_id": record_id,
        "text": result_text,
        "version": "2.0.0",
        "annotations": annotations,
        "language": language,
        "script": SCRIPT_MAP.get(language, "Latn"),
        "language_family": LANGUAGE_FAMILY_MAP.get(language, "unknown"),
        "resource_level": RESOURCE_LEVEL_MAP.get(language, "low"),
        "primary_dimension": primary_dimension,
        "dimensions": dimensions,
        "data_type": data_type,
        "document_type": document_type,
        "domain": domain,
        "difficulty_level": difficulty,
        "context_length_tier": "short" if token_count <= 50 else "medium" if token_count <= 200 else "long" if token_count <= 500 else "very_long",
        "token_count": token_count,
        "entity_tracking": {
            "num_repeated_entities": 0,
            "coreference_chains": [],
            "tracking_difficulty": "none",
            "num_distinct_persons": sum(1 for a in annotations if a["entity_type"] == "PERSON_NAME"),
        },
        "adversarial": {
            "type": adversarial_type,
            "difficulty": adversarial_difficulty,
            "techniques": adversarial_techniques or [],
        },
        "privacy_risk": {
            "quasi_identifiers": quasi_ids,
            "reidentification_risk": reident_risk,
            "k_anonymity_estimate": None,
        },
        "regulatory_domains": regulatory_domains,
        "query_context": None,
        "provenance": {
            "source_type": "synthetic",
            "license": "CC0-1.0",
            "generation_seed": SEED,
            "v1_record_id": None,
        },
    }


# ─── Category Generators ────────────────────────────────────────────────────

def generate_entity_tracking(rng: random.Random, count: int) -> list[dict]:
    """Generate entity tracking records with coreference chains."""
    records = []
    templates = [
        "Employee {name1} (ID: {emp_id}) works at {org}. Contact {name1} at {email} or {phone}. {name1_formal}'s manager approved the request. SSN on file: {ssn}. Address: {address}.",
        "{name1} submitted report #TR-{report}. In the meeting, {name1_first} presented findings to the board. {name1_formal} concluded that action was needed. Email {name1} at {email}. Phone: {phone}.",
        "Patient {name1} (MRN: {mrn}) was admitted on {dob}. Dr. {name2} examined {name1_last} and prescribed {med}. {name1_formal} was discharged with instructions to follow up. Contact: {phone}.",
        "Applicant {name1} applied for position at {org}. {name1_first} has {job_title} experience. Resume for {name1_formal} includes email {email} and address {address}. SSN: {ssn}.",
        "Customer {name1} (Account: {acct}) reported an issue. Our agent spoke with {name1_formal} and resolved the complaint. {name1_first} can be reached at {phone} or {email}. Address on file: {address}.",
    ]

    languages = ["en"] * 5 + ["de", "fr", "es"]

    for i in range(count):
        lang = rng.choice(languages)
        factory = PIIFactory(rng, lang)
        template = rng.choice(templates)

        cluster1 = f"person_{i}_1"
        name1_full = factory.person_name(cluster_id=cluster1, variant="full_name")
        first = name1_full.value.split()[0] if " " in name1_full.value else name1_full.value
        last = name1_full.value.split()[-1] if " " in name1_full.value else name1_full.value
        formal_prefix = rng.choice(["Mr.", "Ms.", "Dr."])

        slots = {"name1": name1_full}

        # Create coreference variants — use unique placeholder names
        if "{name1_first}" in template:
            slots["name1_first"] = PIIValue("PERSON_NAME", first, "identity_demographics",
                                            "direct_identifier", cluster_id=cluster1, mention_variant="first_name")
        if "{name1_formal}" in template:
            slots["name1_formal"] = PIIValue("PERSON_NAME", f"{formal_prefix} {last}", "identity_demographics",
                                             "direct_identifier", cluster_id=cluster1, mention_variant="formal")
        if "{name1_last}" in template:
            slots["name1_last"] = PIIValue("PERSON_NAME", last, "identity_demographics",
                                           "direct_identifier", cluster_id=cluster1, mention_variant="last_name")
        if "{name2}" in template:
            slots["name2"] = factory.person_name(cluster_id=f"person_{i}_2")
        if "{email}" in template:
            slots["email"] = factory.email(name1_full.value)
        if "{phone}" in template:
            slots["phone"] = factory.phone()
        if "{ssn}" in template:
            slots["ssn"] = factory.ssn()
        if "{address}" in template:
            slots["address"] = factory.address()
        if "{org}" in template:
            slots["org"] = factory.org()
        if "{emp_id}" in template:
            slots["emp_id"] = factory.employee_id()
        if "{mrn}" in template:
            slots["mrn"] = factory.mrn()
        if "{dob}" in template:
            slots["dob"] = factory.dob()
        if "{med}" in template:
            slots["med"] = factory.medication()
        if "{job_title}" in template:
            slots["job_title"] = factory.job_title()
        if "{acct}" in template:
            slots["acct"] = factory.bank_account()
        if "{report}" in template:
            slots["report"] = PIIValue("EMPLOYEE_ID", str(rng.randint(1000, 9999)),
                                       "employment", "direct_identifier")

        rec = build_record(template, slots, language=lang,
                           primary_dimension="entity_tracking", domain="general",
                           difficulty=rng.choice(["moderate", "hard", "challenging"]))

        # Fix entity tracking metadata
        chains = {}
        for a in rec["annotations"]:
            cid = a.get("cluster_id")
            if cid:
                chains.setdefault(cid, []).append(a["entity_id"])
        coref_chains = [ids for ids in chains.values() if len(ids) > 1]
        rec["entity_tracking"] = {
            "num_repeated_entities": sum(1 for c in coref_chains),
            "coreference_chains": coref_chains,
            "tracking_difficulty": "complex" if len(coref_chains) > 1 else "moderate" if coref_chains else "simple",
            "num_distinct_persons": len(chains),
        }
        records.append(rec)

    return records


def generate_clinical(rng: random.Random, count: int) -> list[dict]:
    """Generate clinical/healthcare domain records."""
    records = []
    templates = [
        "Discharge Summary\nPatient: {name}, MRN: {mrn}\nDOB: {dob}\nDiagnosis: {diagnosis}\nMedication: {med}\nProvider: {org}\nContact: {phone}\nInsurance: {ins_id}",
        "Progress Note - {name} ({mrn})\nDate: {timestamp}\nCC: {diagnosis}\nAssessment: Patient reports improvement with {med}.\nPlan: Follow-up in 2 weeks. Procedure: {procedure}\nContact: {email}",
        "Lab Results for {name} (MRN: {mrn})\nOrdered by: Dr. {name2} at {org}\nTest: {procedure}\nDiagnosis: {diagnosis}\nInsurance ID: {ins_id}\nPhone: {phone}",
        "Referral Letter\nFrom: Dr. {name2}, {org}\nTo: Specialist\nRe: {name} (DOB: {dob}, MRN: {mrn})\nDiagnosis: {diagnosis}\nCurrent Medications: {med}\nContact: {phone}, {email}",
    ]

    for i in range(count):
        lang = rng.choice(["en"] * 6 + ["de", "fr", "es", "ja", "zh"])
        factory = PIIFactory(rng, lang)
        template = rng.choice(templates)

        slots = {
            "name": factory.person_name(),
            "mrn": factory.mrn(),
            "diagnosis": factory.diagnosis(),
            "med": factory.medication(),
            "org": factory.org(),
            "phone": factory.phone(),
        }
        if "{dob}" in template:
            slots["dob"] = factory.dob()
        if "{ins_id}" in template:
            slots["ins_id"] = factory.insurance_id()
        if "{timestamp}" in template:
            slots["timestamp"] = factory.timestamp()
        if "{procedure}" in template:
            slots["procedure"] = factory.procedure()
        if "{email}" in template:
            slots["email"] = factory.email(slots["name"].value)
        if "{name2}" in template:
            slots["name2"] = factory.person_name()

        rec = build_record(template, slots, language=lang,
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="clinical", document_type="discharge_summary",
                           difficulty=rng.choice(["moderate", "hard"]),
                           regulatory_domains=["gdpr", "hipaa"])
        records.append(rec)
    return records


def generate_financial(rng: random.Random, count: int) -> list[dict]:
    """Generate financial domain records."""
    records = []
    templates = [
        "Wire Transfer Confirmation\nFrom: {name} (Acct: {acct}, Routing: {routing})\nTo: {org}\nIBAN: {iban}\nSWIFT: {swift}\nAmount: {salary}\nRef: {invoice}\nDate: {timestamp}",
        "KYC Verification\nCustomer: {name}\nDOB: {dob}\nSSN: {ssn}\nAddress: {address}\nEmployer: {org}\nTitle: {job_title}\nIncome: {salary}\nID: {passport}",
        "Credit Application\nApplicant: {name}\nEmail: {email}\nPhone: {phone}\nCredit Card: {cc}\nBank Account: {acct}\nTax ID: {tax_id}\nEmployer: {org}\nAddress: {address}",
        "Account Statement - {name}\nAccount: {acct}\nRouting: {routing}\nBalance: {salary}\nRecent: Wire to {org} ({iban}), SWIFT: {swift}\nInvoice: {invoice}\nContact: {phone}",
    ]

    for i in range(count):
        lang = rng.choice(["en"] * 5 + ["de", "fr", "ja", "zh", "ar"])
        factory = PIIFactory(rng, lang)
        template = rng.choice(templates)

        slots = {"name": factory.person_name(), "org": factory.org()}
        if "{acct}" in template: slots["acct"] = factory.bank_account()
        if "{routing}" in template: slots["routing"] = factory.routing_number()
        if "{iban}" in template: slots["iban"] = factory.iban()
        if "{swift}" in template: slots["swift"] = factory.swift_code()
        if "{salary}" in template: slots["salary"] = factory.salary()
        if "{invoice}" in template: slots["invoice"] = factory.invoice_number()
        if "{timestamp}" in template: slots["timestamp"] = factory.timestamp()
        if "{dob}" in template: slots["dob"] = factory.dob()
        if "{ssn}" in template: slots["ssn"] = factory.ssn()
        if "{address}" in template: slots["address"] = factory.address()
        if "{job_title}" in template: slots["job_title"] = factory.job_title()
        if "{passport}" in template: slots["passport"] = factory.passport()
        if "{email}" in template: slots["email"] = factory.email(slots["name"].value)
        if "{phone}" in template: slots["phone"] = factory.phone()
        if "{cc}" in template: slots["cc"] = factory.credit_card()
        if "{tax_id}" in template: slots["tax_id"] = factory.tax_id()

        rec = build_record(template, slots, language=lang,
                           primary_dimension="diverse_pii_types", domain="financial",
                           document_type="wire_transfer",
                           difficulty=rng.choice(["moderate", "hard"]),
                           regulatory_domains=["gdpr", "ccpa", "pci_dss"])
        records.append(rec)
    return records


def generate_legal(rng: random.Random, count: int) -> list[dict]:
    """Generate legal domain records."""
    records = []
    templates = [
        "Case {case_no}\nPlaintiff: {name1}\nDefendant: {name2}\nCourt: {org}\nFiled: {timestamp}\nPlaintiff Address: {address}\nPlaintiff SSN: {ssn}\nDefendant contact: {phone}",
        "Contract between {name1} (SSN: {ssn}) and {org}.\nEffective: {timestamp}\nAddress: {address}\nContact: {email}, {phone}\nWitness: {name2}\nNotary License: {license}",
        "Compliance Report - {org}\nPrepared by: {name1} ({job_title})\nDate: {timestamp}\nSubject: {name2}\nNational ID: {nat_id}\nPassport: {passport}\nAddress: {address}",
    ]

    for i in range(count):
        lang = rng.choice(["en"] * 5 + ["de", "fr", "es"])
        factory = PIIFactory(rng, lang)
        template = rng.choice(templates)

        slots = {"name1": factory.person_name(), "org": factory.org()}
        if "{name2}" in template: slots["name2"] = factory.person_name()
        if "{case_no}" in template: slots["case_no"] = factory.court_case_number()
        if "{timestamp}" in template: slots["timestamp"] = factory.timestamp()
        if "{address}" in template: slots["address"] = factory.address()
        if "{ssn}" in template: slots["ssn"] = factory.ssn()
        if "{phone}" in template: slots["phone"] = factory.phone()
        if "{email}" in template: slots["email"] = factory.email(slots["name1"].value)
        if "{license}" in template: slots["license"] = factory.driver_license()
        if "{job_title}" in template: slots["job_title"] = factory.job_title()
        if "{nat_id}" in template: slots["nat_id"] = factory.national_id()
        if "{passport}" in template: slots["passport"] = factory.passport()

        rec = build_record(template, slots, language=lang,
                           primary_dimension="diverse_pii_types", domain="legal",
                           document_type="court_filing",
                           difficulty=rng.choice(["hard", "challenging"]))
        records.append(rec)
    return records


def generate_code(rng: random.Random, count: int) -> list[dict]:
    """Generate code-embedded PII records."""
    records = []
    templates = [
        '# Config for {name}\nDB_HOST = "{ip}"\nDB_USER = "{username}"\nDB_PASS = "{password}"\nAPI_KEY = "{api_key}"\nADMIN_EMAIL = "{email}"',
        'const config = {{\n  apiKey: "{api_key}",\n  adminEmail: "{email}",\n  serverIp: "{ip}",\n  dbUser: "{username}",\n  dbPass: "{password}",\n  macAddress: "{mac}"\n}};',
        '// Author: {name} <{email}>\n// Server: {ip}\nfunc connect() {{\n  token := "{api_key}"\n  user := "{username}"\n  pass := "{password}"\n}}',
        'apiVersion: v1\nkind: Secret\nmetadata:\n  name: app-secrets\n  # Maintainer: {name} ({email})\ndata:\n  api-key: "{api_key}"\n  db-password: "{password}"\n  server-ip: "{ip}"',
        "-- Database setup by {name}\n-- Contact: {email}\nCREATE USER '{username}'@'{ip}' IDENTIFIED BY '{password}';\nGRANT ALL ON *.* TO '{username}'@'{ip}';",
    ]

    for i in range(count):
        factory = PIIFactory(rng, "en")
        template = rng.choice(templates)

        name_val = factory.person_name()
        slots = {"name": name_val}
        if "{email}" in template: slots["email"] = factory.email(name_val.value)
        if "{ip}" in template: slots["ip"] = factory.ip_address()
        if "{username}" in template: slots["username"] = factory.username()
        if "{password}" in template: slots["password"] = factory.password()
        if "{api_key}" in template: slots["api_key"] = factory.api_key()
        if "{mac}" in template: slots["mac"] = factory.mac_address()

        rec = build_record(template, slots, language="en",
                           primary_dimension="edge_cases", data_type="code",
                           domain="technology", difficulty="hard")
        records.append(rec)
    return records


def generate_structured_docs(rng: random.Random, count: int) -> list[dict]:
    """Generate structured documents (forms, invoices, tables)."""
    records = []

    form_templates = [
        "FORM W-2 WAGE AND TAX STATEMENT\nEmployee: {name}\nSSN: {ssn}\nEmployer: {org}\nEIN: {tax_id}\nWages: {salary}\nAddress: {address}\nState: Filed",
        "INSURANCE CLAIM FORM\nClaimant: {name}\nPolicy: {ins_pol}\nDOB: {dob}\nDiagnosis: {diagnosis}\nProvider: {org}\nAmount: {salary}\nPhone: {phone}",
    ]

    invoice_templates = [
        "INVOICE {invoice}\nDate: {timestamp}\nFrom: {org}\nTo: {name}\nAddress: {address}\nBank: IBAN {iban}\nSWIFT: {swift}\nTotal: {salary}",
    ]

    table_templates = [
        "emp_id,name,email,phone,ssn,department\n{emp_id},{name},{email},{phone},{ssn},Engineering\n{emp_id2},{name2},{email2},{phone2},{ssn2},Marketing",
    ]

    for i in range(count):
        lang = rng.choice(["en"] * 6 + ["de", "fr", "es", "ja"])
        factory = PIIFactory(rng, lang)

        roll = rng.random()
        if roll < 0.5:
            template = rng.choice(form_templates)
            doc_type, data_type_val = "form", "form"
        elif roll < 0.8:
            template = rng.choice(invoice_templates)
            doc_type, data_type_val = "invoice", "structured"
        else:
            template = rng.choice(table_templates)
            doc_type, data_type_val = "employee_roster", "table"

        name_val = factory.person_name()
        slots = {"name": name_val, "org": factory.org()}
        if "{ssn}" in template: slots["ssn"] = factory.ssn()
        if "{tax_id}" in template: slots["tax_id"] = factory.tax_id()
        if "{salary}" in template: slots["salary"] = factory.salary()
        if "{address}" in template: slots["address"] = factory.address()
        if "{dob}" in template: slots["dob"] = factory.dob()
        if "{diagnosis}" in template: slots["diagnosis"] = factory.diagnosis()
        if "{phone}" in template: slots["phone"] = factory.phone()
        if "{ins_pol}" in template: slots["ins_pol"] = factory.insurance_policy()
        if "{invoice}" in template: slots["invoice"] = factory.invoice_number()
        if "{timestamp}" in template: slots["timestamp"] = factory.timestamp()
        if "{iban}" in template: slots["iban"] = factory.iban()
        if "{swift}" in template: slots["swift"] = factory.swift_code()
        if "{email}" in template: slots["email"] = factory.email(name_val.value)
        if "{emp_id}" in template: slots["emp_id"] = factory.employee_id()
        # Second person for table templates
        if "{name2}" in template:
            name2 = factory.person_name()
            slots["name2"] = name2
            slots["email2"] = factory.email(name2.value)
            slots["phone2"] = factory.phone()
            slots["ssn2"] = factory.ssn()
            slots["emp_id2"] = factory.employee_id()

        rec = build_record(template, slots, language=lang,
                           primary_dimension="format_variations", data_type=data_type_val,
                           domain="financial" if "INVOICE" in template else "general",
                           document_type=doc_type,
                           difficulty=rng.choice(["moderate", "hard"]))
        records.append(rec)
    return records


def generate_temporal(rng: random.Random, count: int) -> list[dict]:
    """Generate temporal consistency records (time-series entity evolution)."""
    records = []

    for i in range(count):
        lang = rng.choice(["en"] * 6 + ["de", "fr", "es"])
        factory = PIIFactory(rng, lang)
        name = factory.person_name()
        email1 = factory.email(name.value)

        entries = []
        for step in range(rng.randint(3, 5)):
            ts = factory.timestamp()
            event = rng.choice([
                f"[{ts.value}] {name.value} logged in from {factory.ip_address().value}. Session: {factory.session_id().value}",
                f"[{ts.value}] {name.value} updated profile. Email: {email1.value}. Phone: {factory.phone().value}",
                f"[{ts.value}] Alert for {name.value}: access from {factory.ip_address().value} (MAC: {factory.mac_address().value})",
            ])
            entries.append(event)

        full_text = "\n".join(entries)

        # Build annotations by scanning for PII in the final text
        all_pii_patterns = [
            (name.value, "PERSON_NAME", "identity_demographics", "direct_identifier"),
            (email1.value, "EMAIL_ADDRESS", "contact", "direct_identifier"),
        ]

        annotations = []
        for value, etype, cat, sens in all_pii_patterns:
            start = 0
            while True:
                idx = full_text.find(value, start)
                if idx == -1:
                    break
                annotations.append({
                    "entity_id": f"e{len(annotations)}",
                    "entity_type": etype,
                    "start": idx,
                    "end": idx + len(value),
                    "text": value,
                    "category": cat,
                    "sensitivity_class": sens,
                    "cluster_id": f"person_{i}",
                    "mention_variant": None,
                })
                start = idx + len(value)

        # Also find timestamps, IPs, etc. via regex-like scanning
        import re
        for match in re.finditer(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', full_text):
            annotations.append({
                "entity_id": f"e{len(annotations)}",
                "entity_type": "TIMESTAMP",
                "start": match.start(),
                "end": match.end(),
                "text": match.group(),
                "category": "location_temporal",
                "sensitivity_class": "quasi_identifier",
                "cluster_id": None,
                "mention_variant": None,
            })

        for match in re.finditer(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', full_text):
            annotations.append({
                "entity_id": f"e{len(annotations)}",
                "entity_type": "IP_ADDRESS",
                "start": match.start(),
                "end": match.end(),
                "text": match.group(),
                "category": "digital_online",
                "sensitivity_class": "direct_identifier",
                "cluster_id": None,
                "mention_variant": None,
            })

        # Sort and re-ID
        annotations.sort(key=lambda a: (a["start"], a["end"]))
        for j, a in enumerate(annotations):
            a["entity_id"] = f"e{j}"

        from scripts.migrate_v1_to_v2 import SCRIPT_MAP, LANGUAGE_FAMILY_MAP, RESOURCE_LEVEL_MAP

        token_count = max(1, len(full_text.split()))
        quasi_ids = sorted({a["entity_type"] for a in annotations if a["sensitivity_class"] == "quasi_identifier"})

        rec = {
            "record_id": str(uuid.uuid4()),
            "text": full_text,
            "version": "2.0.0",
            "annotations": annotations,
            "language": lang,
            "script": SCRIPT_MAP.get(lang, "Latn"),
            "language_family": LANGUAGE_FAMILY_MAP.get(lang, "unknown"),
            "resource_level": RESOURCE_LEVEL_MAP.get(lang, "low"),
            "primary_dimension": "temporal_consistency",
            "dimensions": sorted({"temporal_consistency"} | ({"multilingual"} if lang != "en" else set())),
            "data_type": "logs",
            "document_type": "audit_log",
            "domain": "technology",
            "difficulty_level": rng.choice(["hard", "challenging"]),
            "context_length_tier": "short" if token_count <= 50 else "medium" if token_count <= 200 else "long",
            "token_count": token_count,
            "entity_tracking": {
                "num_repeated_entities": sum(1 for _ in set()),
                "coreference_chains": [],
                "tracking_difficulty": "moderate",
                "num_distinct_persons": 1,
            },
            "adversarial": {"type": None, "difficulty": "clean", "techniques": []},
            "privacy_risk": {
                "quasi_identifiers": quasi_ids,
                "reidentification_risk": "moderate",
                "k_anonymity_estimate": None,
            },
            "regulatory_domains": ["gdpr"],
            "query_context": None,
            "provenance": {"source_type": "synthetic", "license": "CC0-1.0", "generation_seed": SEED, "v1_record_id": None},
        }
        records.append(rec)
    return records


def generate_edge_cases(rng: random.Random, count: int) -> list[dict]:
    """Generate adversarial/edge case records."""
    records = []

    for i in range(count):
        factory = PIIFactory(rng, "en")
        case_type = rng.choice(["leetspeak", "partial_redaction", "mixed_case",
                                "abbreviated", "unicode_variant", "dense_pii",
                                "ambiguous", "format_noise"])

        name = factory.person_name()
        email = factory.email(name.value)
        phone = factory.phone()
        ssn = factory.ssn()
        extra_slots: dict[str, PIIValue] = {}

        if case_type == "leetspeak":
            template = "Usr {name} - em4il: {email} - ph0ne: {phone} - s0cial: {ssn}"
            adv_type, adv_diff, techniques = "leetspeak", "moderate", ["character_substitution"]
        elif case_type == "partial_redaction":
            template = "Record for {name}. SSN: ***-**-{ssn_last4}. Phone: {phone}. Email: {email}."
            ssn_val = ssn.value
            extra_slots["ssn_last4"] = PIIValue("SOCIAL_SECURITY_NUMBER", ssn_val[-4:],
                                                 "government_legal", "direct_identifier")
            adv_type, adv_diff, techniques = "partial_redaction", "hard", ["partial_masking"]
        elif case_type == "mixed_case":
            template = "CONTACT: {name} EMAIL: {email} PHONE: {phone} SSN: {ssn} ADDRESS: {address}"
            adv_type, adv_diff, techniques = "mixed_case", "mild", ["case_variation"]
        elif case_type == "abbreviated":
            first = name.value.split()[0] if " " in name.value else name.value
            last = name.value.split()[-1] if " " in name.value else name.value
            extra_slots["abbrev_name"] = PIIValue("PERSON_NAME", f"{first[0]}. {last}",
                                                   "identity_demographics", "direct_identifier")
            template = "Ref: {abbrev_name} - {email} - {phone}"
            adv_type, adv_diff, techniques = "abbreviation", "moderate", ["name_abbreviation"]
        elif case_type == "dense_pii":
            template = "{name}|{email}|{phone}|{ssn}|{address}|{dob}|{org}|{emp_id}"
            adv_type, adv_diff, techniques = "dense_pii", "challenging", ["high_density"]
        elif case_type == "ambiguous":
            template = "Jordan sent {email} to Pat at {org}. They called {phone} about order #{emp_id}. SSN: {ssn}."
            name = PIIValue("PERSON_NAME", "Jordan", "identity_demographics", "direct_identifier")
            adv_type, adv_diff, techniques = "ambiguous", "hard", ["gender_ambiguous_name"]
        elif case_type == "format_noise":
            template = "Name:   {name}  \t Email:\t{email}\n\nPhone:  {phone}  SSN: {ssn}"
            adv_type, adv_diff, techniques = "format_noise", "moderate", ["whitespace_variation"]
        else:
            template = "{name}, {email}, {phone}, {ssn}"
            adv_type, adv_diff, techniques = None, "clean", []

        slots = {"name": name, "email": email, "phone": phone, "ssn": ssn}
        if "{address}" in template: slots["address"] = factory.address()
        if "{dob}" in template: slots["dob"] = factory.dob()
        if "{org}" in template: slots["org"] = factory.org()
        if "{emp_id}" in template: slots["emp_id"] = factory.employee_id()
        slots.update(extra_slots)

        rec = build_record(template, slots, language="en",
                           primary_dimension="edge_cases", domain="general",
                           difficulty=rng.choice(["hard", "challenging"]),
                           adversarial_type=adv_type,
                           adversarial_difficulty=adv_diff,
                           adversarial_techniques=techniques)
        records.append(rec)
    return records


# ─── Main ────────────────────────────────────────────────────────────────────

GENERATORS = {
    "entity_tracking": (generate_entity_tracking, 10000),
    "clinical": (generate_clinical, 5000),
    "financial": (generate_financial, 5000),
    "legal": (generate_legal, 3000),
    "code": (generate_code, 2000),
    "structured": (generate_structured_docs, 4000),
    "temporal": (generate_temporal, 3000),
    "edge_cases": (generate_edge_cases, 5000),
}


def main():
    parser = argparse.ArgumentParser(description="Generate new PII-Anon v2 records")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--category", type=str, choices=list(GENERATORS.keys()),
                        help="Generate only this category")
    parser.add_argument("--count", type=int, help="Override record count")
    parser.add_argument("--all", action="store_true", help="Generate all categories")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    rng = random.Random(args.seed)

    if args.category:
        gen_func, default_count = GENERATORS[args.category]
        count = args.count or default_count
        print(f"Generating {count} {args.category} records...")
        records = gen_func(rng, count)
    elif args.all or not args.category:
        records = []
        for cat, (gen_func, default_count) in GENERATORS.items():
            count = default_count
            print(f"Generating {count} {cat} records...")
            batch = gen_func(rng, count)
            records.extend(batch)
            print(f"  Generated {len(batch)} records")
    else:
        parser.print_help()
        return

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(records)} records to {args.output}")

    # Stats
    dim_counts = Counter(r["primary_dimension"] for r in records)
    domain_counts = Counter(r["domain"] for r in records)
    entity_types = Counter()
    for r in records:
        for a in r["annotations"]:
            entity_types[a["entity_type"]] += 1

    print(f"\nDimension distribution:")
    for d, c in dim_counts.most_common():
        print(f"  {d}: {c}")
    print(f"\nDomain distribution:")
    for d, c in domain_counts.most_common():
        print(f"  {d}: {c}")
    print(f"\nEntity types: {len(entity_types)}")
    for t, c in entity_types.most_common(20):
        print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
