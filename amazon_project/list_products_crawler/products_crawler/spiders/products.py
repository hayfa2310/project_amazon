import re
import time
import scrapy
from scrapy import Request
from ..items import ProductsItem


class ProductsSpider(scrapy.Spider):
    name = 'products'
    allowed_domains = ['amazon.com.br',
                       'amazon.ca',
                       'amazon.com.mx',
                       'amazon.com',
                       'amazon.cn',
                       'amazon.in',
                       'amazon.co.jp',
                       'amazon.sg',
                       'amazon.com.tr',
                       'amazon.ae',
                       'amazon.fr',
                       'amazon.de',
                       'amazon.it',
                       'amazon.nl',
                       'amazon.es',
                       'amazon.co.uk',
                       'amazon.com.au'
                       ]
    products_url_regex = '(https://)?(www.)?amazon.([A-z]{2,3})(.[A-z]{2,3})?/s\?me=([A-Z0-9]{14})??(.*)?'
    seller_id_regex = '(?:https://)?(?:www.)?amazon.(?:[A-z]{2,3})(?:.[A-z]{2,3})?/s\?me=([A-Z0-9]{14})??(?:.*)?'
    marketplace_regex = '(?:https://)?(?:www.)?amazon.([A-z]{2,3})?.?([A-z]{2,3})?/s\?me=(?:[A-Z0-9]{14})??(?:.*)?'

    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.marketplace = self.get_marketplace_from_url()
        self.page_number = 0

    def is_valid_review_url(self):
        return re.search(self.products_url_regex, self.url, re.IGNORECASE)

    def get_seller_id_from_url(self):
        seller_id = re.findall(self.seller_id_regex, self.url, re.IGNORECASE)
        if seller_id:
            return seller_id[0]
        else:
            self.logger.error('ASIN not found')

    def get_marketplace_from_url(self):
        marketplace = re.findall(self.marketplace_regex, self.url, re.IGNORECASE)
        if marketplace:
            if marketplace[0][1] == '':
                return marketplace[0][0]
            else:
                return marketplace[0][1]
        else:
            self.logger.error('Marketplace not listed')

    def start_requests(self):
        if self.is_valid_review_url():
            yield Request(self.url)
        else:
            self.logger.error('Not an amazon product\'s list url')

    def parse(self, response):
        product_ids = response.xpath('//*[@data-component-type="s-search-result"]/@data-asin').getall()
        average_ratings = response.xpath('//*[@class="a-section a-spacing-none a-spacing-top-micro"]//i/span/text()').getall()

        for product_id, average_rating in zip(product_ids, average_ratings):
            item = ProductsItem()
            item['asin'] = product_id
            item['average_rating'] = average_rating.split(' ')[0]
            yield item

        next_page = response.css('li.a-last a::attr(href)').get()

        if next_page:
            self.page_number += 1
            self.logger.info("Finished scraping list products page number " + str(self.page_number) + " >>>>> NEXT")
            time.sleep(5)
            yield response.follow(next_page, callback=self.parse)
