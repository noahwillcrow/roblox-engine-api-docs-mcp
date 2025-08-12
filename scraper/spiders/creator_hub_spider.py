import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup

class CreatorHubSpider(CrawlSpider):
    name = 'creator_hub'
    allowed_domains = ['create.roblox.com']
    start_urls = ['https://create.roblox.com/docs/reference/engine']

    # This rule allows the spider to follow internal links within the /docs path
    rules = (
        Rule(LinkExtractor(allow=r'/docs/reference/engine'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        """
        This function is called for each page crawled. It extracts structured
        content from the page and yields it as a dictionary.
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = soup.find('main')

        if main_content:
            title = main_content.find('h1').get_text(strip=True) if main_content.find('h1') else ''
            
            # Extracting a summary or introduction
            # This is a sample selector, it might need to be adjusted
            summary_p = main_content.find('p')
            summary = summary_p.get_text(strip=True) if summary_p else ''

            sections = []
            for header in main_content.find_all(['h2', 'h3']):
                section_title = header.get_text(strip=True)
                content = []
                for sibling in header.find_next_siblings():
                    if sibling.name in ['h2', 'h3']:
                        break
                    content.append(sibling.get_text(strip=True))
                sections.append({
                    "title": section_title,
                    "content": "\n".join(content)
                })

            code_examples = []
            for code_block in main_content.find_all('code'):
                code_examples.append(code_block.get_text(strip=True))

            yield {
                'source': response.url,
                'title': title,
                'summary': summary,
                'sections': sections,
                'code_examples': code_examples,
                'raw_content': main_content.prettify()
            }