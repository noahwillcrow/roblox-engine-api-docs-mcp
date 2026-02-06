#!/bin/bash

# Cron wrapper script for automated build and publish
# This script runs the build-and-publish/go script every Thursday at 2am
#
# Usage:
#   1. Set up Docker Hub credentials in ~/.dockerhub-creds
#   2. Add to crontab: 0 2 * * 4 /path/to/build-and-publish/cron-wrapper.sh
#
# The crontab schedule format is:
#   minute hour day-of-month month day-of-week command
#   0 2 * * 4 = 2:00 AM on Thursdays

set -eo pipefail

# Change to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Load credentials from secure file
CREDS_FILE="$HOME/.dockerhub-creds"
if [ ! -f "$CREDS_FILE" ]; then
    echo "Error: Credentials file not found at $CREDS_FILE" >&2
    echo "Please create it with format: USERNAME:PASSWORD_OR_PAT" >&2
    exit 1
fi

# Read credentials
DOCKERHUB_USERNAME=$(head -n 1 "$CREDS_FILE" | cut -d':' -f1)
DOCKERHUB_PAT=$(head -n 1 "$CREDS_FILE" | cut -d':' -f2-)

if [ -z "$DOCKERHUB_USERNAME" ] || [ -z "$DOCKERHUB_PAT" ]; then
    echo "Error: Invalid credentials format in $CREDS_FILE" >&2
    echo "Expected format: USERNAME:PASSWORD_OR_PAT" >&2
    exit 1
fi

# Set up environment
export DOCKER_API_VERSION=1.41
export OMP_NUM_THREADS=1

# Log file with date stamp
LOG_FILE="/tmp/roblox-mcp-build-$(date +%Y%m%d-%H%M%S).log"

echo "Starting automated build at $(date)" | tee "$LOG_FILE"
echo "Project directory: $PROJECT_DIR" | tee -a "$LOG_FILE"

# Run the build and publish script
if "$(dirname "$0")/go" "$DOCKERHUB_USERNAME" "$DOCKERHUB_PAT" >> "$LOG_FILE" 2>&1; then
    echo "Build completed successfully at $(date)" | tee -a "$LOG_FILE"
else
    echo "Build failed at $(date)" | tee -a "$LOG_FILE"
    echo "Check log at: $LOG_FILE" | tee -a "$LOG_FILE"
    exit 1
fi

# Optional: Clean up old logs (keep last 10)
ls -t /tmp/roblox-mcp-build-*.log 2>/dev/null | tail -n +11 | xargs -r rm

echo "Done at $(date)" | tee -a "$LOG_FILE"
