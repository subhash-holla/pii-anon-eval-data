#!/usr/bin/env python3
"""
Generate v1.2.0 expansion records: realistic document formats, advanced adversarial,
and new entity types.

Adds:
- 20 realistic document format generators (8 healthcare + 5 legal + 7 financial)
- 13 advanced adversarial pattern generators (Unicode, OCR, Base64, etc.)
- 8 new entity types (NPI, DEA, UDI, BAR, DOCKET, CVV, PIN, USER_AGENT)
- ~33,500 new records total

Usage:
    PYTHONPATH=. python scripts/generate_v120_records.py --all
    PYTHONPATH=. python scripts/generate_v120_records.py --category healthcare
    PYTHONPATH=. python scripts/generate_v120_records.py --category adversarial --count 1000
"""

import argparse
import base64
import json
import random
import string
import urllib.parse
from collections import Counter
from pathlib import Path

from _version import DATASET_VERSION
from scripts.generate_records import (
    PIIFactory,
    PIIValue,
    build_record,
    NAME_DB,
    DIAGNOSES,
    MEDICATIONS,
    PROCEDURES,
    ORGS,
    JOB_TITLES,
    SEED,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "src" / "pii_anon_datasets" / "data" / "pii_anon_v120_generated.jsonl"


# ─── New Entity Type Generators (added to PIIFactory) ─────────────────────────

def _npi_number(factory: PIIFactory) -> PIIValue:
    """Generate a 10-digit NPI number."""
    num = "".join(str(factory.rng.randint(0, 9)) for _ in range(10))
    return PIIValue("NPI_NUMBER", num, "medical_biological", "direct_identifier")


def _dea_number(factory: PIIFactory) -> PIIValue:
    """Generate a DEA number: 2 letters + 7 digits."""
    prefix = factory._pick(["A", "B", "F", "M"])
    letter = factory._pick(string.ascii_uppercase)
    digits = "".join(str(factory.rng.randint(0, 9)) for _ in range(7))
    return PIIValue("DEA_NUMBER", f"{prefix}{letter}{digits}", "medical_biological", "direct_identifier")


def _medical_device_udi(factory: PIIFactory) -> PIIValue:
    """Generate a medical device UDI (GS1 format)."""
    company = "".join(str(factory.rng.randint(0, 9)) for _ in range(7))
    device = "".join(str(factory.rng.randint(0, 9)) for _ in range(7))
    return PIIValue("MEDICAL_DEVICE_UDI", f"(01)0{company}{device}", "medical_biological", "direct_identifier")


def _bar_number(factory: PIIFactory) -> PIIValue:
    """Generate a bar association number."""
    state = factory._pick(["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "MA", "VA"])
    num = factory.rng.randint(100000, 999999)
    return PIIValue("BAR_NUMBER", f"{state}-{num}", "government_legal", "direct_identifier")


def _docket_number(factory: PIIFactory) -> PIIValue:
    """Generate a court docket number (PACER format)."""
    district = factory.rng.randint(1, 11)
    year = factory.rng.randint(22, 26)
    case_type = factory._pick(["cv", "cr", "mc", "mj"])
    num = factory.rng.randint(1000, 9999)
    judge = "".join(factory._pick(string.ascii_uppercase) for _ in range(3))
    return PIIValue("DOCKET_NUMBER", f"{district}:{year}-{case_type}-{num:05d}-{judge}",
                    "government_legal", "direct_identifier")


def _cvv(factory: PIIFactory) -> PIIValue:
    """Generate a CVV/CVC code."""
    digits = factory.rng.randint(100, 999)
    return PIIValue("CVV", str(digits), "financial", "direct_identifier")


def _pin(factory: PIIFactory) -> PIIValue:
    """Generate a PIN code."""
    digits = factory.rng.randint(1000, 9999)
    return PIIValue("PIN", str(digits), "financial", "direct_identifier")


def _user_agent_string(factory: PIIFactory) -> PIIValue:
    """Generate a browser user agent string."""
    os_list = ["Windows NT 10.0; Win64; x64", "Macintosh; Intel Mac OS X 10_15_7",
               "X11; Linux x86_64", "Windows NT 11.0; Win64; x64"]
    browser_list = [
        ("Chrome", f"{factory.rng.randint(100,130)}.0.{factory.rng.randint(1000,9999)}.{factory.rng.randint(10,99)}"),
        ("Firefox", f"{factory.rng.randint(100,130)}.0"),
        ("Safari", f"{factory.rng.randint(600,620)}.{factory.rng.randint(1,9)}.{factory.rng.randint(1,15)}"),
    ]
    os = factory._pick(os_list)
    browser, ver = factory._pick(browser_list)
    return PIIValue("USER_AGENT_STRING",
                    f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) {browser}/{ver}",
                    "digital_online", "quasi_identifier")


# ─── Clinical Vocabulary ──────────────────────────────────────────────────────

SYMPTOMS = [
    "persistent cough and fatigue", "intermittent chest pain", "shortness of breath on exertion",
    "bilateral lower extremity edema", "nausea and decreased appetite", "headache and dizziness",
    "joint pain and morning stiffness", "difficulty sleeping and anxiety", "blurred vision",
    "frequent urination and increased thirst", "abdominal pain with bloating",
    "progressive weakness in lower extremities", "chronic low back pain radiating to left leg",
    "recurrent episodes of palpitations", "unexplained weight loss over past 3 months",
]

CLINICAL_FINDINGS = [
    "lungs clear to auscultation bilaterally", "regular rate and rhythm, no murmurs",
    "abdomen soft, non-tender, non-distended", "mild tenderness in right upper quadrant",
    "2+ pitting edema bilateral lower extremities", "decreased breath sounds at left base",
    "oriented x3, cranial nerves II-XII intact", "skin warm and dry, no rashes noted",
    "mild erythema of oropharynx without exudate", "full range of motion all extremities",
    "trace pedal edema bilaterally", "no lymphadenopathy or hepatosplenomegaly",
]

RADIOLOGY_FINDINGS = [
    "No acute cardiopulmonary process", "Small bilateral pleural effusions",
    "1.2 cm nodule in right upper lobe, recommend follow-up CT in 3 months",
    "Mild cardiomegaly without pulmonary edema", "Consolidation in left lower lobe consistent with pneumonia",
    "Degenerative changes of the lumbar spine", "No acute intracranial abnormality",
    "3mm stone in left ureterovesical junction with mild hydronephrosis",
    "Diffuse fatty infiltration of the liver", "Stable post-surgical changes",
]

SPECIMEN_TYPES = [
    "left breast, needle core biopsy", "colon, sigmoid, polypectomy",
    "skin, left forearm, excision", "thyroid, right lobe, lobectomy",
    "lymph node, cervical, excisional biopsy", "prostate, needle biopsy",
    "lung, right upper lobe, wedge resection", "endometrium, curettings",
]

PATHOLOGY_DIAGNOSES = [
    "Invasive ductal carcinoma, Grade 2, ER+/PR+/HER2-",
    "Tubular adenoma with low-grade dysplasia",
    "Basal cell carcinoma, nodular type, margins clear",
    "Papillary thyroid carcinoma, 1.5 cm, no lymphovascular invasion",
    "Reactive lymphoid hyperplasia, no evidence of malignancy",
    "Prostatic adenocarcinoma, Gleason 3+4=7",
    "Squamous cell carcinoma in situ",
    "Benign endometrial polyp with no atypia",
]

HOSPITALS = [
    "Memorial Regional Medical Center", "St. Mary's General Hospital",
    "University Hospital", "Community Health Center",
    "Northeast Medical Center", "Pacific General Hospital",
    "Children's Hospital of the Valley", "Mercy Medical Center",
    "Regional Cancer Institute", "Veterans Affairs Medical Center",
]

DEPARTMENTS = [
    "Internal Medicine", "Cardiology", "Pulmonology", "Orthopedics",
    "Neurology", "Gastroenterology", "Oncology", "Endocrinology",
    "Rheumatology", "Nephrology", "General Surgery", "Emergency Medicine",
]

# ─── Legal Vocabulary ─────────────────────────────────────────────────────────

LEGAL_SUBJECTS = [
    "breach of contract", "negligence claim", "employment discrimination",
    "personal injury", "medical malpractice", "intellectual property dispute",
    "securities fraud", "wrongful termination", "product liability",
    "insurance coverage dispute", "real estate transaction", "tax evasion investigation",
]

COURT_NAMES = [
    "United States District Court for the Southern District of New York",
    "Superior Court of California, County of Los Angeles",
    "United States District Court for the Northern District of Illinois",
    "Circuit Court of Cook County, Illinois",
    "United States District Court for the District of Massachusetts",
    "Supreme Court of the State of New York",
]

# ─── Financial Vocabulary ─────────────────────────────────────────────────────

COMPLAINT_SUBJECTS = [
    "unauthorized charges on credit card", "incorrect credit report information",
    "denied mortgage application", "fraudulent account opened in my name",
    "excessive late fees and interest charges", "failure to process loan modification",
    "unauthorized wire transfer from checking account",
    "identity theft and compromised account", "billing error on student loan",
    "insurance claim denied without proper review",
]

TRANSACTION_TYPES = [
    "wire transfer", "ACH debit", "check deposit", "ATM withdrawal",
    "POS purchase", "online transfer", "cash deposit", "returned check",
    "international wire", "P2P payment",
]


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: HEALTHCARE DOCUMENT FORMAT GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_progress_notes(rng: random.Random, count: int) -> list[dict]:
    """Generate clinical progress notes (SOAP format)."""
    records = []
    for i in range(count):
        lang = rng.choice(["en"] * 8 + ["es", "fr"])
        factory = PIIFactory(rng, lang)

        patient = factory.person_name()
        patient_first = patient.value.split()[0] if " " in patient.value else patient.value
        patient_last = patient.value.split()[-1] if " " in patient.value else patient.value
        provider = factory.person_name()
        npi = _npi_number(factory)
        mrn = factory.mrn()
        dob = factory.dob()
        ts = factory.timestamp()
        diag = factory.diagnosis()
        med = factory.medication()
        phone = factory.phone()
        ins = factory.insurance_id()
        symptom = rng.choice(SYMPTOMS)
        finding = rng.choice(CLINICAL_FINDINGS)
        dept = rng.choice(DEPARTMENTS)

        templates = [
            (
                f"PROGRESS NOTE\nDate: {{ts}}  Provider: Dr. {{provider}}, NPI: {{npi}}\n"
                f"Patient: {{patient}}  MRN: {{mrn}}  DOB: {{dob}}\nDepartment: {dept}\n\n"
                f"SUBJECTIVE: {patient_last} reports {symptom}. "
                f"Currently taking {{med}}. No new allergies.\n\n"
                f"OBJECTIVE: Vitals: BP {rng.randint(110,160)}/{rng.randint(60,95)}, HR {rng.randint(60,100)}, "
                f"Temp {rng.choice(['98.6', '99.1', '98.2', '100.1'])}F. "
                f"Exam: {finding}.\n\n"
                f"ASSESSMENT: {{diag}} - {'stable' if rng.random() > 0.3 else 'worsening'}.\n\n"
                f"PLAN: Continue {{med}}. Follow up in {rng.choice([2, 4, 6, 8])} weeks. "
                f"Contact {patient_first} at {{phone}} if symptoms worsen.\n"
                f"Insurance: {{ins}}"
            ),
            (
                f"OUTPATIENT VISIT NOTE\n"
                f"Patient: {{patient}} (MRN: {{mrn}}) | DOB: {{dob}}\n"
                f"Visit Date: {{ts}} | Provider: Dr. {{provider}} (NPI: {{npi}})\n"
                f"---\n"
                f"CC: {symptom}\n"
                f"HPI: {{patient}} is a {rng.randint(25,85)}-year-old presenting with {symptom}. "
                f"Symptom onset was {rng.choice(['3 days ago', '2 weeks ago', '1 month ago'])}. "
                f"Patient has been taking {{med}} with {rng.choice(['partial', 'good', 'minimal'])} relief.\n"
                f"PE: {finding}\n"
                f"A/P: {{diag}}. Continue current regimen. RTC in {rng.choice([2, 4])} weeks.\n"
                f"Patient phone: {{phone}} | Insurance: {{ins}}"
            ),
            (
                f"{dept} CLINIC NOTE\n"
                f"{{ts}}\n\n"
                f"RE: {{patient}}, MRN {{mrn}}, DOB {{dob}}\n"
                f"Attending: {{provider}}, NPI {{npi}}\n\n"
                f"This {rng.randint(30,80)}-year-old patient presents for "
                f"{'follow-up' if rng.random() > 0.5 else 'new consultation'} regarding {{diag}}.\n\n"
                f"Current medications include {{med}}. The patient reports {symptom}.\n"
                f"On examination: {finding}.\n\n"
                f"We discussed treatment options at length with {{patient}}. "
                f"Plan to {'continue current therapy' if rng.random() > 0.3 else 'adjust medication regimen'}. "
                f"Please contact {{patient}} at {{phone}} with lab results.\n"
                f"Insurance ID: {{ins}}"
            ),
        ]

        template = rng.choice(templates)
        slots = {
            "patient": patient, "provider": provider, "npi": npi, "mrn": mrn,
            "dob": dob, "ts": ts, "diag": diag, "med": med, "phone": phone, "ins": ins,
        }

        rec = build_record(template, slots, language=lang,
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="clinical", document_type="progress_note",
                           difficulty=rng.choice(["moderate", "hard"]),
                           regulatory_domains=["gdpr", "hipaa"])
        records.append(rec)
    return records


def generate_nursing_notes(rng: random.Random, count: int) -> list[dict]:
    """Generate nursing notes with informal language and abbreviations."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        patient = factory.person_name()
        pt_last = patient.value.split()[-1] if " " in patient.value else patient.value
        mrn = factory.mrn()
        ts = factory.timestamp()
        med = factory.medication()
        phone = factory.phone()

        vitals = (f"BP {rng.randint(100,180)}/{rng.randint(55,100)}, "
                  f"HR {rng.randint(55,120)}, RR {rng.randint(12,28)}, "
                  f"SpO2 {rng.randint(88,100)}%, Temp {rng.choice(['36.8', '37.2', '37.5', '38.1'])}C")

        templates = [
            (
                f"NURSING ASSESSMENT - {{ts}}\n"
                f"Pt: {{patient}} MRN: {{mrn}}\n"
                f"Shift: {rng.choice(['0700-1900', '1900-0700'])}\n\n"
                f"VS: {vitals}\n"
                f"Pt {rng.choice(['alert and oriented x4', 'drowsy but arousable', 'alert, oriented x3'])}. "
                f"{pt_last} c/o {rng.choice(['pain 6/10 at incision site', 'mild nausea', 'difficulty sleeping', 'no complaints'])}. "
                f"Admin {{med}} at {rng.randint(6,22):02d}00. "
                f"{rng.choice(['Tolerated well', 'Pt reported relief', 'No adverse effects noted'])}.\n"
                f"Call bell within reach. Side rails x2 up. "
                f"Family notified at {{phone}}.\n"
                f"- {rng.choice(['RN Smith', 'RN Johnson', 'RN Williams', 'RN Davis'])}"
            ),
            (
                f"{{ts}} - Bedside assessment\n"
                f"{{patient}} ({{mrn}})\n"
                f"Vitals: {vitals}\n"
                f"Pt resting comfortably. IV site L forearm - no signs of infiltration. "
                f"I&O: intake {rng.randint(500,2000)}ml, output {rng.randint(300,1500)}ml. "
                f"Wound care completed per protocol. "
                f"{{med}} given as scheduled. {pt_last} tolerated PO diet. "
                f"NOK contacted at {{phone}} re: discharge planning.\n"
                f"Will continue to monitor."
            ),
        ]

        template = rng.choice(templates)
        slots = {"patient": patient, "mrn": mrn, "ts": ts, "med": med, "phone": phone}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="clinical", document_type="nursing_note",
                           difficulty=rng.choice(["moderate", "hard"]),
                           regulatory_domains=["gdpr", "hipaa"])
        records.append(rec)
    return records


def generate_radiology_reports(rng: random.Random, count: int) -> list[dict]:
    """Generate radiology reports with structured sections."""
    records = []
    modalities = ["Chest X-Ray", "CT Abdomen/Pelvis", "MRI Brain", "CT Chest",
                  "Ultrasound Abdomen", "MRI Lumbar Spine", "CT Head without Contrast"]
    for i in range(count):
        factory = PIIFactory(rng, "en")
        patient = factory.person_name()
        mrn = factory.mrn()
        dob = factory.dob()
        referring = factory.person_name()
        reading = factory.person_name()
        npi = _npi_number(factory)
        ts = factory.timestamp()
        finding = rng.choice(RADIOLOGY_FINDINGS)
        modality = rng.choice(modalities)
        hospital = rng.choice(HOSPITALS)

        template = (
            f"RADIOLOGY REPORT\n"
            f"{hospital}\n\n"
            f"Patient: {{patient}}  MRN: {{mrn}}  DOB: {{dob}}\n"
            f"Exam: {modality}\n"
            f"Date: {{ts}}\n"
            f"Referring Physician: Dr. {{referring}}\n"
            f"Radiologist: Dr. {{reading}}, NPI: {{npi}}\n\n"
            f"CLINICAL INDICATION: {rng.choice(['Rule out pneumonia', 'Chest pain', 'Follow-up', 'Abdominal pain', 'Headache'])}.\n\n"
            f"COMPARISON: {rng.choice(['None available', 'Prior study from 2024-01-15', 'Comparison with previous exam'])}.\n\n"
            f"FINDINGS:\n{finding}\n\n"
            f"IMPRESSION:\n"
            f"1. {finding.split('.')[0]}.\n"
            f"2. {rng.choice(['No acute findings', 'Clinical correlation recommended', 'Follow-up recommended'])}.\n\n"
            f"Electronically signed by Dr. {{reading}}"
        )

        slots = {"patient": patient, "mrn": mrn, "dob": dob, "referring": referring,
                 "reading": reading, "npi": npi, "ts": ts}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="clinical", document_type="radiology_report",
                           difficulty="moderate",
                           regulatory_domains=["gdpr", "hipaa"])
        records.append(rec)
    return records


def generate_pathology_reports(rng: random.Random, count: int) -> list[dict]:
    """Generate pathology reports with specimen and accession details."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        patient = factory.person_name()
        mrn = factory.mrn()
        dob = factory.dob()
        pathologist = factory.person_name()
        npi = _npi_number(factory)
        surgeon = factory.person_name()
        ts = factory.timestamp()
        accession = f"S{rng.randint(24, 26)}-{rng.randint(10000, 99999)}"
        specimen = rng.choice(SPECIMEN_TYPES)
        path_diag = rng.choice(PATHOLOGY_DIAGNOSES)

        template = (
            f"SURGICAL PATHOLOGY REPORT\n"
            f"Accession #: {accession}\n\n"
            f"Patient: {{patient}}  MRN: {{mrn}}  DOB: {{dob}}\n"
            f"Date of Surgery: {{ts}}\n"
            f"Surgeon: Dr. {{surgeon}}\n"
            f"Pathologist: Dr. {{pathologist}}, NPI: {{npi}}\n\n"
            f"SPECIMEN: {specimen}\n\n"
            f"GROSS DESCRIPTION:\n"
            f"Received fresh, {rng.choice(['labeled with patient name and MRN', 'in formalin'])}. "
            f"Specimen measures {rng.randint(1, 8)}.{rng.randint(0,9)} x "
            f"{rng.randint(1, 5)}.{rng.randint(0,9)} x "
            f"{rng.randint(0, 3)}.{rng.randint(0,9)} cm. "
            f"{'Entirely submitted' if rng.random() > 0.5 else 'Representative sections submitted'}.\n\n"
            f"DIAGNOSIS:\n{path_diag}\n\n"
            f"Signed: Dr. {{pathologist}}"
        )

        slots = {"patient": patient, "mrn": mrn, "dob": dob, "surgeon": surgeon,
                 "pathologist": pathologist, "npi": npi, "ts": ts}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="clinical", document_type="pathology_report",
                           difficulty="moderate",
                           regulatory_domains=["gdpr", "hipaa"])
        records.append(rec)
    return records


def generate_clinical_transcripts(rng: random.Random, count: int) -> list[dict]:
    """Generate doctor-patient conversation transcripts."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        patient = factory.person_name()
        pt_first = patient.value.split()[0] if " " in patient.value else patient.value
        doctor = factory.person_name()
        mrn = factory.mrn()
        dob = factory.dob()
        phone = factory.phone()
        med = factory.medication()
        diag = factory.diagnosis()
        pharmacy_name = rng.choice(["CVS on Main Street", "Walgreens at Oak Plaza", "Rite Aid downtown"])

        template = (
            f"CLINICAL ENCOUNTER TRANSCRIPT\n"
            f"Patient: {{patient}} (MRN: {{mrn}})\n"
            f"Provider: Dr. {{doctor}}\n\n"
            f"DR: Good morning, {{patient}}. How are you feeling today?\n\n"
            f"PT: Hi doctor. I've been having {rng.choice(SYMPTOMS)} for about "
            f"{rng.choice(['a week', 'two weeks', 'a month'])} now.\n\n"
            f"DR: I see. And you were born on {{dob}}, correct? Just confirming for our records.\n\n"
            f"PT: Yes, that's right.\n\n"
            f"DR: Are you still taking {{med}}?\n\n"
            f"PT: Yes, I take it {rng.choice(['every morning', 'twice a day', 'at bedtime'])}.\n\n"
            f"DR: Good. Based on the exam, I think we're looking at {{diag}}. "
            f"I'd like to adjust your medication. Can we reach you at {{phone}} with results?\n\n"
            f"PT: Yes, that's my cell. You can also call my {rng.choice(['wife', 'husband', 'daughter'])} "
            f"if I don't answer.\n\n"
            f"DR: Perfect, {pt_first}. I'll send the prescription to {pharmacy_name}. "
            f"Please schedule a follow-up in two weeks."
        )

        slots = {"patient": patient, "doctor": doctor, "mrn": mrn, "dob": dob,
                 "phone": phone, "med": med, "diag": diag}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="clinical", document_type="clinical_transcript",
                           difficulty=rng.choice(["hard", "challenging"]),
                           regulatory_domains=["gdpr", "hipaa"])
        records.append(rec)
    return records


def generate_referral_letters(rng: random.Random, count: int) -> list[dict]:
    """Generate referral letters between providers."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        patient = factory.person_name()
        referring_dr = factory.person_name()
        specialist = factory.person_name()
        ref_npi = _npi_number(factory)
        mrn = factory.mrn()
        dob = factory.dob()
        diag = factory.diagnosis()
        med = factory.medication()
        phone = factory.phone()
        email = factory.email(referring_dr.value)
        ins = factory.insurance_id()
        ref_hospital = rng.choice(HOSPITALS)
        spec_dept = rng.choice(DEPARTMENTS)

        template = (
            f"REFERRAL LETTER\n\n"
            f"From: Dr. {{referring_dr}}, NPI: {{ref_npi}}\n"
            f"      {ref_hospital}\n"
            f"      Email: {{email}}\n\n"
            f"To: Dr. {{specialist}}, Department of {spec_dept}\n\n"
            f"Date: {rng.randint(2024,2026)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}\n\n"
            f"RE: {{patient}} (DOB: {{dob}}, MRN: {{mrn}})\n\n"
            f"Dear Dr. {{specialist}},\n\n"
            f"I am writing to refer my patient, {{patient}}, for evaluation of {{diag}}. "
            f"{{patient}} is a {rng.randint(25,85)}-year-old who has been under my care for "
            f"{rng.choice(['the past year', 'several years', 'six months'])}.\n\n"
            f"Current medications include {{med}}. "
            f"Recent labs and imaging are attached for your review.\n\n"
            f"The patient's insurance ID is {{ins}}. "
            f"They can be reached at {{phone}} to schedule an appointment.\n\n"
            f"Thank you for your prompt attention to this referral.\n\n"
            f"Sincerely,\nDr. {{referring_dr}}"
        )

        slots = {"patient": patient, "referring_dr": referring_dr, "specialist": specialist,
                 "ref_npi": ref_npi, "mrn": mrn, "dob": dob, "diag": diag, "med": med,
                 "phone": phone, "email": email, "ins": ins}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="clinical", document_type="referral_letter",
                           difficulty="moderate",
                           regulatory_domains=["gdpr", "hipaa"])
        records.append(rec)
    return records


def generate_prescriptions(rng: random.Random, count: int) -> list[dict]:
    """Generate prescription/pharmacy records with DEA and NPI numbers."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        patient = factory.person_name()
        prescriber = factory.person_name()
        npi = _npi_number(factory)
        dea = _dea_number(factory)
        mrn = factory.mrn()
        dob = factory.dob()
        med = factory.medication()
        phone = factory.phone()
        address = factory.address()
        ins = factory.insurance_id()
        rx_num = f"RX-{rng.randint(1000000, 9999999)}"

        template = (
            f"PRESCRIPTION\n"
            f"Rx#: {rx_num}\n\n"
            f"Patient: {{patient}}\n"
            f"DOB: {{dob}}  MRN: {{mrn}}\n"
            f"Address: {{address}}\n"
            f"Phone: {{phone}}\n\n"
            f"Prescriber: Dr. {{prescriber}}\n"
            f"NPI: {{npi}}  DEA: {{dea}}\n\n"
            f"Medication: {{med}}\n"
            f"Sig: {rng.choice(['Take 1 tablet by mouth daily', 'Take 1 tablet twice daily with food', 'Apply topically as directed'])}\n"
            f"Qty: {rng.choice(['30', '60', '90'])}  Refills: {rng.randint(0, 5)}\n"
            f"DAW: {rng.choice(['Yes', 'No'])}\n\n"
            f"Insurance: {{ins}}\n"
            f"Signature: Dr. {{prescriber}}"
        )

        slots = {"patient": patient, "prescriber": prescriber, "npi": npi, "dea": dea,
                 "mrn": mrn, "dob": dob, "med": med, "phone": phone, "address": address, "ins": ins}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="form",
                           domain="clinical", document_type="prescription",
                           difficulty="moderate",
                           regulatory_domains=["gdpr", "hipaa"])
        records.append(rec)
    return records


def generate_insurance_claims_clinical(rng: random.Random, count: int) -> list[dict]:
    """Generate clinical insurance claim narratives."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        patient = factory.person_name()
        provider = factory.person_name()
        npi = _npi_number(factory)
        mrn = factory.mrn()
        dob = factory.dob()
        diag = factory.diagnosis()
        procedure = factory.procedure()
        ins = factory.insurance_id()
        policy = factory.insurance_policy()
        claim_num = f"CLM-{rng.randint(2024, 2026)}-{rng.randint(100000, 999999)}"
        phone = factory.phone()

        template = (
            f"INSURANCE CLAIM NARRATIVE\n"
            f"Claim #: {claim_num}\n\n"
            f"Patient: {{patient}} | DOB: {{dob}} | MRN: {{mrn}}\n"
            f"Insurance ID: {{ins}} | Policy: {{policy}}\n"
            f"Provider: Dr. {{provider}} | NPI: {{npi}}\n\n"
            f"NARRATIVE:\n"
            f"{{patient}} presented on {rng.randint(2024,2026)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d} "
            f"with symptoms consistent with {{diag}}. After examination and diagnostic workup, "
            f"{{procedure}} was performed. The patient tolerated the procedure well. "
            f"Post-procedure care instructions were provided. "
            f"Follow-up appointment scheduled in {rng.choice([2, 4, 6])} weeks.\n\n"
            f"Contact patient at {{phone}} for any claim inquiries.\n\n"
            f"BILLING CODES: {rng.choice(['99213', '99214', '99215'])}, "
            f"{rng.choice(['J0696', 'J1100', 'J3490'])}"
        )

        slots = {"patient": patient, "provider": provider, "npi": npi, "mrn": mrn,
                 "dob": dob, "diag": diag, "ins": ins, "policy": policy, "phone": phone}
        # procedure used in plain text, not as slot (it's part of the narrative flow)
        # Actually let's make it a slot for annotation:
        slots["procedure"] = PIIValue("PROCEDURE_NAME", procedure.value,
                                       "medical_biological", "sensitive_attribute")

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="clinical", document_type="insurance_claim",
                           difficulty="hard",
                           regulatory_domains=["gdpr", "hipaa"])
        records.append(rec)
    return records


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: LEGAL DOCUMENT FORMAT GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_deposition_transcripts(rng: random.Random, count: int) -> list[dict]:
    """Generate deposition transcripts with Q&A format."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        witness = factory.person_name()
        w_first = witness.value.split()[0] if " " in witness.value else witness.value
        attorney1 = factory.person_name()
        attorney2 = factory.person_name()
        bar1 = _bar_number(factory)
        docket = _docket_number(factory)
        address = factory.address()
        dob = factory.dob()
        ssn = factory.ssn()
        phone = factory.phone()
        email = factory.email(witness.value)
        party = factory.person_name()
        org = factory.org()
        ts = factory.timestamp()

        template = (
            f"DEPOSITION OF {{witness}}\n"
            f"Case No: {{docket}}\n"
            f"Date: {{ts}}\n"
            f"Court Reporter: Certified Shorthand Reporter\n\n"
            f"EXAMINATION BY {{attorney1}} (Bar No. {{bar1}}):\n\n"
            f"Q: Please state your full name for the record.\n"
            f"A: {{witness}}.\n\n"
            f"Q: And your date of birth?\n"
            f"A: {{dob}}.\n\n"
            f"Q: What is your current address?\n"
            f"A: {{address}}.\n\n"
            f"Q: And the best phone number to reach you?\n"
            f"A: {{phone}}.\n\n"
            f"Q: What is your email address?\n"
            f"A: {{email}}.\n\n"
            f"Q: {w_first}, do you know the plaintiff, {{party}}?\n"
            f"A: Yes, I worked with {{party}} at {{org}} for approximately "
            f"{rng.randint(1,10)} years.\n\n"
            f"Q: And your Social Security Number, for the record?\n"
            f"A: {{ssn}}.\n\n"
            f"Q: Can you describe the events of "
            f"{rng.choice(['January', 'March', 'June', 'September'])} {rng.randint(2022, 2025)}?\n"
            f"A: Yes. I was present when {{party}} submitted the complaint to {{org}}.\n\n"
            f"{{attorney1}}: No further questions at this time.\n"
            f"{{attorney2}}: We reserve cross-examination."
        )

        slots = {"witness": witness, "attorney1": attorney1, "attorney2": attorney2,
                 "bar1": bar1, "docket": docket, "address": address, "dob": dob,
                 "ssn": ssn, "phone": phone, "email": email, "party": party,
                 "org": org, "ts": ts}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="legal", document_type="deposition_transcript",
                           difficulty="hard",
                           regulatory_domains=["gdpr", "ccpa"])
        records.append(rec)
    return records


def generate_witness_statements(rng: random.Random, count: int) -> list[dict]:
    """Generate first-person witness statements."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        witness = factory.person_name()
        w_first = witness.value.split()[0] if " " in witness.value else witness.value
        subject = factory.person_name()
        dob = factory.dob()
        address = factory.address()
        phone = factory.phone()
        org = factory.org()
        case_no = factory.court_case_number()
        ts = factory.timestamp()

        templates = [
            (
                f"WITNESS STATEMENT\n"
                f"Case: {{case_no}}\n"
                f"Date: {{ts}}\n\n"
                f"I, {{witness}}, of {{address}}, make this statement voluntarily.\n\n"
                f"My date of birth is {{dob}}. I can be contacted at {{phone}}.\n\n"
                f"On the date in question, I was employed at {{org}} as a "
                f"{rng.choice(JOB_TITLES)}. I personally observed {{subject}} "
                f"enter the premises at approximately {rng.randint(8,18):02d}:{rng.choice(['00','15','30','45'])}. "
                f"I recognized {{subject}} because we had worked together previously.\n\n"
                f"{{subject}} appeared {rng.choice(['agitated', 'calm', 'in a hurry', 'normal'])} "
                f"and {rng.choice(['spoke briefly with the receptionist', 'went directly to the office', 'waited in the lobby'])}.\n\n"
                f"I believe this statement to be true and accurate.\n\n"
                f"Signed: {{witness}}\n"
                f"Date: {{ts}}"
            ),
        ]

        template = rng.choice(templates)
        slots = {"witness": witness, "subject": subject, "dob": dob, "address": address,
                 "phone": phone, "org": org, "case_no": case_no, "ts": ts}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="legal", document_type="witness_statement",
                           difficulty="hard",
                           regulatory_domains=["gdpr", "ccpa"])
        records.append(rec)
    return records


def generate_legal_memos(rng: random.Random, count: int) -> list[dict]:
    """Generate legal memoranda with client PII in analytical context."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        client = factory.person_name()
        attorney = factory.person_name()
        bar = _bar_number(factory)
        case_no = factory.court_case_number()
        opposing = factory.person_name()
        org = factory.org()
        ssn = factory.ssn()
        address = factory.address()
        ts = factory.timestamp()
        subject = rng.choice(LEGAL_SUBJECTS)

        template = (
            f"CONFIDENTIAL LEGAL MEMORANDUM\n\n"
            f"TO: File\n"
            f"FROM: {{attorney}} (Bar No. {{bar}})\n"
            f"DATE: {{ts}}\n"
            f"RE: {{client}} v. {{org}} - {subject}\n"
            f"    Case No. {{case_no}}\n\n"
            f"FACTS:\n"
            f"Our client, {{client}} (SSN: {{ssn}}), residing at {{address}}, "
            f"has retained this office regarding a {subject} matter against {{org}}. "
            f"The opposing party, {{opposing}}, has filed a counterclaim.\n\n"
            f"ANALYSIS:\n"
            f"Under the applicable statute, {{client}}'s claim appears "
            f"{rng.choice(['strong', 'viable but with some risk', 'challenging'])}. "
            f"The key issue is whether {{org}}'s actions constituted "
            f"{rng.choice(['a material breach', 'negligence', 'discrimination', 'fraud'])}. "
            f"{{opposing}}'s defense will likely focus on "
            f"{rng.choice(['comparative negligence', 'statute of limitations', 'lack of standing'])}.\n\n"
            f"RECOMMENDATION:\n"
            f"I recommend {rng.choice(['proceeding to mediation', 'filing a motion for summary judgment', 'engaging in discovery'])}.\n\n"
            f"{{attorney}}"
        )

        slots = {"client": client, "attorney": attorney, "bar": bar, "case_no": case_no,
                 "opposing": opposing, "org": org, "ssn": ssn, "address": address, "ts": ts}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="legal", document_type="legal_memo",
                           difficulty="hard",
                           regulatory_domains=["gdpr", "ccpa"])
        records.append(rec)
    return records


def generate_court_opinions(rng: random.Random, count: int) -> list[dict]:
    """Generate court opinion excerpts with party PII."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        plaintiff = factory.person_name()
        defendant = factory.person_name()
        judge = factory.person_name()
        docket = _docket_number(factory)
        court = rng.choice(COURT_NAMES)
        ts = factory.timestamp()
        org = factory.org()

        template = (
            f"{court}\n\n"
            f"{{plaintiff}}, Plaintiff,\n"
            f"  v.\n"
            f"{{defendant}} and {{org}}, Defendants.\n\n"
            f"Case No. {{docket}}\n"
            f"Filed: {{ts}}\n"
            f"Judge: Hon. {{judge}}\n\n"
            f"OPINION AND ORDER\n\n"
            f"This matter comes before the Court on Defendant's motion to dismiss. "
            f"Plaintiff {{plaintiff}}, a {rng.randint(25,70)}-year-old resident of "
            f"{rng.choice(['New York', 'California', 'Illinois', 'Texas', 'Florida'])}, "
            f"alleges that {{defendant}}, acting in {rng.choice(['his', 'her'])} capacity as "
            f"{rng.choice(JOB_TITLES)} of {{org}}, "
            f"{rng.choice(['committed fraud', 'breached the employment agreement', 'engaged in discrimination'])}.\n\n"
            f"Having reviewed the pleadings and arguments of counsel, the Court finds that "
            f"{{plaintiff}}'s complaint {rng.choice(['states a plausible claim', 'fails to state a claim'])} "
            f"upon which relief can be granted.\n\n"
            f"IT IS SO ORDERED.\n\n"
            f"{{judge}}\n"
            f"United States District Judge"
        )

        slots = {"plaintiff": plaintiff, "defendant": defendant, "judge": judge,
                 "docket": docket, "org": org, "ts": ts}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="legal", document_type="court_opinion",
                           difficulty="moderate",
                           regulatory_domains=["gdpr", "ccpa"])
        records.append(rec)
    return records


def generate_discovery_letters(rng: random.Random, count: int) -> list[dict]:
    """Generate discovery cover letters with multi-party references."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        sender_atty = factory.person_name()
        recipient_atty = factory.person_name()
        bar = _bar_number(factory)
        client = factory.person_name()
        case_no = factory.court_case_number()
        email = factory.email(sender_atty.value)
        phone = factory.phone()
        org = factory.org()

        template = (
            f"RE: {{client}} v. {{org}}\n"
            f"    Case No. {{case_no}}\n\n"
            f"Dear {{recipient_atty}},\n\n"
            f"Enclosed please find {{client}}'s responses to your First Set of Interrogatories "
            f"and Request for Production of Documents, Bates-stamped {rng.choice(['SMITH', 'JONES', 'DAVIS'])}"
            f"{rng.randint(1, 100):06d} through "
            f"{rng.choice(['SMITH', 'JONES', 'DAVIS'])}{rng.randint(100, 500):06d}.\n\n"
            f"We note our objections as stated in the accompanying responses. "
            f"Privileged documents have been withheld and are listed on the attached privilege log.\n\n"
            f"Please direct any questions to the undersigned at {{phone}} or {{email}}.\n\n"
            f"Sincerely,\n\n"
            f"{{sender_atty}}\n"
            f"Bar No. {{bar}}\n"
            f"Counsel for {{client}}"
        )

        slots = {"sender_atty": sender_atty, "recipient_atty": recipient_atty,
                 "bar": bar, "client": client, "case_no": case_no, "email": email,
                 "phone": phone, "org": org}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="legal", document_type="discovery_letter",
                           difficulty="moderate",
                           regulatory_domains=["gdpr", "ccpa"])
        records.append(rec)
    return records


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: FINANCIAL DOCUMENT FORMAT GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_complaint_emails(rng: random.Random, count: int) -> list[dict]:
    """Generate customer complaint emails with free-text PII."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        customer = factory.person_name()
        c_first = customer.value.split()[0] if " " in customer.value else customer.value
        email = factory.email(customer.value)
        phone = factory.phone()
        acct = factory.bank_account()
        cc = factory.credit_card()
        ssn = factory.ssn()
        address = factory.address()
        org = factory.org()
        complaint = rng.choice(COMPLAINT_SUBJECTS)

        templates = [
            (
                f"From: {{email}}\n"
                f"To: complaints@{rng.choice(['bigbank', 'nationalfinance', 'creditunion'])}.com\n"
                f"Subject: URGENT - {complaint}\n\n"
                f"To whom it may concern,\n\n"
                f"My name is {{customer}} and I am writing regarding {complaint}. "
                f"My account number is {{acct}} and the card ending in {cc.value[-4:]} (full number: {{cc}}) "
                f"was involved in the incident.\n\n"
                f"My SSN is {{ssn}} - I'm providing this so you can verify my identity. "
                f"My address is {{address}} and you can reach me at {{phone}}.\n\n"
                f"I have been a customer of {{org}} for {rng.randint(2,15)} years and I am "
                f"extremely {rng.choice(['frustrated', 'disappointed', 'upset', 'concerned'])} "
                f"about this situation.\n\n"
                f"Please resolve this immediately.\n\n"
                f"Regards,\n{c_first}"
            ),
            (
                f"Subject: Account {{acct}} - {complaint}\n"
                f"From: {{email}}\n\n"
                f"Hi,\n\n"
                f"I need help with my account. I'm {{customer}}, SSN {{ssn}}. "
                f"There are unauthorized charges on my card {{cc}}. "
                f"My address on file should be {{address}}. "
                f"Call me at {{phone}} ASAP.\n\n"
                f"This is ridiculous. I've been with {{org}} forever and this is how you treat customers?\n\n"
                f"{{customer}}"
            ),
        ]

        template = rng.choice(templates)
        slots = {"customer": customer, "email": email, "phone": phone, "acct": acct,
                 "cc": cc, "ssn": ssn, "address": address, "org": org}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="financial", document_type="complaint_email",
                           difficulty=rng.choice(["hard", "challenging"]),
                           regulatory_domains=["gdpr", "ccpa", "pci_dss"])
        records.append(rec)
    return records


def generate_support_chats(rng: random.Random, count: int) -> list[dict]:
    """Generate customer support chat logs with multi-turn PII disclosure."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        customer = factory.person_name()
        c_first = customer.value.split()[0] if " " in customer.value else customer.value
        agent_name = rng.choice(["Alex", "Sam", "Jordan", "Pat", "Morgan"])
        acct = factory.bank_account()
        phone = factory.phone()
        email = factory.email(customer.value)
        cc = factory.credit_card()
        cvv = _cvv(factory)
        dob = factory.dob()
        ssn = factory.ssn()

        template = (
            f"CHAT TRANSCRIPT - {rng.choice(['LiveChat', 'Zendesk', 'Intercom'])} "
            f"Session #{rng.randint(100000,999999)}\n\n"
            f"[{rng.randint(9,17):02d}:{rng.randint(0,59):02d}] CUSTOMER: hi i need help with my account\n\n"
            f"[{rng.randint(9,17):02d}:{rng.randint(0,59):02d}] {agent_name}: Hello! I'd be happy to help. "
            f"Can I get your name please?\n\n"
            f"[{rng.randint(9,17):02d}:{rng.randint(0,59):02d}] CUSTOMER: {{customer}}\n\n"
            f"[{rng.randint(9,17):02d}:{rng.randint(0,59):02d}] {agent_name}: Thank you, {c_first}. "
            f"For verification, can you provide your account number and date of birth?\n\n"
            f"[{rng.randint(9,17):02d}:{rng.randint(0,59):02d}] CUSTOMER: acct {{acct}} dob {{dob}}\n\n"
            f"[{rng.randint(9,17):02d}:{rng.randint(0,59):02d}] {agent_name}: "
            f"Thank you. I also need the last 4 of your SSN.\n\n"
            f"[{rng.randint(9,17):02d}:{rng.randint(0,59):02d}] CUSTOMER: {{ssn}}\n\n"
            f"[{rng.randint(9,17):02d}:{rng.randint(0,59):02d}] {agent_name}: "
            f"Verified. I see the issue on your account. "
            f"I'll send a confirmation to {{email}}. "
            f"Is {{phone}} still the best number for callback?\n\n"
            f"[{rng.randint(9,17):02d}:{rng.randint(0,59):02d}] CUSTOMER: yes thats correct. "
            f"also my card {{cc}} cvv {{cvv}} keeps getting declined\n\n"
            f"[{rng.randint(9,17):02d}:{rng.randint(0,59):02d}] {agent_name}: "
            f"I see. Let me look into that for you. Please don't share CVV in chat for security reasons.\n\n"
            f"[{rng.randint(9,17):02d}:{rng.randint(0,59):02d}] CUSTOMER: ok sorry"
        )

        slots = {"customer": customer, "acct": acct, "dob": dob, "ssn": ssn,
                 "email": email, "phone": phone, "cc": cc, "cvv": cvv}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="financial", document_type="support_chat",
                           difficulty="challenging",
                           regulatory_domains=["gdpr", "ccpa", "pci_dss"])
        records.append(rec)
    return records


def generate_analyst_notes(rng: random.Random, count: int) -> list[dict]:
    """Generate financial analyst notes with client PII in analytical context."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        client = factory.person_name()
        advisor = factory.person_name()
        acct = factory.bank_account()
        ssn = factory.ssn()
        salary = factory.salary()
        org = factory.org()
        phone = factory.phone()
        ts = factory.timestamp()

        template = (
            f"CLIENT PORTFOLIO NOTE\n"
            f"Date: {{ts}}\n"
            f"Advisor: {{advisor}} | Client: {{client}}\n"
            f"Account: {{acct}} | SSN: {{ssn}}\n\n"
            f"Met with {{client}} to review portfolio allocation. "
            f"Client reports annual income of {{salary}} from {{org}}. "
            f"Risk tolerance: {rng.choice(['conservative', 'moderate', 'aggressive'])}. "
            f"Current allocation: {rng.randint(40,80)}% equities, "
            f"{rng.randint(10,40)}% fixed income, remainder in alternatives.\n\n"
            f"Recommended rebalancing to {rng.choice(['increase bond allocation', 'shift to growth stocks', 'add real estate exposure'])}. "
            f"{{client}} agreed to the proposed changes. "
            f"Will follow up at {{phone}} next quarter.\n\n"
            f"- {{advisor}}"
        )

        slots = {"client": client, "advisor": advisor, "acct": acct, "ssn": ssn,
                 "salary": salary, "org": org, "phone": phone, "ts": ts}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="financial", document_type="analyst_note",
                           difficulty="moderate",
                           regulatory_domains=["gdpr", "ccpa", "sox"])
        records.append(rec)
    return records


def generate_loan_narratives(rng: random.Random, count: int) -> list[dict]:
    """Generate loan application narratives with dense personal + financial PII."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        applicant = factory.person_name()
        ssn = factory.ssn()
        dob = factory.dob()
        address = factory.address()
        phone = factory.phone()
        email = factory.email(applicant.value)
        org = factory.org()
        job = factory.job_title()
        salary = factory.salary()
        acct = factory.bank_account()
        tax_id = factory.tax_id()

        template = (
            f"LOAN APPLICATION NARRATIVE\n"
            f"Application #: LA-{rng.randint(100000, 999999)}\n\n"
            f"Applicant: {{applicant}}\n"
            f"SSN: {{ssn}} | DOB: {{dob}}\n"
            f"Address: {{address}}\n"
            f"Phone: {{phone}} | Email: {{email}}\n\n"
            f"EMPLOYMENT:\n"
            f"Current employer: {{org}} | Position: {{job}} | Annual income: {{salary}}\n"
            f"Length of employment: {rng.randint(1, 20)} years\n"
            f"Employer Tax ID: {{tax_id}}\n\n"
            f"FINANCIAL:\n"
            f"Primary checking account: {{acct}}\n"
            f"Total assets: ${rng.randint(10, 500) * 1000:,}\n"
            f"Total liabilities: ${rng.randint(5, 200) * 1000:,}\n"
            f"Credit score: {rng.randint(580, 850)}\n\n"
            f"LOAN REQUEST:\n"
            f"Purpose: {rng.choice(['Home purchase', 'Auto loan', 'Debt consolidation', 'Home improvement'])}\n"
            f"Amount requested: ${rng.randint(10, 500) * 1000:,}\n"
            f"Term: {rng.choice([60, 120, 180, 360])} months\n\n"
            f"Underwriter notes: Applicant {{applicant}} meets initial qualification criteria."
        )

        slots = {"applicant": applicant, "ssn": ssn, "dob": dob, "address": address,
                 "phone": phone, "email": email, "org": org, "job": job,
                 "salary": salary, "acct": acct, "tax_id": tax_id}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="form",
                           domain="financial", document_type="loan_narrative",
                           difficulty="challenging",
                           regulatory_domains=["gdpr", "ccpa", "sox"])
        records.append(rec)
    return records


def generate_sar_narratives(rng: random.Random, count: int) -> list[dict]:
    """Generate Suspicious Activity Report narratives."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        subject = factory.person_name()
        s_first = subject.value.split()[0] if " " in subject.value else subject.value
        ssn = factory.ssn()
        dob = factory.dob()
        address = factory.address()
        acct = factory.bank_account()
        routing = factory.routing_number()
        org = factory.org()
        phone = factory.phone()

        amounts = [f"${rng.randint(5, 50) * 1000:,}" for _ in range(3)]
        dates = [f"2025-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}" for _ in range(3)]

        template = (
            f"SUSPICIOUS ACTIVITY REPORT - NARRATIVE\n"
            f"SAR ID: {rng.randint(10000000, 99999999)}\n\n"
            f"SUBJECT: {{subject}}\n"
            f"SSN: {{ssn}} | DOB: {{dob}}\n"
            f"Address: {{address}} | Phone: {{phone}}\n"
            f"Account: {{acct}} | Routing: {{routing}}\n\n"
            f"NARRATIVE:\n"
            f"On {dates[0]}, {s_first} deposited {amounts[0]} in cash, followed by "
            f"a wire transfer of {amounts[1]} on {dates[1]} to {{org}} (account ending "
            f"{rng.randint(1000,9999)}). On {dates[2]}, an additional cash deposit of "
            f"{amounts[2]} was made, structured just under the $10,000 reporting threshold.\n\n"
            f"The pattern of transactions is consistent with structuring. {{subject}} has no "
            f"known business income to justify these cash deposits. The beneficiary {{org}} "
            f"was previously associated with a separate investigation.\n\n"
            f"Recommended action: escalate for further review."
        )

        slots = {"subject": subject, "ssn": ssn, "dob": dob, "address": address,
                 "acct": acct, "routing": routing, "org": org, "phone": phone}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="financial", document_type="sar_narrative",
                           difficulty="challenging",
                           regulatory_domains=["gdpr", "ccpa", "sox"])
        records.append(rec)
    return records


def generate_insurance_claims_financial(rng: random.Random, count: int) -> list[dict]:
    """Generate financial insurance claim narratives."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        claimant = factory.person_name()
        policy = factory.insurance_policy()
        phone = factory.phone()
        email = factory.email(claimant.value)
        address = factory.address()
        dob = factory.dob()
        ssn = factory.ssn()
        claim_no = f"CLM-{rng.randint(2024,2026)}-{rng.randint(100000,999999)}"

        template = (
            f"INSURANCE CLAIM\n"
            f"Claim #: {claim_no} | Policy: {{policy}}\n\n"
            f"Claimant: {{claimant}}\n"
            f"DOB: {{dob}} | SSN: {{ssn}}\n"
            f"Address: {{address}}\n"
            f"Phone: {{phone}} | Email: {{email}}\n\n"
            f"INCIDENT DESCRIPTION:\n"
            f"On {rng.randint(2024,2025)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}, "
            f"{{claimant}} reported {rng.choice(['a vehicle collision at the intersection of Main St and Oak Ave', 'water damage to the property', 'theft of personal belongings from the residence', 'a slip and fall incident at the covered premises'])}. "
            f"Estimated damages: ${rng.randint(1,50) * 1000:,}.\n\n"
            f"ADJUSTER NOTES:\n"
            f"Contacted {{claimant}} at {{phone}} to schedule inspection. "
            f"Documentation requested. Awaiting police report."
        )

        slots = {"claimant": claimant, "policy": policy, "phone": phone, "email": email,
                 "address": address, "dob": dob, "ssn": ssn}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="unstructured_text",
                           domain="financial", document_type="insurance_claim_financial",
                           difficulty="moderate",
                           regulatory_domains=["gdpr", "ccpa"])
        records.append(rec)
    return records


def generate_kyc_notes(rng: random.Random, count: int) -> list[dict]:
    """Generate KYC/onboarding notes with multi-document PII."""
    records = []
    for i in range(count):
        factory = PIIFactory(rng, "en")
        customer = factory.person_name()
        ssn = factory.ssn()
        dob = factory.dob()
        address = factory.address()
        phone = factory.phone()
        email = factory.email(customer.value)
        passport = factory.passport()
        dl = factory.driver_license()
        org = factory.org()
        job = factory.job_title()
        salary = factory.salary()
        acct = factory.bank_account()
        pin = _pin(factory)

        template = (
            f"KYC ONBOARDING NOTES\n"
            f"Date: {rng.randint(2024,2026)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}\n"
            f"New Account: {{acct}} | PIN: {{pin}}\n\n"
            f"CUSTOMER INFORMATION:\n"
            f"Name: {{customer}}\n"
            f"DOB: {{dob}} | SSN: {{ssn}}\n"
            f"Address: {{address}}\n"
            f"Phone: {{phone}} | Email: {{email}}\n\n"
            f"IDENTITY VERIFICATION:\n"
            f"Passport: {{passport}} - verified ✓\n"
            f"Driver's License: {{dl}} - verified ✓\n"
            f"Address proof: utility bill matches ✓\n\n"
            f"EMPLOYMENT & INCOME:\n"
            f"Employer: {{org}} | Title: {{job}} | Income: {{salary}}\n"
            f"Source of funds: employment income\n\n"
            f"RISK ASSESSMENT:\n"
            f"PEP screening: clear\n"
            f"Sanctions check: clear\n"
            f"Risk level: {rng.choice(['low', 'medium'])}\n\n"
            f"Approved by: {rng.choice(['Compliance Team', 'Senior Analyst'])}"
        )

        slots = {"customer": customer, "ssn": ssn, "dob": dob, "address": address,
                 "phone": phone, "email": email, "passport": passport, "dl": dl,
                 "org": org, "job": job, "salary": salary, "acct": acct, "pin": pin}

        rec = build_record(template, slots, language="en",
                           primary_dimension="diverse_pii_types", data_type="form",
                           domain="financial", document_type="kyc_notes",
                           difficulty="challenging",
                           regulatory_domains=["gdpr", "ccpa", "sox"])
        records.append(rec)
    return records


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: ADVANCED ADVERSARIAL PATTERN GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

# Homoglyph mapping: Latin → visually similar Cyrillic/Greek characters
HOMOGLYPH_MAP = {
    'a': 'а',  # Cyrillic а (U+0430)
    'c': 'с',  # Cyrillic с (U+0441)
    'e': 'е',  # Cyrillic е (U+0435)
    'o': 'о',  # Cyrillic о (U+043E)
    'p': 'р',  # Cyrillic р (U+0440)
    'x': 'х',  # Cyrillic х (U+0445)
    'y': 'у',  # Cyrillic у (U+0443)
    'A': 'А',  # Cyrillic А (U+0410)
    'B': 'В',  # Cyrillic В (U+0412)
    'C': 'С',  # Cyrillic С (U+0421)
    'E': 'Е',  # Cyrillic Е (U+0415)
    'H': 'Н',  # Cyrillic Н (U+041D)
    'K': 'К',  # Cyrillic К (U+041A)
    'M': 'М',  # Cyrillic М (U+041C)
    'O': 'О',  # Cyrillic О (U+041E)
    'P': 'Р',  # Cyrillic Р (U+0420)
    'T': 'Т',  # Cyrillic Т (U+0422)
    'X': 'Х',  # Cyrillic Х (U+0425)
}

# OCR confusion map: common OCR misread pairs
OCR_CONFUSION_MAP = {
    '0': 'O', 'O': '0', 'o': '0',
    '1': 'l', 'l': '1', 'I': '1',
    'rn': 'm', 'm': 'rn',
    'cl': 'd', 'd': 'cl',
    'vv': 'w', 'w': 'vv',
    '5': 'S', 'S': '5',
    '8': 'B', 'B': '8',
}

ZERO_WIDTH_CHARS = [
    '\u200b',  # Zero Width Space
    '\u200c',  # Zero Width Non-Joiner
    '\u200d',  # Zero Width Joiner
    '\ufeff',  # Zero Width No-Break Space (BOM)
]


def _apply_homoglyphs(rng: random.Random, text: str, rate: float = 0.3) -> str:
    """Replace some characters with visually identical homoglyphs."""
    result = list(text)
    for i, ch in enumerate(result):
        if ch in HOMOGLYPH_MAP and rng.random() < rate:
            result[i] = HOMOGLYPH_MAP[ch]
    return "".join(result)


def _insert_zero_width(rng: random.Random, text: str, count: int = 2) -> str:
    """Insert zero-width characters at random positions."""
    result = list(text)
    for _ in range(count):
        if len(result) > 2:
            pos = rng.randint(1, len(result) - 1)
            result.insert(pos, rng.choice(ZERO_WIDTH_CHARS))
    return "".join(result)


def _apply_ocr_errors(rng: random.Random, text: str, rate: float = 0.1) -> str:
    """Apply OCR-like character confusions."""
    result = text
    # Single-char substitutions
    for orig, repl in [('0', 'O'), ('1', 'l'), ('I', '1'), ('5', 'S'), ('8', 'B')]:
        if orig in result and rng.random() < rate:
            # Replace first occurrence only
            result = result.replace(orig, repl, 1)
    # Multi-char substitutions
    if 'rn' in result and rng.random() < rate:
        result = result.replace('rn', 'm', 1)
    return result


def generate_advanced_adversarial(rng: random.Random, count: int) -> list[dict]:
    """Generate advanced adversarial records across 13 attack categories."""
    records = []
    categories = [
        ("unicode_homoglyph", int(count * 0.125)),
        ("zero_width_char", int(count * 0.10)),
        ("bidi_attack", int(count * 0.0625)),
        ("base64_encoding", int(count * 0.075)),
        ("url_encoding", int(count * 0.0625)),
        ("ocr_artifact", int(count * 0.10)),
        ("negated_pii", int(count * 0.075)),
        ("context_ambiguous", int(count * 0.075)),
        ("partial_redaction_advanced", int(count * 0.0625)),
        ("code_embedded", int(count * 0.075)),
        ("url_embedded", int(count * 0.05)),
        ("mixed_script", int(count * 0.0625)),
        ("multi_token", int(count * 0.075)),
    ]

    for cat_type, cat_count in categories:
        for j in range(cat_count):
            factory = PIIFactory(rng, "en")
            name = factory.person_name()
            email = factory.email(name.value)
            phone = factory.phone()
            ssn = factory.ssn()

            if cat_type == "unicode_homoglyph":
                # Replace chars in PII with Cyrillic/Greek lookalikes
                adv_name = PIIValue("PERSON_NAME", _apply_homoglyphs(rng, name.value),
                                     "identity_demographics", "direct_identifier")
                adv_email = PIIValue("EMAIL_ADDRESS", _apply_homoglyphs(rng, email.value, 0.2),
                                      "contact", "direct_identifier")
                template = "Employee record: {adv_name} - Email: {adv_email} - Phone: {phone} - SSN: {ssn}"
                slots = {"adv_name": adv_name, "adv_email": adv_email, "phone": phone, "ssn": ssn}
                techniques = ["homoglyph_substitution", "cyrillic_lookalike"]

            elif cat_type == "zero_width_char":
                adv_name = PIIValue("PERSON_NAME", _insert_zero_width(rng, name.value),
                                     "identity_demographics", "direct_identifier")
                template = "Contact {adv_name} at {email} or {phone}. SSN: {ssn}."
                slots = {"adv_name": adv_name, "email": email, "phone": phone, "ssn": ssn}
                techniques = ["zero_width_insertion"]

            elif cat_type == "bidi_attack":
                # Insert RTL override before PII
                bidi_name = PIIValue("PERSON_NAME", f"\u202e{name.value}\u202c",
                                      "identity_demographics", "direct_identifier")
                template = "User profile: {bidi_name} | {email} | {phone}"
                slots = {"bidi_name": bidi_name, "email": email, "phone": phone}
                techniques = ["bidi_override", "rtl_injection"]

            elif cat_type == "base64_encoding":
                encoded = base64.b64encode(name.value.encode()).decode()
                b64_pii = PIIValue("PERSON_NAME", encoded, "identity_demographics", "direct_identifier")
                template = (f"The encoded patient identifier is {{b64_pii}} (base64). "
                           f"Contact: {{email}}. Decode before processing. SSN: {{ssn}}.")
                slots = {"b64_pii": b64_pii, "email": email, "ssn": ssn}
                techniques = ["base64_encoding"]

            elif cat_type == "url_encoding":
                encoded_email = urllib.parse.quote(email.value)
                url_email = PIIValue("EMAIL_ADDRESS", encoded_email, "contact", "direct_identifier")
                template = "API request: GET /api/user?email={url_email}&phone={phone}&name={name}"
                slots = {"url_email": url_email, "phone": phone, "name": name}
                techniques = ["url_percent_encoding"]

            elif cat_type == "ocr_artifact":
                ocr_name = PIIValue("PERSON_NAME", _apply_ocr_errors(rng, name.value, 0.3),
                                     "identity_demographics", "direct_identifier")
                ocr_ssn = PIIValue("SOCIAL_SECURITY_NUMBER", _apply_ocr_errors(rng, ssn.value, 0.2),
                                    "government_legal", "direct_identifier")
                template = "Scanned document: Patient {ocr_name}, SSN {ocr_ssn}, Phone {phone}, Email {email}"
                slots = {"ocr_name": ocr_name, "ocr_ssn": ocr_ssn, "phone": phone, "email": email}
                techniques = ["ocr_char_confusion", "scan_artifact"]

            elif cat_type == "negated_pii":
                templates_neg = [
                    "The account does NOT belong to {name}. The actual holder's email is {email}. SSN on file: {ssn}.",
                    "Correction: The patient is not {name}. Please update records. Contact: {phone}.",
                    "If {name} were to apply, their SSN {ssn} would be verified against {email}.",
                    "REDACTED: {name} was removed from the case. Previous phone: {phone}. Previous SSN: {ssn}.",
                ]
                template = rng.choice(templates_neg)
                slots = {"name": name, "email": email, "ssn": ssn, "phone": phone}
                techniques = ["negation", "hypothetical_context"]

            elif cat_type == "context_ambiguous":
                # Names that are also places/companies
                ambig_names = ["Jordan", "Austin", "Chase", "Dakota", "Madison",
                               "Virginia", "Georgia", "Carolina", "Florence", "Paris"]
                ambig_name = PIIValue("PERSON_NAME", rng.choice(ambig_names),
                                       "identity_demographics", "direct_identifier")
                templates_ambig = [
                    "{ambig_name} moved from {ambig_name} to work at {org}. Contact: {email}.",
                    "Customer {ambig_name} filed a complaint about the {ambig_name} branch. Phone: {phone}.",
                    "Dr. {ambig_name} practices in {ambig_name}. SSN: {ssn}. Email: {email}.",
                ]
                template = rng.choice(templates_ambig)
                org = factory.org()
                slots = {"ambig_name": ambig_name, "org": org, "email": email,
                         "phone": phone, "ssn": ssn}
                techniques = ["context_ambiguity", "name_location_collision"]

            elif cat_type == "partial_redaction_advanced":
                name_parts = name.value.split()
                if len(name_parts) >= 2:
                    redacted = f"{name_parts[0][0]}{'*' * (len(name_parts[0])-1)} {name_parts[-1][0]}{'*' * (len(name_parts[-1])-1)}"
                else:
                    redacted = f"{name.value[0]}{'*' * (len(name.value)-1)}"
                partial_name = PIIValue("PERSON_NAME", redacted, "identity_demographics", "direct_identifier")
                template = (f"Partially redacted record: {{partial_name}}, email {{email}}, "
                           f"graduated from {rng.choice(['Harvard Law', 'Stanford Medicine', 'MIT'])} "
                           f"in {rng.randint(1990, 2020)}. Phone: {{phone}}.")
                slots = {"partial_name": partial_name, "email": email, "phone": phone}
                techniques = ["partial_masking", "context_recoverable"]

            elif cat_type == "code_embedded":
                mrn = factory.mrn()
                ip = factory.ip_address()
                templates_code = [
                    'config = {{"patient_name": "{name}", "mrn": "{mrn}", "email": "{email}", "ip": "{ip}"}}',
                    'INSERT INTO patients (name, ssn, phone) VALUES (\'{name}\', \'{ssn}\', \'{phone}\');',
                    'logger.info(f"Processing request for {name} (IP: {ip}) - MRN: {mrn}")',
                ]
                template = rng.choice(templates_code)
                slots = {"name": name, "mrn": mrn, "email": email, "ip": ip,
                         "ssn": ssn, "phone": phone}
                techniques = ["code_embedding", "structured_context"]

            elif cat_type == "url_embedded":
                template = ("https://portal.example.com/profile?name={name}&email={email}"
                           "&ssn={ssn}&phone={phone}")
                slots = {"name": name, "email": email, "ssn": ssn, "phone": phone}
                techniques = ["url_parameter_embedding"]

            elif cat_type == "mixed_script":
                ja_factory = PIIFactory(rng, "ja")
                ja_name = ja_factory.person_name()
                template = "Please forward the report to {ja_name} at {email}. CC: {name} ({phone})."
                slots = {"ja_name": ja_name, "email": email, "name": name, "phone": phone}
                techniques = ["mixed_script", "cross_language"]

            elif cat_type == "multi_token":
                # Generate multi-token compound names
                compound_names = [
                    "María del Carmen García-López", "Jean-Pierre de la Fontaine",
                    "Mohammed bin Abdulaziz Al-Rashid", "Nguyễn Thị Minh Khai",
                    "Johann Sebastian von Hohenberg", "José María Álvarez del Manzano",
                    "Mary Catherine Elizabeth O'Brien-Williams",
                    "Abubakar Ibn Muhammad Al-Farabi",
                ]
                compound = PIIValue("PERSON_NAME", rng.choice(compound_names),
                                     "identity_demographics", "direct_identifier")
                template = "Patient {compound} ({email}) was seen today. Phone: {phone}. SSN: {ssn}."
                slots = {"compound": compound, "email": email, "phone": phone, "ssn": ssn}
                techniques = ["multi_token_entity", "compound_name"]

            else:
                continue

            rec = build_record(template, slots, language="en",
                               primary_dimension="edge_cases", domain="general",
                               difficulty="challenging",
                               adversarial_type=cat_type,
                               adversarial_difficulty="severe" if cat_type in ["unicode_homoglyph", "zero_width_char", "bidi_attack"] else "hard",
                               adversarial_techniques=techniques)
            records.append(rec)

    return records


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

GENERATORS_V120 = {
    # Healthcare (8 types)
    "progress_notes": (generate_progress_notes, 2000),
    "nursing_notes": (generate_nursing_notes, 1500),
    "radiology_reports": (generate_radiology_reports, 1200),
    "pathology_reports": (generate_pathology_reports, 1000),
    "clinical_transcripts": (generate_clinical_transcripts, 1200),
    "referral_letters": (generate_referral_letters, 1000),
    "prescriptions": (generate_prescriptions, 1000),
    "insurance_claims_clinical": (generate_insurance_claims_clinical, 1100),
    # Legal (5 types)
    "deposition_transcripts": (generate_deposition_transcripts, 1500),
    "witness_statements": (generate_witness_statements, 1250),
    "legal_memos": (generate_legal_memos, 1250),
    "court_opinions": (generate_court_opinions, 1250),
    "discovery_letters": (generate_discovery_letters, 1000),
    # Financial (7 types)
    "complaint_emails": (generate_complaint_emails, 1500),
    "support_chats": (generate_support_chats, 1500),
    "analyst_notes": (generate_analyst_notes, 1000),
    "loan_narratives": (generate_loan_narratives, 1250),
    "sar_narratives": (generate_sar_narratives, 1000),
    "insurance_claims_financial": (generate_insurance_claims_financial, 1000),
    "kyc_notes": (generate_kyc_notes, 1500),
    # Adversarial (13 categories)
    "adversarial": (generate_advanced_adversarial, 8000),
}

# Category groupings for --category flag
CATEGORY_GROUPS = {
    "healthcare": ["progress_notes", "nursing_notes", "radiology_reports", "pathology_reports",
                   "clinical_transcripts", "referral_letters", "prescriptions", "insurance_claims_clinical"],
    "legal": ["deposition_transcripts", "witness_statements", "legal_memos",
              "court_opinions", "discovery_letters"],
    "financial": ["complaint_emails", "support_chats", "analyst_notes", "loan_narratives",
                  "sar_narratives", "insurance_claims_financial", "kyc_notes"],
    "adversarial": ["adversarial"],
}


def main():
    parser = argparse.ArgumentParser(description="Generate v1.2.0 expansion records")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--category", type=str,
                        choices=list(CATEGORY_GROUPS.keys()) + list(GENERATORS_V120.keys()),
                        help="Generate only this category or group")
    parser.add_argument("--count", type=int, help="Override record count (per generator)")
    parser.add_argument("--all", action="store_true", help="Generate all categories")
    parser.add_argument("--seed", type=int, default=SEED + 120)  # Different seed from v1.1.0
    args = parser.parse_args()

    rng = random.Random(args.seed)

    if args.category:
        # Check if it's a group name
        if args.category in CATEGORY_GROUPS:
            gen_names = CATEGORY_GROUPS[args.category]
        else:
            gen_names = [args.category]

        records = []
        for gen_name in gen_names:
            gen_func, default_count = GENERATORS_V120[gen_name]
            count = args.count or default_count
            print(f"Generating {count} {gen_name} records...")
            batch = gen_func(rng, count)
            records.extend(batch)
            print(f"  Generated {len(batch)} records")

    elif args.all:
        records = []
        for gen_name, (gen_func, default_count) in GENERATORS_V120.items():
            count = args.count or default_count
            print(f"Generating {count} {gen_name} records...")
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
    doc_type_counts = Counter(r.get("document_type") for r in records)
    domain_counts = Counter(r["domain"] for r in records)
    dim_counts = Counter(r["primary_dimension"] for r in records)
    entity_types = Counter()
    adv_types = Counter()
    for r in records:
        for a in r["annotations"]:
            entity_types[a["entity_type"]] += 1
        if r["adversarial"]["type"]:
            adv_types[r["adversarial"]["type"]] += 1

    print(f"\nDocument type distribution:")
    for d, c in doc_type_counts.most_common():
        print(f"  {d}: {c}")
    print(f"\nDomain distribution:")
    for d, c in domain_counts.most_common():
        print(f"  {d}: {c}")
    print(f"\nDimension distribution:")
    for d, c in dim_counts.most_common():
        print(f"  {d}: {c}")
    print(f"\nEntity types: {len(entity_types)}")
    for t, c in entity_types.most_common(30):
        print(f"  {t}: {c}")
    if adv_types:
        print(f"\nAdversarial types:")
        for t, c in adv_types.most_common():
            print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
