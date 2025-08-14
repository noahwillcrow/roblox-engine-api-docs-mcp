# Build and Publish Script

This directory contains a script to automate the process of building and publishing the Docker image for the Roblox Engine API Docs MCP Server.

## `go` Script

The `go` script is a parameterized shell script that encapsulates all the necessary steps to build the Docker image and push it to a container registry.

### Prerequisites

*   Docker Desktop (or Docker Engine) installed and running.
*   Python 3.11 and Poetry installed.
*   A Docker Hub account (or access to another container registry).

### Usage

To run the script, navigate to the project root directory and execute the following command:

```bash
./build-and-publish/go DOCKERHUB_USERNAME [DOCKERHUB_PASSWORD_OR_PAT]
```

#### Arguments

*   `DOCKERHUB_USERNAME`: (Required) Your Docker Hub username.
*   `DOCKERHUB_PASSWORD_OR_PAT`: (Optional) Your Docker Hub password or a Personal Access Token (PAT). If you do not provide this argument, you will be prompted to enter your password interactively. Using a PAT is recommended for better security, especially in automated environments.

### What the Script Does

1.  **Logs in to Docker Hub**: It authenticates you with Docker Hub using the provided credentials.
2.  **Gets the Roblox API Version**: It runs the `src/scripts/get_roblox_version.py` script to fetch the latest Roblox API version. This version is used to tag the Docker image.
3.  **Builds the Docker Image**: It builds the Docker image with two tags: `latest` and the specific version number obtained in the previous step.
4.  **Pushes the Docker Image**: It pushes both tags of the image to your Docker Hub repository.

This script simplifies the release process and ensures that builds are consistent and tagged appropriately.