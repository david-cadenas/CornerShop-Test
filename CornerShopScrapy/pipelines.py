# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from scrapy.exceptions import DropItem


from models import Base, Product, BranchProduct

class ProductPipeline(object):
    def __init__(self):
        self.engine = create_engine('sqlite:///db.sqlite')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def process_item(self, item, spider):

        if item.get('image_urls') and len(list(item.get('image_urls'))) > 0:
            item['image_urls'] = ','.join([','.join([x['large']['url'], x['small']['url']]) for x in item.get('image_urls')])

        if item.get('barcodes') and len(list(item.get('barcodes'))) > 0:
            item['barcodes'] = self.arrayToString(item.get('barcodes'))

        if item.get('categories') and len(list(item.get('categories'))) > 0:
            item['categories'] = ','.join([ ','.join(list(map(lambda x: x['seo']['text'] , x['hierarchy']))) for x in item.get('categories')])

        item['description'] = self.removeHTML(item['description']).strip().capitalize()
        item['name'] = item['name'].capitalize()
        item['brand'] = item['brand'].capitalize()
        item['package'] = item['package'] if len(re.findall(r"\d", item['package'])) > 0 else 'n/a'

        return self.save(item)

    def save(self, item):
        try:
            product = Product(
                store='Walmart',
                barcodes=item.get('barcodes'),
                sku=str(item.get('sku')),
                brand=item.get('brand'),
                name=item.get('name'),
                description=item.get('description'),
                package=item.get('package'),
                categories=item.get('categories'),
                image_urls=item.get('image_urls'))

            branch = BranchProduct(
                branch=item.get('store'),
                product=product,
                stock=item['stock'],
                price=float(item.get('price')),
            )

            self.session.add(product)
            self.session.commit()
            return item
        except IntegrityError:
            self.session.rollback()
            return None


    def removeHTML(self, text):
        soup = BeautifulSoup(text)
        return soup.get_text()

    def arrayToString(self, item):
        return ','.join([x for x in item])
