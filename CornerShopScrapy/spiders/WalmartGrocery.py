# -*- coding: utf-8 -*-
import os
import scrapy
import pickle
import requests

from CornerShopScrapy.spiders.SeleniumSpider import SeleniumSpiderBase


class WalmartGrocerySpider(SeleniumSpiderBase):
    name = 'WalmartGrocery'
    allowed_domains = ['www.walmart.ca/en/grocery/N-117']
    start_urls = ['http://www.walmart.ca/en/grocery/N-117/']
    driver = None

    def __init__(self, *args, **kwargs):
        super(WalmartGrocerySpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        self.logger.info("starting task: %s" % response.url)
        self.driver.get(response.url)
        self.driver.implicitly_wait(30)
        links = list(map(lambda x: x.get_attribute("href"), self.driver.find_elements_by_xpath("//div[contains(@class, 'categoryTile')]/a")))
        if len(links) > 0:
            pickle.dump( links, open( "list.p", "wb" ) )
        self.driver.close()

    def closed(self, reason):
        super(WalmartGrocerySpider, self).closed(reason)
