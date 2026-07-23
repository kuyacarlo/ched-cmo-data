#!/usr/bin/env python3
"""
E2E CHED → course table → SAGE-shaped export (MVP).

Stages:
  1. index      — scrape legacy CHED year pages → out.csv / data/cmo_index.*
  2. download   — fetch missing PDFs
  3. scan       — page counts / OCR flags
  4. courses    — build course_program_cmo_ver (canonical BSCPE for now)
  5. validate   — production checks + provenance warnings
  6. export     — already written by courses stage

Usage:
  uv run python scripts/e2e_pipeline.py              # courses+validate only (default, safe)
  uv run python scripts/e2e_pipeline.py --full        # also index/download/scan (slow, network)
  uv run python scripts/e2e_pipeline.py --stage courses
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def stage_index() -> None:
    run([sys.executable, "01.py"])
    run([sys.executable, "scripts/export_catalog.py"])


def stage_download() -> None:
    run([sys.executable, "02.py"])


def stage_scan() -> None:
    run([sys.executable, "scan_downloads.py"])


def stage_courses() -> None:
    run([sys.executable, "scripts/build_course_program_cmo_ver.py"])


def stage_validate() -> dict:
    from ched_ocr.canonical_bscpe_cmo87 import canonical_courses, validate_canonical

    rows = canonical_courses()
    stats = validate_canonical(rows)
    inferred = sorted(
        {
            f
            for r in rows
            for f in (r.get("inferred_fields") or "").split("|")
            if f
        }
    )
    unverified = sum(1 for r in rows if not r.get("verified"))
    report = {
        **stats,
        "unverified_rows": unverified,
        "inferred_field_types": inferred,
        "warnings": [],
    }
    if unverified:
        report["warnings"].append(
            f"{unverified}/{len(rows)} rows verified=false — review competency_tags/course_code/classification before SAGE prod seed"
        )
    if "competency_tags" in inferred:
        report["warnings"].append("competency_tags are inferred — double-check")
    if "course_code" in inferred:
        report["warnings"].append("course_code are inferred stable IDs — not from CHED")
    out = ROOT / "data" / "e2e_validate_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not stats["min_units_ok"] or not stats["unique_codes"]:
        raise SystemExit("validation failed hard checks")
    return report


STAGES = {
    "index": stage_index,
    "download": stage_download,
    "scan": stage_scan,
    "courses": stage_courses,
    "validate": stage_validate,
}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--full", action="store_true", help="Run index→download→scan→courses→validate")
    p.add_argument(
        "--stage",
        choices=list(STAGES),
        action="append",
        help="Run specific stage(s); default courses+validate",
    )
    args = p.parse_args()

    if args.full:
        order = ["index", "download", "scan", "courses", "validate"]
    elif args.stage:
        order = args.stage
    else:
        order = ["courses", "validate"]

    for name in order:
        print(f"\n=== stage: {name} ===", flush=True)
        STAGES[name]()
    print("\nE2E done.")


if __name__ == "__main__":
    main()
