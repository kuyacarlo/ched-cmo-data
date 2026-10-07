#!/usr/bin/env python3
"""Validate the checked-in public CHED CMO catalog without live network access."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def main() -> None:
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    csv_rows = list(csv.DictReader((DATA / "cmo_index.csv").open(encoding="utf-8")))
    jsonl_rows = [json.loads(line) for line in (DATA / "cmo_index.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

    assert manifest["row_count"] == len(csv_rows), "manifest row_count does not match CSV"
    assert manifest["row_count"] == len(jsonl_rows), "manifest row_count does not match JSONL"
    assert {"year", "cmo_no", "cmo_reference", "title", "category", "url"}.issubset(csv_rows[0]), "CSV schema missing required columns"
    assert all(row.get("url", "").startswith("http") for row in csv_rows if row.get("url")), "catalog contains non-URL source pointers"

    print(json.dumps({"rows": len(csv_rows), "year_min": manifest["year_min"], "year_max": manifest["year_max"]}, indent=2))


if __name__ == "__main__":
    main()
