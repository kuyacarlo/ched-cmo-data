"""Production-curated BSCpE sample Program of Study from CMO No. 87, s. 2017.

CHED does not mandate institutional course codes; codes here are stable
Ghost-Commons / SAGE identifiers derived from the CMO titles.
Source of truth for sequencing/units: CMO 87 sample semestral PoS (Annex).
"""
from __future__ import annotations

from typing import Any

CMO_META = {
    "program_code": "BSCPE",
    "program_name": "Bachelor of Science in Computer Engineering",
    "cmo_year": 2017,
    "cmo_no": "87",
    "cmo_reference": "CMO No. 87, Series of 2017",
    "cmo_ver": "2017-87",
    "academic_year": "AY 2018-2019",
    "source_pdf": "downloads/2017/CMO-87-s.-2017-BS-Computer-Engineering.pdf",
    "extraction_method": "canonical",
    "source": "ched_cmo",
    # Provenance: what came from CMO sample PoS vs human/AI inference
    "verified": False,
    "inferred_fields": "course_code|classification|competency_tags",
    "cmo_grounded_fields": "year_level|semester|course_title|lec_hours|lab_hours|units|prerequisites|cmo_reference|cmo_ver",
    "review_notes": "course_code/classification/competency_tags are NOT in CMO 87; double-check before SAGE prod seed",
}

# (year, sem, code, title, lec, lab, units, prereq, classification, tags)
_RAW: list[tuple] = [
    # YEAR 1 SEM 1
    (1, 1, "MATH101", "Calculus 1", 3, 0, 3, "", "shared_major", ["calculus", "limits", "differentiation"]),
    (1, 1, "CHEM101", "Chemistry for Engineers", 3, 3, 4, "", "shared_major", ["chemistry", "engineering science"]),
    (1, 1, "CPE100", "Computer Engineering as a Discipline", 1, 0, 1, "", "program_specific", ["computer engineering", "profession"]),
    (1, 1, "CPE101", "Programming Logic and Design", 0, 6, 2, "", "program_specific", ["programming", "logic", "algorithms"]),
    (1, 1, "GEC101", "Mathematics in the Modern World", 3, 0, 3, "", "core_gened", ["mathematics", "modern world"]),
    (1, 1, "GEC102", "Science, Technology, and Society", 3, 0, 3, "", "core_gened", ["science", "technology", "society"]),
    (1, 1, "GEC103", "Understanding the Self", 3, 0, 3, "", "core_gened", ["psychology", "self"]),
    (1, 1, "PE101", "Physical Education 1", 2, 0, 2, "", "core_gened", ["physical education"]),
    (1, 1, "NSTP101", "National Service Training Program 1", 3, 0, 3, "", "core_gened", ["nstp", "national service"]),
    # YEAR 1 SEM 2
    (1, 2, "MATH102", "Calculus 2", 3, 0, 3, "Calculus 1", "shared_major", ["calculus", "integration"]),
    (1, 2, "PHYS101", "Physics for Engineers", 3, 3, 4, "Calculus 1", "shared_major", ["physics", "mechanics"]),
    (1, 2, "CPE102", "Object Oriented Programming", 0, 6, 2, "Programming Logic and Design", "program_specific", ["oop", "programming"]),
    (1, 2, "MATH103", "Engineering Data Analysis", 3, 0, 3, "Calculus 1", "shared_major", ["statistics", "data analysis"]),
    (1, 2, "MATH104", "Discrete Mathematics", 3, 0, 3, "Calculus 1", "shared_major", ["discrete math", "logic"]),
    (1, 2, "GEC104", "Readings in Philippine History", 3, 0, 3, "", "core_gened", ["philippine history"]),
    (1, 2, "PE102", "Physical Education 2", 2, 0, 2, "Physical Education 1", "core_gened", ["physical education"]),
    (1, 2, "NSTP102", "National Service Training Program 2", 3, 0, 3, "National Service Training Program 1", "core_gened", ["nstp", "national service"]),
    # YEAR 2 SEM 1
    (2, 1, "MATH201", "Differential Equations", 3, 0, 3, "Calculus 2", "shared_major", ["differential equations", "modeling"]),
    (2, 1, "GEC201", "Art Appreciation", 3, 0, 3, "", "core_gened", ["art", "appreciation"]),
    (2, 1, "CPE201", "Data Structures and Algorithms", 0, 6, 2, "Object Oriented Programming", "program_specific", ["data structures", "algorithms"]),
    (2, 1, "ENGR201", "Engineering Economics", 3, 0, 3, "2nd Year Standing", "shared_major", ["economics", "engineering management"]),
    (2, 1, "CPE202", "Fundamentals of Electrical Circuits", 3, 3, 4, "Physics for Engineers", "program_specific", ["circuits", "electrical"]),
    (2, 1, "GEC202", "GEC Elective 1", 3, 0, 3, "", "elective", ["general education", "elective"]),
    (2, 1, "ENGR202", "Computer-Aided Drafting", 0, 3, 1, "2nd Year Standing", "shared_major", ["cad", "drafting"]),
    (2, 1, "PE201", "Physical Education 3", 2, 0, 2, "Physical Education 2", "core_gened", ["physical education"]),
    # YEAR 2 SEM 2
    (2, 2, "MATH202", "Numerical Methods", 3, 0, 3, "Differential Equations", "shared_major", ["numerical methods", "algorithms"]),
    (2, 2, "CPE203", "Software Design", 3, 3, 4, "Data Structures and Algorithms", "program_specific", ["software design", "engineering"]),
    (2, 2, "GEC203", "Purposive Communication", 3, 0, 3, "", "core_gened", ["communication", "writing"]),
    (2, 2, "CPE204", "Fundamentals of Electronic Circuits", 3, 3, 4, "Fundamentals of Electrical Circuits", "program_specific", ["electronics", "circuits"]),
    (2, 2, "GEC204", "Life and Works of Rizal", 3, 0, 3, "", "core_gened", ["rizal", "philippine history"]),
    (2, 2, "PE202", "Physical Education 4", 2, 0, 2, "Physical Education 3", "core_gened", ["physical education"]),
    (2, 2, "GEC205", "The Contemporary World", 3, 0, 3, "", "core_gened", ["globalization", "society"]),
    # YEAR 3 SEM 1
    (3, 1, "CPE301", "Logic Circuits and Design", 3, 3, 4, "Fundamentals of Electronic Circuits", "program_specific", ["digital logic", "hdl"]),
    (3, 1, "CPE302", "Operating Systems", 3, 0, 3, "Data Structures and Algorithms", "program_specific", ["operating systems"]),
    (3, 1, "CPE303", "Data and Digital Communications", 3, 0, 3, "Fundamentals of Electronic Circuits", "program_specific", ["communications", "signals"]),
    (3, 1, "CPE304", "Introduction to HDL", 0, 3, 1, "Programming Logic and Design; Fundamentals of Electronic Circuits", "program_specific", ["hdl", "verilog", "vhdl"]),
    (3, 1, "CPE305", "Feedback and Control Systems", 3, 0, 3, "Numerical Methods; Fundamentals of Electrical Circuits", "program_specific", ["control systems"]),
    (3, 1, "CPE306", "Fundamentals of Mixed Signals and Sensors", 3, 0, 3, "Fundamentals of Electronic Circuits", "program_specific", ["sensors", "mixed signal"]),
    (3, 1, "CPE307", "Computer Engineering Drafting and Design", 0, 3, 1, "Fundamentals of Electronic Circuits", "program_specific", ["drafting", "design"]),
    (3, 1, "CPE308", "Cognate / Elective Course 1", 3, 0, 3, "3rd Year Standing", "elective", ["cognate", "elective"]),
    # YEAR 3 SEM 2
    (3, 2, "CPE309", "Basic Occupational Health and Safety", 3, 0, 3, "3rd Year Standing", "program_specific", ["safety", "occupational health"]),
    (3, 2, "CPE310", "Computer Networks and Security", 3, 3, 4, "Data and Digital Communications", "program_specific", ["networks", "security"]),
    (3, 2, "CPE311", "Microprocessors", 3, 3, 4, "Logic Circuits and Design", "program_specific", ["microprocessors", "architecture"]),
    (3, 2, "CPE312", "Methods of Research", 2, 0, 2, "Engineering Data Analysis; Purposive Communication; Logic Circuits and Design", "program_specific", ["research", "methods"]),
    (3, 2, "CPE313", "Technopreneurship", 3, 0, 3, "3rd Year Standing", "program_specific", ["technopreneurship", "startup"]),
    (3, 2, "GEC301", "Ethics", 3, 0, 3, "", "core_gened", ["ethics", "values"]),
    (3, 2, "CPE314", "CpE Laws and Professional Practice", 2, 0, 2, "3rd Year Standing", "program_specific", ["professional practice", "laws"]),
    (3, 2, "CPE315", "Cognate / Elective Course 2", 3, 0, 3, "Cognate / Elective Course 1", "elective", ["cognate", "elective"]),
    # YEAR 4 SEM 1
    (4, 1, "CPE401", "Embedded Systems", 3, 3, 4, "Microprocessors", "program_specific", ["embedded systems"]),
    (4, 1, "CPE402", "Computer Architecture and Organization", 3, 3, 4, "Microprocessors", "program_specific", ["computer architecture"]),
    (4, 1, "CPE403", "Emerging Technologies in CpE", 3, 0, 3, "4th Year Standing", "program_specific", ["emerging technologies"]),
    (4, 1, "CPE404", "CpE Practice and Design 1", 0, 3, 1, "Microprocessors; Methods of Research", "program_specific", ["design project", "capstone"]),
    (4, 1, "CPE405", "Digital Signal Processing", 3, 3, 4, "Feedback and Control Systems", "program_specific", ["dsp", "signals"]),
    (4, 1, "GEC401", "GEC Elective 2", 3, 0, 3, "", "elective", ["general education", "elective"]),
    (4, 1, "CPE406", "Cognate / Elective Course 3", 3, 0, 3, "Cognate / Elective Course 2", "elective", ["cognate", "elective"]),
    # YEAR 4 SEM 2
    (4, 2, "CPE407", "CpE Practice and Design 2", 0, 6, 2, "CpE Practice and Design 1", "program_specific", ["design project", "capstone"]),
    (4, 2, "CPE408", "Seminars and Fieldtrips", 0, 3, 1, "4th Year Standing", "program_specific", ["seminars", "fieldtrips"]),
    (4, 2, "CPE409", "On the Job Training", 0, 240, 3, "4th Year Standing", "program_specific", ["ojt", "internship"]),
    (4, 2, "GEC402", "GEC Elective 3", 3, 0, 3, "", "elective", ["general education", "elective"]),
]


def canonical_courses() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for year, sem, code, title, lec, lab, units, prereq, classification, tags in _RAW:
        assert 1 <= len(tags) <= 4, title
        rows.append(
            {
                **CMO_META,
                "year_level": year,
                "semester": sem,
                "course_code": code,
                "course_title": title,
                "lec_hours": lec,
                "lab_hours": lab,
                "units": units,
                "prerequisites": prereq,
                "classification": classification,
                "competency_tags": list(tags),
            }
        )
    return rows


def validate_canonical(rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    rows = rows or canonical_courses()
    total_units = sum(r["units"] for r in rows)
    years = {r["year_level"] for r in rows}
    codes = [r["course_code"] for r in rows]
    return {
        "row_count": len(rows),
        "total_units": total_units,
        "years": sorted(years),
        "unique_codes": len(set(codes)) == len(codes),
        "min_units_ok": total_units >= 166,
    }
