import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import request
from scrapy.http.response.html import HtmlResponse
import justext
from LibDemNews.items import BlogItem
import dateparser


class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["libdems.org.uk"]
    start_urls = ["https://www.libdems.org.uk/news"]
    allow_whitelist = "libdems.org.uk/news/.*"
    extract_whitelist = r"https://www\.libdems\.org\.uk/news/(adlib-)?articles?/.*"

    def __init__(self):
        self.html_path = "./out/html/"
        self.link_extractor = LinkExtractor(self.allow_whitelist)

    def parse(self, response: HtmlResponse):
        for link in self.link_extractor.extract_links(response):
            yield request.Request(link.url)

        paragraphs, heading = self.get_paragraphs_and_headings(response)

        yield BlogItem(
            content="\n".join(paragraphs),
            date=self.get_date(response),
            link=response.url,
            name=heading,
            type="json",
        )

    def get_paragraphs_and_headings(self, response: HtmlResponse):
        all_content = justext.justext(response.text, justext.get_stoplist("English"))
        non_boilerplate = filter(lambda x: not (x.is_boilerplate), all_content)
        paragraphs = map(lambda x: x.text, non_boilerplate)
        heading = next(content.text for content in non_boilerplate if content.heading)
        return paragraphs, heading

    def get_date(self, response: HtmlResponse):
        return response.xpath(
            "//div[@class='type-body-a ml-8 first:ml-0 sm:ml-8 sm:first:ml-0']/text()"
        ).get("")