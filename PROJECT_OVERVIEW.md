# Project Overview: Roblox Engine API Docs MCP

This document provides an overview of the Roblox Engine API Docs MCP project, detailing its major components and local development helpers.

## Major Project Components

The project is structured around three core components that work together to provide a Retrieval-Augmented Generation (RAG) API for the Roblox engine:

1.  **MCP Server (`src/mcp_server`)**:
    *   This is the FastAPI application that serves as the Meta-Cognitive Process (MCP) server.
    *   It exposes an API endpoint that AI agents can use to query the Roblox API documentation.
    *   It integrates with a vector database (Qdrant) to perform semantic searches based on user queries.
    *   The server is designed to be non-blocking and efficient, leveraging `asyncio` for I/O operations.

2.  **Ingestion Python Code (`src/ingestion`)**:
    *   This component is responsible for scraping, parsing, chunking, and embedding the Roblox API documentation.
    *   It uses Scrapy for web scraping and processes the extracted data into a format suitable for the vector database.
    *   The processed data is then embedded using a pre-trained model and stored in Qdrant.
    *   This code is designed to be run periodically to keep the documentation up-to-date.

3.  **Build-and-Publish (`build-and-publish`)**:
    *   This directory contains the necessary scripts and Dockerfiles to build the entire project and publish the Docker image.
    *   It orchestrates the ingestion process (running the Python code) and then packages the MCP server along with the pre-populated Qdrant data into a single Docker image.
    *   This ensures that the deployed container is ready to serve queries immediately upon startup, without requiring a separate ingestion step.

## Local Development Helpers

To facilitate quick and easy local development and builds, the project includes several helper configurations:

*   **`./qdrant_data` directory**: This directory is used to store the Qdrant vector database data locally. It is gitignored (`.gitignore`) to prevent large binary files from being committed to version control. This allows developers to persist their local Qdrant data between runs and avoid re-ingesting data every time.
*   **`./local-build-caches` directory**: This directory is used for caching build artifacts during local development. Similar to `qdrant_data`, it is gitignored to keep the repository clean and focused on source code. Caching build artifacts speeds up iterative development cycles.
*   **`docker-compose.yml`**: This allows developers to easily spin up the MCP server while using mounts to their local file system for quick-and-easy rebuilds of the image and then quick testing. This simplifies the local development environment setup and ensures consistency across different development machines.

These local helpers are crucial for a smooth development workflow, enabling developers to quickly build, test, and iterate on the project components without interfering with the main repository.