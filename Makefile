.PHONY: sync scrape export pipeline courses e2e test

sync:
	uv sync

scrape:
	uv run python 01.py
	uv run python 02.py
	uv run python scan_downloads.py

export:
	uv run python scripts/export_catalog.py

courses:
	uv run python scripts/build_course_program_cmo_ver.py

e2e:
	uv run python scripts/e2e_pipeline.py

e2e-full:
	uv run python scripts/e2e_pipeline.py --full

test:
	uv run pytest tests/ -q

pipeline: scrape export courses
