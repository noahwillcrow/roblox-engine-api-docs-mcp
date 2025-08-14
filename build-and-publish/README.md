# Build and Publish Script

This directory contains a script to automate the process of building and publishing the Docker image for the Roblox Engine API Docs MCP Server.

## `go` Script

The `go` script is a parameterized shell script that encapsulates all the necessary steps to build the Docker image and push it to a container registry.

### Prerequisites

*   Docker Desktop (or Docker Engine) installed and running.
*   Docker Buildx installed and configured.
    *   **For Docker Desktop users**: Buildx is usually included and enabled by default. If not, ensure Docker Desktop is up to date.
    *   **For Linux users**: You might need to install the Docker Buildx plugin separately. Refer to the official Docker documentation for your distribution. After installation, you might need to initialize a builder instance: `docker buildx create --name mybuilder --use`. If you encounter issues, try running `docker buildx install` to ensure the necessary components are in place.
*   Python 3.11 and Poetry installed.
*   A Docker Hub account (or access to another container registry).

### Usage

To run the script, navigate to the project root directory and execute the following command:

```bash
./build-and-publish/go DOCKERHUB_USERNAME [DOCKERHUB_PASSWORD_OR_PAT] [--skip-ingestion]
```

#### Arguments

*   `DOCKERHUB_USERNAME`: (Required) Your Docker Hub username.
*   `DOCKERHUB_PASSWORD_OR_PAT`: (Optional) Your Docker Hub password or a Personal Access Token (PAT). If you do not provide this argument, you will be prompted to enter your password interactively. Using a PAT is recommended for better security, especially in automated environments.
*   `--skip-ingestion`: (Optional) If provided, the script will skip building the ingestion Docker image. This assumes a pre-built `roblox-engine-api-docs-mcp-ingestion:latest` image is available locally.

### What the Script Does

1.  **Logs in to Docker Hub**: It authenticates you with Docker Hub using the provided credentials.
2.  **Gets the Roblox API Version**: It runs the `src/scripts/get_roblox_version.py` script to fetch the latest Roblox API version. This version is used to tag the Docker image.
3.  **Builds the Ingestion Docker Image**: It builds the `roblox-engine-api-docs-mcp-ingestion:latest` Docker image locally, which contains the pre-processed data. This image is not pushed to Docker Hub and does not require a Docker Hub username prefix.
4.  **Builds and Pushes the MCP Server Docker Image**: It builds the `roblox-engine-api-docs-mcp-server` Docker image for `linux/amd64` and `linux/arm64` platforms, leveraging the locally built ingestion image. It then pushes both `latest` and the specific version number tags to your Docker Hub repository. This step leverages Docker Buildx for multi-platform builds.

This script simplifies the release process and ensures that builds are consistent and tagged appropriately.