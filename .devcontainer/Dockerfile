# Use a specific Python version as the base image
FROM python:3.11-slim-buster

# Avoids prompts from apt-get
ARG DEBIAN_FRONTEND=noninteractive

# Install common development tools and Poetry
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends git curl build-essential && \
    pip install poetry && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user for development
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN /bin/bash -c "groupadd --gid $USER_GID $USERNAME && \
    useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    apt-get update && \
    apt-get install -y sudo && \
    echo '$USERNAME ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*"

# Set the working directory
WORKDIR /app

# Copy poetry configuration files
COPY poetry.lock pyproject.toml ./

# Install project dependencies
# The postCreateCommand in devcontainer.json will handle `poetry install --no-root`
# This is just to ensure the image has the dependencies if built standalone
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi || true

# Switch to the non-root user
USER $USERNAME