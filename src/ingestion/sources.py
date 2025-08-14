import httpx
import subprocess
import tempfile
import os
import json
from pathlib import Path

# --- Constants ---
API_DUMP_URL = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/roblox/Full-API-Dump.json"
CREATOR_DOCS_REPO_URL = "https://github.com/Roblox/creator-docs.git"
CREATOR_DOCS_SUBDIR = "content/en-us"

# --- Public Functions ---

def get_api_dump() -> dict:
    """
    Fetches the Full-API-Dump.json from the Roblox-Client-Tracker repository.

    Returns:
        A dictionary containing the parsed JSON data of the API dump.
    """
    print(f"Fetching API dump from {API_DUMP_URL}...")
    try:
        response = httpx.get(API_DUMP_URL, timeout=30.0)
        response.raise_for_status()  # Raise an exception for bad status codes
        print("API dump fetched successfully.")
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        raise
    except httx.RequestError as e:
        print(f"An error occurred while requesting the API dump: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from API dump: {e}")
        raise

def get_creator_docs_path() -> Path:
    """
    Clones the creator-docs repository into a temporary directory and returns the
    path to the relevant content subdirectory.

    Returns:
        A Path object pointing to the 'content/en-us' directory within the
        cloned repository.
    """
    temp_dir = tempfile.mkdtemp(prefix="creator-docs-")
    print(f"Cloning creator-docs repository into temporary directory: {temp_dir}...")

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", CREATOR_DOCS_REPO_URL, temp_dir],
            check=True,
            capture_output=True,
            text=True
        )
        print("Creator-docs repository cloned successfully.")
        
        docs_path = Path(temp_dir) / CREATOR_DOCS_SUBDIR
        if not docs_path.is_dir():
            raise FileNotFoundError(f"Could not find expected content directory: {docs_path}")
            
        return docs_path
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone creator-docs repository.")
        print(f"Stderr: {e.stderr}")
        raise
    except FileNotFoundError as e:
        # Clean up the temp directory if the subdir isn't found
        # shutil.rmtree(temp_dir)
        raise

if __name__ == '__main__':
    # Example usage and basic testing
    print("--- Testing Data Sources ---")
    
    # Test API Dump Fetch
    try:
        api_dump_data = get_api_dump()
        print(f"Successfully fetched API dump. Found {len(api_dump_data.get('Classes', []))} classes.")
    except Exception as e:
        print(f"Error fetching API dump: {e}")

    print("\n" + "="*20 + "\n")

    # Test Creator Docs Clone
    docs_path = None
    try:
        docs_path = get_creator_docs_path()
        print(f"Successfully cloned creator-docs. Content path: {docs_path}")
        # Count markdown files
        md_files = list(docs_path.glob("**/*.md"))
        print(f"Found {len(md_files)} markdown files in the content directory.")
    except Exception as e:
        print(f"Error cloning creator-docs: {e}")
    finally:
        # Clean up the temporary directory
        if docs_path:
            # The actual directory to remove is the parent of the returned path
            import shutil
            shutil.rmtree(docs_path.parent.parent)
            print(f"Cleaned up temporary directory: {docs_path.parent.parent}")
