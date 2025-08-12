# Technical Specification: Roblox API RAG Agent Knowledge Base

## 1\. Objective

To build a resilient, self-contained, and easily distributable system that periodically ingests Roblox API documentation into a vector database. This system will expose a retrieval-focused API, designed to serve as a "knowledge base" tool for LLM agents like Roo Code, enabling them to access up-to-date, accurate information for tasks such as code generation and game design.

## 2\. System Architecture

The system will be implemented as a multi-container application orchestrated by Docker Compose. This approach provides the desired operational simplicity of a single distributable package (`docker compose up`) while ensuring modularity, resilience, and adherence to modern software engineering best practices.

### 2.1. High-Level Diagram

The architecture consists of three distinct services communicating over an isolated Docker network:

  * **Scraper Service:** A Python container that runs on a schedule to fetch, process, and embed Roblox documentation.
  * **Vector DB Service:** A container running a Qdrant instance for persistent vector storage and retrieval.
  * **RAG API Service:** A Python FastAPI container that exposes the retrieval functionality to external LLM agents.

### 2.2. Service Definitions

| Service | Description |
| :--- | :--- |
| **`scraper-service`** | A Python-based container responsible for the data acquisition and ingestion pipeline. It runs a scheduled task, managed by **APScheduler**, to periodically fetch data from the official Roblox JSON API dump and crawl the Creator Hub documentation. After processing and chunking, it connects to the `vector-db-service` to upsert the resulting vectors. |
| **`vector-db-service`** | This container runs the official **Qdrant** image, providing a high-performance, persistent storage and retrieval layer for vector embeddings. It will be configured with a named Docker volume to ensure data persistence across restarts. |
| **`rag-api-service`** | A Python-based container running a **FastAPI** application. It exposes a single, retrieval-focused REST API endpoint. When queried by an agent, it connects to the `vector-db-service` to retrieve relevant document chunks and returns them as structured data. |

## 3\. Technology Stack

| Component | Technology | Justification |
| :--- | :--- | :--- |
| **Container Orchestration** | Docker Compose | Standard for defining and running multi-container applications, providing a single, distributable package that is easy to manage. |
| **Primary Data Source** | Roblox JSON API Dump | An official, structured, and versioned source of API data. Its machine-readable format is inherently more resilient to changes than HTML web pages. |
| **Supplemental Scraping** | Scrapy | A robust, asynchronous framework designed for large-scale web crawling, superior to simpler libraries for comprehensively scraping contextual documentation. |
| **Scheduling** | APScheduler | A powerful Python library for in-process task scheduling that is simpler to containerize and offers more granular control than system-level tools like cron. |
| **Vector Database** | Qdrant | A high-performance vector database written in Rust, chosen for its low resource usage, advanced filtering capabilities, and straightforward Docker deployment. |
| **Data Ingestion/Chunking** | LlamaIndex | A specialized framework for building data ingestion pipelines for LLMs, offering advanced tools like `SemanticSplitterNodeParser` for creating contextually coherent chunks. |
| **API Framework** | FastAPI | A high-performance, asynchronous API framework with excellent developer experience, Pydantic data validation, and automatic documentation. |
| **Agent Integration** | MCP Server | The Model Context Protocol (MCP) is the standard for extending agents like Roo Code with external tools, providing the most robust and native integration path. |

## 4\. Data Ingestion Pipeline (`scraper-service`)

### 4.1. Data Sources & Scraping Strategy

The data acquisition strategy is a hybrid approach prioritizing stability:

1.  **Primary Source (JSON API Dump):** The service will first fetch the latest Roblox client version GUID from an endpoint like `http://setup.roblox.com/versionQTStudio`. It will then use this GUID to construct the URL and download the full, structured API dump (e.g., `http://setup.roblox.com/{versionGuid}-API-Dump.json`). This structured data is the primary source for API class and member information.
2.  **Supplemental Source (Creator Hub Crawl):** To acquire contextual information, code examples, and guides, a **Scrapy** spider will be configured to crawl `https://create.roblox.com/docs`. The spider will recursively follow internal links and extract main content areas, discarding irrelevant HTML elements.

### 4.2. Chunking Strategy

To ensure high-quality retrieval, a **semantic chunking** strategy will be employed, as it preserves the contextual integrity of the source material. This will be implemented using **LlamaIndex's `SemanticSplitterNodeParser`**, which adaptively splits text between sentences based on embedding similarity, ensuring that resulting chunks are thematically coherent.

### 4.3. Scheduling

The entire data acquisition and ingestion pipeline will be scheduled to run periodically using **APScheduler**. An in-process `BackgroundScheduler` will be configured within the scraper script to execute the main data pipeline function on a cron-style schedule (e.g., daily).

## 5\. RAG API Service (`rag-api-service`)

The API is designed specifically for consumption by an LLM agent, not a human user. Its sole purpose is to provide raw, structured context that the agent can use for its own reasoning and generation tasks.

### 5.1. API Endpoint Definition

  * **Endpoint:** `POST /retrieve`
  * **Function:** Accepts a natural language query and returns a list of the most relevant document chunks from the vector database. It performs **retrieval only** and does not perform a generation step.
  * **Request Body:** A JSON object containing the user's query.
  * **Response Body:** A JSON object containing a list of retrieved documents, including their content, source, and metadata.

### 5.2. Pydantic Data Models

The request and response structures will be strictly defined using Pydantic models to ensure data validation and generate automatic API documentation.python
from pydantic import BaseModel
from typing import List, Dict, Any

class RetrievalRequest(BaseModel):
query: str

class RetrievedDocument(BaseModel):
source: str
content: str
metadata: Dict[str, Any]

class RetrievalResponse(BaseModel):
documents: List

````

### 5.3. Production Considerations

The API will be built with production readiness in mind:
*   **Asynchronous Operations:** All I/O-bound operations (database calls) will be asynchronous to handle concurrent requests efficiently.
*   **Error Handling:** The service will use FastAPI's `HTTPException` to return meaningful HTTP status codes and clear error messages that an agent can interpret.
*   **Logging:** Structured logging will be implemented to provide observability for debugging and monitoring.

## 6. Integration with Roo Code

The primary method for integrating this RAG system with Roo Code will be through the **Model Context Protocol (MCP)**.

1.  **Create an MCP Server:** A lightweight MCP server will be developed. This server will define a new tool (e.g., `roblox_api_knowledge_base`) for Roo Code.
2.  **Tool Definition:** The tool's description will be carefully crafted to be clear and explicit, as this is what the Roo Code agent uses to determine when to invoke the tool. For example: *"Searches and returns up-to-date documentation from the Roblox API and Creator Hub. Use this for any questions about Roblox scripting, classes, methods, services, or game design best practices."*
3.  **Workflow:** When the Roo Code agent decides to use this tool, the MCP server will call the `POST /retrieve` endpoint on the RAG API service and return the structured `RetrievalResponse` directly to the agent.
4.  **Configuration:** The Roo Code extension in VS Code will be configured to connect to this custom MCP server.

## 7. Deployment and Operations

The entire system is designed to be built and run with a single command.

### 7.1. `docker-compose.yml`

```yaml
# docker-compose.yml
version: '3.8'

services:
  rag-api:
    build:
      context:.
      dockerfile: Dockerfile
    container_name: rag-api-service
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    depends_on:
      - qdrant
    env_file:
      -.env
    networks:
      - roblox-rag-net

  scraper:
    build:
      context:.
      dockerfile: Dockerfile
    container_name: scraper-service
    command: python scraper/main.py
    depends_on:
      - qdrant
    env_file:
      -.env
    networks:
      - roblox-rag-net

  qdrant:
    image: qdrant/qdrant:latest
    container_name: vector-db-service
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    env_file:
      -.env
    networks:
      - roblox-rag-net

volumes:
  qdrant_data:

networks:
  roblox-rag-net:
    driver: bridge
````

### 7.2. `Dockerfile` (Multi-stage)

```dockerfile
# Dockerfile

# ---- Stage 1: Builder ----
FROM python:3.11-slim as builder

WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml./

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# ---- Stage 2: Final ----
FROM python:3.11-slim as final

WORKDIR /app

COPY --from=builder /app /app
COPY./app./app
COPY./scraper./scraper

# Default command for the API service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.3. Configuration (`.env.example`)

```
# Qdrant API Key for securing the vector database
QDRANT_API_KEY="your_secure_api_key_here"

# OpenAI API Key for the embedding model in the scraper
OPENAI_API_KEY="your_openai_api_key_here"
```

### 7.4. Operational Guide

1.  **Clone Repository:** `git clone <repository_url>`
2.  **Configure Environment:** Copy `.env.example` to `.env` and populate with necessary API keys.
3.  **Build and Start:** `docker compose up --build -d`
4.  **Trigger Initial Scrape (Manual):** `docker compose exec scraper python scraper/main.py`
5.  **Query the API:** Send a POST request to `http://localhost:8000/retrieve`.
6.  **Stop System:** `docker compose down -v`

<!-- end list -->

```
```