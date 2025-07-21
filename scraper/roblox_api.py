import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL to fetch the latest Roblox client version GUID
VERSION_URL = "http://setup.roblox.com/versionQTStudio"
API_DUMP_URL_TEMPLATE = "http://setup.roblox.com/{version_guid}-API-Dump.json"

async def get_latest_api_dump_url():
    """
    Fetches the latest Roblox client version GUID and constructs the API dump URL.

    Returns:
        str: The URL for the latest API dump JSON file, or None if an error occurs.
    """
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Fetching latest version GUID from {VERSION_URL}")
            response = await client.get(VERSION_URL)
            response.raise_for_status()  # Raise an exception for bad status codes
            version_guid = response.text.strip()
            logger.info(f"Successfully fetched version GUID: {version_guid}")
            
            api_dump_url = API_DUMP_URL_TEMPLATE.format(version_guid=version_guid)
            logger.info(f"Constructed API dump URL: {api_dump_url}")
            return api_dump_url
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}: {e.response.text}")
    
    return None

async def fetch_api_dump(url: str):
    """
    Fetches and parses the JSON API dump from the given URL.

    Args:
        url: The URL of the API dump JSON file.

    Returns:
        dict: The parsed JSON data, or None if an error occurs.
    """
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Downloading API dump from {url}")
            # Increase the timeout to handle large file downloads
            response = await client.get(url, timeout=60.0)
            response.raise_for_status()
            logger.info("Successfully downloaded API dump.")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}: {e.response.text}")
    except Exception as e:
        logger.error(f"Failed to parse JSON from API dump: {e}")

    return None

if __name__ == "__main__":
    import asyncio

    async def main():
        latest_url = await get_latest_api_dump_url()
        if latest_url:
            print(f"Latest API Dump URL: {latest_url}")
            api_data = await fetch_api_dump(latest_url)
            if api_data:
                print(f"Successfully fetched and parsed API dump.")
                print(f"API Version: {api_data.get('Version')}")
                print(f"Found {len(api_data.get('Classes', []))} classes.")
        else:
            print("Failed to retrieve the latest API dump URL.")

    asyncio.run(main())