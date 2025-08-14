# --- Stage 1: Base ---
# Use a specific Python version to ensure consistency.
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    NLTK_DATA="/usr/local/nltk_data"

# Install poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python - && \
    apt-get remove -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Stage 2: Builder ---
# This stage installs all dependencies. It's cached as long as pyproject.toml/poetry.lock don't change.
FROM base as builder

WORKDIR /app

# Install build-essential for packages that need to compile C extensions and git for cloning
RUN apt-get update && apt-get install -y build-essential git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root && \
    rm -rf /root/.cache/pypoetry

# --- Stage 3: Final ---
# This is the minimal production image.
FROM base as final

WORKDIR /app

# Copy the installed dependencies from the builder stage
COPY --from=builder /opt/poetry /opt/poetry
COPY --from=builder /app/.venv /app/.venv

# Copy the project files
COPY --from=builder /app/poetry.lock ./
COPY --from=builder /app/pyproject.toml ./

# Copy the API application code and ingestion data
COPY ./src/mcp_server ./src/mcp_server

# Copy the populated Qdrant database from the local build context
COPY ./qdrant_data /app/qdrant_data

# Set environment variables for the runtime
ENV QDRANT_DATA_PATH="/app/qdrant_data" \
    COLLECTION_NAME="roblox_api"

EXPOSE 8000

# Add the virtual environment's bin directory to the PATH to make executables like 'uvicorn' available.
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "mcp_server.main:app", "--host", "0.0.0.0", "--port", "8000"]