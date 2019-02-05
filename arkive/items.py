# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArkiveItem(scrapy.Item):
    id = scrapy.Field()
    index = scrapy.Field()
    videos_url = scrapy.Field()
    photos_url = scrapy.Field()
    videos_path = scrapy.Field()
    photos_path = scrapy.Field()
    video_count = scrapy.Field()
    photo_count = scrapy.Field()


