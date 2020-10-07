import scrapy
from scrapy import Request
from ..items import AmazonItem
from dateparser.search import search_dates
import datetime
import re


class ProductReviewsSpider(scrapy.Spider):
    name = 'product_reviews'
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
    review_url_regex = '(https://)?(www.)?amazon.([A-z]{2,3})(.[A-z]{2,3})?/?(.*)?/product-reviews/[A-z0-9]{10}/?(.*)?'
    asin_regex = '(?:https://)?(?:www.)?amazon.(?:[A-z]{2,3})(?:.[A-z]{2,3})?/?(?:.*)?/product-reviews/([A-z0-9]{10})/?(?:.*)?'
    marketplace_regex = '(?:https://)?(?:www.)?amazon.([A-z]{2,3})?.?([A-z]{2,3})?/?(?:.*)?/product-reviews/(?:[A-z0-9]{10})/?(?:.*)?'

    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.asin = self.get_asin_from_url()
        self.marketplace = self.get_marketplace_from_url()

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
            self.logger.error('Marketplace not listed')

    def start_requests(self):
        if self.is_valid_review_url():
            yield Request(self.url)
        else:
            self.logger.error('Not an amazon product review url')

    # def get_number_total_reviews(self, response):
    #     list_total_reviews = response.xpath('//span[@data-hook="cr-filter-info-review-count"]/text()').extract()
    #     string_total_reviews = list_total_reviews[0].replace(u'\xa0', u' ')
    #     total_reviews = [int(s) for s in string_total_reviews.split() if s.isdigit()][-1]
    #     return total_reviews

    def parse(self, response):
        self.logger.info('User Agent : ' + str(response.request.headers['User-Agent']))
        self.logger.info('Proxy ip address is ' + str(response.headers['X-Crawlera-Slave']))

        reviews_titles = response.xpath('//a[@class="a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold"]/span/text()').extract()
        star_ratings = response.xpath('//div[@id="cm_cr-review_list"]//span[@class="a-icon-alt"]/text()').extract()
        reviews_dates = response.xpath('//div[@id="cm_cr-review_list"]//span[@data-hook="review-date"]/text()').extract()
        comments = response.xpath('//span[@data-hook="review-body"][not(parent::*[@class="cr-translated-review-content aok-hidden"])]')
        reviews_votes = response.xpath('//span[@class="a-size-base a-color-tertiary cr-vote-text"]/text()').extract()

        if reviews_titles:

            for i in range(len(reviews_titles)):
                product_review = AmazonItem()

                product_review['scraping_date'] = str(datetime.datetime.now())

                if i < len(reviews_dates):
                    product_review['review_date'] = str(search_dates(reviews_dates[i], settings={'TIMEZONE': 'UTC'})[0][1])
                else:
                    product_review['review_date'] = ''

                product_review['review_title'] = reviews_titles[i]
                product_review['comment'] = ' '.join(comments[i].xpath('string(.)').get().replace('\n', '').split())

                if i < len(star_ratings):
                    product_review['star_rating'] = star_ratings[i][:3]
                else:
                    product_review['star_rating'] = ''

                if i < len(reviews_votes):
                    product_review['review_votes'] = reviews_votes[i]
                else:
                    product_review['review_votes'] = ''

                yield product_review

            next_page = response.css('li.a-last a::attr(href)').get()

            if next_page:
                yield response.follow(next_page, callback=self.parse)

        else:
            self.logger.warning(" No Reviews on this page or Blocked with Captcha")
