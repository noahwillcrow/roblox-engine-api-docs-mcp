# This file is the entry point for the uvicorn server.
# It imports the mcp_server instance from the mcp_server module
# and assigns it to a variable named "app", which uvicorn expects.

import os
import json
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from langchain_community.embeddings import SentenceTransformerEmbeddings

from mcp.server.fastmcp import FastMCP

# --- Constants ---
QDRANT_DATA_PATH = os.getenv("QDRANT_DATA_PATH", "./qdrant_data")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "roblox_api")
DATA_TYPES_CLASSES_FILE = Path(QDRANT_DATA_PATH) / "data_types_and_classes.json"

# --- Application State Management ---
app_state = {}

@asynccontextmanager
async def lifespan(app): # The lifespan is passed the FastAPI app, not the MCP wrapper
    """
    Manages the application's lifespan, loading and cleaning up resources.
    """
    print("--- Application Startup ---")
    # Load expensive resources on startup
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    app_state["embedding_model"] = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
    
    print(f"Initializing Qdrant client from path: {QDRANT_DATA_PATH}")
    app_state["qdrant_client"] = QdrantClient(path=QDRANT_DATA_PATH)
    
    app_state["collection_name"] = COLLECTION_NAME

    # Load data types and classes
    print(f"Loading data types and classes from {DATA_TYPES_CLASSES_FILE}")
    if DATA_TYPES_CLASSES_FILE.exists():
        with open(DATA_TYPES_CLASSES_FILE, "r") as f:
            app_state["data_types_and_classes"] = json.load(f)
        print("Data types and classes loaded successfully.")
    else:
        print(f"Warning: {DATA_TYPES_CLASSES_FILE} not found. Data types and classes endpoint will return empty data.")
        app_state["data_types_and_classes"] = {"data_types": [], "classes": []}
    
    print("Startup complete.")
    
    yield
    
    # Clean up resources on shutdown
    print("--- Application Shutdown ---")
    app_state.clear()
    print("Shutdown complete.")

# Initialize FastMCP server
mcp = FastMCP(
    name="RobloxEngineApiReference",
    lifespan=lifespan
)

# Define Pydantic models for tool inputs/outputs if they are not already defined elsewhere
# These models will be automatically converted to JSON schemas by FastMCP

class QueryResultPayload(BaseModel):
    page_content: str
    metadata: Dict[str, Any]

class QueryResult(BaseModel):
    score: float
    payload: QueryResultPayload

class QueryResponse(BaseModel):
    results: List[QueryResult]

class DataTypesAndClassesResponse(BaseModel):
    data_types: List[str]
    classes: List[str]

@mcp.resource("resource://query/{text}")
async def roblox_engine_api_docs(
    text: str,
) -> QueryResponse:
    """
    Search the Roblox API documentation and API dump for information. Use this for general questions about Roblox API, classes, properties, functions, events, or code examples.
    """
    # Set default values for parameters not in the URI
    top_k = 5
    filters = None

    print(f"Received query for: '{text}' with top_k={top_k}")

    qdrant_client = app_state["qdrant_client"]
    embeddings_model = app_state["embedding_model"]
    collection_name = app_state["collection_name"]

    try:
        # Generate embedding for the query text
        query_embedding = embeddings_model.embed_query(text)

        # Build the filter conditions for Qdrant
        filter_conditions = []
        if filters:
            if filters.source:
                filter_conditions.append(
                    rest.FieldCondition(key="metadata.source", match=rest.MatchValue(value=filters.source))
                )
            if filters.class_name:
                filter_conditions.append(
                    rest.FieldCondition(key="metadata.class_name", match=rest.MatchValue(value=filters.class_name))
                )
            if filters.member_type:
                filter_conditions.append(
                    rest.FieldCondition(key="metadata.member_type", match=rest.MatchValue(value=filters.member_type))
                )
        
        query_filter = rest.Filter(must=filter_conditions) if filter_conditions else None

        # Perform the search in Qdrant
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )

        # Format the results for the response
        formatted_results = [
            QueryResult(
                score=result.score,
                payload=QueryResultPayload(
                    page_content=result.payload.get("page_content"),
                    metadata=result.payload.get("metadata")
                ),
            )
            for result in search_results
        ]

        return QueryResponse(results=formatted_results)
    except Exception as e:
        print(f"Error during query: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")


@mcp.custom_route("/health", methods=["GET"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@mcp.custom_route("/openapi.json", methods=["GET"])
async def get_openapi_schema():
    """Return the OpenAPI schema."""
    return mcp.openapi()

@mcp.resource("resource://datatypes-and-classes")
async def get_roblox_data_types_and_classes() -> DataTypesAndClassesResponse:
    """
    Provides a list of all available Roblox API data types and class names. Use this to understand the full scope of Roblox API objects before formulating specific queries or if the user asks for a list of available types/classes.
    """
    print("Received request for Roblox data types and classes resource.")

    data_types_and_classes = app_state.get("data_types_and_classes")

    if not data_types_and_classes:
        print("Error: Data types and classes not loaded in app_state.")
        raise HTTPException(status_code=500, detail="Data types and classes not loaded.")

    return DataTypesAndClassesResponse(
        data_types=data_types_and_classes.get("data_types", []),
        classes=data_types_and_classes.get("classes", [])
    )

# The mcp_router is no longer needed as FastMCP handles routing internally.

# The `mcp` object is the server builder.
# The actual ASGI application is at `mcp.app`.
app = mcp.app

if __name__ == "__main__":
    # The builder has a `run` method for local development.
    mcp.run(transport="http")