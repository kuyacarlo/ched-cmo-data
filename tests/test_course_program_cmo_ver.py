"""Production course_program_cmo_ver (SAGE-ready) tests."""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "bscpe_cmo87_pos_ocr.txt"
PDF = Path("downloads/2017/CMO-87-s.-2017-BS-Computer-Engineering.pdf")


def test_canonical_bscpe_is_production_ready():
    from ched_ocr.canonical_bscpe_cmo87 import canonical_courses, validate_canonical

    rows = canonical_courses()
    stats = validate_canonical(rows)
    assert stats["row_count"] >= 55
    assert stats["years"] == [1, 2, 3, 4]
    assert stats["unique_codes"] is True
    assert stats["total_units"] >= 166
    assert stats["min_units_ok"] is True

    # SAGE-required fields
    for r in rows:
        assert r["program_code"] == "BSCPE"
        assert r["course_code"]
        assert r["course_title"]
        assert 1 <= r["year_level"] <= 4
        assert 1 <= r["semester"] <= 2
        assert 1 <= len(r["competency_tags"]) <= 4
        assert r["classification"] in {
            "core_gened",
            "shared_major",
            "program_specific",
            "elective",
        }
        assert r["units"] >= 1
        assert r["verified"] is False
        assert "competency_tags" in r["inferred_fields"]
        assert "course_code" in r["inferred_fields"]


def test_canonical_includes_calculus_1_y1s1():
    from ched_ocr.canonical_bscpe_cmo87 import canonical_courses

    rows = canonical_courses()
    calc = next(r for r in rows if r["course_title"] == "Calculus 1")
    assert calc["year_level"] == 1 and calc["semester"] == 1
    assert calc["units"] == 3
    assert calc["course_code"] == "MATH101"


def test_build_writes_sage_shaped_export(tmp_path):
    from ched_ocr.build_table import build_bscpe_cmo87, to_sage_records
    from ched_ocr.canonical_bscpe_cmo87 import canonical_courses

    out_csv = tmp_path / "course_program_cmo_ver.csv"
    out_json = tmp_path / "course_program_cmo_ver.json"
    sage_json = tmp_path / "course_program_cmo_ver.sage.json"
    rows = build_bscpe_cmo87(out_csv=out_csv, out_json=out_json, sage_json=sage_json)
    assert out_csv.exists() and sage_json.exists()
    sage = to_sage_records(rows)
    assert sage[0]["course_code"]
    assert isinstance(sage[0]["competency_tags"], list)
    assert len(rows) == len(canonical_courses())


def test_parse_pos_still_extracts_calculus_from_fixture():
    """OCR path remains available for other CMOs (draft quality)."""
    from ched_ocr.parse_pos import parse_program_of_study

    courses = parse_program_of_study(FIXTURE.read_text(encoding="utf-8"))
    titles = {c["course_title"].lower() for c in courses}
    assert any("calculus 1" in t for t in titles)


@pytest.mark.integration
def test_ocr_pdf_pages_nonempty_when_pdf_present():
    if not PDF.exists():
        pytest.skip("CompE PDF not downloaded")
    from ched_ocr.pdf_text import extract_pages_text

    text = extract_pages_text(PDF, page_numbers=[11, 12], dpi_scale=1.5)
    assert "FIRST YEAR" in text or "Calculus" in text
