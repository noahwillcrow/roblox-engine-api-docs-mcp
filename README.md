# Roblox API RAG

This project provides a Retrieval-Augmented Generation (RAG) API for the Roblox engine. It ingests the official Roblox API dump and the Creator Documentation, creating a searchable vector database that can be queried to get relevant information about Roblox API classes, functions, properties, events, and documentation.

## Features

*   **Data Ingestion Pipeline**: Automatically fetches the latest Roblox API dump and Creator Documentation.
*   **Vector Database**: Parses, chunks, and embeds the documentation into a Qdrant vector database.
*   **Semantic Search API**: A FastAPI application that exposes an endpoint for performing semantic searches on the indexed data.
*   **MCP Server**: Integrates with a Meta-Cognitive Process (MCP) server, exposing the search functionality as a tool for other systems (e.g., AI agents).
*   **Data Filtering**: Allows for filtering search results by source (API dump or creator docs), class name, and member type.

## Architecture Overview

The project is composed of two main services: the **Ingestion Service** and the **API Service**. For a more detailed explanation of each service, please see the `README.md` files in the following directories:

*   `src/ingestion/README.md`
*   `src/mcp_server/README.md`

## Getting Started

### Prerequisites

*   Python 3.8+
*   Poetry for dependency management
*   Docker and Docker Compose

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/roblox-api-rag.git
    cd roblox-api-rag
    ```

2.  **Install dependencies using Poetry:**

    ```bash
    poetry install
    ```

### Running the Services

The services are managed using Docker Compose.

1.  **Build and run the services:**

    ```bash
    docker-compose up --build
    ```

    This will start the following services:
    *   `qdrant`: The Qdrant vector database.
    *   `ingestion`: The data ingestion service. This service will run once to populate the database and then exit.
    *   `api`: The FastAPI application.

## Usage

### MCP Server

The MCP server is mounted at `/mcp` and is available for interaction with other agents. The server exposes a `query_roblox_api_rag` tool that can be used to query the RAG system.

## Configuration

The application can be configured using environment variables. You can create a `.env` file in the root of the project to set these variables.

| Variable          | Description                                       | Default                |
| ----------------- | ------------------------------------------------- | ---------------------- |
| `QDRANT_DATA_PATH`  | The path to the Qdrant data directory.            | `./qdrant_data`        |
| `EMBEDDING_MODEL`   | The sentence transformer model to use for embeddings. | `all-MiniLM-L6-v2`     |
| `COLLECTION_NAME`   | The name of the Qdrant collection.                | `roblox_api`           |
