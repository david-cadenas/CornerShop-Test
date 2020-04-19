# -*- coding: utf-8 -*-
import scrapy
import os
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class SeleniumSpiderBase(scrapy.Spider):
    name = 'SeleniumSpider'


    def __init__(self,  *args, **kwargs):
        super(SeleniumSpiderBase, self).__init__(*args, **kwargs)
        self.driver = webdriver.Remote(os.environ['SELENIUM_URL'], DesiredCapabilities.FIREFOX)

    def closed(self, reason):
        self.driver.close()
