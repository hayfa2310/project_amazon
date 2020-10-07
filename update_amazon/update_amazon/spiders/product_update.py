# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy import Request
from ..items import UpdateAmazonItem
from dateparser.search import search_dates
import datetime

# custom_settings = {'FEED_URI': 'tutorial/outputfile.json', 'CLOSESPIDER_TIMEOUT': 15}
# This will tell scrapy to store the scraped data to outputfile.json and for how long the spider should run.


class ProductUpdateSpider(scrapy.Spider):
    name = 'product_update'
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
    review_url_regex = '(https://)?(www.)?amazon.([A-z]{2,3})(.[A-z]{2,3})?/product-reviews/[A-z0-9]{10}/?(.*)?'
    asin_regex = '(?:https://)?(?:www.)?amazon.(?:[A-z]{2,3})(?:.[A-z]{2,3})?/product-reviews/([A-z0-9]{10})/?(?:.*)?'
    marketplace_regex = '(?:https://)?(?:www.)?amazon.([A-z]{2,3})(?:.([A-z]{2,3}))?/product-reviews/(?:[A-z0-9]{10})/?(?:.*)?'

    def __init__(self, url, days=6, **kwargs):
        super().__init__(**kwargs)
        self.url = url + "?&sortBy=recent"
        try:
            self.days = int(days)
        except ValueError:
            self.days = 6
        self.asin = self.get_asin_from_url()
        self.marketplace = self.get_marketplace_from_url()
        self.product_reviews = []
        self.nb_reviews_scrapped = 0

    def is_valid_review_url(self):
        return re.search(self.review_url_regex, self.url, re.IGNORECASE)

    def get_asin_from_url(self):
        asin = re.findall(self.asin_regex, self.url, re.IGNORECASE)
        if asin:
            return asin[0]
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
            self.logger.error('Marketplace not found')

    def start_requests(self):
        if self.is_valid_review_url():
            yield Request(self.url)
        else:
            self.logger.error('Not an amazon product review url')

    def is_recent(self, review_date):
        # if the review is less than 6 days old
        today = datetime.date.today()
        return (today - review_date.date()).days <= self.days

    def parse(self, response):
        self.logger.info('Proxy ip address is %s', response.headers['X-Crawlera-Slave'])

        if 'CAPTCHA' in response.xpath("//title/text()").extract():
            self.logger.info("Warning Captcha detected !")
        else:
            reviews_titles = response.xpath('//a[@class="a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold"]/span/text()').extract()
            star_ratings = response.xpath('//div[@id="cm_cr-review_list"]//span[@class="a-icon-alt"]/text()').extract()
            reviews_dates = response.xpath('//div[@id="cm_cr-review_list"]//span[@data-hook="review-date"]/text()').extract()
            comments = response.xpath('//span[@data-hook="review-body"][not(parent::*[@class="cr-translated-review-content aok-hidden"])]')
            reviews_votes = response.xpath('//span[@class="a-size-base a-color-tertiary cr-vote-text"]/text()').extract()
            old_review = False

            for i in range(len(reviews_titles)):
                scraping_date = str(datetime.datetime.now())

                if i < len(reviews_dates):
                    review_date = search_dates(reviews_dates[i], settings={'TIMEZONE': 'UTC'})[0][1]
                    if self.is_recent(review_date) or self.days == 0:
                        review_date = str(review_date)
                        old_review = False
                    else:
                        old_review = True
                else:
                    # date not specified
                    review_date = ''
                    old_review = True

                review_title = reviews_titles[i]
                review_comment = ' '.join(comments[i].xpath('string(.)').get().replace('\n', '').split())

                if i < len(star_ratings):
                    star_rating = star_ratings[i][:3]
                else:
                    star_rating = ''

                if i < len(reviews_votes):
                    review_votes = reviews_votes[i]
                else:
                    review_votes = ''

                if not old_review:
                    product_review = UpdateAmazonItem()
                    product_review['scraping_date'] = scraping_date
                    product_review['review_title'] = review_title
                    product_review['comment'] = review_comment
                    product_review['star_rating'] = star_rating
                    product_review['review_date'] = review_date
                    product_review['review_votes'] = review_votes
                    yield product_review

            if not old_review:
                next_page = response.css('li.a-last a::attr(href)').get()
                if next_page:
                    yield response.follow(next_page, callback=self.parse)
