import httpx
import re

# This script is intended to be run by the CI/CD pipeline to get the
# latest Roblox version for tagging the Docker image.

VERSION_URL = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/roblox/version.txt"

def get_latest_roblox_version():
    """
    Fetches the latest Roblox version string from the Client Tracker repo.
    """
    try:
        response = httpx.get(VERSION_URL)
        response.raise_for_status()
        # The version is the first line of the file
        version = response.text.strip().split('\n')[0]
        # Sanitize the version to be a valid Docker tag
        sanitized_version = re.sub(r'[^a-zA-Z0-9_.-]', '_', version)
        return sanitized_version
    except Exception as e:
        print(f"Failed to fetch Roblox version: {e}")
        # Fallback to a generic tag if fetching fails
        return "unknown"

if __name__ == "__main__":
    version = get_latest_roblox_version()
    print(version)