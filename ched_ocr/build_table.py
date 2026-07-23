from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ched_ocr.parse_pos import parse_program_of_study
from ched_ocr.pdf_text import extract_pages_text

COLUMNS = [
    "program_code",
    "program_name",
    "cmo_year",
    "cmo_no",
    "cmo_reference",
    "cmo_ver",
    "year_level",
    "semester",
    "course_title",
    "lec_hours",
    "lab_hours",
    "units",
    "prerequisites",
    "extraction_method",
    "source_pdf",
]


def rows_for_cmo(
    *,
    ocr_text: str,
    program_code: str,
    program_name: str,
    cmo_year: int,
    cmo_no: str,
    cmo_reference: str,
    source_pdf: str,
    extraction_method: str = "ocr",
) -> list[dict[str, Any]]:
    cmo_ver = f"{cmo_year}-{cmo_no}"
    out: list[dict[str, Any]] = []
    for c in parse_program_of_study(ocr_text):
        out.append(
            {
                "program_code": program_code,
                "program_name": program_name,
                "cmo_year": cmo_year,
                "cmo_no": str(cmo_no),
                "cmo_reference": cmo_reference,
                "cmo_ver": cmo_ver,
                "year_level": c["year_level"],
                "semester": c["semester"],
                "course_title": c["course_title"],
                "lec_hours": c["lec_hours"],
                "lab_hours": c["lab_hours"],
                "units": c["units"],
                "prerequisites": c["prerequisites"],
                "extraction_method": extraction_method,
                "source_pdf": source_pdf,
            }
        )
    return out


def write_table(rows: list[dict[str, Any]], csv_path: Path, json_path: Path | None = None) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    if json_path:
        json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def build_bscpe_cmo87(
    pdf_path: str | Path = "downloads/2017/CMO-87-s.-2017-BS-Computer-Engineering.pdf",
    out_csv: str | Path = "data/course_program_cmo_ver.csv",
    out_json: str | Path = "data/course_program_cmo_ver.json",
    pages: list[int] | None = None,
) -> list[dict[str, Any]]:
    pages = pages or [11, 12, 13, 14, 15]
    text = extract_pages_text(pdf_path, page_numbers=pages, dpi_scale=2.0)
    rows = rows_for_cmo(
        ocr_text=text,
        program_code="BSCpE",
        program_name="Bachelor of Science in Computer Engineering",
        cmo_year=2017,
        cmo_no="87",
        cmo_reference="CMO No. 87, Series of 2017",
        source_pdf=str(pdf_path),
        extraction_method="ocr",
    )
    write_table(rows, Path(out_csv), Path(out_json))
    return rows
