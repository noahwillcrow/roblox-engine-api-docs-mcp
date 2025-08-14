# Technical Plan for Roblox API RAG MCP Extension

This document outlines the technical plan for integrating an MCP (Model Context Protocol) server with the existing Roblox API RAG. The primary goal is to expose the RAG's capabilities, specifically its `/query` endpoint and a new endpoint for listing data types and classes, to an LLM via the MCP.

## 1. Core Decisions

*   **MCP Server Language**: The MCP server will be implemented in **Python**.
*   **Web Framework**: The existing FastAPI application will be extended to serve the MCP. While FastAPI is currently in use, the plan acknowledges openness to alternative Python web frameworks if a more suitable option for MCP integration arises during development.

## 2. Updated Roblox API RAG Endpoints

To support the MCP, the existing Roblox API RAG FastAPI application will be enhanced with the following:

### 2.1. Existing `/query` Endpoint

*   **Endpoint**: `POST /query`
*   **Purpose**: This endpoint will continue to serve natural language queries to the vector database.
*   **Integration**: The MCP server will act as a proxy or direct caller to this endpoint, forwarding LLM queries and receiving structured results.

### 2.2. New `/data_types_and_classes` Endpoint

*   **Endpoint**: `GET /data_types_and_classes`
*   **Purpose**: To provide the LLM with a comprehensive list of all Roblox API data types and class names. This information is crucial for the LLM to formulate precise queries and understand the Roblox API schema.
*   **Response Body**:
    ```json
    {
      "data_types": ["CFrame", "Vector3", ...],
      "classes": ["Part", "Player", "Workspace", "DataModel", ...]
    }
    ```
*   **Data Generation**: The data for this endpoint will be generated during the RAG's ingestion process.
    *   The `Full-API-Dump.json` will be parsed to extract all unique data type and class names.
    *   This extracted data will be saved to a persistent file (e.g., `data_types_and_classes.json`) within the Qdrant data directory.
    *   This file will then be copied into the final Docker image, making it accessible to the FastAPI application at runtime.

## 3. Ingestion Pipeline Modifications

The ingestion pipeline (`src/roblox_api_rag/ingestion/main.py`) will be modified to:

*   **Extract Data Types and Classes**: Integrate a new step to call a function (e.g., `extract_data_types_and_classes` in `src/roblox_api_rag/ingestion/parsing.py`) that processes the `Full-API-Dump.json` to gather all unique data types and class names.
*   **Persist Data**: Save the extracted data types and classes to a JSON file (e.g., `data_types_and_classes.json`) in the `QDRANT_DATA_PATH` directory. This file will be loaded by the FastAPI application.

## 4. MCP Server Integration

The MCP server functionality will be integrated directly into the existing Roblox API RAG Docker image.

*   **Implementation**: The FastAPI application will be modified to serve the MCP. This might involve:
    *   Adding a new APIRouter specifically for MCP-related endpoints.
    *   Implementing the necessary MCP protocol handlers.
    *   Utilizing a Python MCP SDK if available and suitable (e.g., `@modelcontextprotocol/sdk-python`).
*   **Dependencies**: Any new Python dependencies required for the MCP SDK or related functionalities will be added to `pyproject.toml`.
*   **Docker Image Updates**:
    *   The `Dockerfile` will be updated to install new Python dependencies.
    *   The `docker-compose.yml` will be reviewed and updated to ensure necessary ports are exposed for the MCP server and that the `data_types_and_classes.json` file is correctly copied into the image.

## 5. Future Considerations

*   **Error Handling and Logging**: Ensure robust error handling and comprehensive logging for all new MCP-related functionalities.
*   **Testing**: Develop unit and integration tests for the new `/data_types_and_classes` endpoint and the MCP integration.
*   **Security**: Review and implement appropriate security measures for the MCP server.