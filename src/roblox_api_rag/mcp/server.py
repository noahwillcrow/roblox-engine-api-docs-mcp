from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# --- MCP Models (Simplified for demonstration) ---

class Tool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    endpoint_url: str = Field(..., description="The URL where this tool's actions can be invoked.")
    http_method: str = Field("POST", description="The HTTP method to use for invoking this tool (e.g., GET, POST).")

class ModelContext(BaseModel):
    tools: List[Tool] = []
    schemas: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class ModelContextRequest(BaseModel):
    model_id: str = Field(..., description="The ID of the model requesting context.")
    protocol_version: str = Field(..., description="The version of the Model Context Protocol being used.")

class ModelContextResponse(BaseModel):
    api_version: str = Field("1.0.0", description="Version of the API providing the context.")
    context: ModelContext

# --- MCP Router ---
mcp_router = APIRouter()

@mcp_router.post("/mcp", response_model=ModelContextResponse)
async def get_model_context(request: ModelContextRequest):
    """
    Provides the model context, including available tools and schemas.
    """
    print(f"Received model context request for model_id: {request.model_id}, protocol_version: {request.protocol_version}")

    # Define the tools available to the LLM
    tools = [
        Tool(
            name="query_roblox_api_rag",
            description="Search the Roblox API documentation and API dump for information. Use this for general questions about Roblox API, classes, properties, functions, events, or code examples.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The natural language query to search for."
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "The number of results to return (default: 5, max: 20).",
                        "default": 5
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional metadata filters to apply to the search.",
                        "properties": {
                            "source": {
                                "type": "string",
                                "enum": ["api_dump", "creator_docs"],
                                "description": "Filter by data source: 'api_dump' for API reference, 'creator_docs' for general documentation."
                            },
                            "class_name": {
                                "type": "string",
                                "description": "Filter by a specific API class name (e.g., 'Part'). Only applies to 'api_dump' source."
                            },
                            "member_type": {
                                "type": "string",
                                "enum": ["Property", "Function", "Event", "Callback"],
                                "description": "Filter by member type: 'Property', 'Function', 'Event', or 'Callback'. Only applies to 'api_dump' source."
                            }
                        },
                        "required": [] # All properties within filters are optional
                    }
                },
                "required": ["text"]
            },
            endpoint_url="/api/v1/query",
            http_method="POST"
        ),
        Tool(
            name="get_roblox_data_types_and_classes",
            description="Retrieve a list of all available Roblox API data types and class names. Use this to understand the full scope of Roblox API objects before formulating specific queries or if the user asks for a list of available types/classes.",
            parameters={
                "type": "object",
                "properties": {}
            },
            endpoint_url="/api/v1/data_types_and_classes",
            http_method="GET"
        )
    ]

    # Define schemas for the tools (referencing existing FastAPI models)
    # These schemas should match the Pydantic models used by your /query and /data_types_and_classes endpoints
    schemas = {
        "QueryRequest": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "top_k": {"type": "integer"},
                "filters": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "enum": ["api_dump", "creator_docs"]},
                        "class_name": {"type": "string"},
                        "member_type": {"type": "string", "enum": ["Property", "Function", "Event", "Callback"]}
                    }
                }
            },
            "required": ["text"]
        },
        "QueryResponse": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "number"},
                            "payload": {"type": "object"}
                        },
                        "required": ["score", "payload"]
                    }
                }
            },
            "required": ["results"]
        },
        "DataTypesAndClassesResponse": {
            "type": "object",
            "properties": {
                "data_types": {"type": "array", "items": {"type": "string"}},
                "classes": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["data_types", "classes"]
        }
    }

    # Add metadata (optional)
    metadata = {
        "description": "Model Context Protocol server for Roblox API RAG.",
        "contact": "roblox-api-rag-team@example.com"
    }

    return ModelContextResponse(
        context=ModelContext(
            tools=tools,
            schemas=schemas,
            metadata=metadata
        )
    )