import logging
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core import Document
from llama_index.embeddings.openai import OpenAIEmbedding

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_chunking_service():
    """
    Initializes and returns the SemanticSplitterNodeParser.
    """
    # This will require an OpenAI API key to be set in the environment
    embed_model = OpenAIEmbedding()
    
    splitter = SemanticSplitterNodeParser(
        buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
    )
    
    return splitter

def process_and_chunk_data(api_data: dict, scraped_items: list, splitter: SemanticSplitterNodeParser):
    """
    Processes the raw data from the API dump and Scrapy spider, and chunks it
    using the provided splitter.

    Args:
        api_data: The parsed JSON data from the Roblox API dump.
        scraped_items: A list of items scraped from the Creator Hub.
        splitter: The SemanticSplitterNodeParser instance.

    Returns:
        A list of chunked nodes.
    """
    documents = []

    # Process API data
    if api_data and 'Classes' in api_data:
        for class_data in api_data['Classes']:
            # For now, we'll just create a single document per class.
            # This can be improved to create more granular documents for members.
            doc_content = f"Class: {class_data['Name']}\n"
            doc_content += f"Superclass: {class_data.get('Superclass', 'None')}\n"
            
            documents.append(Document(
                text=doc_content,
                metadata={"source": "Roblox API Dump", "class_name": class_data['Name']}
            ))

    # Process scraped data
    for item in scraped_items:
        documents.append(Document(
            text=item['content'],
            metadata={"source": item['source']}
        ))

    logger.info(f"Processing {len(documents)} documents for chunking.")
    
    nodes = splitter.get_nodes_from_documents(documents)
    
    logger.info(f"Successfully chunked documents into {len(nodes)} nodes.")
    
    return nodes