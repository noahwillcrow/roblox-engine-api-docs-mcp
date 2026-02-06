#!/bin/bash

# Cron wrapper script for automated build and publish using Docker
# This script runs the build process in a Docker container (no Poetry needed on host)
#
# Prerequisites:
#   1. Run 'docker login' manually on the host first
#   2. Set DOCKERHUB_USERNAME environment variable or pass as argument
#
# Usage:
#   DOCKERHUB_USERNAME=yourusername ./build-and-publish/cron-wrapper-docker.sh
#   OR
#   ./build-and-publish/cron-wrapper-docker.sh yourusername
#
# Cron setup:
#   0 2 * * 4 DOCKERHUB_USERNAME=yourusername /path/to/build-and-publish/cron-wrapper-docker.sh

set -eo pipefail

# Change to the project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

# Get Docker Hub username from argument or environment variable
DOCKERHUB_USERNAME="${1:-$DOCKERHUB_USERNAME}"

if [ -z "$DOCKERHUB_USERNAME" ]; then
    echo "Error: Docker Hub username is required" >&2
    echo "Usage: DOCKERHUB_USERNAME=yourusername $0" >&2
    echo "   or: $0 yourusername" >&2
    exit 1
fi

# Check if logged into Docker Hub
echo "--- Checking Docker Hub login status ---"
if ! docker info 2>/dev/null | grep -q "Username"; then
    echo "Error: Not logged into Docker Hub" >&2
    echo "Please run 'docker login' first" >&2
    exit 1
fi

echo "Logged in as: $(docker info 2>/dev/null | grep Username | awk '{print $2}')"

# Log file with date stamp
LOG_FILE="/tmp/roblox-mcp-build-$(date +%Y%m%d-%H%M%S).log"

echo "Starting automated build at $(date)" | tee "$LOG_FILE"
echo "Project directory: $PROJECT_DIR" | tee -a "$LOG_FILE"
echo "Docker Hub username: $DOCKERHUB_USERNAME" | tee -a "$LOG_FILE"

# Docker image name for the build environment
BUILDER_IMAGE="roblox-mcp-builder:latest"

# Build the builder image if it doesn't exist or if Dockerfile changed
echo "--- Ensuring builder image is up to date ---" | tee -a "$LOG_FILE"
docker build \
    -t "$BUILDER_IMAGE" \
    -f "$PROJECT_DIR/build-and-publish/Dockerfile.ingestion" \
    "$PROJECT_DIR" 2>&1 | tee -a "$LOG_FILE"

# Run the build process in a Docker container
# - Mount Docker socket to allow building/pushing images
# - Mount the project directory
# - Mount Docker config to use host's login credentials
echo "--- Running build process in Docker container ---" | tee -a "$LOG_FILE"
if docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$PROJECT_DIR:/app" \
    -v "$HOME/.docker:/root/.docker:ro" \
    -e DOCKERHUB_USERNAME="$DOCKERHUB_USERNAME" \
    -e DOCKER_API_VERSION=1.41 \
    -e OMP_NUM_THREADS=1 \
    "$BUILDER_IMAGE" \
    ./build-and-publish/go "$DOCKERHUB_USERNAME" 2>&1 | tee -a "$LOG_FILE"; then
    echo "Build completed successfully at $(date)" | tee -a "$LOG_FILE"
else
    echo "Build failed at $(date)" | tee -a "$LOG_FILE"
    echo "Check log at: $LOG_FILE" | tee -a "$LOG_FILE"
    exit 1
fi

# Optional: Clean up old logs (keep last 10)
ls -t /tmp/roblox-mcp-build-*.log 2>/dev/null | tail -n +11 | xargs -r rm

echo "Done at $(date)" | tee -a "$LOG_FILE"
