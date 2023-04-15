import scrapy


class ShopSpider(scrapy.Spider):
    name = "shop"
    allowed_domains = ["shop.adidas.jp"]
    start_urls = ["http://shop.adidas.jp/"]

    def parse(self, response):
        pass
