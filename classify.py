"""CMO category classifier shared by scraper + public export."""
from __future__ import annotations

import re


def extract_cmo_no(cmo_ref: str) -> str:
    match = re.search(r"\b(?:No|NO)\.?\s*(\d+)", cmo_ref, re.IGNORECASE)
    if match:
        return str(int(match.group(1)))
    match2 = re.search(r"\b(\d+)\b", cmo_ref)
    if match2:
        return str(int(match2.group(1)))
    return ""


def classify_category(title: str, cmo_ref: str) -> str:
    title_upper = title.upper()
    ref_upper = cmo_ref.upper()
    combined = f"{title_upper} {ref_upper}"

    procedural = any(
        k in title_upper
        for k in [
            "CONSULTATIVE CONFERENCE",
            "PUBLIC HEARING",
            "NATIONAL CONSULTATIVE",
            "CALL FOR COMMENTS",
        ]
    )

    curriculum_kw = [
        "POLICIES, STANDARDS AND GUIDELINES",
        "POLICIES, STANDARDS, AND GUIDELINES",
        "POLICIES AND STANDARDS FOR",
        "UPDATED POLICIES AND STANDARDS",
        "REVISED POLICIES AND STANDARDS",
        "REVISED MINIMUM CURRICULUM",
        "MINIMUM CURRICULUM REQUIREMENT",
        "MINIMUM STANDARDS FOR",
        "PSG FOR",
        "BACHELOR OF",
        "BACHELOR IN",
        "DOCTOR OF",
        "MASTER OF",
        "MASTER IN",
        "DEGREE PROGRAM",
        "UNDERGRADUATE PROGRAM",
        "GRADUATE PROGRAM",
        "CURRICULA FOR",
        "CURRICULUM REQUIREMENT",
        "FOR MIDWIFERY EDUCATION",
        "FOR NURSING EDUCATION",
        "FOR MEDICAL EDUCATION",
        "FOR ENGINEERING EDUCATION",
        "INFORMATION TECHNOLOGY EDUCATION",
        "RADIOLOGIC TECHNOLOGY EDUCATION",
        "INTEGRATION OF PEACE STUDIES",
        "INDIGENOUS PEOPLES STUDIES",
        "VETERINARY MEDICINE",
        "SYLLABI FOR",
    ]

    if not procedural and (
        any(k in combined for k in curriculum_kw)
        or re.search(r"\b(?:BS|BA|MS|MA|PHD|MD|DMD|DVM|PSG)\b", combined)
    ):
        if not any(k in title_upper for k in ["COMMON TO ALL", "ADMISSION OF"]):
            return "curriculum_program"

    if any(
        k in combined
        for k in [
            "HIGHER EDUCATION INSTITUTION",
            "HEI",
            "STATE UNIVERSITIES AND COLLEGES",
            "SUC",
            "LOCAL COLLEGES AND UNIVERSITIES",
            "LCU",
            "AUTONOMOUS AND DEREGULATED",
            "PRIVATE HIGHER EDUCATION",
            "COES CODS",
            "CENTERS OF EXCELLENCE",
            "CENTERS OF DEVELOPMENT",
            "INSTITUTIONAL DEVELOPMENT",
            "LEVELLING RESULTS",
            "UNIVERSITY LEVEL",
        ]
    ):
        return "curriculum_college"

    if any(
        k in combined
        for k in [
            "SCHOLARSHIP",
            "STUDENT INTERNSHIP",
            "DRUG TESTING",
            "ADMISSION OF",
            "GRANTS-IN-AID",
            "STUFAPS",
            "TUITION",
            "ASSISTANCE TO STUDENTS",
            "STUDENTS'",
            "FINANCIAL ASSISTANCE",
            "BAYANIHAN",
            "SIKAP",
        ]
    ):
        return "scholarship_student_services"

    if any(
        k in combined
        for k in [
            "FACULTY TRAINING",
            "CONTINUING PROFESSIONAL EDUCATION",
            "CPE GRANTS",
            "SCHOLARSHIPS FOR GRADUATE STUDIES",
            "IRSE GRANTS",
            "TEACHING PERSONNEL",
            "NON-TEACHING PERSONNEL",
            "RESEARCH CHAIR",
            "TRAINING OF TRAINORS",
            "TRAINING OF GE",
        ]
    ):
        return "faculty_development"

    if any(k in combined for k in ["RECOGNIZED JOURNALS", "CHED JIP", "JOURNAL RECOGNITION"]):
        return "research_journals"

    return "administrative_governance"
