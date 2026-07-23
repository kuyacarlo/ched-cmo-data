from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ched_ocr.canonical_bscpe_cmo87 import canonical_courses, validate_canonical
from ched_ocr.parse_pos import parse_program_of_study
from ched_ocr.pdf_text import extract_pages_text

COLUMNS = [
    "program_code",
    "program_name",
    "cmo_year",
    "cmo_no",
    "cmo_reference",
    "cmo_ver",
    "academic_year",
    "year_level",
    "semester",
    "course_code",
    "course_title",
    "lec_hours",
    "lab_hours",
    "units",
    "prerequisites",
    "classification",
    "competency_tags",
    "extraction_method",
    "source",
    "source_pdf",
    "verified",
    "inferred_fields",
    "cmo_grounded_fields",
    "review_notes",
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
    """Draft OCR path — all structural fields except titles/hours need review."""
    cmo_ver = f"{cmo_year}-{cmo_no}"
    out: list[dict[str, Any]] = []
    for i, c in enumerate(parse_program_of_study(ocr_text), start=1):
        out.append(
            {
                "program_code": program_code,
                "program_name": program_name,
                "cmo_year": cmo_year,
                "cmo_no": str(cmo_no),
                "cmo_reference": cmo_reference,
                "cmo_ver": cmo_ver,
                "academic_year": "",
                "year_level": c["year_level"],
                "semester": c["semester"],
                "course_code": f"AUTO{i:03d}",
                "course_title": c["course_title"],
                "lec_hours": c["lec_hours"],
                "lab_hours": c["lab_hours"],
                "units": c["units"],
                "prerequisites": c["prerequisites"],
                "classification": "program_specific",
                "competency_tags": ["curriculum"],
                "extraction_method": extraction_method,
                "source": "ched_cmo",
                "source_pdf": source_pdf,
                "verified": False,
                "inferred_fields": "course_code|classification|competency_tags|year_level|semester|lec_hours|lab_hours|units|prerequisites",
                "cmo_grounded_fields": "course_title|cmo_reference|cmo_ver",
                "review_notes": "OCR draft — do not seed SAGE until verified",
            }
        )
    return out


def _serialize(row: dict[str, Any]) -> dict[str, Any]:
    out = {k: row.get(k, "") for k in COLUMNS}
    tags = row.get("competency_tags") or []
    if isinstance(tags, list):
        out["competency_tags"] = "|".join(tags)
    out["verified"] = "true" if row.get("verified") else "false"
    return out


def write_table(rows: list[dict[str, Any]], csv_path: Path, json_path: Path | None = None) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(_serialize(r) for r in rows)
    if json_path:
        json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def to_sage_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """SAGE CMORecordCreate shape + provenance for human review."""
    out = []
    for r in rows:
        out.append(
            {
                "program_code": r["program_code"],
                "cmo_reference": r["cmo_reference"],
                "academic_year": r.get("academic_year") or None,
                "classification": r.get("classification"),
                "year_level": r["year_level"],
                "semester": r["semester"],
                "course_code": r["course_code"],
                "course_title": r["course_title"],
                "competency_tags": list(r["competency_tags"]),
                "source": r.get("source", "ched_cmo"),
                "_provenance": {
                    "verified": bool(r.get("verified")),
                    "inferred_fields": (r.get("inferred_fields") or "").split("|"),
                    "cmo_grounded_fields": (r.get("cmo_grounded_fields") or "").split("|"),
                    "review_notes": r.get("review_notes"),
                    "cmo_ver": r.get("cmo_ver"),
                    "extraction_method": r.get("extraction_method"),
                },
            }
        )
    return out


def build_bscpe_cmo87(
    pdf_path: str | Path = "downloads/2017/CMO-87-s.-2017-BS-Computer-Engineering.pdf",
    out_csv: str | Path = "data/course_program_cmo_ver.csv",
    out_json: str | Path = "data/course_program_cmo_ver.json",
    sage_json: str | Path = "data/course_program_cmo_ver.sage.json",
    pages: list[int] | None = None,
    use_canonical: bool = True,
) -> list[dict[str, Any]]:
    if use_canonical:
        rows = canonical_courses()
    else:
        pages = pages or [11, 12, 13, 14, 15]
        text = extract_pages_text(pdf_path, page_numbers=pages, dpi_scale=2.0)
        rows = rows_for_cmo(
            ocr_text=text,
            program_code="BSCPE",
            program_name="Bachelor of Science in Computer Engineering",
            cmo_year=2017,
            cmo_no="87",
            cmo_reference="CMO No. 87, Series of 2017",
            source_pdf=str(pdf_path),
            extraction_method="ocr",
        )
    write_table(rows, Path(out_csv), Path(out_json))
    Path(sage_json).write_text(json.dumps(to_sage_records(rows), indent=2), encoding="utf-8")
    return rows
