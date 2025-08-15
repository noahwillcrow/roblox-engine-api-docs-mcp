# This Dockerfile creates a "job runner" container.
# Its purpose is to execute the 'build-and-publish/go' script in an isolated environment,
# avoiding the need to install Python, Poetry, or other dependencies on the host machine.
#
# How to use:
# 1. Build this Docker image:
#    docker build -t roblox-mcp-runner -f build-and-publish/Dockerfile.runner .
#
# 2. Run the script using this image:
#    docker run --rm -it \
#      -v /var/run/docker.sock:/var/run/docker.sock \
#      -v "$(pwd)":/app \
#      roblox-mcp-runner \
#      <DOCKERHUB_USERNAME> [DOCKERHUB_PASSWORD_OR_PAT] [--force-ingestion]
#
# The Docker socket is mounted to allow the container to use the host's Docker daemon.
# The project directory is mounted to '/app' so that:
#   a) The scripts have access to all project files.
#   b) The 'qdrant_data' directory, when generated, is created on the host.
#   c) The Docker build context is correct when 'docker buildx' is called.

# Use the official Python 3.11 slim base image.
FROM python:3.11-slim-bullseye

# Set environment variables to prevent interactive prompts during installation.
ENV DEBIAN_FRONTEND=noninteractive

# Install Docker CLI, buildx plugin, and other necessary dependencies.
RUN \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        bash \
        gfortran \
        libopenblas-dev \
        liblapack-dev \
        build-essential \
        pkg-config \
        git && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        docker-ce-cli \
        docker-buildx-plugin && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory inside the container
WORKDIR /app

# Copy all project files into the image.
COPY . .

# Install poetry dependencies
RUN poetry install --no-root

# Make the scripts executable
RUN chmod +x ./build-and-publish/go && \
    chmod +x ./build-and-publish/ingest-locally

# Set the entrypoint to the 'go' script.
ENTRYPOINT ["./build-and-publish/go"]

# Default command is empty.
CMD []