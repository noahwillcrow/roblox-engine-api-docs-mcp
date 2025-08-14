# Web Server

This directory contains the user-facing service that provides the search functionality for the Roblox API RAG project.

## Server

The web server is a FastAPI application that provides the following functionalities:

*   **MCP Server Integration**: The search functionality is exposed as a tool through a Meta-Cognitive Process (MCP) server, which is mounted at the `/mcp` path. This allows other systems, such as AI agents, to use the RAG system as a knowledge source.

### Lifespan Management

The server uses a lifespan manager to share resources with the main FastAPI application. This ensures that the MCP server uses the same Qdrant client and embedding model as the rest of the application, avoiding resource duplication.

### Tools

The following tools are exposed by the MCP server:

*   **`query_roblox_api_rag`**: This tool allows you to perform a semantic search over the Roblox API and Creator Documentation. It accepts a natural language query, a `top_k` parameter to limit the number of results, and a set of filters to narrow down the search.

### Resources

The following resources are exposed by the MCP server:

*   **`/roblox/types-and-classes`**: This resource provides a list of all available Roblox API data types and class names. This is useful for understanding the scope of the API and for formulating more specific queries.