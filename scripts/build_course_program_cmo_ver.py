#!/usr/bin/env python3
"""Build production course_program_cmo_ver (+ SAGE-shaped export)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ched_ocr.build_table import build_bscpe_cmo87
from ched_ocr.canonical_bscpe_cmo87 import validate_canonical


def main() -> None:
    rows = build_bscpe_cmo87(use_canonical=True)
    stats = validate_canonical(rows)
    print(json.dumps({"stats": stats, "sample": rows[:2]}, indent=2))
    if not stats["min_units_ok"] or not stats["unique_codes"]:
        raise SystemExit("canonical curriculum failed production checks")


if __name__ == "__main__":
    main()
