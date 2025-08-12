# Knowledge Base for Roblox API RAG Agent

This document provides an overview of the data stored in the vector database that powers the Roblox API RAG Agent.

## 1. Purpose

The purpose of this knowledge base is to provide a comprehensive and up-to-date source of information about the Roblox API and Creator Hub. This data is used by the RAG (Retrieval-Augmented Generation) agent to answer questions and generate code related to Roblox development.

## 2. Data Sources

The knowledge base is built from two primary data sources:

1.  **Roblox JSON API Dump**: This is an official, structured dump of the Roblox API, providing detailed information about classes, methods, properties, and events.
2.  **Roblox Creator Hub**: The official documentation website for Roblox developers. This provides contextual information, tutorials, guides, and code examples.

## 3. Data Ingestion Pipeline

The data ingestion pipeline has been significantly improved to enhance the quality and granularity of the data stored in the vector database.

### 3.1. Scraping

The Scrapy spider (`creator_hub_spider.py`) has been enhanced to perform structured content extraction from the Creator Hub documentation. Instead of extracting the entire raw HTML of the main content area, it now parses the page to extract:

-   **Title**: The main title of the documentation page.
-   **Summary**: The introductory paragraph or summary.
-   **Sections**: The content is broken down into sections based on headings (H2, H3), preserving the document's structure.
-   **Code Examples**: All code blocks are extracted and stored separately.
-   **Metadata**: The source URL is stored as metadata for each item.

This structured approach ensures that the extracted data is clean, well-organized, and retains its original context.

### 3.2. Chunking

The chunking process (`chunking.py`) has been updated to leverage the structured data from the scraper and the API dump:

-   **API Data**: The API dump is processed to create individual `Document` objects for each class and each of its members (properties, methods, events). This creates highly granular and focused documents for each API element.
-   **Scraped Data**: The structured data from the scraper is used to create multiple `Document` objects from a single scraped page. Separate documents are created for the summary, each section, and each code example. This ensures that the resulting chunks are semantically coherent and contextually rich.
-   **Metadata**: Each `Document` is enriched with detailed metadata, including the source, title, section, class name, and member type. This metadata is crucial for filtering and retrieval.

### 3.3. Vector Database

The chunked and processed documents (nodes) are then upserted into a Qdrant vector database. The `BAAI/bge-small-en-v1.5` model is used to generate embeddings for each node.

## 4. Retrieval Strategy

The retrieval process (`retriever.py`) has been enhanced to improve the relevance of the retrieved documents:

-   **Increased Retrieval Pool**: The retriever now fetches a larger number of documents (`similarity_top_k=10`) from the vector database to create a wider pool of potential candidates.
-   **Re-ranking**: A local reranker (ColbertRerank) has been implemented as a post-processor in the query engine. This reranker takes the initially retrieved documents and re-orders them based on their relevance to the query, ensuring that the most accurate and contextually appropriate documents are returned without relying on external API keys.
-   **Metadata Filtering**: The detailed metadata attached to each document can be leveraged in the future to implement advanced filtering strategies, further improving retrieval precision.

These improvements to the data ingestion and retrieval pipeline result in a more robust and accurate RAG system, capable of providing higher quality and more relevant information for answering queries about the Roblox API.