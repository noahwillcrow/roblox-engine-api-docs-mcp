import logging
import os
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.postprocessor.colbert_rerank import ColbertRerank

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
    

    # Initialize local reranker
    local_rerank = ColbertRerank(
        top_n=5,
        model="colbertv2",  # Using a pre-trained ColbertV2 model
        tokenizer="colbertv2",
        keep_retrieved=True,
    )

    # Create a query engine that directly returns nodes
    query_engine = index.as_query_engine(
        similarity_top_k=10, # Retrieve more documents for the reranker
        response_mode="no_text",  # This ensures only source nodes are returned
        node_postprocessors=[local_rerank],
    )
    
    logger.info("Successfully initialized retriever engine with local reranker.")
    return query_engine