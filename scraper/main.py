import asyncio
import logging
import sys
import argparse
import crochet
from roblox_api import get_latest_api_dump_url, fetch_api_dump
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from spiders.creator_hub_spider import CreatorHubSpider
from chunking import get_chunking_service, process_and_chunk_data
from vector_db import upsert_nodes_to_qdrant
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from twisted.internet import asyncioreactor
asyncioreactor.install()

# Set up crochet to run Scrapy in a separate thread
crochet.setup()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@crochet.run_in_reactor
def run_spider_in_thread():
    """
    Runs the Scrapy spider in a separate thread using crochet.
    Returns a crochet EventualResult which will hold the list of items.
    """
    runner = CrawlerRunner(get_project_settings())
    
    scraped_items = []

    def item_scraped(item, response, spider):
        scraped_items.append(item)

    crawler = runner.create_crawler(CreatorHubSpider)
    crawler.signals.connect(item_scraped, signal=scrapy.signals.item_scraped)
    
    d = runner.crawl(crawler)
    d.addCallback(lambda _: scraped_items)
    return d

async def main():
    """
    Main function to run the scraper pipeline.
    """
    logger.info("Starting scraper pipeline...")

    # 1. Fetch the latest API dump URL
    api_dump_url = await get_latest_api_dump_url()
    if not api_dump_url:
        logger.error("Failed to get API dump URL. Exiting.")
        return

    # 2. Fetch the API dump data
    api_data = await fetch_api_dump(api_dump_url)
    if not api_data:
        logger.error("Failed to fetch API dump data. Exiting.")
        return

    logger.info("Successfully fetched API data.")
    
    # Run the Scrapy spider and wait for the result
    logger.info("Starting Creator Hub spider...")
    eventual_result = run_spider_in_thread()
    # Set a timeout for the spider to prevent it from running indefinitely
    scraped_items = eventual_result.wait(timeout=300.0)
    logger.info(f"Scraped {len(scraped_items)} items from the Creator Hub.")

    # 3. Process and chunk the data
    chunking_service = get_chunking_service()
    nodes = process_and_chunk_data(api_data, scraped_items, chunking_service)
    
    # 4. Upsert vectors to Qdrant
    upsert_nodes_to_qdrant(nodes)

    logger.info("Scraper pipeline finished.")

async def run_scheduler():
    """
    Initializes and starts the scheduler.
    """
    scheduler = AsyncIOScheduler()
    # Schedule the main function to run every day
    scheduler.add_job(main, 'interval', days=1, misfire_grace_time=60*60)
    
    # Start the scheduler
    scheduler.start()
    
    logger.info("Scheduler started. Press Ctrl+C to exit.")

    # Keep the script running
    try:
        while True:
            await asyncio.sleep(1000)
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Roblox API Scraper")
    parser.add_argument("--run-now", action="store_true", help="Run the scraper immediately instead of starting the scheduler.")
    args = parser.parse_args()

    if args.run_now:
        asyncio.run(main())
    else:
        asyncio.run(run_scheduler())