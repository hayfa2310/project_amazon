import crochet
from flask import current_app
from scrapy.signalmanager import dispatcher
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from feedback_scraper import SellerFeedbackScraper
from list_products_crawler.products_crawler.spiders.products import ProductsSpider
from persistence.seller_dao import SellerDAO
from services.products_reviews.new_product_service import NewProductService

crochet.setup()
output_data = []
crawl_runner = CrawlerRunner(get_project_settings())

seller_dao = SellerDAO()
new_product_service = NewProductService()


def add_seller(seller_id, username, marketplaces):
    return seller_dao.save(seller_id, username, marketplaces)


def add_list_products(seller_id, marketplace):
    base_url = 'https://www.amazon.' + marketplace + '/s?me=' + seller_id

    current_app.logger.info('Running Spider: Scrapping list of the products')
    scrape_with_crochet(base_url)  # Passing that URL to our Scraping Function
    current_app.logger.info(output_data)

    current_app.logger.info('Persisting ASINs of the products')
    response = persist_list_products(seller_id, marketplace, output_data)
    current_app.logger.info(response)

    # Calling the Amazon Scraper
    current_app.logger.info('Calling Scraping Amazon Products module')
    new_product_service.save_products(seller_id, marketplace)


# Crochet layer, wrapping the method in a blocking call
@crochet.wait_for(timeout=3600.0)
def scrape_with_crochet(base_url):
    # Connect to the dispatcher that will kind of loop the code between these two functions.
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    eventual = crawl_runner.crawl(ProductsSpider, url=base_url)
    return eventual


# Append the data to the output data list
def _crawler_result(item, response, spider):
    if item is not None:
        output_data.append(dict(item))


def crawl_feedback(seller_id, marketplace):
    current_app.logger.info('Running Selenium: Scrapping Feedback')
    seller_feedback_scraper = SellerFeedbackScraper()
    list_feedback = seller_feedback_scraper.scrape(seller_id, marketplace)

    if not list_feedback:
        current_app.logger.info('Exception detected while trying to scrape Feedback')
    seller_dao.save_feedback(seller_id, marketplace, list_feedback)


def persist_list_products(seller_id, marketplace, data):
    # Add the list of products of a given Marketplace to the respective Seller
    return seller_dao.save_list_products(seller_id, marketplace, data)

