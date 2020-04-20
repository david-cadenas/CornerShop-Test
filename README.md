# Cornershop's backend integrations test


# How to use it

* First make sure you have [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/install/).Theses tools are essential to make this app run.
* Create a copy of the `.env.example` file with then name `.env`. Make sure you have all the values correct. Ex: `cp .env.example .env`
* Create the database using `python database_setup.py`
* Run `docker-compose up -d`, this command will run `both` scrapper at the same time. Each scraper is a a separate service `walmmart` and `richard` respectively.

# Main features

* Fully configurable
* Pagination
* Container based

# Considerations

Although the test asked for the data to be clean, I think the real approach could be to save the data raw in some NoNSQL service, and then process that information into a `Product` table. By this way the `raw` data could offer some benefits for analysis, such as `tendency`,  `price estimation` and `recommendation`.

Also, I made this in separate containers in order to look for a micro services architecture that this could be manage as 2 separate services and run as `schedule` task inside the `cloud`

Each scraper has it owns configuration, for `Walmart` the configuration is obtained from the environment  and for `Richard` is inside `CornerShopRichard` folder, the `config.yaml` file


## Spiders
### Walmart:

The main core of the website is rendered by JS, so in this case the scraper uses [Selenium](https://www.selenium.dev/projects/) in order to render the content and get the data.

In this case, the scraper is divided in 3 main `spiders`, `WalmartGrocery` which is the one that get all the main categories of the grocery store, `WalmartGroceryCategory` which is the one that collect and paginate product urls. These 2 `spiders` uses `selenium` to render the content.

On the other hand, the `product` spider doesn't required to use `selenium`, because the page contain an `js` object with the `product` information embedded inside the header. I use this object to obtain all the product information to save the data.

### Ricahrds:

I used [pandas](https://pandas.pydata.org/) which is a very powerful tool to manipulate data. Although this is a very powerful tool, for a higher amount of data it's possible that this approach breaks. Therefore, in that case I think using `chunksize` it will be the best approach



# Environment:
* `CELERY_BROKER_URL`: Broker `URL` by default `rabbitmq`
* `SCRAPPER_URLS`: The first `url` to start the scraper by default `https://www.walmart.ca/en/grocery/N-117`
* `CELERYD_MAX_TASKS_PER_CHILD`: Child per task in `celery`, default `1`
* `SELENIUM_URL`: We use selenium as remote service, the `url` for selenium driver. By default `selenium`
* `MAX_NUMBER_OF_PRODUCTS_TOTAL`: Total amount of products can get `walmart` scraper
* `MAX_NUMBER_OF_PRODUCTS_PER_PAGE`: Maximum amount of product per `page` in `walmart` scraper
* `MAX_PAGE`: Max page to iterate, in other words, last page in `walmart` scraper

[Gustavo Sanchez](https://www.linkedin.com/in/antero10/)
