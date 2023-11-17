import regex
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import request
from scrapy.http.response.html import HtmlResponse
from LibDemNews.items import BlogItem, MetadataItem


class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["libdems.org.uk"]
    start_urls = [
        "https://www.libdems.org.uk/news",
        "https://www.libdems.org.uk/press/",
    ]
    allow_whitelist = "libdems.org.uk/(news|press)/.*"
    extract_whitelist = (
        r"https://www\.libdems\.org\.uk/(news|press)/((adlib-)?articles?|release)/.*"
    )

    def __init__(self):
        self.html_path = "./out/html/"
        self.link_extractor = LinkExtractor(self.allow_whitelist)

    def parse(self, response: HtmlResponse):
        for link in self.link_extractor.extract_links(response):
            yield request.Request(link.url)

        paragraphs, heading = self.get_paragraphs_and_headings(response)

        if regex.match(self.extract_whitelist, response.url) and len(paragraphs) > 0:
            yield BlogItem(
                content=paragraphs,
                metadata=MetadataItem(
                    date=self.get_date(response),
                    link=response.url,
                    name=heading,
                    type="json",
                ),
            )

    def get_paragraphs_and_headings(self, response: HtmlResponse) -> (str, str):
        response.xpath("//footer").drop()
        response.xpath("//div[@id='tx_cookies']").drop()
        content = response.xpath(
            "/html/body/div/div[@class='page-layout']//text()"
        ).getall()
        content = regex.sub(r"\s+", " ", "\n".join(content))
        heading = response.xpath("//h1/text()").get()
        return content, heading

    def get_date(self, response: HtmlResponse):
        return response.xpath(
            "//div[@class='type-body-a ml-8 first:ml-0 sm:ml-8 sm:first:ml-0']/text()"
        ).get("")
