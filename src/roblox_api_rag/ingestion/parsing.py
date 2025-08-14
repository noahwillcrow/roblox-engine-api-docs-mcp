from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain.docstore.document import Document
import re

# --- Constants ---
UNWANTED_PATTERNS = [
    re.compile(r'---\n(.*?)\n---', re.DOTALL),  # YAML frontmatter
    re.compile(r'<figure>(.*?)</figure>', re.DOTALL),  # Figures with videos/images
    re.compile(r'\{\s*?\"(.*?)\"\s*?\}', re.DOTALL),    # JSON-like blocks
]

# --- Public Functions ---

def parse_api_dump(api_dump_data: dict) -> list[Document]:
    """
    Parses the JSON API dump into a list of Document objects.

    Each API member (Property, Function, Event, Callback) becomes a
    separate Document with structured metadata.

    Args:
        api_dump_data: The raw dictionary from Full-API-Dump.json.

    Returns:
        A list of Document objects, ready for chunking and embedding.
    """
    print("Parsing API dump...")
    documents = []
    
    for class_data in api_dump_data.get("Classes", []):
        class_name = class_data.get("Name")
        
        for member in class_data.get("Members", []):
            member_type = member.get("MemberType")
            member_name = member.get("Name")
            
            # Basic content
            content_lines = [f"Class: {class_name}", f"{member_type}: {member_name}"]
            
            # Add details based on member type
            if member_type in ["Function", "Callback"]:
                # Handle parameters
                params = member.get("Parameters", [])
                if params:
                    param_str = ", ".join([f"{p.get('Name')}: {p.get('Type', {}).get('Name', 'void')}" for p in params])
                    content_lines.append(f"Parameters: ({param_str})")
                else:
                    content_lines.append("Parameters: ()")
                # Handle return type
                return_type = member.get("ReturnType", {}).get("Name", "void")
                content_lines.append(f"Returns: {return_type}")

            elif member_type == "Property":
                prop_type = member.get("ValueType", {}).get("Name", "unknown")
                content_lines.append(f"Type: {prop_type}")

            elif member_type == "Event":
                params = member.get("Parameters", [])
                if params:
                    param_str = ", ".join([f"{p.get('Name')}: {p.get('Type', {}).get('Name', 'void')}" for p in params])
                    content_lines.append(f"Fires with: ({param_str})")
                else:
                    content_lines.append("Fires with: ()")

            # Add security and tags if they exist
            security = member.get("Security")
            if security:
                content_lines.append(f"Security: {security}")
            
            tags = member.get("Tags")
            if tags:
                content_lines.append(f"Tags: {', '.join([t.get('Name') for t in tags])}")

            page_content = "\n".join(content_lines)
            
            metadata = {
                "source": "api_dump",
                "class_name": class_name,
                "member_name": member_name,
                "member_type": member_type,
                "tags": tags or []
            }
            
            documents.append(Document(page_content=page_content, metadata=metadata))
            
    print(f"Parsed {len(documents)} documents from API dump.")
    return documents

def parse_markdown_documents(docs_path: Path) -> list[Document]:
    """
    Loads all markdown files from a directory, cleans their content,
    and returns them as a list of Document objects.

    Args:
        docs_path: The path to the directory containing markdown files
                   (e.g., the 'content/en-us' directory).

    Returns:
        A list of Document objects from the markdown files.
    """
    print(f"Parsing markdown documents from: {docs_path}")
    
    loader = DirectoryLoader(
        str(docs_path),
        glob="**/*.md",
        show_progress=True,
        use_multithreading=True,
        silent_errors=True
    )
    
    documents = loader.load()
    
    cleaned_docs = []
    for doc in documents:
        # Clean the content
        cleaned_content = doc.page_content
        for pattern in UNWANTED_PATTERNS:
            cleaned_content = pattern.sub('', cleaned_content)
        
        # Update metadata
        doc.metadata["source"] = "creator_docs"
        doc.page_content = cleaned_content.strip()
        
        if doc.page_content:  # Only add documents that still have content
            cleaned_docs.append(doc)
            
    print(f"Parsed and cleaned {len(cleaned_docs)} markdown documents.")
    return cleaned_docs

if __name__ == '__main__':
    # This block is for testing the parsing functions independently.
    # It requires local copies of the data sources.
    print("--- Testing Parsing Functions ---")

    # Note: To run this test, you need to manually place
    # 'Full-API-Dump.json' and the 'creator-docs' repo content
    # in a 'temp_data' directory.

    temp_data_path = Path("./temp_data")
    api_dump_file = temp_data_path / "Full-API-Dump.json"
    creator_docs_folder = temp_data_path / "creator-docs" / "content" / "en-us"

    if not temp_data_path.exists():
        print("\nSkipping tests. Create a 'temp_data' directory with test files to run.")
    else:
        # Test API Dump Parsing
        if api_dump_file.exists():
            import json
            with open(api_dump_file, 'r') as f:
                test_api_dump = json.load(f)
            api_docs = parse_api_dump(test_api_dump)
            print(f"Sample API doc:\n{api_docs[150].page_content}\nMetadata: {api_docs[150].metadata}")
        else:
            print("\nSkipping API dump parsing test: 'Full-API-Dump.json' not found.")

        print("\n" + "="*20 + "\n")

        # Test Markdown Parsing
        if creator_docs_folder.exists():
            md_docs = parse_markdown_documents(creator_docs_folder)
            print(f"Sample MD doc path: {md_docs[50].metadata.get('source')}")
            print(f"Sample MD doc content snippet:\n---\n{md_docs[50].page_content[:300]}...\n---")
        else:
            print("\nSkipping markdown parsing test: 'creator-docs' content not found.")