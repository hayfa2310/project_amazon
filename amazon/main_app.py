import crochet
from flask import Flask, jsonify, request, redirect, url_for
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from amazon.spiders.product_reviews import ProductReviewsSpider

crochet.setup()

# Creating Flask App Variable
app = Flask(__name__)

output_data = []
crawl_runner = CrawlerRunner(get_project_settings())

configure_logging()


# By Default Flask will come into this when we run the file
@app.route('/')
def index():
    return "Welcome to Amazon Scraping"


# After clicking the Submit Button FLASK will come into this
@app.route('/', methods=['POST'])
def submit():
    global baseURL

    if request.method == 'POST':
        global output_data
        output_data = []
        # Getting the Input Amazon Product Infos
        marketplace = request.json['marketplace']
        product_id = request.json['product_id']

        baseURL = 'https://www.amazon.' + marketplace + '/product-reviews/' + product_id

        scrape_with_crochet(baseURL=baseURL)  # Passing that URL to our Scraping Function
        return jsonify(output_data)  # Returns the scraped data


# Crochet layer, wrapping the method in a blocking call
@crochet.wait_for(timeout=3600.0)
def scrape_with_crochet(baseURL):
    # Connect to the dispatcher that will kind of loop the code between these two functions.
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)

    # This will connect to the ProductUpdateSpider function
    # in our scrapy file and after each yield will pass to the crawler_result function.
    eventual = crawl_runner.crawl(ProductReviewsSpider, url=baseURL)
    return eventual


# This will append the data to the output data list.
def _crawler_result(item, response, spider):
    if item is not None:
        output_data.append(dict(item))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
