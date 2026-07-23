#!/usr/bin/env python3
"""Build data/course_program_cmo_ver.* via OCR of sample Program of Study pages."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ched_ocr.build_table import build_bscpe_cmo87


def main() -> None:
    rows = build_bscpe_cmo87()
    print(json.dumps({"rows": len(rows), "sample": rows[:3]}, indent=2))


if __name__ == "__main__":
    main()
