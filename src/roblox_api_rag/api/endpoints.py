from fastapi import APIRouter, HTTPException, Depends
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from langchain_community.embeddings import SentenceTransformerEmbeddings

from .models import QueryRequest, QueryResponse, HealthResponse, StatusResponse, DataTypesAndClassesResponse

# --- API Router ---
router = APIRouter()

# --- Dependencies ---

# These dependencies are managed by the main.py entrypoint,
# which will create the objects on startup and pass them to the router.
# This is a common pattern to manage expensive resources like models and clients.

def get_qdrant_client() -> QdrantClient:
    """Dependency to get the Qdrant client."""
    # This will be replaced by the actual client instance in main.py
    raise NotImplementedError("get_qdrant_client dependency not implemented")

def get_embedding_model() -> SentenceTransformerEmbeddings:
    """Dependency to get the embedding model."""
    # This will be replaced by the actual model instance in main.py
    raise NotImplementedError("get_embedding_model dependency not implemented")

def get_collection_name() -> str:
    """Dependency to get the collection name."""
    raise NotImplementedError("get_collection_name dependency not implemented")

# --- Endpoints ---

@router.post("/query", response_model=QueryResponse)
def query_database(
    request: QueryRequest,
    qdrant_client: QdrantClient = Depends(get_qdrant_client),
    embeddings_model: SentenceTransformerEmbeddings = Depends(get_embedding_model),
    collection_name: str = Depends(get_collection_name)
):
    """
    Accepts a query, embeds it, and searches the vector database.
    """
    try:
        # Generate embedding for the query text
        query_embedding = embeddings_model.embed_query(request.text)

        # Build the filter conditions for Qdrant
        filter_conditions = []
        if request.filters:
            if request.filters.source:
                filter_conditions.append(
                    rest.FieldCondition(key="metadata.source", match=rest.MatchValue(value=request.filters.source))
                )
            if request.filters.class_name:
                filter_conditions.append(
                    rest.FieldCondition(key="metadata.class_name", match=rest.MatchValue(value=request.filters.class_name))
                )
            if request.filters.member_type:
                filter_conditions.append(
                    rest.FieldCondition(key="metadata.member_type", match=rest.MatchValue(value=request.filters.member_type))
                )
        
        query_filter = rest.Filter(must=filter_conditions) if filter_conditions else None

        # Perform the search in Qdrant
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=request.top_k,
            with_payload=True,
        )

        # Format the results for the response
        formatted_results = [
            {
                "score": result.score,
                "payload": result.payload,
            }
            for result in search_results
        ]

        return {"results": formatted_results}
    except Exception as e:
        print(f"Error during query: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    Standard health check endpoint to verify that the API is responsive.
    """
    return {"status": "ok"}

@router.get("/status", response_model=StatusResponse)
def get_status(
    qdrant_client: QdrantClient = Depends(get_qdrant_client),
    collection_name: str = Depends(get_collection_name)
):
    """
    Provides metadata about the current state of the service, including
    the number of documents in the vector database.
    """
    try:
        collection_info = qdrant_client.get_collection(collection_name=collection_name)
        total_docs = collection_info.points_count
        
        # In a real implementation, version and last_updated would be dynamically
        # loaded from a file or environment variable set during the build process.
        return {
            "roblox_version": "TBD",
            "last_updated": "TBD",
            "total_documents": total_docs
        }
    except Exception as e:
        print(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve collection status.")

@router.get("/data_types_and_classes", response_model=DataTypesAndClassesResponse)
def get_data_types_and_classes(
    data_types_and_classes: dict = Depends(lambda: app_state.get("data_types_and_classes"))
):
    """
    Returns a list of all Roblox API data types and classes.
    This data is generated during the ingestion process.
    """
    if not data_types_and_classes:
        raise HTTPException(status_code=500, detail="Data types and classes not loaded.")
    return data_types_and_classes