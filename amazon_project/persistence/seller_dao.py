from datetime import datetime
import pymongo

db_url = "mongodb+srv://hayfa23:0000@cluster0.nmxdi.mongodb.net/amazon_products?retryWrites=true&w=majority"


class SellerDAO:
    def __init__(self):
        self.client = pymongo.MongoClient(db_url)
        self.db = self.client.amazon_scrapping
        self.collection = self.db.sellers

    def save(self, seller_id, username, marketplaces):
        seller = self.collection.find_one({"_id": seller_id})
        if not seller:
            self.collection.insert(dict({"_id": seller_id,
                                         "username": username,
                                         "date_creation": str(datetime.now().date()),
                                         "marketplaces": list(marketplaces)}))
            return "Saved Successfully " + username
        else:
            if not [value for value in marketplaces if value in seller['marketplaces']]:
                self.collection.update_one({"_id": seller_id},
                                           {"$push":
                                                {"marketplaces": {"$each":marketplaces}}})
                return "Seller already exists but added new marketplace(s)"
            else:
                return "Sorry Seller relative to these marketplaces already exists. Please recheck!"

    def save_list_products(self, seller_id, marketplace, products):
        seller = self.collection.find_one({"_id": seller_id})
        if seller:
            self.collection.update_one({"_id": seller_id},
                                       {"$addToSet":
                                            {"products." + marketplace: {"$each": products}}})
            return "Saved Successfully list products"
        else:
            return "Warning: Seller doesn't exist"

    def save_feedback(self, seller_id, marketplace, list_feedback):
        seller = self.collection.find_one({"_id": seller_id})
        if seller:
            self.collection.update_one({"_id": seller_id},
                                       {"$addToSet":
                                            {"feedback." + marketplace: {"$each": list_feedback}}})
        else:
            pass

    def find_all_sellers(self):
        cursor = self.collection.find({})
        result = []
        for record in cursor:
            result.append(record['_id'])
        return result

    def find_seller_by_id(self, seller_id):
        try:
            cursor = self.collection.find_one({"_id": seller_id})
            if cursor:
                return cursor
            else:
                return {}
        except Exception:
            return {}

    def get_seller_marketplaces(self, seller_id):
        cursor = self.collection.find_one({"_id": seller_id})
        if cursor:
            return cursor['marketplaces']

    def get_list_products(self, seller_id, marketplace):
        cursor = self.collection.find_one({"_id": seller_id})
        try:
            products = cursor['products'][marketplace]
            result = []
            for product in products:
                result.append(product['asin'])
            return result
        except KeyError:
            return []
