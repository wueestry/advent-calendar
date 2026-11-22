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

# A single worker keeps the in-memory login throttle and session revocation
# registry shared across requests; threads still allow concurrent handling.
CMD [".venv/bin/gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--worker-class", "gthread", \
     "--workers", "1", \
     "--threads", "8", \
     "--access-logfile", "-", \
     "advent_calendar:create_app()"]
