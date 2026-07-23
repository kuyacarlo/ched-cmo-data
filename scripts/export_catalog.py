#!/usr/bin/env python3
"""Build cleaned public catalog from pipeline out.csv."""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from classify import classify_category, extract_cmo_no  # noqa: E402

SRC = ROOT / "out.csv"
OUT_CSV = ROOT / "data" / "cmo_index.csv"
OUT_JSONL = ROOT / "data" / "cmo_index.jsonl"
OUT_META = ROOT / "data" / "manifest.json"
SAMPLE_CSV = ROOT / "data" / "sample" / "cmo_index.sample.csv"

FIELDS = [
    "year", "cmo_no", "cmo_reference", "title", "category", "url",
    "file_size_bytes", "page_count", "is_ocr_needed", "is_corrupted", "status",
]


def coerce_bool(v):
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"1", "true", "yes", "y"}


def coerce_int(v):
    if v is None or v == "":
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Missing {SRC}; run pipeline first")

    raw = list(csv.DictReader(SRC.open(encoding="utf-8")))
    cleaned = []
    changed = 0
    for r in raw:
        title = (r.get("title") or "").strip()
        ref = (r.get("cmo_reference") or "").strip()
        new_cat = classify_category(title, ref)
        if new_cat != (r.get("category") or "").strip():
            changed += 1
        cmo_no = (r.get("cmo_no") or "").strip() or extract_cmo_no(ref)
        cleaned.append({
            "year": coerce_int(r.get("year")),
            "cmo_no": cmo_no,
            "cmo_reference": ref,
            "title": title,
            "category": new_cat,
            "url": (r.get("url") or "").strip(),
            "file_size_bytes": coerce_int(r.get("file_size_bytes")),
            "page_count": coerce_int(r.get("page_count")),
            "is_ocr_needed": coerce_bool(r.get("is_ocr_needed")),
            "is_corrupted": coerce_bool(r.get("is_corrupted")),
            "status": (r.get("status") or "").strip() or None,
        })

    cleaned.sort(key=lambda x: (x["year"] or 0, int(x["cmo_no"]) if str(x["cmo_no"]).isdigit() else 0, x["title"]))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    SAMPLE_CSV.parent.mkdir(parents=True, exist_ok=True)

    def csv_row(row):
        out = {k: ("" if row[k] is None else row[k]) for k in FIELDS}
        for b in ("is_ocr_needed", "is_corrupted"):
            out[b] = "" if row[b] is None else ("true" if row[b] else "false")
        return out

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(csv_row(r) for r in cleaned)

    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for row in cleaned:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    sample = []
    by_cat = {}
    for row in cleaned:
        by_cat.setdefault(row["category"], []).append(row)
    for rows in by_cat.values():
        pool = [r for r in rows if r["is_ocr_needed"] is False] or rows
        sample.extend(pool[:2])
    sample = sample[:12]

    with SAMPLE_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(csv_row(r) for r in sample)

    ph_src = ROOT / "pharmacy_curriculum.csv"
    if ph_src.exists():
        (ROOT / "data" / "sample" / "pharmacy_curriculum.sample.csv").write_text(
            ph_src.read_text(encoding="utf-8"), encoding="utf-8"
        )
    phj = ROOT / "pharmacy_curriculum.json"
    if phj.exists():
        (ROOT / "data" / "sample" / "pharmacy_curriculum.sample.json").write_text(
            phj.read_text(encoding="utf-8"), encoding="utf-8"
        )

    cats = Counter(r["category"] for r in cleaned)
    years = [r["year"] for r in cleaned if r["year"] is not None]
    manifest = {
        "name": "ched-cmo-index",
        "title": "CHED Memorandum Orders (CMO) Index",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "https://legacy.ched.gov.ph/",
        "source_pattern": "https://legacy.ched.gov.ph/{year}-ched-memorandum-orders/",
        "row_count": len(cleaned),
        "year_min": min(years) if years else None,
        "year_max": max(years) if years else None,
        "categories": dict(cats),
        "category_changes_from_raw": changed,
        "downloaded": sum(1 for r in cleaned if r["status"] == "downloaded"),
        "needs_ocr": sum(1 for r in cleaned if r["is_ocr_needed"] is True),
        "searchable": sum(1 for r in cleaned if r["is_ocr_needed"] is False),
        "files": {
            "csv": "data/cmo_index.csv",
            "jsonl": "data/cmo_index.jsonl",
            "sample_csv": "data/sample/cmo_index.sample.csv",
        },
        "notes": [
            "Derived metadata index. PDF contents remain with CHED; urls point to legacy.ched.gov.ph.",
            "Program course tables are not included yet (except pharmacy sample).",
        ],
    }
    OUT_META.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(cleaned), "category_changes": changed, "categories": dict(cats)}, indent=2))


if __name__ == "__main__":
    main()
