
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from CornerShopScrapy.spiders.WalmartGrocery import WalmartGrocerySpider
from CornerShopScrapy.spiders.WalmartGroceryCategory import WalmartGroceryCategorySpider
from CornerShopScrapy.spiders.WalmartGroceryProduct import WalmartGroceryProductSpider

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(WalmartGrocerySpider)
    yield runner.crawl(WalmartGroceryCategorySpider)
    yield runner.crawl(WalmartGroceryProductSpider)
    reactor.stop()


configure_logging()
config = get_project_settings()
runner = CrawlerRunner(settings=config)
crawl()
reactor.run()
