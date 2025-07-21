# Knowledge Base for Roblox API RAG Agent

This document provides an overview of the data stored in the vector database that powers the Roblox API RAG Agent.

## 1. Purpose

The purpose of this knowledge base is to provide a comprehensive and up-to-date source of information about the Roblox API and Creator Hub. This data is used by the RAG (Retrieval-Augmented Generation) agent to answer questions and generate code related to Roblox development.

## 2. Data Sources

The knowledge base is built from two primary data sources:

1.  **Roblox JSON API Dump**: This is an official, structured dump of the Roblox API, providing detailed information about classes, methods, properties, and events.
2.  **Roblox Creator Hub**: The official documentation website for Roblox developers. This provides contextual information, tutorials, guides, and code examples.

## 3. Data Processing

The raw data from these sources is processed and chunked before being stored in the vector database.

### 3.1. Chunking Strategy

A **semantic chunking** strategy is used to split the documents into contextually coherent chunks. This is done using LlamaIndex's `SemanticSplitterNodeParser`, which helps to preserve the meaning and relationships within the source material.

### 3.2. Data Structure

Each chunk is stored as a vector in the Qdrant database, along with the following metadata:

*   **`source`**: The URL or origin of the document (e.g., "Roblox API Dump" or a specific Creator Hub URL).
*   **`content`**: The text content of the chunk.
*   **`metadata`**: A dictionary containing additional information, such as the class name for API dump entries.

This structured approach allows the RAG agent to retrieve relevant and context-rich information to assist with a wide range of development tasks.