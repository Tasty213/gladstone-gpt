# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from pathlib import Path
import re
from itemadapter.adapter import ItemAdapter
from scrapy import Spider
from scrapy.crawler import Crawler
from LibDemNews.items import BlogItem


class BlogPipeline:
    def __init__(self, output_folder):
        self.output_folder = output_folder

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        settings = crawler.settings
        return cls(settings.get("OUTPUT_FOLDER"))

    def open_spider(self, spider: Spider):
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)

    def process_item(self, item: BlogItem, spider):
        item_name = item.get("metadata").get("name")
        output_file_path = Path(
            f"{self.output_folder}/{self.get_valid_filename(item_name)}.json"
        )
        with open(output_file_path, "w+") as output_file:
            json.dump(
                ItemAdapter(item).asdict(),
                output_file,
                indent=4,
            )

    def get_valid_filename(self, name):
        s = str(name).strip().replace(" ", "_")
        s = re.sub(r"(?u)[^-\w.]", "", s)
        if s in {"", ".", ".."}:
            raise Exception("Could not derive file name from '%s'" % name)
        return s
