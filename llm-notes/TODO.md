# TODO: Roblox API RAG Agent Implementation

This document outlines the tasks required to implement the Roblox API RAG Agent based on the technical specification.

## Phase 1: Project Setup & Foundation

- [ ] Initialize Git repository and define `.gitignore`.
- [ ] Create the initial directory structure (`app`, `scraper`, `mcp_server`, `knowledge-database`, `llm-notes`).
- [ ] Set up the Python environment using Poetry and install initial dependencies.
- [ ] Create the initial `docker-compose.yml` file with service definitions.
- [ ] Create a multi-stage `Dockerfile` for building the Python services.
- [ ] Create the `.env.example` file with placeholder keys.
- [ ] Configure the `qdrant` service in `docker-compose.yml` with a persistent volume.

## Phase 2: Scraper Service (`scraper-service`)

- [ ] Implement the primary data scraper for the Roblox JSON API dump.
- [ ] Implement the supplemental Scrapy spider for the Creator Hub documentation.
- [ ] Implement the semantic chunking strategy using LlamaIndex's `SemanticSplitterNodeParser`.
- [ ] Implement the Qdrant client logic to connect and upsert vectors.
- [ ] Integrate the components into a single pipeline in `scraper/main.py`.
- [ ] Configure APScheduler to run the scraping pipeline periodically.

## Phase 3: RAG API Service (`rag-api-service`)

- [ ] Set up the FastAPI application in `app/main.py`.
- [ ] Define Pydantic models for `RetrievalRequest` and `RetrievalResponse`.
- [ ] Implement the `POST /retrieve` endpoint.
- [ ] Implement the logic to query the Qdrant vector database.
- [ ] Implement asynchronous operations for I/O-bound calls.
- [ ] Add structured logging and robust error handling.

## Phase 4: MCP Server Integration

- [ ] Create the basic MCP server structure.
- [ ] Define the `roblox_api_knowledge_base` tool for Roo Code.
- [ ] Implement the tool's logic to call the RAG API's `/retrieve` endpoint.
- [ ] Add configuration details for connecting Roo Code to the MCP server.

## Phase 5: Documentation & Finalization

- [ ] Create a comprehensive `README.md` with setup, configuration, and operational instructions.
- [ ] Write a `knowledge-database/README.md` to explain the purpose and structure of the data.
- [ ] Write implementation guidelines in `.roo/rules/implementation-guidelines.md`.
- [ ] Perform end-to-end testing of the entire system.
- [ ] Review and finalize all configurations.