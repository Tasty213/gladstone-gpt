# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BlogItem(scrapy.Item):
    content = scrapy.Field()
    metadata = scrapy.Field()


class MetadataItem(scrapy.Item):
    link = scrapy.Field()
    name = scrapy.Field()
    date = scrapy.Field()
    type = scrapy.Field()
