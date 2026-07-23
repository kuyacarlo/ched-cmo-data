FROM docker.io/python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY 01.py 02.py scan_downloads.py ./

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Default: full index + download missing PDFs + scan
CMD ["bash", "-c", "python 01.py && python 02.py && python scan_downloads.py"]
