import logging
import os
from qdrant_client import QdrantClient, models
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.embeddings.fastembed import FastEmbedEmbedding

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "roblox_api_docs"

def get_qdrant_client():
    """
    Initializes and returns the Qdrant client.
    """
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def create_qdrant_collection(client: QdrantClient):
    """
    Creates the Qdrant collection if it doesn't already exist.
    """
    try:
        client.get_collection(collection_name=COLLECTION_NAME)
        logger.info(f"Collection '{COLLECTION_NAME}' already exists.")
    except Exception:
        logger.info(f"Collection '{COLLECTION_NAME}' not found. Creating new collection.")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
        logger.info(f"Successfully created collection '{COLLECTION_NAME}'.")

def upsert_nodes_to_qdrant(nodes):
    """
    Upserts the chunked nodes to the Qdrant vector database.
    """
    client = get_qdrant_client()
    create_qdrant_collection(client)

    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    index = VectorStoreIndex(
       nodes=nodes,
       storage_context=storage_context,
       embed_model=FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    )
    
    logger.info(f"Successfully upserted {len(nodes)} nodes to Qdrant.")
    return index