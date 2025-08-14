# Plan to Integrate Roblox API RAG with MCP Server

The objective is to create a local MCP server that acts as a bridge to your existing Roblox API RAG, specifically exposing its `/query` endpoint for natural language queries and a new resource for listing data types and classes.

## 1. Understand the Existing RAG API

*   **Endpoint**: The primary endpoint we will interact with is [`POST /query`](../../technical-specs.md:151).
*   **Request Body**: This endpoint expects a [`QueryRequest`](../../technical-specs.md:198) Pydantic model, which includes `text` (the query string), `top_k` (number of results), and optional `filters` (for `source`, `class_name`, `member_type`).
*   **Response Body**: It returns a [`QueryResponse`](../../technical-specs.md:215) containing a list of `SearchResult` objects.
*   **Running Instance**: It's assumed that your Roblox API RAG FastAPI server will be running, likely accessible at `http://localhost:8000` as per the `docker-compose.yml` strategy outlined in [`technical-specs.md`](../../technical-specs.md:311).

## 2. Update Roblox API RAG to Expose Data Types and Classes

To provide the LLM with a list of all Roblox API data types and classes, we will add a new endpoint to the existing Roblox API RAG.

*   **New Endpoint**: `GET /data_types_and_classes`
*   **Description**: This endpoint, specific to this project's MCP, will return a JSON object with two arrays: one for Roblox API data types and one for classes. This list will be generated during the RAG's ingestion process and stored in a way that the FastAPI server can easily retrieve it at runtime.
*   **Response Body Example**:
    ```json
    {
      "data_types": ["CFrame", "Vector3", ...],
      "classes": ["Part", "Player", "Workspace", "DataModel", "RemoteEvent", "BindableFunction", ...]
    }
    ```
*   **Ingestion Integration**: The RAG's ingestion pipeline will be modified to extract all class and data type names from the `Full-API-Dump.json` and save them to a file (e.g., `data_types_and_classes.json`) within the Qdrant data directory, which will then be copied into the final Docker image.

## 3. Integrate MCP Server into Existing Roblox API RAG Docker Image

Instead of creating a separate MCP server project, the existing Roblox API RAG Docker image will be extended to expose an MCP. This involves:

*   **MCP Integration**: The FastAPI application within the Roblox API RAG will be modified to serve the MCP, exposing the `/query` and `/data_types_and_classes` endpoints. This will be implemented in Python.
*   **Dependencies**: The existing Docker image will be updated to include any necessary Python MCP SDK (e.g., `@modelcontextprotocol/sdk-python` if available, or a similar library) and other required dependencies.
*   **Configuration**: Ensure the Docker image is configured to expose the necessary ports for the MCP.