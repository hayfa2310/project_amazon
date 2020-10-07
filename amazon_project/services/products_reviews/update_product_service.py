from datetime import datetime
import requests
from flask import current_app
from persistence.product_dao import ProductDAO

# Global parameters
# To move in a settings' file
days_threshold = 2  # Do not scrap to update a product for a number of days less than the threshold
requests_threshold = 5
period_of_time = 20  # in milliseconds


def find_update_interval_minutes(reviews):
    reviews.sort(reverse=True, key=lambda r: r['scraping_date'])
    recent_scraping_date = datetime.strptime(reviews[0]['scraping_date'], '%Y-%m-%d %H:%M:%S.%f')
    return ((datetime.now() - recent_scraping_date).seconds % 3600) // 60


def find_update_interval_days(reviews):
    if reviews:
        reviews.sort(reverse=True, key=lambda r: r['scraping_date'])
        recent_scraping_date = datetime.strptime(reviews[0]['scraping_date'], '%Y-%m-%d %H:%M:%S.%f')
        return (datetime.now() - recent_scraping_date).days
    else:
        return 0


class UpdateService:

    def __init__(self, update_crawler_url="http://update_prod:5002/"):
        self.update_crawler_url = update_crawler_url
        self.persistence_service = ProductDAO()

    def get_list_products_to_update(self):
        list_products = []
        list_all_products = self.persistence_service.get_all_ids()
        for product_id in list_all_products:
            marketplaces = self.persistence_service.get_marketplaces_by_id(product_id)
            for marketplace in marketplaces:
                list_reviews = self.persistence_service.get_reviews_by_id_marketplace(product_id, marketplace)
                suggested_days = find_update_interval_days(list_reviews)
                if suggested_days > days_threshold:
                    days = suggested_days
                    data = {'marketplace': marketplace,
                            'product_id': product_id,
                            'days': days
                            }
                    list_products.append(data)
        sorted_list_products = sorted(list_products, key=lambda i: i['days'], reverse=True)
        return sorted_list_products

    def get_reviews_to_update(self, data):
        response = requests.post(self.update_crawler_url, json=data)
        return response.json()

    # This method updates all the products from the DB at once.
    # With a Big set of data,
    # possibility of implementing a method sending a fixed number of requests to update each time.
    def update_all_products(self):
        list_products = self.get_list_products_to_update()
        if list_products:
            for product in list_products:
                reviews = self.get_reviews_to_update(product)
                if len(reviews) > 0:
                    current_app.logger.info(str(datetime.now()) + " persisting "
                                            + str(len(reviews)) + " new reviews of the product " +
                                            str(product['product_id']) + " updated after " + str(
                                            product['days']) + " days")
                    self.persistence_service.save(product, reviews)
            return "Updated successfully " + str(len(list_products)) + " products"
        else:
            return "Now, there is 0 products to update."
