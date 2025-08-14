from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from langchain_community.embeddings import SentenceTransformerEmbeddings

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

from .state import app_state

@dataclass
class AppContext:
    """Application context with typed dependencies for MCP server."""
    qdrant_client: QdrantClient
    embeddings_model: SentenceTransformerEmbeddings
    collection_name: str
    data_types_and_classes: Dict[str, Any]

@asynccontextmanager
async def mcp_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context for MCP server."""
    try:
        yield AppContext(
            qdrant_client=app_state["qdrant_client"],
            embeddings_model=app_state["embedding_model"],
            collection_name=app_state["collection_name"],
            data_types_and_classes=app_state["data_types_and_classes"]
        )
    finally:
        # No cleanup needed here, as the main app's lifespan manager handles it.
        pass

# Initialize FastMCP server with lifespan
mcp_server = FastMCP(
    "Roblox Engine API Docs MCP Server",
    lifespan=mcp_lifespan
)

# Define Pydantic models for tool inputs/outputs if they are not already defined elsewhere
# These models will be automatically converted to JSON schemas by FastMCP

class QueryFilters(BaseModel):
    source: Optional[str] = Field(None, description="Filter by data source: 'api_dump' for API reference, 'creator_docs' for general documentation.")
    class_name: Optional[str] = Field(None, description="Filter by a specific API class name (e.g., 'Part'). Only applies to 'api_dump' source.")
    member_type: Optional[str] = Field(None, description="Filter by member type: 'Property', 'Function', 'Event', or 'Callback'. Only applies to 'api_dump' source.")

class QueryRequest(BaseModel):
    text: str = Field(..., description="The natural language query to search for.")
    top_k: int = Field(5, description="The number of results to return (default: 5, max: 20).", ge=1, le=20)
    filters: Optional[QueryFilters] = Field(None, description="Optional metadata filters to apply to the search.")

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

@mcp_server.tool()
async def roblox_engine_api_docs(
    ctx: Context[ServerSession, AppContext], # Inject context for logging/progress and app resources
    text: str = Field(..., description="The natural language query to search for."),
    top_k: int = Field(5, description="The number of results to return (default: 5, max: 20).", ge=1, le=20),
    filters: Optional[QueryFilters] = Field(None, description="Optional metadata filters to apply to the search."),
) -> QueryResponse:
    """
    Search the Roblox API documentation and API dump for information. Use this for general questions about Roblox API, classes, properties, functions, events, or code examples.
    """
    if ctx:
        await ctx.info(f"Received query for: {text} with top_k={top_k} and filters={filters}")

    app_ctx = ctx.request_context.lifespan_context
    qdrant_client = app_ctx.qdrant_client
    embeddings_model = app_ctx.embeddings_model
    collection_name = app_ctx.collection_name

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
        if ctx:
            await ctx.error(f"Error during query: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

@mcp_server.resource("/roblox/types-and-classes")
async def get_roblox_data_types_and_classes(
    ctx: Context[ServerSession, AppContext], # Inject context for logging/progress and app resources
) -> DataTypesAndClassesResponse:
    """
    Provides a list of all available Roblox API data types and class names. Use this to understand the full scope of Roblox API objects before formulating specific queries or if the user asks for a list of available types/classes.
    """
    if ctx:
        await ctx.info("Received request for Roblox data types and classes resource.")

    app_ctx = ctx.request_context.lifespan_context
    data_types_and_classes = app_ctx.data_types_and_classes

    if not data_types_and_classes:
        if ctx:
            await ctx.error("Data types and classes not loaded in AppContext.")
        raise HTTPException(status_code=500, detail="Data types and classes not loaded.")
    
    return DataTypesAndClassesResponse(
        data_types=data_types_and_classes.get("data_types", []),
        classes=data_types_and_classes.get("classes", [])
    )

# The mcp_router is no longer needed as FastMCP handles routing internally.