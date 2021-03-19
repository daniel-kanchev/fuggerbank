import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from fuggerbank.items import Article


class FuggerbankSpider(scrapy.Spider):
    name = 'fuggerbank'
    start_urls = ['https://www.fuggerbank.de/aktuelles/']

    def parse(self, response):
        links = response.xpath('//h2/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('(//a[@class="prev-next hidden-phone"]/@href)[last()]').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//meta[@property="article:published_time"]/@content').get()[:10]
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="entry-content content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
