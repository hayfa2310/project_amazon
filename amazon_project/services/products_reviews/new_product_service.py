from datetime import datetime
import pymongo
import requests
from flask import current_app
from persistence.product_dao import ProductDAO
from persistence.seller_dao import SellerDAO


class NewProductService:

    def __init__(self, crawler_url="http://new_prod:5001/"):
        self.crawler_url = crawler_url
        try:
            self.product_dao = ProductDAO()
            self.seller_dao = SellerDAO()
        except pymongo.errors.ConfigurationError as err:
            current_app.logger.error(datetime.now() + str(err))

    def new_list_products(self, seller_id, marketplace):
        data = []
        list_products = self.seller_dao.get_list_products(seller_id, marketplace)
        if list_products:
            for asin in list_products:
                if self.product_dao.find_product_by_marketplace(asin, marketplace):
                    self.product_dao.increment_number_sellers(asin, marketplace)
                else:
                    data.append({"marketplace": marketplace, "product_id": asin})
        return data

    def get_reviews_to_save(self, data):
        try:
            response = requests.post(self.crawler_url, json=data)
            response.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as error:
            return "Error: " + str(error)
        return response.json()

    def save_products(self, seller_id, marketplace):
        list_products = self.new_list_products(seller_id, marketplace)
        if list_products:
            current_app.logger.info(str(datetime.now()) +
                                    " Retrieved data to scrap: " + str(len(list_products)) + " product")
            for data in list_products:
                current_app.logger.info(str(datetime.now()) + " SCRAPPING product reviews " + str(data['product_id']))
                reviews = self.get_reviews_to_save(data)
                if "Error" in reviews:
                    current_app.logger.info(str(datetime.now()) +
                                            " Failed to get product reviews " + str(data['product_id']))
                    current_app.logger.error(reviews)
                else:
                    # send to Persistence service to update DB (reviews + product_data)
                    current_app.logger.info(str(datetime.now()) + "Persisting " + str(len(reviews)) +
                                            " reviews of the product " + str(data['product_id']))
                    self.product_dao.save(data, reviews)
        else:
            current_app.logger.info(str(datetime.now()) + " 0 new products to scrap")
