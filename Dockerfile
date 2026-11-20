FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev \
    && useradd --create-home --uid 10001 appuser

EXPOSE 5000

USER appuser

CMD [".venv/bin/flask", "--app", "advent_calendar", "run", "--host=0.0.0.0", "--port=5000"]
