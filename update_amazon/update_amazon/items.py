# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UpdateAmazonItem(scrapy.Item):
    # define the fields for the review
    scraping_date = scrapy.Field()
    review_date = scrapy.Field()
    review_title = scrapy.Field()
    star_rating = scrapy.Field()
    comment = scrapy.Field()
    review_votes = scrapy.Field()
