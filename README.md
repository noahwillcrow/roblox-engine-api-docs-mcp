# Roblox API RAG Agent Knowledge Base

This project provides a self-contained system for ingesting Roblox API documentation into a vector database and exposing it through a retrieval-focused API. It is designed to serve as a knowledge base for LLM agents like Roo Code, enabling them to access up-to-date and accurate information about the Roblox API.

## 1. System Architecture

The system is a multi-container application orchestrated by Docker Compose, consisting of the following services:

*   **`scraper-service`**: A Python container that periodically fetches, processes, and embeds Roblox documentation from the official JSON API dump and the Creator Hub.
*   **`vector-db-service`**: A Qdrant container for persistent vector storage and retrieval.
*   **`rag-api-service`**: A Python FastAPI container that exposes a retrieval-focused API for LLM agents.
*   **`mcp-server-service`**: A Python container running the MCP server to provide a tool for Roo Code.

## 2. Technology Stack

*   **Container Orchestration**: Docker Compose
*   **Data Sources**: Roblox JSON API Dump, Creator Hub
*   **Web Scraping**: Scrapy
*   **Scheduling**: APScheduler
*   **Vector Database**: Qdrant
*   **Data Ingestion/Chunking**: LlamaIndex
*   **API Framework**: FastAPI
*   **Agent Integration**: MCP Server

## 3. Setup and Configuration

### Prerequisites

*   Docker and Docker Compose
*   Git
*   Poetry for Python dependency management

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd roblox-api-rag
    ```

2.  **Configure the environment:**
    Copy the `.env.example` file to `.env` and populate it with your API keys.
    ```bash
    cp .env.example .env
    ```

3.  **Install Python dependencies:**
    ```bash
    poetry install
    ```

## 4. Operational Guide

### Building and Starting the System

To build and start all services, run the following command:

```bash
docker compose up --build -d
```

### Triggering an Initial Scrape

The scraper service is scheduled to run daily. To trigger an initial scrape manually, run the following command:

```bash
docker compose exec scraper python scraper/main.py
```

### Querying the API

You can query the RAG API directly by sending a POST request to `http://localhost:8000/retrieve`.

**Example using `curl`:**

```bash
curl -X POST "http://localhost:8000/retrieve" \
-H "Content-Type: application/json" \
-d '{"query": "How do I create a part in Roblox?"}'
```

### Stopping the System

To stop all services and remove the containers, run:

```bash
docker compose down -v
```

## 5. Project Structure

```
.
├── app/                # RAG API Service (FastAPI)
│   ├── main.py
│   ├── models.py
│   ├── retriever.py
│   └── logging_config.py
├── scraper/            # Scraper Service
│   ├── main.py
│   ├── roblox_api.py
│   ├── chunking.py
│   ├── vector_db.py
│   └── spiders/
│       └── creator_hub_spider.py
├── mcp_server/         # MCP Server for Roo Code integration
│   └── main.py
├── knowledge-database/ # Documentation and notes about the data
├── llm-notes/          # Technical specifications and TODOs
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── poetry.lock
├── pyproject.toml
└── README.md
