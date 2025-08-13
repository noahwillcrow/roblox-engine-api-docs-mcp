import os
import uuid
from qdrant_client import QdrantClient, models
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.docstore.document import Document

from .sources import get_api_dump, get_creator_docs_path
from .parsing import parse_api_dump, parse_markdown_documents
from .chunking import chunk_documents

# --- Constants ---
QDRANT_DATA_PATH = os.getenv("QDRANT_DATA_PATH", "./qdrant_data")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "roblox_api")

# --- Main Ingestion Function ---

def run_ingestion():
    """
    Executes the full data ingestion pipeline.
    Fetches, parses, chunks, embeds, and stores the documentation.
    """
    print("--- Starting Data Ingestion Pipeline ---")

    # 1. Fetch Data Sources
    print("\n--- Step 1: Fetching Data Sources ---")
    api_dump_data = get_api_dump()
    docs_path = get_creator_docs_path()

    # 2. Parse Documents
    print("\n--- Step 2: Parsing Documents ---")
    api_docs = parse_api_dump(api_dump_data)
    md_docs = parse_markdown_documents(docs_path)
    all_docs = api_docs + md_docs

    # 3. Chunk Documents
    print("\n--- Step 3: Chunking Documents ---")
    chunks = chunk_documents(all_docs)

    # 4. Embed and Store in Qdrant
    print("\n--- Step 4: Embedding and Storing in Qdrant ---")
    
    # Initialize Embedding Model
    print(f"Initializing embedding model: {EMBEDDING_MODEL}")
    embeddings_model = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
    
    # Initialize Qdrant Client
    print(f"Initializing Qdrant client at {QDRANT_DATA_PATH}")
    client = QdrantClient(path=QDRANT_DATA_PATH)
    
    # Get vector size from the embedding model
    vector_size = embeddings_model.client.get_sentence_embedding_dimension()
    
    # Recreate the collection to ensure it's fresh
    print(f"Recreating Qdrant collection '{COLLECTION_NAME}' with vector size {vector_size}")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
    )

    # Embed and upload in batches
    batch_size = 128
    print(f"Embedding and uploading {len(chunks)} chunks in batches of {batch_size}...")
    
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i+batch_size]
        
        # Get embeddings
        contents_to_embed = [chunk.page_content for chunk in batch_chunks]
        embeddings = embeddings_model.embed_documents(contents_to_embed)
        
        # Create points for Qdrant
        points_to_upload = [
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": chunk.page_content,
                    "metadata": chunk.metadata,
                }
            )
            for chunk, embedding in zip(batch_chunks, embeddings)
        ]
        
        # Upsert batch to Qdrant
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points_to_upload,
            wait=True,
        )
        print(f"  - Uploaded batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")

    print(f"Successfully uploaded {len(chunks)} points to Qdrant.")
    
    # 5. Cleanup
    print("\n--- Step 5: Cleaning up temporary files ---")
    import shutil
    shutil.rmtree(docs_path.parent.parent)
    print(f"Cleaned up temporary directory: {docs_path.parent.parent}")

    print("\n--- Data Ingestion Pipeline Complete ---")


if __name__ == "__main__":
    run_ingestion()