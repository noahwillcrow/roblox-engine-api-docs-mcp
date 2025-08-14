# Ingestion Service

The ingestion service is a Python script that processes raw data from various sources and populates the vector database. It is the foundation of the RAG system, ensuring that the data is up-to-date and correctly formatted for efficient retrieval.

## Pipeline

The ingestion pipeline consists of the following steps:

1.  **Fetch**: It downloads the latest API dump from the [Roblox-Client-Tracker](https://github.com/MaximumADHD/Roblox-Client-Tracker) repository and clones the [creator-docs](https://github.com/Roblox/creator-docs) repository.
2.  **Parse**:
    *   The API dump is parsed into individual documents for each API member (e.g., `Part.Position`, `Workspace:Raycast`).
    *   The markdown files from the creator docs are loaded and cleaned to remove unnecessary content like YAML frontmatter and figures.
3.  **Chunk**:
    *   The documents from the API dump are considered pre-chunked, as each document represents a single, atomic piece of information.
    *   The creator docs are split into smaller chunks using a `RecursiveCharacterTextSplitter` to ensure they fit within the context window of the embedding model.
4.  **Embed**: The content of each chunk is converted into a vector embedding using a sentence transformer model (`all-MiniLM-L6-v2`).
5.  **Store**: The embeddings and their corresponding text content are stored in a [Qdrant](https://qdrant.tech/) vector database.

## Modules

*   **`main.py`**: The entry point for the ingestion service. It orchestrates the entire pipeline.
*   **`sources.py`**: Handles fetching the raw data from the various sources.
*   **`parsing.py`**: Contains the logic for parsing the raw data into a structured format.
*   **`chunking.py`**: Responsible for chunking the documents into smaller pieces.