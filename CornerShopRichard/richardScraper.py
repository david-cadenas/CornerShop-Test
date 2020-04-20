import glob
import os
import pandas as pd
import progressbar
import urllib.request
import uuid
import yaml

from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from scrapy.exceptions import DropItem

from models import Base, Product, BranchProduct

class RichardScraper(object):

    def __init__(self):

        with open(os.path.dirname(os.path.abspath(__file__)) + '/config.yaml') as f:
            obj = yaml.load(f, Loader=yaml.FullLoader)
            self.config = obj['app']

        self.pbar = None
        self.engine = create_engine('sqlite:///db.sqlite')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def showProgress(self,block_num, block_size, total_size):
        if not self.pbar:
            self.pbar = progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()

    def load(self):
        for key,value in self.config['urls'].items():
            self.getFile(key, value)
            setattr(self, key,pd.read_csv('%s.csv' % key, delimiter="|") )


        print("Processing file...")

        self.stock = self.stock[self.stock['BRANCH_REFERENCE'].isin(self.config['branches'])]
        self.prices = self.prices[(self.prices['BRANCH_REFERENCE'].isin(self.config['branches'])) & (self.prices['STOCK'] > 0) & (self.prices['STOCK'].notna())]
        self.products = pd.merge(self.products, self.prices, on='SKU', how='inner')
        self.stock = pd.merge(self.stock, self.products, on=['BRANCH_REFERENCE', 'SKU'], how='inner')
        self.stock = self.stock.drop_duplicates(subset=['SKU'])
        self.stock = self.stock[:self.config['max_number_of_items']]

        return self

    def clean(self):
        print("Cleaning file...")

        package_re = r'([0-9]+\s?[A-z]{2})'

        self.stock['ITEM_NAME'] = self.stock['ITEM_NAME'].str.capitalize()
        self.stock['package'] = self.stock['ITEM_DESCRIPTION'].str.extract(package_re)
        self.stock['ITEM_DESCRIPTION'] = self.stock['ITEM_DESCRIPTION'].apply(self.removeHTML).str.capitalize().str.strip().str.replace(package_re, '')
        self.stock['categories'] = self.stock[['CATEGORY','SUB_CATEGORY', 'SUB_SUB_CATEGORY']].apply(lambda x: 'N/A' if x.isnull().values.any() else ','.join(x.values.astype(str)).strip().capitalize(), axis=1)
        self.stock['BRAND_NAME'] = self.stock['BRAND_NAME'].str.capitalize()
        self.stock["ITEM_IMG"].fillna("N/A", inplace = True)
        self.stock["BRAND_NAME"].fillna("N/A", inplace = True)
        self.stock["STOCK"].fillna("N/A", inplace = True)

        return self

    def save(self):
        print('About to save the data')
        self.pbar = progressbar.ProgressBar(maxval=len(self.stock)).start()
        for index, row  in self.stock.iterrows():
            item = dict(
                barcodes=row['FINELINE_NUMBER'],
                sku=row['SKU'],
                brand=row['BRAND_NAME'],
                name=row['ITEM_NAME'],
                description=row['ITEM_DESCRIPTION'],
                package=row['package'],
                categories=row['categories'],
                image_urls=row['ITEM_IMG'],
                store=row['BRANCH_REFERENCE'],
                price= self.getPrice(row),
                stock=row['STOCK']
            )
            item = self.saveDatabase(item)
            if index < len(self.stock):
                self.pbar.update(index)
            else:
                self.pbar.finish()
        self.removeFiles()

    def saveDatabase(self, item):
        try:
            product = Product(
                store="Richart's",
                barcodes=item['barcodes'],
                sku=str(item['sku']),
                brand=item['brand'],
                name=item['name'],
                description=item['description'],
                package=item['package'],
                categories=item['categories'],
                image_urls=item['image_urls']
                )

            branch = BranchProduct(
                branch=item['store'],
                product=product,
                stock=item['stock'],
                price=float(item['price']),
            )

            self.session.add(product)
            self.session.commit()
            return item

        except IntegrityError as e:
            self.session.rollback()
            return None



    def getFile(self, name, url):
        print("Getting %s file" % name)
        file_name =  '%s.csv' % (name)
        urllib.request.urlretrieve (url, file_name, self.showProgress)
        self.pbar = None


    def removeHTML(self, text):
        if text and isinstance(text, str):
            return BeautifulSoup(text).get_text()
        return 'N/A'

    def getPrice(self, row):
        return "%.2f" % round(float(row['PRICE_WITHOUT_IVA']) + ( row['PRICE_WITHOUT_IVA'] * float(row['IVA'].replace('%',''))))

    def removeFiles(self):
        for i in glob.glob("*.csv"):
            os.remove(i)
