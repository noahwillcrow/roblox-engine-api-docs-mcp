# --- Stage 1: Base ---
# Use a specific Python version to ensure consistency.
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH"

# Install poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python - && \
    apt-get remove -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Stage 2: Builder ---
# This stage installs all dependencies. It's cached as long as pyproject.toml/poetry.lock don't change.
FROM base as builder

WORKDIR /app

# Install build-essential for packages that need to compile C extensions
RUN apt-get update && apt-get install -y build-essential git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN poetry install --no-root

# --- Stage 3: Ingester ---
# This stage runs the slow data ingestion process. It's cached as long as the ingestion code doesn't change.
FROM builder as ingester

WORKDIR /app

COPY ./src /app/src

# Set the data path for the Qdrant database
ENV QDRANT_DATA_PATH="/app/qdrant_data"

# Run the ingestion script
RUN poetry run python -m roblox_api_rag.ingestion.main

# --- Stage 4: Final ---
# This is the minimal production image.
FROM base as final

WORKDIR /app

# Copy the installed dependencies from the builder stage
COPY --from=builder /opt/poetry /opt/poetry
COPY --from=builder /app/.venv /app/.venv

# Copy the populated Qdrant database from the ingester stage
COPY --from=ingester /app/qdrant_data /app/qdrant_data

# Copy the API application code
COPY ./src/roblox_api_rag/main.py ./src/roblox_api_rag/main.py
COPY ./src/roblox_api_rag/api ./src/roblox_api_rag/api

# Set environment variables for the runtime
ENV QDRANT_DATA_PATH="/app/qdrant_data" \
    COLLECTION_NAME="roblox_api"

EXPOSE 8000

CMD ["uvicorn", "roblox_api_rag.main:app", "--host", "0.0.0.0", "--port", "8000"]