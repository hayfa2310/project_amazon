from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

import logging
from flask import Flask, render_template, request, jsonify, render_template_string
from flask_executor import Executor
from services import new_seller_service
from services.products_reviews.update_product_service import UpdateService


app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_MAX_WORKERS'] = 5
app.config['EXECUTOR_PROPAGATE_EXCEPTIONS'] = True
executor = Executor(app)


@app.route('/')
def home_page():
    return render_template('index.html')


# After clicking the Submit Button, POST Request sent
@app.route('/add', methods=['POST'])
def submit():
    if request.method == 'POST':
        username = request.form['username']
        seller_id = request.form['sellerID']
        marketplaces = request.form.getlist('marketplace')

        response = new_seller_service.add_seller(seller_id, username, marketplaces)
        app.logger.info(response)

        if 'Sorry' not in response:
            executor.submit(add_seller_info, seller_id, marketplaces)
            return render_template("new_seller.html", name=username)
        else:
            return render_template("error.html")


@app.route('/update')
def update_products():
    update_service = UpdateService()
    response = update_service.update_all_products()
    return render_template('update.html', response=response)


def add_seller_info(seller_id, marketplaces):
    # Add list products for each marketplace
    for marketplace in marketplaces:
        # Scrapy crawler
        app.logger.info("Started collecting seller info relative to " + str(marketplace) + " marketplace")
        new_seller_service.add_list_products(seller_id, marketplace)

        # Selenium crawler
        app.logger.info("Saved seller's list of products from marketplace: " + str(marketplace))
        new_seller_service.crawl_feedback(seller_id, marketplace)
        app.logger.info("Saved seller feedback from marketplace: " + str(marketplace))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
