.PHONY: sync scrape export pipeline

sync:
	uv sync

scrape:
	uv run python 01.py
	uv run python 02.py
	uv run python scan_downloads.py

export:
	uv run python scripts/export_catalog.py

pipeline: scrape export
