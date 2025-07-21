# ---- Stage 1: Builder ----
FROM python:3.11-slim as builder

WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.in-project true && \
    poetry lock && \
    poetry install --no-root --no-interaction --no-ansi

# ---- Stage 2: Final ----
FROM python:3.11-slim as final

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY ./app ./app
COPY ./scraper ./scraper
COPY ./mcp_server ./mcp_server

ENV PATH="/app/.venv/bin:$PATH"

# Default command for the API service
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]