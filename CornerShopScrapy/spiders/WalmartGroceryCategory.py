# -*- coding: utf-8 -*-
import os
import pickle
import scrapy

from CornerShopScrapy.spiders.SeleniumSpider import SeleniumSpiderBase


class WalmartGroceryCategorySpider(SeleniumSpiderBase):
    name = 'WalmartGroceryCategory'

    def __init__(self,  *args, **kwargs):
        super(WalmartGroceryCategorySpider, self).__init__(*args, **kwargs)
        self.start_urls =  pickle.load( open( "list.p", "rb" ) )
        self.links = []
        self.PAGINATE = True
        self.MAX_NUMBER_OF_PRODUCTS_TOTAL = os.environ['MAX_NUMBER_OF_PRODUCTS_TOTAL']
        self.MAX_NUMBER_OF_PRODUCTS_PER_PAGE = os.environ['MAX_NUMBER_OF_PRODUCTS_PER_PAGE']
        self.MAX_PAGE = os.environ['MAX_PAGE']

        print(self.MAX_PAGE)
        print(self.settings.keys())
        if os.path.exists("products.p"):
            os.remove("products.p")

    def parse(self, response):
        if len(self.links) < self.MAX_NUMBER_OF_PRODUCTS_TOTAL:
            self.logger.info("starting task: %s" % response.url)
            self.driver.get(response.url)
            self.driver.implicitly_wait(30)
            self.links = self.links + self.getProducts()
            if self.PAGINATE:
                self.paginate(response)
        else:
            yield "The script has completed"

    def paginate(self, response):
        last_page = self.driver.find_element_by_xpath("//ul[contains(@class, 'page-select')]//li[last()]")
        self.current_links = []
        for x in range(2, int(last_page.text)):
            if x > self.MAX_PAGE:
                break
            else:
                url = response.url + '/page-%d' % (x)
                self.driver.get(url)
                self.driver.implicitly_wait(30)
                current_links = self.getProducts()
                self.links = self.links + current_links[:self.MAX_NUMBER_OF_PRODUCTS_PER_PAGE]

    def closed(self, reason):
        if len(self.links) > 0:
            with open('products.p', 'ab+') as fp:
                pickle.dump(self.links, fp, protocol=2)
                fp.close()


    def getProducts(self):
        return list(map(lambda x: x.get_attribute("href"), self.driver.find_elements_by_xpath("//a[contains(@class,'product-link')]")))
