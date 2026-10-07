# CHED CMO Data

Reproducible scraper + public index of [CHED](https://ched.gov.ph) Memorandum Orders (CMOs) from the legacy listings:

`https://legacy.ched.gov.ph/{year}-ched-memorandum-orders/`

## Quick start (use published data)

```bash
# CSV
head -5 data/cmo_index.csv

# JSONL
head -2 data/cmo_index.jsonl

# Build metadata
cat data/manifest.json
```

Schema and caveats: [`docs/DATASET_CARD.md`](docs/DATASET_CARD.md).

## Reproduce the index

Requires [uv](https://github.com/astral-sh/uv) and Python ≥ 3.12.

```bash
uv sync
uv run python 01.py                 # scrape year pages → out.csv / out.jsonl
uv run python 02.py                 # download PDFs not yet in downloads/
uv run python scan_downloads.py     # enrich with page counts / OCR flags
uv run python scripts/export_catalog.py
```

**PDFs are gitignored** (~2GB). The published dataset keeps `url` pointers to CHED so the catalog stays small and reproducible.

### Podman

```bash
podman build -t localhost/ched-cmo-pipeline:latest .
podman run --rm --network=host -v "$PWD:/work:Z" -w /work \
  localhost/ched-cmo-pipeline:latest \
  bash -c "python 01.py && python 02.py && python scan_downloads.py"
uv run python scripts/export_catalog.py
```

## Layout

| Path | Purpose |
|------|---------|
| `01.py` / `02.py` / `scan_downloads.py` | Pipeline stages |
| `classify.py` | Shared category heuristics |
| `scripts/export_catalog.py` | Builds `data/cmo_index.*` |
| `data/` | **Published** catalog + samples |
| `downloads/` | Local PDF cache (not in git) |
| `docs/` | Dataset card + BetterGov notes |

## BetterGov / open data

See [`docs/BETTERGOV.md`](docs/BETTERGOV.md). Education category on [data.bettergov.ph](https://data.bettergov.ph/datasets) has no CHED set yet — this index is meant to fill that gap.

## License

Index + scraper: [CC0](LICENSE). Linked PDFs remain CHED publications.

## Status

- **v1:** CMO metadata index (done)
- **v2 (planned):** OCR + structured course tables across degree programs

## Local finalization note

This isolated copy preserves the CHED CMO metadata dataset for review/archive. Verified locally: the published dataset files load and the manifest row count matches the CSV and JSONL artifacts. Full rescrape/download was not run because it performs live CHED network fetches and creates a multi-GB local PDF cache.
