# -*- coding: utf-8 -*-

import scrapy
import pickle
import re
import json
import requests

from CornerShopScrapy.items import Product

class WalmartGroceryProductSpider(scrapy.Spider):
    name = 'WalmartGroceryProduct'


    def __init__(self):
        self.start_urls =  pickle.load( open( "products.p", "rb" ) )
        self.STORES_IDS = [3124, 3106, 3159]

    def parse(self, response):
        js = response.xpath('//script//text()').extract()
        object  = None
        id = response.url.split('/')[-1]
        for script in js:
            if ("window.__PRELOADED_STATE__=" in script):
                object = script.replace('window.__PRELOADED_STATE__=', '')
                object = object.replace(';', '')
                object = json.loads(object)

        if object:
            product = object['product']
            catchment = object['catchment'] #storeId
            if (int(catchment['storeId']) in self.STORES_IDS):
                sku = product['activeSkuId']
                entities = object['entities']['skus'][str(sku)]
                offer = self.get_offer(id, [sku])
                product = Product(store=catchment['storeId'], barcodes=entities['upc'],
                            sku=sku, brand=entities['brand']['name'],
                            name=product['item']['name']['en'],
                            description=entities['longDescription'],
                            package=entities['description'],
                            price=offer['currentPrice'],
                            stock=product['quantity'],
                            image_urls=entities['images'])
                yield product

    def get_offer(self, id, skuIds):
        r = requests.post('https://www.walmart.ca/api/product-page/price-offer', json={
            "availabilityStoreId": "3124",
            "fsa": "P7B",
            "experience": "grocery",
            "products": [
                {
                    "productId": id,
                    "skuIds": skuIds
                }
            ],
            "lang": "en"
        })
        data = r.json()
        return data['offers'][str(skuIds[0])]
