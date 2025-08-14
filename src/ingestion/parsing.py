from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain.docstore.document import Document
import re
import yaml

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
                return_type_data = member.get("ReturnType")
                if isinstance(return_type_data, list):
                    # If it's a list, join the names of the types
                    return_type = ", ".join([t.get("Name", "void") for t in return_type_data])
                else:
                    # Otherwise, treat it as a dictionary
                    return_type = return_type_data.get("Name", "void")
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
                # Handle tags which can be strings or dictionaries
                processed_tags = []
                for t in tags:
                    if isinstance(t, dict):
                        processed_tags.append(t.get('Name'))
                    elif isinstance(t, str):
                        processed_tags.append(t)
                    else:
                        raise TypeError("Unexpected type for tag: " + type(t))
                content_lines.append(f"Tags: {', '.join(filter(None, processed_tags))}")

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

def parse_yaml_documents(docs_path: Path) -> list[Document]:
    """
    Loads all YAML files from the 'reference/engine' subdirectories,
    extracts relevant content, and returns them as a list of Document objects.

    Args:
        docs_path: The path to the 'content/en-us' directory within the
                   cloned creator-docs repository.

    Returns:
        A list of Document objects from the YAML files.
    """
    print(f"Parsing YAML documents from: {docs_path}")
    documents = []

    reference_path = docs_path / "reference" / "engine"
    
    for sub_dir in ["classes", "datatypes", "libraries", "enums"]:
        current_path = reference_path / sub_dir
        if current_path.is_dir():
            for file_path in current_path.glob("*.yaml"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        
                        # Extract relevant information from YAML
                        name = data.get("name", file_path.stem)
                        doc_type = data.get("type", sub_dir[:-1]) # 'class', 'datatype', 'library', or 'enum'
                        summary = data.get("summary", "")
                        description = data.get("description", "")
                        
                        content_parts = [f"Name: {name}", f"Type: {doc_type}"]
                        if summary:
                            content_parts.append(f"Summary: {summary}")
                        if description:
                            content_parts.append(f"Description: {description}")

                        # Add properties, methods, functions, events, constructors, math_operations
                        for section in ["properties", "methods", "functions", "events", "constructors", "math_operations", "items"]:
                            if data.get(section):
                                content_parts.append(f"\n--- {section.capitalize()} ---")
                                for item in data[section]:
                                    item_name = item.get("name", "Unnamed")
                                    item_summary = item.get("summary", "")
                                    item_description = item.get("description", "")
                                    item_type = item.get("type", "")
                                    
                                    content_parts.append(f"{item_name} ({item_type}): {item_summary}")
                                    if item_description:
                                        content_parts.append(f"  {item_description}")
                                    
                                    if item.get("parameters"):
                                        params = ", ".join([f"{p.get('name')}: {p.get('type')}" for p in item["parameters"]])
                                        content_parts.append(f"  Parameters: ({params})")
                                    if item.get("returns"):
                                        returns = ", ".join([t.get('type') for t in item["returns"]])
                                        content_parts.append(f"  Returns: {returns}")

                        page_content = "\n".join(content_parts)
                        
                        metadata = {
                            "source": "creator_docs_yaml",
                            "file_path": str(file_path.relative_to(docs_path.parent.parent)),
                            "type": doc_type,
                            "name": name,
                            "summary": summary,
                            "inherits": data.get("inherits", []),
                            "tags": data.get("tags", []),
                            "deprecation_message": data.get("deprecation_message", ""),
                            "security": data.get("security", {}),
                            "thread_safety": data.get("thread_safety", ""),
                            "category": data.get("category", ""),
                            "serialization": data.get("serialization", {}),
                            "capabilities": data.get("capabilities", [])
                        }
                        documents.append(Document(page_content=page_content.strip(), metadata=metadata))
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML file {file_path}: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred while processing {file_path}: {e}")
        else:
            print(f"Warning: Directory not found at {current_path}")

    print(f"Parsed {len(documents)} documents from YAML files.")
    return documents

def extract_data_types_and_classes(creator_docs_path: Path) -> dict:
    """
    Extracts data types and classes from the creator docs reference directories.

    Args:
        creator_docs_path: The path to the 'content/en-us' directory within the
                           cloned creator-docs repository.

    Returns:
        A dictionary containing extracted data types and classes.
    """
    print("Extracting data types and classes from creator docs...")
    data_types = []
    classes = []

    # Paths to the reference directories
    reference_path = creator_docs_path / "reference" / "engine"
    classes_path = reference_path / "classes"
    datatypes_path = reference_path / "datatypes"

    # Extract class names
    if classes_path.is_dir():
        for file_path in classes_path.glob("*.yaml"):
            classes.append(file_path.stem)
    else:
        print(f"Warning: Classes directory not found at {classes_path}")

    # Extract data type names
    if datatypes_path.is_dir():
        for file_path in datatypes_path.glob("*.yaml"):
            data_types.append(file_path.stem)
    else:
        print(f"Warning: DataTypes directory not found at {datatypes_path}")

    print("Finished extracting data types and classes.")
    return {
        "data_types": sorted(list(set(data_types))), # Use set for uniqueness and sort for consistency
        "classes": sorted(list(set(classes)))
    }

    print("Finished extracting data types and classes.")
    return data_types_and_classes