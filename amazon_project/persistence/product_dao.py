import pymongo

db_url = "mongodb+srv://hayfa23:0000@cluster0.nmxdi.mongodb.net/amazon_products?retryWrites=true&w=majority"


class ProductDAO:
    def __init__(self):
        self.client = pymongo.MongoClient(db_url)
        self.db = self.client.amazon_scrapping
        self.collection = self.db.products

    def save(self, item, reviews):
        product = self.collection.find_one({"_id": item['product_id']})
        if product:
            exist = False
            for element in product:
                if element == item['marketplace']:
                    exist = True
            if not exist:
                self.collection.update_one({"_id": item['product_id']},
                                           {"$addToSet":
                                                {item['marketplace'] + ".reviews":
                                                     {"$each": reviews}}})
        else:
            self.collection.insert_one(dict({"_id": item['product_id'],
                                             item['marketplace']: {"reviews": reviews, "active_sellers": 1}
                                             }))

    def get_all_products(self):
        cursor = self.collection.find({})
        result = []
        for record in cursor:
            result.append(record)
        return result

    def get_product_by_id(self, product_id):
        try:
            cursor = self.collection.find_one({"_id": product_id})
            if cursor:
                return cursor
            else:
                return {}
        except Exception:
            return {}

    def find_product_by_marketplace(self, product_id, marketplace):
        try:
            cursor = self.collection.find_one({"_id": product_id})
            if cursor:
                if cursor[marketplace]:
                    return True
            return False
        except Exception:
            return False

    def get_reviews_by_id_marketplace(self, product_id, product_marketplace):
        try:
            cursor = self.collection.find_one({"_id": product_id}, {'_id': False})
            if cursor:
                return cursor[product_marketplace]['reviews']
            return []
        except Exception:
            return []

    def get_marketplaces_by_id(self, product_id):
        try:
            cursor = self.collection.find_one({"_id": product_id}, {'_id': False})
            res = []
            for record in cursor:
                res.append(record)
                return res
            return res
        except Exception:
            return res

    def get_all_ids(self):
        cursor = self.collection.find({})
        result = []
        for record in cursor:
            result.append(record['_id'])
        return result

    def increment_number_sellers(self, product_id, marketplace):
        self.collection.update_one({"_id": product_id},
                               {"$inc": {marketplace + ".active_sellers": 1}})
