# Amazon Scraper Updating Product

The objective of this project is to retrieve the new reviews of an Amazon product given a number of days through scrapping. The data extracted by the Scraper can be fetched by accessing the endpoints given by the Flask RESTful API.

## Amazon Marketplace
In this project, the allowed domains from the existing marketplaces offered by Amazon are 17 marketplaces.

```
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
 ````
 
## Amazon Reviews
The Amazon Scraper retrieves all the Reviews of a specific product identified with his *ASIN* (Amazon Standard Identification Numbers, a 10 caracters ID) and a specific marketplace from the list of the *allowed_domains*. The information collected includes:
1. review date
2. review title
3. star rating out of 5
4. text of the **comment** 
5. **review votes** telling how many people found this review useful

Concerning the Scrapped review date, we used a "parse" function which extracts the date from the string mentionned in Amazon (could be in different languages according to the marketplace) then returns it as *datetime*. The function used is in the **dateparser package**.

```
from dateparser.search import search_dates
search_dates("Commenté en France le 7 mars 2019", settings= {'TIMEZONE': 'UTC'})
> datetime.datetime(2019, 3, 7, 0, 0)
````

## Framework Scrapy
Scrapy is a fast high-level web crawling and web scraping framework, used to crawl websites and extract structured data from their pages. We've implemented a Spider which is a  classe defining how an Amazon product review page will be scraped, including how to perform the crawl (i.e. follow links) and how to extract structured data from their pages (i.e. scraping items). 


## RESTful API with Flask
There are Flask extensions that help with building RESTful services with Flask. Basicly, the API allows HTTP post requests containing ASIN and marketplace the user wants to scrape. 

### Calling Scrapy from a script
Remember that Scrapy is built on top of the Twisted asynchronous networking library, so you need to run it inside the Twisted reactor.

There’s a Scrapy utility that provides control over the crawling process:  ***scrapy.crawler.CrawlerRunner***. This class is a thin wrapper that encapsulates some simple helpers to run multiple crawlers, but it won’t start or interfere with existing reactors in any way.

```
crawl_runner = CrawlerRunner(get_project_settings())
```

### Using Crochet from Twisted Applications
Crochet is an MIT-licensed library that makes it easier to use Twisted from regular blocking code such as easily use Twisted from a blocking framework like Django or Flask.

```
import crochet
crochet.setup()

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
```

and finally Flask returns the reviews of the scraped product as a JSON object.

## Avoiding Amazon Bot Detection
Any site that has a vested interest in protecting its data will usually have some basic anti-scraping measures in place like CAPTCHA and blocking. Amazon.com is certainly no exception.
For this crawl, we made sure to:
1. Spoof headers to make requests seem to be coming from a browser, not a script using **random user agent middleware** rotating over a list of user agents

```
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'random_useragent.RandomUserAgentMiddleware': 400
}

USER_AGENT_LIST = "<your_path>/user_agents.txt"
```

2. Rotate IPs using **Crawlera**

```
DOWNLOADER_MIDDLEWARES = {
    'scrapy_crawlera.CrawleraMiddleware': 610,
}

CRAWLERA_ENABLED = True
CRAWLERA_APIKEY = '<your_api_key>'
```

