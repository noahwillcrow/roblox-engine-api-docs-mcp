import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class CreatorHubSpider(CrawlSpider):
    name = 'creator_hub'
    allowed_domains = ['create.roblox.com']
    start_urls = ['https://create.roblox.com/docs']

    # This rule allows the spider to follow internal links within the /docs path
    rules = (
        Rule(LinkExtractor(allow=r'/docs/'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        """
        This function is called for each page crawled. It extracts the main content
        of the page and yields it as a dictionary.
        """
        # The main content is typically within a <main> tag
        main_content = response.css('main').get()
        
        if main_content:
            yield {
                'source': response.url,
                'content': main_content
            }