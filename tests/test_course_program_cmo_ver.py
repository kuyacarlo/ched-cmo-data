"""TDD: OCR + parse SAMPLE PROGRAM OF STUDY → course_program_cmo_ver rows."""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "bscpe_cmo87_pos_ocr.txt"
PDF = Path("downloads/2017/CMO-87-s.-2017-BS-Computer-Engineering.pdf")


def test_parse_pos_extracts_first_year_calculus():
    from ched_ocr.parse_pos import parse_program_of_study

    text = FIXTURE.read_text(encoding="utf-8")
    courses = parse_program_of_study(text)
    titles = {c["course_title"].lower() for c in courses}
    assert any("calculus 1" in t for t in titles), titles
    calc = next(c for c in courses if "calculus 1" in c["course_title"].lower())
    assert calc["year_level"] == 1
    assert calc["semester"] == 1
    assert calc["units"] == 3


def test_parse_pos_has_multiple_years_and_required_columns():
    from ched_ocr.parse_pos import parse_program_of_study

    courses = parse_program_of_study(FIXTURE.read_text(encoding="utf-8"))
    required = {
        "year_level",
        "semester",
        "course_title",
        "lec_hours",
        "lab_hours",
        "units",
        "prerequisites",
    }
    assert len(courses) >= 20
    years = {c["year_level"] for c in courses}
    assert {1, 2, 3, 4}.issubset(years)
    for c in courses:
        assert required <= set(c.keys())
        assert isinstance(c["course_title"], str) and len(c["course_title"]) > 2


def test_build_course_program_cmo_ver_rows_include_cmo_identity():
    from ched_ocr.build_table import rows_for_cmo

    rows = rows_for_cmo(
        ocr_text=FIXTURE.read_text(encoding="utf-8"),
        program_code="BSCpE",
        program_name="Bachelor of Science in Computer Engineering",
        cmo_year=2017,
        cmo_no="87",
        cmo_reference="CMO No. 87, Series of 2017",
        source_pdf="downloads/2017/CMO-87-s.-2017-BS-Computer-Engineering.pdf",
        extraction_method="ocr",
    )
    assert rows
    assert all(r["cmo_ver"] == "2017-87" for r in rows)
    assert all(r["program_code"] == "BSCpE" for r in rows)


@pytest.mark.integration
def test_ocr_pdf_pages_nonempty_when_pdf_present():
    if not PDF.exists():
        pytest.skip("CompE PDF not downloaded")
    from ched_ocr.pdf_text import extract_pages_text

    text = extract_pages_text(PDF, page_numbers=[11, 12], dpi_scale=1.5)
    assert "Calculus" in text or "calculus" in text.lower() or "FIRST YEAR" in text
