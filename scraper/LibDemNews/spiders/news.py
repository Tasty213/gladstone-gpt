import json
import re
import scrapy
import justext
from scrapy.linkextractors import LinkExtractor
from scrapy.http import request
from scrapy.http.response.html import HtmlResponse
import dateparser

class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["libdems.org.uk"]
    start_urls = ["https://www.libdems.org.uk/news"]
    allow_whitelist = "libdems.org.uk/news/.*"
    extract_whitelist = r"https://www\.libdems\.org\.uk/news/(adlib-)?articles?/.*"

    def __init__(self):
        self.html_path = './out/html/'
        self.link_extractor = LinkExtractor(self.allow_whitelist)

    def parse(self, response: HtmlResponse):
        if re.match(self.extract_whitelist, response.url):
            parsed_content = justext.justext(response.text, justext.get_stoplist("English"))
            paragraphs = [content.text for content in parsed_content if not(content.is_boilerplate)] 
            main_heading = [content.text for content in parsed_content if content.heading and not(content.is_boilerplate)][0]
            date_posted_raw = response.xpath("//div[@class='type-body-a ml-8 first:ml-0 sm:ml-8 sm:first:ml-0']").get()
            
            if isinstance(date_posted_raw, str):
                date = dateparser.parse(date_posted_raw)
            else: 
                date = ""
            
            with open(f"{self.html_path}{self.get_valid_filename(main_heading)}.json", 'w+') as html_file:
                json.dump({
                    "link": response.url,
                    "name": main_heading,
                    "author": "Liberal Democrats",
                    "date": str(date),
                    "content":"\n".join(paragraphs),
                    "type":"json"
                }, html_file, indent=4)

        for link in self.link_extractor.extract_links(response):
            yield request.Request(link.url)
        
    def get_valid_filename(self, name):
        s = str(name).strip().replace(" ", "_")
        s = re.sub(r"(?u)[^-\w.]", "", s)
        if s in {"", ".", ".."}:
            raise Exception("Could not derive file name from '%s'" % name)
        return s