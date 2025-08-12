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
            class_name = class_data['Name']
            # Create a document for the class itself
            class_content = f"Class: {class_name}\nSuperclass: {class_data.get('Superclass', 'None')}"
            documents.append(Document(
                text=class_content,
                metadata={"source": "Roblox API Dump", "type": "Class", "class_name": class_name}
            ))
            
            # Create documents for each member of the class
            for member in class_data.get('Members', []):
                member_name = member['Name']
                member_type = member['MemberType']
                doc_content = f"{member_type}: {class_name}.{member_name}\n"
                # Potentially add more details here in the future
                
                documents.append(Document(
                    text=doc_content,
                    metadata={
                        "source": "Roblox API Dump",
                        "type": member_type,
                        "class_name": class_name,
                        "member_name": member_name
                    }
                ))

    # Process scraped data
    for item in scraped_items:
        source = item['source']
        title = item['title']
        
        # Document for the summary
        if item['summary']:
            documents.append(Document(
                text=f"Title: {title}\n\n{item['summary']}",
                metadata={"source": source, "title": title, "section": "Summary"}
            ))
            
        # Documents for each section
        for section in item['sections']:
            section_title = section['title']
            section_content = section['content']
            if section_content:
                documents.append(Document(
                    text=f"Title: {title}\nSection: {section_title}\n\n{section_content}",
                    metadata={"source": source, "title": title, "section": section_title}
                ))

        # Documents for each code example
        for i, code in enumerate(item['code_examples']):
            if code:
                documents.append(Document(
                    text=f"Title: {title}\nCode Example {i+1}\n\n```\n{code}\n```",
                    metadata={"source": source, "title": title, "section": f"Code Example {i+1}"}
                ))

    logger.info(f"Processing {len(documents)} documents for chunking.")
    
    if not documents:
        logger.warning("No documents were created for chunking. The scraper might not have found any content.")
        return []
        
    nodes = splitter.get_nodes_from_documents(documents)
    
    logger.info(f"Successfully chunked documents into {len(nodes)} nodes.")
    
    return nodes