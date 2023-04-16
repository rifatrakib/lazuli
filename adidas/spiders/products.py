import scrapy


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["shop.adidas.jp"]
    catalogue_url_base = "https://shop.adidas.jp/f/v1/pub/product"
    product_url_base = "https://shop.adidas.jp/f/v2/web/pub/products/article"

    def start_requests(self):
        yield scrapy.Request(
            f"{self.catalogue_url_base}/list?gender=mens&limit=120&page=1",
            callback=self.parse_links,
        )

    def parse_links(self, response):
        data = response.json()

        if "canonical_param_next" in data:
            endpoint = data["canonical_param_next"].replace("item/", "list")
            print(f"{self.catalogue_url_base}/{endpoint}")
            yield scrapy.Request(
                f"{self.catalogue_url_base}/{endpoint}",
                callback=self.parse_links,
            )

        for product_code, information in data["articles"].items():
            yield scrapy.Request(
                f"{self.product_url_base}/{product_code}/",
                callback=self.parse_products,
                cb_kwargs=information,
            )

    def parse_products(self, response, **kwargs):
        data = response.json()
        yield {**data, **kwargs}
