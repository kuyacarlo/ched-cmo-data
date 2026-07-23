# Dataset Card: CHED CMO Index

## Summary
Machine-readable index of Commission on Higher Education (CHED) Memorandum Orders (CMOs) scraped from the CHED legacy site, covering series years **2000–2026**.

| Field | Value |
|-------|-------|
| Rows | see `data/manifest.json` → `row_count` |
| Primary files | `data/cmo_index.csv`, `data/cmo_index.jsonl` |
| Source | https://legacy.ched.gov.ph/{year}-ched-memorandum-orders/ |
| Update model | Re-run scraper (Podman/systemd on maintainer host, or `uv run`) |
| License (index) | CC0 1.0 |
| PDFs | **Not redistributed**; `url` points at CHED |

## Intended use
- Discover CMOs by year, number, title, and rough category
- Feed civic / education data portals (e.g. BetterGov Education)
- Seed downstream curriculum/course extraction (OCR + parsers) — **not included yet**

## Out of scope (v1)
- Full text of memoranda
- Structured course lists per degree program (except pharmacy sample)
- Official CHED API guarantees (legacy HTML may change)

## Schema

| Column | Type | Description |
|--------|------|-------------|
| year | int | Series year |
| cmo_no | string | Numeric CMO number when parseable |
| cmo_reference | string | Raw reference text (e.g. `CMO No. 25, Series of 2015`) |
| title | string | Title from listing page |
| category | string | Heuristic label (see below) |
| url | string | PDF URL on legacy.ched.gov.ph |
| file_size_bytes | int/null | Local download size if scanned |
| page_count | int/null | PDF page count if scanned |
| is_ocr_needed | bool/null | True when first pages have little extractable text |
| is_corrupted | bool/null | True if PDF parse failed |
| status | string/null | `downloaded` / `not_downloaded` / … |

### Categories
- `curriculum_program` — PSGs / program curricula / syllabi
- `curriculum_college` — HEI/SUC/LCU institutional policies
- `scholarship_student_services`
- `faculty_development`
- `research_journals`
- `administrative_governance` — residual

Categories are **heuristic**, not official CHED taxonomy. Expect edge cases.

## Quality notes
- ~90%+ of PDFs are scanned images (`is_ocr_needed=true`) → course extraction needs OCR
- One or more listings may fail to download (see `status`)
- Titles/links inherit whatever CHED published on the legacy year pages

## Reproduction
```bash
uv sync
uv run python 01.py          # index years → out.jsonl / out.csv
uv run python 02.py          # download missing PDFs → downloads/
uv run python scan_downloads.py
uv run python scripts/export_catalog.py   # → data/cmo_index.*
```

Or with Podman: see root `README.md`.

## Citation
CHED Memorandum Orders via legacy.ched.gov.ph; index compiled in this repository. Prefer citing both the CHED source URL and this dataset version (`manifest.json` → `generated_at`).
