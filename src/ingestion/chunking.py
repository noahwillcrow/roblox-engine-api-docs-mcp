from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Constants ---
MARKDOWN_CHUNK_SIZE = 1000
MARKDOWN_CHUNK_OVERLAP = 150

# --- Public Functions ---

def chunk_documents(documents: list[Document]) -> list[Document]:
    """
    Chunks a list of documents based on their source metadata.

    - Documents from 'api_dump' are considered pre-chunked and are passed through directly.
    - Documents from 'creator_docs' are split into smaller chunks using a text splitter.

    Args:
        documents: A list of Document objects from the parsing stage.

    Returns:
        A list of chunked Document objects ready for embedding.
    """
    print("Chunking documents...")
    api_dump_docs = []
    creator_docs_to_chunk = []

    for doc in documents:
        source = doc.metadata.get("source")
        if source == "api_dump":
            # API dump documents are already logically chunked
            api_dump_docs.append(doc)
        elif source == "creator_docs":
            creator_docs_to_chunk.append(doc)
        else:
            print(f"Warning: Document with unknown source found: {doc.metadata}")

    # Chunk the markdown documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=MARKDOWN_CHUNK_SIZE,
        chunk_overlap=MARKDOWN_CHUNK_OVERLAP,
        length_function=len,
    )
    
    chunked_creator_docs = text_splitter.split_documents(creator_docs_to_chunk)
    
    total_chunks = len(api_dump_docs) + len(chunked_creator_docs)
    print(f"Chunking complete. Total chunks: {total_chunks}")
    print(f"  - API Dump chunks: {len(api_dump_docs)}")
    print(f"  - Creator Docs chunks: {len(chunked_creator_docs)}")
    
    return api_dump_docs + chunked_creator_docs

if __name__ == '__main__':
    # This block is for testing the chunking function independently.
    print("--- Testing Chunking Function ---")

    # Create some dummy documents to simulate parsed data
    test_docs = [
        Document(
            page_content="Class: Part\nProperty: Position\nType: Vector3",
            metadata={"source": "api_dump", "class_name": "Part"}
        ),
        Document(
            page_content="Class: Workspace\nFunction: Raycast\nParameters: (origin: Vector3, direction: Vector3)\nReturns: RaycastResult",
            metadata={"source": "api_dump", "class_name": "Workspace"}
        ),
        Document(
            page_content="""
            This is a long document about scripting. It has many sentences and paragraphs.
            The purpose of this document is to explain how to create amazing experiences on Roblox.
            We will cover topics such as variables, loops, and functions.
            This part should be in the first chunk.
            
            Now we are moving on to the second part of the document. This part should ideally
            be in a separate chunk, perhaps with some overlap from the previous part to maintain
            context. This is very important for good retrieval results. This sentence makes the
            document long enough to be split for sure. Let's add even more text to be absolutely
            certain that the chunker has something to do. More text, more text, more text.
            This should be enough now.
            """ * 5, # Make it long enough to be chunked
            metadata={"source": "creator_docs", "file_path": "scripting/intro.md"}
        )
    ]

    chunked_results = chunk_documents(test_docs)

    print(f"\nTotal documents before chunking: {len(test_docs)}")
    print(f"Total documents after chunking: {len(chunked_results)}")

    print("\n--- Sample Chunks ---")
    for i, chunk in enumerate(chunked_results):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Source: {chunk.metadata.get('source')}")
        print(f"Content Snippet:\n{chunk.page_content[:200]}...")
        if chunk.metadata.get("source") == "creator_docs":
            print(f"Chunk length: {len(chunk.page_content)}")