# Technical Specification: Roblox API RAG

## 1. Introduction

This document outlines the technical plan for creating the Roblox API RAG, a self-contained, regularly-updated Docker image that provides a Retrieval-Augmented Generation (RAG) API. The primary objective is to furnish LLM-based agents with a comprehensive and easily accessible knowledge base of the Roblox engine's API and the Creator Hub's documentation.

The final deliverable will be a single Docker image, versioned in lockstep with the Roblox engine. This will allow developers to spin up a powerful, local-first knowledge base with a single command, empowering a new class of AI-driven developer tools for the Roblox ecosystem.

## 2. System Architecture

The system is designed as a composable, "build-it-yourself" architecture, prioritizing simplicity, portability, and performance. It consists of three main components: a data ingestion pipeline, a lightweight vector database, and a JSON-based RAG API server. These components are bundled together into a single, immutable Docker image using a multi-stage build process.

This approach, heavily informed by the research in [`open-source-dependencies-research.md`](./background/open-source-dependencies-research.md), ensures that the final artifact is self-contained and pre-loaded with all necessary data, requiring no runtime initialization or external dependencies.

### 2.1. Architectural Diagram

The following diagram illustrates the flow of data from the source repositories to the final API endpoint.

```mermaid
graph TD
    subgraph "Data Sources"
        A[Roblox Client Tracker<br>(API Dump)]
        B[Roblox Creator Docs<br>(Markdown Content)]
    end

    subgraph "Build-Time: Data Ingestion Pipeline (GitHub Action)"
        C[Scraper & Parser]
        D[Document Chunker]
        E[Embedding Model]
        F[Vector DB Populator]
    end

    subgraph "Runtime: Docker Container"
        G[File-based Vector DB<br>(Qdrant - Local Mode)]
        H[RAG API Server<br>(FastAPI)]
        I[API Endpoint<br>(/query)]
    end

    A -- Raw API JSON --> C
    B -- Raw Markdown --> C
    C -- Parsed Docs --> D
    D -- Text Chunks --> E
    E -- Vector Embeddings --> F
    F -- Populates --> G
    H -- Loads & Wraps --> G
    H -- Exposes --> I

    style G fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#ccf,stroke:#333,stroke-width:2px
```

### 2.2. Component Overview

*   **Data Ingestion Pipeline (Build-Time)**: Executed within a GitHub Action on a weekly schedule. This pipeline is responsible for:
    1.  Fetching the latest API dump from the `Roblox-Client-Tracker` repository.
    2.  Cloning the `creator-docs` repository.
    3.  Parsing, cleaning, and chunking the documentation into semantically meaningful segments.
    4.  Generating vector embeddings for each chunk.
    5.  Populating a local Qdrant vector database.

*   **Vector Database (Runtime)**: A file-based instance of Qdrant running in local mode. This database is "baked" into the final Docker image during the build process, making the container a self-contained, read-only knowledge appliance.

*   **RAG API Server (Runtime)**: A lightweight, asynchronous API server built with FastAPI. Its sole responsibility is to load the local Qdrant database and expose a `/query` endpoint. This endpoint accepts a natural language query, converts it into a vector embedding, and retrieves the most relevant document chunks from the database.

## 3. Data Sources and Technology Stack

This section details the specific data to be ingested and the technology stack chosen to build the RAG tool.

### 3.1. Data Sources

The knowledge base will be constructed from two primary sources:

1.  **Roblox Engine API Dump**:
    *   **Repository**: `https://github.com/MaximumADHD/Roblox-Client-Tracker`
    *   **File**: `Full-API-Dump.json`
    *   **Description**: This file provides a comprehensive, structured JSON representation of the Roblox engine's API, including classes, enums, properties, methods, and events. Its structured nature is ideal for precise metadata extraction.

2.  **Roblox Creator Documentation**:
    *   **Repository**: `https://github.com/Roblox/creator-docs`
    *   **Directory**: `content/en-us/`
    *   **Files**: All markdown (`.md`) files within this directory and its subdirectories.
    *   **Description**: This collection of guides, tutorials, and conceptual articles provides the narrative context and practical examples that are absent from the raw API dump.

### 3.2. Technology Stack

The technology stack is selected based on the principles of performance, simplicity, and alignment with the single-container architectural goal, as detailed in the [`open-source-dependencies-research.md`](./background/open-source-dependencies-research.md) document.

*   **Programming Language**: Python 3.11+
*   **Vector Database**: **Qdrant** (in local, file-based mode).
    *   **Reasoning**: Chosen for its high-performance, Rust-based architecture and exceptionally powerful metadata filtering capabilities, which are critical for querying structured API documentation.
*   **RAG API Framework**: **FastAPI**.
    *   **Reasoning**: A modern, high-performance, asynchronous web framework that is ideal for building minimal, efficient API servers.
*   **Embedding Model**: **`sentence-transformers/all-MiniLM-L6-v2`**.
    *   **Reasoning**: A high-quality, lightweight sentence transformer model that provides an excellent balance of performance and resource footprint, making it suitable for embedding within the container.
*   **Asynchronous HTTP Client**: **`httpx`**.
    *   **Reasoning**: Required for making non-blocking HTTP requests within the asynchronous FastAPI application, particularly for fetching data from source repositories during the ingestion phase.
*   **Dependency Management**: **Poetry**.
    *   **Reasoning**: Ensures a consistent, reproducible, and isolated development environment, simplifying dependency management and packaging.

## 4. Data Ingestion Pipeline

The data ingestion pipeline is a build-time process responsible for fetching, parsing, chunking, and embedding the source documentation into the vector database.

### 4.1. Execution Environment

*   **Trigger**: The pipeline will be executed weekly via a scheduled GitHub Action.
*   **Schedule**: The action will run at midnight on Thursday mornings (Pacific Time) to align with the typical weekly update schedule of the Roblox engine.
*   **Environment**: The pipeline will run within a temporary `ingester` stage of a multi-stage Docker build, ensuring that all ingestion-related dependencies are isolated from the final runtime image.

### 4.2. Ingestion Steps

The pipeline will follow these sequential steps:

1.  **Fetch Data Sources**:
    *   The `Roblox-Client-Tracker` repository will be queried to download the latest `Full-API-Dump.json`.
    *   The `Roblox/creator-docs` repository will be cloned to get the latest markdown documentation from the `content/en-us/` directory.

2.  **Parse and Pre-process**:
    *   **API Dump (`Full-API-Dump.json`)**: A custom parser will process the JSON file. It will iterate through each class and its members (properties, functions, events, callbacks). For each API member, it will generate a "document" containing its name, description, parameters, and return types, formatted into a clean, human-readable string.
    *   **Creator Docs (`.md` files)**: The markdown files will be loaded, and any unnecessary frontmatter or HTML tags will be stripped to retain only the core textual content.

3.  **Chunk Documents**:
    *   **API Dump**: Chunking will be logical. Each API member (e.g., `Part.Position`, `workspace:Raycast`) will constitute a single, distinct chunk. This ensures that retrieval results are highly specific and directly relevant to an API element.
    *   **Creator Docs**: A `RecursiveCharacterTextSplitter` will be used to break down the markdown documents into semantically coherent chunks of approximately 500-1000 characters, with some overlap to preserve context between chunks.

4.  **Generate Metadata**:
    *   This is a critical step for enabling powerful filtering. Each chunk will be associated with a rich metadata payload.
    *   **For API Chunks**:
        *   `source`: 'api_dump'
        *   `class_name`: The name of the parent class (e.g., 'Part').
        *   `member_name`: The name of the member (e.g., 'Position').
        *   `member_type`: The type of member ('Property', 'Function', 'Event', 'Callback').
        *   `tags`: Any relevant tags from the API dump (e.g., 'ReadOnly', 'Deprecated').
    *   **For Documentation Chunks**:
        *   `source`: 'creator_docs'
        *   `file_path`: The original path to the markdown file.
        *   `title`: The document's title, extracted from the H1 header.

5.  **Embed and Store**:
    *   The text content of each chunk will be converted into a vector embedding using the `all-MiniLM-L6-v2` model.
    *   Each chunk, consisting of its unique ID, vector embedding, and metadata payload, will be upserted into the Qdrant collection. The collection will be configured to index the metadata fields (`source`, `class_name`, `member_type`) to allow for fast and efficient filtering during queries.

## 5. RAG API Server

The RAG API server is a lightweight, asynchronous web application built with FastAPI. It serves as the runtime interface to the pre-loaded vector database.

### 5.1. Endpoints

The API will expose the following endpoints:

#### 5.1.1. `POST /query`

This is the primary endpoint for performing a retrieval-augmented search.

*   **Method**: `POST`
*   **Description**: Accepts a natural language query and optional filters, embeds the query, and returns the most relevant document chunks from the vector database.
*   **Request Body**: `QueryRequest`
*   **Response Body**: `QueryResponse`

#### 5.1.2. `GET /health`

A standard health check endpoint.

*   **Method**: `GET`
*   **Description**: Used to verify that the API server is running and responsive.
*   **Response Body**:
    ```json
    {
      "status": "ok"
    }
    ```

#### 5.1.3. `GET /status`

Provides metadata about the current state of the service.

*   **Method**: `GET`
*   **Description**: Returns information about the loaded data, such as the Roblox engine version it's based on.
*   **Response Body**:
    ```json
    {
      "roblox_version": "0.674.0.6740328",
      "last_updated": "2024-08-15T00:00:00Z",
      "total_documents": 15234
    }
    ```

### 5.2. Data Models (Pydantic)

The API will use Pydantic models for request and response validation.

#### 5.2.1. `QueryRequest`

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class QueryFilter(BaseModel):
    source: Optional[str] = Field(None, description="Filter by 'api_dump' or 'creator_docs'")
    class_name: Optional[str] = Field(None, description="Filter by a specific API class name")
    member_type: Optional[str] = Field(None, description="Filter by 'Property', 'Function', etc.")

class QueryRequest(BaseModel):
    text: str = Field(..., description="The natural language query text.")
    top_k: int = Field(5, gt=0, le=20, description="The number of results to return.")
    filters: Optional[QueryFilter] = Field(None, description="Optional metadata filters.")
```

#### 5.2.2. `QueryResponse`

```python
from pydantic import BaseModel
from typing import List, Dict, Any

class SearchResult(BaseModel):
    score: float
    payload: Dict[str, Any]

class QueryResponse(BaseModel):
    results: List[SearchResult]
```

### 5.3. Query Logic

Upon receiving a request at `/query`:

1.  The server embeds the incoming `text` from the `QueryRequest` into a vector using the loaded `all-MiniLM-L6-v2` model.
2.  It constructs a search query for Qdrant, including the query vector and any specified `filters`.
3.  The search is performed against the Qdrant collection.
4.  The results from Qdrant are formatted into the `QueryResponse` model and returned to the client.

## 6. Dockerization and CI/CD

This section describes how the application will be containerized and how the build and deployment process will be automated.

### 6.1. Optimized Multi-Stage Dockerfile

To maximize build cache efficiency and speed up development iterations, the `Dockerfile` will be structured with more granular stages. This isolates dependency installation from the slow data ingestion process.

*   **Stage 1: `base`**
    *   Installs base system dependencies and Poetry.

*   **Stage 2: `builder`**
    *   Copies the `pyproject.toml` and `poetry.lock` files.
    *   Installs all Python dependencies using Poetry. This layer is cached as long as dependencies do not change.

*   **Stage 3: `ingester`**
    *   Copies the ingestion source code from the `builder` stage.
    *   **Runs the data ingestion script.** This is the slowest step. This layer will be cached and only re-runs if the ingestion-related source code changes.

*   **Stage 4: `final`**
    *   **Base Image**: `python:3.11-slim`
    *   **Purpose**: This is the minimal, production-ready runtime image.
    *   **Steps**:
        1.  Copies the required runtime dependencies from the `builder` stage.
        2.  Copies the FastAPI application code.
        3.  **Crucially, copies the populated `/app/qdrant_data` directory from the `ingester` stage.**
        4.  Sets the `CMD` to run the FastAPI application using `uvicorn`.
        5.  Exposes the API port (e.g., 8000).

### 6.2. CI/CD Pipeline (GitHub Actions)

A GitHub Actions workflow will automate the entire build, test, and deployment process.

*   **Trigger**:
    *   `schedule`: Weekly, on Thursday mornings (Pacific Time).
    *   `workflow_dispatch`: To allow for manual runs.
    *   `push`: On pushes to the `main` branch (for testing the build process, not for deployment).

*   **Workflow Steps**:
    1.  **Checkout Code**: Checks out the repository.
    2.  **Get Roblox Version**: A script will query the `Roblox-Client-Tracker` repository to get the latest engine version string (e.g., `0.674.0.6740328`). This version will be used to tag the Docker image.
    3.  **Set up Docker Buildx**: Initializes the Docker build environment.
    4.  **Log in to Docker Hub**: Authenticates with Docker Hub using a repository secret.
    5.  **Build and Push Docker Image**:
        *   Executes the multi-stage Docker build.
        *   Tags the resulting image with the Roblox version and `latest`. For example: `yourusername/roblox-api-rag:0.674.0.6740328` and `yourusername/roblox-api-rag:latest`.
        *   Pushes the tagged images to Docker Hub.

### 6.3. Security and Secrets Management

To ensure that credentials are not leaked in a public repository, the following security measure will be implemented:

*   **Docker Hub Token**: The authentication token for pushing images to Docker Hub will **not** be stored in the repository code. Instead, it will be configured as an encrypted secret within the GitHub repository's settings (e.g., named `DOCKERHUB_TOKEN`).
*   **Workflow Access**: The GitHub Actions workflow will access this token securely using the `secrets` context (`${{ secrets.DOCKERHUB_TOKEN }}`). This mechanism prevents the secret from being exposed in logs or the repository's source code.

## 7. Local Development and Testing

To facilitate rapid development and testing, a `docker-compose.yml` file will be provided. This allows for a workflow that avoids re-running the slow ingestion process on every code change.

### 7.1. Docker Compose Strategy

The `docker-compose.yml` file will define:

*   **An `api` service**:
    *   Builds the application from the `Dockerfile`.
    *   Mounts the `src/` directory as a volume into the container. This enables **hot-reloading** of the FastAPI server, so code changes are reflected instantly without rebuilding the image.
    *   Maps the container's API port to a local port (e.g., `8000:8000`).

*   **A named volume `qdrant_data`**:
    *   This volume will be used to persist the Qdrant vector database on the host machine.
    *   The data will persist even when the container is stopped and removed.

### 7.2. Local Workflow

1.  **Initial Data Ingestion**: A developer will run a one-off command to execute the ingestion pipeline, which populates the `qdrant_data` volume.
    ```bash
    docker-compose run --rm api poetry run python -m roblox_api_rag.ingestion.main
    ```
2.  **Run API Server**: The developer will then start the API server.
    ```bash
    docker-compose up
    ```
3.  **Develop**: Any changes made to the API server code in the `src/` directory will trigger an automatic reload of the server inside the container. The database is not re-ingested, allowing for instant testing of API logic.

## 8. Project Structure

The project will be organized into a clear and modular structure to promote maintainability and ease of development.

```
/
├── .github/
│   └── workflows/
│       └── build_and_publish.yml  # GitHub Action for CI/CD
├── .devcontainer/
│   └── devcontainer.json          # VSCode Dev Container config
├── .gitignore
├── Dockerfile                     # Optimized multi-stage Dockerfile
├── docker-compose.yml             # For local development and testing
├── pyproject.toml                 # Poetry for dependency management
├── poetry.lock
├── README.md                      # High-level project overview
├── project-planning/
│   ├── README.md
│   ├── technical-specs.md         # This document
│   └── background/
│       └── ...                    # Supporting research documents
└── src/
    ├── roblox_api_rag/
    │   ├── __init__.py
    │   ├── main.py                # FastAPI application entry point
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── models.py          # Pydantic request/response models
    │   │   └── endpoints.py       # API endpoint definitions
    │   └── ingestion/
    │       ├── __init__.py
    │       ├── main.py            # Main ingestion script entry point
    │       ├── sources.py         # Logic for fetching data from GitHub
    │       ├── parsing.py         # Parsers for API dump and markdown
    │       └── chunking.py        # Logic for document chunking
    └── scripts/
        └── get_roblox_version.py  # Script to fetch the latest version for tagging