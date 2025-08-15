# Quickstart Guide: Using the Pre-built Roblox Engine API Docs MCP Container

This guide provides a quick overview of how to use the pre-built Docker container for the Roblox Engine API Docs MCP. This container comes with the Qdrant vector database already populated with Roblox API documentation, making it ready for immediate use.

## Prerequisites

*   [Docker](https://www.docker.com/get-started) installed on your system.

## Running the Service

1.  **Pull the Docker image:**
    Pull the latest image from DockerHub. You can also pull a specific version by replacing `latest` with a Roblox version number (e.g., `v0.618.0.6180446`).

    ```bash
    docker pull noahwillcrowdocker/roblox-engine-api-docs-mcp-server:latest
    ```

2.  **Run the container:**
    Start the container, mapping the service's internal port 8000 to a local port. You can specify the host port by setting the `ROBLOX_API_MCP_HOST_PORT` environment variable. If `ROBLOX_API_MCP_HOST_PORT` is not set, it defaults to `8000`.

    ```bash
    # To run on the default port 8000:
    docker run -d -p 8000:8000 --name roblox-engine-api-docs-mcp-server noahwillcrowdocker/roblox-engine-api-docs-mcp-server:latest

    # To run on a custom port, e.g., 9000:
    docker run -d -p 9000:8000 -e ROBLOX_API_MCP_HOST_PORT=9000 --name roblox-engine-api-docs-mcp-server noahwillcrowdocker/roblox-engine-api-docs-mcp-server:latest
    ```

    The service will now be running and accessible at `http://localhost:<YOUR_HOST_PORT>`. For example, if you used port 9000, it would be `http://localhost:9000`.

## Key Features of the Built Container

The pre-built container offers the following features:

*   **Pre-populated Knowledge Base**: The container includes a Qdrant vector database pre-filled with the latest Roblox Engine API documentation. This means you don't need to run the ingestion process yourself.
*   **Retrieval-Augmented Generation (RAG) API**: The container exposes a FastAPI-based MCP server that allows AI agents to query the documentation using natural language.
*   **MCP Compatibility**: The server is fully compatible with the Meta-Cognitive Process (MCP) protocol, enabling seamless integration with AI agents like Cursor and Roo Cline.
*   **Easy Deployment**: With Docker, deploying the service is as simple as pulling the image and running a single command.
*   **Scalability**: The containerized setup allows for easy scaling and management of the service.

## Usage for AI Agents (Cursor & Roo Cline)

The service exposes a Meta-Cognitive Process (MCP) server with a tool that AI agents can use to query the Roblox API and documentation.

### Registering the Tool

To allow an agent like Cursor or Roo Cline to use this service, you need to register the `roblox_engine_api_docs` tool.

1.  **Tool Name**: `roblox_engine_api_docs`
2.  **API Endpoint**: The MCP server is available at `http://localhost:<YOUR_HOST_PORT>/mcp/`.
3.  **OpenAPI Schema**: The agent can find the tool's definition at `http://localhost:<YOUR_HOST_PORT>/openapi.json`.

You would typically provide this information in the agent's configuration or tool registration interface. For example, if you are running the service on port 9000, you might tell the agent:

> "You have a new tool available: `roblox_engine_api_docs`. You can access its OpenAPI schema at `http://localhost:9000/openapi.json` and interact with it via the MCP server at `http://localhost:9000/mcp/`."

The agent can then inspect the schema to understand how to use the tool's parameters for searching the Roblox API knowledge base.