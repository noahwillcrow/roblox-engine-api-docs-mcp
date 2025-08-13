import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from qdrant_client import QdrantClient
from langchain_community.embeddings import SentenceTransformerEmbeddings

from .api import endpoints

# --- Constants ---
QDRANT_DATA_PATH = os.getenv("QDRANT_DATA_PATH", "./qdrant_data")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "roblox_api")

# --- Application State Management ---
# Use a dictionary to hold the application's state, including our expensive resources.
app_state = {}

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

app.dependency_overrides[endpoints.get_qdrant_client] = get_qdrant_client_override
app.dependency_overrides[endpoints.get_embedding_model] = get_embedding_model_override
app.dependency_overrides[endpoints.get_collection_name] = get_collection_name_override

# --- Include API Router ---
app.include_router(endpoints.router, prefix="/api/v1")

# --- Root Endpoint ---
@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Welcome to the Roblox API RAG. See /docs for API documentation."}