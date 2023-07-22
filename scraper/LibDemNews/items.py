# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BlogItem(scrapy.Item):
    link = scrapy.Field()
    name = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    type = scrapy.Field()
