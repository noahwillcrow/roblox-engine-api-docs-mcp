import os
import json
from pathlib import Path
from fastapi import FastAPI
from contextlib import asynccontextmanager
from qdrant_client import QdrantClient
from langchain_community.embeddings import SentenceTransformerEmbeddings

from .mcp.server import mcp_server
from .state import app_state

# --- Constants ---
QDRANT_DATA_PATH = os.getenv("QDRANT_DATA_PATH", "./qdrant_data")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "roblox_api")
DATA_TYPES_CLASSES_FILE = Path(QDRANT_DATA_PATH) / "data_types_and_classes.json"

# --- Application State Management ---
# Use a dictionary to hold the application's state, including our expensive resources.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's lifespan. This is the recommended way to handle
    startup and shutdown events in modern FastAPI.
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

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Roblox API RAG",
    description="A RAG API for the Roblox engine, pre-loaded with API and documentation.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Dependency Injection Overrides ---
# These functions provide the actual resource instances to the API endpoints.

def get_qdrant_client_override():
    return app_state.get("qdrant_client")

def get_embedding_model_override():
    return app_state.get("embedding_model")

def get_collection_name_override():
    return app_state.get("collection_name")

# --- Mount MCP Server ---
# Mount the FastMCP server at the /mcp path.
# This makes the MCP interface available at http://localhost:8000/mcp
app.mount("/mcp", mcp_server.create_app())

# --- Root Endpoint ---
@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Welcome to the Roblox API RAG. See /docs for API documentation or /mcp for the MCP interface."}