import logging
import os
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import RetrieverQueryEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "roblox_api_docs"

def get_retriever():
    """
    Initializes and returns the retriever engine.
    """
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    )
    
    # Initialize OpenAI LLM
    llm = OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

    # Create a query engine that directly returns nodes
    query_engine = index.as_query_engine(
        similarity_top_k=5,
        response_mode="no_text", # This ensures only source nodes are returned
    )
    
    logger.info("Successfully initialized retriever engine.")
    return query_engine