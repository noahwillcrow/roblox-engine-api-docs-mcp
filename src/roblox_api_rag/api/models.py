from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# --- Request Models ---

class QueryFilter(BaseModel):
    """
    Metadata filters to narrow down the search space.
    """
    source: Optional[str] = Field(
        None, 
        description="Filter by data source: 'api_dump' or 'creator_docs'"
    )
    class_name: Optional[str] = Field(
        None, 
        description="Filter by a specific API class name (e.g., 'Part'). Only applies to 'api_dump' source."
    )
    member_type: Optional[str] = Field(
        None, 
        description="Filter by member type: 'Property', 'Function', 'Event', or 'Callback'."
    )

class QueryRequest(BaseModel):
    """
    The request body for the main /query endpoint.
    """
    text: str = Field(
        ..., 
        description="The natural language query text.",
        example="How do I change a part's color?"
    )
    top_k: int = Field(
        5, 
        gt=0, 
        le=20, 
        description="The number of results to return."
    )
    filters: Optional[QueryFilter] = Field(
        None, 
        description="Optional metadata filters to apply to the search."
    )

# --- Response Models ---

class SearchResult(BaseModel):
    """
    Represents a single search result from the vector database.
    """
    score: float
    payload: Dict[str, Any]

class QueryResponse(BaseModel):
    """
    The response body for the /query endpoint.
    """
    results: List[SearchResult]

class HealthResponse(BaseModel):
    """
    The response for the /health endpoint.
    """
    status: str = "ok"

class StatusResponse(BaseModel):
    """
    The response for the /status endpoint, providing metadata about the service.
    """
    roblox_version: str
    last_updated: str
    total_documents: int